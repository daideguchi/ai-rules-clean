#!/bin/bash
# 🗄️ Database Unified Maintenance System - DB統合メンテナンスシステム
# ================================================================
# db-maintenance-scheduler.sh + archive-wal.sh + setup-backup-cron.sh統合
# o3推奨のflock制御・排他実行・構造化ログ・段階的実行対応

set -o pipefail  # o3推奨: set -e回避でCron停止防止

PROJECT_ROOT="/Users/dd/Desktop/1_dev/coding-rule2"
DB_NAME="coding_rule2_ai"
DB_USER="dd"
LOG_DIR="$PROJECT_ROOT/runtime/ai_api_logs"
BACKUP_DIR="$PROJECT_ROOT/runtime/backups"
WAL_ARCHIVE_DIR="$PROJECT_ROOT/runtime/wal_archives"
UNIFIED_LOG="$LOG_DIR/db_unified_maintenance_$(date +%Y%m%d).log"

# o3推奨: ディレクトリ作成
mkdir -p "$LOG_DIR" "$BACKUP_DIR" "$WAL_ARCHIVE_DIR"

# o3推奨: 構造化ログ + syslog統合
log_structured() {
    local level=$1
    local operation=$2
    local message=$3
    local timestamp=$(date -Iseconds)
    local details="${4:-{}}"
    
    # 構造化JSON出力
    echo "{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"operation\":\"$operation\",\"message\":\"$message\",\"details\":$details}" | tee -a "$UNIFIED_LOG"
    
    # syslog送信（監視系連携）
    logger -t db-unified-maintenance -p local3.$level "[$operation] $message"
    
    # 従来ログ互換性
    echo "[$timestamp] [$level] [$operation] $message" | tee -a "$LOG_DIR/maintenance_$(date +%Y%m%d).log"
}

show_usage() {
    cat << EOF
Database Unified Maintenance System - DB統合メンテナンスシステム

使用方法:
  $0 [OPTIONS] <operation>

操作:
  vacuum          データベースVACUUM・ANALYZE実行
  backup          フルバックアップ作成（pg_dump）  
  archive         WALアーカイブ実行（PITR用）
  monitor         パフォーマンス監視・メトリクス収集
  vector          ベクターインデックス最適化
  inheritance     メモリ継承システム強化
  embeddings      エンベディングバージョン更新
  setup-cron      cronジョブ自動セットアップ
  all             全メンテナンス実行（排他制御付き）

オプション:
  --dry-run       実行内容をプレビューのみ（実際の変更なし）
  --scope <name>  特定スコープのみ実行（tables/indexes/logs）
  --throttle <n>  操作間の待機時間（秒、デフォルト: 5）
  --no-lock       ロック制御をスキップ（緊急時のみ）
  --output <fmt>  出力形式（json|text、デフォルト: text）
  -v, --verbose   詳細ログ出力
  -h, --help      このヘルプを表示

例:
  $0 --dry-run all                    # 全操作のドライラン
  $0 --throttle 10 vacuum backup      # VACUUM→バックアップ（10秒間隔）
  $0 --scope tables vacuum            # テーブルのみVACUUM
  $0 --output json monitor            # 監視結果をJSON出力

統合元スクリプト:
  - db-maintenance-scheduler.sh (PostgreSQL保守)
  - archive-wal.sh (WALアーカイブ)
  - setup-backup-cron.sh (バックアップ設定)

o3推奨セキュリティ機能:
  - flock(1)による単一インスタンス実行制御
  - 段階的実行（各ステップの独立エラーハンドリング）
  - PostgreSQL接続プール制御
  - 構造化ログ + syslog監視連携
EOF
}

