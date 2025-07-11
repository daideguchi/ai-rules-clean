#!/usr/bin/env python3
"""
🤝 Subagent Memory Merge Hook
サブエージェント終了時のメモリ統合とコンフリクト解決
"""

import datetime
import json
import sys
from pathlib import Path


def analyze_subagent_contribution(transcript_path: str, session_id: str) -> dict:
    """サブエージェントの貢献分析"""

    contribution = {
        "session_id": session_id,
        "subagent_id": f"sub_{session_id}",
        "tools_used": [],
        "files_modified": [],
        "commands_executed": [],
        "knowledge_generated": [],
        "quality_score": 0.0,
        "conflict_potential": "low",
    }

    try:
        if not Path(transcript_path).exists():
            return contribution

        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    if entry.get("type") == "tool_use":
                        tool_name = entry.get("tool_name", "")
                        tool_input = entry.get("tool_input", {})

                        contribution["tools_used"].append(tool_name)

                        # ファイル操作記録
                        if tool_name in ["Edit", "Write", "MultiEdit"]:
                            file_path = tool_input.get("file_path", "")
                            if (
                                file_path
                                and file_path not in contribution["files_modified"]
                            ):
                                contribution["files_modified"].append(file_path)

                        # コマンド実行記録
                        elif tool_name == "Bash":
                            command = tool_input.get("command", "")
                            if command:
                                contribution["commands_executed"].append(command[:100])

                        # 知識生成記録
                        elif tool_name in ["Read", "Grep", "Glob"]:
                            contribution["knowledge_generated"].append(
                                f"{tool_name} operation"
                            )

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        print(f"⚠️  Failed to analyze subagent contribution: {e}", file=sys.stderr)

    # 品質スコア計算
    contribution["quality_score"] = calculate_quality_score(contribution)

    # コンフリクト判定
    contribution["conflict_potential"] = assess_conflict_potential(contribution)

    return contribution


def calculate_quality_score(contribution: dict) -> float:
    """サブエージェントの品質スコア計算"""

    score = 0.0

    # ツール使用の多様性
    unique_tools = len(set(contribution["tools_used"]))
    score += min(1.0, unique_tools / 5.0) * 30

    # ファイル操作の効率性
    file_ops = len(contribution["files_modified"])
    if file_ops > 0:
        score += min(1.0, file_ops / 3.0) * 25

    # 知識生成の価値
    knowledge_ops = len(contribution["knowledge_generated"])
    if knowledge_ops > 0:
        score += min(1.0, knowledge_ops / 5.0) * 20

    # コマンド実行の安全性
    safe_commands = sum(
        1
        for cmd in contribution["commands_executed"]
        if not any(danger in cmd.lower() for danger in ["rm -rf", "sudo", "chmod 777"])
    )
    total_commands = len(contribution["commands_executed"])
    if total_commands > 0:
        safety_ratio = safe_commands / total_commands
        score += safety_ratio * 25
    else:
        score += 25  # ボーナス for no risky commands

    return round(score, 2)


def assess_conflict_potential(contribution: dict) -> str:
    """コンフリクトポテンシャルの評価"""

    # 同時ファイル編集のリスク
    critical_files = [
        f
        for f in contribution["files_modified"]
        if any(
            pattern in f.lower() for pattern in ["config", "settings", "main", "init"]
        )
    ]

    if len(critical_files) > 2:
        return "high"
    elif len(critical_files) > 0 or len(contribution["files_modified"]) > 5:
        return "medium"
    else:
        return "low"


def merge_subagent_memory(contribution: dict, session_id: str) -> bool:
    """サブエージェントメモリのメインメモリへの統合"""

    memory_dir = Path("src/memory/subagents")
    memory_dir.mkdir(parents=True, exist_ok=True)

    # サブエージェント貢献ログ
    contribution_file = memory_dir / "subagent_contributions.jsonl"

    merge_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "main_session_id": session_id,
        "contribution": contribution,
        "merge_status": "completed",
    }

    try:
        with open(contribution_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(merge_entry, ensure_ascii=False) + "\\n")

        # 統合サマリーファイル更新
        update_integration_summary(contribution, session_id)

        return True

    except Exception as e:
        print(f"⚠️  Failed to merge subagent memory: {e}", file=sys.stderr)
        return False


def update_integration_summary(contribution: dict, session_id: str):
    """統合サマリーの更新"""

    summary_file = Path("src/memory/subagents/integration_summary.json")

    try:
        # 既存サマリー読み込み
        if summary_file.exists():
            with open(summary_file, encoding="utf-8") as f:
                summary = json.load(f)
        else:
            summary = {
                "total_subagents": 0,
                "average_quality_score": 0.0,
                "high_conflict_sessions": [],
                "top_contributors": [],
            }

        # サマリー更新
        summary["total_subagents"] += 1

        # 平均品質スコア更新
        current_avg = summary["average_quality_score"]
        new_score = contribution["quality_score"]
        summary["average_quality_score"] = round(
            (current_avg * (summary["total_subagents"] - 1) + new_score)
            / summary["total_subagents"],
            2,
        )

        # 高コンフリクトセッション記録
        if contribution["conflict_potential"] == "high":
            summary["high_conflict_sessions"].append(
                {
                    "session_id": session_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )
            # 最新10件のみ保持
            summary["high_conflict_sessions"] = summary["high_conflict_sessions"][-10:]

        # トップ貢献者記録
        if contribution["quality_score"] > 70:
            summary["top_contributors"].append(
                {
                    "session_id": session_id,
                    "score": contribution["quality_score"],
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )
            # スコア順ソート、最新10件のみ保持
            summary["top_contributors"] = sorted(
                summary["top_contributors"], key=lambda x: x["score"], reverse=True
            )[:10]

        # サマリー保存
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"⚠️  Failed to update integration summary: {e}", file=sys.stderr)


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id", "unknown")
        transcript_path = input_data.get("transcript_path", "")
        stop_hook_active = input_data.get("stop_hook_active", False)

        # 重複実行防止
        if stop_hook_active:
            print("🔄 SubagentStop hook already active, skipping merge")
            sys.exit(0)

        # サブエージェント貢献分析
        contribution = analyze_subagent_contribution(transcript_path, session_id)

        # メモリ統合
        merged = merge_subagent_memory(contribution, session_id)

        # 結果出力
        if merged:
            print("🤝 Subagent Memory Merge Completed")
            print(f"📊 Quality Score: {contribution['quality_score']}/100")
            print(f"⚡ Tools Used: {len(set(contribution['tools_used']))}")
            print(f"📁 Files Modified: {len(contribution['files_modified'])}")
            print(f"⚠️  Conflict Risk: {contribution['conflict_potential']}")

            if contribution["conflict_potential"] == "high":
                print("🚨 High conflict potential detected - review required")
        else:
            print("❌ Subagent memory merge failed")

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
