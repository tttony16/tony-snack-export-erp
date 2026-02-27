#!/bin/bash
# 数据库每日自动备份脚本
# cron: 0 2 * * * /home/dev/workspace/snack-export-erp/scripts/backup-db.sh

set -euo pipefail

BACKUP_DIR="/home/dev/docker-data/snack-erp/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/snack_erp_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

docker exec snack-erp-postgres pg_dump -U erp_user snack_erp | gzip > "${BACKUP_FILE}"

echo "Backup created: ${BACKUP_FILE}"

# 保留最近 30 天的备份
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +30 -delete

echo "Old backups cleaned up."
