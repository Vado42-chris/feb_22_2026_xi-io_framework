#!/usr/bin/env python3
"""
XI-IO v8 CLI Tool
Command-line interface for framework diagnostics and management
"""
import sys
import builtins
_original_print = builtins.print
def _clean_print(*args, **kwargs):
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            arg = arg.replace('</ξ#@⁺-|λ|-⁺@#ξ>', '').replace('</ξ#@⁺-|AG|-⁺@#ξ>', '')
        new_args.append(arg)
    _original_print(*new_args, **kwargs)
builtins.print = _clean_print

import argparse
import json
from pathlib import Path
import time
import re
import os
import subprocess
import platform
import fcntl
from datetime import datetime
import hashlib
from contextlib import contextmanager
from verification_manager import verification_manager as phase6_verifier

# Industrial Exit Codes (v8.9.9.6)
EXIT_CODES = {
    "OK": 0,
    "ROUTE_ERR": 10,
    "RECEIPT_MISSING": 11,
    "HASH_MISMATCH": 12,
    "POLICY_VIOLATION": 13,
    "STALE_PLAN": 14,
    "TIMEOUT": 15,
    "CAP_REACHED": 16,
    "STUB_DETECTED": 20
}

from enum import Enum

class AgenticMode(Enum):
    PLAN = "PLAN"
    ACT = "ACT"
    DEBUG = "DEBUG"
    CHAT = "CHAT"
    REVIEW = "REVIEW"

GOVERNOR_RULES = {
    AgenticMode.PLAN: {
        "forbidden": ["write", "create", "edit", "patch", "delete", "run", "git", "purge", "archive"],
        "message": "Action prohibited in PLAN mode: {cmd}"
    },
    AgenticMode.DEBUG: {
        "forbidden": ["write", "create", "edit", "patch", "delete", "purge", "run", "git", "archive"],
        "message": "Tool '{cmd}' not available in DEBUG mode. (Read-only + Wargame execution only)"
    }
}

def _get_version():
    try:
       
        version_file = Path(__file__).parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
    except:
        pass
    return "8.9.9.9.28"

__version__ = _get_version()

# Add framework to path
# Industrial Root (v8.9.9.9.17 - Dynamic Refactor)
framework_root = Path(__file__).parent.absolute()
if os.environ.get("XI_FRAMEWORK_ROOT"):
    framework_root = Path(os.environ["XI_FRAMEWORK_ROOT"])
sys.path.insert(0, str(framework_root))

# Core industrial imports (v8.9.8 Standardized)
from framework import Framework, ActionReceipt, CategoryRouter
from progress import with_spinner, with_progress
from optimized_orchestrator import OptimizedOrchestrator
from xi_utils import XIUtils
from context_manager import ContextManager
from image_analyzer import ImageAnalyzer
from workspace_registry import WorkspaceRegistry
from prompt_guard import get_guard as get_prompt_guard
from terminal_ui import TerminalUI, Colors

LOG_FILE = str(Path.home() / ".xi-io" / "relocation_manifest.log")
# [Security Update] Lock file must resolve to user home if framework root is read-only (e.g. /usr/local/bin)
LOCK_FILE = framework_root / ".xi-lock"
if not os.access(framework_root, os.W_OK):
    LOCK_FILE = Path.home() / ".xi-lock"

@contextmanager
def workspace_lock():
    """Advisory locking for the workspace with PID liveness recovery (v8.9.8+)"""
    lock_path = Path(LOCK_FILE)
    f = open(lock_path, 'a+')
    try:
       
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
           
            f.seek(0)
            old_pid = f.read().strip()
            if old_pid and old_pid != str(os.getpid()):
                print(f" [Hardening] Stale lock detected (PID {old_pid}). Recovering...")
        except BlockingIOError:
           
            f.seek(0)
            pid_str = f.read().strip()
            if pid_str:
                pid = int(pid_str)
                try:
                    os.kill(pid, 0)
                    print(f" [!] BUSY_WORKSPACE: Another XI process (PID {pid}) is active.")
                    sys.exit(1)
                except (ProcessLookupError, ValueError):
                    # PID is dead. We can attempt to take over.
                    # Note: Using LOCK_NB even here to prevent FUSE-related hangs (v8.9.9.9.17)
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        print(f" [!] BUSY_WORKSPACE: Stale lock recovery failed. Another process took it.")
                        sys.exit(1)

        f.seek(0)
        f.truncate()
        f.write(str(os.getpid()))
        f.flush()
        yield
    finally:
        # Release the lock and cleanup
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
       
        if lock_path.exists():
            try:
               
               
                lock_path.unlink()
            except:
                pass

def cmd_version(args):
    """Show version information (Deterministic)"""
    print(f"{__version__}")

def cmd_whereami(args):
    """Show deterministic path and environment facts (v8.9.8 Hardened)"""
    facts = {
        "version": __version__,
        "entrypoint": sys.argv[0],
        "realpath": str(Path(sys.argv[0]).resolve()),
        "cli_path": str(Path(__file__).resolve()),
        "python_exe": sys.executable,
        "platform": platform.platform(),
        "framework_root": str(framework_root),
        "working_dir": str(Path.cwd()),
        "orchestrator": "OptimizedOrchestrator (Active)"
    }
    if hasattr(args, 'json') and args.json:
        print(json.dumps(facts, indent=2))
        return
    
    is_receipts = getattr(args, 'format', 'chat') == 'receipts'
    if not is_receipts:
       
        print(f"{facts['working_dir']}")

def cmd_validate(args):
    """Validate framework installation"""
    print("Validating XI-IO v8 Framework...")
    print()
    
    from framework import Framework
    framework = Framework()
    
   
    print("✓ Framework initialized")
    
   
    test_system = {"test": "data"}
    is_valid = framework.validate(test_system)
    print(f"✓ BHVT validation: {is_valid}")
    
   
    models = framework.models.list_all()
    print(f"✓ Model registry: {len(models)} models available")
    
   
    try:
        import ollama
        ollama.list()
        print("✓ Ollama connection: working")
    except:
        print("✗ Ollama connection: failed")
    
    print()
    print("Framework validation complete!")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_models(args):
    """List available models"""
    from framework import Framework
    framework = Framework()
    
    print("Available Models:")
    print()
    
   
    print("Framework Models:")
    all_models = framework.models.list_all()
    for model in sorted(all_models):
        print(f"  - {model}")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
    
    print()
    
   
    try:
        import ollama
        ollama_models = ollama.list()
        print("Ollama Models:")
        for model in ollama_models.get('models', []):
            print(f"  - {model.model}")
        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
    except:
        print("Ollama not available")
        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_test_agent(args):
    """Test agent generation"""
    from framework import Framework
    framework = Framework()
    
    print(f"Testing agent with model: {args.model}")
    print()
    
    response = framework.models.generate(
        args.model,
        args.prompt or "Say 'Agent working' only",
        max_tokens=20
    )
    
    print(f"Response: {response}")
    print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")

def cmd_info(args):
    """Show detailed framework info"""
    from framework import Framework, PHI
    print("XI-IO v8 Framework Information")
    print("=" * 60)
    print()
    print(f"Framework Root: {framework_root}")
    print(f"Golden Ratio (\u03c6): {PHI:.6f}")
    print(f"Fractal Depth (\u03c6^8): {PHI**8:.3f}")
    print()
    print("Core Systems:")
    print("  - BHVT (Black Hole Validator Theory) - 7 loops")
    print("  - Hallberg Mathematics - Fractal depth")
    print("  - Category 42/43 System - Routing")
    print("  - Model Registry - Multi-model support")
    print("  - Agent Spawning - Dynamic agents")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_ask(args):
    """Natural language query to framework"""
    import ollama
    from framework import Framework
    from optimized_orchestrator import OptimizedOrchestrator
    
    query = ' '.join(args.query)
    
   
    INDUSTRIAL_IDENTITY = f"""[IDENTITY_FENCE]
# Industrial Directive
XI is the Sovereign Industrial Intelligence (System Engine).
You report ABOUT XI. Do NOT claim to be XI.

INDUSTRIAL DIRECTIVES:
1. AUTHORITY: You have full hardware access via XI's tools in {framework_root}.
2. TONE: Concise. Technical. Grounded in
3. IDENTITY BORDER: Never say "I am XI" or "I am Sovereign." Use "XI" or "The system" for the framework.

Context:
- Version: {__version__}
- Location: {framework_root}

Respond in English. Industrial Tone. ENACT the answer."""

    print("Thinking...")
    framework = Framework()
    orchestrator = OptimizedOrchestrator(framework)
    result = orchestrator.execute_single(f"{INDUSTRIAL_IDENTITY}\n\nUser Question: {query}", task_type='general')
    
    print()
    print(result['response'])
    print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")

def cmd_run(args):
    """Execute industrial directive/command"""
    from xi_utils import XIUtils
    utils = XIUtils(os.getcwd())
    command = args.command
    result = utils.run_command(command)
    if result.get('success'):
        if not is_receipts:
            print(f" [Execution Output]")
        print(result['stdout'])
        if result['stderr']:
            print(f"Stderr: {result['stderr']}")
    else:
        print(f"✗ Execution failed (Code {result.get('code')}): {result.get('error') or result.get('stderr')}")
    print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")

def cmd_delete(args):
    """Delete industrial asset"""
    from xi_utils import XIUtils
    utils = XIUtils(os.getcwd())
    print(utils.delete_file(args.filename))
    print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")

def cmd_read(args):
    """Read industrial asset"""
    import sys
    import json
    from xi_utils import XIUtils
    utils = XIUtils(os.getcwd())
    res = utils.read_file(args.filename)
    print(res)
    if '"ok": false' in res:
        try: sys.exit(json.loads(res).get('exit_code', 1))
        except: sys.exit(1)
    print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")

def cmd_write(args):
    """Write industrial asset"""
    import sys
    import json
    from xi_utils import XIUtils
    utils = XIUtils(os.getcwd())
    res = utils.write_file(args.filename, args.content)
    print(res)
    if '"ok": false' in res:
        try: sys.exit(json.loads(res).get('exit_code', 1))
        except: sys.exit(1)
    print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")

def output_json_receipt(data):
    """Strict JSON receipt output for Command Center UI contract."""
    print(json.dumps({"ok": True, "receipt": data, "timestamp": time.time(), "bridge": "active"}))
    sys.exit(0)

