-- AI自律成長システム用テーブル作成 (Supabase Dashboard用)

-- 1. AIパフォーマンスログテーブル
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

-- 2. AI学習パターンテーブル
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

-- 3. Claude.md進化履歴テーブル
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

-- インデックス作成（パフォーマンス向上）
CREATE INDEX IF NOT EXISTS idx_performance_session ON ai_performance_log(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON ai_performance_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_success ON ai_performance_log(task_success);
CREATE INDEX IF NOT EXISTS idx_learning_pattern_type ON ai_learning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_learning_timestamp ON ai_learning_patterns(timestamp);

-- Row Level Security (RLS) 設定
ALTER TABLE ai_performance_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE claude_evolution_history ENABLE ROW LEVEL SECURITY;

-- 基本的なポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated users" ON ai_performance_log
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users" ON ai_learning_patterns
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users" ON claude_evolution_history
    FOR ALL USING (auth.role() = 'authenticated');

-- サービスロール用ポリシー（n8nアクセス用）
CREATE POLICY "Allow service role" ON ai_performance_log
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role" ON ai_learning_patterns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role" ON claude_evolution_history
    FOR ALL USING (auth.role() = 'service_role');

-- 確認用クエリ
SELECT 'AI Growth Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name LIKE 'ai_%' OR table_name LIKE 'claude_%');