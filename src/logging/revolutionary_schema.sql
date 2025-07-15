-- Revolutionary Log Management System Database Schema
-- Complete schema for all three tasks

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Task 1: Unified Log Management Tables

-- Main unified logs table with atomic synchronization support
CREATE TABLE IF NOT EXISTS unified_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file TEXT NOT NULL,
    log_level VARCHAR(20) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    component VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    structured_data JSONB DEFAULT '{}',
    session_id VARCHAR(100),
    hash_signature VARCHAR(64) UNIQUE NOT NULL,
    embedding vector(384),
    sync_status VARCHAR(20) DEFAULT 'synced' CHECK (sync_status IN ('pending', 'synced', 'error')),
    file_backup_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Log aggregation metadata
CREATE TABLE IF NOT EXISTS log_aggregation_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(100) UNIQUE NOT NULL,
    source_path TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('file', 'database', 'api', 'memory')),
    is_active BOOLEAN DEFAULT TRUE,
    last_processed TIMESTAMPTZ,
    processing_config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session continuity tracking
CREATE TABLE IF NOT EXISTS session_continuity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    parent_session_id VARCHAR(100),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    inherited_context JSONB DEFAULT '{}',
    log_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Task 2: Script/Document Reference System Tables

-- Python script references with dependency tracking
CREATE TABLE IF NOT EXISTS script_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    script_path TEXT UNIQUE NOT NULL,
    script_name VARCHAR(255) NOT NULL,
    relative_path TEXT NOT NULL,
    dependencies JSONB DEFAULT '[]',
    doc_references JSONB DEFAULT '[]',
    last_modified TIMESTAMPTZ NOT NULL,
    functions JSONB DEFAULT '[]',
    classes JSONB DEFAULT '[]',
    imports JSONB DEFAULT '[]',
    description TEXT,
    docstring TEXT,
    line_count INTEGER DEFAULT 0,
    complexity_score FLOAT DEFAULT 0.0,
    embedding vector(384),
    analysis_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document references with semantic search capability
CREATE TABLE IF NOT EXISTS document_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_path TEXT UNIQUE NOT NULL,
    doc_name VARCHAR(255) NOT NULL,
    relative_path TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    referenced_scripts JSONB DEFAULT '[]',
    sections JSONB DEFAULT '[]',
    last_modified TIMESTAMPTZ NOT NULL,
    description TEXT,
    full_content TEXT,
    word_count INTEGER DEFAULT 0,
    embedding vector(384),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cross-reference mapping table
CREATE TABLE IF NOT EXISTS cross_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('script', 'document')),
    source_id UUID NOT NULL,
    target_type VARCHAR(20) NOT NULL CHECK (target_type IN ('script', 'document')),
    target_id UUID NOT NULL,
    reference_type VARCHAR(50) NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    context_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_id, target_id, reference_type)
);

-- Task 3: Folder Structure Rule Enforcement Tables

-- Folder structure violations tracking
CREATE TABLE IF NOT EXISTS folder_structure_violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    violation_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    file_path TEXT NOT NULL,
    details JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_details JSONB DEFAULT '{}',
    resolution_time TIMESTAMPTZ,
    session_id VARCHAR(100),
    auto_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Folder structure rules definition
CREATE TABLE IF NOT EXISTS folder_structure_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(100) UNIQUE NOT NULL,
    rule_type VARCHAR(50) NOT NULL CHECK (rule_type IN ('file_limit', 'location_rule', 'naming_convention', 'dependency_rule')),
    path_pattern TEXT NOT NULL,
    rule_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    enforcement_level VARCHAR(20) DEFAULT 'warning' CHECK (enforcement_level IN ('info', 'warning', 'error', 'critical')),
    auto_fix BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- File organization actions log
CREATE TABLE IF NOT EXISTS file_organization_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('move', 'rename', 'delete', 'create_dir', 'organize')),
    source_path TEXT NOT NULL,
    target_path TEXT,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'reverted')),
    metadata JSONB DEFAULT '{}',
    performed_by VARCHAR(100) DEFAULT 'system',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_id VARCHAR(100)
);

-- Performance and Analytics Tables

-- System performance metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit VARCHAR(20),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_id VARCHAR(100),
    metadata JSONB DEFAULT '{}'
);

-- Search queries and results for optimization
CREATE TABLE IF NOT EXISTS search_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    search_type VARCHAR(50) NOT NULL CHECK (search_type IN ('logs', 'scripts', 'documents', 'cross_reference')),
    results_count INTEGER DEFAULT 0,
    execution_time_ms INTEGER DEFAULT 0,
    used_vector_search BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_id VARCHAR(100),
    user_context JSONB DEFAULT '{}'
);

