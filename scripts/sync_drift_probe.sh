#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

CANDIDATES=(
  "../xi-io_xibalba_framework_8_USB_install"
  "../feb_22_2026_xi-io_framework"
  "../xi-io_framework"
)

KEY_FILES=(
  "axiom_engine.py"
  "context_manager.py"
  "image_analyzer.py"
  "progress.py"
  "prompt_guard.py"
  "terminal_ui.py"
  "verification_manager.py"
  "workspace_registry.py"
  "optimized_orchestrator.py"
  "xi_utils.py"
  "ROOT_CAUSE_ANALYSIS.md"
  "SEARCH_STALL_DIAGNOSIS.md"
)

echo "== Sync Drift Probe =="
echo "root: $(pwd)"
echo "time: $(date -Iseconds)"

echo "\n[1] Current repository identity"
timeout 8 git rev-parse --short HEAD || true
timeout 8 git branch -vv || true

echo "\n[2] Candidate sibling discovery"
for c in "${CANDIDATES[@]}"; do
  if [ -d "$c" ]; then
    echo "FOUND:$c"
  else
    echo "MISSING:$c"
  fi
done

echo "\n[3] Local key file presence"
for f in "${KEY_FILES[@]}"; do
  [ -f "$f" ] && echo "LOCAL:OK:$f" || echo "LOCAL:MISSING:$f"
done

for c in "${CANDIDATES[@]}"; do
  [ -d "$c" ] || continue
  echo "\n[4] Comparing against $c"
  if [ -d "$c/.git" ]; then
    timeout 8 git -C "$c" rev-parse --short HEAD || true
  fi
  for f in "${KEY_FILES[@]}"; do
    if [ -f "$c/$f" ] && [ -f "$f" ]; then
      a=$(sha256sum "$f" | awk '{print $1}')
      b=$(sha256sum "$c/$f" | awk '{print $1}')
      if [ "$a" = "$b" ]; then
        echo "MATCH:$f"
      else
        echo "DIFF:$f"
      fi
    elif [ -f "$c/$f" ]; then
      echo "ONLY_SIBLING:$f"
    elif [ -f "$f" ]; then
      echo "ONLY_LOCAL:$f"
    else
      echo "MISSING_BOTH:$f"
    fi
  done
done

echo "\n[5] Safe copy plan template"
cat <<'EOF'
# Example (manual, explicit, no recursive copy):
# cp -v ../xi-io_xibalba_framework_8_USB_install/progress.py ./progress.py
# cp -v ../xi-io_xibalba_framework_8_USB_install/terminal_ui.py ./terminal_ui.py
EOF
