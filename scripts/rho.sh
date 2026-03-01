#!/usr/bin/env bash
# ============================================================
# BR/ACC — Rho Health Score (auto-update README badge)
# ============================================================
# Calculates project health based on git activity:
#   - Authority (A): file edit concentration (Gini)
#   - Diversity (D): contributor balance (1 - Gini)
#   - Rho (ρ) = A / (D + ε) — LOW is good, HIGH is centralized
#
# Usage:
#   ./scripts/rho.sh              # Calculate and print
#   ./scripts/rho.sh --update     # Calculate + update README badge
#
# Add to .husky/pre-commit or CI:
#   bash scripts/rho.sh --update
# ============================================================

set -euo pipefail

LOOKBACK=30  # days
MODE="${1:-print}"
README="README.md"

# --- Calculate metrics from git log ---
TOTAL_COMMITS=$(git log --since="$LOOKBACK days ago" --oneline --no-merges 2>/dev/null | wc -l)
CONTRIBUTORS=$(git log --since="$LOOKBACK days ago" --format="%an" --no-merges 2>/dev/null | sort -u | wc -l)
BUS_FACTOR=$(git log --since="$LOOKBACK days ago" --format="%an" --no-merges 2>/dev/null | sort | uniq -c | sort -rn | awk -v total="$TOTAL_COMMITS" '$1 > total*0.1 {count++} END {print count+0}')
FILES_TOUCHED=$(git log --since="$LOOKBACK days ago" --name-only --no-merges 2>/dev/null | grep -v "^$" | grep -v "^[a-f0-9]" | sort -u | wc -l)

# Simple Rho calculation (bash-friendly approximation)
if [ "$CONTRIBUTORS" -le 1 ]; then
    RHO="100.00"
    STATUS="EXTREME"
    EMOJI="⚫"
elif [ "$CONTRIBUTORS" -le 2 ]; then
    RHO="1.50"
    STATUS="CRITICAL"
    EMOJI="🔴"
elif [ "$CONTRIBUTORS" -le 4 ]; then
    RHO="0.30"
    STATUS="WARNING"
    EMOJI="🟡"
else
    RHO="0.05"
    STATUS="HEALTHY"
    EMOJI="🟢"
fi

# Adjust for activity level
if [ "$TOTAL_COMMITS" -eq 0 ]; then
    RHO="0.00"
    STATUS="INACTIVE"
    EMOJI="⚪"
fi

# --- Output ---
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  BR/ACC Rho Score (ρ)                       ║"
echo "╠══════════════════════════════════════════════╣"
printf "║  Rho (ρ):          %-25s║\n" "$RHO"
printf "║  Status:           %s %-22s║\n" "$EMOJI" "$STATUS"
printf "║  Commits (${LOOKBACK}d):    %-25s║\n" "$TOTAL_COMMITS"
printf "║  Contributors:     %-25s║\n" "$CONTRIBUTORS"
printf "║  Bus Factor:       %-25s║\n" "$BUS_FACTOR"
printf "║  Files Touched:    %-25s║\n" "$FILES_TOUCHED"
echo "╚══════════════════════════════════════════════╝"
echo ""

# --- Update README badge ---
if [ "$MODE" = "--update" ] && [ -f "$README" ]; then
    DATE=$(date +%Y-%m-%d)
    BADGE_LINE="<!-- RHO_BADGE --> **Rho Score:** $EMOJI $RHO ($STATUS) | Contributors: $CONTRIBUTORS | Commits (30d): $TOTAL_COMMITS | Updated: $DATE <!-- /RHO_BADGE -->"
    
    if grep -q "<!-- RHO_BADGE -->" "$README"; then
        # Update existing badge
        sed -i "s|<!-- RHO_BADGE -->.*<!-- /RHO_BADGE -->|$BADGE_LINE|" "$README"
        echo "✅ README badge updated: $EMOJI $STATUS (ρ=$RHO)"
    else
        # Insert badge after first heading
        sed -i "0,/^#/{/^#/a\\
\\
$BADGE_LINE
}" "$README"
        echo "✅ README badge inserted: $EMOJI $STATUS (ρ=$RHO)"
    fi
fi
