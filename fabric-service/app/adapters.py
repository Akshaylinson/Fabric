from dataclasses import dataclass


@dataclass
class FabricTransferResult:
    rendered_image_ref: str


@dataclass
class TextureMappingResult:
    preserved_structure: bool
    notes: str


class FabricTransferAdapter:
    def transfer(self, fabric_ref: str, template_ref: str) -> FabricTransferResult:
        return FabricTransferResult(
            rendered_image_ref=f"minio://outputs/fabric/{template_ref.split('/')[-1]}_{fabric_ref.split('/')[-1]}.png"
        )


class TextureMappingAdapter:
    def map_texture(self, fabric_ref: str, template_ref: str) -> TextureMappingResult:
        return TextureMappingResult(
            preserved_structure=True,
            notes="Mock fabric transfer preserved garment structure and replaced only appearance.",
        )

