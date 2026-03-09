#!/bin/bash
# =============================================================================
# EGOS Inteligência — ETL Progress Monitor v2.0
# Tracks CNPJ ETL progress (Partner nodes + SOCIO_DE rels)
# Runs via cron every 10 minutes: */10 * * * * /opt/bracc/scripts/etl-monitor.sh
# =============================================================================

set -euo pipefail

LOG_FILE="/opt/bracc/logs/etl-monitor.log"
STATE_FILE="/opt/bracc/logs/etl-monitor-state.json"

if [ -f /opt/bracc/infra/.env ]; then
  set -a; source /opt/bracc/infra/.env; set +a
fi

NEO4J_PASS="${NEO4J_PASSWORD:-BrAcc2026EgosNeo4j!}"
# Password loaded directly from NEO4J_PASSWORD

mkdir -p "$(dirname "$LOG_FILE")"

send_telegram() {
  local msg="$1"
  [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ] && return 0
  curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" -d "parse_mode=HTML" -d "text=${msg}" \
    --max-time 10 > /dev/null 2>&1 || true
}

# Check ETL process
ETL_PID=$(pgrep -f "bracc-etl run.*cnpj" | head -1 || echo "")

# Get current counts — Partner is the PRIMARY metric during Phase 3
PARTNER_COUNT=$(timeout 10 docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASS" \
  "MATCH (p:Partner) RETURN count(p) as c" --format plain 2>/dev/null | tail -1 || echo "0")
COMPANY_COUNT=$(timeout 10 docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASS" \
  "MATCH (c:Company) RETURN count(c) as c" --format plain 2>/dev/null | tail -1 || echo "0")
SOCIO_COUNT=$(timeout 10 docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASS" \
  "MATCH ()-[r:SOCIO_DE]->() RETURN count(r) as c" --format plain 2>/dev/null | tail -1 || echo "0")
PERSON_COUNT=$(timeout 10 docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASS" \
  "MATCH (p:Person) RETURN count(p) as c" --format plain 2>/dev/null | tail -1 || echo "0")

# Total entities
TOTAL=$((COMPANY_COUNT + PARTNER_COUNT + PERSON_COUNT))

# Load previous state
PREV_PARTNER=0
if [ -f "$STATE_FILE" ]; then
  PREV_PARTNER=$(grep -o "\"partner\":[0-9]*" "$STATE_FILE" 2>/dev/null | cut -d: -f2 || echo "0")
fi

# Calculate delta and progress
DELTA=$((PARTNER_COUNT - PREV_PARTNER))
TARGET_PARTNER=24600000  # 24.6M expected total partners from CNPJ QSA
if [ "$PARTNER_COUNT" -gt 0 ] && [ "$TARGET_PARTNER" -gt 0 ]; then
  PCT=$((PARTNER_COUNT * 100 / TARGET_PARTNER))
else
  PCT=0
fi

# Save state
echo "{\"partner\":${PARTNER_COUNT},\"company\":${COMPANY_COUNT},\"socio_de\":${SOCIO_COUNT},\"person\":${PERSON_COUNT},\"total\":${TOTAL},\"ts\":\"$(date -Iseconds)\"}" > "$STATE_FILE"

# Get ETL log cumulative rows
CUMULATIVE=$(tail -1 /opt/bracc/cnpj-etl.log 2>/dev/null | grep -o "cumulative: [0-9]*" | grep -o "[0-9]*" || echo "0")

# Log
TS=$(date "+%Y-%m-%d %H:%M:%S")
if [ -n "$ETL_PID" ]; then
  ETL_CPU=$(ps -p "$ETL_PID" -o %cpu= 2>/dev/null | xargs || echo "?")
  ETL_MEM=$(ps -p "$ETL_PID" -o rss= 2>/dev/null | awk "{printf \"%.1fGB\", \$1/1048576}" || echo "?")
  echo "[$TS] ETL running | Partner: ${PARTNER_COUNT} (+${DELTA}) ${PCT}% | SOCIO_DE: ${SOCIO_COUNT} | Company: ${COMPANY_COUNT} | Total: ${TOTAL} | Rows: ${CUMULATIVE} | CPU:${ETL_CPU}% RAM:${ETL_MEM}" >> "$LOG_FILE"
else
  echo "[$TS] ETL stopped | Partner: ${PARTNER_COUNT} ${PCT}% | SOCIO_DE: ${SOCIO_COUNT} | Company: ${COMPANY_COUNT} | Total: ${TOTAL}" >> "$LOG_FILE"
  
  # Alert if ETL stopped and not at 100%
  if [ "$PCT" -lt 95 ] && [ "$PREV_PARTNER" -gt 0 ]; then
    send_telegram "⚠️ <b>ETL Stopped</b>
Partner: ${PARTNER_COUNT} / ${TARGET_PARTNER} (${PCT}%)
SOCIO_DE: ${SOCIO_COUNT} | Company: ${COMPANY_COUNT}
Total entities: ${TOTAL}
<b>ETL process not running. May need restart.</b>
<code>tmux attach -t etl</code>"
  fi
fi

# Milestone alerts (every 1M new partners)
if [ "$DELTA" -gt 0 ] && [ $((PARTNER_COUNT % 1000000)) -lt "$DELTA" ] && [ "$PARTNER_COUNT" -gt 100000 ]; then
  MILLIONS=$((PARTNER_COUNT / 1000000))
  send_telegram "📊 <b>ETL Milestone</b>
Partner: ${MILLIONS}M / 24.6M (${PCT}%)
Company: ${COMPANY_COUNT} | Total: ${TOTAL}
Rows processed: ${CUMULATIVE}"
fi

# Completion alert
if [ "$PCT" -ge 95 ] && [ "$PREV_PARTNER" -lt $((TARGET_PARTNER * 95 / 100)) ]; then
  send_telegram "🎉 <b>ETL Near Complete!</b>
Partner: ${PARTNER_COUNT} (${PCT}%)
SOCIO_DE: ${SOCIO_COUNT}
Total entities: ${TOTAL}"
fi

# Trim log
if [ -f "$LOG_FILE" ] && [ "$(wc -l < "$LOG_FILE")" -gt 500 ]; then
  tail -n 200 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi
