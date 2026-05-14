#!/bin/bash
# backup.sh — creates a timestamped zip backup of the project

PROJECT_NAME="library_system"
BACKUP_DIR="${HOME}/library_backups"   # saves to home directory
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S") # e.g. 2024-03-15_14-30-00
BACKUP_FILE="${BACKUP_DIR}/${PROJECT_NAME}_${TIMESTAMP}.zip"

# ── Create backup directory if it doesn't exist ───────────────
if [ ! -d "${BACKUP_DIR}" ]; then
    mkdir -p "${BACKUP_DIR}"
    echo "✓ Created backup directory: ${BACKUP_DIR}"
fi

# ── Create the zip — excluding venv and cache files ───────────
echo "Creating backup..."
zip -r "${BACKUP_FILE}" . \
    --exclude "venv/*" \
    --exclude "__pycache__/*" \
    --exclude "*.pyc" \
    --exclude ".git/*" \
    --quiet

echo "✓ Backup saved to: ${BACKUP_FILE}"

# ── Show backup size ───────────────────────────────────────────
BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
echo "✓ Backup size: ${BACKUP_SIZE}"

# ── Keep only last 5 backups — delete oldest ──────────────────
BACKUP_COUNT=$(ls "${BACKUP_DIR}" | wc -l)
if [ ${BACKUP_COUNT} -gt 5 ]; then
    OLDEST=$(ls -t "${BACKUP_DIR}" | tail -1)
    rm "${BACKUP_DIR}/${OLDEST}"
    echo "⚠ Removed oldest backup: ${OLDEST}"
fi