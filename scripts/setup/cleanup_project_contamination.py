#!/usr/bin/env python3
"""
プロジェクト汚染除去スクリプト
他プロジェクトに作成された不要ファイルを検出・削除
"""

from pathlib import Path


def cleanup_contamination():
    """他プロジェクト汚染除去"""
    print("🧹 プロジェクト汚染除去開始")
    print("=" * 40)

    base_dir = Path("/Users/dd/Desktop/1_dev")
    current_project = base_dir / "coding-rule2"

    contamination_patterns = [
        "**/claude_desktop_n8n_config.json",
        "**/n8n_config.json",
        "**/autonomous_growth*.py",
        "**/performance_auto_sender.py",
        "**/.claude_auto_trigger",
    ]

    removed_files = []

    for pattern in contamination_patterns:
        for file_path in base_dir.glob(pattern):
            # 現在のプロジェクト以外のファイルのみ削除
            if not str(file_path).startswith(str(current_project)):
                try:
                    if file_path.exists():
                        print(f"🗑️ Removing: {file_path}")
                        file_path.unlink()
                        removed_files.append(str(file_path))
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")

    print(f"\\n✅ 除去完了: {len(removed_files)}ファイル")
    for file in removed_files:
        print(f"   - {file}")

    # 予防措置: 今後の汚染防止
    create_contamination_prevention()


def create_contamination_prevention():
    """汚染防止システム作成"""
    prevention_script = """#!/usr/bin/env python3
# プロジェクト汚染防止
import os
import sys
from pathlib import Path

def ensure_project_isolation():
    project_root = Path(__file__).parent.parent.parent
    if not str(os.getcwd()).startswith(str(project_root)):
        print("⚠️ WARNING: Operating outside project boundary!")
        print(f"Current: {os.getcwd()}")
        print(f"Expected: {project_root}")
        return False
    return True

if __name__ == "__main__":
    ensure_project_isolation()
"""

    prevention_path = Path(
        "/Users/dd/Desktop/1_dev/coding-rule2/scripts/setup/project_isolation_check.py"
    )
    with open(prevention_path, "w") as f:
        f.write(prevention_script)

    print(f"🛡️ 汚染防止スクリプト作成: {prevention_path}")


if __name__ == "__main__":
    cleanup_contamination()