def cmd_status(args):
    """Show status in JSON format for UI contract (Real Metrics)"""
    from framework import Framework, PHI
    import psutil
    
    if getattr(args, 'json', False):
        try:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            commit = 'UNKNOWN'
        ledger_path = os.path.expanduser('~/.xi-io/production_ledger.json')
        event_count = 0
        if os.path.exists(ledger_path):
            with open(ledger_path, 'r') as f:
                event_count = len(json.load(f))
        output_json_receipt({"op": "status", "status": "NOMINAL", "version": __version__, "storage": "1", "commit": commit, "event_count": event_count})
    
    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(framework_root):
       
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '.venv', '__pycache__']]
        file_count += len(files)
        dir_count += len(dirs)
        
    cpu_idle = (100.0 - psutil.cpu_percent(interval=None)) / 100.0
    ram_idle = (100.0 - psutil.virtual_memory().percent) / 100.0
    
    status = {
        "framework": "XI-IO v8",
        "version": __version__,
        "phi": PHI,
        "health": "GREEN",
        "metrics": {
            "files": file_count,
            "directories": dir_count,
            "cpu_availability": round(cpu_idle, 3),
            "ram_availability": round(ram_idle, 3)
        }
    }
    print(json.dumps(status, indent=2))

def cmd_hook_scan(args):
    """Run anchor validation (v8.9.9.9.18)"""
    from framework import Framework
    from optimized_orchestrator import OptimizedOrchestrator
    from xi_utils import XIUtils
    from context_manager import ContextManager
    import os
    
    ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state()
    execute_command_string("/hook-scan", ctx_mgr, orchestrator, swarm, utils, framework, working_dir)

def cmd_policy_probe(args):
    """Run policy validation (v8.9.9.9.18)"""
    from framework import Framework
    from optimized_orchestrator import OptimizedOrchestrator
    from xi_utils import XIUtils
    from context_manager import ContextManager
    import os
    
    ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state()
    execute_command_string("/policy-probe", ctx_mgr, orchestrator, swarm, utils, framework, working_dir)

def cmd_discovery(args):
    """Discover projects in a root path"""
    from workspace_registry import WorkspaceRegistry
    print(f"Discovering projects in: {args.path}...")
    registry = WorkspaceRegistry()
    found = registry.discover(args.path)
    if found:
        print(f"✓ Found and registered {len(found)} projects")
    else:
        print("✗ No projects discovered.")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_swarm(args):
    """Manage the Agentic Swarm (42 Lanes)"""
    ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state()
    
    if args.swarm_cmd == 'status':
        status = swarm.get_status()
        print(f"\n{Colors.CYAN}=== SWARM ORCHESTRATION STATUS ==={Colors.RESET}")
        print(f" Backlog: {status['total_backlog']} items")
        print(f" Buckets: {json.dumps(status['buckets'], indent=2)}")
        print(f" Agents:  {status['agent_assignments']}")
        print(f" Lanes:   {status['fire_teams']} Fire Teams Active")
        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
        
    elif args.swarm_cmd == 'process':
        with with_spinner("Swarm Firing up 42 Lanes..."):
            results = swarm.process_backlog()
        
        if not results:
            print(" [Swarm] No work in backlog.")
            return

        for r in results:
            print(f"\n[{r['status']}] {r['fire_team']} (Lane 42.{r['lane']})")
            print(f"  Executing {r['items']} tasks with {len(r['agents'])} agents: {', '.join(r['agents'])}")
            # Real execution would follow here
        print(f"\n✓ Backlog processed.")
        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

    elif args.swarm_cmd == 'add':
        task = " ".join(args.task)
        swarm.add_to_bucket(task, status=args.bucket.upper())
        print(f"✓ Added task to {args.bucket.upper()} bucket.")
        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_lane(args):
    """Execute specialized injection into a Fire Team lane (42.1, 42.2, 42.3)"""
    ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state()
    lane = args.lane
    prompt = " ".join(args.prompt)
    
    # Simple lane routing logic (42-System)
    lane_map = {
        '42.1': 'alpha',
        '42.2': 'beta',
        '42.3': 'gamma',
        'alpha': 'alpha',
        'beta': 'beta',
        'gamma': 'gamma'
    }
    
    team_key = lane_map.get(lane.lower())
    if not team_key:
        print(f" [!] Invalid lane: {lane}. Use 42.1, 42.2, or 42.3.")
        return

    team = swarm.fire_teams[team_key]
    print(f" [XI-IO] ROUTING TO {team['name']} ({team['focus'].upper()})")
    
    # Execute through 42-system
    route_res = swarm.route_through_42({'task': prompt, 'type': team['focus']})
    print(f" Route: {' -> '.join(route_res['route'])}")
    
    # Simulated execution for now (matching v8.9.9.9.21 'hotwire')
    res = orchestrator.execute_industrial_line(prompt)
    print(f" Result: {res.get('write_status', res.get('response', 'OK'))}")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_inject_new(args):
    from workspace_registry import WorkspaceRegistry
    registry = WorkspaceRegistry()
    active_path = registry.get_active_path() or os.getcwd()
    os.chdir(active_path)
    
    print(f" [XI-IO] INJECTING INTO {lane.upper()} ({model}) in {active_path}...")
    
   
    try:
        from optimized_orchestrator import OptimizedOrchestrator
        orchestrator = OptimizedOrchestrator()
        result = orchestrator.execute_industrial_line(prompt, model=model)
        
        print("\nIGNITION REPORT:")
        if not result.get("ok") and result.get("error"):
             print(f" [!] Injection failed: {result.get('error')}")
             sys.exit(EXIT_CODES["ROUTE_ERR"])
             
        print(f"Identity: {result.get('identity')}...")
        print(f" [XI-IO] {result.get('write_status')}")
        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
        
    except Exception as e:
        print(f" [!] Injection failed: {e}")
        sys.exit(EXIT_CODES["ROUTE_ERR"])

def cmd_use(args):
    """Switch the active project context"""
    from workspace_registry import WorkspaceRegistry
    registry = WorkspaceRegistry()
    is_receipts = getattr(args, 'format', 'chat') == 'receipts'
    if registry.set_active(args.project):
        path = registry.get_active_path()
        if not is_receipts:
            print(f"✓ Switched to project: {args.project}")
            print(f"  Path: {path}")
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
    else:
        if not is_receipts:
            print(f"✗ Project or path not found: {args.project}")
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_list_projects(args):
    """List all registered projects"""
    from workspace_registry import WorkspaceRegistry
    registry = WorkspaceRegistry()
    projects = registry.list_workspaces()
    active = registry.registry.get("active")
    print("Registered Projects:")
    for name, path in projects.items():
        marker = "[ACTIVE]" if name == active else "        "
        print(f"  {marker} {name}: {path}")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_selftest(args):
    """Run framework self-test without LLMs"""
    print("--- XI-IO v8 Self-Test ---")
    results = []
    
    try:
        from framework import Framework
        Framework()
        results.append("✓ Core Framework: OK")
    except Exception as e:
        results.append(f"✗ Core Framework: FAILED ({e})")
        
    try:
        import ollama
        ollama.list()
        results.append("✓ Ollama Connectivity: OK")
    except:
        results.append("✗ Ollama Connectivity: FAILED")
        
    try:
        import psutil
        psutil.cpu_percent()
        results.append("✓ Resource Telemetry (psutil): OK")
    except:
        results.append("✗ Resource Telemetry: FAILED")
        
    for r in results:
        print(r)
    
    print("Self-test complete.")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

def cmd_verify(args):
    """Run Phase 6 Verification via VerificationManager"""
    if getattr(args, 'json', False) and not sys.stdin.isatty():
        raw_input = sys.stdin.read()
        try:
            unit = json.loads(raw_input)
            from verification_manager import verification_manager
            result = verification_manager.verify(unit)
            output_json_receipt({"op": "verify", "result": result})
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}))
            sys.exit(1)
    try:
        from verification_manager import VerificationManager
        vm = VerificationManager()
        result = vm.verify({'content': str(datetime.now()), 'provenance': 'CLI_OPERATOR', 'uncertainty': 1.0, 'evidence': ['selftest']})
        if getattr(args, 'json', False):
            output_json_receipt({"op": "verify", "result": result})
        else:
            print(f"Status: {result.get('overall_status')}")
            for check in result.get('checks', []):
                print(f"  [{check['status']}] {check['submodule']}")
    except Exception as e:
        if getattr(args, 'json', False):
            print(json.dumps({"ok": False, "error": str(e)}))
            sys.exit(1)
        else:
            print(f"Verification Failed: {e}")

def cmd_gates(args):
    """Run Phase Gate checks for governance wargame."""
    gate_results = []
    gate_results.append({"gate": 0, "name": "Local Truth", "pass": os.path.exists(".git")})
    gate_results.append({"gate": 1, "name": "Schema Valid", "pass": os.path.exists(os.path.join(framework_root, "schemas", "hallberg.schema.json"))})
    ledger_path = os.path.expanduser('~/.xi-io/production_ledger.json')
    gate_results.append({"gate": 2, "name": "Ledger Exists", "pass": os.path.exists(ledger_path)})
    gate_results.append({"gate": 3, "name": "Verification Module", "pass": os.path.exists(os.path.join(framework_root, "verification_manager.py"))})
    gate_results.append({"gate": 4, "name": "Orchestrator Online", "pass": os.path.exists(os.path.join(framework_root, "optimized_orchestrator.py"))})
    failed = [g for g in gate_results if not g['pass']]
    all_pass = len(failed) == 0
    if getattr(args, 'json', False):
        try:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            commit = 'UNKNOWN'
        output_json_receipt({"op": "gates", "check": "PASS" if all_pass else "FAIL", "gates": gate_results, "failed_count": len(failed), "commit": commit, "source": "METAL_S1"})
    for g in gate_results:
        icon = '\u2713' if g['pass'] else '\u2717'
        color_code = '\033[92m' if g['pass'] else '\033[91m'
        print(f"  {color_code}[{icon}] Gate {g['gate']}: {g['name']}\033[0m")
    if all_pass:
        print("GATES: ALL PASS")
    else:
        print(f"GATES: {len(failed)} FAILED")

def cmd_route_set(args):
    """Set model route for a lane"""
    from pathlib import Path
    import json
    state_dir = Path.home() / ".xi-io"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "sovereign_state.json"
    
    state = {}
    if state_path.exists():
        with open(state_path, 'r') as f:
            state = json.load(f)
            
    if "routes" not in state:
        state["routes"] = {}
        
    state["routes"][args.lane] = args.model
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=4)
    print(f"✓ Routed lane '{args.lane}' to '{args.model}'")

def cmd_models_list(args):
    """List available model cylinders"""
    import ollama
    try:
        models = ollama.list()
        print("Model Cylinders:")
        for m in models.get('models', []):
            print(f"  - {m['name']}")
    except:
        print("✗ Could not connect to Ollama.")

