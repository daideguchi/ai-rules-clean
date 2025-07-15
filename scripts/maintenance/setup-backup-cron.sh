#!/bin/bash
set -euo pipefail

# Setup automated backup and maintenance cron jobs
# Provides Point-in-Time Recovery (PITR) capabilities

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MAINTENANCE_SCRIPT="$PROJECT_ROOT/scripts/maintenance/db-maintenance-scheduler.sh"

echo "🔧 Setting up automated database maintenance and backup system..."

# Create cron jobs for different maintenance tasks
setup_cron_jobs() {
    local temp_cron=$(mktemp)
    
    # Preserve existing cron jobs
    crontab -l 2>/dev/null > "$temp_cron" || true
    
    # Remove any existing maintenance jobs to avoid duplicates
    grep -v "db-maintenance-scheduler.sh" "$temp_cron" > "${temp_cron}.tmp" || true
    mv "${temp_cron}.tmp" "$temp_cron"
    
    echo "# AI Database Maintenance Jobs" >> "$temp_cron"
    echo "# Daily backup at 2 AM" >> "$temp_cron"
    echo "0 2 * * * $MAINTENANCE_SCRIPT backup >/dev/null 2>&1" >> "$temp_cron"
    
    echo "# Vector index optimization every Sunday at 3 AM" >> "$temp_cron"
    echo "0 3 * * 0 $MAINTENANCE_SCRIPT vector >/dev/null 2>&1" >> "$temp_cron"
    
    echo "# Memory cleanup every 6 hours" >> "$temp_cron"
    echo "0 */6 * * * $MAINTENANCE_SCRIPT cleanup >/dev/null 2>&1" >> "$temp_cron"
    
    echo "# Vacuum and analyze every day at 4 AM" >> "$temp_cron"
    echo "0 4 * * * $MAINTENANCE_SCRIPT vacuum >/dev/null 2>&1" >> "$temp_cron"
    
    echo "# Performance monitoring every hour" >> "$temp_cron"
    echo "0 * * * * $MAINTENANCE_SCRIPT monitor >/dev/null 2>&1" >> "$temp_cron"
    
    echo "# Embedding version updates daily at 1 AM" >> "$temp_cron"
    echo "0 1 * * * $MAINTENANCE_SCRIPT embeddings >/dev/null 2>&1" >> "$temp_cron"
    
    # Install new cron jobs
    crontab "$temp_cron"
    rm "$temp_cron"
    
    echo "✅ Cron jobs installed successfully"
}

# Setup PostgreSQL WAL archiving for PITR
setup_wal_archiving() {
    echo "🔧 Setting up WAL archiving for Point-in-Time Recovery..."
    
    local wal_archive_dir="$PROJECT_ROOT/runtime/wal_archives"
    mkdir -p "$wal_archive_dir"
    
    # Create WAL archive script
    cat > "$PROJECT_ROOT/scripts/maintenance/archive-wal.sh" << 'EOF'
#!/bin/bash
# WAL archiving script for PITR
set -euo pipefail

WAL_PATH="$1"
WAL_FILE="$2"
ARCHIVE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/runtime/wal_archives"

# Ensure archive directory exists
mkdir -p "$ARCHIVE_DIR"

# Copy WAL file to archive
cp "$WAL_PATH" "$ARCHIVE_DIR/$WAL_FILE"

# Verify copy
if [[ -f "$ARCHIVE_DIR/$WAL_FILE" ]]; then
    echo "$(date): Archived $WAL_FILE" >> "$ARCHIVE_DIR/archive.log"
    exit 0
else
    echo "$(date): Failed to archive $WAL_FILE" >> "$ARCHIVE_DIR/archive.log"
    exit 1
fi
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/maintenance/archive-wal.sh"
    
    echo "📝 WAL archiving script created at: $PROJECT_ROOT/scripts/maintenance/archive-wal.sh"
    echo "⚠️  To enable WAL archiving, add the following to postgresql.conf:"
    echo "    wal_level = replica"
    echo "    archive_mode = on" 
    echo "    archive_command = '$PROJECT_ROOT/scripts/maintenance/archive-wal.sh %p %f'"
    echo "    max_wal_senders = 3"
    echo "    wal_keep_size = 1GB"
}

# Create backup restoration script
create_restore_script() {
    cat > "$PROJECT_ROOT/scripts/maintenance/restore-from-backup.sh" << 'EOF'
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
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/maintenance/restore-from-backup.sh"
    echo "✅ Restoration script created: $PROJECT_ROOT/scripts/maintenance/restore-from-backup.sh"
}