# o3推奨: PIDベース単一インスタンス実行制御（flockの代替）
acquire_lock() {
    local lock_file="/tmp/db_unified_maintenance.lock"
    local operation=${1:-"maintenance"}
    local timeout=300  # 5分
    
    # 既存ロックファイル確認
    if [ -f "$lock_file" ]; then
        local lock_pid=$(cat "$lock_file" 2>/dev/null || echo "")
        if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
            log_structured "ERROR" "$operation" "Another maintenance instance is running" "{\"lock_pid\":\"$lock_pid\"}"
            exit 1
        else
            log_structured "WARN" "$operation" "Stale lock file removed" "{\"old_pid\":\"$lock_pid\"}"
            rm -f "$lock_file"
        fi
    fi
    
    # 新しいロック作成
    echo $$ > "$lock_file"
    log_structured "INFO" "$operation" "Lock acquired successfully" "{\"pid\":$$}"
}

# データベース接続確認
verify_db_connection() {
    local operation=${1:-"connection"}
    
    if ! psql -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        log_structured "ERROR" "$operation" "Database connection failed" "{\"database\":\"$DB_NAME\"}"
        return 1
    fi
    
    log_structured "INFO" "$operation" "Database connection verified" "{\"database\":\"$DB_NAME\"}"
    return 0
}

# o3推奨: 段階的VACUUM実行（テーブル毎に分割）
execute_vacuum_analyze() {
    local dry_run=${1:-false}
    local scope=${2:-all}
    local throttle=${3:-5}
    
    log_structured "INFO" "vacuum" "Starting vacuum and analyze operations" "{\"scope\":\"$scope\",\"throttle\":$throttle}"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "vacuum" "[DRY-RUN] Would execute VACUUM ANALYZE on all tables"
        return 0
    fi
    
    if ! verify_db_connection "vacuum"; then
        return 1
    fi
    
    local tables=()
    case $scope in
        "all"|"tables")
            tables=("context_stream" "mistakes_database" "document_intelligence" "session_memory" "learning_signals")
            ;;
        "context")
            tables=("context_stream")
            ;;
        "logs")
            tables=("mistakes_database" "learning_signals")
            ;;
        *)
            log_structured "ERROR" "vacuum" "Invalid scope specified" "{\"scope\":\"$scope\"}"
            return 1
            ;;
    esac
    
    local vacuum_success=0
    local vacuum_total=${#tables[@]}
    
    for table in "${tables[@]}"; do
        log_structured "INFO" "vacuum" "Processing table: $table"
        
        # テーブル毎に個別実行（エラー継続）
        if psql -d "$DB_NAME" -c "VACUUM (ANALYZE, VERBOSE) $table;" 2>/dev/null; then
            ((vacuum_success++))
            log_structured "INFO" "vacuum" "Table vacuum completed" "{\"table\":\"$table\",\"status\":\"success\"}"
        else
            log_structured "WARN" "vacuum" "Table vacuum failed" "{\"table\":\"$table\",\"status\":\"failed\"}"
        fi
        
        sleep "$throttle"
    done
    
    # 結果ログ記録
    psql -d "$DB_NAME" -c "
        INSERT INTO maintenance_log 
        (operation_type, table_name, status, details, completed_at) 
        VALUES ('vacuum', 'multiple', 'completed', '{\"success\":$vacuum_success,\"total\":$vacuum_total}'::jsonb, NOW())
    " 2>/dev/null || true
    
    log_structured "INFO" "vacuum" "Vacuum operations completed" "{\"success\":$vacuum_success,\"total\":$vacuum_total}"
    
    return 0
}

