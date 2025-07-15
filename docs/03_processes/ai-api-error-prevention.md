# AI API エラー防止システム

**目的**: 同じAPIエラーを二度と繰り返さない仕組み構築

## 🚨 過去の失敗パターン

### Gemini API エラー（2025-07-07）
1. **CLI引数誤用**: `-c`を設定ファイルと勘違い
2. **モデル名間違い**: 存在しないモデル指定
3. **クオータ制限**: 使用量確認せず連続実行

## 🛡️ 防止システム

### 1. API実行前チェックリスト
```bash
# scripts/utilities/ai-api-check.sh
#!/bin/bash

api_pre_check() {
    echo "🔍 API実行前チェック"
    echo "1. モデル名確認済み？ [y/n]"
    echo "2. 引数・オプション確認済み？ [y/n]"
    echo "3. クオータ残量確認済み？ [y/n]"
    echo "4. エラー時の代替手段準備済み？ [y/n]"
}
```

### 2. API実行ラッパー
```bash
# 安全なGemini実行
safe_gemini() {
    local prompt="$1"
    local model="${2:-gemini-1.5-pro}"

    # 事前確認
    echo "モデル: $model"
    echo "プロンプト: ${prompt:0:50}..."
    read -p "実行しますか？ [y/n]: " confirm

    if [ "$confirm" != "y" ]; then
        echo "キャンセル"
        return 1
    fi

    # 実行
    echo "$prompt" | npx https://github.com/google-gemini/gemini-cli -m "$model"
}
```

### 3. エラーパターン辞書
| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Unknown argument` | オプション誤用 | `--help`で確認 |
| `404 Not Found` | モデル名間違い | 正確なモデル名使用 |
| `Resource exhausted` | クオータ超過 | 時間を置くかO3使用 |

### 4. 強制チェックフック
```bash
# .claude/hooks/pre-ai-api.sh
if [[ "$1" =~ "gemini\|o3\|claude" ]]; then
    ./scripts/utilities/ai-api-check.sh || exit 1
fi
```

## 📊 学習記録システム

### 失敗ログ自動記録
```bash
log_api_error() {
    local error="$1"
    local command="$2"
    echo "$(date): ERROR: $error | CMD: $command" >> runtime/api_errors.log
}
```

### 月次レビュー
- 同じエラーの再発回数
- 新しいエラーパターン
- 対策の有効性評価

---

**次回同じエラーが発生したら、このシステムの不備として扱う**
