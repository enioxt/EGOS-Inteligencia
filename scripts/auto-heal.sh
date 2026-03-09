#!/bin/bash
# =============================================================================
# EGOS Inteligência — Auto-Heal System v1.0
# Monitors Docker containers and restarts unhealthy/stopped services
# Runs via cron every 2 minutes
# =============================================================================

set -euo pipefail

COMPOSE_DIR="/opt/bracc/infra"
LOG_FILE="/opt/bracc/logs/auto-heal.log"
SITE_URL="https://inteligencia.egos.ia.br/"
MAX_LOG_LINES=500

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Trim log file if too large
if [ -f "$LOG_FILE" ] && [ "$(wc -l < "$LOG_FILE")" -gt "$MAX_LOG_LINES" ]; then
  tail -n 200 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

HEALED=0

# ─── CHECK 1: Container State ───────────────────────────────────────────────
# Detect containers that are Created/Exited/Dead (not running)
EXPECTED_CONTAINERS=("infra-api-1" "infra-frontend-1" "bracc-neo4j" "infra-redis-1" "infra-caddy-1")

for container in "${EXPECTED_CONTAINERS[@]}"; do
  STATE=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "missing")
  
  if [ "$STATE" != "running" ]; then
    log "HEAL: Container $container is '$STATE' — restarting all services"
    cd "$COMPOSE_DIR" && docker compose up -d 2>&1 | head -5 >> "$LOG_FILE"
    HEALED=1
    break
  fi
done

# ─── CHECK 2: Healthcheck Status ────────────────────────────────────────────
# If containers are running but unhealthy, restart the specific service
if [ "$HEALED" -eq 0 ]; then
  for container in "infra-api-1" "infra-frontend-1"; do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
    
    if [ "$HEALTH" = "unhealthy" ]; then
      SERVICE_NAME=$(echo "$container" | sed 's/infra-//;s/-1$//')
      log "HEAL: $container is unhealthy — restarting $SERVICE_NAME"
      cd "$COMPOSE_DIR" && docker compose restart "$SERVICE_NAME" 2>&1 | head -3 >> "$LOG_FILE"
      HEALED=1
    fi
  done
fi

# ─── CHECK 3: External URL Check ────────────────────────────────────────────
# If the site returns 502/503/000, force restart everything
if [ "$HEALED" -eq 0 ]; then
  HTTP_CODE=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$SITE_URL" 2>/dev/null || echo "000")
  
  if [ "$HTTP_CODE" = "502" ] || [ "$HTTP_CODE" = "503" ] || [ "$HTTP_CODE" = "000" ]; then
    log "HEAL: Site returned HTTP $HTTP_CODE — force restarting all services"
    cd "$COMPOSE_DIR" && docker compose down 2>&1 | tail -3 >> "$LOG_FILE"
    sleep 5
    cd "$COMPOSE_DIR" && docker compose up -d 2>&1 | tail -5 >> "$LOG_FILE"
    HEALED=1
  fi
fi

# ─── CHECK 4: Disk Space ────────────────────────────────────────────────────
# If disk >90%, prune Docker and warn
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 90 ]; then
  log "WARN: Disk usage at ${DISK_USAGE}% — pruning Docker"
  docker system prune -f --volumes 2>&1 | tail -3 >> "$LOG_FILE"
fi

# ─── RESULT ──────────────────────────────────────────────────────────────────
if [ "$HEALED" -eq 1 ]; then
  # Wait for services to come up, then verify
  sleep 30
  VERIFY=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 10 "$SITE_URL" 2>/dev/null || echo "000")
  log "VERIFY: After heal, site returned HTTP $VERIFY"
  
  if [ "$VERIFY" = "200" ]; then
    log "SUCCESS: Auto-heal completed — site is back online"
  else
    log "FAIL: Auto-heal attempted but site still returns HTTP $VERIFY — manual intervention needed"
  fi
fi
