#!/bin/bash
# Audio Hooks 音響・音声機能の簡単切り替え

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/src/hooks/hooks-config.json"

show_usage() {
    echo "🔊 Audio Hooks 切り替えツール"
    echo ""
    echo "使用方法:"
    echo "  $0 sound on|off     # 音響効果の有効/無効"
    echo "  $0 tts on|off       # 音声読み上げの有効/無効"
    echo "  $0 all on|off       # 全音響機能の有効/無効"
    echo "  $0 status           # 現在の設定表示"
    echo ""
    echo "例:"
    echo "  $0 sound on         # 音響効果を有効にする"
    echo "  $0 all off          # 全音響機能を無効にする"
}

get_current_setting() {
    local key="$1"
    python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
print(str(config['audio_hooks']['${key}']).lower())
"
}

update_setting() {
    local key="$1"
    local value="$2"
    
    python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

config['audio_hooks']['${key}'] = ${value}

with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
}

show_status() {
    echo "🔊 Audio Hooks 現在の設定:"
    echo ""
    
    sound_status=$(get_current_setting "sound_enabled")
    tts_status=$(get_current_setting "tts_enabled")
    logging_status=$(get_current_setting "logging_enabled")
    
    if [ "$sound_status" = "true" ]; then
        echo "   🎵 音響効果: ✅ 有効"
    else
        echo "   🎵 音響効果: ❌ 無効"
    fi
    
    if [ "$tts_status" = "true" ]; then
        echo "   🗣️  音声読み上げ: ✅ 有効"
    else
        echo "   🗣️  音声読み上げ: ❌ 無効"
    fi
    
    if [ "$logging_status" = "true" ]; then
        echo "   📝 ログ記録: ✅ 有効"
    else
        echo "   📝 ログ記録: ❌ 無効"
    fi
    
    echo ""
    echo "📋 ログファイル:"
    
    if [ -f "$PROJECT_ROOT/FILE_OPERATIONS_LOG.md" ]; then
        op_count=$(grep -c "^-" "$PROJECT_ROOT/FILE_OPERATIONS_LOG.md" 2>/dev/null || echo "0")
        echo "   📄 FILE_OPERATIONS_LOG.md: ${op_count}件"
    else
        echo "   📄 FILE_OPERATIONS_LOG.md: なし"
    fi
    
    if [ -f "$PROJECT_ROOT/AI_INTERACTIONS_LOG.md" ]; then
        ai_count=$(grep -c "^-" "$PROJECT_ROOT/AI_INTERACTIONS_LOG.md" 2>/dev/null || echo "0")
        echo "   🤖 AI_INTERACTIONS_LOG.md: ${ai_count}件"
    else
        echo "   🤖 AI_INTERACTIONS_LOG.md: なし"
    fi
}

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    "sound")
        if [ "$2" = "on" ]; then
            update_setting "sound_enabled" "True"
            echo "🎵 音響効果を有効にしました"
        elif [ "$2" = "off" ]; then
            update_setting "sound_enabled" "False"
            echo "🔇 音響効果を無効にしました"
        else
            echo "❌ sound は on または off を指定してください"
            exit 1
        fi
        ;;
    "tts")
        if [ "$2" = "on" ]; then
            update_setting "tts_enabled" "True"
            echo "🗣️  音声読み上げを有効にしました"
        elif [ "$2" = "off" ]; then
            update_setting "tts_enabled" "False"
            echo "🔇 音声読み上げを無効にしました"
        else
            echo "❌ tts は on または off を指定してください"
            exit 1
        fi
        ;;
    "all")
        if [ "$2" = "on" ]; then
            update_setting "sound_enabled" "True"
            update_setting "tts_enabled" "True"
            echo "🔊 全音響機能を有効にしました"
        elif [ "$2" = "off" ]; then
            update_setting "sound_enabled" "False"
            update_setting "tts_enabled" "False"
            echo "🔇 全音響機能を無効にしました"
        else
            echo "❌ all は on または off を指定してください"
            exit 1
        fi
        ;;
    "status")
        show_status
        ;;
    *)
        echo "❌ 不明なコマンド: $1"
        show_usage
        exit 1
        ;;
esac