#!/bin/bash
set -euo pipefail

# PostgreSQL Database Maintenance Scheduler
# Handles reindexing, vacuuming, memory cleanup, and backup operations

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DB_NAME="coding_rule2_ai"
DB_USER="dd"
LOG_DIR="$PROJECT_ROOT/runtime/ai_api_logs"
BACKUP_DIR="$PROJECT_ROOT/runtime/backups"

# Create required directories
mkdir -p "$LOG_DIR" "$BACKUP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/maintenance_$(date +%Y%m%d).log"
}

log_operation() {
    local operation="$1"
    local table_name="$2"
    local status="$3"
    local details="${4:-{}}"
    
    # Escape single quotes in JSON for safe SQL insertion
    local escaped_details=$(echo "$details" | sed "s/'/''/g")
    
    psql -d "$DB_NAME" -c "
        INSERT INTO maintenance_log 
        (operation_type, table_name, status, details, completed_at) 
        VALUES ('$operation', '$table_name', '$status', '$escaped_details'::jsonb, NOW())
    " 2>/dev/null || log "⚠️ Failed to log operation: $operation"
}

# Vector index optimization
optimize_vector_indexes() {
    log "🔧 Starting vector index optimization..."
    
    # Check index statistics
    local stats=$(psql -d "$DB_NAME" -t -c "
        SELECT 
            schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
        FROM pg_stat_user_indexes 
        WHERE indexname LIKE '%vector%'
        ORDER BY idx_scan DESC;
    ")
    
    log "📊 Current vector index usage: $stats"
    
    # Reindex vector indexes if they show performance degradation
    psql -d "$DB_NAME" << 'EOF'
        -- Reindex vector indexes concurrently
        REINDEX INDEX CONCURRENTLY idx_context_stream_vector_cosine;
        REINDEX INDEX CONCURRENTLY idx_context_stream_vector_l2;
        REINDEX INDEX CONCURRENTLY idx_context_stream_vector_recall;
EOF
    
    log_operation "reindex" "context_stream" "completed" '{"indexes": ["vector_cosine", "vector_l2", "vector_recall"]}'
    log "✅ Vector index optimization completed"
}

# Memory inheritance and accumulation (NO DELETION)
enhance_memory_inheritance() {
    log "🧠 Enhancing memory inheritance and accumulation..."
    
    # Mark high-value memories for enhanced cross-referencing
    psql -d "$DB_NAME" << 'EOF'
        -- Enhance cross-references for high-value memories
        UPDATE context_stream 
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'), 
            '{inheritance_enhanced}', 
            'true'
        )
        WHERE 
            salience_score > 0.7
            AND metadata->>'inheritance_enhanced' IS NULL;
            
        -- Build learning connections between related contexts
        UPDATE context_stream cs1
        SET cross_references = array_append(
            COALESCE(cs1.cross_references, '{}'), 
            cs2.id
        )
        FROM context_stream cs2
        WHERE 
            cs1.id != cs2.id
            AND cs1.salience_score > 0.6
            AND cs2.salience_score > 0.6
            AND array_length(cs1.cross_references, 1) < 5;
EOF
    
    log_operation "inheritance" "context_stream" "completed" '{"action": "enhanced_cross_references"}'
    log "✅ Memory inheritance enhancement completed"
}

# Database vacuum and analyze
vacuum_analyze() {
    log "🔄 Starting vacuum and analyze operations..."
    
    # Vacuum main tables
    psql -d "$DB_NAME" << 'EOF'
        VACUUM (ANALYZE, VERBOSE) context_stream;
        VACUUM (ANALYZE, VERBOSE) mistakes_database;
        VACUUM (ANALYZE, VERBOSE) document_intelligence;
        VACUUM (ANALYZE, VERBOSE) session_memory;
        VACUUM (ANALYZE, VERBOSE) learning_signals;
EOF
    
    log_operation "vacuum" "all_tables" "completed" '{"operation": "vacuum_analyze"}'
    log "✅ Vacuum and analyze completed"
}

