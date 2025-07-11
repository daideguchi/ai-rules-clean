# システム状態クイックリファレンス
更新日時: 2025-07-11T07:54:16.580481

## インストール済みツール
- ✅ gemini: /opt/homebrew/bin/gemini
- ✅ claude: /opt/homebrew/bin/claude
- ✅ npm: /opt/homebrew/bin/npm
- ✅ python3: /Users/dd/Desktop/1_dev/coding-rule2/venv/bin/python3

## API設定状況
- OPENAI_API_KEY: ✅ 設定済み
- GEMINI_API_KEY: ✅ 設定済み
- ANTHROPIC_API_KEY: ❌ 未設定

## MCP設定
- ✅ o3
- ✅ gemini-custom

## 重要なコマンド
- Gemini: `gemini -p "質問"`
- o3: MCP経由でアクセス
- PRESIDENT宣言: `make declare-president`

## よくある質問と回答
1. **Q: GeminiのMCP設定は？**
   A: GeminiはCLI直接使用。MCPは不要。

2. **Q: o3のMCP設定は？**
   A: .mcp.jsonでo3-search-mcpパッケージ使用。

3. **Q: 仮想環境は？**
   A: venv/ディレクトリに設定済み。activate必要。
