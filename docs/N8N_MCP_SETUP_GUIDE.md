# n8n-MCP 設定ガイド

## 🚀 概要

n8n-MCPは、Claude Desktopとn8nを接続し、AIがn8nワークフローを理解・操作できるようにするModel Context Protocol (MCP)サーバーです。

### 提供される機能
- 📚 **528個のn8nノード**の完全なドキュメント
- 🔧 **ノードプロパティ**の詳細情報
- ⚡ **ワークフロー管理**（作成、更新、実行）
- 🤖 **263個のAI対応ノード**の情報

## 📋 設定手順

### 1. Claude Desktop設定ファイルの更新

**macOSの場合:**
```bash
# 設定ファイルの場所を開く
open ~/Library/Application\ Support/Claude/
```

**設定ファイル名:** `claude_desktop_config.json`

### 2. n8n-MCP設定の追加

既存の設定ファイルに以下を追加（または作成された`claude_desktop_n8n_config.json`の内容を追加）:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://app.n8n.io",
        "N8N_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxZDhkZjBkNS1jNTc2LTRkMTctOTZmZC1lYzYwNjUyZDQ2OTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUyMzE5Mzk5fQ.m3nqC6d3HimtXRhlVAHu-jDG70Xex9KA8PgKZ0Z1-B8"
      }
    }
  }
}
```

### 3. Claude Desktopを再起動

設定を反映するためにClaude Desktopを完全に再起動してください。

## 🔧 利用可能なMCPツール

n8n-MCPは以下のツールを提供します：

### 基本ツール
- `list_nodes` - 利用可能なn8nノードをリスト
- `get_node_info` - 特定ノードの詳細情報を取得
- `get_node_essentials` - 必須プロパティのみ取得（95%サイズ削減）
- `search_nodes` - ノードをキーワード検索
- `search_node_properties` - ノード内のプロパティを検索

### ワークフロー検証
- `validate_workflow` - ワークフロー全体を検証
- `validate_node_operation` - ノード設定を検証
- `validate_workflow_connections` - 接続を検証
- `validate_workflow_expressions` - n8n式を検証

### n8n管理ツール（APIキー設定時のみ）
- `n8n_create_workflow` - 新規ワークフロー作成
- `n8n_get_workflow` - ワークフロー取得
- `n8n_update_full_workflow` - ワークフロー更新
- `n8n_update_partial_workflow` - 差分更新
- `n8n_delete_workflow` - ワークフロー削除
- `n8n_trigger_webhook_workflow` - Webhook経由で実行
- `n8n_list_workflows` - ワークフロー一覧
- `n8n_health_check` - API接続確認

## 🧪 動作確認

Claude Desktopで以下のプロンプトを試してください：

```
n8n-mcpツールを使って、HTTPリクエストノードの情報を教えてください
```

```
n8nのワークフローで、SlackにメッセージをWebhook経由で送信する方法を教えてください
```

## ⚠️ 注意事項

- **本番環境のワークフローは直接編集しない**でください
- 必ず開発環境でテストしてから本番に適用してください
- 重要なワークフローはバックアップを取ってください

## 📚 参考資料

- [n8n-MCP GitHub](https://github.com/czlonkowski/n8n-mcp)
- [n8n Documentation](https://docs.n8n.io/)
- [Model Context Protocol](https://github.com/modelcontextprotocol)

## 🔐 セキュリティ

提供されたAPIキーは安全に管理してください。このキーは：
- n8nインスタンスへのアクセスを提供します
- ワークフローの作成・編集・削除が可能です
- 適切な権限管理が必要です