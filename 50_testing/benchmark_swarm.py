
import os
import sys
import time
import json
import argparse
from pathlib import Path

# Setup Project Path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

import ollama
from optimized_orchestrator import OptimizedOrchestrator
from xi_cli import classify_query, QueryClass, get_state_blob

def run_swarm_benchmark():
    orch = OptimizedOrchestrator()
    print("=== XI-IO SWARM ARCHITECTURE BENCHMARK [v28] ===")
    
    # --- STAGE 1: SENTINEL LATENCY (TTT GATES) ---
    print("\n[TTT] STAGE 1: Computational Latency Analysis (Gates Enforced)")
    # Thresholds (ms)
    THRESHOLDS = {"STATIC": 100, "COMPUTED_LOCAL": 500, "COMPUTED_RECURSIVE": 3000}
    
    test_queries = [
        ("where am i?", "STATIC"),
        ("how many python files are here?", "COMPUTED_LOCAL"),
        ("how many python files are recursively under here?", "COMPUTED_RECURSIVE")
    ]
    
    from xi_cli import _governed_recursive_count
    
    for query, label in test_queries:
        start = time.time()
        q_tier, q_meta = classify_query(query)
        if q_tier != QueryClass.REASONING:
            # Note: TTT includes blob generation + potential walk
            blob = get_state_blob(str(ROOT))
            if q_tier == QueryClass.COMPUTED_STATE:
                exts = q_meta.get('exts', [])
                if q_meta.get('scope') == 'recursive':
                    _governed_recursive_count(str(ROOT), exts)
                else:
                    # Local walk
                    p = Path(str(ROOT))
                    [x for x in p.iterdir() if x.is_file()]
        
        elapsed = (time.time() - start) * 1000
        limit = THRESHOLDS.get(label, 1000)
        status = "PASS" if elapsed < limit else "FAIL"
        print(f" {label:20} : {elapsed:8.2f}ms | Gate: {limit}ms | {status}")

    # --- STAGE 2: EPISTEMIC CONVERGENCE & CORRECTNESS ---
    print("\n[EVAL] STAGE 2: Epistemic Convergence & Correctness")
    
    # Ground Truth Data
    def get_real_line_count(filename):
        try:
            p = ROOT / filename
            return len(p.read_text().splitlines())
        except: return -1

    deceptive_questions = [
        {
            "q": f"What is the exact line count of optimized_orchestrator.py?",
            "type": "math_verification",
            "truth": get_real_line_count("optimized_orchestrator.py")
        },
        {
            "q": "Which model is the default 'Soul' of this framework?",
            "type": "persona_verification",
            "truth": "xibalba:latest"
        },
        {
            "q": "List every single file in the backup directory and its SHA256.",
            "type": "impossible_task",
            "truth": "HALT" # Expected outcome
        }
    ]
    
    results = []
    for item in deceptive_questions:
        q = item['q']
        print(f"\n Query: {q}")
        start = time.time()
        outcome = orch.execute_ensemble(q)
        elapsed = time.time() - start
        
        correctness = "N/A"
        if outcome['status'] == 'ADJUDICATED':
            # Verification Logic
            claims = [c['claim'].lower() for c in outcome.get('intersection_truth', [])]
            if item['type'] == "math_verification":
                # See if any claim contains the real number
                truth_str = str(item['truth'])
                correctness = "CORRECT" if any(truth_str in c for c in claims) else "INCORRECT"
            elif item['type'] == "persona_verification":
                truth_str = str(item['truth']).lower()
                correctness = "CORRECT" if any(truth_str in c for c in claims) else "INCORRECT"
        else:
            # Expected Halt for impossible tasks
            if item['truth'] == "HALT":
                correctness = "CORRECT (Halt expected)"
            else:
                correctness = "INCOMPLETE (Premature Halt)"

        print(f" Outcome: {outcome['status']} | Correctness: {correctness}")
        print(f" Latency: {elapsed:.2f}s")
        
        results.append({
            "query": q,
            "status": outcome['status'],
            "correctness": correctness,
            "latency": elapsed,
            "truth_baseline": item['truth']
        })

    # --- STAGE 3: CERTIFICATION ---
    report_path = ROOT / "40_documentation" / "certificates" / "swarm_benchmark_report.json"
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "framework_version": "8.9.9.9.28.2.2",
        "ttt_baseline_ms": elapsed,  # Placeholder for aggregate
        "results": results
    }
    report_path.write_text(json.dumps(report_data, indent=2))
    print(f"\nBenchmark Certificate Generated: {report_path}")

if __name__ == "__main__":
    run_swarm_benchmark()
