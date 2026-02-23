"""Conversation/context persistence helpers for XI CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class ContextManager:
    def __init__(self, working_dir: str | Path):
        self.working_dir = Path(working_dir)
        self.context_file = self.working_dir / ".xi_context.json"
        self.ignore_file = self.working_dir / ".xi-ignore"
        self.context: Dict[str, List[Dict[str, str]]] = {"conversation": [], "receipts": []}
        self.silent = False
        self._load_context()

    def _load_context(self) -> None:
        if self.context_file.exists():
            try:
                self.context = json.loads(self.context_file.read_text())
            except Exception:
                self.context = {"conversation": [], "receipts": []}

    def save_context(self) -> None:
        self.context_file.write_text(json.dumps(self.context, indent=2))

    def add_message(self, role: str, content: str) -> None:
        self.context.setdefault("conversation", []).append({"role": role, "content": content})
        self.save_context()

    def get_context_summary(self) -> Dict[str, int]:
        return {
            "messages": len(self.context.get("conversation", [])),
            "receipts": len(self.context.get("receipts", [])),
        }

    def build_context_budget(self, max_files: int = 10) -> Dict[str, int]:
        return {"max_files": max_files, "messages": len(self.context.get("conversation", []))}

    def detect_patterns(self, text: str) -> Dict[str, bool]:
        lower = text.lower()
        return {
            "asks_for_plan": "plan" in lower,
            "asks_for_code": any(k in lower for k in ["code", "create", "build", "patch"]),
        }
