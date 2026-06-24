from dataclasses import dataclass


def template_preview_key(template_id: str) -> str:
    return f"templates/{template_id}/preview/preview.png"


def template_mask_key(template_id: str, mask_name: str) -> str:
    return f"templates/{template_id}/masks/{mask_name}"


def fabric_output_key(job_id: str) -> str:
    return f"outputs/fabric/{job_id}/rendered.png"


def tryon_output_key(job_id: str) -> str:
    return f"outputs/tryon/{job_id}/preview.png"


@dataclass(frozen=True)
class JobStatus:
    job_id: str
    status: str
    message: str = ""
