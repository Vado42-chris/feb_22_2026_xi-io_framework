# Search Stall Diagnosis (Antigravity / Codex)

## Result summary
- In this checkout, the bootstrap modules are present in the repository root:
  - `progress.py`
  - `terminal_ui.py`
  - `prompt_guard.py`
  - `workspace_registry.py`
  - `context_manager.py`
  - `image_analyzer.py`
  - `verification_manager.py`
  - `axiom_engine.py`
- No symbolic links were found under the repo tree in this environment.
- There is no `00_core/automation` directory in this checkout.

## Why recursive search can appear to hang
Even without symlink cycles, broad recursive scans can stall on:
1. `.git` internals (many small/object files)
2. regenerated virtualenv or cache folders (if present in your local machine)
3. binary-heavy trees when using `grep -R` without excludes

## Recommended safe search pattern
Use ripgrep and explicitly exclude heavy paths:

```bash
rg -n "<pattern>" . -g '!**/.git/**' -g '!**/.venv/**' -g '!**/node_modules/**' -g '!**/__pycache__/**'
```

For file discovery only:

```bash
rg --files . -g '!**/.git/**' -g '!**/.venv/**' -g '!**/node_modules/**' -g '!**/__pycache__/**'
```

## Probe-first commands for your side
If your Aries copy differs from this one, run:

```bash
find . -type l -printf '%p -> %l\n'
find . -maxdepth 5 -type d | sed -n '1,300p'
```

If these reveal links or a large nested mirror under `00_core/automation` on Aries, that would explain the behavior you saw there.
