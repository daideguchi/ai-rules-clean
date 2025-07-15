-- PostgreSQL Database Initialization for AI Learning System
-- Optimized for scale with human-like intelligence features

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Main context stream table with partitioning for scale
CREATE TABLE IF NOT EXISTS context_stream (
    id UUID DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    session_id UUID NOT NULL,
    vector_embedding vector(1536),
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    embedding_version VARCHAR(50) DEFAULT 'v1',
    embedding_hash VARCHAR(64),
    parent_event_id UUID,
    importance_level VARCHAR(20) DEFAULT 'normal',
    project_name VARCHAR(100) DEFAULT 'coding-rule2',
    file_tier VARCHAR(20) DEFAULT 'hot',
    retention_category VARCHAR(30) DEFAULT 'standard',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- expires_at TIMESTAMPTZ,  -- REMOVED: Memory inheritance system never expires
    
    -- Human-like intelligence fields
    emotional_context JSONB,  -- Joy, frustration, discovery patterns
    learning_weight FLOAT DEFAULT 1.0,  -- How much to learn from this
    cross_references UUID[],  -- Related events/contexts
    pattern_tags TEXT[],  -- Identified behavioral patterns
    confidence_score FLOAT DEFAULT 0.5,  -- AI confidence in this data
    salience_score FLOAT DEFAULT 0.5,  -- Memory importance for inheritance weighting
    PRIMARY KEY (id, timestamp)  -- Include timestamp in primary key for partitioning
) PARTITION BY RANGE (timestamp);

-- Create initial partitions (current + next 3 months)
DO $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    FOR i IN 0..3 LOOP
        start_date := date_trunc('month', CURRENT_DATE + interval '1 month' * i);
        end_date := start_date + interval '1 month';
        partition_name := 'context_stream_' || to_char(start_date, 'YYYY_MM');
        
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I 
            PARTITION OF context_stream
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date);
    END LOOP;
END $$;

-- Enhanced mistakes and learning database with structured error taxonomy
CREATE TYPE error_severity AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE error_category AS ENUM ('hallucination', 'factual_error', 'policy_violation', 'technical_failure', 'user_experience', 'security', 'performance');

