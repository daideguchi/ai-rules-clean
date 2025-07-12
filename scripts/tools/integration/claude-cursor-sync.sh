#!/bin/bash
# Claude Code ⇄ Cursor Editor Synchronization System
# Manages work status, file paths, and project coordination

set -euo pipefail

echo "🔗 Claude Code ⇄ Cursor Sync System"

# Configuration
SYNC_DATA_FILE="runtime/cursor-claude-sync.json"
WORK_LOG_FILE="runtime/logs/work-log.md"
PROJECT_STATUS_FILE="runtime/project-status.json"

# Ensure runtime directories exist
mkdir -p runtime/logs runtime/data

# Function to get current timestamp in Japan timezone
get_japan_timestamp() {
    TZ='Asia/Tokyo' date '+%Y-%m-%d %H:%M:%S JST'
}

# Function to get current git status
get_git_status() {
    local status=""
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local branch=$(git branch --show-current 2>/dev/null || echo "detached")
        local changes=$(git status --porcelain | wc -l | tr -d ' ')
        local commits_ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
        
        status="$branch ($changes changes, $commits_ahead ahead)"
    else
        status="Not a git repository"
    fi
    
    echo "$status"
}

# Function to get project paths
get_project_paths() {
    local paths=$(cat << EOF
{
    "root": "$(pwd)",
    "scripts": "$(pwd)/scripts",
    "docs": "$(pwd)/docs",
    "src": "$(pwd)/src",
    "cursor_rules": "$(pwd)/.cursor/rules",
    "runtime": "$(pwd)/runtime",
    "ai_memory": "$(pwd)/src/ai/memory",
    "claude_md": "$(pwd)/docs/instructions/CLAUDE.md"
}
EOF
)
    echo "$paths"
}

# Function to record current work status
record_status() {
    local message="${1:-Auto-generated status}"
    local timestamp=$(get_japan_timestamp)
    local git_status=$(get_git_status)
    local paths=$(get_project_paths)
    
    # Create sync data
    local sync_data=$(cat << EOF
{
    "timestamp": "$timestamp",
    "message": "$message",
    "git_status": "$git_status",
    "paths": $paths,
    "file_counts": {
        "total_files": $(find . -type f | wc -l | tr -d ' '),
        "scripts": $(find scripts -name "*.sh" 2>/dev/null | wc -l | tr -d ' '),
        "docs": $(find docs -name "*.md" 2>/dev/null | wc -l | tr -d ' '),
        "src_files": $(find src -type f 2>/dev/null | wc -l | tr -d ' ')
    },
    "recent_changes": [
$(git log --oneline -5 --pretty=format:'        "%h: %s"' 2>/dev/null | head -5 | sed '$ ! s/$/,/')
    ]
}
EOF
)
    
    echo "$sync_data" > "$SYNC_DATA_FILE"
    
    # Also log to work log
    echo "## [$timestamp] $message" >> "$WORK_LOG_FILE"
    echo "- Git: $git_status" >> "$WORK_LOG_FILE"
    echo "- Files: $(find . -type f | wc -l | tr -d ' ') total" >> "$WORK_LOG_FILE"
    echo "" >> "$WORK_LOG_FILE"
    
    echo "✅ Status recorded: $message"
    echo "📁 Data saved to: $SYNC_DATA_FILE"
}

# Function to share current status
share_status() {
    if [[ ! -f "$SYNC_DATA_FILE" ]]; then
        echo "❌ No sync data found. Run 'record' first."
        exit 1
    fi
    
    echo "📊 Latest Project Status"
    echo "======================="
    
    local timestamp=$(jq -r '.timestamp' "$SYNC_DATA_FILE" 2>/dev/null || echo "Unknown")
    local message=$(jq -r '.message' "$SYNC_DATA_FILE" 2>/dev/null || echo "No message")
    local git_status=$(jq -r '.git_status' "$SYNC_DATA_FILE" 2>/dev/null || echo "Unknown")
    
    echo "🕐 Last Update: $timestamp"
    echo "💬 Message: $message"  
    echo "🌿 Git Status: $git_status"
    echo ""
    
    echo "📁 Project Paths:"
    if command -v jq >/dev/null 2>&1; then
        jq -r '.paths | to_entries[] | "  \(.key): \(.value)"' "$SYNC_DATA_FILE" 2>/dev/null || echo "  (Path data unavailable)"
    else
        echo "  (Install jq for detailed path information)"
    fi
    echo ""
    
    echo "📊 File Counts:"
    if command -v jq >/dev/null 2>&1; then
        jq -r '.file_counts | to_entries[] | "  \(.key): \(.value)"' "$SYNC_DATA_FILE" 2>/dev/null || echo "  (Count data unavailable)"
    else
        echo "  (Install jq for detailed file counts)"
    fi
    echo ""
    
    echo "📝 Recent Changes:"
    if command -v jq >/dev/null 2>&1; then
        jq -r '.recent_changes[]?' "$SYNC_DATA_FILE" 2>/dev/null | while read -r change; do
            echo "  - $change"
        done
    else
        git log --oneline -5 2>/dev/null | while read -r line; do
            echo "  - $line"
        done
    fi
}

