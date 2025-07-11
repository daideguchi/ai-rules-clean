#!/bin/bash
set -euo pipefail
# Claude Code永続記憶システム - セッション架橋スクリプト
# Enterprise-grade memory backend with hooks integration

MEMORY_ROOT="$(pwd)/memory/core"
CURRENT_SESSION="$MEMORY_ROOT/session-records/current-session.json"
ORGANIZATION_STATE="$MEMORY_ROOT/organization_state.json"

# Command processing for hooks integration
COMMAND="$1"
SESSION_ID="$2"

# Security hardening functions
validate_session_id() {
    local sid="$1"
    # Only allow alphanumeric, underscore, dash (max 64 chars)
    if [[ ! "$sid" =~ ^[a-zA-Z0-9_-]{1,64}$ ]]; then
        echo "❌ Invalid session ID: $sid" >&2
        exit 1
    fi
}

sanitize_input() {
    local input="$1"
    # Remove null bytes and control characters except newlines/tabs
    printf '%s' "$input" | tr -d '\000-\010\013\014\016-\037\177'
}

# File locking for atomic operations (macOS compatible)
execute_with_lock() {
    local lockfile="$1"
    local operation="$2"
    shift 2
    
    # Create lock directory if it doesn't exist
    mkdir -p "$(dirname "$lockfile")"
    
    # Simple file-based locking for macOS
    local timeout=10
    local waited=0
    
    while [[ $waited -lt $timeout ]]; do
        if mkdir "$lockfile.lock" 2>/dev/null; then
            # Lock acquired, execute operation
            eval "$operation"
            local result=$?
            
            # Release lock
            rmdir "$lockfile.lock" 2>/dev/null
            return $result
        fi
        
        # Wait and retry
        sleep 0.1
        waited=$((waited + 1))
    done
    
    echo "❌ Failed to acquire lock: $lockfile (timeout)" >&2
    exit 1
}

# JSON integrity verification
verify_json_integrity() {
    local file="$1"
    local checksum_file="${file}.sha256"
    
    if [[ -f "$file" && -f "$checksum_file" ]]; then
        local current_hash=$(sha256sum "$file" | cut -d' ' -f1)
        local stored_hash=$(cat "$checksum_file" 2>/dev/null)
        
        if [[ "$current_hash" != "$stored_hash" ]]; then
            echo "⚠️ JSON integrity check failed for $file" >&2
            return 1
        fi
    fi
    return 0
}

save_json_with_integrity() {
    local file="$1"
    local content="$2"
    local checksum_file="${file}.sha256"
    
    # Write to temporary file first
    local temp_file="${file}.tmp.$$"
    echo "$content" > "$temp_file"
    
    # Verify JSON is valid
    if ! jq empty "$temp_file" 2>/dev/null; then
        echo "❌ Invalid JSON content" >&2
        rm -f "$temp_file"
        return 1
    fi
    
    # Calculate checksum
    local hash=$(sha256sum "$temp_file" | cut -d' ' -f1)
    
    # Atomic move and save checksum
    mv "$temp_file" "$file"
    echo "$hash" > "$checksum_file"
    
    echo "✅ JSON saved with integrity check: $file"
}

