#!/usr/bin/env python3
"""
📋 セッション記憶継承強化システム
同じ質問・作業の繰り返し防止
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


class SessionMemoryEnhancer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.memory_dir = self.project_root / "runtime" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 重要な設定・状態ファイル
        self.key_files = [
            "CLAUDE.md",
            ".mcp.json",
            "scripts/hooks/gemini_command_validator.py",
            ".env",
        ]

    def scan_current_state(self):
        """現在のシステム状態をスキャン"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "installed_tools": self._check_installed_tools(),
            "environment_vars": self._check_env_vars(),
            "mcp_config": self._check_mcp_config(),
            "key_configurations": self._check_key_configs(),
        }

        # メモリファイルに保存
        memory_file = self.memory_dir / "current_system_state.json"
        with open(memory_file, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        return state

    def _check_installed_tools(self):
        """インストール済みツールチェック"""
        tools = {}

        # CLI tools
        cli_tools = ["gemini", "claude", "npm", "python3"]
        for tool in cli_tools:
            try:
                result = subprocess.run(["which", tool], capture_output=True, text=True)
                tools[tool] = {
                    "installed": result.returncode == 0,
                    "path": result.stdout.strip() if result.returncode == 0 else None,
                }
            except Exception:
                tools[tool] = {"installed": False, "path": None}

        # NPM packages
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0"], capture_output=True, text=True
            )
            tools["npm_global_packages"] = result.stdout
        except Exception:
            tools["npm_global_packages"] = "Unable to check"

        return tools

    def _check_env_vars(self):
        """重要な環境変数チェック"""
        important_vars = ["OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]

        env_status = {}
        for var in important_vars:
            value = os.getenv(var)
            env_status[var] = {
                "set": value is not None,
                "length": len(value) if value else 0,
            }

        return env_status

    def _check_mcp_config(self):
        """MCP設定確認"""
        mcp_file = self.project_root / ".mcp.json"
        if mcp_file.exists():
            try:
                with open(mcp_file) as f:
                    return json.load(f)
            except Exception:
                return {"error": "Invalid JSON"}
        return {"status": "not_found"}

    def _check_key_configs(self):
        """重要設定ファイルの存在確認"""
        configs = {}
        for file_path in self.key_files:
            full_path = self.project_root / file_path
            configs[file_path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0,
                "modified": full_path.stat().st_mtime if full_path.exists() else None,
            }
        return configs

    def create_quick_reference(self):
        """クイックリファレンス生成"""
        state = self.scan_current_state()

        reference = f"""# システム状態クイックリファレンス
更新日時: {state["timestamp"]}

## インストール済みツール
"""

        for tool, info in state["installed_tools"].items():
            if isinstance(info, dict) and info.get("installed"):
                reference += f"- ✅ {tool}: {info['path']}\n"
            elif isinstance(info, dict):
                reference += f"- ❌ {tool}: 未インストール\n"

        reference += """
## API設定状況
"""
        for var, info in state["environment_vars"].items():
            status = "✅ 設定済み" if info["set"] else "❌ 未設定"
            reference += f"- {var}: {status}\n"

        reference += """
## MCP設定
"""
        if "mcpServers" in state["mcp_config"]:
            for server in state["mcp_config"]["mcpServers"]:
                reference += f"- ✅ {server}\n"
        else:
            reference += "- ❌ MCP設定なし\n"

        reference += """
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
"""

        # クイックリファレンス保存
        ref_file = self.project_root / "QUICK_REFERENCE.md"
        with open(ref_file, "w") as f:
            f.write(reference)

        return reference


def main():
    enhancer = SessionMemoryEnhancer()
    state = enhancer.scan_current_state()
    enhancer.create_quick_reference()

    print("🧠 記憶継承システム強化完了")
    print(f"✅ システム状態スキャン: {len(state)} 項目")
    print("✅ クイックリファレンス生成: QUICK_REFERENCE.md")
    print("\n📋 今後は同じ質問を繰り返す前に、このファイルを確認してください。")


if __name__ == "__main__":
    main()