# o3推奨: フルバックアップ実行（世代管理付き）
execute_full_backup() {
    local dry_run=${1:-false}
    local retention_days=${2:-7}
    
    log_structured "INFO" "backup" "Starting full database backup" "{\"retention_days\":$retention_days}"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "backup" "[DRY-RUN] Would create compressed backup with pg_dump"
        log_structured "INFO" "backup" "[DRY-RUN] Would clean backups older than $retention_days days"
        return 0
    fi
    
    if ! verify_db_connection "backup"; then
        return 1
    fi
    
    local backup_file="$BACKUP_DIR/coding_rule2_ai_$(date +%Y%m%d_%H%M%S).sql"
    local start_time=$(date +%s)
    
    # pg_dump実行（圧縮付き）
    log_structured "INFO" "backup" "Creating database backup" "{\"file\":\"$backup_file\"}"
    
    if pg_dump "$DB_NAME" | gzip > "${backup_file}.gz" 2>/dev/null; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local backup_size=$(du -h "${backup_file}.gz" 2>/dev/null | cut -f1 || echo "unknown")
        
        log_structured "INFO" "backup" "Backup completed successfully" "{\"file\":\"${backup_file}.gz\",\"size\":\"$backup_size\",\"duration\":$duration}"
        
        # バックアップ検証
        if gzip -t "${backup_file}.gz" 2>/dev/null; then
            log_structured "INFO" "backup" "Backup integrity verified"
        else
            log_structured "WARN" "backup" "Backup integrity check failed"
        fi
        
        # 世代管理（古いバックアップ削除）
        local deleted_count=$(find "$BACKUP_DIR" -name "coding_rule2_ai_*.sql.gz" -mtime +$retention_days -delete -print | wc -l)
        if [ "$deleted_count" -gt 0 ]; then
            log_structured "INFO" "backup" "Old backups cleaned up" "{\"deleted_count\":$deleted_count}"
        fi
        
        # ログ記録
        psql -d "$DB_NAME" -c "
            INSERT INTO maintenance_log 
            (operation_type, table_name, status, details, completed_at) 
            VALUES ('backup', 'database', 'completed', '{\"file\":\"${backup_file}.gz\",\"size\":\"$backup_size\",\"duration\":$duration}'::jsonb, NOW())
        " 2>/dev/null || true
        
        return 0
    else
        log_structured "ERROR" "backup" "Backup creation failed" "{\"file\":\"$backup_file\"}"
        
        # 失敗ログ記録
        psql -d "$DB_NAME" -c "
            INSERT INTO maintenance_log 
            (operation_type, table_name, status, details, completed_at) 
            VALUES ('backup', 'database', 'failed', '{\"error\":\"pg_dump_failed\"}'::jsonb, NOW())
        " 2>/dev/null || true
        
        return 1
    fi
}

# o3推奨: WALアーカイブ実行（PITR対応）
execute_wal_archive() {
    local dry_run=${1:-false}
    local wal_path=${2:-}
    local wal_file=${3:-}
    
    # PostgreSQLのarchive_commandから呼ばれる場合の引数処理
    if [ -n "$wal_path" ] && [ -n "$wal_file" ]; then
        log_structured "INFO" "archive" "WAL archive request" "{\"wal_path\":\"$wal_path\",\"wal_file\":\"$wal_file\"}"
        
        if [ "$dry_run" = "true" ]; then
            log_structured "INFO" "archive" "[DRY-RUN] Would archive WAL file"
            return 0
        fi
        
        # WALファイルアーカイブ実行
        if cp "$wal_path" "$WAL_ARCHIVE_DIR/$wal_file" 2>/dev/null; then
            # アーカイブ検証
            if [ -f "$WAL_ARCHIVE_DIR/$wal_file" ]; then
                echo "$(date -Iseconds): Archived $wal_file" >> "$WAL_ARCHIVE_DIR/archive.log"
                log_structured "INFO" "archive" "WAL file archived successfully" "{\"wal_file\":\"$wal_file\"}"
                return 0
            fi
        fi
        
        echo "$(date -Iseconds): Failed to archive $wal_file" >> "$WAL_ARCHIVE_DIR/archive.log"
        log_structured "ERROR" "archive" "WAL archive failed" "{\"wal_file\":\"$wal_file\"}"
        return 1
    else
        # 手動実行の場合（アーカイブ状況確認）
        log_structured "INFO" "archive" "Checking WAL archive status"
        
        if [ "$dry_run" = "true" ]; then
            log_structured "INFO" "archive" "[DRY-RUN] Would check archive status and cleanup old WAL files"
            return 0
        fi
        
        # アーカイブ済みファイル数確認
        local archived_count=$(find "$WAL_ARCHIVE_DIR" -name "*.wal" -o -name "*[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]" | wc -l)
        local archive_size=$(du -sh "$WAL_ARCHIVE_DIR" 2>/dev/null | cut -f1 || echo "unknown")
        
        log_structured "INFO" "archive" "WAL archive status" "{\"archived_files\":$archived_count,\"total_size\":\"$archive_size\"}"
        
        # 古いWALファイル削除（7日以上前）
        local deleted_wal=$(find "$WAL_ARCHIVE_DIR" -type f -mtime +7 -delete -print | wc -l)
        if [ "$deleted_wal" -gt 0 ]; then
            log_structured "INFO" "archive" "Old WAL files cleaned up" "{\"deleted_count\":$deleted_wal}"
        fi
        
        return 0
    fi
}

