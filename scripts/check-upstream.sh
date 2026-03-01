#!/usr/bin/env bash
# ============================================================
# BR/ACC — Fork Monitor: Check upstream before push
# ============================================================
# Compares our fork (enioxt/br-acc) with upstream (World-Open-Graph/br-acc)
# to avoid duplicated work and identify collaboration opportunities.
#
# Usage:
#   ./scripts/check-upstream.sh          # Full check
#   ./scripts/check-upstream.sh --quick  # Just commit count
#
# Add to .husky/pre-push:
#   bash scripts/check-upstream.sh --quick
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

UPSTREAM="World-Open-Graph/br-acc"
FORK="enioxt/br-acc"
MODE="${1:-full}"

log() { echo -e "${GREEN}[UPSTREAM]${NC} $1"; }
warn() { echo -e "${YELLOW}[OVERLAP]${NC} $1"; }
err() { echo -e "${RED}[CONFLICT]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }

# Ensure upstream remote exists
if ! git remote | grep -q upstream; then
    git remote add upstream "https://github.com/$UPSTREAM.git" 2>/dev/null || true
fi

log "Fetching upstream ($UPSTREAM)..."
git fetch upstream --quiet 2>/dev/null || { warn "Could not fetch upstream. Continuing..."; exit 0; }

# Count commits ahead/behind
BEHIND=$(git rev-list --count HEAD..upstream/main 2>/dev/null || echo "?")
AHEAD=$(git rev-list --count upstream/main..HEAD 2>/dev/null || echo "?")

log "Our fork: ${AHEAD} commits ahead, ${BEHIND} commits behind upstream"

if [ "$MODE" = "--quick" ]; then
    if [ "$BEHIND" != "?" ] && [ "$BEHIND" -gt 20 ]; then
        warn "We are $BEHIND commits behind upstream. Consider rebasing."
        warn "  git fetch upstream && git rebase upstream/main"
    fi
    exit 0
fi

# Full mode: analyze recent upstream changes
echo ""
log "═══════════════════════════════════════════════"
log "UPSTREAM RECENT ACTIVITY (last 7 days)"
log "═══════════════════════════════════════════════"

git log upstream/main --oneline --since="7 days ago" --no-merges 2>/dev/null | head -20 | while read -r line; do
    info "$line"
done

# Check for overlapping files (files we both modified recently)
echo ""
log "═══════════════════════════════════════════════"
log "OVERLAP CHECK (files modified by both)"
log "═══════════════════════════════════════════════"

OUR_FILES=$(git diff --name-only upstream/main..HEAD 2>/dev/null | sort)
THEIR_FILES=$(git log upstream/main --name-only --oneline --since="7 days ago" --no-merges 2>/dev/null | grep -v "^[a-f0-9]" | sort -u)

OVERLAP=$(comm -12 <(echo "$OUR_FILES") <(echo "$THEIR_FILES") 2>/dev/null || true)

if [ -n "$OVERLAP" ]; then
    err "OVERLAP DETECTED — These files were modified by BOTH us and upstream:"
    echo "$OVERLAP" | while read -r f; do
        [ -n "$f" ] && err "  → $f"
    done
    echo ""
    warn "RECOMMENDATION:"
    warn "  1. Review upstream changes: git diff upstream/main -- <file>"
    warn "  2. If they're ahead, consider rebasing: git rebase upstream/main"
    warn "  3. If we have better changes, prepare a PR to upstream"
else
    log "✅ No file overlap detected. Safe to push."
fi

# Check upstream PRs and issues
echo ""
log "═══════════════════════════════════════════════"
log "UPSTREAM OPEN PRs"
log "═══════════════════════════════════════════════"

if command -v gh &>/dev/null; then
    gh pr list --repo "$UPSTREAM" --limit 5 2>/dev/null | while read -r line; do
        info "$line"
    done
    
    echo ""
    log "UPSTREAM RECENT ISSUES"
    gh issue list --repo "$UPSTREAM" --limit 5 2>/dev/null | while read -r line; do
        info "$line"
    done
else
    warn "Install GitHub CLI (gh) for PR/issue monitoring"
fi

echo ""
log "═══════════════════════════════════════════════"
log "SUMMARY"
log "  Fork: $AHEAD ahead, $BEHIND behind"
log "  Overlap: $(echo "$OVERLAP" | grep -c . 2>/dev/null || echo 0) files"
log "═══════════════════════════════════════════════"
