#!/bin/bash
# =============================================================================
# EGOS Inteligência — Auto-Heal System v2.0
# Multi-layer self-healing with Telegram alerts and AI-safe recovery
# Runs via cron every 2 minutes: */2 * * * * /opt/bracc/scripts/auto-heal-v2.sh
#
# SAFETY PRINCIPLES:
#   - ONLY pre-approved commands (whitelist, never blacklist)
#   - NO code modifications, NO git operations, NO package installs
#   - ALL actions logged with timestamps
#   - Telegram alert on every heal action
#   - Escalation to human after 3 consecutive failures
# =============================================================================

set -euo pipefail

COMPOSE_DIR="/opt/bracc/infra"
LOG_FILE="/opt/bracc/logs/auto-heal.log"
STATE_FILE="/opt/bracc/logs/heal-state.json"
SITE_URL="https://inteligencia.egos.ia.br/"
API_HEALTH="https://inteligencia.egos.ia.br/health"
MAX_LOG_LINES=1000
MAX_CONSECUTIVE_FAILURES=3

if [ -f /opt/bracc/infra/.env ]; then
  set -a; source /opt/bracc/infra/.env; set +a
fi

NEO4J_PASS="${NEO4J_AUTH:-neo4j/neo4j}"
NEO4J_PASS="${NEO4J_PASS#*/}"

mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

send_telegram() {
  local msg="$1"
  [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ] && return 0
  curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" -d "parse_mode=HTML" -d "text=${msg}" \
    --max-time 10 > /dev/null 2>&1 || true
}

get_fail_count() {
  [ -f "$STATE_FILE" ] && grep -o '"fail":[0-9]*' "$STATE_FILE" 2>/dev/null | cut -d: -f2 || echo "0"
}
set_state() {
  echo "{\"fail\":$1,\"ts\":\"$(date -Iseconds)\",\"action\":\"$2\"}" > "$STATE_FILE"
}

# Trim log
if [ -f "$LOG_FILE" ] && [ "$(wc -l < "$LOG_FILE")" -gt "$MAX_LOG_LINES" ]; then
  tail -n 500 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

HEALED=0
HEAL_ACTION=""
FAIL_COUNT=$(get_fail_count)

# ─── ESCALATION GUARD ───────────────────────────────────────────────────────
if [ "$FAIL_COUNT" -ge "$MAX_CONSECUTIVE_FAILURES" ]; then
  LAST_MOD=$(stat -c %Y "$STATE_FILE" 2>/dev/null || echo "0")
  NOW=$(date +%s)
  if [ $((NOW - LAST_MOD)) -gt 3600 ]; then
    send_telegram "🚨 <b>EGOS ESCALATION</b>
${MAX_CONSECUTIVE_FAILURES} consecutive heal failures.
<b>Manual intervention required.</b>
<code>ssh root@VPS</code>
<code>cd /opt/bracc/infra && docker compose logs --tail 50</code>"
    touch "$STATE_FILE"
  fi
  log "ESCALATED: $FAIL_COUNT failures — waiting for human"
  exit 0
fi

# ─── CHECK 1: Container State ───────────────────────────────────────────────
EXPECTED=("infra-api-1" "infra-frontend-1" "bracc-neo4j" "infra-redis-1" "infra-caddy-1")
DOWN=""
for c in "${EXPECTED[@]}"; do
  ST=$(docker inspect --format='{{.State.Status}}' "$c" 2>/dev/null || echo "missing")
  [ "$ST" != "running" ] && DOWN="${DOWN}$(echo "$c" | sed 's/infra-//;s/-1$//')(${ST}) "
done

if [ -n "$DOWN" ]; then
  HEAL_ACTION="Container(s) down: ${DOWN}"
  log "HEAL: $HEAL_ACTION"
  cd "$COMPOSE_DIR" && docker compose up -d >> "$LOG_FILE" 2>&1
  HEALED=1
fi

