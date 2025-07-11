#!/usr/bin/env python3
"""
Runtime Orchestrator Hook - 実行時オーケストレーターフック
Claude Code実行ライフサイクルの全イベントを統合管理
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project path to Python path
project_path = Path(__file__).parent.parent.parent
sys.path.append(str(project_path / "src"))

try:
    from orchestrator.claude_code_integration import get_claude_code_integration

    async def main():
        """メインフック処理"""
        try:
            # Get Claude Code integration
            integration = get_claude_code_integration()

            # Get command line arguments
            sys.argv[1:] if len(sys.argv) > 1 else []
            hook_type = os.getenv("CLAUDE_HOOK_TYPE", "general")

            # Process based on hook type
            if hook_type == "Start":
                # Session start
                await integration.handle_president_declaration()
                memory_status = integration.get_memory_inheritance_status()
                print(
                    f"🧠 記憶継承システム稼働確認、コード{memory_status.get('confirmation_code', '7749')}"
                )
                print(
                    f"📊 CSA: {memory_status.get('csa_memories_count', 0)}, 永続: {memory_status.get('permanent_memories_count', 0)}"
                )

            elif hook_type == "PreToolUse":
                # Pre-tool execution
                tool_name = os.getenv("CLAUDE_TOOL_NAME", "")
                if tool_name:
                    await integration.handle_user_input(f"Tool execution: {tool_name}")

            elif hook_type == "PostToolUse":
                # Post-tool execution
                tool_name = os.getenv("CLAUDE_TOOL_NAME", "")
                if tool_name:
                    # Check for thinking requirements
                    if tool_name in ["Edit", "Write", "MultiEdit"]:
                        await integration.handle_thinking_enforcement()

            elif hook_type == "Stop":
                # Session cleanup
                await integration.cleanup_session()
                print("🔄 セッション完了 - 記憶継承データ保存済み")

            return 0

        except Exception as e:
            print(f"❌ Runtime orchestrator hook error: {e}", file=sys.stderr)
            return 1

    # Run async main
    if __name__ == "__main__":
        exit_code = asyncio.run(main())
        sys.exit(exit_code)

except ImportError as e:
    print(f"⚠️ Runtime orchestrator not available: {e}", file=sys.stderr)
    sys.exit(0)  # Don't fail if system not available
