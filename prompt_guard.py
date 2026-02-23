"""Minimal prompt safety guard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PromptGuard:
    silent: bool = False

    def check(self, text: str) -> Dict[str, str]:
        lower = text.lower()
        blocked = ["rm -rf /", "format c:", "shutdown -h now"]
        for pattern in blocked:
            if pattern in lower:
                return {
                    "severity": "BLOCK",
                    "reason": "dangerous_command",
                    "category": "safety",
                    "refusal_message": "Blocked potentially destructive command.",
                }
        return {"severity": "ALLOW", "reason": "ok", "category": "safe"}

    def get_refusal_message(self, verdict: Dict[str, str]) -> str:
        return verdict.get("refusal_message", "Request blocked by PromptGuard")


def get_guard(silent: bool = False) -> PromptGuard:
    return PromptGuard(silent=silent)
