# Root Cause Analysis: Recursive Search + Git/Pull Stall Symptoms

## Executive conclusion
In this container snapshot, we **cannot reproduce a true filesystem recursion loop**. The likely root issue class is **environment-specific scan amplification** (heavy recursive traversal paths) plus potential **Git remote/tracking/credential waits** on your Aries machine.

## What was verified in this checkout
1. No symlink cycles were found.
2. No `00_core/automation` directory exists in this checkout.
3. Repository is small (~1.2M) and sparse in file count.
4. `git pull` does not hang here; it exits quickly because branch `work` has no upstream tracking.

## Why your Aries behavior can still hang
Even if this checkout is clean, Aries may differ and still hang when tools recurse into:
- `.git` object trees
- `.venv`, `node_modules`, `__pycache__`
- mirrored/nested framework copies
- network mounts / slow disks / antivirus scan-on-read

Additionally, `git pull` can appear to hang when waiting for:
- upstream resolution over unstable network
- credential helper prompt deadlock in non-interactive shells
- remote host DNS latency / unreachable endpoints

## Root-cause buckets and signatures

### A) Recursive scan amplification (most likely)
**Signature:** `grep -R` / search APIs freeze only on broad scans; targeted file probes remain responsive.

### B) Host I/O bottleneck
**Signature:** all file-heavy commands degrade (find/grep/git status), especially with many small files.

### C) Git remote/credential wait
**Signature:** `git pull` hangs while local `git status` is fine.

### D) Hidden symlink or bind-mount loops (possible on Aries only)
**Signature:** directory walk never terminates or explodes in depth.

## Deterministic triage order on Aries
1. `timeout 8 find . -xdev -type l -printf '%p -> %l\n'`
2. `timeout 8 rg --files . -g '!**/.git/**' -g '!**/.venv/**' -g '!**/node_modules/**' -g '!**/__pycache__/**' | head`
3. `GIT_TERMINAL_PROMPT=0 GIT_TRACE=1 timeout 15 git pull --ff-only`
4. `timeout 8 git remote -v && timeout 8 git branch -vv`
5. `timeout 8 find . -maxdepth 5 -type d | sed -n '1,300p'`

## Added tooling
A diagnostic script was added:
- `scripts/root_cause_doctor.sh`

It runs timeout-protected probes for:
- git topology and pull signal,
- lock/hook checks,
- symlink/cycle probe,
- hotspot directory file counts,
- safe recursive search smoke test.

## Immediate operational guardrails
- Avoid `grep -R .` style scans in agent tooling.
- Standardize on `rg` with excludes.
- Run the doctor script before long sessions.
- Enforce timeout wrappers for search and git network operations.
