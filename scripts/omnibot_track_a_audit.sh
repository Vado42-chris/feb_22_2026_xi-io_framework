#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

echo "== Omnibot Track Audit =="
echo "repo: $(pwd)"
echo "commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"

echo "\n[1] Expected Track-B artifacts"
artifacts=(
  "00_core/ui/forge/Omnibot.tsx"
  "00_core/ui/ai-components/SidebarCoPilot.tsx"
  "00_core/ui/ai-components/AICompletion.tsx"
  "00_core/ui/theme_injector.ts"
  "00_core/ui/lib/omnibot_types.ts"
  "walkthrough.md"
  "task.md"
)
for f in "${artifacts[@]}"; do
  [ -f "$f" ] && echo "FOUND:$f" || echo "MISSING:$f"
done

echo "\n[2] Omnibot temporary typing + stream graft markers"
rg -n "GRAFT|type StreamEvent = any|type RunStartEvent = any|type AgentThinkEvent = any" 00_core/ui/forge/Omnibot.tsx || true

echo "\n[3] Hardcoded UI palette markers (zinc/orange/hex literals)"
rg -n "zinc-|orange-|#[0-9a-fA-F]{3,6}|bg-black|text-white" \
  00_core/ui/forge/Omnibot.tsx \
  00_core/ui/ai-components/SidebarCoPilot.tsx \
  00_core/ui/ai-components/AICompletion.tsx || true

echo "\n[4] Token usage markers"
rg -n "var\(--ui-|TOKENS|theme|white label|white-label" 00_core/ui -g '*.tsx' -g '*.ts' -g '*.md' || true

echo "\n[5] Runtime endpoint touchpoints"
rg -n "fetch\('/api/ai/edit'|run.final|window.addEventListener\('message'" 00_core/ui/forge/Omnibot.tsx || true

echo "\nAudit complete."