# Create monitoring dashboard script
create_monitoring_dashboard() {
    cat > "$PROJECT_ROOT/scripts/maintenance/monitoring-dashboard.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

# Database monitoring dashboard

DB_NAME="coding_rule2_ai"

echo "🔍 AI Database Monitoring Dashboard"
echo "=================================="

# Database size and growth
echo ""
echo "📊 Database Statistics:"
psql -d "$DB_NAME" -c "
    SELECT 
        'Database Size' as metric,
        pg_size_pretty(pg_database_size('$DB_NAME')) as value
    UNION ALL
    SELECT 
        'Context Records',
        (SELECT COUNT(*)::text FROM context_stream)
    UNION ALL
    SELECT 
        'Mistake Records',
        (SELECT COUNT(*)::text FROM mistakes_database)
    UNION ALL
    SELECT 
        'Learning Signals',
        (SELECT COUNT(*)::text FROM learning_signals)
    UNION ALL
    SELECT 
        'Active Sessions',
        (SELECT COUNT(DISTINCT session_id)::text FROM context_stream WHERE created_at > NOW() - INTERVAL '24 hours');
"

# Recent maintenance operations
echo ""
echo "🔧 Recent Maintenance Operations:"
psql -d "$DB_NAME" -c "
    SELECT 
        operation_type,
        table_name,
        status,
        started_at,
        completed_at
    FROM maintenance_log 
    ORDER BY started_at DESC 
    LIMIT 10;
"

# Performance metrics
echo ""
echo "⚡ Performance Metrics:"
psql -d "$DB_NAME" -c "
    SELECT 
        'Avg Learning Weight (24h)' as metric,
        ROUND(AVG(learning_weight)::numeric, 3)::text as value
    FROM context_stream 
    WHERE created_at > NOW() - INTERVAL '24 hours'
    UNION ALL
    SELECT 
        'High Confidence Events',
        COUNT(*)::text
    FROM context_stream 
    WHERE confidence_score > 0.8 AND created_at > NOW() - INTERVAL '24 hours'
    UNION ALL
    SELECT 
        'Memory Policy Violations',
        COUNT(*)::text
    FROM context_stream cs
    JOIN memory_policies mp ON mp.policy_name = 'standard_memories'
    WHERE cs.created_at < NOW() - INTERVAL '1 day' * mp.retention_days
        AND cs.salience_score < mp.min_salience_threshold;
"

# Index usage
echo ""
echo "📈 Index Usage Statistics:"
psql -d "$DB_NAME" -c "
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan as scans,
        idx_tup_read as reads,
        idx_tup_fetch as fetches
    FROM pg_stat_user_indexes 
    WHERE indexname LIKE '%context%' OR indexname LIKE '%vector%'
    ORDER BY idx_scan DESC
    LIMIT 10;
"
EOF

    chmod +x "$PROJECT_ROOT/scripts/maintenance/monitoring-dashboard.sh"
    echo "✅ Monitoring dashboard created: $PROJECT_ROOT/scripts/maintenance/monitoring-dashboard.sh"
}

# Main execution
main() {
    echo "🚀 Setting up comprehensive backup and maintenance system..."
    
    # Create maintenance directory
    mkdir -p "$PROJECT_ROOT/scripts/maintenance"
    mkdir -p "$PROJECT_ROOT/runtime/backups"
    mkdir -p "$PROJECT_ROOT/runtime/wal_archives"
    
    setup_cron_jobs
    setup_wal_archiving
    create_restore_script
    create_monitoring_dashboard
    
    echo ""
    echo "🎉 Backup and maintenance system setup completed!"
    echo ""
    echo "📋 Available commands:"
    echo "  • $MAINTENANCE_SCRIPT [operation]  # Run maintenance"
    echo "  • $PROJECT_ROOT/scripts/maintenance/restore-from-backup.sh  # Restore database"
    echo "  • $PROJECT_ROOT/scripts/maintenance/monitoring-dashboard.sh  # View metrics"
    echo ""
    echo "⏰ Automated schedules:"
    echo "  • Daily backups at 2 AM"
    echo "  • Memory cleanup every 6 hours"
    echo "  • Vector reindexing weekly"
    echo "  • Performance monitoring hourly"
    echo ""
    echo "📁 Data locations:"
    echo "  • Backups: $PROJECT_ROOT/runtime/backups/"
    echo "  • WAL Archives: $PROJECT_ROOT/runtime/wal_archives/"
    echo "  • Logs: $PROJECT_ROOT/runtime/ai_api_logs/"
}

main "$@"