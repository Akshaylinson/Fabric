from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters import HumanParsingAdapter, PoseAdapter, TryOnAdapter

router = APIRouter()


class TryOnRequest(BaseModel):
    customer_image_ref: str
    garment_image_ref: str


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "tryon-service"}


@router.post("/tryon/render")
def render_tryon(request: TryOnRequest) -> dict[str, object]:
    human_parsing = HumanParsingAdapter().parse(request.customer_image_ref)
    pose = PoseAdapter().estimate(request.customer_image_ref)
    result = TryOnAdapter().generate(
        request.customer_image_ref,
        request.garment_image_ref,
        human_parsing.body_mask_ref,
        pose.pose_keypoints_ref,
    )
    return {
        "output_image_ref": result.output_image_ref,
        "notes": result.notes,
        "face_preserved": True,
        "body_shape_preserved": True,
        "garment_structure_preserved": True,
        "fabric_appearance_preserved": True,
    }

