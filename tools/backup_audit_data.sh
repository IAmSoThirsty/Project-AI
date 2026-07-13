#!/bin/sh
set -eu

# Backup audit data from PVC-mounted /data to backup PVC-mounted /backup.
# Usage: backup_audit_data.sh [DATA_DIR] [BACKUP_DIR]
# Environment:
#   BACKUP_RETENTION_DAYS (default 30) — delete backups older than N days

DATA_DIR="${1:-/data}"
BACKUP_DIR="${2:-/backup}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/audit-${TIMESTAMP}.tar.gz"

echo "Starting backup at $(date -u)"
echo "  data: ${DATA_DIR}"
echo "  backup: ${BACKUP_FILE}"
echo "  retention: ${RETENTION_DAYS} days"

if [ ! -d "${DATA_DIR}" ]; then
  echo "ERROR: data directory ${DATA_DIR} does not exist" >&2
  exit 1
fi

if [ ! -d "${BACKUP_DIR}" ]; then
  echo "ERROR: backup directory ${BACKUP_DIR} does not exist" >&2
  exit 1
fi

# Create the compressed archive
tar czf "${BACKUP_FILE}" -C "${DATA_DIR}" .

echo "Backup created: ${BACKUP_FILE} ($(du -h "${BACKUP_FILE}" | cut -f1))"

# Prune old backups
echo "Pruning backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name 'audit-*.tar.gz' -mtime +${RETENTION_DAYS} -print -delete || true

# List remaining backups
echo "Remaining backups:"
ls -lh "${BACKUP_DIR}"/audit-*.tar.gz 2>/dev/null || echo "  (none)"

echo "Backup completed at $(date -u)"
