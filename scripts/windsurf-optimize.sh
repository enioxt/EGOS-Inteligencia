#!/bin/bash
# =============================================================================
# Windsurf IDE Memory Optimization Script
# Run when Windsurf feels slow or before long sessions
# Usage: bash ~/br-acc/scripts/windsurf-optimize.sh
# =============================================================================

set -euo pipefail

echo "🔧 Windsurf Optimization Script v1.0"
echo "======================================"

# 1. Clear npm/npx caches
echo ""
echo "📦 Clearing npm caches..."
NPM_BEFORE=$(du -sh ~/.npm/ 2>/dev/null | cut -f1)
npm cache clean --force 2>/dev/null
find ~/.npm/_npx -maxdepth 1 -type d -mtime +3 -exec rm -rf {} + 2>/dev/null || true
NPM_AFTER=$(du -sh ~/.npm/ 2>/dev/null | cut -f1)
echo "   npm: $NPM_BEFORE → $NPM_AFTER"

# 2. Clear Windsurf render/GPU caches
echo ""
echo "🖥️  Clearing Windsurf caches..."
WS_BEFORE=$(du -sh ~/.config/Windsurf/ 2>/dev/null | cut -f1)
rm -rf ~/.config/Windsurf/Cache/Cache_Data/* 2>/dev/null || true
rm -rf ~/.config/Windsurf/GPUCache/* 2>/dev/null || true
rm -rf ~/.config/Windsurf/DawnWebGPUCache/* 2>/dev/null || true
rm -rf ~/.config/Windsurf/DawnGraphiteCache/* 2>/dev/null || true
rm -rf ~/.config/Windsurf/Crashpad/completed/* 2>/dev/null || true
rm -rf ~/.config/Windsurf/Crashpad/pending/* 2>/dev/null || true
find ~/.config/Windsurf/logs -name "*.log" -mtime +3 -delete 2>/dev/null || true
find ~/.config/Windsurf/logs -maxdepth 1 -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
WS_AFTER=$(du -sh ~/.config/Windsurf/ 2>/dev/null | cut -f1)
echo "   Windsurf: $WS_BEFORE → $WS_AFTER"

# 3. Clear old Cascade caches
echo ""
echo "🌊 Clearing old Cascade data..."
CASCADE_BEFORE=$(du -sh ~/.codeium/windsurf/cascade/ 2>/dev/null | cut -f1)
find ~/.codeium/windsurf/cascade -type f -mtime +14 -delete 2>/dev/null || true
CASCADE_AFTER=$(du -sh ~/.codeium/windsurf/cascade/ 2>/dev/null | cut -f1)
echo "   Cascade: $CASCADE_BEFORE → $CASCADE_AFTER"

# 4. Clear temp files
echo ""
echo "🧹 Clearing temp files..."
find /tmp -name "windsurf-terminal-*" -mmin +60 -delete 2>/dev/null || true
find /tmp -name "vscode-typescript*" -type d -mmin +120 -exec rm -rf {} + 2>/dev/null || true
find /tmp -name "vscode-ipc-*" -mtime +1 -delete 2>/dev/null || true
echo "   Temp files cleaned"

# 5. Drop filesystem caches (safe, needs no sudo usually)
echo ""
echo "💾 Dropping filesystem page cache..."
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 && echo "   Page cache dropped" || echo "   (needs sudo — skipped)"

# 6. Memory report
echo ""
echo "📊 Memory Status:"
free -h
echo ""
echo "Top memory consumers:"
ps aux --sort=-%mem | head -8 | awk '{printf "  %5s MB  %s\n", int($6/1024), $11}'
echo ""
echo "✅ Optimization complete. Restart Windsurf for full effect."
echo "   Tip: Close unused tabs and limit open workspaces to reduce memory."
