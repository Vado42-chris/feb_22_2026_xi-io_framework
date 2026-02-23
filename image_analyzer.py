"""Image analysis shim for CLI commands."""

from __future__ import annotations

from typing import Any, Dict


class ImageAnalyzer:
    def __init__(self, context_manager: Any):
        self.context_manager = context_manager

    def analyze_image(self, path: str, prompt: str = "Describe this image.") -> Dict[str, Any]:
        return {"ok": True, "path": path, "analysis": f"Image analysis unavailable in this build. Prompt: {prompt}"}

    def extract_code_from_image(self, path: str) -> Dict[str, Any]:
        return {"ok": True, "path": path, "code": "", "note": "OCR module not bundled in this snapshot."}
