#!/bin/bash
# =============================================================================
# Neo4j Daily Backup Script — EGOS Inteligência v2.0
# Cron: 0 3 * * * /opt/bracc/scripts/neo4j-backup.sh >> /opt/bracc/backups/backup.log 2>&1
# Strategy: hot tar of data volume + count snapshot + Telegram alert on failure
# =============================================================================

set -euo pipefail

BACKUP_DIR=/opt/bracc/backups
MAX_BACKUPS=5
DATE=$(date +%Y%m%d_%H%M%S)
NEO4J_DATA=/var/lib/docker/volumes/infra_neo4j-data/_data

if [ -f /opt/bracc/infra/.env ]; then
  set -a; source /opt/bracc/infra/.env; set +a
fi

NEO4J_PASS="${NEO4J_AUTH:-neo4j/neo4j}"
NEO4J_PASS="${NEO4J_PASS#*/}"

mkdir -p "$BACKUP_DIR"

send_telegram() {
  local msg="$1"
  [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ] && return 0
  curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" -d "parse_mode=HTML" -d "text=${msg}" \
    --max-time 10 > /dev/null 2>&1 || true
}

echo "[$DATE] === Neo4j Backup Starting ==="

# Step 1: Count snapshot
echo "[$DATE] Taking count snapshot..."
docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASS" \
    "MATCH (n) RETURN labels(n)[0] AS tipo, count(n) AS total ORDER BY total DESC" \
    > "$BACKUP_DIR/neo4j_counts_$DATE.txt" 2>&1 || true

# Step 2: Hot tar backup
echo "[$DATE] Starting hot tar backup ($(du -sh "$NEO4J_DATA" 2>/dev/null | cut -f1))..."
if tar czf "$BACKUP_DIR/neo4j_data_$DATE.tar.gz" -C /var/lib/docker/volumes/infra_neo4j-data _data 2>&1; then
    SIZE=$(ls -lh "$BACKUP_DIR/neo4j_data_$DATE.tar.gz" | awk '{print $5}')
    echo "[$DATE] ✅ Backup saved: neo4j_data_$DATE.tar.gz ($SIZE)"
    send_telegram "🗄️ <b>Neo4j Backup OK</b>
Size: ${SIZE}
File: neo4j_data_${DATE}.tar.gz"
else
    TAR_EXIT=$?
    echo "[$DATE] ⚠️ tar exited with code $TAR_EXIT"
    send_telegram "❌ <b>Neo4j Backup FAILED</b>
Exit code: ${TAR_EXIT}
<b>Check:</b> <code>tail -20 /opt/bracc/backups/backup.log</code>"
fi

# Step 3: Rotate old backups
ls -t "$BACKUP_DIR"/neo4j_data_*.tar.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f 2>/dev/null || true
ls -t "$BACKUP_DIR"/neo4j_counts_*.txt 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f 2>/dev/null || true

# Step 4: Disk check
DISK=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK" -gt 85 ]; then
    send_telegram "⚠️ <b>VPS Disk Warning</b>
After backup: ${DISK}% used"
fi

echo "[$DATE] === Backup Complete ==="
