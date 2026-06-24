from dataclasses import dataclass


@dataclass
class HumanParsingResult:
    body_mask_ref: str


@dataclass
class PoseResult:
    pose_keypoints_ref: str


@dataclass
class TryOnResult:
    output_image_ref: str
    notes: str


class HumanParsingAdapter:
    def parse(self, customer_image_ref: str) -> HumanParsingResult:
        return HumanParsingResult(body_mask_ref=f"{customer_image_ref}:body-mask")


class PoseAdapter:
    def estimate(self, customer_image_ref: str) -> PoseResult:
        return PoseResult(pose_keypoints_ref=f"{customer_image_ref}:pose")


class TryOnAdapter:
    def generate(
        self,
        customer_image_ref: str,
        garment_image_ref: str,
        body_mask_ref: str,
        pose_keypoints_ref: str,
    ) -> TryOnResult:
        return TryOnResult(
            output_image_ref=f"minio://outputs/tryon/{customer_image_ref.split('/')[-1]}_{garment_image_ref.split('/')[-1]}.png",
            notes="Mock try-on preserves face, body shape, garment structure, and fabric appearance at the contract level.",
        )

