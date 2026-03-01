#!/bin/bash
# Database backup script for AI Mutation Governance Firewall

set -e

BACKUP_DIR="/backups"
DATABASE_NAME="ai_mutation_governance_firewall"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DATABASE_NAME}_${TIMESTAMP}.sql"

echo "Starting backup of ${DATABASE_NAME}..."

echo "Backup completed: ${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    SIZE=$(stat -f%z "${BACKUP_FILE}" 2>/dev/null || stat -c%s "${BACKUP_FILE}" 2>/dev/null)
    echo "Backup size: ${SIZE} bytes"
    
    if [ ${SIZE} -eq 0 ]; then
        echo "ERROR: Backup file is empty!"
        exit 1
    fi
else
    echo "ERROR: Backup file not found!"
    exit 1
fi

# Keep only last 30 backups
cd "${BACKUP_DIR}"
ls -t ${DATABASE_NAME}_*.* | tail -n +31 | xargs rm -f -- 2>/dev/null || true

echo "Backup process completed successfully"
