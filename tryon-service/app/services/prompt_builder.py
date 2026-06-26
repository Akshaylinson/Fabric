from __future__ import annotations

from typing import Any


def build_prompt(
    customer_summary: dict[str, Any],
    garment_summary: dict[str, Any],
    settings_summary: dict[str, Any] | None = None,
) -> str:
    settings_summary = settings_summary or {}
    customer_notes = customer_summary.get("notes", "customer identity reference")
    garment_notes = garment_summary.get("notes", "rendered garment reference")
    garment_material = garment_summary.get("fabric", "preserve garment fabric")
    garment_color = garment_summary.get("color", "preserve garment color")

    lines = [
        "Generate a photorealistic virtual try-on preview.",
        "Use the first image as the customer identity reference.",
        "Use the second image as the garment reference from Workflow 2.",
        "Preserve facial identity, hairstyle, skin tone, body proportions, and pose.",
        "Preserve the garment exactly as rendered and do not redesign it.",
        f"Customer notes: {customer_notes}.",
        f"Garment notes: {garment_notes}.",
        f"Keep fabric characteristics such as {garment_material} and {garment_color} intact.",
        "Do not add accessories or change the customer's face.",
        "Generate a realistic full-body studio fashion photograph with natural cloth draping.",
    ]

    if settings_summary.get("face_restoration"):
        lines.append("Apply gentle face restoration while preserving identity.")
    if settings_summary.get("upscaling"):
        lines.append("Return a high-resolution output suitable for customer preview.")

    lines.append("Photorealistic. Fashion photography quality.")
    return "\n".join(lines)
