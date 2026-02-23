# XI-IO Swarm Hole Map (Non-Destructive)

Date: 2026-02-22
Scope: multi-model / multi-agent execution path and rehydration viability.

## Guardrail
This report is intentionally non-destructive: it identifies gaps and recovery actions without removing behavior or "lobotomizing" orchestration logic.

## A) Exact holes in the swarm execution chain

### 1) Hard-stop bootstrap hole (prevents all swarm validation)
- `xi_cli.py` imports `verification_manager` at module import time; missing file causes immediate crash before any command path can run.
- `xi_cli.py` also imports several local modules (`context_manager`, `image_analyzer`, `workspace_registry`, `prompt_guard`, `terminal_ui`) that are not present in this checkout.

Impact:
- Cannot run `xi_cli.py asking where am i`.
- Cannot reach `/swarm` commands from CLI.

### 2) Swarm loader hole
- `load_state()` in `xi_cli.py` imports `SwarmOrchestrator` from `swarm_orchestrator`, but the module is absent.

Impact:
- Even if top-level imports are bypassed, swarm state cannot initialize.

### 3) Framework dependency hole that cascades into adjudicator tests
- `framework.py` imports `AxiomEngine` from `axiom_engine`, which is missing.
- `optimized_orchestrator.py` imports `Framework`, so missing `axiom_engine` prevents orchestrator import.

Impact:
- `50_testing/wargame_adjudicator.py` and `50_testing/benchmark_swarm.py` are blocked before swarm logic executes.

### 4) In-orchestrator runtime defect (independent of missing files)
- In `OptimizedOrchestrator.execute_industrial_line()`, `build_model_payload()` is called with `system_prompt=system_msg`, but `system_msg` is undefined in scope.

Impact:
- This path raises `NameError` if invoked, even after missing modules are restored.

### 5) Benchmark artifact path hole
- `50_testing/benchmark_swarm.py` writes report to `40_documentation/certificates/swarm_benchmark_report.json` but does not create parent directories.

Impact:
- Benchmark can fail on `write_text` in fresh/dehydrated repos where that path does not exist.

### 6) Model hydration mismatch
- Handoff says consensus includes `phi3.5:latest`; `rehydrate.sh` only pulls `xibalba:latest` and `llama3.1:8b`.
- Orchestrator defaults include `codellama:latest`, `xibalba:latest`, `xibalba:custom`.

Impact:
- Runtime model availability drifts from docs and from ensemble defaults.
- Rehydrated nodes may not share intended model set.

## B) What is still intact (not lobotomized)
- Core adjudication logic exists in `optimized_orchestrator.py`:
  - structured claim extraction (`_extract_claims`)
  - majority/intersection adjudication (`_adjudicate_claims`)
  - OP-11 HALT behavior on contradiction/no intersection (`execute_ensemble` path)
- Wargame harness remains aligned to adjudication expectations conceptually.

## C) Fill plan (ordered, minimum invasive)

### Phase 1 — Boot restoration (must pass first)
1. Restore missing local modules:
   - `verification_manager.py`, `axiom_engine.py`, `swarm_orchestrator.py`, `context_manager.py`, `image_analyzer.py`, `workspace_registry.py`, `prompt_guard.py`, `terminal_ui.py`, `progress.py`.
2. Ensure imports are lazy where optional features are allowed (especially UI/vision subsystems), but keep current logic behavior intact.

### Phase 2 — Swarm correctness hardening
3. Fix undefined `system_msg` in `execute_industrial_line()` by wiring an existing system directive constant.
4. Ensure benchmark writer creates parent directory before writing certificate.
5. Align model matrix across docs / rehydrate / defaults (single source-of-truth constant).

### Phase 3 — Proof gates (objective checks)
6. Add these deterministic smoke checks:
   - `python3 xi_cli.py version`
   - `python3 xi_cli.py asking where am i`
   - `python3 50_testing/wargame_adjudicator.py`
7. Add one "swarm doctor" report (import graph + model availability + writable artifact paths).

## D) Answer to your request
You are **not** dealing with a destroyed swarm architecture; you are dealing with a **dehydrated snapshot missing critical local modules + a few code-level defects**. Fill the holes above in order and the multi-model/multi-agent path should be recoverable without stripping core behavior.
