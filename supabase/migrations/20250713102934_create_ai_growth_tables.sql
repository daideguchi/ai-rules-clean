-- AIÍãw∑π∆‡(∆¸÷Î\ﬁ§∞Ï¸∑ÁÛ

-- 1. AI—’©¸ﬁÛπÌ∞∆¸÷Î
CREATE TABLE IF NOT EXISTS ai_performance_log (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    task_success BOOLEAN NOT NULL DEFAULT FALSE,
    execution_time NUMERIC(10,3) DEFAULT 0,
    tool_calls_count INTEGER DEFAULT 0,
    tool_calls JSONB DEFAULT '[]',
    error_count INTEGER DEFAULT 0,
    thinking_tag_used BOOLEAN DEFAULT FALSE,
    todo_tracking BOOLEAN DEFAULT FALSE,
    task_complexity TEXT DEFAULT 'simple',
    learning_score NUMERIC(5,2) DEFAULT 0,
    success_patterns JSONB DEFAULT '[]',
    failure_patterns JSONB DEFAULT '[]',
    user_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. AIf“—ø¸Û∆¸÷Î
CREATE TABLE IF NOT EXISTS ai_learning_patterns (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    pattern_type TEXT NOT NULL, -- 'success' or 'failure'
    patterns JSONB NOT NULL DEFAULT '[]',
    effectiveness_score NUMERIC(5,2) DEFAULT 0,
    session_id TEXT,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Claude.md2et∆¸÷Î
CREATE TABLE IF NOT EXISTS claude_evolution_history (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    change_type TEXT NOT NULL,
    old_content TEXT,
    new_content TEXT,
    reason TEXT,
    performance_improvement NUMERIC(5,2) DEFAULT 0,
    triggered_by_session TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- §Û«√Øπ\—’©¸ﬁÛπ
	
CREATE INDEX IF NOT EXISTS idx_performance_session ON ai_performance_log(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON ai_performance_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_success ON ai_performance_log(task_success);
CREATE INDEX IF NOT EXISTS idx_learning_pattern_type ON ai_learning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_learning_timestamp ON ai_learning_patterns(timestamp);

-- Row Level Security (RLS) -ö
ALTER TABLE ai_performance_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE claude_evolution_history ENABLE ROW LEVEL SECURITY;

-- ˙,Ñj›Í∑¸ç<Ê¸∂¸	
CREATE POLICY "Allow authenticated users" ON ai_performance_log
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users" ON ai_learning_patterns
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users" ON claude_evolution_history
    FOR ALL USING (auth.role() = 'authenticated');

-- µ¸”πÌ¸Î(›Í∑¸n8n¢Øªπ(	
CREATE POLICY "Allow service role" ON ai_performance_log
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role" ON ai_learning_patterns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role" ON claude_evolution_history
    FOR ALL USING (auth.role() = 'service_role');