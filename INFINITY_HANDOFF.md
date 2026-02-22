# ∞ XI-IO INFINITY: REORIENTATION & HANDOFF GUIDE (v28.3)

This document is the "Neural Bridge" for any agent or developer picking up the XI-IO v8 Framework from this point forward. It defines the state of the "Steel," the "Soul," and the "Circuitry."

---

## 🏛️ 1. SYSTEM HIERARCHY & COMPONENT STATUS

### **A. THE STEEL (Functional Logic Layer)**

| Component | Status | Role | UI? |
| :--- | :--- | :--- | :--- |
| `xi_cli.py` | **STABLE** | **The Sentinel.** Hierarchical query interceptor. Hardware-first. | CLI |
| `optimized_orchestrator.py` | **STABLE** | **The Adjudicator.** Swarm consensus & OP-11 Halt engine. | CLI |
| `framework.py` | **STABLE** | Core BHVT logic & Category 42 definitions. | Core |
| `ledger_guard.py` | **STABLE** | Action recording & UUID tagging. | CLI |
| `rosetta_stone.py` | **STABLE** | Pivot-based schema translation. | Core |
| `xi_utils.py` | **STABLE** | Hardened filesystem operations. | Core |

### **B. THE FORGE (Interface Layer - IN PROGRESS)**

- **Terminal UI:** Fully integrated into `xi_cli.py` via `terminal_ui.py`.
- **Management Plane:** Located in `_forge/xi-io-management-plane/`. This is a React/TypeScript interface.
- **Visuals:** Currently handles stream events and metrics, but **needs update** to display the v28 Adjudication Logs (the "how agents argued" view).

---

## 🧠 2. THE SWARM: MODELS & HYDRATION

### **Swarm Configuration**

- **Default Sentinel (The Interceptor):** Local Python (No LLM for facts).
- **The Core Soul:** `xibalba:latest` (Customized Llama-3 based with Industrial Fences).
- **Consensus Agents:** `llama3.1:8b`, `phi3.5:latest`.
- **Adjudicator Threshold:** `floor(n/2) + 1`.

### **Hydration & Training Strategy**

1. **Hydration:** Controlled via `rehydrate.sh`. It pulls specific GGUF/Ollama tags to ensure every node in the swarm is using the "Certified" weight.
2. **Identity Fencing:** We do not rely on traditional fine-tuning for v8. We use **Identity Fences** (in `xi_cli.py`) that strictly define the agent's relationship to the hardware.
3. **Grounding:** The `STATE_BLOB` (in `xi_cli.py`) provides the "Ocular Truth" of the disk to the models, preventing hallucinations.

---

## 🔗 3. THE LINKS (The Circuitry)

1. **Query -> Sentinel:** Every line typed into the CLI goes to `classify_query()`.
2. **Sentinel -> Truth:** If it's a fact (CWD, version) or computation (file count), Python returns the answer immediately. **LLM never sees it.**
3. **Sentinel -> Adjudicator:** If it requires "Reasoning," it spawns a swarm in `OptimizedOrchestrator`.
4. **Adjudicator -> Ledger:** Every agreed-upon action is written to the Ledger by `ledger_guard`.
5. **Ledger -> UI:** The UI reads the Ledger to show the "Chain of Truth."

---

## 🛠️ 4. THE REMAINING DOCKET (What to build next)

1. **UI Parity:** Update the Management Plane to show the `disagreements` field from a HALT (OP-11). The UI should glow RED when the swarm fractures.
2. **Mathematical Convergence:** More work is needed in `tests/benchmark_swarm.py` to handle "Shared Hallucinations" (where agents agree on a wrong number).
3. **Search Optimization:** The `search` command still uses raw `grep`. It should be upgraded to use the **Governed Recursive Iterator** (CS004) to avoid hangs.

---

## 📡 5. REORIENTATION FOR AI/DEVELOPERS

**If you are picking this up, start here:**

1. **Check the Sentinel:** Run `python3 xi_cli.py asking where am i`. If it doesn't show your real path, the Interceptor is broken.
2. **Run a Wargame:** `python3 50_testing/wargame_adjudicator.py`. Verify that the system HALTS when agents disagree.
3. **The Code is Truth:** Trust the filesystem utility `xi_utils.py` over your own assumptions. Always use the `STATE_BLOB`.

---
**8 for Infinity (∞)** - The framework is now clean. The cords are cut.
**[LINK TO REPO](https://github.com/Vado42-chris/feb_22_2026_xi-io_framework.git)**
