#!/bin/bash
# Audio Hooks System セットアップスクリプト
# 音響効果・音声読み上げ・記録システムの自動設定

set -euo pipefail

echo "🔊 Audio Hooks System セットアップ開始"

PROJECT_ROOT="${PROJECT_ROOT}"
HOOKS_DIR="$PROJECT_ROOT/src/hooks"
SOUNDS_DIR="$PROJECT_ROOT/assets/sounds"

# 1. 必要ディレクトリ作成
echo "📁 ディレクトリ構造作成中..."
mkdir -p "$SOUNDS_DIR"
mkdir -p "$PROJECT_ROOT/runtime/hooks-logs"

# 2. サウンドファイル生成
echo "🎵 優しい音響効果生成中..."

# SoXがインストールされているかチェック
if command -v sox &> /dev/null; then
    echo "   ✅ SoX検出 - カスタム音響効果を生成"
    
    # 優しいファイル作成音 (800Hz, 0.3秒)
    sox -n "$SOUNDS_DIR/gentle_create.wav" synth 0.3 sine 800 fade 0.1 0.3 0.1 vol 0.3
    
    # ソフトなファイル変更音 (600Hz, 0.2秒)  
    sox -n "$SOUNDS_DIR/soft_modify.wav" synth 0.2 sine 600 fade 0.05 0.2 0.05 vol 0.3
    
    # 優しい削除音 (400Hz, 0.4秒、フェードアウト長め)
    sox -n "$SOUNDS_DIR/gentle_delete.wav" synth 0.4 sine 400 fade 0.1 0.4 0.2 vol 0.3
    
    # 成功チャイム (1000Hz->1200Hz, 0.3秒)
    sox -n "$SOUNDS_DIR/success_chime.wav" synth 0.3 sine 1000:1200 fade 0.1 0.3 0.1 vol 0.4
    
    # 優しいエラー音 (300Hz->200Hz, 0.5秒)
    sox -n "$SOUNDS_DIR/gentle_error.wav" synth 0.5 sine 300:200 fade 0.1 0.5 0.2 vol 0.3
    
    # 検証ビープ (短いチャイム)
    sox -n "$SOUNDS_DIR/validation_beep.wav" synth 0.15 sine 900 fade 0.02 0.15 0.02 vol 0.4
    
    echo "   🎼 6個の音響効果ファイル生成完了"
    
else
    echo "   ⚠️  SoXが見つかりません - デフォルト音響効果をスキップ"
    echo "   💡 インストール: brew install sox (macOS) または apt install sox (Linux)"
fi

# 3. TTS（音声読み上げ）環境確認
echo "🗣️  TTS環境確認中..."

if command -v say &> /dev/null; then
    echo "   ✅ macOS say コマンド検出"
    TTS_AVAILABLE=true
elif command -v espeak-ng &> /dev/null; then
    echo "   ✅ espeak-ng 検出"
    TTS_AVAILABLE=true
elif command -v spd-say &> /dev/null; then
    echo "   ✅ Speech Dispatcher 検出"
    TTS_AVAILABLE=true
else
    echo "   ⚠️  TTS コマンドが見つかりません"
    echo "   💡 インストール推奨:"
    echo "      - macOS: 標準搭載 (say)"
    echo "      - Linux: apt install espeak-ng"
    TTS_AVAILABLE=false
fi

# 4. 設定ファイル更新
echo "⚙️  設定ファイル更新中..."

# TTS設定を環境に応じて更新
if [ "$TTS_AVAILABLE" = true ]; then
    # TTSを有効化（オプション）
    echo "   💭 TTS機能が利用可能です（デフォルトは無効）"
    echo "   🔧 有効化するには hooks-config.json で tts_enabled: true に設定"
else
    echo "   📝 TTS無効で設定を維持"
fi

# 5. Python環境確認
echo "🐍 Python環境確認中..."

if python3 -c "import threading, subprocess, json" 2>/dev/null; then
    echo "   ✅ 必要なPythonモジュール確認完了"
else
    echo "   ❌ 必要なPythonモジュールが不足しています"
    exit 1
fi

# 6. 統合テスト実行
echo "🧪 統合テスト実行中..."

cd "$PROJECT_ROOT"

# Hooks システムテスト
if python3 src/hooks/audio-hooks-system.py; then
    echo "   ✅ Audio Hooks System 正常動作"
else
    echo "   ❌ Audio Hooks System テスト失敗"
    exit 1
fi

# 7. 既存システムとの統合
echo "🔗 既存システム統合中..."

# ファイル検証システムとの統合
if [ -f "$PROJECT_ROOT/scripts/validate-file-creation.py" ]; then
    echo "   🔧 ファイル検証システムにhooks統合を追加"
    
    # 統合コード追加（既存ファイルの末尾に追加）
    cat >> "$PROJECT_ROOT/scripts/validate-file-creation.py" << 'EOF'

# === Audio Hooks Integration ===
try:
    import sys
    sys.path.append('src/hooks')
    from audio_hooks_system import emit_validation_result
    
    def emit_validation_hook(path: str, passed: bool, details: dict = None):
        """検証結果をhooksシステムに送信"""
        emit_validation_result(path, passed, details or {})
        
except ImportError:
    def emit_validation_hook(path: str, passed: bool, details: dict = None):
        pass  # フォールバック：何もしない
EOF
    
    echo "   ✅ ファイル検証システム統合完了"
fi

# 8. 起動スクリプト作成
echo "🚀 起動スクリプト作成中..."

cat > "$PROJECT_ROOT/start-with-hooks.sh" << 'EOF'
#!/bin/bash
# Hooks付きプロジェクト起動

export HOOKS_ENABLED=true
export AUDIO_HOOKS_CONFIG="src/hooks/hooks-config.json"

echo "🔊 Audio Hooks System 有効化"
echo "📝 ファイル操作ログ: FILE_OPERATIONS_LOG.md"
echo "🤖 AI相互作用ログ: AI_INTERACTIONS_LOG.md"
echo ""

# プロジェクト起動
exec "$@"
EOF

chmod +x "$PROJECT_ROOT/start-with-hooks.sh"

# 9. 設定サマリー表示
echo ""
echo "✅ Audio Hooks System セットアップ完了！"
echo ""
echo "📊 セットアップサマリー:"
echo "   🎵 音響効果: $(ls -1 "$SOUNDS_DIR"/*.wav 2>/dev/null | wc -l)個のサウンドファイル"
echo "   🗣️  TTS機能: $TTS_AVAILABLE"
echo "   📝 ログファイル: 2個（最上位ディレクトリ）"
echo "   🔧 設定ファイル: src/hooks/hooks-config.json"
echo ""
echo "🚀 使用方法:"
echo "   基本: python3 src/hooks/audio-hooks-system.py"
echo "   統合: ./start-with-hooks.sh [command]"
echo ""
echo "⚙️  設定カスタマイズ:"
echo "   - 音量調整: hooks-config.json の volume"
echo "   - TTS有効化: hooks-config.json の tts_enabled"
echo "   - 音響効果無効化: hooks-config.json の sound_enabled"
echo ""
echo "📋 ログファイル:"
echo "   - FILE_OPERATIONS_LOG.md (ファイル操作記録)"
echo "   - AI_INTERACTIONS_LOG.md (AI相互作用記録)"

echo ""
echo "🎉 優しい音でファイル操作をお楽しみください！"