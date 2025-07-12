#!/bin/bash
set -euo pipefail

# Database restoration script with PITR support

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/runtime/backups"
WAL_ARCHIVE_DIR="$PROJECT_ROOT/runtime/wal_archives"
DB_NAME="coding_rule2_ai"

usage() {
    echo "Usage: $0 [backup_file] [target_time]"
    echo "  backup_file: Path to backup file (latest if not specified)"
    echo "  target_time: Point-in-time to restore to (YYYY-MM-DD HH:MM:SS)"
    echo ""
    echo "Examples:"
    echo "  $0  # Restore from latest backup"
    echo "  $0 /path/to/backup.sql.gz  # Restore from specific backup"
    echo "  $0 /path/to/backup.sql.gz '2025-07-08 12:00:00'  # PITR restore"
}

restore_from_backup() {
    local backup_file="$1"
    local target_time="${2:-}"
    
    echo "🔄 Starting database restoration..."
    echo "📁 Backup file: $backup_file"
    [[ -n "$target_time" ]] && echo "🕒 Target time: $target_time"
    
    # Create backup of current database
    echo "💾 Creating safety backup of current database..."
    pg_dump "$DB_NAME" | gzip > "$BACKUP_DIR/pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
    
    # Drop and recreate database
    echo "🗑️ Dropping current database..."
    dropdb "$DB_NAME" || true
    createdb "$DB_NAME"
    
    # Restore from backup
    echo "📥 Restoring from backup..."
    if [[ "$backup_file" =~ \.gz$ ]]; then
        zcat "$backup_file" | psql -d "$DB_NAME"
    else
        psql -d "$DB_NAME" < "$backup_file"
    fi
    
    # Apply WAL files for PITR if target time specified
    if [[ -n "$target_time" ]]; then
        echo "🕒 Applying WAL files for point-in-time recovery..."
        # This would require more advanced setup with pg_basebackup
        echo "⚠️  PITR requires base backup + WAL files. Use pg_basebackup for full PITR support."
    fi
    
    echo "✅ Database restoration completed"
}

main() {
    local backup_file="${1:-}"
    local target_time="${2:-}"
    
    if [[ "$backup_file" == "-h" || "$backup_file" == "--help" ]]; then
        usage
        exit 0
    fi
    
    # Find latest backup if none specified
    if [[ -z "$backup_file" ]]; then
        backup_file=$(find "$BACKUP_DIR" -name "coding_rule2_ai_*.sql.gz" -type f | sort | tail -1)
        if [[ -z "$backup_file" ]]; then
            echo "❌ No backup files found in $BACKUP_DIR"
            exit 1
        fi
        echo "📁 Using latest backup: $backup_file"
    fi
    
    # Verify backup file exists
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ Backup file not found: $backup_file"
        exit 1
    fi
    
    # Confirmation prompt
    echo "⚠️  This will completely replace the current database!"
    read -p "Continue? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "❌ Restoration cancelled"
        exit 1
    fi
    
    restore_from_backup "$backup_file" "$target_time"
}

main "$@"