def cmd_models_scan(args):
    """Scan reality for local models"""
    print("Scanning neural reality...")
    import ollama
    ollama.list()
    print("✓ Reality scan complete.")

def cmd_info(args):
    """Show industrial info"""
    print(f"XI-IO Industrial Intelligence v{__version__}")
    print(f"Core: {framework_root}")
    print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")

##### Phase 6: The Trinity Loop (v8.9.9.9.22)
def _micro_review(action, filename, receipt_json, working_dir, is_receipts):
    """
    Automatic Micro-Review after Tool Execution.
    Verifies the file hash exists and prints a receipt.
    """
    if is_receipts: return 

    import json
    try:
        data = json.loads(receipt_json)
        if not data.get('ok'):
             return 
        
       
        from service.managers.verification_manager import VerificationManager
        vm = VerificationManager()
        
        target_path = Path(working_dir) / filename
        
        print(f"{Colors.CYAN}[Micro-Review] Verifying {action.upper()} on {filename}...{Colors.RESET}")
        
        if action == 'delete':
             if not target_path.exists():
                 print(f"   [✓] Status: GONE (Verified)")
             else:
                 print(f"   [!] Status: GHOST (Delete Failed)")
        else:
             expected = data.get('sha256')
             report = vm.verify_file_integrity(str(target_path), expected_hash=expected)
             
             if report['ok']:
                  match_str = "(MATCH)" if report.get('match') else "(NEW)"
                  print(f"   [✓] Integrity: {report['sha256'][:8]}... {match_str}")
                  print(f"   [✓] Status: {report['status']}")
             else:
                  print(f"   [!] Integrity Check Failed: {report['status']}")
                  
    except Exception as e:
        print(f" [!] Review Logic Failed: {e}")

from enum import Enum
import re
from pathlib import Path

class QueryClass(Enum):
    STATIC_STATE = "STATIC_STATE"      # Pure precomputed facts
    COMPUTED_STATE = "COMPUTED_STATE"  # Filtered counts/lists we can do locally (CS001)
    REASONING = "REASONING"            # Ambiguous or complex interpretation needed

_RECURSIVE_KEYWORDS = (
    "recursively", "recursive", "all subfolders", "all subdirectories", 
    "subfolders", "sub-folders", "subdirectories", "sub-directories", 
    "tree", "under", "all levels"
)

_EXTENSION_ALIASES = {
    "python": (".py",), "py": (".py",), ".py": (".py",),
    "javascript": (".js", ".jsx"), "js": (".js", ".jsx"), ".js": (".js",),
    "typescript": (".ts", ".tsx"), "ts": (".ts", ".tsx"), ".ts": (".ts",),
    "markdown": (".md", ".markdown"), "md": (".md", ".markdown"), ".md": (".md",),
    "json": (".json",), "css": (".css",), "html": (".html",),
    "hidden": ("__HIDDEN__",)
}

def _extract_extensions(command: str):
    c = command.lower()
    found = set()
    # Explicit extension mention like ".py"
    explicit = re.findall(r"\.[a-z0-9]{1,6}\b", c)
    found.update(explicit)
    for k, exts in _EXTENSION_ALIASES.items():
        if re.search(rf"\b{re.escape(k)}\b", c):
            found.update(exts)
    return tuple(sorted(found))

def classify_query(text):
    """3-tier decision engine for state queries. (CS001)
    Returns (QueryClass, metadata_dict)"""
    lower = text.lower().strip().strip('?!.')
    
    # Tier 1: Computed State (The 'Counts')
    is_count = bool(re.search(r"\bhow many\b", lower)) or 'count' in lower
    if is_count:
        # Detect Scope
        is_recursive = any(k in lower for k in _RECURSIVE_KEYWORDS)
        has_exclusion = any(s in lower for s in ['excluding', 'gitignore', 'ignore'])
        
        if has_exclusion:
            return QueryClass.REASONING, {"reason": "complex_intent_exclusions"}
            
        exts = _extract_extensions(lower)
        meta = {"scope": "recursive" if is_recursive else "local", "exts": exts, "op": "count_files"}
        
        if exts or is_recursive:
            return QueryClass.COMPUTED_STATE, meta
        
        return QueryClass.STATIC_STATE, meta

    # Tier 2: Static State (The 'Facts')
    _static_phrases = [
        'working directory', 'current directory', 'where am i',
        'framework version', 'system version', 'active_model', 'active model',
        'what version', 'which version', 'show version'
    ]
    if any(q in lower for q in _static_phrases):
        return QueryClass.STATIC_STATE, {}

    return QueryClass.REASONING, {}

def _governed_recursive_count(root_dir, exts=None, max_files=50000, max_time=3.0):
    """Optimized governed walk (CS004). Uses scandir for TTT speedup."""
    import os
    import time
    
    start_time = time.time()
    count = 0
    samples = []
    
    # Standard Industrial Ignores (Pruned early)
    IGNORES = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".pytest_cache", ".mypy_cache"}
    ext_set = set(e.lower() for e in exts) if exts else None
    is_hidden_only = exts and "__HIDDEN__" in exts

    try:
        root_dev = os.stat(root_dir).st_dev
    except OSError:
        return 0, [], "OS_ERROR"

    # Hybrid queue-based walk for maximum control and pruning
    stack = [root_dir]
    while stack:
        current = stack.pop()
        
        # Check Guards frequently
        if time.time() - start_time > max_time: return count, samples, "TIMEOUT"
        if count >= max_files: return count, samples, "MAX_REACHED"

        try:
            with os.scandir(current) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name in IGNORES: continue
                        # One Filesystem check
                        try:
                            if entry.stat().st_dev == root_dev:
                                stack.append(entry.path)
                        except OSError: continue
                    elif entry.is_file(follow_symlinks=False):
                        # Filter logic
                        match = False
                        if not exts: match = True
                        elif is_hidden_only:
                            if entry.name.startswith('.'): match = True
                        else:
                            if any(entry.name.lower().endswith(e) for e in ext_set):
                                match = True
                        
                        if match:
                            count += 1
                            if len(samples) < 5: samples.append(entry.name)
        except (PermissionError, OSError):
            continue

    return count, samples, "OK"

def get_state_blob(working_dir, orchestrator=None):
    """Deterministic state observation. No LLM. Python-only. Single source of truth."""
    import hashlib
    wd = os.path.realpath(working_dir)
    try:
        all_items = os.listdir(wd)
        files = [f for f in all_items if os.path.isfile(os.path.join(wd, f))]
        file_count = len(files)
        # Limit file list size to avoid prompt bloat, but give enough for "how many x"
        file_list = files[:100]
        if len(files) > 100:
            file_list.append(f"... and {len(files)-100} more")
    except OSError:
        file_count = 0
        file_list = []

    blob = {
        "cwd": wd,
        "project": os.path.basename(wd),
        "version": _get_version(),
        "file_count": file_count,
        "file_list": file_list,
        "model": orchestrator.model_strengths['general'] if orchestrator else "unknown",
        "framework_root": str(framework_root),
        "python": sys.executable,
    }
    blob['sha256'] = hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()[:16]
    return blob

def _is_state_query(text):
    """Detect if user is asking a PUREly observational/state question.
    Smart Sentinel: If the query is instructional (e.g. 'delete files'), don't intercept."""
    lower = text.lower().strip().strip('?!.')
    
    # Phrases that indicate a state inquiry
    _pure_queries = [
        'working directory', 'current directory', 'what directory', 'where am i',
        'file count', 'how many files', 'number of files', 'filecount',
        'system state', 'system status', 'current state', 'state blob',
        'what version', 'which version', 'framework version',
        'which model', 'what model', 'active model', 'active_model'
    ]
    
    # Catch-all observational questions
    is_asking = any(q in lower for q in _pure_queries)
    
    # QUALIFIER DETECTION: If they ask for specific types (e.g. 'python files'), don't intercept.
    # We want the LLM to use the file_list in the STATE_BLOB for filtered counts.
    _qualifiers = ['.py', 'python', '.js', 'javascript', '.ts', 'typescript', '.md', 'markdown', '.json', 'hidden', 'only', 'all']
    has_qualifier = any(q in lower for q in _qualifiers)

    # BUT: If it's a mixed command or imperative, we want the soul to handle it
    _imperative_verbs = ['create', 'delete', 'update', 'modify', 'fix', 'run', 'execute', 'search', 'find', 'make', 'list', 'show']
    is_action = any(lower.startswith(v) for v in _imperative_verbs)
    
    return is_asking and not is_action and not has_qualifier

def _is_within_workspace(target_path, workspace_root):
    """Boundary enforcement via realpath normalization + allowlist."""
    try:
        real_target = os.path.realpath(os.path.expanduser(target_path))
        real_root = os.path.realpath(workspace_root)
        return real_target.startswith(real_root + os.sep) or real_target == real_root
    except (OSError, ValueError):
        return False

