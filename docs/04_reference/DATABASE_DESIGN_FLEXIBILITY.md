# 🗄️ データベース設計 - プロダクト柔軟性対応

## 設計戦略：共有クラスター + プロダクト別スキーマ

### アーキテクチャ概要
```
PostgreSQL Cluster (single instance)
├── core schema          # 共通テンプレート
├── coding_rule2 schema  # 現在のプロダクト
├── future_product schema # 将来のプロダクト
└── monitoring schema    # 監視・メトリクス
```

## 実装詳細

### 1. 共通スキーマ（core）
```sql
-- Core schema for template functionality
CREATE SCHEMA IF NOT EXISTS core;

-- AI System registry
CREATE TABLE core.ai_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Common monitoring events
CREATE TABLE core.monitoring_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Template configuration
CREATE TABLE core.template_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    config_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 2. プロダクト固有スキーマ
```sql
-- Product-specific schema
CREATE SCHEMA IF NOT EXISTS coding_rule2;

-- 88-mistake prevention system
CREATE TABLE coding_rule2.mistake_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    pattern_description TEXT NOT NULL,
    pattern_data JSONB NOT NULL,
    occurrences INTEGER DEFAULT 0,
    last_occurrence TIMESTAMPTZ,
    prevention_actions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation context with vector search
CREATE TABLE coding_rule2.conversation_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context_data JSONB NOT NULL,
    vector_embedding vector(1536),
    importance_level VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Constitutional AI violations
CREATE TABLE coding_rule2.constitutional_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    violation_type VARCHAR(50) NOT NULL,
    violation_description TEXT NOT NULL,
    original_response TEXT NOT NULL,
    corrected_response TEXT,
    severity_level VARCHAR(20) NOT NULL,
    auto_corrected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Memory inheritance
CREATE TABLE coding_rule2.memory_inheritance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    memory_content JSONB NOT NULL,
    retention_priority INTEGER DEFAULT 5,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. 監視スキーマ
```sql
-- Monitoring schema
CREATE SCHEMA IF NOT EXISTS monitoring;

-- System performance metrics
CREATE TABLE monitoring.performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(20),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- AI worker status
CREATE TABLE monitoring.worker_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(50) NOT NULL,
    worker_id VARCHAR(50) NOT NULL,
    worker_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    task_count INTEGER DEFAULT 0,
    last_heartbeat TIMESTAMPTZ DEFAULT NOW()
);
```

## 接続管理

### 1. 接続プール設定
```python
# templates/db/connection_pool.py
import psycopg2
from psycopg2 import pool
from typing import Optional

class DatabaseManager:
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min, max connections
            host="localhost",
            database="ai_systems",
            user="ai_user",
            password="secure_password"
        )
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None, schema: str = None):
        """Execute query with automatic schema switching"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                if schema:
                    cur.execute(f"SET search_path TO {schema}, core, monitoring")
                else:
                    cur.execute(f"SET search_path TO {self.product_id}, core, monitoring")
                
                cur.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cur.fetchall()
                else:
                    conn.commit()
                    return cur.rowcount
        finally:
            self.return_connection(conn)
```

### 2. プロダクト固有アクセス
```python
# products/coding_rule2/extensions/db_access.py
from templates.db.connection_pool import DatabaseManager

class CodingRule2Database(DatabaseManager):
    def __init__(self):
        super().__init__(product_id="coding_rule2")
    
    def save_mistake_pattern(self, pattern_type: str, pattern_data: dict):
        """Save mistake pattern"""
        query = """
        INSERT INTO mistake_patterns (pattern_type, pattern_description, pattern_data)
        VALUES (%s, %s, %s)
        ON CONFLICT (pattern_type) DO UPDATE SET
            occurrences = mistake_patterns.occurrences + 1,
            last_occurrence = NOW(),
            pattern_data = EXCLUDED.pattern_data
        """
        return self.execute_query(query, (
            pattern_type, 
            pattern_data.get('description', ''),
            json.dumps(pattern_data)
        ))
    
    def search_conversation_context(self, query_vector: list, limit: int = 10):
        """Vector similarity search"""
        query = """
        SELECT id, session_id, user_message, ai_response, context_data,
               1 - (vector_embedding <=> %s::vector) as similarity
        FROM conversation_context
        WHERE vector_embedding IS NOT NULL
        ORDER BY vector_embedding <=> %s::vector
        LIMIT %s
        """
        return self.execute_query(query, (query_vector, query_vector, limit))
```

## マイグレーション戦略

### 1. Alembicマルチスキーマ
```python
# alembic/env.py
from alembic import context
from sqlalchemy import create_engine
import os

def run_migrations():
    """Run migrations for all product schemas"""
    
    # Get list of active products
    products = os.getenv('ACTIVE_PRODUCTS', 'coding_rule2').split(',')
    
    for product in products:
        # Set schema context
        context.configure(
            target_metadata=get_metadata_for_product(product),
            version_table_schema=product,
            include_schemas=True
        )
        
        # Run migrations
        with context.begin_transaction():
            context.run_migrations()

def get_metadata_for_product(product_id: str):
    """Get metadata for specific product"""
    if product_id == 'coding_rule2':
        from products.coding_rule2.models import metadata
        return metadata
    # Add other products as needed
    return None
```

### 2. 自動マイグレーション
```bash
#!/bin/bash
# scripts/db/migrate_all_products.sh

PRODUCTS=("coding_rule2" "future_product")

for product in "${PRODUCTS[@]}"; do
    echo "Migrating $product..."
    
    # Core schema migrations
    alembic -x schema=core upgrade head
    
    # Product-specific migrations
    alembic -x schema=$product upgrade head
    
    echo "✅ $product migration completed"
done
```

## 運用管理

### 1. バックアップ戦略
```bash
# 全体バックアップ
pg_dump -h localhost -U ai_user ai_systems > backup_full.sql

# スキーマ別バックアップ
pg_dump -h localhost -U ai_user -n coding_rule2 ai_systems > backup_coding_rule2.sql
pg_dump -h localhost -U ai_user -n core ai_systems > backup_core.sql
```

### 2. 監視・アラート
```python
# monitoring/db_health.py
class DatabaseHealthMonitor:
    def check_schema_health(self, product_id: str):
        """Check health of product schema"""
        metrics = {
            'table_count': self.count_tables(product_id),
            'record_count': self.count_records(product_id),
            'last_activity': self.get_last_activity(product_id),
            'schema_size': self.get_schema_size(product_id)
        }
        return metrics
    
    def alert_on_anomalies(self, metrics: dict):
        """Alert on database anomalies"""
        if metrics['record_count'] < 100:
            self.send_alert(f"Low record count: {metrics['record_count']}")
        
        if metrics['schema_size'] > 10_000_000:  # 10MB
            self.send_alert(f"Schema size growing: {metrics['schema_size']}MB")
```

## 結論

**共有クラスター + プロダクト別スキーマ + 自動マイグレーション**

1. **コスト効率**: 単一PostgreSQLクラスター
2. **データ分離**: プロダクト別スキーマ
3. **柔軟性**: 独立したマイグレーション
4. **スケーラビリティ**: 接続プール + 監視システム
5. **セキュリティ**: Row Level Security + スキーマ分離