CREATE TABLE IF NOT EXISTS mistakes_database (
    id SERIAL PRIMARY KEY,
    mistake_id VARCHAR(50) UNIQUE NOT NULL,
    mistake_type VARCHAR(100) NOT NULL,
    error_category error_category NOT NULL DEFAULT 'technical_failure',
    description TEXT NOT NULL,
    pattern_regex TEXT NOT NULL,
    examples JSONB NOT NULL,
    severity error_severity NOT NULL DEFAULT 'medium',
    prevention TEXT NOT NULL,
    trigger_action VARCHAR(50) NOT NULL,
    incident_count INTEGER DEFAULT 0,
    last_occurrence TIMESTAMPTZ,
    financial_impact DECIMAL(10,2) DEFAULT 0,
    learning_notes JSONB,
    prevention_success_rate FLOAT DEFAULT 0.0,
    root_cause_context_id UUID REFERENCES context_stream(id),
    remediation_steps JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document intelligence table
CREATE TABLE IF NOT EXISTS document_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    content_summary TEXT,
    key_insights JSONB,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    access_frequency INTEGER DEFAULT 1,
    relevance_score FLOAT DEFAULT 0.5,
    content_embedding vector(1536),
    tags TEXT[],
    related_documents UUID[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session memory for human-like continuity
CREATE TABLE IF NOT EXISTS session_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_intent TEXT,
    context_summary TEXT,
    emotional_state JSONB,
    key_decisions JSONB,
    unresolved_issues JSONB,
    next_session_prep JSONB,
    session_quality_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes for scale with optimized parameters
CREATE INDEX IF NOT EXISTS idx_context_stream_timestamp ON context_stream USING BTREE (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_stream_importance ON context_stream USING BTREE (importance_level, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_stream_project ON context_stream USING BTREE (project_name, file_tier);
CREATE INDEX IF NOT EXISTS idx_context_stream_learning_weight ON context_stream USING BTREE (learning_weight DESC) WHERE learning_weight > 0.5;

-- Optimized vector indexes for different use cases
CREATE INDEX IF NOT EXISTS idx_context_stream_vector_cosine ON context_stream USING ivfflat (vector_embedding vector_cosine_ops) WITH (lists = 200);
CREATE INDEX IF NOT EXISTS idx_context_stream_vector_l2 ON context_stream USING ivfflat (vector_embedding vector_l2_ops) WITH (lists = 200);

-- High-recall vector index for broader searches
CREATE INDEX IF NOT EXISTS idx_context_stream_vector_recall ON context_stream USING hnsw (vector_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_context_stream_content_fts ON context_stream USING GIN (to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_mistakes_pattern_search ON mistakes_database USING GIN (description gin_trgm_ops);

-- Triggers for human-like learning
CREATE OR REPLACE FUNCTION update_learning_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update mistake incident count
    IF TG_TABLE_NAME = 'mistakes_database' THEN
        NEW.updated_at = NOW();
        NEW.incident_count = OLD.incident_count + 1;
        NEW.last_occurrence = NOW();
    END IF;
    
    -- Update document access patterns
    IF TG_TABLE_NAME = 'document_intelligence' THEN
        NEW.last_accessed = NOW();
        NEW.access_frequency = OLD.access_frequency + 1;
        -- Increase relevance based on access frequency
        NEW.relevance_score = LEAST(1.0, OLD.relevance_score + 0.1);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS tr_mistakes_learning ON mistakes_database;
CREATE TRIGGER tr_mistakes_learning
    BEFORE UPDATE ON mistakes_database
    FOR EACH ROW EXECUTE FUNCTION update_learning_metrics();

DROP TRIGGER IF EXISTS tr_document_learning ON document_intelligence;
CREATE TRIGGER tr_document_learning
    BEFORE UPDATE ON document_intelligence
    FOR EACH ROW EXECUTE FUNCTION update_learning_metrics();

-- Views for human-like intelligence queries
CREATE OR REPLACE VIEW learning_insights AS
SELECT 
    md.mistake_type,
    md.severity,
    md.incident_count,
    md.prevention_success_rate,
    CASE 
        WHEN md.incident_count > 10 THEN 'Critical Pattern'
        WHEN md.incident_count > 5 THEN 'Recurring Issue'
        ELSE 'Isolated Event'
    END as learning_category,
    md.last_occurrence,
    md.prevention
FROM mistakes_database md
ORDER BY md.incident_count DESC, md.last_occurrence DESC;

CREATE OR REPLACE VIEW context_intelligence AS
SELECT 
    cs.event_type,
    cs.importance_level,
    COUNT(*) as frequency,
    AVG(cs.confidence_score) as avg_confidence,
    MAX(cs.timestamp) as last_seen,
    ARRAY_AGG(DISTINCT cs.project_name) as projects,
    STRING_AGG(DISTINCT cs.source, ', ') as sources
FROM context_stream cs
WHERE cs.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY cs.event_type, cs.importance_level
ORDER BY frequency DESC;

-- Initialize with current mistakes data if exists
-- This will be populated by the migration script

-- Memory management and TTL policies
CREATE TABLE IF NOT EXISTS memory_policies (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(100) UNIQUE NOT NULL,
    retention_days INTEGER NOT NULL,
    min_salience_threshold FLOAT DEFAULT 0.3,
    max_context_items INTEGER DEFAULT 10000,
    summarization_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Learning weight signal logging
CREATE TABLE IF NOT EXISTS learning_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_id UUID NOT NULL,
    signal_type VARCHAR(50) NOT NULL, -- 'user_feedback', 'performance_metric', 'error_correction'
    signal_value FLOAT NOT NULL,
    signal_metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT false
);

-- Scheduled maintenance and optimization tracking
CREATE TABLE IF NOT EXISTS maintenance_log (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL, -- 'reindex', 'vacuum', 'summarize', 'cleanup'
    table_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed'
    details JSONB,
    performance_impact JSONB
);

-- Insert default memory policies
INSERT INTO memory_policies (policy_name, retention_days, min_salience_threshold, max_context_items) VALUES
('high_value_memories', 365, 0.8, 1000),
('standard_memories', 90, 0.5, 5000),
('low_value_memories', 30, 0.3, 10000),
('critical_errors', -1, 0.9, -1) -- Never expire
ON CONFLICT (policy_name) DO NOTHING;

COMMENT ON DATABASE coding_rule2_ai IS 'AI Learning System Database - Human-like Intelligence Implementation with Advanced Memory Management';
COMMENT ON TABLE context_stream IS 'Core context accumulation with emotional and learning intelligence, embedding versioning, and TTL support';
COMMENT ON TABLE mistakes_database IS '78+ mistakes database with structured error taxonomy and root cause tracking';
COMMENT ON TABLE document_intelligence IS 'Document understanding and relevance tracking';
COMMENT ON TABLE session_memory IS 'Cross-session memory for human-like continuity';
COMMENT ON TABLE memory_policies IS 'Memory retention and cleanup policies for different data types';
COMMENT ON TABLE learning_signals IS 'Raw learning signals for weight calculation auditing and retraining';
COMMENT ON TABLE maintenance_log IS 'Database maintenance operations tracking for performance optimization';