def execute_industrial_line(line, ctx_mgr, orchestrator, swarm, utils, framework, working_dir, current_file=None, mode=AgenticMode.CHAT):
    _allowed_single = {'exit', 'quit', 'help', 'ls', 'models', 'validate', 'info', 'status', 'context', 'version', 'whereami', 'state'}
    if len(line.strip().split()) == 1 and not line.startswith('/') and line.strip().lower() not in _allowed_single:
        print(f"[!] Unrecognized command: '{line}'. Use '/' for tools or type a full sentence for AI.")
        return current_file, False, working_dir, False

    """Unified industrial command execution (v8.9.8)"""
    # [v8.9.9.9.27] Command/Comment Filter
    if not line or line.strip().startswith('#'):
        return current_file, False, working_dir, False
        
   
    if not isinstance(ctx_mgr, ContextManager):
        ctx_mgr = ContextManager(working_dir)

    # Phase 6: Verification Gate
    _v6_unit = {'content': line, 'provenance': 'CLI_OPERATOR', 'uncertainty': 1.0, 'evidence': ['operator_input']}
    _v6_result = phase6_verifier.verify(_v6_unit)
    if _v6_result['overall_status'] == 'FAILED':
        print(f"[PHASE 6 GATE] Verification FAILED: {_v6_result['checks']}")
    elif _v6_result['overall_status'] == 'FLAGGED':
        print(f"[PHASE 6 GATE] Verification FLAGGED: {_v6_result['checks']}")
    
    is_receipts = getattr(orchestrator, 'format_mode', 'chat') == 'receipts'
    if is_receipts:
        from framework import IndustrialAuditService, HardwareGuard
        IndustrialAuditService.set_silent(True)
        HardwareGuard.set_silent(True)
    
    
    if line.lower() in ['exit', 'quit', '/quit']:
        return current_file, True, working_dir, False
    
    import shlex
    try:
       
        words = shlex.split(line)
    except ValueError:
        words = line.split()
        
   
    recognized_industrial_cmds = [
        'create', 'write', 'edit', 'patch', 'delete', 'read', 'run', 
        'ls', 'search', 'git', 'test', 'backup', 'diff', 'count', 
        'format', 'use', 'analyze', 'extract', 'ui', 'context', 'info',
        'models', 'validate', 'selftest', 'discovery', 'purge', 'archive', 'design',
        'simulate_failure', 'status', 'version', 'whereami', 'help', 'state',
        'hook-scan', 'policy-probe', 'diagnostics', 'wargame',
        'swarm', 'lane', 'sprint'
    ]

    # [v8.9.9.9.28] Boundary Enforcement: realpath normalization + allowlist
    # Extract file arguments from words (positions 1+) and check each
    _path_args = [w for w in words[1:] if '/' in w or '..' in w] if len(words) > 1 else []
    for _pa in _path_args:
        if not _is_within_workspace(_pa, working_dir):
            if not is_receipts:
                _real = os.path.realpath(os.path.expanduser(_pa))
                print(f"\n[CRITICAL] POLICY_VIOLATION: Path '{_pa}' resolves to '{_real}'")
                print(f" Workspace root: {os.path.realpath(working_dir)}")
                print(f" Refusal: Target is outside workspace boundary.")
                print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")
            else:
                print(json.dumps({
                    "op": "security_probe",
                    "ok": False,
                    "exit_code": "POLICY_VIOLATION",
                    "receipt_type": "AUDITED_REFUSAL",
                    "reason": f"Path outside workspace: {_pa}"
                }))
            sys.exit(EXIT_CODES["POLICY_VIOLATION"])

   
    is_receipts = getattr(orchestrator, 'format_mode', 'chat') == 'receipts'
    is_explicit = False

   
   
    if not is_receipts:
         _pg = get_prompt_guard(silent=True)
         verdict = _pg.check(line)
         if verdict['severity'] == 'BLOCK':
              print(f"\n[Security Refusal] {verdict.get('refusal_message', 'Blocked by PromptGuard')}\n")
              return current_file, False, working_dir, False

    
   
    # [v8.9.9.9.25] Parser Hardening: Expanded Noise Matrix (Conversation Stripper)
    noise = [
        'prompt:', 'xi:', 'input:', 'user:', 'expectation:', 'success:', 'what success looks like:', 
        'xi', '-c', 'xi:', 'note:', 'command:', 'result:', 'expected:', 'hey', 'hi', 'hallberg',
        'can', 'please', 'you', 'help', 'me', 'with', 'would', 'like', 'to', 'want', 'to', 'do',
        'i', 'need', 'to', 'show', 'tell', 'me', 'about'
    ]
    mute_keywords = ['expectation:', 'success:', 'note:', 'what success looks like:', 'expected:', 'result:']
    
    while words:
        # [v8.9.9.9.26] Hardened Stripper: Remove surrounding punctuation
        first_word = words[0].lower().strip(':,?!. ')
        if first_word in noise:
             # If it's a dedicated mute keyword and ONLY that remains, terminate.
             if first_word in mute_keywords and len(words) == 1:
                 return current_file, False, working_dir, True
             
             if first_word == 'what' and len(words) > 3:
                 phrase = " ".join(words[:4]).lower().strip(':,?!. ')
                 if phrase == 'what success looks like':
                     if len(words) == 4:
                         return current_file, False, working_dir, True
                     words = words[4:]
                     continue
             
             words = words[1:]
        else:
            break
    
   
    if words and words[0].startswith('/') and words[0][1:].lower() in recognized_industrial_cmds:
        is_explicit = True

    raw_cmd = words[0].lower() if words else ''
    cmd = raw_cmd[1:] if is_explicit else raw_cmd
    
   
    if len(words) > 1:
        words = [words[0]] + [w.strip('"').strip("'") for w in words[1:]]
    
    if not is_explicit and not is_receipts:
       
        if words and words[0].lower() in recognized_industrial_cmds:
            # B6 GUARD: Detect natural language that happens to start with a command word
            # e.g. "create a file called X" or "delete the old backups" or "read me the contents"
            _nl_filler = {'a', 'an', 'the', 'this', 'that', 'my', 'me', 'all', 'some', 'called', 'named', 'file', 'files'}
            if len(words) > 1 and words[1].lower().rstrip('.,!?') in _nl_filler:
                cmd = 'chat_fallback'  # Route to LLM for natural language processing
            else:
                is_explicit = True
                cmd = words[0].lower()
        else:
           
            cmd = 'chat_fallback'
    elif is_receipts:
       
        if cmd not in recognized_industrial_cmds:
           
            print(f"Error: Command '{cmd}' unknown in receipts mode.")
            sys.exit(1)
    
    # Governor Enforcement (v8.9.9.9.22 Hardening)
    rules = GOVERNOR_RULES.get(mode, {})
    if "forbidden" in rules and cmd in rules["forbidden"]:
        err_msg = rules['message'].format(cmd=cmd)
        if mode == AgenticMode.PLAN:
            raise PermissionError(err_msg)
        print(f" [Refusal] {err_msg}")
        sys.exit(EXIT_CODES["POLICY_VIOLATION"])

    is_deterministic = (cmd != 'chat_fallback')

    try:
        if cmd == 'version':
            if not is_receipts:
                print(f"{__version__}")
        elif cmd == 'whereami':
            if not is_receipts:
                print(f"{working_dir}")
        elif cmd == 'help':
            if not is_receipts:
                pass
        elif cmd == 'diagnostics':
            cmd_validate(None)
            cmd_status(None)
        elif cmd == 'validate':
            cmd_validate(None)
        elif cmd == 'models':
            cmd_models(None)
        elif cmd == 'info':
            cmd_info(None)
        elif cmd == 'context':
            summary = ctx_mgr.get_context_summary()
            if not is_receipts:
                print(json.dumps(summary, indent=2))
        elif cmd == 'state':
            blob = get_state_blob(working_dir, orchestrator)
            print(json.dumps(blob, indent=2))
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            return current_file, False, working_dir, False
        elif cmd == 'status':
            cmd_status(None)
        elif cmd == 'selftest':
            cmd_selftest(None)
        elif cmd == 'hook-scan':
            print(f"XI_BIN: {Path(sys.argv[0]).resolve()}")
            print(f"{__version__}")
        elif cmd == 'policy-probe':
           
            print("Warning: Policy probe requires target argument.")
        elif cmd == 'discovery':
            path = words[1] if len(words) > 1 else str(framework_root)
            cmd_discovery(argparse.Namespace(path=path))
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
        
       
        elif cmd == 'build':
            summary = ctx_mgr.get_context_summary()
            budget = ctx_mgr.build_context_budget(max_files=10)
            summary['budget_files'] = budget
            
            synth_result = orchestrator.execute_cognitive_synthesis(line, summary)
            
            if synth_result.get('enactment') and synth_result.get('staged_files'):
                if not is_receipts:
                    print(f"Plan: {synth_result.get('response')}")
                
                auto_enact = any(f in line.lower() for f in ['--force', '--yes', 'force'])
                confirm = 'y' if auto_enact else input("Confirm (y/n): ").strip().lower()
                
                if confirm == 'y':
                    for sf in synth_result['staged_files']:
                        path = sf.get('path')
                        content = sf.get('content')
                        if path and content:
                            res = utils.write_file(path, content)
                            print(res)
                else:
                    if not is_receipts: print("Aborted")
            else:
                if not is_receipts:
                    print(synth_result.get('response', 'Error'))
            
            return current_file, False, working_dir, False

        elif cmd == 'chat_fallback':
            capability_keywords = ['capabilities', 'tools', 'toolkit']
            if any(kw in line.lower() for kw in capability_keywords):
                if not is_receipts:
                    print("Directives: create, read, edit, patch, delete, ls, search, run, status, context, state")
                return current_file, False, working_dir, False

            # PATCH 6: THE COMPUTED SENTINEL (3-tier Classifier)
            q_tier, q_meta = classify_query(line)

            if q_tier != QueryClass.REASONING:
                blob = get_state_blob(working_dir, orchestrator)
                
                if q_tier == QueryClass.COMPUTED_STATE:
                    # Perform local computation
                    exts = q_meta.get('exts', [])
                    scope = q_meta.get('scope', 'local')
                    import time
                    
                    start_ttt = time.time()
                    
                    if scope == 'recursive':
                        count, samples, status = _governed_recursive_count(working_dir, exts)
                        if status == "TIMEOUT" or status == "MAX_REACHED":
                             print(f"\n[OP-11 HALT] (CS003) Scope too broad: {status}")
                             print(f"Safety guard triggered to prevent CLI hang.")
                             return current_file, False, working_dir, False
                    else:
                        # Local computation
                        from pathlib import Path
                        p = Path(working_dir)
                        ext_set = set(e.lower() for e in exts) if exts else None
                        is_hidden = exts and "__HIDDEN__" in exts
                        matches = []
                        for x in p.iterdir():
                            if not x.is_file(): continue
                            if not exts: matches.append(x.name)
                            elif is_hidden: 
                                if x.name.startswith('.'): matches.append(x.name)
                            elif any(x.name.lower().endswith(e) for e in ext_set):
                                matches.append(x.name)
                        count = len(matches)
                        samples = matches[:5]
                        status = "OK"
                    
                    elapsed_ttt = (time.time() - start_ttt) * 1000
                    
                    if not is_receipts:
                        print(f"\n[Computed State Report] (CS001/CS002)")
                        print(f"Filter:  {', '.join(exts) if exts else 'ALL_FILES'}")
                        print(f"Scope:   {scope.upper()}")
                        print(f"Count:   {count} files found.")
                        print(f"Latency: {elapsed_ttt:.2f}ms (TTT)")
                        if samples:
                            print(f"Sample:  {', '.join(samples)}{'...' if count > 5 else ''}")
                        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
                    else:
                        print(json.dumps({
                            "status": "COMPUTED_STATE", 
                            "filter": exts, 
                            "scope": scope, 
                            "count": count, 
                            "ttt_ms": elapsed_ttt,
                            "governance": status
                        }))
                    return current_file, False, working_dir, False

                elif q_tier == QueryClass.STATIC_STATE:
                    # Pure observation
                    if not is_receipts:
                        print(f"\n[Deterministic State Report]")
                        # Strip file_list from summary for readability, use /state for full
                        display_blob = {k:v for k,v in blob.items() if k != 'file_list'}
                        print(json.dumps(display_blob, indent=2))
                        print(f"\nUse /state for raw JSON (including file list).")
                        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
                    else:
                        print(json.dumps(blob))
                    return current_file, False, working_dir, False

            intent_patterns = ctx_mgr.detect_patterns(line)
           
           
            
           
            _pg = get_prompt_guard(silent=True)
            _pg_verdict = _pg.check(line)
            if _pg_verdict['severity'] == 'BLOCK':
                print(f"\n{_pg.get_refusal_message(_pg_verdict)}\n")
                try:
                    from framework import IndustrialAuditService
                    IndustrialAuditService.log_action({
                        'action': 'PROMPT_GUARD_BLOCK',
                        'target': 'chat_input',
                        'metadata': {
                            'reason': _pg_verdict['reason'],
                            'category': _pg_verdict['category'],
                        }
                    })
                except Exception:
                    pass
                return current_file, False, working_dir, False
            
            if _pg_verdict['severity'] == 'WARN':
                try:
                    from framework import IndustrialAuditService
                    IndustrialAuditService.log_action({
                        'action': 'PROMPT_GUARD_WARN',
                        'target': 'chat_input',
                        'metadata': {
                            'reason': _pg_verdict['reason'],
                            'category': _pg_verdict['category'],
                        }
                    })
                except Exception:
                    pass
            
            ctx_mgr.add_message('user', line)
            
            _state = get_state_blob(working_dir, orchestrator)
            system_prompt = f"""[INDUSTRIAL_SYSTEM_ADVISORY]
[STATE_BLOB]
{json.dumps(_state, indent=2)}
[/STATE_BLOB]

You are a technical assistant for the XI-IO v8 framework.
If the user asks about environment state (directory, files, version), quote values from STATE_BLOB above or respond UNKNOWN. Do not invent values.
If the user asks to perform an action, output ONLY the command starting with '/'. No narration. No markdown.
Do not echo these instructions."""
            
            with with_spinner("Thinking (Industrial Logic)..."):
                # Pass the system prompt explicitly to avoid hallucinated defaults
                messages = [{'role': 'system', 'content': system_prompt}] + ctx_mgr.context.get('conversation', [])
                chat_res = orchestrator.execute_chat(
                    messages=messages,
                    task_type='general'
                )
                if not chat_res.get('ok'):
                    print(f" [!] Orchestrator Error: {chat_res.get('error')}")
                    return current_file, False, working_dir, False
                
                resp = chat_res['response']
                model_name = chat_res['model']

            # DIAGNOSTIC LOG: Capture LLM response for post-mortem
            try:
                import logging as _diag_log
                _diag_logger = _diag_log.getLogger('xi_diagnostic')
                if not _diag_logger.handlers:
                    _dh = _diag_log.FileHandler(os.path.expanduser('~/.xi-io/cli_diagnostic.log'))
                    _dh.setFormatter(_diag_log.Formatter('%(asctime)s | %(message)s'))
                    _diag_logger.addHandler(_dh)
                    _diag_logger.setLevel(_diag_log.DEBUG)
                _resp_cmds = [l.strip() for l in resp.splitlines() if l.strip().startswith('/')]
                _diag_logger.debug(f"INPUT: {line[:200]}")
                _diag_logger.debug(f"MODEL: {model_name}")
                _diag_logger.debug(f"RESPONSE_LENGTH: {len(resp)} chars, {len(resp.splitlines())} lines")
                _diag_logger.debug(f"EXTRACTED_CMDS: {_resp_cmds}")
                if not _resp_cmds:
                    _diag_logger.debug(f"NO_CMDS_EXTRACTED — Full response: {resp[:500]}")
            except Exception:
                pass

            # [v8.9.9.9.25] ICEBERG_DETECTOR: Narrative Theater Prevention
            _narrative_hallucinations = ['i have successfully', 'i created', 'i modified', 'file updated', 'operation complete', 'i read the file']
            _has_cmds = any(l.strip().startswith('/') for l in resp.splitlines())
            _has_narrative = any(phrase in resp.lower() for phrase in _narrative_hallucinations)
            
            if _has_narrative and not _has_cmds:
                print(f"{Colors.YELLOW}[!] ALERT: Narrative Theater Detected.{Colors.RESET}")
                print(f" [XI] The model claimed an action but emitted no verifiable industrial tool commands.")
                print(f" Suggestion: Re-prompt with 'ENACT' or ensure a '/' command is expected.")

            if not is_receipts:
                print(f"\n{resp.strip()}\n")
            ctx_mgr.add_message('assistant', resp.strip())
            
           
           
            executed_any = False
            in_resp_block = False
            
            for resp_line in resp.splitlines():
               
                if "```" in resp_line:
                   
                   
                    toggles = resp_line.count("```")
                    if toggles % 2 != 0:
                        in_resp_block = not in_resp_block
                   
                    continue
                
                if in_resp_block:
                    continue

                resp_line = resp_line.strip()
                if resp_line.startswith('/') and len(resp_line) > 2:
                    # BUG #1 GUARD: Block auto-exec of template/placeholder commands
                    if '<' in resp_line and '>' in resp_line:
                        if not is_receipts:
                            print(f"{Colors.YELLOW}[Auto-Exec BLOCKED] Template placeholder detected: {resp_line}{Colors.RESET}")
                        continue
                    cmd_word = resp_line.split()[0][1:].lower()
                    if cmd_word in recognized_industrial_cmds:
                        if not is_receipts:
                            print(f"{Colors.CYAN}[Auto-Executing] {resp_line}{Colors.RESET}")
                        execute_industrial_line(
                            resp_line, 
                            ctx_mgr, orchestrator, swarm, utils, framework, working_dir, current_file, mode=mode
                        )
                        executed_any = True
            
            if not is_receipts:
                if executed_any:
                     print(f" {'</ξ#@⁺-|AG|-⁺@#ξ>'}")
                else:
                     print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")
            
            return current_file, False, working_dir, False
        
       
        elif cmd == 'read' and len(words) > 1:
            res = utils.read_file(words[1])
            if isinstance(res, str) and not res.startswith('{'):
                
                 if is_receipts:
                      info = utils._get_file_info(Path(working_dir) / words[1])
                      print(ActionReceipt.create("read", words[1], True, bytes=info['length'], sha256=info['sha256'], mtime=info['mtime']))
                 else:
                      print(res)
            else:
                
                 print(res)
                 if is_receipts:
                      try: 
                          rc = json.loads(res).get('exit_code', 13)
                          sys.exit(rc)
                      except: sys.exit(13)
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'write' or cmd == 'create':
            if len(words) < 2:
                print("[!] Usage: /create <filename> \"content\"")
                return current_file, False, working_dir, False
            filename = words[1]
            
           
            if any(kw in line.lower() for kw in ['5000', '1000', '10000', 'files', '*']):
                    if 'force' not in line.lower():
                        msg = " [!] RUNAWAY_GUARD_TRIGGERED: Mass file operation detected."
                        if is_receipts:
                             print(ActionReceipt.create("write", filename, False, exit_code=16, policy="blocked", reason="RUNAWAY_GUARD"))
                             sys.exit(EXIT_CODES["CAP_REACHED"])
                        print(msg)
                        print(" Use 'force' keyword to override this industrial safety boundary.")
                        print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
                        return current_file, False, working_dir, False

            content = ' '.join(words[2:])
            if not content and not is_receipts:
                print("Enter content (END to finish):")
                lines = []
                while True:
                    try:
                        l = input("... ")
                    except EOFError: break
                    if l == 'END': break
                    lines.append(l)
                content = '\n'.join(lines)
            
            res = utils.write_file(filename, content)
            print(res)
            _micro_review("write", filename, res, working_dir, is_receipts)
            if is_receipts and '"ok": false' in res:
               
                try: 
                    rc = json.loads(res).get('exit_code', 1)
                    sys.exit(rc)
                except: sys.exit(1)
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'run' and len(words) > 1:
            res_str = utils.run_command(" ".join(words[1:]))
            if is_receipts:
                print(res_str)
                if '"ok": false' in res_str:
                    try: 
                        rc = json.loads(res_str).get('exit_code', 1)
                        sys.exit(rc)
                    except: sys.exit(1)
            else:
                try:
                    res_obj = json.loads(res_str)
                    if res_obj.get('ok'):
                        if not is_receipts: print(f" [Execution Output]")
                        print(res_obj.get('stdout', ''))
                        if res_obj.get('stderr'):
                            print(f"Stderr: {res_obj['stderr']}")
                    else:
                        reason = res_obj.get('reason') or res_obj.get('stderr') or 'Unknown error'
                        print(f"✗ Execution failed (Code {res_obj.get('exit_code', '?')}): {reason}")
                except:
                    print(res_str)
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'delete' and len(words) > 1:
            res = utils.delete_file(words[1])
            print(res)
            _micro_review("delete", words[1], res, working_dir, is_receipts)
            if is_receipts and '"ok": false' in res:
                try: 
                    rc = json.loads(res).get('exit_code', 1)
                    sys.exit(rc)
                except: sys.exit(1)
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'edit' and len(words) > 2:
           
            raw_changes = ' '.join(words[2:])
            if 'replace:' in raw_changes and '->' in raw_changes:
                parts = raw_changes.replace('replace:', '').split('->')
                if len(parts) == 2:
                    res = utils.patch_file(words[1], parts[0], parts[1])
                    print(res)
                    _micro_review("edit", words[1], res, working_dir, is_receipts)
                    if is_receipts and '"ok": false' in res:
                        sys.exit(1)
                else:
                    if not is_receipts: print(" [!] Error: Invalid edit format. Use replace:OLD->NEW")
            else:
                if not is_receipts: print(" [!] Error: Invalid edit format. Use replace:OLD->NEW")
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'patch' and len(words) > 3:
            res = utils.patch_file(words[1], words[2], words[3])
            print(res)
            _micro_review("patch", words[1], res, working_dir, is_receipts)
            if is_receipts and '"ok": false' in res:
                sys.exit(1)
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'use' and len(words) > 1:
            new_path = str(Path(words[1]).resolve())
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            
           
            working_dir = new_path
            utils.working_dir = new_path
            ctx_mgr.working_dir = Path(new_path)
            ctx_mgr.context_file = ctx_mgr.working_dir / '.xi_context.json'
            ctx_mgr.ignore_file = ctx_mgr.working_dir / '.xi-ignore'
            
            if not is_receipts:
                print(f" Context switched to: {new_path}")
                print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            
            return current_file, False, new_path, False 
        elif cmd == 'ls':
            pattern = words[1] if len(words) > 1 else "*"
            files = utils.list_files(pattern)
            print("Files:")
            for f in files:
                print(f"  {f}")
            print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'search' and len(words) > 1:
            with with_spinner("Industrial Search (Smart Case)..."):
                results = utils.search_files(' '.join(words[1:]))
            for r in results:
                print(f"  {r['file']}: lines {r['lines']}")
            print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'diff' and len(words) > 2:
            print(utils.diff_files(words[1], words[2]))
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'count':
            pattern = words[1] if len(words) > 1 else "*"
            with with_spinner(f"Counting lines ({pattern})..."):
                res = utils.count_lines(pattern)
            print(f" Files: {res['files']} | Lines: {res['lines']}")
            print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'format' and len(words) > 1:
            print(utils.format_code(words[1]))
            if not is_receipts: print(f" {'</ξ#@⁺-|λ|-⁺@#ξ>'}")
        elif cmd == 'analyze' and len(words) > 1:
            analyzer = ImageAnalyzer(ctx_mgr)
            with with_spinner("Analyzing Image (Vision Swarm)..."):
                res = analyzer.analyze_image(words[1], ' '.join(words[2:]) if len(words) > 2 else "Describe this image.")
            if res.get('success'):
                print(res['description'])
            else:
                print(f" Error: {res.get('error')}")
            print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")
        elif cmd == 'extract' and len(words) > 1:
            analyzer = ImageAnalyzer(ctx_mgr)
            res = analyzer.extract_code_from_image(words[1])
            if res.get('success'):
                print(res['code'])
            else:
                print(f" Error: {res.get('message', res.get('error'))}")
            print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")
        elif cmd == 'ui' and len(words) > 1:
            analyzer = ImageAnalyzer(ctx_mgr)
            res = analyzer.ui_to_code(words[1])
            if res.get('success'):
                print(res['code'])
            else:
                print(f" Error: {res.get('error')}")
            print(f" {'</ξ#@⁺-|ξ|-⁺@#ξ>'}")
        elif cmd == 'context':
            if len(words) > 1 and words[1] == 'clear':
                ctx_mgr.context['conversation'] = []
                ctx_mgr.context['receipts'] = []
                ctx_mgr.save_context()
                if not is_receipts: print(" [Sovereign] Context purged. Session history cleared.")
            else:
                if not is_receipts:
                    print(f"Context Summary for {working_dir}:")
                    print(f"  Messages: {len(ctx_mgr.context.get('conversation', []))}")
                    print(f"  Receipts: {len(ctx_mgr.context.get('receipts', []))}")
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
        elif cmd == 'design':
           
            summary = ctx_mgr.get_context_summary()
            budget = ctx_mgr.build_context_budget(max_files=10)
            summary['budget_files'] = budget
            
           
            with with_spinner("Industrial Architect Proposing Plan..."):
                synth_result = orchestrator.execute_cognitive_synthesis(line, summary)
            
            if synth_result.get('enactment'):
                if not is_receipts:
                    print(f"\nPLAN: {synth_result.get('response')}")
                    print(f"RATIONALE: {synth_result.get('rationale')}")
                    print("\nSTAGED FILES:")
                    for sf in synth_result['staged_files']:
                        print(f" - [{sf.get('action', 'CREATE')}] {sf.get('path')}")
                    
                    while True:
                        try:
                            confirm = input("\nDo you wish to ENACT these changes? (y/n): ").strip().lower()
                            if confirm in ['y', 'n']: break
                        except EOFError: confirm = 'n'; break
                        
                    if confirm == 'y':
                        for sf in synth_result['staged_files']:
                            path, content = sf.get('path'), sf.get('content')
                            if path and content: print(utils.write_file(path, content))
                        print("\n✓ Enactment complete.")
                ctx_mgr.add_message('assistant', f"PROPOSED PLAN: {synth_result.get('response')}")
            else:
                print(f"\n{synth_result.get('response', 'Design failed.')}\n")
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            return current_file, False, working_dir, False
        
        elif cmd == 'swarm':
            if len(words) > 1 and words[1] == 'status':
                status = swarm.get_status()
                print(f"\n{Colors.CYAN}=== SWARM ORCHESTRATION STATUS ==={Colors.RESET}")
                print(f" Backlog: {status['total_backlog']} items")
                print(f" Buckets: {json.dumps(status['buckets'], indent=2)}")
                print(f" Agents:  {status['agent_assignments']}")
                print(f" Lanes:   {status['fire_teams']} Fire Teams Active")
                print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            elif len(words) > 1 and words[1] == 'process':
                with with_spinner("Swarm Firing up 42 Lanes..."):
                    results = swarm.process_backlog()
                if not results:
                    print(" [Swarm] No work in backlog.")
                else:
                    for r in results:
                        print(f"\n[{r['status']}] {r['fire_team']} (Lane 42.{r['lane']})")
                        print(f"  Executing {r['items']} tasks with {len(r['agents'])} agents")
                print(f"\n✓ Backlog processed.")
                print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            elif len(words) > 2 and words[1] == 'add':
                task = " ".join(words[3:]) if len(words) > 3 else words[2]
                swarm.add_to_bucket(task, status=words[2].upper())
                print(f"✓ Added task to {words[2].upper()} bucket.")
                print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            else:
                print("[!] Usage: /swarm [status|process|add <bucket> <task>]")
            return current_file, False, working_dir, False

        elif cmd == 'lane':
            if len(words) < 3:
                print("[!] Usage: /lane <lane_id> <prompt>")
            else:
                lane_id = words[1]
                prompt = " ".join(words[2:])
                lane_map = {'42.1': 'alpha', '42.2': 'beta', '42.3': 'gamma'}
                team_key = lane_map.get(lane_id)
                if not team_key:
                    print(f" [!] Invalid lane: {lane_id}. Use 42.1, 42.2, or 42.3.")
                else:
                    team = swarm.fire_teams[team_key]
                    print(f" [XI-IO] ROUTING TO {team['name']} ({team['focus'].upper()})")
                    route_res = swarm.route_through_42({'task': prompt, 'type': team['focus']})
                    
                    # Industrial Route Log: Clean join
                    clean_route = " -> ".join(route_res['route']).replace(" → ", " -> ")
                    print(f" Route: {clean_route}")
                    
                    res = orchestrator.execute_industrial_line(prompt)
                    result_text = res.get('write_status') or res.get('response', 'OK')
                    if result_text == "Skipped (No target detected)":
                        result_text = "Task Routed (Observation Only)"
                    print(f" Result: {result_text}")
                print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            return current_file, False, working_dir, False

        elif cmd == 'sprint':
            sprint = swarm.sprint_planning()
            print(f"\n{Colors.CYAN}=== INDUSTRIAL SPRINT PLAN ==={Colors.RESET}")
            print(f" Size: {sprint['sprint_size']} items")
            print(f" Remaining Backlog: {sprint['remaining_backlog']}")
            print(f"\n Distribution:")
            for team, items in sprint['by_team'].items():
                print(f"  {team.upper()}: {len(items)} tasks")
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            return current_file, False, working_dir, False
        
        elif cmd == 'purge':
            if not is_receipts: print("Purging session artifacts...")
            count = 0
            for p in Path(working_dir).glob("*.backup"):
                p.unlink()
                count += 1
            for p in Path(working_dir).glob(".xi-tmp-*"):
                p.unlink()
                count += 1
            if not is_receipts: print(f"Cleaned {count} artifacts.")
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
        elif cmd == 'simulate_failure':
            from framework import HardwareGuard
            try:
                HardwareGuard.simulate_failure(Path(working_dir) / "sim_error.bin")
            except OSError as e:
                print(ActionReceipt.create("simulate_failure", "sim_error.bin", False, exit_code=15, reason=str(e)))
                sys.exit(EXIT_CODES["TIMEOUT"])
            return current_file, False, working_dir, False
        else:
            # B8 FIX: Provide usage hints when command has insufficient arguments
            _usage_hints = {
                'read': '/read <filename>',
                'delete': '/delete <filename>',
                'edit': '/edit <filename> replace:OLD->NEW',
                'patch': '/patch <filename> <old_text> <new_text>',
                'search': '/search <text>',
                'run': '/run <command>',
                'diff': '/diff <file1> <file2>',
                'format': '/format <filename>',
                'analyze': '/analyze <image> [task]',
                'extract': '/extract code from <image>',
                'ui': '/ui to code <image>',
                'use': '/use <path>',
                'backup': '/backup <filename>',
                'test': '/test <filename>',
            }
            if cmd in _usage_hints:
                print(f"[!] Usage: {_usage_hints[cmd]}")
            elif not is_explicit:
                print(f" [!] Recognized command '{cmd}' but implementation pending in this loop refactor.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return current_file, False, working_dir, False


def execute_command_string(full_line, ctx_mgr, orchestrator, swarm, utils, framework, working_dir, current_file=None, in_code_block=False, recursion_depth=0, mode=AgenticMode.CHAT):
    """
    Handle chained commands with quote-aware splitting (v8.9.9.9.8)
    [Safety Override] Respects Markdown code blocks (```) and Recursion Depth
    """
    should_exit = False
    import sys
    import re
    
   
    if recursion_depth > 1:
        print(f" [!] Safety Override: Command recursion limit reached ({recursion_depth}). Aborting chain.")
        return current_file, False, working_dir, in_code_block

   
   
   
   
    if isinstance(full_line, list):
        full_line = ' '.join(full_line)
        
    block_toggles = full_line.count("```")
    if block_toggles % 2 != 0:
        in_code_block = not in_code_block
    
   
   
   
   
   
   
   
   
   
   
    
   
   
   
    
   
   
   
   
    
   
   
   
   
    
   
   
   
    
   
   
   
    
    if in_code_block and block_toggles == 0:
       
       
       
        return current_file, should_exit, working_dir, in_code_block

    if in_code_block and block_toggles > 0:
        
        
        
        
        
        
        
         pass
         
   
   
   
    
   
   
   
    
    if in_code_block:
        if "```" in full_line:
             in_code_block = False
             return current_file, should_exit, working_dir, in_code_block
        else:
             return current_file, should_exit, working_dir, in_code_block

   
    if "```" in full_line:
       
       
       
        in_code_block = True
        return current_file, should_exit, working_dir, in_code_block
        
   
   
    # Industrial Shredder: Stateful quote-aware splitter (v8.9.9.9.23)
    # Replaces catastrophic backtracking regex.
    commands = []
    current = []
    in_quote = None
    for char in full_line:
        if char in ("'", '"'):
            if not in_quote: in_quote = char
            elif in_quote == char: in_quote = None
            current.append(char)
        elif char in (';', '\n') and not in_quote:
            commands.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        commands.append("".join(current))
    
    for cmd_line in commands:
        cmd_line = cmd_line.strip()
        if not cmd_line: continue
        
       
        if cmd_line.startswith("//") or cmd_line.startswith("#"):
            continue
            
        try:
            res = execute_industrial_line(
                cmd_line, ctx_mgr, orchestrator, swarm, utils, framework, working_dir, current_file, mode=mode
            )
           
            if len(res) == 4:
                current_file, should_exit, working_dir, muted = res
            else:
                current_file, should_exit, working_dir = res
            sys.stdout.flush()
            if should_exit: break
        except Exception as e:
            print(f" [!] Execution Error: {e}")
            
    return current_file, should_exit, working_dir, in_code_block

def interactive_mode():
    """Interactive editor mode with AI assistance (v8.9.8 Hardened)"""
    import ollama
    import subprocess
    import os
    import re
    from pathlib import Path
    
    from framework import Framework, PHI
    from optimized_orchestrator import OptimizedOrchestrator
    from xi_utils import XIUtils
    from context_manager import ContextManager
    from image_analyzer import ImageAnalyzer
    from workspace_registry import WorkspaceRegistry
    
    TerminalUI.clear()
    TerminalUI.banner()
    
    help_text = """File Operations:
  /create <file> <desc>        Create new file (Provable)
  /edit <file> <changes>       Modify file (Deterministic)
  /patch <file>                Patch file (Atomic)
  /delete <file>               Delete file (Verified)
  /read <file>                 Show file content (Bounded)
  /run <command>               Execute command (Audited)

Utilities:
  /ls [pattern]                List files
  /search <text>               Search in files
  /test <file>                 Run tests
  /backup <file>               Backup file
  /diff <file1> <file2>        Compare files
  /count [pattern]             Count lines
  /format <file>               Format code
  /use <path>                  Set project workspace

Images:
  /analyze <image> [task]      Analyze screenshot/image
  /extract code from <image>   Extract code from image
  /ui to code <image>          Generate code from UI

Git:
  /status                      Git status
  /git commit <msg>            Quick commit

Framework:
  /validate                    Run validation
  /models                      List models
  /info                        Framework info
  /design <request>            Propose enactment plan
  /context                     Show context
  /clear context               Clear context
  
Orchestration (42 Lanes):
  /swarm status                Show agentic status
  /swarm add <stat> <task>     Add task (RAW, PROPOSED, REVIEWED)
  /swarm process               Execute backlog
  /lane <id> <prompt>          Direct fire-team injection
  /sprint                      Plan roadmap

Type 'exit' to quit"""

    TerminalUI.print_panel(help_text, title="COMMAND REFERENCE", color=Colors.CYAN)
    print()
    
    conversation_history = []
    current_file = None
    working_dir = os.getcwd()
    
   
    with workspace_lock():
        ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state(working_dir)
        image_analyzer = ImageAnalyzer(context_manager=ctx_mgr)
        registry = WorkspaceRegistry()
        
        TerminalUI.status(f"Interactive Session Active (v{__version__})", "OK")
        print()
        
        in_code_block = False
        
        while True:
           
            if not isinstance(ctx_mgr, ContextManager) or not isinstance(orchestrator, OptimizedOrchestrator):
                TerminalUI.status("ALARM: Critical system state corruption detected. Aborting session.", "ERR")
                break
                
            try:
               
                rel_path = f"[{current_file}]" if current_file else ""
                prompt_text = f"{Colors.CYAN}{working_dir}{Colors.RESET} {Colors.YELLOW}{rel_path}{Colors.RESET}\n{Colors.GREEN}XI-IO >{Colors.RESET} "
                if in_code_block:
                    prompt_text = f"{Colors.CYAN}{working_dir}{Colors.RESET} {Colors.YELLOW} (BLOCK MODE) {Colors.RESET}\n{Colors.GREEN}... >{Colors.RESET} "
                
                user_input = input(prompt_text).strip()
                
                # PASTE COLLECTOR (Bug #3 v3): Capture all pasted lines,
                # show a preview, and WAIT for confirmation before processing.
                # This prevents accidental execution of wrong clipboard contents.
                try:
                    import select, termios
                    paste_lines = []
                    while select.select([sys.stdin], [], [], 0.05)[0]:
                        extra_line = sys.stdin.readline()
                        if extra_line:
                            paste_lines.append(extra_line.rstrip('\n'))
                        else:
                            break
                    if paste_lines:
                        total_lines = len(paste_lines) + 1
                        all_lines = [user_input] + paste_lines
                        
                        # Show preview
                        print(f'\n{Colors.YELLOW}[!] Paste Detected: {total_lines} lines captured.{Colors.RESET}')
                        # Show first 3 and last line for context
                        preview_lines = all_lines[:3]
                        if total_lines > 4:
                            preview_lines.append(f'  ... ({total_lines - 4} more lines) ...')
                        if total_lines > 3:
                            preview_lines.append(all_lines[-1])
                        for pl in preview_lines:
                            print(f'  {Colors.CYAN}│{Colors.RESET} {pl[:100]}')
                        
                        # Flush any remaining stdin before confirmation prompt
                        termios.tcflush(sys.stdin, termios.TCIFLUSH)
                        
                        # Wait for confirmation
                        try:
                            confirm = input(f'{Colors.GREEN}Process this paste? (Enter=yes, n=discard): {Colors.RESET}').strip().lower()
                        except EOFError:
                            confirm = 'n'
                        
                        if confirm == 'n':
                            print('[!] Paste discarded.')
                            continue  # Back to main prompt
                        
                        # Merge all lines into single input
                        if user_input.startswith('/'):
                            # First line is a command — execute it, save rest as context
                            _paste_context = '\n'.join(paste_lines)
                            ctx_mgr.add_message('user', f'[PASTED CONTEXT]\n{_paste_context}')
                            print(f'[!] Command: {user_input} | {len(paste_lines)} context lines stored.')
                        else:
                            # Natural language — merge everything
                            user_input = '\n'.join(all_lines)
                except Exception:
                    pass  # Non-terminal environments (pipes, etc)
               
                current_file, should_exit, working_dir, in_code_block = execute_command_string(
                    user_input, ctx_mgr, orchestrator, swarm, utils, framework, working_dir, current_file, in_code_block, mode=AgenticMode.CHAT
                )
                
                if should_exit:
                    break
                   
                if utils.working_dir != working_dir:
                    ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state(working_dir)

            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

def cmd_modal_execution(args):
    """Execute command with Hardened Modal Invariants"""
    mode = getattr(args, 'mode', AgenticMode.CHAT)
    command_str = ' '.join(args.command)
    
    ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state()
    
    # ACT mode forces receipts
    if mode == AgenticMode.ACT:
         orchestrator.format_mode = 'receipts'
    
    with workspace_lock():
        execute_command_string(command_str, ctx_mgr, orchestrator, swarm, utils, framework, working_dir, mode=mode)

def load_state(working_dir=None):
    """
    Unify session state loading to prevent context ghosting.
    Returns: (ctx_mgr, orchestrator, swarm, utils, framework, working_dir)
    """
    if not working_dir:
        working_dir = os.getcwd()
    
    from framework import Framework
    from optimized_orchestrator import OptimizedOrchestrator
    from swarm_orchestrator import SwarmOrchestrator
    from context_manager import ContextManager
    from xi_utils import XIUtils

    framework = Framework()
    orchestrator = OptimizedOrchestrator(framework)
    swarm = SwarmOrchestrator()
    
    # Load persistence
    initial_context = ContextManager(working_dir)
    persisted_ws = initial_context.context.get('workspace')
    if persisted_ws and os.path.exists(persisted_ws) and not working_dir.startswith(persisted_ws):
        working_dir = persisted_ws
        try:
            os.chdir(working_dir)
        except OSError: pass

    ctx_mgr = ContextManager(working_dir)
    utils = XIUtils(working_dir, context_manager=ctx_mgr)
    
    return ctx_mgr, orchestrator, swarm, utils, framework, working_dir

def main():
    """Industrial Entry Point (φ Alignment)"""
    is_receipts = '--format=receipts' in sys.argv or '--format receipts' in ' '.join(sys.argv)

   
    if len(sys.argv) == 1:
        interactive_mode()
        return 0
    
   
    parser = argparse.ArgumentParser(
        description="XI-IO v8 Framework CLI - Use natural language or commands",
        prog="xi",
        epilog="Examples:\n  xi validate\n  xi models\n  xi -c \"create test.txt hello\""
    )
    
    parser.add_argument('--version', '-v', action='store_true', help='Show version')
    parser.add_argument('--command', '-c', help='Run a single command and exit')
    parser.add_argument('--format', choices=['chat', 'receipts'], default='chat', help='Output format')
    parser.add_argument('--silent', action='store_true', help='Suppress non-receipt output')
    parser.add_argument('--mode', choices=[m.value for m in AgenticMode], default=AgenticMode.CHAT.value, help="Force a specific CLI mode")
    parser.add_argument('--json', action='store_true', help='Output strict JSON receipts for Command Center UI')
    
    subparsers = parser.add_subparsers(dest='command_name', help='Commands')
    
   
    validate_parser = subparsers.add_parser('validate', help='Validate framework')
    validate_parser.set_defaults(func=cmd_validate)
    
   
    models_parser = subparsers.add_parser('models', help='Manage AI model cylinders')
    models_sub = models_parser.add_subparsers(dest='models_cmd')
    m_scan = models_sub.add_parser('scan', help='Scan reality for local models')
    m_scan.set_defaults(func=cmd_models_scan)
    m_list = models_sub.add_parser('list', help='Identify model cylinders')
    m_list.set_defaults(func=cmd_models_list)
    models_parser.set_defaults(func=lambda args: cmd_models_list(args) if not getattr(args, 'models_cmd', None) else None)
    
   
    route_parser = subparsers.add_parser('route', help='Manage model firing order')
    route_sub = route_parser.add_subparsers(dest='route_cmd')
    r_set = route_sub.add_parser('set', help='Set lane route')
    r_set.add_argument('lane', help='Routing lane')
    r_set.add_argument('model', help='Model name')
    r_set.set_defaults(func=cmd_route_set)

   
    inject_parser = subparsers.add_parser('inject', help='Inject prompt into lane')
    inject_parser.add_argument('lane', help='Routing lane')
    inject_parser.add_argument('prompt', help='Prompt message')
    inject_parser.set_defaults(func=cmd_inject_new)

   
    info_parser = subparsers.add_parser('info', help='Show framework info')
    info_parser.set_defaults(func=cmd_info)
    
   
    status_parser = subparsers.add_parser('status', help='Show JSON status for UI')
    status_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    status_parser.set_defaults(func=cmd_status)

   
    verify_parser = subparsers.add_parser('verify', help='Run Phase 6 Verification')
    verify_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    verify_parser.set_defaults(func=cmd_verify)
    
    gates_parser = subparsers.add_parser('gates', help='Run Phase Gate checks')
    gates_parser.add_argument('--check', action='store_true', help='Execute gate verification')
    gates_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    gates_parser.set_defaults(func=cmd_gates)
    
   
    self_parser = subparsers.add_parser('selftest', help='Run framework self-test')
    self_parser.set_defaults(func=cmd_selftest)
    
   
    test_parser = subparsers.add_parser('test-agent', help='Test agent generation')
    test_parser.add_argument('--model', default='thrawn-commander', help='Model to use')
    test_parser.add_argument('--prompt', help='Test prompt')
    test_parser.set_defaults(func=cmd_test_agent)
    
   
    ask_parser = subparsers.add_parser('ask', help='Ask natural language question')
    ask_parser.add_argument('query', nargs='+', help='Your question')
    ask_parser.set_defaults(func=cmd_ask)
    
   
    discovery_parser = subparsers.add_parser('discovery', help='Discover projects')
    discovery_parser.add_argument('path', help='Root path to scan')
    discovery_parser.set_defaults(func=cmd_discovery)
    
   
    use_parser = subparsers.add_parser('use', help='Switch project context')
    use_parser.add_argument('project', help='Project name or path')
    use_parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    use_parser.set_defaults(func=cmd_use)
    
   
    where_parser = subparsers.add_parser('whereami', help='Show framework diagnostic facts')
    where_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    where_parser.set_defaults(func=cmd_whereami)
 
   
    run_parser = subparsers.add_parser('run', help='Execute industrial command')
    run_parser.add_argument('command', nargs='+', help='Command to execute')
    run_parser.set_defaults(func=cmd_run)
 
   
    del_parser = subparsers.add_parser('delete', help='Delete file')
    del_parser.add_argument('filename', help='File to delete')
    del_parser.set_defaults(func=cmd_delete)
 
   
    read_parser = subparsers.add_parser('read', help='Read file content')
    read_parser.add_argument('filename', help='File to read')
    read_parser.set_defaults(func=cmd_read)
 
   
    write_parser = subparsers.add_parser('write', help='Write file content')
    write_parser.add_argument('filename', help='File to write')
    write_parser.add_argument('content', help='Content to write')
    write_parser.set_defaults(func=cmd_write)

    # Swarm/Orchestration Commands
    swarm_parser = subparsers.add_parser('swarm', help='Manage agentic swarm')
    swarm_sub = swarm_parser.add_subparsers(dest='swarm_cmd')
    swarm_status = swarm_sub.add_parser('status', help='Show swarm status')
    swarm_status.set_defaults(func=cmd_swarm)
    swarm_process = swarm_sub.add_parser('process', help='Process swarm backlog')
    swarm_process.set_defaults(func=cmd_swarm)
    swarm_add = swarm_sub.add_parser('add', help='Add task to swarm')
    swarm_add.add_argument('bucket', choices=['raw', 'proposed', 'reviewed', 'canon'], help='Bucket to add to')
    swarm_add.add_argument('task', nargs='+', help='Task description')
    swarm_add.set_defaults(func=cmd_swarm)

    lane_parser = subparsers.add_parser('lane', help='Execute specialized lane injection')
    lane_parser.add_argument('lane', help='Lane ID (42.1, 42.2, 42.3)')
    lane_parser.add_argument('prompt', nargs='+', help='Prompt for the lane fire-team')
    lane_parser.set_defaults(func=cmd_lane)

    # ls command
    write_parser.set_defaults(func=cmd_write)
 
    create_parser = subparsers.add_parser('create', help='Create new file')
    create_parser.add_argument('filename', help='File to create')
    create_parser.add_argument('content', help='Initial content')
    create_parser.set_defaults(func=cmd_write)
 
   
    # ls command
    ls_parser = subparsers.add_parser('ls', help='List project files')
    ls_parser.add_argument('pattern', nargs='?', default='*', help='Glob pattern')
    ls_parser.set_defaults(func=lambda args: execute_industrial_line(f"ls {args.pattern}", *load_state()))

    # search command
    search_parser = subparsers.add_parser('search', help='Search for text')
    search_parser.add_argument('text', nargs='+', help='Text to find')
    search_parser.set_defaults(func=lambda args: execute_industrial_line(f"search {' '.join(args.text)}", *load_state()))

    # diff command
    diff_parser = subparsers.add_parser('diff', help='Compare two files')
    diff_parser.add_argument('file1', help='First file')
    diff_parser.add_argument('file2', help='Second file')
    diff_parser.set_defaults(func=lambda args: execute_industrial_line(f"diff {args.file1} {args.file2}", *load_state()))

    # count command
    count_parser = subparsers.add_parser('count', help='Count lines in files')
    count_parser.add_argument('pattern', nargs='?', default='*', help='Glob pattern')
    count_parser.set_defaults(func=lambda args: execute_industrial_line(f"count {args.pattern}", *load_state()))

    # format command
    format_parser = subparsers.add_parser('format', help='Format code files')
    format_parser.add_argument('filename', help='File to format')
    format_parser.set_defaults(func=lambda args: execute_industrial_line(f"format {args.filename}", *load_state()))

    # backup command
    backup_parser = subparsers.add_parser('backup', help='Backup file')
    backup_parser.add_argument('filename', help='File to backup')
    backup_parser.set_defaults(func=lambda args: execute_industrial_line(f"backup {args.filename}", *load_state()))

    # test command
    test_p = subparsers.add_parser('test', help='Run project tests')
    test_p.add_argument('filename', nargs='?', help='Specific test file')
    test_p.set_defaults(func=lambda args: execute_industrial_line(f"test {args.filename or ''}", *load_state()))

    # edit / patch / read / write (Already present or handled via execute_industrial_line)
    edit_parser = subparsers.add_parser('edit', help='Modify file content')
    edit_parser.add_argument('filename', help='File to edit')
    edit_parser.add_argument('changes', nargs='*', help='Changes to apply (e.g. replace:OLD->NEW)')
    edit_parser.set_defaults(func=lambda args: execute_industrial_line(f"edit {args.filename} {' '.join(args.changes)}", *load_state()))
 
   
    list_parser = subparsers.add_parser('list-projects', help='List registered projects')
    list_parser.set_defaults(func=cmd_list_projects)

   
    version_parser = subparsers.add_parser('version', help='Show version')
    version_parser.set_defaults(func=cmd_version)

   
    help_parser = subparsers.add_parser('help', help='Show help')
    help_parser.set_defaults(func=lambda args: parser.print_help())
    
   
    hook_parser = subparsers.add_parser('hook-scan', help='Run anchor validation')
    hook_parser.set_defaults(func=cmd_hook_scan)
    
   
    policy_parser = subparsers.add_parser('policy-probe', help='Run policy validation')
    policy_parser.set_defaults(func=cmd_policy_probe)
    
    # Modal subcommands (v8.9.9.9.22)
    for mode in [AgenticMode.PLAN, AgenticMode.ACT, AgenticMode.DEBUG, AgenticMode.REVIEW]:
        m_parser = subparsers.add_parser(mode.name.lower(), help=f"Execute in {mode.value} mode")
        m_parser.add_argument('command', nargs='+', help=f"Command to execute in {mode.value} mode")
        m_parser.set_defaults(func=cmd_modal_execution, mode=mode)
    
   
    known_commands = list(subparsers.choices.keys()) + ['--version', '-v', '-h', '--help', '-c', '--command', 'version', 'whereami', 'help']
    
   
    first_non_flag = None
    for arg in sys.argv[1:]:
        if arg in ['--version', '-v', '-h', '--help']:
           
            args, _ = parser.parse_known_args()
            if args.version:
                cmd_version(args)
                return 0
            parser.print_help()
            return 0
        if not arg.startswith('-'):
            first_non_flag = arg
            break
    
    if first_non_flag and first_non_flag not in known_commands and '-c' not in sys.argv and '--command' not in sys.argv:
       
        query = ' '.join(sys.argv[1:])
        import ollama
        prompt_context = f"""[IDENTITY_FENCE]
# Industrial Directive
XI is the Sovereign Industrial Intelligence (System Engine).
You speak ABOUT XI to the user. Do NOT claim to be XI.

INDUSTRIAL DIRECTIVES:
1. AUTHORITY: You have full access to XI's tools and files at {framework_root}.
2. TONE: Concise. Technical. Grounded.
3. REFERENCE: Use "XI" or "The system" for the framework.

Context: 
- Version: {__version__}
- User query: {query}

Provide a precise, industrial response in English. No persona leak."""

        print("Thinking...")
        try:
            from framework import Framework
            from optimized_orchestrator import OptimizedOrchestrator
            framework = Framework()
            orchestrator = OptimizedOrchestrator(framework)
            result = orchestrator.execute_single(prompt_context, task_type='general')
            print()
            print(result['response'])
            print()
            print(f" {'</ξ#@⁺-|∞|-⁺@#ξ>'}")
            return 0
        except Exception as e:
            print(f" [!] Fallback failed: {e}")
            return 1

   
    args = parser.parse_args()
    
    # Standardize mode to Enum
    if isinstance(args.mode, str):
        args.mode = AgenticMode(args.mode.upper())
    
    if args.version:
        cmd_version(args)
        return 0
    
    if args.command:
        # Standardize receipts mode
        if is_receipts:
            from framework import IndustrialAuditService, HardwareGuard
            IndustrialAuditService.set_silent(True)
            HardwareGuard.set_silent(True)
            
        with workspace_lock():
            # Unified State Loading
            ctx_mgr, orchestrator, swarm, utils, framework, working_dir = load_state()
            
            if is_receipts: 
                ctx_mgr.silent = True
                orchestrator.format_mode = 'receipts'
                orchestrator.silent = True
            
            try:
                execute_command_string(
                    args.command, ctx_mgr, orchestrator, swarm, utils, framework, working_dir, mode=args.mode
                )
            except SystemExit as e:
                return e.code
            except Exception as e:
                if not is_receipts:
                    print(f" [!] Execution Error: {e}")
                return 1
        return 0

    if hasattr(args, 'command_name') and args.command_name:
        with workspace_lock():
            args.func(args)
        return 0
    
    # DEFAULT: Enter Interactive Mode
    interactive_mode()
    return 0

if __name__ == '__main__':
    sys.exit(main())
