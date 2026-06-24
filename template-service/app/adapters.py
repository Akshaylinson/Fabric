from dataclasses import dataclass


@dataclass
class SegmentationResult:
    masks: list[str]


@dataclass
class MetadataResult:
    garment_type: str
    collar_type: str
    sleeve_type: str
    fit_type: str
    length: str
    description: str


@dataclass
class EmbeddingResult:
    vector: list[float]


class SegmentationAdapter:
    def segment(self, image_refs: list[str]) -> SegmentationResult:
        return SegmentationResult(masks=[f"mask_for_{ref}" for ref in image_refs])


class MetadataAdapter:
    def extract(self, image_refs: list[str]) -> MetadataResult:
        return MetadataResult(
            garment_type="shirt",
            collar_type="spread",
            sleeve_type="long",
            fit_type="regular",
            length="hip",
            description="Mock garment description generated from uploaded design images.",
        )


class EmbeddingAdapter:
    def embed(self, description: str) -> EmbeddingResult:
        return EmbeddingResult(vector=[0.12, 0.34, 0.56, 0.78])

