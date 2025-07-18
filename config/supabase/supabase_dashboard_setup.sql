
-- AI Performance Tracking Table Setup
-- Execute this in Supabase Dashboard > SQL Editor

-- 1. Create the main table
CREATE TABLE IF NOT EXISTS public.ai_performance_log (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    task_success BOOLEAN DEFAULT FALSE,
    execution_time FLOAT DEFAULT 0,
    tool_calls_count INTEGER DEFAULT 0,
    tool_calls JSONB DEFAULT '[]',
    error_count INTEGER DEFAULT 0,
    thinking_tag_used BOOLEAN DEFAULT FALSE,
    todo_tracking BOOLEAN DEFAULT FALSE,
    task_complexity TEXT DEFAULT 'simple',
    user_feedback TEXT,
    learning_score INTEGER DEFAULT 0,
    success_patterns JSONB DEFAULT '[]',
    failure_patterns JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable RLS
ALTER TABLE public.ai_performance_log ENABLE ROW LEVEL SECURITY;

-- 3. Create policies for anonymous access
CREATE POLICY "Allow anonymous inserts" ON public.ai_performance_log
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anonymous reads" ON public.ai_performance_log
    FOR SELECT TO anon USING (true);

-- 4. Grant permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT, INSERT ON public.ai_performance_log TO anon;
GRANT USAGE, SELECT ON SEQUENCE public.ai_performance_log_id_seq TO anon;

-- 5. Insert test data
INSERT INTO public.ai_performance_log (
    session_id, task_success, execution_time, tool_calls_count,
    tool_calls, error_count, thinking_tag_used, todo_tracking,
    task_complexity, learning_score, success_patterns
) VALUES (
    'dashboard_setup_test', true, 1.5, 2,
    '["SQL", "Dashboard"]', 0, false, true,
    'simple', 3, '["dashboard_success"]'
);

-- 6. Verify setup
SELECT * FROM public.ai_performance_log ORDER BY created_at DESC LIMIT 5;
