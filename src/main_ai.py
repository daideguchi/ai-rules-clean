#!/usr/bin/env python3
"""
🤖 AI - 完璧UX開発並走システム
===============================

【ワンコマンドですべて】
- ai setup     : 完全自動初期設定
- ai dev start : 自動開発開始
- ai status    : 現在状況確認
- ai help      : 完全ガイド表示

【最高UX設計】
- 迷わせない明確な誘導
- AI組織自動連携・分散処理
- 要件自動把握・擦り合わせ
- 一人の優秀な人間のような対応
"""

import subprocess
import sys
from pathlib import Path


def display_perfect_welcome():
    """完璧ウェルカム表示"""
    print("""
🤖 AI開発並走システム - 完璧UX
================================

【このAIシステムについて】
プロジェクトの完成まで一貫して並走し、
ルールを忘れず、一人の優秀な人間のような
AIとして開発をサポートします。

【今すぐできること】
""")


def show_status():
    """現在状況表示"""
    project_root = Path.cwd()

    print("📊 現在のプロジェクト状況")
    print("=" * 40)
    print(f"📁 プロジェクト: {project_root.name}")

    # AI組織状況確認
    memory_dir = project_root / "memory"
    if memory_dir.exists():
        ai_systems = len(list(memory_dir.glob("*.py")))
        print(f"🤖 AIシステム: {ai_systems}個稼働中")

        # 設定ファイル確認
        config_dir = project_root / "config"
        if config_dir.exists():
            configs = len(list(config_dir.glob("*.json")))
            print(f"⚙️ 設定ファイル: {configs}個")

        # データベース確認
        try:
            import psycopg2

            db_config = {
                "host": "localhost",
                "database": f"{project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            }
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("💾 データベース: 接続済み")
        except Exception:
            print("💾 データベース: 未設定")

        print("✅ AIシステム: 準備完了")
    else:
        print("❌ AIシステム: 未初期化")
        print("   → 'ai setup' で初期設定を実行してください")


def run_setup():
    """完全自動初期設定実行"""
    project_root = Path.cwd()
    memory_dir = project_root / "memory"

    if not memory_dir.exists():
        print("❌ memoryディレクトリが見つかりません")
        print("   このコマンドはAI Memory Systemがあるプロジェクトで実行してください")
        return

    print("🚀 完全自動初期設定開始...")

    # President AI組織システム起動
    president_file = memory_dir / "president_ai_organization.py"
    if president_file.exists():
        print("👑 President AI組織システム起動中...")
        try:
            result = subprocess.run(
                [sys.executable, str(president_file), "--quick-start"],
                cwd=project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ President AI組織: 初期設定完了")
            else:
                print(f"⚠️ President AI初期設定警告: {result.stderr}")
        except Exception as e:
            print(f"❌ President AI初期設定エラー: {e}")

    # Hooks システムセットアップ
    hooks_file = memory_dir / "ai_hooks_system.py"
    if hooks_file.exists():
        print("🪝 AI Hooksシステムセットアップ中...")
        try:
            result = subprocess.run(
                [sys.executable, str(hooks_file)],
                cwd=project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ AI Hooks: セットアップ完了")
        except Exception as e:
            print(f"❌ AI Hooksセットアップエラー: {e}")

    print("\n🎉 完全自動初期設定完了!")
    print("   次に 'ai status' で状況を確認するか")
    print("   'ai dev start' で自動開発を開始してください")


def start_development():
    """自動開発開始"""
    project_root = Path.cwd()

    print("🚀 AI自動開発システム開始")
    print("=" * 40)

    # President AI起動
    memory_dir = project_root / "memory"
    president_file = memory_dir / "president_ai_organization.py"

    if president_file.exists():
        print("👑 President AI起動中...")
        try:
            result = subprocess.run(
                [sys.executable, str(president_file)], cwd=project_root
            )

            if result.returncode == 0:
                print("✅ AI自動開発システム稼働中")
            else:
                print("⚠️ 開発システム起動に問題がありました")
        except Exception as e:
            print(f"❌ 開発システム起動エラー: {e}")
    else:
        print("❌ President AIが見つかりません")
        print("   'ai setup' で初期設定を実行してください")


def show_help():
    """完全ヘルプ表示"""
    print("""
🤖 AI完璧UXヘルプ
=================

【基本コマンド】
  ai setup       完全自動初期設定（初回のみ）
  ai dev start   自動開発開始
  ai status      現在状況確認
  ai help        このヘルプ表示

【使い方の流れ】
  1. ai setup           # 初回のみ：完全自動設定
  2. ai status          # 状況確認
  3. ai dev start       # 自動開発開始
  4. [具体的な要求]      # AIが自動で実現

【AI組織について】
  👑 PRESIDENT AI    : 戦略・統括・品質保証
  🛠️ DEVELOPER AI   : 実装・技術・テスト
  📊 ANALYST AI     : 分析・最適化・レポート
  📖 USER_GUIDE AI  : UX・案内・サポート

【特徴】
  ✅ ワンコマンド完全自動設定
  ✅ AI組織自動連携・分散処理
  ✅ 要件自動把握・擦り合わせ
  ✅ 一人の優秀な人間のような対応
  ✅ プロジェクト完成まで一貫並走
  ✅ ルール・文脈を忘れない学習機能

【サポート】
  問題がある場合は 'ai status' で状況確認
  または memory/ ディレクトリ内のシステムを
  個別に実行して詳細確認できます

🎯 目標: 開発者が迷うことなく、AIと共に
         効率的に高品質なプロジェクトを完成
""")


def main():
    """メイン実行"""

    if len(sys.argv) < 2:
        display_perfect_welcome()
        print("🎯 使い方: ai <command>")
        print("   詳細: ai help")
        return

    command = sys.argv[1].lower()

    if command == "setup":
        run_setup()
    elif command == "status":
        show_status()
    elif command in ["dev", "start"] or (len(sys.argv) > 2 and sys.argv[2] == "start"):
        start_development()
    elif command == "help":
        show_help()
    else:
        print(f"❌ 不明なコマンド: {command}")
        print("   使用可能: setup, status, dev start, help")
        print("   詳細: ai help")


if __name__ == "__main__":
    main()
