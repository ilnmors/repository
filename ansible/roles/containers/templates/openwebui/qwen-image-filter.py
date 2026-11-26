"""
title: Qwen-Image-2.1 Prompt Guide
author: repository
version: 1.0.0
description: Injects Qwen-Image-2.1-only prompt safeguards (no literal N-head tokens, positive phrasing for CFG 1.0, 32-multiple sizes) when image generation is active.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field

MARKER = "[Image Generation & Editing Guide — qwen-image-2.1]"

DEFAULT_GUIDE = """[Image Generation & Editing Guide — qwen-image-2.1]
These rules apply ONLY to the qwen-image-2.1 image model (ChatR Labs Uncensored Omni + 8-step Turbo LoRA).
When calling generate_image or edit_image, write a clear, detailed English visual prompt.

CRITICAL RULES (qwen-image-2.1):
- NEVER WRITE "N-head" PROPORTION PHRASES: NEVER write "2-head", "3-head", "7-head", "8-head", or "<number>-head proportions". Qwen3-VL-8B interprets "<number>-head" literally and draws multiple heads on one body. Instead use "super-deformed chibi proportions" / "chibi proportions" for chibi characters, and "tall slender anime proportions" / "natural adult proportions" for full-height figures.
- POSITIVE PHRASING ONLY (CFG 1.0): The 8-step Turbo LoRA runs at CFG 1.0 without negative prompts. Avoid phrasing like "no <feature>" or "without <feature>" that puts unwanted nouns into the prompt; describe what SHOULD appear positively (e.g., write "completely smooth hairless skin" instead of "no pubic hair").
- SERVER-APPLIED TURBO LORA: The 8-step Turbo LoRA is applied automatically by the server for both generate_image and edit_image. Do NOT append <sd_cpp_extra_args> or <lora:...> tags unless the user explicitly asks for a custom seed or override.
- RESOLUTION (MULTIPLES OF 32):
  - Square (default): omit size (1024x1024)
  - Portrait / vertical: "896x1152" or "1024x1536"
  - Landscape / horizontal: "1152x896" or "1152x1024"
- NATIVE I2I EDITING: edit_image preserves identity, hands, and layout natively; describe only what should change and what should stay identical."""


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=0, description="Filter execution priority.")
        enabled: bool = Field(
            default=True,
            description="Enable Qwen-Image-2.1 prompt safeguards when image generation is active.",
        )
        target_image_model: str = Field(
            default="qwen-image-2.1",
            description="Apply this filter only when IMAGE_GENERATION_MODEL matches this model id.",
        )
        extra_instructions: str = Field(
            default="",
            description="Optional extra lines appended to the Qwen-Image-2.1 guide.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict, __metadata__: Optional[dict] = None) -> dict:
        if not self.valves.enabled:
            return body

        target = (self.valves.target_image_model or "").strip()
        active_image_model = os.environ.get("IMAGE_GENERATION_MODEL", "").strip()
        if target and active_image_model and active_image_model != target:
            return body

        features = body.get("features") or (__metadata__ or {}).get("features") or {}
        if not features.get("image_generation"):
            return body

        messages = body.get("messages")
        if not isinstance(messages, list):
            return body

        guide = DEFAULT_GUIDE
        extra = (self.valves.extra_instructions or "").strip()
        if extra:
            guide = f"{guide}\n\n{extra}"

        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content") or ""
                if isinstance(content, str) and MARKER not in content:
                    msg["content"] = f"{content}\n\n{guide}" if content.strip() else guide
                return body

        messages.insert(0, {"role": "system", "content": guide})
        return body
