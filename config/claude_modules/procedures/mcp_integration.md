# MCP Integration Procedures - 詳細手順

## 🔧 MCP設定完全ガイド

### o3 MCP設定（公式パッケージ使用）

**IMPORTANT:** o3は公式MCP経由でのみアクセス

#### 1. パッケージインストール
```bash
npm install -g o3-search-mcp
```

#### 2. .mcp.json設定
```json
{
  "mcpServers": {
    "o3": {
      "command": "npx",
      "args": ["o3-search-mcp"],
      "env": {
        "OPENAI_API_KEY": "your-openai-key",
        "SEARCH_CONTEXT_SIZE": "medium",
        "REASONING_EFFORT": "medium"
      }
    }
  }
}
```

#### 3. Claude CLI登録（オプション）
```bash
claude mcp add o3 -s user \
    -e OPENAI_API_KEY=your-key \
    -e SEARCH_CONTEXT_SIZE=medium \
    -e REASONING_EFFORT=medium \
    -- npx o3-search-mcp
```

### Gemini CLI設定（直接CLI使用）

**IMPORTANT:** GeminiはMCP不要、CLI直接使用

#### 1. インストール確認
```bash
which gemini
# 期待: /opt/homebrew/bin/gemini
```

#### 2. 基本使用方法
```bash
# 基本質問
gemini -p "質問内容"

# モデル指定
gemini -m "gemini-2.5-pro" -p "質問内容"

# YOLOモード（自動承認）
gemini -y -p "質問内容"
```

#### 3. 自動修正フック (.claude/settings.json統合済み)
Claude Code Hooks統合により自動修正：
- `gemini "テキスト"` → `gemini -p "テキスト"`
- `gemini テキスト` → `gemini -p "テキスト"`

### API設定

#### 必須環境変数
```bash
# .env ファイル
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSyC...
```

#### 設定確認
```bash
# システム状態確認
python3 scripts/memory/session_memory_enhancer.py

# クイックリファレンス確認
cat QUICK_REFERENCE.md
```

### トラブルシューティング

#### よくあるエラー
1. **o3 MCP接続失敗**
   ```bash
   # パッケージ再インストール
   npm uninstall -g o3-search-mcp
   npm install -g o3-search-mcp
   ```

2. **Gemini CLI認証エラー**
   ```bash
   # API KEY確認
   echo $GEMINI_API_KEY
   # 再設定
   export GEMINI_API_KEY="your-key"
   ```

3. **仮想環境問題**
   ```bash
   # 仮想環境有効化
   source venv/bin/activate
   ```

### 使用例

#### o3との対話（MCP経由）
Claude Code内で自動的にo3ツールが利用可能

#### Geminiとの対話（CLI直接）
```bash
gemini -p "CLAUDE.mdの最適化について教えて"
```