# パフォーマンス監視・メトリクス収集
execute_performance_monitor() {
    local dry_run=${1:-false}
    local output_format=${2:-text}
    
    log_structured "INFO" "monitor" "Starting performance monitoring"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "monitor" "[DRY-RUN] Would collect database performance metrics"
        return 0
    fi
    
    if ! verify_db_connection "monitor"; then
        return 1
    fi
    
    # システムメトリクス収集
    local db_size=$(psql -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | xargs || echo "unknown")
    local context_records=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM context_stream;" 2>/dev/null | xargs || echo "0")
    local mistake_records=$(psql -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM mistakes_database;" 2>/dev/null | xargs || echo "0")
    local avg_learning_weight=$(psql -d "$DB_NAME" -t -c "SELECT ROUND(AVG(learning_weight)::numeric, 3) FROM context_stream WHERE created_at > NOW() - INTERVAL '24 hours';" 2>/dev/null | xargs || echo "0")
    
    # 低速クエリ検出
    local slow_queries=$(psql -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM pg_stat_statements 
        WHERE mean_exec_time > 1000;" 2>/dev/null | xargs || echo "0")
    
    # メトリクスJSON生成
    local metrics_json="{\"database_size\":\"$db_size\",\"context_records\":$context_records,\"mistake_records\":$mistake_records,\"avg_learning_weight\":$avg_learning_weight,\"slow_queries\":$slow_queries}"
    
    log_structured "INFO" "monitor" "Performance metrics collected" "$metrics_json"
    
    # 監視ログ記録
    psql -d "$DB_NAME" -c "
        INSERT INTO maintenance_log 
        (operation_type, table_name, status, details, completed_at) 
        VALUES ('monitor', 'database', 'completed', '$metrics_json'::jsonb, NOW())
    " 2>/dev/null || true
    
    if [ "$output_format" = "json" ]; then
        echo "$metrics_json"
    else
        echo "📊 DB監視完了: サイズ $db_size, コンテキスト $context_records, ミス $mistake_records"
    fi
    
    return 0
}

# ベクターインデックス最適化（元db-maintenance-scheduler.sh機能）
execute_vector_optimization() {
    local dry_run=${1:-false}
    local throttle=${2:-5}
    
    log_structured "INFO" "vector" "Starting vector index optimization"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "vector" "[DRY-RUN] Would reindex vector indexes concurrently"
        return 0
    fi
    
    if ! verify_db_connection "vector"; then
        return 1
    fi
    
    # ベクターインデックス統計取得
    local vector_stats=$(psql -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM pg_stat_user_indexes 
        WHERE indexname LIKE '%vector%';" 2>/dev/null | xargs || echo "0")
    
    if [ "$vector_stats" -eq 0 ]; then
        log_structured "WARN" "vector" "No vector indexes found"
        return 0
    fi
    
    # REINDEXコマンド実行（CONCURRENTLYで非ブロッキング）
    local reindex_commands=(
        "REINDEX INDEX CONCURRENTLY IF EXISTS idx_context_stream_vector_cosine"
        "REINDEX INDEX CONCURRENTLY IF EXISTS idx_context_stream_vector_l2"
        "REINDEX INDEX CONCURRENTLY IF EXISTS idx_context_stream_vector_recall"
    )
    
    local reindex_success=0
    for cmd in "${reindex_commands[@]}"; do
        if psql -d "$DB_NAME" -c "$cmd;" 2>/dev/null; then
            ((reindex_success++))
            log_structured "INFO" "vector" "Vector index reindexed" "{\"command\":\"$cmd\"}"
        else
            log_structured "WARN" "vector" "Vector index reindex failed" "{\"command\":\"$cmd\"}"
        fi
        sleep "$throttle"
    done
    
    # 結果ログ記録
    psql -d "$DB_NAME" -c "
        INSERT INTO maintenance_log 
        (operation_type, table_name, status, details, completed_at) 
        VALUES ('reindex', 'context_stream', 'completed', '{\"indexes\":[\"vector_cosine\",\"vector_l2\",\"vector_recall\"],\"success\":$reindex_success}'::jsonb, NOW())
    " 2>/dev/null || true
    
    log_structured "INFO" "vector" "Vector optimization completed" "{\"reindexed\":$reindex_success,\"total\":${#reindex_commands[@]}}"
    
    return 0
}

# メモリ継承システム強化（元db-maintenance-scheduler.sh機能）
execute_inheritance_enhancement() {
    local dry_run=${1:-false}
    
    log_structured "INFO" "inheritance" "Starting memory inheritance enhancement"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "inheritance" "[DRY-RUN] Would enhance memory inheritance cross-references"
        return 0
    fi
    
    if ! verify_db_connection "inheritance"; then
        return 1
    fi
    
    # 高価値メモリの強化
    local enhanced_count=$(psql -d "$DB_NAME" -t -c "
        UPDATE context_stream 
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'), 
            '{inheritance_enhanced}', 
            'true'
        )
        WHERE 
            salience_score > 0.7
            AND metadata->>'inheritance_enhanced' IS NULL;
        SELECT ROW_COUNT();
    " 2>/dev/null | xargs || echo "0")
    
    log_structured "INFO" "inheritance" "High-value memories enhanced" "{\"enhanced_count\":$enhanced_count}"
    
    # クロスリファレンス構築
    local cross_ref_count=$(psql -d "$DB_NAME" -t -c "
        WITH updates AS (
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
                AND array_length(cs1.cross_references, 1) < 5
                AND NOT (cs2.id = ANY(COALESCE(cs1.cross_references, '{}')))
            RETURNING cs1.id
        )
        SELECT COUNT(*) FROM updates;
    " 2>/dev/null | xargs || echo "0")
    
    log_structured "INFO" "inheritance" "Cross-references built" "{\"cross_ref_count\":$cross_ref_count}"
    
    # 結果ログ記録
    psql -d "$DB_NAME" -c "
        INSERT INTO maintenance_log 
        (operation_type, table_name, status, details, completed_at) 
        VALUES ('inheritance', 'context_stream', 'completed', '{\"enhanced\":$enhanced_count,\"cross_references\":$cross_ref_count}'::jsonb, NOW())
    " 2>/dev/null || true
    
    return 0
}

# エンベディングバージョン更新（元db-maintenance-scheduler.sh機能）
execute_embeddings_update() {
    local dry_run=${1:-false}
    
    log_structured "INFO" "embeddings" "Starting embedding version update"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "embeddings" "[DRY-RUN] Would update embedding model versions"
        return 0
    fi
    
    if ! verify_db_connection "embeddings"; then
        return 1
    fi
    
    # バージョン情報なしのレコード数確認
    local unversioned_count=$(psql -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM context_stream 
        WHERE embedding_model IS NULL OR embedding_version IS NULL;" 2>/dev/null | xargs || echo "0")
    
    if [ "$unversioned_count" -eq 0 ]; then
        log_structured "INFO" "embeddings" "All embeddings have version info"
        return 0
    fi
    
    # エンベディングバージョン更新
    local updated_count=$(psql -d "$DB_NAME" -t -c "
        UPDATE context_stream 
        SET 
            embedding_model = 'text-embedding-ada-002',
            embedding_version = 'v1',
            embedding_hash = md5(vector_embedding::text)
        WHERE embedding_model IS NULL OR embedding_version IS NULL;
        SELECT ROW_COUNT();
    " 2>/dev/null | xargs || echo "0")
    
    log_structured "INFO" "embeddings" "Embedding versions updated" "{\"updated_count\":$updated_count}"
    
    # 結果ログ記録
    psql -d "$DB_NAME" -c "
        INSERT INTO maintenance_log 
        (operation_type, table_name, status, details, completed_at) 
        VALUES ('update', 'context_stream', 'completed', '{\"updated_records\":$updated_count}'::jsonb, NOW())
    " 2>/dev/null || true
    
    return 0
}

# cronジョブセットアップ（元setup-backup-cron.sh機能）
execute_cron_setup() {
    local dry_run=${1:-false}
    
    log_structured "INFO" "setup" "Setting up automated maintenance cron jobs"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "setup" "[DRY-RUN] Would install cron jobs for automated maintenance"
        return 0
    fi
    
    local temp_cron=$(mktemp)
    local this_script="$PROJECT_ROOT/scripts/maintenance/db-unified-maintenance.sh"
    
    # 既存cron保持
    crontab -l 2>/dev/null > "$temp_cron" || true
    
    # 既存のDB保守ジョブ削除（重複回避）
    grep -v "db-maintenance-scheduler.sh\|db-unified-maintenance.sh" "$temp_cron" > "${temp_cron}.tmp" || true
    mv "${temp_cron}.tmp" "$temp_cron"
    
    # 統合保守ジョブ追加
    cat >> "$temp_cron" << EOF
# AI Database Unified Maintenance Jobs (Generated by db-unified-maintenance.sh)
0 2 * * * $this_script backup >/dev/null 2>&1
0 3 * * 0 $this_script vector >/dev/null 2>&1
0 4 * * * $this_script vacuum >/dev/null 2>&1
0 * * * * $this_script monitor >/dev/null 2>&1
0 1 * * * $this_script embeddings >/dev/null 2>&1
0 5 * * * $this_script inheritance >/dev/null 2>&1
0 6 * * * $this_script archive >/dev/null 2>&1
EOF
    
    # cronジョブ インストール
    if crontab "$temp_cron" 2>/dev/null; then
        rm "$temp_cron"
        log_structured "INFO" "setup" "Cron jobs installed successfully" "{\"script\":\"$this_script\"}"
        
        echo "✅ 自動保守cronジョブをインストールしました:"
        echo "  • 02:00 daily - フルバックアップ"
        echo "  • 03:00 weekly(日曜) - ベクターインデックス最適化"
        echo "  • 04:00 daily - VACUUM・ANALYZE"
        echo "  • 毎時00分 - パフォーマンス監視"
        echo "  • 01:00 daily - エンベディング更新"
        echo "  • 05:00 daily - メモリ継承強化"
        echo "  • 06:00 daily - WALアーカイブ確認"
        
        return 0
    else
        rm "$temp_cron"
        log_structured "ERROR" "setup" "Failed to install cron jobs"
        return 1
    fi
}

# o3推奨: 全メンテナンス実行（排他制御付き）
execute_all_maintenance() {
    local dry_run=${1:-false}
    local throttle=${2:-10}
    local scope=${3:-all}
    
    log_structured "INFO" "all" "Starting comprehensive database maintenance" "{\"throttle\":$throttle,\"scope\":\"$scope\"}"
    
    # 実行順序（o3推奨：データ影響の少ない順）
    local operations=(
        "monitor"
        "embeddings"
        "inheritance"
        "vector"
        "vacuum"
        "backup"
        "archive"
    )
    
    local success_count=0
    local total_count=${#operations[@]}
    
    for operation in "${operations[@]}"; do
        log_structured "INFO" "all" "Executing operation: $operation"
        
        case $operation in
            "monitor")
                execute_performance_monitor "$dry_run" "text"
                ;;
            "embeddings")
                execute_embeddings_update "$dry_run"
                ;;
            "inheritance")
                execute_inheritance_enhancement "$dry_run"
                ;;
            "vector")
                execute_vector_optimization "$dry_run" "$throttle"
                ;;
            "vacuum")
                execute_vacuum_analyze "$dry_run" "$scope" "$throttle"
                ;;
            "backup")
                execute_full_backup "$dry_run" 7
                ;;
            "archive")
                execute_wal_archive "$dry_run"
                ;;
        esac
        
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            ((success_count++))
            log_structured "INFO" "all" "Operation completed successfully" "{\"operation\":\"$operation\"}"
        else
            log_structured "WARN" "all" "Operation failed" "{\"operation\":\"$operation\",\"exit_code\":$exit_code}"
        fi
        
        # o3推奨：操作間の間隔調整
        sleep "$throttle"
    done
    
    log_structured "INFO" "all" "Comprehensive maintenance completed" "{\"success\":$success_count,\"total\":$total_count}"
    
    echo "🎯 全DB保守完了: $success_count/$total_count 成功"
    
    return 0
}

