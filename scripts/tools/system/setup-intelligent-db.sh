#!/bin/bash
set -euo pipefail

# Intelligent Database Setup for Human-like AI Learning
# Designed for scale with emotional intelligence and adaptive learning

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
DB_NAME="coding_rule2_ai"
DB_USER="dd"
LOG_FILE="$PROJECT_ROOT/runtime/ai_api_logs/db_setup_$(date +%Y%m%d_%H%M%S).log"

echo "🧠 Setting up Intelligent Database for Human-like AI Learning"
echo "============================================================"

# Create log directory
mkdir -p "$PROJECT_ROOT/runtime/ai_api_logs"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if PostgreSQL is running
check_postgresql() {
    if ! command -v psql &> /dev/null; then
        log "❌ PostgreSQL not found. Please install PostgreSQL first."
        log "🍺 macOS: brew install postgresql"
        log "🐧 Ubuntu: sudo apt-get install postgresql postgresql-contrib"
        return 1
    fi
    
    if ! pg_isready &> /dev/null; then
        log "⚠️ PostgreSQL not running. Starting PostgreSQL..."
        # Try to start PostgreSQL
        if command -v brew &> /dev/null; then
            brew services start postgresql || log "Failed to start PostgreSQL with brew"
        elif command -v systemctl &> /dev/null; then
            sudo systemctl start postgresql || log "Failed to start PostgreSQL with systemctl"
        else
            log "❌ Cannot start PostgreSQL automatically. Please start it manually."
            return 1
        fi
        
        # Wait for PostgreSQL to start
        sleep 3
        if ! pg_isready &> /dev/null; then
            log "❌ PostgreSQL failed to start"
            return 1
        fi
    fi
    
    log "✅ PostgreSQL is running"
    return 0
}

# Create database and user
setup_database() {
    log "🗄️ Setting up database and user..."
    
    # Create database if it doesn't exist
    if ! psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log "Creating database: $DB_NAME"
        createdb "$DB_NAME" || {
            log "❌ Failed to create database"
            return 1
        }
    else
        log "✅ Database $DB_NAME already exists"
    fi
    
    # Install pgvector extension
    log "📊 Installing pgvector extension..."
    psql -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || {
        log "⚠️ pgvector not available. Installing..."
        
        # Try to install pgvector
        if command -v brew &> /dev/null; then
            brew install pgvector || log "Failed to install pgvector with brew"
        else
            log "❌ pgvector not available. Please install manually:"
            log "   GitHub: https://github.com/pgvector/pgvector"
            return 1
        fi
        
        # Retry extension creation
        psql -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;" || {
            log "❌ Failed to create vector extension"
            return 1
        }
    }
    
    log "✅ pgvector extension ready"
}

# Initialize database schema
initialize_schema() {
    log "🏗️ Initializing intelligent database schema..."
    
    local init_sql="$PROJECT_ROOT/config/postgresql/init-db.sql"
    
    if [[ -f "$init_sql" ]]; then
        if psql -d "$DB_NAME" -f "$init_sql" >> "$LOG_FILE" 2>&1; then
            log "✅ Database schema initialized successfully"
        else
            log "❌ Failed to initialize database schema"
            log "📋 Check log file: $LOG_FILE"
            return 1
        fi
    else
        log "❌ Schema file not found: $init_sql"
        return 1
    fi
}

# Migrate existing data
migrate_existing_data() {
    log "📦 Migrating existing data to intelligent database..."
    
    # Look for mistakes database
    local mistakes_file
    if [[ -f "$PROJECT_ROOT/src/memory/persistent-learning/mistakes-database.json" ]]; then
        mistakes_file="$PROJECT_ROOT/src/memory/persistent-learning/mistakes-database.json"
    elif [[ -f "$PROJECT_ROOT/src/memory/mistakes-database.json" ]]; then
        mistakes_file="$PROJECT_ROOT/src/memory/mistakes-database.json"
    else
        log "⚠️ No mistakes database found to migrate"
        return 0
    fi
    
    log "📄 Found mistakes database: $mistakes_file"
    
    # Use Python to migrate JSON data
    python3 << EOF
import json
import psycopg2
import sys
from datetime import datetime

try:
    with open('$mistakes_file', 'r') as f:
        data = json.load(f)
    
    conn = psycopg2.connect(
        host='localhost',
        database='$DB_NAME',
        user='$DB_USER'
    )
    cur = conn.cursor()
    
    # Migrate mistakes data
    if 'critical_patterns' in data:
        for mistake in data['critical_patterns']:
            cur.execute("""
                INSERT INTO mistakes_database 
                (mistake_id, mistake_type, description, pattern_regex, examples,
                 severity, prevention, trigger_action, incident_count, 
                 last_occurrence, financial_impact)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (mistake_id) DO UPDATE SET
                    incident_count = EXCLUDED.incident_count,
                    last_occurrence = EXCLUDED.last_occurrence
            """, (
                mistake.get('id', ''),
                mistake.get('type', ''),
                mistake.get('description', ''),
                mistake.get('pattern', ''),
                json.dumps(mistake.get('examples', [])),
                mistake.get('severity', 'medium'),
                mistake.get('prevention', ''),
                mistake.get('trigger_action', ''),
                mistake.get('incident_count', 0),
                datetime.fromisoformat(mistake['last_occurrence'].replace('Z', '+00:00')) if mistake.get('last_occurrence') else None,
                float(str(mistake.get('financial_impact', '0')).replace('¥', '').replace('+', '').replace(',', '') or 0)
            ))
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Migration successful")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)
EOF
    
    if [[ $? -eq 0 ]]; then
        log "✅ Data migration completed successfully"
    else
        log "❌ Data migration failed"
        return 1
    fi
}

