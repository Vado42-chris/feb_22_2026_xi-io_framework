#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

echo "== XI Root Cause Doctor =="
echo "cwd: $(pwd)"
echo "time: $(date -Iseconds)"

echo "\n[1] Git topology"
timeout 8 git rev-parse --is-inside-work-tree || true
timeout 8 git branch -vv || true
timeout 8 git remote -v || true

echo "\n[2] Git pull dry-run signal"
GIT_TERMINAL_PROMPT=0 GIT_TRACE=1 timeout 12 git pull --ff-only 2>&1 | sed -n '1,120p' || true

echo "\n[3] Lock & hook checks"
[ -f .git/index.lock ] && echo "index.lock: PRESENT" || echo "index.lock: absent"
find .git/hooks -maxdepth 1 -type f -perm -u+x -printf 'hook:%f\n' 2>/dev/null | sed -n '1,60p'

echo "\n[4] Symlink/cycle probe"
timeout 8 find . -xdev -type l -printf '%p -> %l\n' | sed -n '1,80p' || true

echo "\n[5] Heavy directory hotspot probe (top 20 by file count)"
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
root=Path('.')
counts=defaultdict(int)
for p in root.rglob('*'):
    try:
        if p.is_file():
            parent=str(p.parent)
            counts[parent]+=1
    except Exception:
        pass
for k,v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:20]:
    print(f"{v:6d}  {k}")
PY

echo "\n[6] Safe search smoke"
timeout 8 rg -n "class|def|import" . -g '!**/.git/**' -g '!**/.venv/**' -g '!**/node_modules/**' -g '!**/__pycache__/**' | sed -n '1,40p' || true

echo "\n[7] Repository size summary"
timeout 8 du -sh . .git 2>/dev/null || true

echo "\nDoctor complete."
