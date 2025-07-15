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
        relname as tablename,
        indexrelname as indexname,
        idx_scan as scans,
        idx_tup_read as reads,
        idx_tup_fetch as fetches
    FROM pg_stat_user_indexes 
    WHERE indexrelname LIKE '%context%' OR indexrelname LIKE '%vector%'
    ORDER BY idx_scan DESC
    LIMIT 10;
"