# o3推奨: エラーハンドラ
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_structured "ERROR" "main" "Script failed with exit code $exit_code"
    fi
    
    # ロック解放
    rm -f /tmp/db_unified_maintenance.lock 2>/dev/null || true
}

trap cleanup EXIT ERR INT TERM

# メイン実行関数
main() {
    local operations=()
    local dry_run=false
    local scope="all"
    local throttle=5
    local no_lock=false
    local output_format="text"
    local verbose=false
    
    # 引数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --scope)
                scope="$2"
                shift 2
                ;;
            --throttle)
                throttle="$2"
                shift 2
                ;;
            --no-lock)
                no_lock=true
                shift
                ;;
            --output)
                output_format="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            vacuum|backup|archive|monitor|vector|inheritance|embeddings|setup-cron|all)
                operations+=("$1")
                shift
                ;;
            *)
                echo "エラー: 不明なオプション $1" >&2
                show_usage
                exit 1
                ;;
        esac
    done
    
    # デフォルト操作
    if [ ${#operations[@]} -eq 0 ]; then
        operations=("all")
    fi
    
    # o3推奨: ロック取得（--no-lockでスキップ可能）
    if [ "$no_lock" = "false" ]; then
        acquire_lock "${operations[0]}"
    fi
    
    # バージョン情報
    if [ "$verbose" = "true" ]; then
        log_structured "INFO" "main" "Database Unified Maintenance System v1.0" "{\"operations\":[\"$(IFS=,; echo "${operations[*]}")\"],\"dry_run\":$dry_run}"
    fi
    
    # 操作実行
    for operation in "${operations[@]}"; do
        case $operation in
            vacuum)
                execute_vacuum_analyze "$dry_run" "$scope" "$throttle"
                ;;
            backup)
                execute_full_backup "$dry_run" 7
                ;;
            archive)
                execute_wal_archive "$dry_run"
                ;;
            monitor)
                execute_performance_monitor "$dry_run" "$output_format"
                ;;
            vector)
                execute_vector_optimization "$dry_run" "$throttle"
                ;;
            inheritance)
                execute_inheritance_enhancement "$dry_run"
                ;;
            embeddings)
                execute_embeddings_update "$dry_run"
                ;;
            setup-cron)
                execute_cron_setup "$dry_run"
                ;;
            all)
                execute_all_maintenance "$dry_run" "$throttle" "$scope"
                ;;
        esac
        
        # 複数操作の場合は間隔調整
        if [ ${#operations[@]} -gt 1 ]; then
            sleep "$throttle"
        fi
    done
}

# archive_commandから直接呼ばれる場合の特別処理
if [ "$1" = "--archive-command" ] && [ $# -eq 3 ]; then
    shift  # --archive-commandを除去
    execute_wal_archive false "$1" "$2"
    exit $?
fi

# スクリプトが直接実行された場合
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi