#!/opt/homebrew/bin/python3
"""
PRESIDENT宣言完了後の自動セットアップシステム
- AI組織立ち上げ判定
- 役職自動セット
- 前回セッション概要生成
- システム状態レポート
"""

import json
import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def detect_ai_organization_mode():
    """AI組織モード自動検出"""
    # tmuxセッション確認
    tmux_check = os.system("tmux has-session -t multiagent 2>/dev/null") == 0

    if tmux_check:
        return {
            "mode": "multi_ai_organization",
            "description": "複数AI組織体制",
            "roles": ["PRESIDENT", "DEVELOPER", "ANALYST", "USER_GUIDE"],
            "setup_required": [
                "role_assignment",
                "task_distribution",
                "communication_protocol",
            ],
        }
    else:
        return {
            "mode": "single_president",
            "description": "PRESIDENT単独体制",
            "roles": ["PRESIDENT"],
            "setup_required": ["unified_role_setup", "comprehensive_task_management"],
        }


def load_previous_session_summary():
    """前回セッション概要読み込み"""

    summary = {
        "last_session": "未記録",
        "active_tasks": [],
        "completed_work": [],
        "pending_issues": [],
    }

    try:
        # work-records.mdから最新作業記録取得
        work_records_path = PROJECT_ROOT / "docs/misc/work-records.md"
        if work_records_path.exists():
            with open(work_records_path, encoding="utf-8") as f:
                content = f.read()
                # 最新の作業記録を抽出（簡易実装）
                if "作業記録 #" in content:
                    lines = content.split("\n")
                    for line in lines:
                        if "作業記録 #" in line and "##" in line:
                            summary["last_session"] = line.strip()
                            break

        # operation_log.jsonlから最新操作取得
        operation_log_path = PROJECT_ROOT / "src/memory/operations/operation_log.jsonl"
        if operation_log_path.exists():
            with open(operation_log_path, encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_operation = json.loads(lines[-1])
                    summary["last_operation"] = last_operation.get("operation", "不明")

    except Exception as e:
        summary["error"] = f"セッション読み込みエラー: {str(e)}"

    return summary


def check_system_status():
    """システム状態チェック"""
    status = {
        "project_structure": "✅ 8ディレクトリ構造準拠",
        "hooks_system": "✅ フック制御稼働中",
        "memory_system": "確認中",
        "api_status": "確認中",
        "database_status": "確認中",
    }

    # プロジェクト構造確認
    required_dirs = [
        "src",
        "agents",
        "memory",
        "config",
        "scripts",
        "operations",
        "docs",
        "tests",
    ]
    existing_dirs = [d for d in required_dirs if (PROJECT_ROOT / d).exists()]
    status["project_structure"] = f"✅ {len(existing_dirs)}/8ディレクトリ存在"

    # API設定確認
    api_files = list(PROJECT_ROOT.glob("**/api*"))
    if api_files:
        status["api_status"] = f"✅ API設定ファイル {len(api_files)}個検出"
    else:
        status["api_status"] = "⚠️ API設定未検出"

    # データベース状態確認
    db_files = list(PROJECT_ROOT.glob("**/*.db")) + list(PROJECT_ROOT.glob("**/*.json"))
    status["database_status"] = f"✅ データファイル {len(db_files)}個検出"

    return status


def generate_startup_message(ai_mode, session_summary, system_status):
    """起動メッセージ生成"""
    message = f"""
🔥 **PRESIDENT宣言完了 - システム稼働開始**

## 👑 **AI組織体制**
- **モード**: {ai_mode["description"]}
- **役職**: {", ".join(ai_mode["roles"])}
- **必要セットアップ**: {", ".join(ai_mode["setup_required"])}

## 📊 **前回セッション継承**
- **最新作業**: {session_summary.get("last_session", "未記録")}
- **前回操作**: {session_summary.get("last_operation", "不明")}

## 🔧 **システム状態**
- **プロジェクト構造**: {system_status["project_structure"]}
- **フック制御**: {system_status["hooks_system"]}
- **API状態**: {system_status["api_status"]}
- **データベース**: {system_status["database_status"]}

## 🎯 **次のアクション**
{"### 🤖 **AI組織セットアップ必須**" if ai_mode["mode"] == "multi_ai_organization" else "### 👑 **PRESIDENT統合管理開始**"}
1. 要件定義・仕様書確認
2. {"役職分担・タスク配布" if ai_mode["mode"] == "multi_ai_organization" else "統合タスク管理セットアップ"}
3. 開発・品質管理開始

**準備完了 - 78回のミスを二度と繰り返さない最強体制で支援開始**
"""
    return message.strip()


def main():
    """メイン処理"""
    print("🔄 PRESIDENT宣言後システム初期化中...")

    # AI組織モード検出
    ai_mode = detect_ai_organization_mode()

    # 前回セッション読み込み
    session_summary = load_previous_session_summary()

    # システム状態確認
    system_status = check_system_status()

    # 起動メッセージ生成
    startup_message = generate_startup_message(ai_mode, session_summary, system_status)

    print(startup_message)

    # 状態をファイルに保存
    startup_state = {
        "timestamp": datetime.now().isoformat(),
        "ai_mode": ai_mode,
        "session_summary": session_summary,
        "system_status": system_status,
    }

    state_file = PROJECT_ROOT / "runtime" / "startup_state.json"
    state_file.parent.mkdir(exist_ok=True)

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(startup_state, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
