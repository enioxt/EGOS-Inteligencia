#!/bin/bash
# restore-context-on-start.sh — Integração /start + Context Manager

echo ""
echo "🔍 Checking for context snapshots..."
echo ""

# Verificar se existe snapshot
if [ -d "docs/_context_snapshots" ] && [ "$(ls -A docs/_context_snapshots/*.json 2>/dev/null)" ]; then
  # Pegar último snapshot
  latest=$(bun scripts/context-manager.ts latest 2>/dev/null)

  if [ $? -eq 0 ]; then
    echo "📸 Last Context Snapshot Found:"
    echo "$latest" | jq -r '"  Timestamp: \(.timestamp)\n  Trigger: \(.snapshot_trigger)\n  Branch: \(.branch)\n  Last Commit: \(.lastCommit)\n  Uncommitted: \(.uncommittedFiles) files"' 2>/dev/null

    echo ""
    echo "📋 Last Working Context:"
    echo "$latest" | jq -r '.workingContext' 2>/dev/null | sed 's/^/  /'

    echo ""
    echo "💡 To see full snapshot: bun scripts/context-manager.ts latest"
    echo "💡 To create new snapshot: bun scripts/context-manager.ts snapshot manual"
  else
    echo "⚠️  No snapshots available"
  fi
else
  echo "ℹ️  No context snapshots found. Create one with: bun scripts/context-manager.ts snapshot manual"
fi

echo ""
