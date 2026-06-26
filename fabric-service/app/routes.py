from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.render_client import RenderClientError
from app.services.workflow2_ai_service import Workflow2AIService
from textile_shared.persistence import (
    LocalObjectStorage,
    PersistentJsonStore,
    decode_data_url,
    service_object_dir,
    service_state_dir,
)

router = APIRouter()

_STORAGE = LocalObjectStorage(service_object_dir('fabric-service'))
_RENDER_STATE = PersistentJsonStore(service_state_dir('fabric-service') / 'renders.json', default_factory=list)
_WORKFLOW2 = Workflow2AIService(storage=_STORAGE)


class FabricRenderRequest(BaseModel):
    fabric_ref: str
    template_ref: str
    fabric_image_data: str | None = None
    render_label: str | None = None


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'fabric-service'}


@router.get('/renders/{render_id}/image')
def get_render_image(render_id: str):
    image_path = _STORAGE.path_for(f'renders/{render_id}/final.png')
    if not image_path.exists():
        raise HTTPException(status_code=404, detail='Render image not found')
    return FileResponse(image_path, media_type='image/png', headers={'Cache-Control': 'no-store'})


@router.post('/fabric/render')
def render_fabric(request: FabricRenderRequest) -> dict[str, Any]:
    if not request.fabric_image_data:
        raise HTTPException(status_code=400, detail='fabric_image_data is required')

    try:
        fabric_bytes, fabric_mime_type = decode_data_url(request.fabric_image_data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail='Invalid fabric_image_data encoding') from exc

    template_package = _load_template_package(request.template_ref)

    try:
        result = _WORKFLOW2.render(
            template_package=template_package,
            fabric_ref=request.fabric_ref,
            fabric_bytes=fabric_bytes,
            fabric_mime_type=fabric_mime_type,
            render_label=request.render_label,
        )
    except RenderClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    payload: dict[str, Any] = {
        'render_id': result.render_id,
        'status': 'completed',
        'template_ref': request.template_ref,
        'fabric_ref': request.fabric_ref,
        'rendered_image_url': result.image_url,
        'image_url': result.image_url,
        'provider': result.provider,
        'model': result.model,
        'metadata': result.metadata,
        'timing': result.timing,
        'processing_logs': result.processing_logs,
        'notes': result.notes,
    }

    _RENDER_STATE.update(
        lambda current: [
            *([item for item in current if isinstance(item, dict)] if isinstance(current, list) else []),
            {
                'render_id': result.render_id,
                'template_ref': request.template_ref,
                'fabric_ref': request.fabric_ref,
                'status': 'completed',
                'rendered_image_url': result.image_url,
                'created_at': result.timing['started_at'],
            },
        ]
    )

    return payload


def _load_template_package(template_ref: str) -> dict[str, Any]:
    import json
    import urllib.error
    import urllib.request

    from app.services.config import get_settings

    settings = get_settings()
    url = f"{settings.TEMPLATE_SERVICE_URL.rstrip('/')}/templates/{template_ref}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise HTTPException(status_code=404, detail='Template not found') from exc
        raise HTTPException(status_code=502, detail='Unable to load template package') from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail='Template service unavailable') from exc
