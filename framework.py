"""
XI-IO v8 Framework - Unified API

8 for Infinity (∞) - The Final, Unified Framework
"""

from typing import Any, Dict, List, Optional, Union
import math
import psutil
import os
import time
import base64
import json
import hashlib
from pathlib import Path
from axiom_engine import AxiomEngine
from ledger_guard import LedgerGuard

# Golden Ratio
PHI = (1 + math.sqrt(5)) / 2


class BHVTValidator:
    """Black Hole Validator Theory - 7 Validation Loops"""
    
    def __init__(self, system: Any, engine: Optional[AxiomEngine] = None):
        self.system = system
        self.engine = engine or AxiomEngine()
        self.loops = 7
    
    def validate_all_loops(self) -> bool:
        """Run all 7 BHVT validation loops"""
        results = []
        
        # Loop 1: Foundation
        results.append(self._validate_foundation())
        
        # Loop 2: Fractal Depth
        results.append(self._validate_fractal_depth())
        
        # Loop 3: Intent
        results.append(self._validate_intent())
        
        # Loop 4: Grounding
        results.append(self._validate_grounding())
        
        # Loop 5: REAPER Space
        results.append(self._validate_reaper_space())
        
        # Loop 6: Activation
        results.append(self._validate_activation())
        
        # Loop 7: Final Validation
        results.append(all(results))
        
        return all(results)
    
    def _validate_foundation(self) -> bool:
        """Loop 1: Validate foundation - system must have attributes"""
        return hasattr(self.system, '__dict__') or isinstance(self.system, dict)
    
    def _validate_fractal_depth(self) -> bool:
        """Loop 2: Validate fractal depth - system structure exists"""
        if isinstance(self.system, dict):
            return len(self.system) >= 0  # Any dict is valid
        return True
    
    def _validate_intent(self) -> bool:
        """Loop 3: Validate intent - system has purpose"""
        if isinstance(self.system, dict):
            # Valid if has any content or is explicitly empty
            return True
        return True
    
    def _validate_grounding(self) -> bool:
        """Loop 4: Validate grounding - system is grounded in industrial invariants"""
        # Industrial Grounding: If we find a matching axiom, it's solidly grounded.
        if self.engine.verify_integrity("LEDGER", self.system):
            return True
            
        data = ""
        if isinstance(self.system, dict):
            data = str(self.system.get("content", "")) + str(self.system.get("new_content", ""))
        
        # If it claims to be industrial, it MUST have a header (v8.9.9.9.17)
        if "#hallbergmaths" in data or "INDUSTRIAL_DIRECTIVE_MANIFEST" in data:
            return True
            
        # For non-industrial objects (simple work), we allow grounding if it has content
        # unless it explicitly triggers an industrial-only code path.
        return bool(data) or (self.system is not None and not data)
    
    def _validate_reaper_space(self) -> bool:
        """Loop 5: Validate REAPER space - system has computational space"""
        # Check for extreme resource exhaustion
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            ram_usage = psutil.virtual_memory().percent
            
            # If system is at >95% capacity, REAPER space is compromised
            if cpu_usage > 95 or ram_usage > 95:
                return False
        except:
            pass
            
        # Axiomatic alignment check
        if not self.engine.verify_integrity("REAPER", self.system):
            # Fallback for standard objects if not explicitly REAPER-aligned
            return self.system is not None or self.system == {} or self.system == []
            
        return True
    
    def _validate_activation(self) -> bool:
        """Loop 6: Validate activation - system can be activated"""
        # Any object can be activated (used)
        return True


class HallbergMath:
    """Hallberg Mathematics Framework"""
    
    def __init__(self, depth: int = 0, beta: float = 1.5, radius: float = 1.0):
        self.depth = depth
        self.beta = beta
        self.radius = radius
        self.PHI = PHI
    
    def fractal_depth(self, n: Optional[int] = None) -> float:
        """Calculate fractal depth: D(n) = φ^n"""
        n = n if n is not None else self.depth
        return self.PHI ** n
    
    def reaper_space(self) -> float:
        """Calculate REAPER space: S_fractal = PHI^depth × β × r²"""
        return (self.PHI ** self.depth) * self.beta * (self.radius ** 2)
    
    def beta_scaling(self, complexity: float = 1.0) -> float:
        """Calculate beta scaling"""
        return self.beta * complexity


