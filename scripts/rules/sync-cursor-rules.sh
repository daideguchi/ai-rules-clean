#!/bin/bash
# Cursor Rules Synchronization System
# Auto-sync between .cursor/rules and project structure

set -euo pipefail

echo "🔄 Cursor Rules Synchronization System"

# Configuration
CURSOR_RULES_DIR=".cursor/rules"
SOURCE_RULES_DIR="cursor-rules"
BACKUP_DIR=".cursor/rules-backup"
SYNC_LOG="runtime/logs/cursor-sync.log"

# Ensure directories exist
mkdir -p "$BACKUP_DIR" "$(dirname "$SYNC_LOG")" runtime/logs

# Function to create backup
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/rules_$timestamp"
    
    if [[ -d "$CURSOR_RULES_DIR" ]]; then
        cp -r "$CURSOR_RULES_DIR" "$backup_path"
        echo "📦 Backup created: $backup_path"
    fi
}

# Function to show diff
show_diff() {
    echo "📊 Checking differences..."
    
    if [[ -d "$SOURCE_RULES_DIR" && -d "$CURSOR_RULES_DIR" ]]; then
        if diff -r "$SOURCE_RULES_DIR" "$CURSOR_RULES_DIR" > /dev/null 2>&1; then
            echo "✅ No differences found"
            return 0
        else
            echo "🔍 Differences detected:"
            diff -r "$SOURCE_RULES_DIR" "$CURSOR_RULES_DIR" || true
            return 1
        fi
    else
        echo "⚠️  One or both directories missing"
        return 1
    fi
}

# Function to sync rules
sync_rules() {
    local direction="$1"
    
    case "$direction" in
        "to-cursor")
            echo "🔄 Syncing: $SOURCE_RULES_DIR → $CURSOR_RULES_DIR"
            create_backup
            mkdir -p "$CURSOR_RULES_DIR"
            rsync -av --delete "$SOURCE_RULES_DIR/" "$CURSOR_RULES_DIR/"
            ;;
        "from-cursor")
            echo "🔄 Syncing: $CURSOR_RULES_DIR → $SOURCE_RULES_DIR"
            mkdir -p "$SOURCE_RULES_DIR"
            rsync -av --delete "$CURSOR_RULES_DIR/" "$SOURCE_RULES_DIR/"
            ;;
        *)
            echo "❌ Invalid direction: $direction"
            exit 1
            ;;
    esac
    
    echo "✅ Sync completed"
}

# Function to validate rules
validate_rules() {
    echo "🔍 Validating cursor rules..."
    
    local errors=0
    
    # Check required files
    local required_files=(
        "$CURSOR_RULES_DIR/globals.mdc"
        "$CURSOR_RULES_DIR/work-log.mdc"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "❌ Missing required file: $file"
            errors=$((errors + 1))
        else
            echo "✅ Found: $file"
        fi
    done
    
    # Validate syntax of .mdc files
    find "$CURSOR_RULES_DIR" -name "*.mdc" -type f | while read -r file; do
        if [[ -s "$file" ]]; then
            echo "✅ Valid: $file"
        else
            echo "⚠️  Empty file: $file"
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        echo "✅ Validation passed"
        return 0
    else
        echo "❌ Validation failed with $errors errors"
        return 1
    fi
}

# Function to auto-detect changes and sync
auto_sync() {
    echo "🤖 Auto-sync mode activated"
    
    # Check which directory has newer changes
    if [[ -d "$SOURCE_RULES_DIR" && -d "$CURSOR_RULES_DIR" ]]; then
        local source_newer=$(find "$SOURCE_RULES_DIR" -newer "$CURSOR_RULES_DIR/globals.mdc" 2>/dev/null | wc -l)
        local cursor_newer=$(find "$CURSOR_RULES_DIR" -newer "$SOURCE_RULES_DIR/globals.mdc" 2>/dev/null | wc -l)
        
        if [[ $source_newer -gt 0 ]]; then
            echo "📈 Source rules are newer, syncing to cursor"
            sync_rules "to-cursor"
        elif [[ $cursor_newer -gt 0 ]]; then
            echo "📈 Cursor rules are newer, syncing from cursor"
            sync_rules "from-cursor"
        else
            echo "✅ Rules are in sync"
        fi
    elif [[ -d "$SOURCE_RULES_DIR" ]]; then
        echo "📁 Source rules exist, syncing to cursor"
        sync_rules "to-cursor"
    elif [[ -d "$CURSOR_RULES_DIR" ]]; then
        echo "📁 Cursor rules exist, syncing from cursor"
        sync_rules "from-cursor"
    else
        echo "❌ No rules directories found"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo "📊 Cursor Rules Status"
    echo "===================="
    
    echo "📁 Directories:"
    echo "  Source: $SOURCE_RULES_DIR $([ -d "$SOURCE_RULES_DIR" ] && echo "✅" || echo "❌")"
    echo "  Cursor: $CURSOR_RULES_DIR $([ -d "$CURSOR_RULES_DIR" ] && echo "✅" || echo "❌")"
    echo "  Backup: $BACKUP_DIR $([ -d "$BACKUP_DIR" ] && echo "✅" || echo "❌")"
    
    if [[ -d "$CURSOR_RULES_DIR" ]]; then
        echo ""
        echo "📄 Cursor Rules Files:"
        find "$CURSOR_RULES_DIR" -name "*.mdc" -type f | while read -r file; do
            local size=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  - $(basename "$file"): $size lines"
        done
    fi
    
    if [[ -d "$BACKUP_DIR" ]]; then
        echo ""
        echo "💾 Recent Backups:"
        ls -1t "$BACKUP_DIR" | head -3 | while read -r backup; do
            echo "  - $backup"
        done
    fi
    
    echo ""
    echo "🕐 Last sync: $([ -f "$SYNC_LOG" ] && tail -1 "$SYNC_LOG" | cut -d' ' -f1-2 || echo "Never")"
}

# Function to log sync operations
log_sync() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$SYNC_LOG"
}

# Main command handler
case "${1:-help}" in
    "status")
        show_status
        ;;
    "diff")
        show_diff
        ;;
    "sync")
        direction="${2:-auto}"
        if [[ "$direction" == "auto" ]]; then
            auto_sync
        else
            sync_rules "$direction"
        fi
        log_sync "Manual sync: $direction"
        ;;
    "validate")
        validate_rules
        ;;
    "backup")
        create_backup
        log_sync "Manual backup created"
        ;;
    "watch")
        echo "👀 Watching for changes... (Press Ctrl+C to stop)"
        while true; do
            if ! show_diff > /dev/null 2>&1; then
                echo "🔄 Changes detected, auto-syncing..."
                auto_sync
                log_sync "Auto-sync triggered by file change"
            fi
            sleep 5
        done
        ;;
    "help"|*)
        echo "Usage: $0 {status|diff|sync|validate|backup|watch}"
        echo ""
        echo "Commands:"
        echo "  status    - Show current status"
        echo "  diff      - Show differences between directories"
        echo "  sync      - Sync rules (auto|to-cursor|from-cursor)"
        echo "  validate  - Validate cursor rules syntax"
        echo "  backup    - Create manual backup"
        echo "  watch     - Auto-sync on file changes"
        echo ""
        echo "Examples:"
        echo "  $0 status"
        echo "  $0 sync auto"
        echo "  $0 sync to-cursor"
        echo "  $0 watch"
        ;;
esac

exit 0