#!/bin/bash

# Database backup script
# Usage: ./scripts/backup-db.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/database_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "💾 Starting database backup..."

# Load environment variables
if [ -f "$PROJECT_DIR/.env.production" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env.production" | xargs)
else
    echo "⚠️  .env.production not found, using default values"
    DB_NAME=${DB_NAME:-asmi_db}
fi

# Check if container is running
if ! docker ps | grep -q dashboard-postgres; then
    echo "❌ PostgreSQL container is not running!"
    exit 1
fi

# Create backup
echo "📦 Creating backup: $BACKUP_FILE"
docker exec dashboard-postgres-prod pg_dump -U postgres "$DB_NAME" > "$BACKUP_FILE"

# Compress backup
echo "🗜️  Compressing backup..."
gzip "$BACKUP_FILE"

COMPRESSED_FILE="$BACKUP_FILE.gz"
BACKUP_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)

echo "✅ Backup completed successfully!"
echo "📁 File: $COMPRESSED_FILE"
echo "📊 Size: $BACKUP_SIZE"

# Keep only last 7 backups
echo "🧹 Cleaning old backups (keeping last 7)..."
cd "$BACKUP_DIR"
ls -t database_backup_*.sql.gz | tail -n +8 | xargs -r rm

echo "📋 Available backups:"
ls -lh database_backup_*.sql.gz | tail -7

echo "✅ Backup process completed!"