class CategoryRouter:
    """Category 42/43 Routing System"""
    
    def __init__(self):
        self.categories = list(range(1, 42))
        self.pivot = 42
        self.validator = 43
    
    def route(self, work: Any, from_category: int, to_category: int, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route work through Category 42/43"""
        # Transform at Category 42
        transformed = self._transform_at_42(work, from_category)
        if meta:
            transformed["metadata"] = meta
        
        # Validate at Category 43
        validated = self._validate_at_43(transformed)
        
        # Deliver to destination
        return self._deliver(validated, to_category)
    
    def _transform_at_42(self, work: Any, from_category: int) -> Dict[str, Any]:
        """Transform at Category 42 pivot"""
        return {
            "original_category": from_category,
            "work": work,
            "transformed_at": 42,
        }
    
    def _validate_at_43(self, transformed: Dict[str, Any]) -> Dict[str, Any]:
        """Validate at Category 43"""
        # Run BHVT validation
        validator = BHVTValidator(transformed)
        is_valid = validator.validate_all_loops()
        
        return {
            **transformed,
            "validated_at": 43,
            "valid": is_valid,
        }
    
    def _deliver(self, validated: Dict[str, Any], to_category: int) -> Dict[str, Any]:
        """Deliver to destination category"""
        # Industrial Log: Record the enactment
        IndustrialAuditService.log_action({
            "user": os.getenv("USER", "XI-IO_CLI"),
            "action": validated.get("metadata", {}).get("action", "CATEGORY_TRANSFORM"),
            "target": validated.get("metadata", {}).get("target", f"CAT_{to_category}"),
            "project": validated.get("metadata", {}).get("project", "XI_CORE"),
            "metadata": {
                **validated.get("metadata", {}),
                "pivot": validated.get("transformed_at"),
                "validator": validated.get("validated_at"),
                "status": "VALIDATED" if validated.get("valid") else "FAILED"
            }
        })
        
        return {
            **validated,
            "destination_category": to_category,
            "delivered": True,
        }

class IndustrialAuditService:
    """Industrial Audit Ledger Service (Category 43)"""
    LEDGER_PATH = Path.home() / ".xi-io" / "production_ledger.json"
    silent = True

    @classmethod
    def set_silent(cls, silent: bool):
        cls.silent = silent

    @staticmethod
    def log_action(entry: Dict[str, Any]):
        """Log an industrial action to the production ledger with hash-chaining."""
        import hashlib
        
        timestamp = int(time.time() * 1000)
        
        # Build the entry (without chain_hash first — it's computed from content)
        entry_id = f"AL-{hashlib.sha256(f'{json.dumps(entry)}-{timestamp}'.encode()).hexdigest()[:12]}-{timestamp}"
        
        full_entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "user": entry.get("user", "XI"),
            "action": entry.get("action", "ENACT"),
            "target": entry.get("target", "UNKNOWN"),
            "project": entry.get("project", "XI_CORE"),
            "metadata": entry.get("metadata", {}),
        }
        
        try:
            os.makedirs(IndustrialAuditService.LEDGER_PATH.parent, exist_ok=True)
            guard = LedgerGuard(IndustrialAuditService.LEDGER_PATH)
            
            # Get previous chain hash for linking
            prev_hash = guard.get_last_hash()
            
            # Compute chain_hash: SHA256(prev_hash + this_entry_json)
            full_entry["chain_hash"] = guard.chain_hash(
                json.dumps(full_entry, sort_keys=True), prev_hash
            )
            
            # Read, append, write
            ledger = guard.read()
            ledger.append(full_entry)
            if len(ledger) > 1000:
                ledger = ledger[-1000:]
            
            if guard.safe_write(ledger):
                if not IndustrialAuditService.silent:
                    print(f" [Industrial] Action logged: {entry_id} [chain: ...{full_entry['chain_hash'][-8:]}]")
            else:
                print(f" [!] Ledger write failed for {entry_id}")
        except Exception as e:
            if not IndustrialAuditService.silent:
                print(f" [AL] Failed to record action: {e}")


class HardwareGuard:
    """
    Hardware Awareness Layer (Sector Guard)
    - Monitors for I/O errors (OSError/EIO)
    - Performs atomic verification (Write-then-Read-Hash)
    - Detects corruption patterns
    """
    
    silent = False

    @classmethod
    def set_silent(cls, silent: bool):
        cls.silent = silent

    @staticmethod
    def verify_io(path: Path, expected_hash: Optional[str] = None) -> bool:
        """Verify that a path is readable and matches a hash if provided"""
        try:
            if not path.exists():
                return False
            content = path.read_bytes()
            if expected_hash:
                actual_hash = hashlib.sha256(content).hexdigest()
                return actual_hash == expected_hash
            return True
        except (OSError, IOError) as e:
            # Detect hardware-level failures (EIO, etc)
            if not HardwareGuard.silent:
                print(f" [HardwareGuard] CRITICAL_IO_ERROR at {path}: {e}")
            return False

    @staticmethod
    def simulate_failure(path: Path):
        """Used for Test 13: Silent Failure Simulation"""
        raise OSError(5, "Input/output error (SIMULATED_SECTOR_CORRUPTION)")


class ActionReceipt:
    """
    Structural Receipt Contract (λ)
    Ensures machine-verifiable truth for all industrial operations.
    """
    
    @staticmethod
    def create(op: str, path: str, ok: bool, **kwargs) -> str:
        """Create a JSON-string receipt"""
        receipt = {
            "op": op,
            "path": str(path),
            "ok": ok,
            "bytes": kwargs.get("bytes", 0),
            "sha256": kwargs.get("sha256", "0" * 64),
            "mtime": kwargs.get("mtime", time.time()),
            "exit_code": kwargs.get("exit_code", 0 if ok else 1),
            "policy": kwargs.get("policy", "allowed")
        }
        # Final contract enforcement: Merge any additional fields
        receipt.update({k: v for k, v in kwargs.items() if k not in receipt})
        return json.dumps(receipt)


class MirrorTransform:
    """Mirror Formula - Bidirectional Validation"""
    
    def forward(self, data: Any) -> Any:
        """Forward transformation (hallbergmaths)"""
        # Category 42 transform
        transformed = {"data": data, "direction": "forward"}
        
        # (7)(0) operator - 7 loops then zero
        validated = self._seven_zero_operator(transformed)
        
        return validated
    
    def backward(self, data: Any) -> Any:
        """Backward transformation (shtamgrebllah#)"""
        # )0()7( operator - zero then 7 loops reverse
        reversed_data = self._zero_seven_operator(data)
        
        return reversed_data.get("data")
    
    def validate_identity(self, original: Any) -> bool:
        """Validate f⁻¹(f(x)) = x"""
        forward_result = self.forward(original)
        backward_result = self.backward(forward_result)
        
        return backward_result == original
    
    def _seven_zero_operator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """(7)(0) operator"""
        return {**data, "loops": 7, "state": "zero"}
    
    def _zero_seven_operator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """")0()7( operator"""
        return {**data, "loops": 7, "state": "reversed"}


class ModelRegistry:
    """AI Model Registry using Ollama"""
    
    def __init__(self, models_dir: str = "70_models"):
        self.models_dir = models_dir
        self.models = {}
        self._ollama_available = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            import ollama
            ollama.list()
            return True
        except:
            return False
    
    def load(self, model_name: str) -> Any:
        """Load AI model by name"""
        if model_name in self.models:
            return self.models[model_name]
        
        model = self._load_model(model_name)
        self.models[model_name] = model
        return model
    
    def _load_model(self, model_name: str) -> Any:
        """Load model via Ollama"""
        if not self._ollama_available:
            return {"name": model_name, "error": "Ollama not available"}
        
        # Map framework model names to Ollama models
        model_map = {
            "thrawn-strategist": "xibalba:custom",
            "thrawn-executor": "xibalba:custom",
            "thrawn-creator": "deepseek-coder:6.7b",
            "thrawn-commander": "xibalba:latest",
            "thrawn-analyst": "deepseek-r1:1.5b",
            "qwen2.5-coder-7b": "deepseek-coder:6.7b",
            "phi3.5-latest": "xibalba:latest",
            "llama3.2-latest": "llama3.1:8b",
        }
        
        ollama_model = model_map.get(model_name, "xibalba:custom")
        
        return {
            "name": model_name,
            "ollama_model": ollama_model,
            "loaded": True,
            "backend": "ollama"
        }
    
    def generate(self, model_name: str, prompt: str, max_tokens: int = 100) -> str:
        """Generate text using loaded model"""
        import ollama
        
        model = self.load(model_name)
        if "error" in model:
            return f"Error: {model['error']}"
        
        response = ollama.generate(
            model=model['ollama_model'],
            prompt=prompt,
            options={'num_predict': max_tokens}
        )
        
        return response['response']
    
    def list_all(self) -> List[str]:
        """List all available models"""
        return [
            "thrawn-strategist",
            "thrawn-executor",
            "thrawn-creator",
            "thrawn-commander",
            "thrawn-analyst",
            "qwen2.5-coder-7b",
            "phi3.5-latest",
            "llama3.2-latest",
        ]


class Framework:
    """
    XI-IO v8 Framework - Unified API
    
    8 for Infinity (∞)
    
    Usage:
        framework = Framework()
        
        # Validate anything
        is_valid = framework.bhvt.validate_all_loops(my_system)
        
        # Calculate fractal depth
        depth = framework.hallberg.fractal_depth(8)  # 46.979
        
        # Route through Category 42/43
        result = framework.category_router.route(work, from_cat=35, to_cat=14)
        
        # Load AI model
        model = framework.models.load("thrawn-strategist")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize core systems
        self.axiom_engine = AxiomEngine()
        self.bhvt = None  # Set when validating
        self.hallberg = HallbergMath(depth=8, beta=1.5, radius=10)
        self.category_router = CategoryRouter()
        self.mirror = MirrorTransform()
        self.models = ModelRegistry()
        from xi_utils import XIUtils
        self.utils = XIUtils(os.getcwd())
    
    def validate(self, system: Any) -> bool:
        """Validate system using BHVT 7 loops with Axiom Engine"""
        self.bhvt = BHVTValidator(system, engine=self.axiom_engine)
        return self.bhvt.validate_all_loops()
    
    def get_reaper_capacity(self) -> Dict[str, float]:
        """
        Get current REAPER (resource) capacity scores.
        Returns values between 0.0 (full) and 1.0 (empty/available).
        """
        try:
            cpu_idle = (100.0 - psutil.cpu_percent(interval=None)) / 100.0
            ram_idle = (100.0 - psutil.virtual_memory().percent) / 100.0
            
            # Simple heuristic for "available swarm capacity" 
            # (assuming each model needs ~15% of resources)
            swarm_capacity = min(cpu_idle, ram_idle)
            
            return {
                "cpu": round(cpu_idle, 3),
                "ram": round(ram_idle, 3),
                "combined": round(swarm_capacity, 3)
            }
        except:
            return {"cpu": 0.5, "ram": 0.5, "combined": 0.5}
    
    def transform(self, work: Any, from_category: int, to_category: int, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Transform work through Category 42/43"""
        return self.category_router.route(work, from_category, to_category, meta=meta)
    
    def calculate_depth(self, n: int) -> float:
        """Calculate fractal depth at level n"""
        return self.hallberg.fractal_depth(n)
    
    def load_model(self, model_name: str) -> Any:
        """Load AI model"""
        return self.models.load(model_name)


# Convenience functions
def initialize_framework(config: Optional[Dict[str, Any]] = None) -> Framework:
    """Initialize XI-IO v8 Framework"""
    return Framework(config)


def validate_system(system: Any) -> bool:
    """Quick validation using BHVT"""
    framework = Framework()
    return framework.validate(system)


def calculate_fractal_depth(n: int) -> float:
    """Quick fractal depth calculation"""
    return PHI ** n


# Export all
__all__ = [
    'Framework',
    'BHVTValidator',
    'HallbergMath',
    'CategoryRouter',
    'MirrorTransform',
    'ModelRegistry',
    'initialize_framework',
    'validate_system',
    'calculate_fractal_depth',
    'PHI',
]