# ─── CHECK 2: Healthcheck ───────────────────────────────────────────────────
if [ "$HEALED" -eq 0 ]; then
  for c in "infra-api-1" "infra-frontend-1"; do
    H=$(docker inspect --format='{{.State.Health.Status}}' "$c" 2>/dev/null || echo "unknown")
    if [ "$H" = "unhealthy" ]; then
      SVC=$(echo "$c" | sed 's/infra-//;s/-1$//')
      HEAL_ACTION="$SVC unhealthy"
      log "HEAL: $HEAL_ACTION — restarting $SVC"
      cd "$COMPOSE_DIR" && docker compose restart "$SVC" >> "$LOG_FILE" 2>&1
      HEALED=1; break
    fi
  done
fi

# ─── CHECK 3: API Health Endpoint ───────────────────────────────────────────
if [ "$HEALED" -eq 0 ]; then
  API_CODE=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$API_HEALTH" 2>/dev/null || echo "000")
  if [ "$API_CODE" != "200" ]; then
    HEAL_ACTION="API health HTTP ${API_CODE}"
    log "HEAL: $HEAL_ACTION — restarting api"
    cd "$COMPOSE_DIR" && docker compose restart api >> "$LOG_FILE" 2>&1
    HEALED=1
  fi
fi

# ─── CHECK 4: Site URL ──────────────────────────────────────────────────────
if [ "$HEALED" -eq 0 ]; then
  HTTP=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$SITE_URL" 2>/dev/null || echo "000")
  if [ "$HTTP" = "502" ] || [ "$HTTP" = "503" ] || [ "$HTTP" = "000" ]; then
    HEAL_ACTION="Site HTTP ${HTTP}"
    log "HEAL: $HEAL_ACTION — full restart"
    cd "$COMPOSE_DIR" && docker compose down >> "$LOG_FILE" 2>&1
    sleep 5
    cd "$COMPOSE_DIR" && docker compose up -d >> "$LOG_FILE" 2>&1
    HEALED=1
  fi
fi

# ─── CHECK 5: Disk Space ────────────────────────────────────────────────────
DISK=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK" -gt 90 ]; then
  log "WARN: Disk ${DISK}% — pruning Docker"
  docker system prune -f >> "$LOG_FILE" 2>&1
  send_telegram "⚠️ <b>EGOS Disk Warning</b>
Disk at ${DISK}%. Docker prune executed."
fi

# ─── CHECK 6: Neo4j Responsiveness ──────────────────────────────────────────
if [ "$HEALED" -eq 0 ]; then
  NEO4J_OK=$(timeout 10 docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASS" \
    'RETURN 1' --format plain 2>/dev/null | tail -1 || echo "fail")
  if [ "$NEO4J_OK" != "1" ]; then
    HEAL_ACTION="Neo4j unresponsive"
    log "HEAL: $HEAL_ACTION — restarting neo4j container"
    docker restart bracc-neo4j >> "$LOG_FILE" 2>&1
    HEALED=1
  fi
fi

# ─── RESULT ──────────────────────────────────────────────────────────────────
if [ "$HEALED" -eq 1 ]; then
  sleep 30
  VERIFY=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$SITE_URL" 2>/dev/null || echo "000")
  
  if [ "$VERIFY" = "200" ]; then
    log "SUCCESS: Healed — site HTTP 200"
    set_state 0 "$HEAL_ACTION"
    send_telegram "🔧 <b>EGOS Auto-Heal</b>
<b>Issue:</b> ${HEAL_ACTION}
<b>Result:</b> ✅ Site back online (HTTP 200)"
  else
    NEW_FAIL=$((FAIL_COUNT + 1))
    log "FAIL: Heal attempted but site HTTP $VERIFY (failure $NEW_FAIL/$MAX_CONSECUTIVE_FAILURES)"
    set_state "$NEW_FAIL" "$HEAL_ACTION"
    send_telegram "⚠️ <b>EGOS Heal Failed</b>
<b>Issue:</b> ${HEAL_ACTION}
<b>Result:</b> ❌ Site HTTP ${VERIFY}
<b>Failures:</b> ${NEW_FAIL}/${MAX_CONSECUTIVE_FAILURES}
${NEW_FAIL} >= ${MAX_CONSECUTIVE_FAILURES} → will escalate next check"
  fi
else
  # All healthy — reset failure counter
  [ "$FAIL_COUNT" -gt 0 ] && set_state 0 "recovered"
fi
