# MCP (Model Context Protocol) セットアップガイド

## 概要
MCP (Model Context Protocol) は、AI Safety Governance SystemでClaude Code、o3、Geminiなどの複数のAIモデルを統合するための重要なプロトコルです。

## セットアップ手順

### 1. 設定ファイルの準備

```bash
# テンプレートファイルをコピー
cp config/.mcp.json.example config/.mcp.json

# 注意: config/.mcp.jsonは.gitignoreに含まれているため、Gitには含まれません
```

### 2. APIキーの設定

`config/.mcp.json`を編集して、各サービスのAPIキーを設定します：

```json
{
  "mcpServers": {
    "o3": {
      "command": "python",
      "args": ["scripts/mcp/o3_mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-proj-xxxxx"  // OpenAI APIキーをここに設定
      }
    },
    "gemini": {
      "command": "python",
      "args": ["scripts/mcp/gemini_mcp_server.py"],
      "env": {
        "GOOGLE_API_KEY": "AIzaSyxxxxx"  // Google APIキーをここに設定
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/coding_rule2_ai"
      ]
    }
  }
}
```

### 3. APIキーの取得方法

#### OpenAI (o3用)
1. [OpenAI Platform](https://platform.openai.com/api-keys)にアクセス
2. 「Create new secret key」をクリック
3. キーをコピーして`OPENAI_API_KEY`に設定

#### Google AI (Gemini用)
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. 「Get API key」をクリック
3. キーをコピーして`GOOGLE_API_KEY`に設定

### 4. PostgreSQLの設定

データベースが既に設定されている場合は、接続文字列を確認：

```bash
# PostgreSQL接続文字列の形式
postgresql://[user]:[password]@[host]:[port]/[database]

# 例：
postgresql://postgres:mypassword@localhost:5432/coding_rule2_ai
```

### 5. 動作確認

```bash
# Claude Codeを起動
claude --mcp

# MCPサーバーの状態を確認
claude mcp status
```

## トラブルシューティング

### よくある問題

1. **「config/.mcp.json not found」エラー**
   - 解決策: テンプレートファイルをコピーして設定
   ```bash
   cp config/.mcp.json.example config/.mcp.json
   ```

2. **APIキー認証エラー**
   - 解決策: APIキーが正しく設定されているか確認
   - キーの前後に余分なスペースがないか確認

3. **PostgreSQL接続エラー**
   - 解決策: データベースが起動しているか確認
   ```bash
   docker-compose up -d postgres
   ```

### セキュリティ注意事項

- **重要**: `config/.mcp.json`は機密情報を含むため、絶対にGitにコミットしないでください
- `.gitignore`に追加済みですが、念のため`git status`で確認してください
- APIキーは定期的にローテーションすることを推奨します

## 関連ドキュメント

- [MCP Integration System](/mcp_integration/docs/README.md)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code/mcp)
- [AI Safety Governance System README](/README.md)