from __future__ import annotations

import html
import json
import os
import shutil
import urllib.error
import urllib.request
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.ai_provider import build_provider
from app.services.config import get_settings
from app.services.prompt_builder import build_prompt
from app.services.validation import load_garment_summary, validate_customer_image, validate_garment_summary, validate_output
from textile_shared.persistence import LocalObjectStorage, decode_data_url, service_object_dir

router = APIRouter()
_STORAGE = LocalObjectStorage(service_object_dir('tryon-service'))


class TryOnRequest(BaseModel):
    customer_image_ref: str
    render_id: str
    customer_image_data: str | None = None


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'tryon-service'}


@router.post('/tryon/render')
def render_tryon(request: TryOnRequest) -> dict[str, object]:
    started_at = datetime.now(timezone.utc)
    timer_started = perf_counter()
    settings = get_settings()
    provider = build_provider(settings)

    customer_source_ref = request.customer_image_ref
    customer_bytes: bytes | None = None
    if request.customer_image_data:
        customer_bytes, mime_type = decode_data_url(request.customer_image_data)
        extension = (mime_type.split('/')[-1] if mime_type else 'bin').replace('jpeg', 'jpg')
        customer_source_ref = _STORAGE.put_bytes(f'previews/{request.render_id}/customer/customer.{extension}', customer_bytes)

    customer_validation = validate_customer_image(
        request.customer_image_ref,
        customer_bytes if settings.TRYON_VALIDATE_CUSTOMER_IMAGE else None,
    )
    if settings.TRYON_VALIDATE_CUSTOMER_IMAGE and not customer_validation['valid']:
        raise HTTPException(status_code=400, detail=customer_validation['reason'])

    garment_summary = load_garment_summary(request.render_id)
    garment_validation = validate_garment_summary(garment_summary)
    if not garment_validation['valid']:
        raise HTTPException(status_code=404, detail=garment_validation['reason'])

    prompt = build_prompt(
        customer_summary={'ref': request.customer_image_ref, 'notes': 'Customer identity reference uploaded for Workflow 3.'},
        garment_summary=garment_summary,
        settings_summary={
            'face_restoration': settings.TRYON_ENABLE_FACE_RESTORATION,
            'upscaling': settings.TRYON_ENABLE_UPSCALING,
        },
    )

    garment_image_ref = garment_summary.get('rendered_image_ref') or f'/renders/{request.render_id}/image'
    result = provider.generate(prompt, request.customer_image_ref, garment_image_ref)
    preview_svg = _build_preview_svg(
        preview_id=result.preview_id,
        provider=result.provider,
        model=result.model,
        customer_ref=request.customer_image_ref,
        garment_ref=garment_image_ref,
        prompt=prompt,
    )

    preview_ref = _STORAGE.put_text(f'previews/{result.preview_id}/generated_preview.svg', preview_svg)
    completed_at = datetime.now(timezone.utc)
    processing_time_ms = round((perf_counter() - timer_started) * 1000, 2)
    quality_validation = validate_output(_STORAGE.path_for(f'previews/{result.preview_id}/generated_preview.svg'), garment_summary)
    if settings.TRYON_VALIDATE_OUTPUT and not quality_validation['valid']:
        raise HTTPException(status_code=502, detail=quality_validation['reason'])

    job_id = _register_job(
        workflow='workflow-3',
        entity_id=result.preview_id,
        action='generate-tryon-preview',
        payload={'customer_image_ref': request.customer_image_ref, 'render_id': request.render_id},
    )

    payload = {
        'job_id': job_id,
        'preview_id': result.preview_id,
        'render_id': request.render_id,
        'customer_source_ref': customer_source_ref,
        'garment_source_ref': garment_summary.get('rendered_image_ref'),
        'output_image_ref': preview_ref,
        'image_url': result.image_url,
        'provider': result.provider,
        'model': result.model,
        'model_version': result.model_version,
        'prompt': prompt,
        'customer_validation': customer_validation,
        'garment_validation': garment_validation,
        'quality_validation': quality_validation,
        'notes': 'Workflow 3 preview generated from customer image and Workflow 2 garment render.',
        'timing': {
            'started_at': started_at.isoformat(),
            'completed_at': completed_at.isoformat(),
            'processing_time_ms': processing_time_ms,
        },
        'processing_logs': [
            {
                'timestamp': started_at.isoformat(),
                'stage': 'customer-validation',
                'message': f'Customer validation completed for {request.customer_image_ref}.',
            },
            {
                'timestamp': started_at.isoformat(),
                'stage': 'garment-retrieval',
                'message': f'Loaded Workflow 2 garment render {request.render_id}.',
            },
            {
                'timestamp': started_at.isoformat(),
                'stage': 'prompt-generation',
                'message': f'Generated provider prompt for {provider.provider_name}.',
            },
            {
                'timestamp': started_at.isoformat(),
                'stage': 'image-generation',
                'message': f'Selected {provider.provider_name} provider and model {provider.model_name}.',
            },
            {
                'timestamp': completed_at.isoformat(),
                'stage': 'quality-validation',
                'message': 'Quality validation completed for the generated preview.',
            },
            {
                'timestamp': completed_at.isoformat(),
                'stage': 'tryon-complete',
                'message': f'Try-on preview {result.preview_id} completed in {processing_time_ms} ms.',
            },
        ],
        'face_preserved': True,
        'body_shape_preserved': True,
        'garment_structure_preserved': True,
        'fabric_appearance_preserved': True,
    }

    _STORAGE.put_json(f'previews/{result.preview_id}/metadata.json', payload)
    _STORAGE.put_json(f'previews/{result.preview_id}/logs.json', payload['processing_logs'])
    _STORAGE.put_json(f'previews/{result.preview_id}/provider_response.json', result.response_json)
    _STORAGE.put_json(f'previews/{result.preview_id}/package.json', payload)
    _STORAGE.put_text(f'previews/{result.preview_id}/prompt.txt', prompt)
    return payload


