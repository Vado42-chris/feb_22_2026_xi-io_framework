# Global Filesystem Hang + Sync Drift Report

## What I verified in this environment
- Current repo path: `/workspace/feb_22_2026_xi-io_framework`
- Current commit: `ed943c5`
- The expected ChatGPT-added bootstrap files are present in the root of this repository:
  - `progress.py`, `terminal_ui.py`, `prompt_guard.py`, `workspace_registry.py`, `context_manager.py`, `image_analyzer.py`, `verification_manager.py`, `axiom_engine.py`
- The expected diagnosis docs are present:
  - `ROOT_CAUSE_ANALYSIS.md`, `SEARCH_STALL_DIAGNOSIS.md`

## Sync drift findings
- The sibling directory you referenced (`../xi-io_xibalba_framework_8_USB_install`) does **not** exist in this container, so I cannot directly compare/copy from it here.
- The only visible sibling repo is `../feb_22_2026_xi-io_framework` and it is byte-identical for all key files checked.

## Root-cause interpretation
Your reported symptoms can coexist:
1. **Filesystem hang behavior on host** (broad recursive scans over slow disk trees, caches, mirrored repos, or mountpoints).
2. **Sync drift between directories** (work landing in a different sibling path than the one being inspected).

Given your measured disk throughput (~32.7 MB/s), recursive scans and broad git operations can look hung even when progressing.

## Added tool for deterministic cross-directory diagnosis
- `scripts/sync_drift_probe.sh`

This script performs timeout-protected checks and compares key files against sibling directories without recursive full-tree operations.

## Use this on Aries exactly
```bash
cd /path/to/feb_22_2026_xi-io_framework
./scripts/sync_drift_probe.sh .
```

If `../xi-io_xibalba_framework_8_USB_install` exists on Aries, this will tell you in one run whether files are missing, different, or identical.

## Safe bridge workflow (manual, explicit)
If drift is confirmed, copy only required files explicitly (no recursive copy):
```bash
cp -v ../xi-io_xibalba_framework_8_USB_install/progress.py ./progress.py
cp -v ../xi-io_xibalba_framework_8_USB_install/terminal_ui.py ./terminal_ui.py
# repeat only for files flagged as ONLY_SIBLING or DIFF
```
Then validate:
```bash
python3 -m compileall -q .
python3 xi_cli.py version
```
