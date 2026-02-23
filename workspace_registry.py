"""Workspace registry persisted under ~/.xi-io."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class WorkspaceRegistry:
    def __init__(self):
        self.registry_path = Path.home() / ".xi-io" / "workspaces.json"
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, object] = {"active": None, "workspaces": {}}
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            try:
                self.registry = json.loads(self.registry_path.read_text())
            except Exception:
                self.registry = {"active": None, "workspaces": {}}

    def _save(self) -> None:
        self.registry_path.write_text(json.dumps(self.registry, indent=2))

    def discover(self, path: str) -> List[str]:
        p = Path(path)
        discovered = [str(x) for x in p.iterdir() if x.is_dir() and (x / ".git").exists()]
        for item in discovered:
            self.registry.setdefault("workspaces", {})[Path(item).name] = item
        self._save()
        return discovered

    def list_workspaces(self) -> Dict[str, str]:
        return self.registry.get("workspaces", {})

    def set_active(self, project: str) -> bool:
        workspaces = self.registry.get("workspaces", {})
        if project in workspaces:
            self.registry["active"] = project
            self._save()
            return True
        return False

    def get_active_path(self) -> str | None:
        active = self.registry.get("active")
        if not active:
            return None
        return self.registry.get("workspaces", {}).get(active)
