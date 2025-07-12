#!/bin/bash
# PostgreSQL + pgvector セットアップスクリプト

echo "🗄️ PostgreSQL + pgvector セットアップ開始"

# PostgreSQLインストール確認
if ! command -v psql &> /dev/null; then
    echo "PostgreSQLをインストール中..."
    brew install postgresql
fi

# PostgreSQL起動
echo "PostgreSQL起動中..."
brew services start postgresql

# データベース作成
echo "データベース作成中..."
createdb coding_rule2_ai 2>/dev/null || echo "データベースは既に存在します"

# pgvectorエクステンション追加
echo "pgvectorエクステンション設定中..."
psql -d coding_rule2_ai -c "CREATE EXTENSION IF NOT EXISTS vector;" || echo "pgvectorは既に設定済みです"

# テーブル作成
echo "テーブル作成中..."
psql -d coding_rule2_ai << 'EOF'
-- メモリテーブル
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(384),
    event_type TEXT,
    source TEXT,
    importance TEXT DEFAULT 'medium',
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS memories_embedding_idx ON memories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS memories_session_idx ON memories (session_id);
CREATE INDEX IF NOT EXISTS memories_created_at_idx ON memories (created_at);

-- タスクテーブル
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    assigned_to TEXT,
    estimated_hours REAL,
    actual_hours REAL,
    dependencies JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- タスクインデックス
CREATE INDEX IF NOT EXISTS tasks_status_idx ON tasks (status);
CREATE INDEX IF NOT EXISTS tasks_priority_idx ON tasks (priority);
CREATE INDEX IF NOT EXISTS tasks_session_idx ON tasks (session_id);

-- 学習パターンテーブル
CREATE TABLE IF NOT EXISTS learning_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name TEXT NOT NULL,
    pattern_data JSONB,
    confidence REAL DEFAULT 0.5,
    occurrences INTEGER DEFAULT 1,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 学習パターンインデックス
CREATE INDEX IF NOT EXISTS learning_patterns_name_idx ON learning_patterns (pattern_name);
CREATE INDEX IF NOT EXISTS learning_patterns_confidence_idx ON learning_patterns (confidence);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $USER;
EOF

echo "✅ PostgreSQL + pgvector セットアップ完了"
echo "🔗 接続情報:"
echo "  データベース: coding_rule2_ai"
echo "  ユーザー: $USER"
echo "  ホスト: localhost"
echo "  ポート: 5432"