# Test database functionality
test_database() {
    log "🧪 Testing database functionality..."
    
    # Test basic connectivity
    if ! psql -d "$DB_NAME" -c "SELECT 1;" > /dev/null; then
        log "❌ Database connectivity test failed"
        return 1
    fi
    
    # Test vector extension
    if ! psql -d "$DB_NAME" -c "SELECT '[1,2,3]'::vector;" > /dev/null; then
        log "❌ Vector extension test failed"
        return 1
    fi
    
    # Test intelligent context system
    if python3 -c "
import sys
sys.path.append('$PROJECT_ROOT/src/memory')
from intelligent_context_system import IntelligentContextSystem
ics = IntelligentContextSystem()
conn = ics.connect_db()
if conn:
    conn.close()
    print('✅ Python database connection successful')
else:
    print('❌ Python database connection failed')
    sys.exit(1)
"; then
        log "✅ Intelligent context system connectivity verified"
    else
        log "❌ Intelligent context system test failed"
        return 1
    fi
}

# Performance optimization
optimize_database() {
    log "⚡ Applying performance optimizations..."
    
    psql -d "$DB_NAME" << 'EOF'
-- Performance settings for AI workload
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD optimization
ALTER SYSTEM SET effective_io_concurrency = 200;  -- SSD optimization

-- Vector-specific optimizations
ALTER SYSTEM SET max_parallel_workers_per_gather = 2;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_worker_processes = 8;

-- Memory for vector operations
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';

SELECT pg_reload_conf();
EOF
    
    log "✅ Performance optimizations applied"
}

# Create monitoring views
setup_monitoring() {
    log "📊 Setting up monitoring and analytics..."
    
    psql -d "$DB_NAME" << 'EOF'
-- Create monitoring views
CREATE OR REPLACE VIEW ai_learning_dashboard AS
SELECT 
    'Mistakes Database' as component,
    COUNT(*) as total_records,
    SUM(incident_count) as total_incidents,
    AVG(prevention_success_rate) as avg_success_rate,
    MAX(last_occurrence) as last_activity
FROM mistakes_database
UNION ALL
SELECT 
    'Context Stream' as component,
    COUNT(*) as total_records,
    COUNT(DISTINCT session_id) as total_sessions,
    AVG(confidence_score) as avg_confidence,
    MAX(timestamp) as last_activity
FROM context_stream
UNION ALL
SELECT 
    'Document Intelligence' as component,
    COUNT(*) as total_records,
    SUM(access_frequency) as total_accesses,
    AVG(relevance_score) as avg_relevance,
    MAX(last_accessed) as last_activity
FROM document_intelligence;

-- Learning efficiency view
CREATE OR REPLACE VIEW learning_efficiency AS
SELECT 
    emotional_context->>'primary_emotion' as emotion,
    COUNT(*) as event_count,
    AVG(learning_weight) as avg_learning_weight,
    AVG(confidence_score) as avg_confidence,
    STRING_AGG(DISTINCT event_type, ', ') as event_types
FROM context_stream 
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY emotional_context->>'primary_emotion'
ORDER BY avg_learning_weight DESC;
EOF
    
    log "✅ Monitoring views created"
}

# Main execution
main() {
    log "🚀 Starting intelligent database setup..."
    
    # Check prerequisites
    check_postgresql || {
        log "❌ PostgreSQL setup failed"
        exit 1
    }
    
    # Setup database
    setup_database || {
        log "❌ Database setup failed"
        exit 1
    }
    
    # Initialize schema
    initialize_schema || {
        log "❌ Schema initialization failed"
        exit 1
    }
    
    # Migrate existing data
    migrate_existing_data
    
    # Test functionality
    test_database || {
        log "❌ Database testing failed"
        exit 1
    }
    
    # Apply optimizations
    optimize_database
    
    # Setup monitoring
    setup_monitoring
    
    log "🎉 Intelligent database setup completed successfully!"
    log ""
    log "📋 Next steps:"
    log "1. Test the intelligent context system:"
    log "   python3 src/memory/intelligent_context_system.py"
    log ""
    log "2. View learning dashboard:"
    log "   psql -d $DB_NAME -c 'SELECT * FROM ai_learning_dashboard;'"
    log ""
    log "3. Monitor learning efficiency:"
    log "   psql -d $DB_NAME -c 'SELECT * FROM learning_efficiency;'"
    log ""
    log "📄 Setup log: $LOG_FILE"
}

# Execute main function
main "$@"