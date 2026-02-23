# Omnibot Product Delivery Plan (Codex + Antigravity)

## Current repository truth (this checkout)
The component and docs foundation exists, but Track B appears **not fully synchronized** into this cloud checkout yet:
- Omnibot component exists: `00_core/ui/forge/Omnibot.tsx`
- White-label docs exist: `00_core/ui/ai-components/WHITE_LABEL_GUIDE.md`, `INTERACTION_STANDARD.md`
- Temporary typing/graft markers still present in Omnibot (`any` stream event placeholders).
- Hardcoded palette markers are still present in Omnibot / AI components.
- Claimed Track-B files are not present here (`theme_injector.ts`, `lib/omnibot_types.ts`, `walkthrough.md`, `task.md`).

## Collaboration model that scales
### Antigravity (local/runtime lane)
- Validate local runtime, stream wiring, endpoint behavior, model behavior.
- Publish branch + test logs to GitHub with exact commands and outputs.

### Codex (cloud/integration lane)
- Normalize types/contracts, refactor components, add guardrails/tests/docs.
- Produce reviewable PRs with deterministic checks and migration notes.

## Branching contract
- `main`: stable integration
- `feature/omnibot-track-b-sync`: import/sync local Track-B deltas
- `feature/omnibot-track-a-contracts`: canonical runtime contract hardening
- `feature/omnibot-track-c-plane`: management-plane integration

## Track A (next PR) — Runtime Contract Hardening
1. Add canonical runtime types (`StreamEvent`, `Receipt`, `RunStart`, `AgentThink`, `RunFinal`) in `00_core/ui/lib/omnibot_types.ts`.
2. Replace `any` stream placeholders in `Omnibot.tsx` with canonical types.
3. Implement safe event parser/guard for `window.postMessage` payloads.
4. Normalize `/api/ai/edit` response contract and error variants.
5. Add smoke checks for event decode + receipt rendering.

## Two-agent execution ritual (daily)
1. Antigravity opens/updates issue with local runtime findings.
2. Codex implements on branch + opens PR.
3. Antigravity pulls branch on Aries, runs local validation, posts pass/fail.
4. Merge only when both cloud checks and Aries checks pass.

## Deterministic checks
Use timeout-safe checks before every handoff:
```bash
./scripts/omnibot_track_a_audit.sh .
python3 -m compileall -q .
```

## Immediate action
Run `./scripts/omnibot_track_a_audit.sh .` in both environments and compare output.
That gives a precise, file-level baseline for what Track-B work is still unsynced before Track-A contract hardening begins.
