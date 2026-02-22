#!/usr/bin/env python3
"""
XI-IO Rosetta Stone (v8.9.9.9.25)
The bridge between Human Intent and Industrial Implementation.

Translates:
1. Intent (User words) -> Symbols (Code paths/Components/Axioms)
2. Virtual (REAPER) -> Real World (RW/FileSystem)
3. Directives -> Deterministic Tool Calls
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class RosettaStone:
    def __init__(self, root: str):
        self.root = Path(root)
        self.axioms_file = self.root / "40_documentation" / "reaper_space" / "EXTRACTED_AXIOMS_FINAL.json"
        self.component_registry_file = self.root / ".xi-io" / "component_registry.json"
        
        # Identity Mappings (The Lexicon)
        self.lexicon = {
            "site": ["renderer", "frontend", "html", "css", "dreamcatcher_saas_os"],
            "app": ["dreamcatcher_saas_os", "terminal_app", "react", "logic"],
            "logic": ["system", "backend", "python", "framework.py"],
            "security": ["BHVT", "validation", "lock", "quarantine"],
            "data": ["ledger", "blockchain", "audit", "storage"],
            "ai": ["ollama", "models", "orchestration", "thrawn"],
            "components": ["imported_legacy_framework/organization/unorganized/xibalba/features"],
            "dashboard": ["ui", "frontend", "studio", "command-center", "xibalba-studio"],
        }
        
        self.axioms = self._load_axioms()
        self.components = self._load_components()

    def _load_axioms(self) -> Dict:
        if self.axioms_file.exists():
            try:
                with open(self.axioms_file, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def _load_components(self) -> Dict:
        if self.component_registry_file.exists():
            try:
                with open(self.component_registry_file, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def translate_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Translate raw user input into a Structural Intent Map.
        This is the 'Rosetta Stone' function.
        """
        input_lower = user_input.lower()
        translated = {
            "intent_symbols": [],
            "suggested_paths": [],
            "relevant_axioms": [],
            "industrial_context": ""
        }

        # 1. Map Lexicon Symbols
        for symbol, kws in self.lexicon.items():
            if any(kw in input_lower for kw in kws):
                translated["intent_symbols"].append(symbol)
                
        # 2. Dynamic Component Matching (v8.9.9.9.28)
        if self.components:
            # Check features
            for feat in self.components.get("features", []):
                name = feat.get("name", "").lower()
                if name in input_lower or (len(name) > 3 and name.replace("_", " ") in input_lower):
                    translated["intent_symbols"].append(f"feature:{name}")
                    translated["suggested_paths"].append(feat.get("path"))
            
            # Check components
            for comp in self.components.get("components", []):
                parent = comp.get("parent_module", "").lower()
                if parent in input_lower:
                    translated["intent_symbols"].append(f"component:{parent}")
                    translated["suggested_paths"].append(comp.get("path"))

        # 3. Suggested Path Defaults
        if "site" in translated["intent_symbols"] and not translated["suggested_paths"]:
            translated["suggested_paths"].append("imported_legacy_framework/organization/unorganized/dreamcatcher_saas_os/frontend")
            
        if "dashboard" in translated["intent_symbols"]:
            translated["suggested_paths"].append("20_development/templates/xibalba-studio")
            
        # 4. Connect to Axioms
        if self.axioms:
            for axiom in self.axioms.get("axioms", []):
                frag = axiom.get("axiom_fragment", "").lower()
                # Check if user input relates to known axioms
                if any(sym in frag for sym in translated["intent_symbols"]):
                    translated["relevant_axioms"].append(axiom.get("axiom_fragment"))
                    if len(translated["relevant_axioms"]) > 3: break

        # 4. Build Industrial Advisory
        if translated["intent_symbols"]:
             translated["industrial_context"] = f"[ROSETTA_STONE_ADVISORY] Identified Domain: {', '.join(translated['intent_symbols'])}. Recommended Paths: {', '.join(translated['suggested_paths'])}"

        return translated

    def get_lexicon_summary(self) -> str:
        """Returns a string representation of the current rosetta lexicon for LLM ingestion."""
        summary = "ROSETTA STONE LEXICON (Intent to Symbol):\n"
        for key, vals in self.lexicon.items():
            summary += f"- {key}: {', '.join(vals)}\n"
        return summary

# Global instance
def get_rosetta(root: str):
    return RosettaStone(root)
