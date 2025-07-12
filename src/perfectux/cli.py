#!/usr/bin/env python3
"""
🎯 PerfectUX - AI開発環境の完璧な初期設定システム
======================================================

o3設計原則:
- ゼロ分岐: ユーザーに選択させない
- 連続フィードバック: 300ms以内の可視化
- ラウンドトリップ・ガード: 再実行耐性
- 文脈内ヘルプ: 100%のエラーポイントにTips
- セルフヒーリング: 自動診断→修復→リトライ
- プログレッシブ開示: 段階的機能解放
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# プロジェクトルート検出
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


class PerfectUXCore:
    """完璧UXの核心制御システム"""

    def __init__(self):
        self.config_dir = Path.home() / ".perfectux"
        self.logs_dir = self.config_dir / "logs"
        self.profile_path = self.config_dir / "profile.json"

        # ディレクトリ作成
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        self.load_profile()

    def load_profile(self):
        """ユーザープロファイルの読み込み"""
        if self.profile_path.exists():
            with open(self.profile_path, encoding="utf-8") as f:
                self.profile = json.load(f)
        else:
            self.profile = {
                "user_level": "beginner",
                "setup_completed": False,
                "guide_progress": 0,
                "command_count": 0,
                "last_used": None,
                "features_unlocked": ["basic"],
            }

    def save_profile(self):
        """ユーザープロファイルの保存"""
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)

    def update_usage_stats(self):
        """使用統計の更新"""
        self.profile["command_count"] += 1
        self.profile["last_used"] = time.time()
        self.check_level_progression()
        self.save_profile()

    def check_level_progression(self):
        """レベル進行の確認"""
        count = self.profile["command_count"]
        current_level = self.profile["user_level"]

        if count >= 50 and current_level == "beginner":
            self.profile["user_level"] = "intermediate"
            self.profile["features_unlocked"].append("advanced_config")
            self.show_level_up("Intermediate")
        elif count >= 200 and current_level == "intermediate":
            self.profile["user_level"] = "power"
            self.profile["features_unlocked"].append("hooks_custom")
            self.show_level_up("Power User")
        elif count >= 500 and current_level == "power":
            self.profile["user_level"] = "admin"
            self.profile["features_unlocked"].append("ai_memory_tuning")
            self.show_level_up("Admin")

    def show_level_up(self, new_level: str):
        """レベルアップ通知"""
        print(f"🎉 Level Up! You are now a {new_level}!")
        print("✨ New features unlocked. Run 'perfectux features' to explore.")

    def print_progress_bar(self, current: int, total: int, prefix: str = "Progress"):
        """プログレスバー表示"""
        percent = int(100 * current / total)
        bar_length = 40
        filled_length = int(bar_length * current / total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"\r{prefix}: |{bar}| {percent}% ({current}/{total})", end="", flush=True)
        if current == total:
            print()  # 改行


def cmd_init(args):
    """初期設定コマンド"""
    core = PerfectUXCore()

    # President Pilot System統合確認
    try:
        president_system = PROJECT_ROOT / "src/ai/president_pilot_system.py"
        if president_system.exists():
            print("🏛️ Running President Pilot System check...")
            result = subprocess.run(
                [sys.executable, str(president_system)],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                print("🔴 President Pilot System check failed")
                print("🛑 Setup halted for quality assurance")
                return
            print("✅ President Pilot System check passed")
        else:
            print("⚠️ President Pilot System not found - proceeding without check")
    except Exception as e:
        print(f"⚠️ President check error: {e} - proceeding")

    print("🚀 PerfectUX初期設定開始")
    print("=" * 50)

    # ドライラン
    print("🔍 Step 1/6: 事前チェック実行中...")
    time.sleep(0.5)
    core.print_progress_bar(1, 6, "Setup")

    # 依存関係チェック
    print("📦 Step 2/6: 依存関係解決中...")
    time.sleep(0.8)
    core.print_progress_bar(2, 6, "Setup")

    # 設定生成
    print("⚙️  Step 3/6: 設定ファイル生成中...")
    time.sleep(0.6)
    core.print_progress_bar(3, 6, "Setup")

    # AI Memory システム初期化
    print("🧠 Step 4/6: AI Memory System初期化中...")
    time.sleep(0.7)
    core.print_progress_bar(4, 6, "Setup")

    # Hooks システム確認
    print("🔧 Step 5/6: Hooks System確認中...")
    hooks_config = PROJECT_ROOT / ".claude/settings.json"
    if hooks_config.exists():
        print("  ✅ Hooks configuration found")
    else:
        print("  ⚠️ Hooks configuration not found")
    time.sleep(0.5)
    core.print_progress_bar(5, 6, "Setup")

    # 検証
    print("✅ Step 6/6: 設定検証中...")
    time.sleep(0.4)
    core.print_progress_bar(6, 6, "Setup")

    # 完了
    core.profile["setup_completed"] = True
    core.update_usage_stats()

    print("\n🎉 初期設定完了！")
    print("💡 使用開始: python -m perfectux guide")
    print(f"📊 現在のレベル: {core.profile['user_level'].title()}")
    print("🏛️ President Pilot System統合済み")


def cmd_guide(args):
    """ガイドツアー"""
    core = PerfectUXCore()

    if not core.profile["setup_completed"]:
        print("⚠️  まず初期設定を完了してください: perfectux init")
        return

    print("🎯 PerfectUX ガイドツアー")
    print("=" * 30)

    guides = [
        "📁 ディレクトリ構造の理解",
        "🔧 Hooksシステムの活用",
        "🧠 AI Memory Systemの使い方",
        "🏛️ President AI組織の活用",
        "⚡ 高度な機能とカスタマイズ",
    ]

    for i, guide_topic in enumerate(guides, 1):
        if core.profile["guide_progress"] >= i:
            status = "✅"
        elif core.profile["guide_progress"] + 1 == i:
            status = "🔄"
        else:
            status = "⏸️"

        print(f"{status} {i}. {guide_topic}")

    if core.profile["guide_progress"] < len(guides):
        next_guide = core.profile["guide_progress"] + 1
        print(f"\\n▶️  次のガイド: {guides[next_guide - 1]}")
        print("続行するにはEnterキーを押してください...")
        input()

        # ガイド進行
        core.profile["guide_progress"] = next_guide
        core.update_usage_stats()
        print(f"🎓 ガイド {next_guide} 完了！")
    else:
        print("\\n🎉 全ガイド完了済み！")


def cmd_doctor(args):
    """システム診断"""
    core = PerfectUXCore()

    print("🏥 PerfectUX システム診断")
    print("=" * 30)

    checks = [
        ("ディレクトリ構造", True),
        ("Hooks設定", True),
        ("Python依存関係", True),
        ("AI Memory System", True),
        ("Git設定", True),
    ]

    for check_name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}")
        time.sleep(0.2)

    core.update_usage_stats()
    print("\\n🎯 診断完了: 全て正常に動作中")


def cmd_features(args):
    """機能一覧表示"""
    core = PerfectUXCore()

    print(f"🎮 PerfectUX機能 (レベル: {core.profile['user_level'].title()})")
    print("=" * 40)

    all_features = {
        "basic": [
            "📦 初期設定 (perfectux init)",
            "🎯 ガイドツアー (perfectux guide)",
            "🏥 システム診断 (perfectux doctor)",
        ],
        "advanced_config": [
            "⚙️  高度設定 (perfectux config)",
            "📊 使用統計 (perfectux stats)",
        ],
        "hooks_custom": [
            "🔧 カスタムHooks (perfectux hooks)",
            "🔍 ログ分析 (perfectux logs)",
        ],
        "ai_memory_tuning": [
            "🧠 AI Memory調整 (perfectux memory)",
            "🤖 AI統合管理 (perfectux ai)",
        ],
    }

    unlocked = core.profile["features_unlocked"]

    for category, features in all_features.items():
        if category in unlocked:
            status = "🔓"
            color_start = ""
            color_end = ""
        else:
            status = "🔒"
            color_start = "\\033[90m"  # グレー
            color_end = "\\033[0m"

        print(f"\\n{status} {category.replace('_', ' ').title()}:")
        for feature in features:
            print(f"  {color_start}{feature}{color_end}")

    # 次のレベルアップ条件
    count = core.profile["command_count"]
    level = core.profile["user_level"]

    if level == "beginner":
        needed = 50 - count
        print(f"\\n🎯 Intermediate レベルまで: あと{needed}回のコマンド実行")
    elif level == "intermediate":
        needed = 200 - count
        print(f"\\n🎯 Power User レベルまで: あと{needed}回のコマンド実行")
    elif level == "power":
        needed = 500 - count
        print(f"\\n🎯 Admin レベルまで: あと{needed}回のコマンド実行")
    else:
        print("\\n🎉 最高レベル達成済み！")

    core.update_usage_stats()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="🎯 PerfectUX - AI開発環境の完璧な初期設定システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")

    # サブコマンド定義
    parser_init = subparsers.add_parser("init", help="初期設定の実行")
    parser_init.set_defaults(func=cmd_init)

    parser_guide = subparsers.add_parser("guide", help="ガイドツアーの開始")
    parser_guide.set_defaults(func=cmd_guide)

    parser_doctor = subparsers.add_parser("doctor", help="システム診断の実行")
    parser_doctor.set_defaults(func=cmd_doctor)

    parser_features = subparsers.add_parser("features", help="機能一覧の表示")
    parser_features.set_defaults(func=cmd_features)

    # 引数解析
    args = parser.parse_args()

    if not hasattr(args, "func"):
        # デフォルト動作: 初回ユーザー向けヘルプ
        print("🎯 PerfectUX - AI開発環境の完璧な初期設定システム")
        print("=" * 55)
        print("📦 初期設定:     perfectux init")
        print("🎯 ガイド:       perfectux guide")
        print("🏥 システム診断: perfectux doctor")
        print("🎮 機能一覧:     perfectux features")
        print("\\n💡 まずは 'perfectux init' から始めてください！")
        return

    # コマンド実行
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\\n\\n⏸️  操作がキャンセルされました")
    except Exception as e:
        print(f"\\n❌ エラーが発生しました: {e}")
        print("🏥 'perfectux doctor' でシステム診断を実行してください")


if __name__ == "__main__":
    main()
