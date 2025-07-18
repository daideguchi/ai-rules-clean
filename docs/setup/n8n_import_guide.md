# 🔄 n8n ワークフロー インポートガイド

## 📋 インポート方法 (3つの選択肢)

### 🌐 方法1: Web UI経由 (推奨・最簡単)

#### ステップ1: n8n にログイン
```
https://n8n.cloud にアクセス
または
自己ホスト版: http://localhost:5678
```

#### ステップ2: ワークフロー作成
1. 「**+ New Workflow**」をクリック
2. 右上の「**・・・**」メニューをクリック
3. 「**Import from File**」を選択

#### ステップ3: ファイル選択
```
config/n8n/workflows/ai_performance_tracker.json
config/n8n/workflows/autonomous_prompt_evolution.json
```
の2ファイルを順番にインポート

#### ステップ4: 設定確認
- **Webhook URL** を確認・コピー
- **Database接続** を設定
- **API認証** を設定

---

### 🚀 方法2: API経由 (自動化)

#### 前提: API キー取得
```bash
# n8n Web UI > User Settings > API Keys で生成
export N8N_API_KEY="your_api_key_here"
export N8N_BASE_URL="https://n8n.cloud"  # または自己ホストURL
```

#### インポート実行
```bash
# Performance Tracker ワークフロー
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/import" \
  -H "Authorization: Bearer ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @config/n8n/workflows/ai_performance_tracker.json

# Prompt Evolution ワークフロー  
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/import" \
  -H "Authorization: Bearer ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @config/n8n/workflows/autonomous_prompt_evolution.json
```

---

### 💻 方法3: CLI (n8n CLI使用)

#### 前提: n8n CLI インストール
```bash
npm install -g n8n-cli
```

#### インポート実行
```bash
# ワークフロー作成
n8n import workflow config/n8n/workflows/ai_performance_tracker.json
n8n import workflow config/n8n/workflows/autonomous_prompt_evolution.json
```

---

## ⚙️ インポート後の設定

### 🔗 1. Webhook URL設定

**Performance Tracker ワークフロー**:
```bash
# インポート後、webhook URLをコピー
# 例: https://n8n.cloud/webhook/claude-performance

# 環境変数に設定
export N8N_WEBHOOK_URL="https://n8n.cloud/webhook/claude-performance"
echo 'export N8N_WEBHOOK_URL="https://n8n.cloud/webhook/claude-performance"' >> ~/.bashrc
```

### 🗄️ 2. データベース接続設定

**SQLite接続** (推奨):
```json
{
  "name": "AI Growth Database",
  "type": "sqlite",
  "database": "/path/to/coding-rule2/runtime/memory/ai_growth.db"
}
```

**PostgreSQL接続** (オプション):
```json
{
  "name": "PostgreSQL Connection", 
  "type": "postgres",
  "host": "localhost",
  "port": 5432,
  "database": "ai_growth",
  "username": "your_username",
  "password": "your_password"
}
```

### 🔐 3. 認証情報設定

**n8n Credentials追加**:
1. Settings > Credentials
2. 「+ Add Credential」
3. 以下を追加:
   - **HTTP Request**: Claude Code API用
   - **SQLite**: データベース用
   - **Webhook**: 受信用

---

## 🧪 動作確認

### テスト1: Webhook接続確認
```bash
# webhook URLにテストデータ送信
curl -X POST "${N8N_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_001",
    "success": true,
    "execution_time": 2.5,
    "tools_used": ["Read", "Edit"],
    "task_complexity": "simple"
  }'
```

### テスト2: ワークフロー実行確認
```bash
# n8n Web UI > Executions で実行履歴確認
# または API経由で確認
curl -H "Authorization: Bearer ${N8N_API_KEY}" \
  "${N8N_BASE_URL}/api/v1/executions"
```

### テスト3: データベース確認
```bash
# SQLite データベース確認
sqlite3 runtime/memory/ai_growth.db "SELECT COUNT(*) FROM ai_performance_log;"
```

---

## 📚 ワークフロー詳細

### 🎯 AI Performance Tracker
- **トリガー**: Webhook (Claude Code Hook)
- **処理**: パフォーマンス解析 + パターン検出
- **出力**: SQLiteデータベース + 学習シグナル

### 🧬 Autonomous Prompt Evolution  
- **トリガー**: Cron (日次 02:00)
- **処理**: パターン分析 + CLAUDE.md進化
- **出力**: 進化ログ + パフォーマンス検証

---

## 🚨 トラブルシューティング

### よくあるエラー

**❌ "Import failed: Invalid JSON"**
```bash
# JSON形式確認
cat config/n8n/workflows/ai_performance_tracker.json | jq .
```

**❌ "Database connection failed"**
```bash
# SQLiteファイル確認
ls -la runtime/memory/ai_growth.db

# パーミッション確認
chmod 644 runtime/memory/ai_growth.db
```

**❌ "Webhook URL not accessible"**
```bash
# ネットワーク確認
curl -I "${N8N_WEBHOOK_URL}"

# n8n ワークフロー有効化確認
# Web UI > Workflows > Status: Active
```

---

## 🎯 次のステップ

### 1. Claude Code Hook統合
```bash
# .claude/settings.json に追加
echo '
{
  "hooks": {
    "session_start": "python3 scripts/hooks/autonomous_growth_hook.py session_start",
    "tool_use_post": "python3 scripts/hooks/autonomous_growth_hook.py tool_use_post"
  }
}' > ~/.claude/settings.json
```

### 2. 環境変数設定
```bash
export AUTONOMOUS_GROWTH_ENABLED=true
export PROJECT_ROOT="/Users/dd/Desktop/1_dev/coding-rule2"
```

### 3. 初回実行
```bash
# 成長エンジン初期化
python3 src/ai/autonomous_growth_engine.py

# フック動作テスト
python3 scripts/hooks/autonomous_growth_hook.py test
```

---

**🚀 これで自律AI成長システムが稼働開始！Claude Codeを使うたびにAIが賢くなります。**