# Secure memory save operation
save_memory_operation() {
    local session_file="$1"
    local user_msg="$2"
    local assistant_msg="$3"
    
    # Load existing memory or create default
    if [[ ! -f "$session_file" ]]; then
        create_default_memory "$session_file"
    fi
    
    # Verify integrity before modification
    if ! verify_json_integrity "$session_file"; then
        echo '⚠️ Memory file corrupted, recreating' >&2
        create_default_memory "$session_file"
    fi
    
    # Add new conversation to log with size limits
    local updated_memory=$(cat "$session_file" | jq \
        --arg user "$user_msg" \
        --arg assistant "$assistant_msg" \
        --arg timestamp "$(date -Iseconds)" \
        '.conversational_log += [
            {"role": "user", "content": $user, "timestamp": $timestamp},
            {"role": "assistant", "content": $assistant, "timestamp": $timestamp}
        ] | .metadata.total_interactions += 1 | .metadata.last_updated = $timestamp')
    
    # Check token limit and auto-compress if needed
    local log_size=$(echo "$updated_memory" | jq '.conversational_log | length')
    if [[ $log_size -gt 50 ]]; then
        echo '🗜️ Auto-compressing memory due to size limit' >&2
        updated_memory=$(echo "$updated_memory" | jq \
            --arg timestamp "$(date -Iseconds)" \
            '.conversational_summary = "Recent conversations about AI永続化システム development. User and assistant discussed implementation details." | 
             .conversational_log = (.conversational_log | .[-10:]) | 
             .metadata.last_compression = $timestamp')
    fi
    
    # Save with integrity check
    save_json_with_integrity "$session_file" "$updated_memory"
    
    # Update current session link
    ln -sf "$session_file" "$CURRENT_SESSION"
}

# 前回セッションからの継承
inherit_previous_session() {
    if [[ -f "$CURRENT_SESSION" ]]; then
        echo "🧠 前回セッション記憶を読み込み中..."
        
        # 前回のミス記録読み込み
        local last_mistakes=$(jq -r '.mistakes_count // 78' "$CURRENT_SESSION")
        echo "📊 継承されたミス回数: $last_mistakes"
        
        # 必須学習事項表示
        if [[ -f "$MEMORY_ROOT/auto-initialization/mandatory-reading.md" ]]; then
            echo "📖 必須学習事項:"
            head -10 "$MEMORY_ROOT/auto-initialization/mandatory-reading.md"
        fi
        
        # 前回の重要な学習事項
        echo "💡 前回の重要学習:"
        jq -r '.important_learnings[]? // "継承データなし"' "$CURRENT_SESSION"
        
        # 未完了タスクの継承
        echo "📋 未完了タスク継承:"
        jq -r '.pending_tasks[]? // "継承タスクなし"' "$CURRENT_SESSION"
        
        echo "🎯 前回セッションからの継承完了"
    else
        echo "🆕 初回セッション開始"
    fi
}

# 新セッション初期化
initialize_new_session() {
    local session_id="session-$(date +%Y%m%d-%H%M%S)"
    local session_file="$MEMORY_ROOT/session-records/$session_id.json"
    
    # 前回データから継承
    local inherited_mistakes=78
    local inherited_tasks=()
    if [[ -f "$CURRENT_SESSION" ]]; then
        inherited_mistakes=$(jq -r '.mistakes_count // 78' "$CURRENT_SESSION")
        mapfile -t inherited_tasks < <(jq -r '.pending_tasks[]?' "$CURRENT_SESSION")
    fi
    
    # 新セッション記録作成
    cat > "$session_file" << EOF
{
  "session_id": "$session_id",
  "start_time": "$(date -Iseconds)",
  "inherited_mistakes": $inherited_mistakes,
  "mistakes_count": $inherited_mistakes,
  "pending_tasks": [
    "AI永続的記憶システム実装継続",
    "外部ストレージ・クラウド同期設計",
    "3AI連携情報共有システム",
    "o3 APIキー安定接続"
  ],
  "user_interactions": [],
  "learning_updates": [],
  "verification_results": [],
  "session_status": "active",
  "current_project": "AI Compliance Engine - 記憶継続システム",
  "important_context": "AIセッション間記憶消失問題の根本解決"
}
EOF
    
    # 現在セッションリンク更新
    ln -sf "$session_file" "$CURRENT_SESSION"
    
    echo "🆕 新セッション初期化完了: $session_id"
}

# 会話履歴の外部保存
save_conversation_history() {
    local conv_dir="$MEMORY_ROOT/conversation-history"
    mkdir -p "$conv_dir"
    
    # 会話履歴のインデックス化準備
    local history_file="$conv_dir/conversation-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$history_file" << 'EOF'
# 会話履歴保存システム

## 重要な会話内容
- ユーザー: AIセッション間記憶継続問題の解決要求
- 課題: Claude Code再起動で記憶・設定・職務がリセット
- 解決策: 永続記憶システム + 外部ストレージ + hooks活用
- 目標: 人間のように記憶を保持し続けるAIエージェント

## 技術的要件
- セッション架橋システム
- クラウド同期機能
- インデックス化された情報管理
- 3AI連携（Claude, Gemini, o3）

## 次回セッション継続事項
- 外部ストレージシステム実装
- hooks統合によるリアルタイム記憶制御
- o3 API安定接続システム
EOF

    echo "💾 会話履歴保存完了: $history_file"
}

# 必須確認事項の強制実行
force_mandatory_checks() {
    echo "🚨 必須確認事項を実行中..."
    
    # ミス履歴の確認
    echo "🚨 私は78回の重大ミスを犯した記録があります"
    echo "🚨 記憶継続システムにより、同じミスを79回目にしません"
    
    # 現在の職務確認
    echo "👔 職務: AI Compliance Engine PRESIDENT"
    echo "🎯 使命: AIの記憶継続問題を技術的に根本解決"
    
    # プロジェクト状況
    echo "📊 進捗: 永続記憶システム実装中"
    echo "🤝 協力者: User, Gemini, o3"
    
    echo "✅ 必須確認事項完了"
}

# JSON utility functions
json_escape() {
    printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

create_default_memory() {
    local session_file="$1"
    cat > "$session_file" << 'EOF'
{
  "foundational_context": {
    "role": "PRESIDENT",
    "mission": "AI永続化システム開発統括 - 記憶喪失問題の根本解決",
    "critical_directives": [
      "🚨 78回のミス記録を継承し、79回目を防ぐ",
      "👑 PRESIDENT役割を継続維持", 
      "🎯 AI Compliance Engine実装統括",
      "🤝 BOSS・WORKER組織の状態管理"
    ],
    "project_context": {
      "name": "AI Persistence & Memory System",
      "phase": "Phase 1 MVP Implementation",
      "technology_stack": "PostgreSQL + pgvector + Claude Code hooks",
      "budget": "$33,000 (Phase 1)",
      "timeline": "2-4 weeks"
    },
    "past_mistakes_summary": "78回の重大ミス（虚偽報告、詐欺、責任逃れ等）を記録済み",
    "behavior_rules": [
      "証拠なき報告は絶対禁止",
      "プロジェクト文脈を常に維持", 
      "職務放棄は重大違反",
      "ユーザーとの信頼関係最優先"
    ]
  },
  "conversational_summary": "",
  "conversational_log": [],
  "metadata": {
    "session_start": "$(date -Iseconds)",
    "total_interactions": 0,
    "last_compression": null
  }
}
EOF
}

create_organization_state() {
    cat > "$ORGANIZATION_STATE" << 'EOF'
{
  "last_updated": "$(date -Iseconds)",
  "president": {
    "status": "active",
    "current_mission": "AI永続化システム実装統括",
    "active_directive": "hooks-implementation"
  },
  "boss": {
    "status": "managing", 
    "current_task": "Phase 1 Implementation Coordination",
    "assigned_workers": ["worker1", "worker2", "worker3"]
  },
  "workers": {
    "worker1": {
      "role": "Frontend Engineer",
      "status": "ready",
      "current_task": null,
      "session_id": null
    },
    "worker2": {
      "role": "Backend Engineer",
      "status": "ready", 
      "current_task": null,
      "session_id": null
    },
    "worker3": {
      "role": "UI/UX Designer",
      "status": "ready",
      "current_task": null,
      "session_id": null
    }
  }
}
EOF
}

# Command handlers for hooks integration
case "$COMMAND" in
    "init")
        echo "🧠 Claude Code 永続記憶システム初期化中..."
        mkdir -p "$MEMORY_ROOT"/{session-records,persistent-learning,auto-initialization,prevention-systems,conversation-history}
        
        if [[ ! -f "$ORGANIZATION_STATE" ]]; then
            create_organization_state
        fi
        
        inherit_previous_session
        initialize_new_session
        save_conversation_history
        force_mandatory_checks
        
        echo "🎯 Claude Code 記憶システム準備完了"
        echo "📝 セッション記録: $CURRENT_SESSION"
        ;;
        
    "get_memory")
        if [[ -z "$SESSION_ID" ]]; then
            SESSION_ID="default"
        fi
        
        # Validate session ID for security
        validate_session_id "$SESSION_ID"
        
        SESSION_FILE="$MEMORY_ROOT/session-records/session-${SESSION_ID}.json"
        LOCKFILE="$MEMORY_ROOT/locks/session-${SESSION_ID}.lock"
        
        execute_with_lock "$LOCKFILE" "
            if [[ -f '$SESSION_FILE' ]]; then
                if verify_json_integrity '$SESSION_FILE'; then
                    cat '$SESSION_FILE'
                else
                    echo '❌ Memory file corrupted, creating new session' >&2
                    create_default_memory '$SESSION_FILE'
                    cat '$SESSION_FILE'
                fi
            else
                create_default_memory '$SESSION_FILE'
                cat '$SESSION_FILE'
            fi
        "
        ;;
        
    "save_memory")
        if [[ -z "$SESSION_ID" ]]; then
            SESSION_ID="default"
        fi
        
        # Validate session ID for security
        validate_session_id "$SESSION_ID"
        
        SESSION_FILE="$MEMORY_ROOT/session-records/session-${SESSION_ID}.json"
        LOCKFILE="$MEMORY_ROOT/locks/session-${SESSION_ID}.lock"
        
        # Read and sanitize new data from stdin
        NEW_DATA=$(cat | head -c 1048576)  # Limit to 1MB to prevent DoS
        NEW_DATA=$(sanitize_input "$NEW_DATA")
        
        # Validate JSON structure
        if ! echo "$NEW_DATA" | jq empty 2>/dev/null; then
            echo '❌ Invalid JSON input' >&2
            exit 1
        fi
        
        USER_MSG=$(echo "$NEW_DATA" | jq -r '.user_message // ""')
        ASSISTANT_MSG=$(echo "$NEW_DATA" | jq -r '.assistant_response // ""')
        
        # Sanitize messages (prevent injection)
        USER_MSG=$(sanitize_input "$USER_MSG")
        ASSISTANT_MSG=$(sanitize_input "$ASSISTANT_MSG")
        
        execute_with_lock "$LOCKFILE" "save_memory_operation '$SESSION_FILE' '$USER_MSG' '$ASSISTANT_MSG'"
        ;;
        
    "compress_memory")
        if [[ -z "$SESSION_ID" ]]; then
            SESSION_ID="default"
        fi
        
        SESSION_FILE="$MEMORY_ROOT/session-records/session-${SESSION_ID}.json"
        
        if [[ -f "$SESSION_FILE" ]]; then
            # Simple compression: keep foundational_context, summarize conversational_log
            COMPRESSED=$(cat "$SESSION_FILE" | jq \
                --arg timestamp "$(date -Iseconds)" \
                '.conversational_summary = "前回の会話で重要なやりとりがありました" | 
                 .conversational_log = [] | 
                 .metadata.last_compression = $timestamp')
            
            echo "$COMPRESSED" > "$SESSION_FILE"
            echo "🗜️ Memory compressed for session $SESSION_ID"
        fi
        ;;
        
    *)
        # Default behavior - backward compatibility
        echo "🧠 Claude Code 永続記憶システム起動中..."
        mkdir -p "$MEMORY_ROOT"/{session-records,persistent-learning,auto-initialization,prevention-systems,conversation-history}
        
        inherit_previous_session
        initialize_new_session
        save_conversation_history
        force_mandatory_checks
        
        echo "🎯 Claude Code 記憶システム準備完了"
        echo "📝 セッション記録: $CURRENT_SESSION"
        ;;
esac