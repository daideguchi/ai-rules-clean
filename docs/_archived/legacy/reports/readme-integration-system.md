# 🚀 AI組織 GitHub + MCP 統合システム

## 🎯 概要

AI組織システムとGitHub Issues、MCPプロトコルを完全統合した革新的なワークフローシステムです。tmux + Claude Codeの既存環境と連携し、4ワーカーによる並列Issue処理を実現します。

## 🏗️ システム アーキテクチャ

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub        │    │  MCP Protocol    │    │  tmux + Claude  │
│   Issues        │◄──►│  Integration     │◄──►│  AI Organization│
│                 │    │  Bridge          │    │  4 Workers      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────▼─────────┐              │
         │              │ Realtime Sync     │              │
         └─────────────►│ Daemon            │◄─────────────┘
                        │ Event Processing  │
                        └───────────────────┘
```

## 📋 コンポーネント

### 1. **メイン統合システム** (`AI_GITHUB_MCP_INTEGRATION.sh`)
- システム全体の初期化・起動・停止
- MCP/GitHub/tmux の設定統合
- Webhookサーバー管理

### 2. **並列ワークフローエンジン** (`PARALLEL_WORKFLOW_ENGINE.sh`)
- 4ワーカー並列Issue処理
- AI駆動最適割り当てアルゴリズム
- リアルタイム進捗監視

### 3. **Claude Code + MCP ブリッジ** (`CLAUDE_MCP_BRIDGE.py`)
- MCPプロトコル統合
- WebSocket API サーバー
- AI組織ステータス管理

### 4. **リアルタイム同期デーモン** (`REALTIME_SYNC_DAEMON.py`)
- GitHub ↔ tmux ↔ AI組織の完全同期
- イベント駆動アーキテクチャ
- 競合解決メカニズム

## 🚀 セットアップ手順

### Phase 1: 初期設定
```bash
# 1. 統合システム初期化
./ai-agents/AI_GITHUB_MCP_INTEGRATION.sh init

# 2. GitHub CLI認証
gh auth login

# 3. 並列ワークフローエンジン初期化
./ai-agents/PARALLEL_WORKFLOW_ENGINE.sh init
```

### Phase 2: システム起動
```bash
# 1. AI組織システム起動
./ai-agents/manage.sh claude-auth

# 2. 統合システム起動
./ai-agents/AI_GITHUB_MCP_INTEGRATION.sh start

# 3. リアルタイム同期デーモン起動
python3 ./ai-agents/REALTIME_SYNC_DAEMON.py &

# 4. Claude MCP ブリッジ起動
python3 ./ai-agents/CLAUDE_MCP_BRIDGE.py &
```

## 🔄 ワークフロー

### 自動Issue処理フロー
```
1. GitHub Issue作成
   ↓
2. AI分析・最適ワーカー選択
   ↓
3. tmuxペインに自動割り当て
   ↓
4. Claude Codeで並列処理
   ↓
5. リアルタイム進捗同期
   ↓
6. 自動完了・クローズ
```

### ワーカー専門分野
```
👑 BOSS (multiagent:0.0)      - プロジェクト管理・調整
💻 WORKER1 (multiagent:0.1)   - フロントエンド開発
⚙️ WORKER2 (multiagent:0.2)   - バックエンド開発
🎨 WORKER3 (multiagent:0.3)   - UI/UXデザイン
```

## 🛠️ 主要機能

### 1. **AI駆動自動割り当て**
- Issue内容・ラベル解析
- ワーカー専門性マッチング
- 負荷分散最適化

### 2. **並列処理システム**
- 最大4件同時処理
- 依存関係自動解決
- プライオリティキュー管理

### 3. **リアルタイム同期**
- GitHub ↔ tmux 双方向同期
- イベント駆動更新
- 競合自動解決

### 4. **MCP統合**
- WebSocket API (port 8765)
- Claude Code拡張
- プロトコル標準準拠

## 📊 使用方法

### Issue自動処理
```bash
# 単一Issue割り当て
./ai-agents/tmux_github_bridge.sh assign 123

# 一括処理
./ai-agents/PARALLEL_WORKFLOW_ENGINE.sh bulk

# 進捗監視
./ai-agents/PARALLEL_WORKFLOW_ENGINE.sh dashboard
```

### システム状況確認
```bash
# 全体状況
./ai-agents/AI_GITHUB_MCP_INTEGRATION.sh status

# ワーカー詳細
./ai-agents/tmux_github_bridge.sh status

# 並列処理監視
./ai-agents/PARALLEL_WORKFLOW_ENGINE.sh monitor
```

### MCP API使用例
```python
import asyncio
import websockets
import json