# Backup operations
perform_backup() {
    log "💾 Starting database backup..."
    
    local backup_file="$BACKUP_DIR/coding_rule2_ai_$(date +%Y%m%d_%H%M%S).sql"
    
    # Create compressed backup
    pg_dump "$DB_NAME" | gzip > "${backup_file}.gz"
    
    # Verify backup
    if [[ -f "${backup_file}.gz" ]]; then
        local backup_size=$(du -h "${backup_file}.gz" | cut -f1)
        log "✅ Backup created: ${backup_file}.gz ($backup_size)"
        
        # Clean old backups (keep last 7 days)
        find "$BACKUP_DIR" -name "coding_rule2_ai_*.sql.gz" -mtime +7 -delete
        
        log_operation "backup" "database" "completed" "{\"file\": \"${backup_file}.gz\", \"size\": \"$backup_size\"}"
    else
        log "❌ Backup failed"
        log_operation "backup" "database" "failed" '{"error": "backup_file_not_created"}'
        return 1
    fi
}

# Performance monitoring
monitor_performance() {
    log "📈 Collecting performance metrics..."
    
    # Get database size and growth
    local db_stats=$(psql -d "$DB_NAME" -t -c "
        SELECT 
            pg_size_pretty(pg_database_size('$DB_NAME')) as db_size,
            (SELECT COUNT(*) FROM context_stream) as context_records,
            (SELECT COUNT(*) FROM mistakes_database) as mistake_records,
            (SELECT AVG(learning_weight) FROM context_stream WHERE created_at > NOW() - INTERVAL '24 hours') as avg_learning_weight
    ")
    
    log "📊 Database stats: $db_stats"
    
    # Check for slow queries
    local slow_queries=$(psql -d "$DB_NAME" -t -c "
        SELECT query, calls, mean_exec_time 
        FROM pg_stat_statements 
        WHERE mean_exec_time > 1000 
        ORDER BY mean_exec_time DESC 
        LIMIT 5;
    " 2>/dev/null || echo "pg_stat_statements not available")
    
    if [[ "$slow_queries" != "pg_stat_statements not available" ]]; then
        log "⚠️ Slow queries detected: $slow_queries"
    fi
    
    log_operation "monitor" "database" "completed" "{\"stats\": \"$db_stats\"}"
}

# Update embedding model versions
update_embedding_versions() {
    log "🔄 Checking for embedding model updates..."
    
    # Check if any embeddings lack version info
    local unversioned=$(psql -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM context_stream 
        WHERE embedding_model IS NULL OR embedding_version IS NULL;
    ")
    
    if [[ "$unversioned" -gt 0 ]]; then
        log "🔧 Updating $unversioned records with embedding version info..."
        
        psql -d "$DB_NAME" << 'EOF'
            UPDATE context_stream 
            SET 
                embedding_model = 'text-embedding-ada-002',
                embedding_version = 'v1',
                embedding_hash = md5(vector_embedding::text)
            WHERE embedding_model IS NULL OR embedding_version IS NULL;
EOF
        
        log_operation "update" "context_stream" "completed" "{\"updated_records\": $unversioned}"
    fi
    
    log "✅ Embedding version update completed"
}

# Main execution
main() {
    local operation="${1:-all}"
    
    log "🚀 Starting database maintenance: $operation"
    
    case "$operation" in
        "vector")
            optimize_vector_indexes
            ;;
        "inheritance")
            enhance_memory_inheritance
            ;;
        "vacuum")
            vacuum_analyze
            ;;
        "backup")
            perform_backup
            ;;
        "monitor")
            monitor_performance
            ;;
        "embeddings")
            update_embedding_versions
            ;;
        "all")
            update_embedding_versions
            optimize_vector_indexes
            enhance_memory_inheritance
            vacuum_analyze
            monitor_performance
            perform_backup
            ;;
        *)
            echo "Usage: $0 [vector|inheritance|vacuum|backup|monitor|embeddings|all]"
            exit 1
            ;;
    esac
    
    log "🎉 Database maintenance completed: $operation"
}

main "$@"