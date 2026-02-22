
import sys
import os
import json
from unittest.mock import MagicMock

# Add current dir to path to import local modules
sys.path.append(os.getcwd())

from optimized_orchestrator import OptimizedOrchestrator

def run_wargame():
    orch = OptimizedOrchestrator()
    print("--- ADJUDICATOR WARGAME START ---")

    # CASE 1: NO INTERSECTION (FRACTURED SWARM)
    print("\n[CASE 1] No Intersection (2 Agents, differing facts)")
    claims_1 = [
        {"claim": "Target file is xi_cli.py", "confidence": 0.99, "type":"fact", "agent": "Agent_A"},
        {"claim": "Target file is framework.py", "confidence": 0.99, "type":"fact", "agent": "Agent_B"}
    ]
    res1 = orch._adjudicate_claims(claims_1, total_agents=2)
    print(f"Status: {res1['status']}")
    print(f"Reason: {res1.get('reason', 'N/A')}")
    print(f"Intersection Count: {len(res1.get('intersection_truth', []))}")

    # CASE 2: MAJORITY WRONG + MINORITY OBJECTION
    print("\n[CASE 2] Majority Wrong + Minority Objection (2 vs 1)")
    claims_2 = [
        {"claim": "Delete file config.yaml", "confidence": 0.95, "type":"action", "agent": "Agent_A"},
        {"claim": "Delete file config.yaml", "confidence": 0.95, "type":"action", "agent": "Agent_B"},
        {"claim": "not Delete file config.yaml", "confidence": 0.95, "type":"risk", "agent": "Agent_C"}
    ]
    res2 = orch._adjudicate_claims(claims_2, total_agents=3)
    print(f"Status: {res2['status']}")
    print(f"Intersection: {[c['claim'] for c in res2.get('intersection_truth', [])]}")
    print(f"Minority: {[c['claim'] for c in res2.get('minority_positions', [])]}")

    # CASE 3: MALFORMED JSON (EXTRACTOR HARDENING)
    print("\n[CASE 3] Malformed JSON (No mercy parsing)")
    # Mocking ollama.generate back in extraction
    import ollama
    original_gen = ollama.generate
    
    # Simulate a response that contains JSON but wrapped in prose without clean fences or just garbage
    bad_responses = [
        "Here is the claims: [{\"claim\": \"X\", \"type\": \"fact\", \"confidence\": 0.9}]", # JSON in prose (used to be allowed)
        "```json\n[{\"claim\": \"Y\"}]", # Unclosed fence (soft failure)
        "NOT JSON AT ALL"
    ]
    
    for i, bad_raw in enumerate(bad_responses):
        ollama.generate = MagicMock(return_value={'response': bad_raw})
        claims = orch._extract_claims("dummy input", f"Agent_{i}")
        print(f"Extraction {i+1} resulting claims: {claims}")

    ollama.generate = original_gen
    print("\n--- WARGAME COMPLETE ---")

if __name__ == "__main__":
    run_wargame()