-- Indexes for Performance

-- Unified logs indexes
CREATE INDEX IF NOT EXISTS idx_unified_logs_timestamp ON unified_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_unified_logs_component ON unified_logs (component, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_unified_logs_level ON unified_logs (log_level, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_unified_logs_session ON unified_logs (session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_unified_logs_hash ON unified_logs (hash_signature);
CREATE INDEX IF NOT EXISTS idx_unified_logs_sync_status ON unified_logs (sync_status, timestamp DESC);

-- Script references indexes
CREATE INDEX IF NOT EXISTS idx_script_references_path ON script_references (script_path);
CREATE INDEX IF NOT EXISTS idx_script_references_name ON script_references (script_name);
CREATE INDEX IF NOT EXISTS idx_script_references_modified ON script_references (last_modified DESC);
CREATE INDEX IF NOT EXISTS idx_script_references_dependencies ON script_references USING GIN (dependencies);

-- Document references indexes
CREATE INDEX IF NOT EXISTS idx_document_references_path ON document_references (doc_path);
CREATE INDEX IF NOT EXISTS idx_document_references_name ON document_references (doc_name);
CREATE INDEX IF NOT EXISTS idx_document_references_modified ON document_references (last_modified DESC);
CREATE INDEX IF NOT EXISTS idx_document_references_scripts ON document_references USING GIN (referenced_scripts);
CREATE INDEX IF NOT EXISTS idx_document_references_hash ON document_references (content_hash);

-- Cross-references indexes
CREATE INDEX IF NOT EXISTS idx_cross_references_source ON cross_references (source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_cross_references_target ON cross_references (target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_cross_references_type ON cross_references (reference_type);

-- Folder structure indexes
CREATE INDEX IF NOT EXISTS idx_folder_violations_type ON folder_structure_violations (violation_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_folder_violations_resolved ON folder_structure_violations (resolved, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_folder_violations_session ON folder_structure_violations (session_id);

-- Vector similarity search indexes (if supported)
CREATE INDEX IF NOT EXISTS idx_unified_logs_embedding ON unified_logs USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_script_references_embedding ON script_references USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_document_references_embedding ON document_references USING ivfflat (embedding vector_cosine_ops);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_unified_logs_message_fts ON unified_logs USING gin(to_tsvector('english', message));
CREATE INDEX IF NOT EXISTS idx_script_references_desc_fts ON script_references USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_document_references_desc_fts ON document_references USING gin(to_tsvector('english', description));

-- Triggers for automatic updates

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_unified_logs_updated_at BEFORE UPDATE ON unified_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_script_references_updated_at BEFORE UPDATE ON script_references FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_document_references_updated_at BEFORE UPDATE ON document_references FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_folder_structure_rules_updated_at BEFORE UPDATE ON folder_structure_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Functions for common operations

-- Get log statistics
CREATE OR REPLACE FUNCTION get_log_statistics()
RETURNS TABLE (
    total_logs BIGINT,
    unique_sessions BIGINT,
    unique_components BIGINT,
    error_count BIGINT,
    warning_count BIGINT,
    today_logs BIGINT,
    avg_logs_per_hour NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_logs,
        COUNT(DISTINCT session_id) as unique_sessions,
        COUNT(DISTINCT component) as unique_components,
        COUNT(*) FILTER (WHERE log_level = 'ERROR') as error_count,
        COUNT(*) FILTER (WHERE log_level = 'WARNING') as warning_count,
        COUNT(*) FILTER (WHERE timestamp >= CURRENT_DATE) as today_logs,
        ROUND(COUNT(*) / GREATEST(EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) / 3600, 1), 2) as avg_logs_per_hour
    FROM unified_logs;
END;
$$ LANGUAGE plpgsql;

-- Get script dependency chain
CREATE OR REPLACE FUNCTION get_script_dependency_chain(script_path_param TEXT)
RETURNS TABLE (
    level INTEGER,
    script_path TEXT,
    script_name VARCHAR(255),
    dependency_type VARCHAR(50)
) AS $$
WITH RECURSIVE dependency_chain AS (
    -- Base case: the script itself
    SELECT 
        0 as level,
        s.script_path,
        s.script_name,
        'root' as dependency_type
    FROM script_references s
    WHERE s.script_path = script_path_param
    
    UNION ALL
    
    -- Recursive case: dependencies
    SELECT 
        dc.level + 1,
        s.script_path,
        s.script_name,
        'dependency' as dependency_type
    FROM dependency_chain dc
    JOIN script_references s ON s.script_name = ANY(SELECT jsonb_array_elements_text(sr.dependencies))
    JOIN script_references sr ON sr.script_path = dc.script_path
    WHERE dc.level < 10 -- Prevent infinite recursion
)
SELECT level, script_path, script_name, dependency_type
FROM dependency_chain
ORDER BY level, script_name;
$$ LANGUAGE SQL;

-- Insert default folder structure rules
INSERT INTO folder_structure_rules (rule_name, rule_type, path_pattern, rule_config, enforcement_level, auto_fix) VALUES
('root_file_limit', 'file_limit', '/', '{"max_files": 12, "allowed_extensions": [".md", ".yml", ".yaml", ".json", ".txt"]}', 'warning', true),
('scripts_organization', 'location_rule', 'scripts/**/*.py', '{"required_parent": "scripts", "max_depth": 3}', 'warning', true),
('docs_organization', 'location_rule', 'docs/**/*.md', '{"required_parent": "docs", "max_depth": 4}', 'info', true),
('config_organization', 'location_rule', 'config/**/*.{json,yml,yaml}', '{"required_parent": "config", "max_depth": 2}', 'info', true),
('log_file_location', 'location_rule', '**/*.log', '{"required_parent": "runtime/logs", "auto_move": true}', 'error', true),
('python_naming', 'naming_convention', '**/*.py', '{"pattern": "^[a-z_][a-z0-9_]*\\.py$", "description": "Python files should use snake_case"}', 'warning', false)
ON CONFLICT (rule_name) DO NOTHING;

-- Insert default log aggregation sources
INSERT INTO log_aggregation_sources (source_name, source_path, source_type, processing_config) VALUES
('ai_api_logs', 'runtime/ai_api_logs', 'file', '{"pattern": "*.log", "format": "auto"}'),
('memory_logs', 'runtime/logs', 'file', '{"pattern": "*.log", "format": "auto"}'),
('conversation_logs', 'runtime/conversation_logs', 'file', '{"pattern": "*.jsonl", "format": "jsonl"}'),
('unified_memory', 'src/memory/unified_memory_manager.py', 'database', '{"table": "unified_memory", "connection": "main"}'),
('constitutional_ai', 'src/ai/constitutional_ai.py', 'api', '{"endpoint": "violations", "format": "json"}')
ON CONFLICT (source_name) DO NOTHING;

-- Create materialized views for performance

-- Recent logs summary
CREATE MATERIALIZED VIEW IF NOT EXISTS recent_logs_summary AS
SELECT 
    component,
    log_level,
    COUNT(*) as count,
    MAX(timestamp) as latest_entry,
    MIN(timestamp) as earliest_entry
FROM unified_logs
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY component, log_level
ORDER BY count DESC;

-- Script complexity overview
CREATE MATERIALIZED VIEW IF NOT EXISTS script_complexity_overview AS
SELECT 
    script_name,
    script_path,
    line_count,
    complexity_score,
    jsonb_array_length(functions) as function_count,
    jsonb_array_length(dependencies) as dependency_count,
    last_modified
FROM script_references
ORDER BY complexity_score DESC;

-- Document reference network
CREATE MATERIALIZED VIEW IF NOT EXISTS document_reference_network AS
SELECT 
    d.doc_name,
    d.doc_path,
    jsonb_array_length(d.referenced_scripts) as script_references,
    jsonb_array_length(d.sections) as section_count,
    d.word_count,
    d.last_modified
FROM document_references d
ORDER BY script_references DESC, word_count DESC;

-- Create refresh function for materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW recent_logs_summary;
    REFRESH MATERIALIZED VIEW script_complexity_overview;
    REFRESH MATERIALIZED VIEW document_reference_network;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE unified_logs IS 'Central table for all unified log entries with atomic synchronization support';
COMMENT ON TABLE script_references IS 'Python script analysis and cross-referencing with dependency tracking';
COMMENT ON TABLE document_references IS 'Markdown document analysis with semantic search capabilities';
COMMENT ON TABLE folder_structure_violations IS 'Real-time folder structure violation tracking and resolution';
COMMENT ON TABLE cross_references IS 'Cross-reference mapping between scripts and documents';
COMMENT ON FUNCTION get_log_statistics() IS 'Returns comprehensive log statistics for monitoring';
COMMENT ON FUNCTION get_script_dependency_chain(TEXT) IS 'Returns recursive dependency chain for a given script';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;