# Function to sync cursor rules
sync_cursor_rules() {
    echo "🔄 Syncing cursor rules..."
    
    if [[ -f "scripts/sync-cursor-rules.sh" ]]; then
        ./scripts/sync-cursor-rules.sh sync auto
        echo "✅ Cursor rules synced"
    else
        echo "⚠️  sync-cursor-rules.sh not found"
    fi
}

# Function to validate project paths
validate_paths() {
    echo "🔍 Validating project paths..."
    
    local errors=0
    local critical_paths=(
        ".cursor/rules/globals.mdc"
        "docs/instructions/CLAUDE.md"
        "scripts/sync-cursor-rules.sh"
        "scripts/claude-cursor-sync.sh"
    )
    
    for path in "${critical_paths[@]}"; do
        if [[ -f "$path" ]]; then
            echo "✅ Found: $path"
        else
            echo "❌ Missing: $path"
            errors=$((errors + 1))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        echo "✅ All critical paths validated"
        return 0
    else
        echo "❌ Path validation failed ($errors errors)"
        return 1
    fi
}

# Function to show quick help for Cursor users
cursor_help() {
    echo "📚 Cursor User Quick Guide"
    echo "========================"
    echo ""
    echo "🔧 Common Commands:"
    echo "  ./scripts/claude-cursor-sync.sh record \"Fixed bug XYZ\""
    echo "  ./scripts/claude-cursor-sync.sh share"
    echo "  ./scripts/claude-cursor-sync.sh sync-rules"
    echo ""
    echo "📁 Important Paths:"
    echo "  .cursor/rules/    - Cursor AI rules"
    echo "  docs/instructions/ - Claude instructions" 
    echo "  scripts/          - Automation scripts"
    echo "  runtime/          - Generated data"
    echo ""
    echo "⚡ Quick Workflow:"
    echo "  1. Start work: ./scripts/claude-cursor-sync.sh share"
    echo "  2. Finish work: ./scripts/claude-cursor-sync.sh record \"What you did\""
    echo "  3. Sync rules: ./scripts/claude-cursor-sync.sh sync-rules"
}

# Function to show Claude Code integration info
claude_help() {
    echo "🤖 Claude Code Integration Guide"
    echo "==============================="
    echo ""
    echo "📡 Data Location:"
    echo "  Runtime data: $SYNC_DATA_FILE"
    echo "  Work log: $WORK_LOG_FILE"
    echo "  Project status: $PROJECT_STATUS_FILE"
    echo ""
    echo "🔗 Integration Points:"
    echo "  - Hooks: src/ai/memory/core/hooks.js"
    echo "  - Memory: src/ai/memory/core/session-bridge.sh"
    echo "  - Rules: .cursor/rules/globals.mdc"
    echo ""
    echo "⚙️ Auto-sync Features:"
    echo "  - File path resolution"
    echo "  - Work status tracking"
    echo "  - Rule synchronization"
}

# Main command handler
case "${1:-help}" in
    "record")
        message="${2:-Work session completed}"
        record_status "$message"
        ;;
    "share")
        share_status
        ;;
    "sync-rules")
        sync_cursor_rules
        record_status "Cursor rules synchronized"
        ;;
    "validate")
        validate_paths
        ;;
    "status")
        share_status
        ;;
    "cursor-help")
        cursor_help
        ;;
    "claude-help")
        claude_help
        ;;
    "paths")
        echo "📁 Current Project Paths:"
        get_project_paths | jq '.' 2>/dev/null || get_project_paths
        ;;
    "auto-record")
        # Auto-record with git status
        if git diff --quiet && git diff --cached --quiet; then
            record_status "Auto-record: No changes"
        else
            local changed_files=$(git status --porcelain | wc -l | tr -d ' ')
            record_status "Auto-record: $changed_files files changed"
        fi
        ;;
    "help"|*)
        echo "Usage: $0 {record|share|sync-rules|validate|status|paths|auto-record}"
        echo ""
        echo "Commands:"
        echo "  record <message>  - Record current work status"
        echo "  share            - Share latest status with Claude Code"
        echo "  sync-rules       - Synchronize cursor rules"
        echo "  validate         - Validate critical project paths"
        echo "  status           - Show current status (alias for share)"
        echo "  paths            - Show project path configuration"
        echo "  auto-record      - Auto-record based on git changes"
        echo ""
        echo "Help:"
        echo "  cursor-help      - Guide for Cursor users"
        echo "  claude-help      - Guide for Claude Code integration"
        echo ""
        echo "Examples:"
        echo "  $0 record \"Implemented feature X\""
        echo "  $0 share"
        echo "  $0 sync-rules"
        ;;
esac

exit 0