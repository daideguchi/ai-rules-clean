-- AI Performance Tracking Table
-- Author: Claude (o3 Best Practices)
-- Date: 2025-07-14

-- Create ai_performance_log table
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

-- Enable Row Level Security
ALTER TABLE public.ai_performance_log ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anonymous inserts (for AI data collection)
CREATE POLICY "Allow anonymous inserts on ai_performance_log"
ON public.ai_performance_log
FOR INSERT
TO anon
WITH CHECK (true);

-- Create policy to allow anonymous reads (for AI analysis)
CREATE POLICY "Allow anonymous reads on ai_performance_log"
ON public.ai_performance_log
FOR SELECT
TO anon
USING (true);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_performance_session_id ON public.ai_performance_log(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_performance_timestamp ON public.ai_performance_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_performance_task_success ON public.ai_performance_log(task_success);
CREATE INDEX IF NOT EXISTS idx_ai_performance_complexity ON public.ai_performance_log(task_complexity);

-- Insert initial test data
INSERT INTO public.ai_performance_log (
    session_id,
    task_success,
    execution_time,
    tool_calls_count,
    tool_calls,
    error_count,
    thinking_tag_used,
    todo_tracking,
    task_complexity,
    learning_score,
    success_patterns,
    failure_patterns
) VALUES (
    'initial_setup_test',
    true,
    2.5,
    3,
    '["Bash", "Write", "Read"]',
    0,
    false,
    true,
    'simple',
    3,
    '["successful_setup", "cli_configuration"]',
    '[]'
);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT, INSERT ON public.ai_performance_log TO anon;
GRANT USAGE, SELECT ON SEQUENCE public.ai_performance_log_id_seq TO anon;