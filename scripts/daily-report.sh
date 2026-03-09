#!/bin/bash
# =============================================================================
# EGOS Inteligência — Daily Health Report v1.0
# Sends comprehensive system health report to Telegram
# Runs via cron daily at 8AM: 0 8 * * * /opt/bracc/scripts/daily-report.sh
# =============================================================================

set -euo pipefail

# ─── CONFIG ──────────────────────────────────────────────────────────────────
COMPOSE_DIR="/opt/bracc/infra"
SITE_URL="https://inteligencia.egos.ia.br/"
NEO4J_USER="neo4j"
LOG_FILE="/opt/bracc/logs/daily-report.log"

# Load env vars (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NEO4J_AUTH)
if [ -f /opt/bracc/infra/.env ]; then
  set -a
  source /opt/bracc/infra/.env
  set +a
fi

NEO4J_PASS="${NEO4J_AUTH#*/}"

# ─── TELEGRAM SENDER ────────────────────────────────────────────────────────
send_telegram() {
  local message="$1"
  local parse_mode="${2:-MarkdownV2}"
  
  if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
    echo "[$(date)] WARN: Telegram not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)" >> "$LOG_FILE"
    return 1
  fi
  
  curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "parse_mode=${parse_mode}" \
    -d "text=${message}" \
    --max-time 15 > /dev/null 2>&1
}

# Escape special chars for MarkdownV2
escape_md() {
  echo "$1" | sed 's/[_*[\]()~`>#+=|{}.!-]/\\&/g'
}

# ─── COLLECT METRICS ────────────────────────────────────────────────────────
mkdir -p "$(dirname "$LOG_FILE")"

# Container status
CONTAINERS_UP=0
CONTAINERS_TOTAL=5
CONTAINER_DETAILS=""
for c in infra-api-1 infra-frontend-1 bracc-neo4j infra-redis-1 infra-caddy-1; do
  STATUS=$(docker inspect --format='{{.State.Status}}' "$c" 2>/dev/null || echo "missing")
  HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$c" 2>/dev/null || echo "n/a")
  UPTIME=$(docker inspect --format='{{.State.StartedAt}}' "$c" 2>/dev/null | xargs -I{} date -d {} +%s 2>/dev/null || echo "0")
  NOW=$(date +%s)
  if [ "$UPTIME" != "0" ] && [ "$STATUS" = "running" ]; then
    UPTIME_HOURS=$(( (NOW - UPTIME) / 3600 ))
    CONTAINERS_UP=$((CONTAINERS_UP + 1))
    SHORT_NAME=$(echo "$c" | sed 's/infra-//;s/-1$//')
    CONTAINER_DETAILS="${CONTAINER_DETAILS}  ✅ ${SHORT_NAME}: ${UPTIME_HOURS}h"$'\n'
  else
    SHORT_NAME=$(echo "$c" | sed 's/infra-//;s/-1$//')
    CONTAINER_DETAILS="${CONTAINER_DETAILS}  ❌ ${SHORT_NAME}: ${STATUS}"$'\n'
  fi
done

# Site HTTP check
HTTP_CODE=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$SITE_URL" 2>/dev/null || echo "000")
RESPONSE_TIME=$(curl -sL -o /dev/null -w '%{time_total}' --max-time 10 "$SITE_URL" 2>/dev/null || echo "0")

