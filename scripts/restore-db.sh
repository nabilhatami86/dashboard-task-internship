#!/bin/bash

# Database restore script
# Usage: ./scripts/restore-db.sh [backup-file]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"

if [ -z "$1" ]; then
    echo "📋 Available backups:"
    ls -lh "$BACKUP_DIR"/database_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "Usage: $0 <backup-file>"
    echo "Example: $0 backups/database_backup_20240101_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will restore the database from backup!"
echo "📁 Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

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

echo "💾 Starting database restore..."

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "🗜️  Decompressing backup..."
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    RESTORE_FILE="$TEMP_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Create a backup of current database before restoring
CURRENT_BACKUP="$BACKUP_DIR/pre_restore_backup_$(date +"%Y%m%d_%H%M%S").sql"
echo "📦 Creating backup of current database..."
docker exec dashboard-postgres-prod pg_dump -U postgres "$DB_NAME" > "$CURRENT_BACKUP"
gzip "$CURRENT_BACKUP"
echo "✅ Current database backed up to: $CURRENT_BACKUP.gz"

# Restore database
echo "♻️  Restoring database from: $RESTORE_FILE"
cat "$RESTORE_FILE" | docker exec -i dashboard-postgres-prod psql -U postgres "$DB_NAME"

# Clean up temp file
if [[ "$BACKUP_FILE" == *.gz ]]; then
    rm "$TEMP_FILE"
fi

echo "✅ Database restore completed successfully!"
echo ""
echo "🔄 Restart application to apply changes:"
echo "   docker-compose -f docker-compose.prod.yml restart backend"