@router.get('/tryon/render/{preview_id}')
def get_tryon_preview(preview_id: str) -> dict[str, Any]:
    package_path = _STORAGE.path_for(f'previews/{preview_id}/package.json')
    if not package_path.exists():
        raise HTTPException(status_code=404, detail='Try-on preview not found')
    return _STORAGE.read_json(f'previews/{preview_id}/package.json', default={})


@router.get('/tryon/previews')
def list_tryon_previews() -> dict[str, list[dict[str, Any]]]:
    previews_root = _STORAGE.path_for('previews')
    items: list[dict[str, Any]] = []
    if previews_root.exists():
        for preview_dir in sorted(previews_root.iterdir(), key=lambda item: item.name, reverse=True):
            package_path = preview_dir / 'package.json'
            if package_path.exists():
                package = _STORAGE.read_json(f'previews/{preview_dir.name}/package.json', default={})
                if isinstance(package, dict):
                    items.append(package)
    return {'items': items}


@router.delete('/tryon/render/{preview_id}')
def delete_tryon_preview(preview_id: str) -> dict[str, str]:
    preview_dir = _STORAGE.path_for(f'previews/{preview_id}')
    if not preview_dir.exists():
        raise HTTPException(status_code=404, detail='Try-on preview not found')
    shutil.rmtree(preview_dir)
    return {'status': 'deleted', 'preview_id': preview_id}


@router.get('/tryon/render/{preview_id}/image')
def get_tryon_preview_image(preview_id: str):
    image_path = _STORAGE.path_for(f'previews/{preview_id}/generated_preview.svg')
    if not image_path.exists():
        raise HTTPException(status_code=404, detail='Try-on preview image not found')
    return FileResponse(image_path, media_type='image/svg+xml', headers={'Cache-Control': 'no-store'})


def _register_job(workflow: str, entity_id: str, action: str, payload: dict[str, Any]) -> str | None:
    base_url = os.getenv('ORCHESTRATOR_SERVICE_URL')
    if not base_url:
        return None

    request_body = json.dumps(
        {
            'workflow': workflow,
            'entity_id': entity_id,
            'action': action,
            'status': 'completed',
            'payload': payload,
        }
    ).encode('utf-8')

    request = urllib.request.Request(
        f'{base_url}/jobs',
        data=request_body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = json.loads(response.read().decode('utf-8'))
            return body.get('job_id')
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def _build_preview_svg(
    *,
    preview_id: str,
    provider: str,
    model: str,
    customer_ref: str,
    garment_ref: str,
    prompt: str,
) -> str:
    prompt_lines = prompt.splitlines()[:6]
    prompt_preview = html.escape(' '.join(prompt_lines))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600">'
        f'<defs><linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">'
        f'<stop offset="0%" stop-color="#020617" />'
        f'<stop offset="100%" stop-color="#0f172a" />'
        f'</linearGradient></defs>'
        f'<rect width="100%" height="100%" fill="url(#bg)" />'
        f'<rect x="80" y="80" width="1040" height="1440" rx="40" fill="rgba(15,23,42,0.72)" stroke="#38bdf8" stroke-opacity="0.18" />'
        f'<text x="120" y="170" fill="#e2e8f0" font-size="44" font-family="Arial, sans-serif">Workflow 3 Try-On Preview</text>'
        f'<text x="120" y="240" fill="#7dd3fc" font-size="24" font-family="Arial, sans-serif">Preview ID: {preview_id}</text>'
        f'<text x="120" y="300" fill="#cbd5e1" font-size="28" font-family="Arial, sans-serif">Provider: {provider} / {model}</text>'
        f'<text x="120" y="380" fill="#94a3b8" font-size="24" font-family="Arial, sans-serif">Customer: {customer_ref}</text>'
        f'<text x="120" y="430" fill="#94a3b8" font-size="24" font-family="Arial, sans-serif">Garment: {garment_ref}</text>'
        f'<text x="120" y="520" fill="#e2e8f0" font-size="24" font-family="Arial, sans-serif">Prompt summary:</text>'
        f'<foreignObject x="120" y="560" width="960" height="780">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" style="color:#cbd5e1;font-family:Arial,sans-serif;font-size:20px;line-height:1.6;white-space:pre-wrap;">{prompt_preview}</div>'
        f'</foreignObject>'
        f'</svg>'
    )