# Neo4j counts
NEO4J_NODES=$(docker exec bracc-neo4j cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" \
  'MATCH (n) RETURN count(n) as c' --format plain 2>/dev/null | tail -1 || echo "error")
NEO4J_RELS=$(docker exec bracc-neo4j cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" \
  'MATCH ()-[r]->() RETURN count(r) as c' --format plain 2>/dev/null | tail -1 || echo "error")
SOCIO_DE_COUNT=$(docker exec bracc-neo4j cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" \
  'MATCH ()-[r:SOCIO_DE]->() RETURN count(r) as c' --format plain 2>/dev/null | tail -1 || echo "error")

# Disk usage
DISK_USAGE=$(df / | awk 'NR==2 {print $5}')
DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')

# Memory
MEM_USED=$(free -h | awk 'NR==2 {print $3}')
MEM_TOTAL=$(free -h | awk 'NR==2 {print $2}')

# ETL status
ETL_PID=$(pgrep -f 'bracc-etl run.*cnpj' | head -1 || echo "")
if [ -n "$ETL_PID" ]; then
  ETL_STATUS="🔄 Running (PID: $ETL_PID)"
  ETL_CPU=$(ps -p "$ETL_PID" -o %cpu= 2>/dev/null | xargs || echo "?")
  ETL_MEM=$(ps -p "$ETL_PID" -o rss= 2>/dev/null | awk '{printf "%.1fGB", $1/1048576}' || echo "?")
  ETL_TIME=$(ps -p "$ETL_PID" -o etime= 2>/dev/null | xargs || echo "?")
  ETL_STATUS="${ETL_STATUS}\n  CPU: ${ETL_CPU}% | RAM: ${ETL_MEM} | Uptime: ${ETL_TIME}"
else
  ETL_STATUS="⏹️ Not running"
fi

# Auto-heal stats (from log)
HEAL_COUNT=0
if [ -f /opt/bracc/logs/auto-heal.log ]; then
  HEAL_COUNT=$(grep -c "HEAL:" /opt/bracc/logs/auto-heal.log 2>/dev/null || echo "0")
fi

# Backup status
LAST_BACKUP=$(ls -t /opt/bracc/backups/neo4j-backup-*.tar.gz 2>/dev/null | head -1 || echo "none")
if [ "$LAST_BACKUP" != "none" ]; then
  BACKUP_SIZE=$(du -h "$LAST_BACKUP" | cut -f1)
  BACKUP_DATE=$(stat -c %y "$LAST_BACKUP" 2>/dev/null | cut -d' ' -f1)
  BACKUP_STATUS="✅ ${BACKUP_DATE} (${BACKUP_SIZE})"
else
  BACKUP_STATUS="❌ No backups found"
fi

# ─── BUILD REPORT ────────────────────────────────────────────────────────────
HEALTH_EMOJI="🟢"
if [ "$CONTAINERS_UP" -lt "$CONTAINERS_TOTAL" ] || [ "$HTTP_CODE" != "200" ]; then
  HEALTH_EMOJI="🔴"
elif [ "$HEAL_COUNT" -gt 0 ]; then
  HEALTH_EMOJI="🟡"
fi

# Plain text format (HTML parse mode for Telegram)
REPORT="<b>${HEALTH_EMOJI} EGOS Inteligência — Daily Report</b>
<code>$(date '+%Y-%m-%d %H:%M UTC%z')</code>

<b>🐳 Containers:</b> ${CONTAINERS_UP}/${CONTAINERS_TOTAL}
${CONTAINER_DETAILS}
<b>🌐 Site:</b> HTTP ${HTTP_CODE} (${RESPONSE_TIME}s)
<b>🔧 Auto-heals today:</b> ${HEAL_COUNT}

<b>📊 Neo4j:</b>
  Nodes: ${NEO4J_NODES}
  Relationships: ${NEO4J_RELS}
  SOCIO_DE: ${SOCIO_DE_COUNT}

<b>📦 ETL:</b>
${ETL_STATUS}

<b>💾 Resources:</b>
  Disk: ${DISK_USAGE} used (${DISK_AVAIL} free)
  RAM: ${MEM_USED}/${MEM_TOTAL}

<b>🗄️ Backup:</b> ${BACKUP_STATUS}

<i>inteligencia.egos.ia.br</i>"

# ─── SEND ────────────────────────────────────────────────────────────────────
send_telegram "$REPORT" "HTML"
echo "[$(date)] Daily report sent" >> "$LOG_FILE"
echo "$REPORT" >> "$LOG_FILE"
