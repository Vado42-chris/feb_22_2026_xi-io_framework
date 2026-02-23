# XI-IO Dehydration/Rehydration Audit (First-Pass Validation)

Date: 2026-02-22
Repo: `feb_22_2026_xi-io_framework`

## Goal of this audit
Validate how well dehydration/rehydration preserved the intended backend-first architecture and the reusable/reskinnable UI-component concept.

## What worked in rehydration
1. `rehydrate.sh` completed successfully:
   - Created virtualenv
   - Installed `requirements.txt`
   - Initialized `~/.xi-io/production_ledger.json`
   - Emitted warning (not fatal) when `ollama` binary was missing
2. The script correctly writes `.env` with `XI_FRAMEWORK_ROOT` and `XI_MODE`.

## What did **not** rehydrate successfully
Even after successful script execution, the verification command in `rehydrate.sh` fails:
- `python3 xi_cli.py asking where am i` fails at import time because `verification_manager` is missing.

Additional critical runtime gap:
- `framework.py` imports `axiom_engine`, which is missing in this repo snapshot.

Conclusion: hydration of Python package dependencies works, but hydration of **internal framework modules** is incomplete in this checkout.

## UI concept check against your intended model
Your concept: build backend-first, then reusable UI components that are reskinnable/themable via variables.

### Evidence this concept is partially present
- `00_core/ui/tokens.ts` already defines CSS-variable-based design tokens (`var(--ui-...)`).
- `00_core/ui/ai-components/WHITE_LABEL_GUIDE.md` explicitly describes white-labeling strategy and notes the need to replace hardcoded colors with CSS vars.

### Evidence it is not finished yet
- Current React components still contain many hardcoded Tailwind color classes (e.g., `bg-zinc-*`, `text-orange-*`), so theming is not fully abstracted yet.
- `Omnibot.tsx` includes temporary grafted typing (`any`) and severed stream-event dependency markers, indicating partial/in-progress integration.

## Direct answer to your core question
> If missing/incomplete files were restored, would the reusable multi-product UI concept "in essence" be there?

**Yes, mostly in essence — but not automatically complete.**

Restoring missing backend modules would likely restore CLI/orchestration runtime and enable end-to-end flows. However, to fully realize your "rotate the room" productization concept, you still need a focused theming/refactor pass on UI components to eliminate hardcoded styling and push mode/endpoint/branding through props/context/tokens.

## Rehydration quality score (practical)
- **Environment bootstrap:** Good
- **Dependency install:** Good (for listed pip packages)
- **Internal code graph restoration:** Poor (missing local modules)
- **Runnable system after rehydrate:** Not yet
- **UI white-label foundation:** Present but incomplete

## Recommended next 72-hour recovery plan
1. Restore internal modules referenced by `xi_cli.py` and `framework.py` (first unblock imports).
2. Add a `python -m xi_doctor` style preflight that asserts local module presence before CLI startup.
3. Expand `requirements.txt`/install docs to include `ollama` expectations and optional degraded-mode behavior.
4. Refactor UI components to token-first classes and API/mode injection props (as already described in white-label guide).
5. Add one deterministic smoke test: `source .venv/bin/activate && python3 xi_cli.py version` must pass in CI.