async def call_mcp_api():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Issue一覧取得
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "github/list_issues",
            "params": {"state": "open"}
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        print(json.loads(response))
```

## 🔧 設定ファイル

### MCP設定 (`mcp/claude_code_config.json`)
```json
{
  "mcp": {
    "servers": {
      "github-ai-organization": {
        "command": "python3",
        "args": ["./mcp/tools/github_integration.py"]
      }
    }
  },
  "tools": {
    "github": {"enabled": true, "auto_assign": true},
    "tmux": {"enabled": true, "auto_status_update": true}
  }
}
```

### ワーカー設定 (`workflow_state.json`)
```json
{
  "workers": {
    "boss": {
      "specialization": "management",
      "status": "idle",
      "current_issue": null
    }
  },
  "metrics": {
    "total_processed": 0,
    "success_rate": 100
  }
}
```

## 📈 監視・メトリクス

### ダッシュボード
```bash
# リアルタイムダッシュボード起動
./ai-agents/PARALLEL_WORKFLOW_ENGINE.sh dashboard
```

### ログ監視
```bash
# 統合ログ
tail -f ai-agents/logs/integration-*.log

# 同期イベント
tail -f ai-agents/logs/sync_events.jsonl

# ワークフロー
tail -f ai-agents/logs/workflow-*.log
```

### パフォーマンス指標
- **処理スループット**: 4件/時間 (並列処理時)
- **平均応答時間**: 2-5分/Issue
- **成功率**: >95%
- **同期遅延**: <3秒

## 🚨 トラブルシューティング

### よくある問題

#### 1. MCP接続エラー
```bash
# MCPブリッジ再起動
pkill -f CLAUDE_MCP_BRIDGE.py
python3 ./ai-agents/CLAUDE_MCP_BRIDGE.py &
```

#### 2. GitHub API制限
```bash
# レート制限確認
gh api rate_limit

# 制限回避 (間隔調整)
export GITHUB_API_DELAY=2
```

#### 3. tmuxセッション問題
```bash
# セッション再作成
./ai-agents/manage.sh clean
./ai-agents/manage.sh claude-auth
```

#### 4. 同期不整合
```bash
# 同期デーモン再起動
pkill -f REALTIME_SYNC_DAEMON.py
python3 ./ai-agents/REALTIME_SYNC_DAEMON.py &
```

### ログ分析
```bash
# エラーログ抽出
grep -i error ai-agents/logs/*.log

# 同期イベント分析
jq '.event_type' ai-agents/logs/sync_events.jsonl | sort | uniq -c

# ワーカー利用率
jq '.workers[].status' ai-agents/workflow_state.json
```

## 🔄 運用

### 日次運用
```bash
# システム状況確認
./ai-agents/AI_GITHUB_MCP_INTEGRATION.sh status

# ログローテーション
find ai-agents/logs -name "*.log" -mtime +7 -exec gzip {} \;

# 統計レポート
./ai-agents/PARALLEL_WORKFLOW_ENGINE.sh status
```

### 週次メンテナンス
```bash
# バックアップ
tar -czf ai-agents-backup-$(date +%Y%m%d).tar.gz ai-agents/

# パフォーマンス最適化
./ai-agents/AI_GITHUB_MCP_INTEGRATION.sh optimize

# システム更新
git pull && ./ai-agents/AI_GITHUB_MCP_INTEGRATION.sh restart
```

## 🎯 最適化ポイント

### パフォーマンス向上
1. **並列度調整**: max_parallel設定
2. **API間隔**: GitHub制限対応
3. **メモリ使用**: 長時間実行最適化
4. **ネットワーク**: 接続プール活用

### 信頼性向上
1. **エラーハンドリング**: 例外処理強化
2. **リトライロジック**: 自動復旧
3. **ヘルスチェック**: システム監視
4. **データ整合性**: 同期検証

## 📞 サポート

### 設定ファイル
- **統合設定**: `ai-agents/config/integration.conf`
- **MCP設定**: `ai-agents/mcp/claude_code_config.json`
- **ワーカー設定**: `ai-agents/workflow_state.json`

### APIドキュメント
- **MCP API**: WebSocket `ws://localhost:8765`
- **REST API**: `http://localhost:8080` (Webhook)
- **GitHub API**: `gh api` コマンド

### コミュニティ
- **Issues**: GitHub Issuesで問題報告
- **ディスカッション**: GitHub Discussions
- **貢献**: Pull Requestsで機能追加

---

**⚙️ 開発**: システム開発担当  
**📅 最終更新**: 2025-06-29  
**🔖 バージョン**: 2.0.0  
**🌟 ステータス**: Production Ready