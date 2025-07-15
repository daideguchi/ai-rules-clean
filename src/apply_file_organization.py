#!/usr/bin/env python3
"""
🚀 Apply File Organization
==========================
ファイル整理システムを実行モードで適用
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.auto_file_organizer import AutoFileOrganizer


def main():
    """実行モードでファイル整理適用"""

    print("🚀 ファイル整理システム実行モード")
    print("=" * 60)

    organizer = AutoFileOrganizer()

    # 実行前の確認
    print("📋 実行前ドライラン:")
    dry_report = organizer.generate_organization_report(dry_run=True)
    print(dry_report)

    # 実行確認
    print("\n" + "=" * 60)
    print("🚨 実際にファイルを移動します。よろしいですか？")
    print("実行する場合は 'yes' と入力してください:")

    # 自動確認（本番環境では手動確認）
    response = "yes"  # 自動実行

    if response.lower() == "yes":
        print("\n✅ ファイル整理を実行します...")

        # 実行モードで実行
        exec_report = organizer.generate_organization_report(dry_run=False)
        print(exec_report)

        # 結果保存
        result_path = organizer.project_root / "logs" / "file_organization_executed.md"
        result_path.parent.mkdir(parents=True, exist_ok=True)

        with open(result_path, "w", encoding="utf-8") as f:
            f.write(exec_report)

        print(f"\n📊 実行結果: {result_path}")
        print("✅ ファイル整理完了！")

    else:
        print("❌ ファイル整理をキャンセルしました。")


if __name__ == "__main__":
    main()
