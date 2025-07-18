#!/usr/bin/env python3
"""
完全ファイル構造問題解決システム
全ての問題を一括で解決し、今後の問題を防止
"""

import subprocess
from pathlib import Path


def run_command(command, description):
    """コマンド実行とエラーハンドリング"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ 完了: {description}")
            if result.stdout.strip():
                print(f"   📄 出力: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ エラー: {description}")
            print(f"   📄 エラー詳細: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ 実行エラー: {e}")
        return False


def solution_menu():
    """解決策メニュー表示"""
    print("🛠️ ファイル構造問題 完全解決システム")
    print("=" * 50)
    print("1. 緊急修正のみ実行（既存の問題を今すぐ修正）")
    print("2. 防止システムのみ設置（今後の問題を防止）")
    print("3. 完全解決（緊急修正 + 防止システム）")
    print("4. 状況確認のみ（現在の問題を表示）")
    print("5. 終了")
    print()

    choice = input("選択してください (1-5): ").strip()
    return choice


def check_current_status():
    """現在の状況確認"""
    print("📊 現在の構造状況確認")
    print("-" * 30)

    project_root = Path.cwd()

    # ルート違反ファイル確認
    root_violations = []
    for item in project_root.iterdir():
        if item.is_file() and item.suffix in [".sh", ".py"]:
            if item.name not in ["setup.py", "manage.py", "pyproject.toml"]:
                root_violations.append(item.name)

    print(f"📁 ルート違反ファイル: {len(root_violations)}個")
    for violation in root_violations:
        print(f"   ❌ {violation}")

    # 命名規則違反確認
    naming_violations = []
    for root, _dirs, files in project_root.rglob("*"):
        for file in files:
            if "_" in file and "__" not in file and file not in ["requirements.txt"]:
                naming_violations.append(str(Path(root) / file))

    print(f"📝 命名規則違反: {len(naming_violations)}個")
    for violation in naming_violations[:5]:  # 最初の5個のみ表示
        print(f"   ❌ {violation}")
    if len(naming_violations) > 5:
        print(f"   ... 他 {len(naming_violations) - 5}個")

    # n8n_marketing ディレクトリ確認
    old_marketing = project_root / "scripts" / "n8n_marketing"
    if old_marketing.exists():
        print("📁 古いマーケティングディレクトリ存在")
        print("   ❌ scripts/n8n_marketing/ → scripts/marketing/ 要修正")

    total_issues = (
        len(root_violations)
        + len(naming_violations)
        + (1 if old_marketing.exists() else 0)
    )
    print(f"\n📊 総問題数: {total_issues}個")

    return total_issues > 0


def execute_emergency_fix():
    """緊急修正実行"""
    print("🚨 緊急修正実行中...")
    return run_command(
        "python3 scripts/automation/emergency-file-structure-fix.py",
        "既存問題の一括修正",
    )


def setup_prevention_system():
    """防止システム設置"""
    print("🛡️ 防止システム設置中...")
    return run_command(
        "python3 scripts/automation/setup-file-structure-prevention.py",
        "今後の問題防止システム設置",
    )


def verify_solution():
    """解決の確認"""
    print("🔍 解決確認中...")

    # Pre-commitフック確認
    hook_path = Path(".git/hooks/pre-commit")
    if hook_path.exists() and hook_path.is_file():
        print("   ✅ Pre-commitフック設置済み")
    else:
        print("   ❌ Pre-commitフック未設置")

    # 自動化スクリプト確認
    automation_scripts = [
        "scripts/automation/emergency-file-structure-fix.py",
        "scripts/automation/setup-file-structure-prevention.py",
        "scripts/automation/auto-file-placement.py",
        "scripts/automation/file-structure-watcher.py",
    ]

    all_exists = True
    for script in automation_scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"   ✅ {script_path.name}")
        else:
            print(f"   ❌ {script_path.name}")
            all_exists = False

    return all_exists


def main():
    """メイン処理"""
    while True:
        choice = solution_menu()

        if choice == "1":
            # 緊急修正のみ
            print("\n🚨 緊急修正実行中...")
            if execute_emergency_fix():
                print("✅ 緊急修正完了！")
            else:
                print("❌ 緊急修正でエラーが発生しました")

        elif choice == "2":
            # 防止システムのみ
            print("\n🛡️ 防止システム設置中...")
            if setup_prevention_system():
                print("✅ 防止システム設置完了！")
            else:
                print("❌ 防止システム設置でエラーが発生しました")

        elif choice == "3":
            # 完全解決
            print("\n🔄 完全解決実行中...")

            # 1. 緊急修正
            emergency_success = execute_emergency_fix()

            # 2. 防止システム設置
            prevention_success = setup_prevention_system()

            # 3. 確認
            verification_success = verify_solution()

            if emergency_success and prevention_success and verification_success:
                print("\n🎊 完全解決成功！")
                print("📋 今後のファイル作成時:")
                print("   - 自動的に適切な場所に配置されます")
                print("   - 命名規則違反は事前にブロックされます")
                print("   - リアルタイム監視でチェックされます")
            else:
                print("\n⚠️ 一部で問題が発生しました")
                print("詳細を確認して手動で対応してください")

        elif choice == "4":
            # 状況確認のみ
            print("\n📊 状況確認中...")
            has_issues = check_current_status()
            if not has_issues:
                print("✅ 構造的問題は検出されませんでした")
            else:
                print("⚠️ 構造的問題が検出されました。修正を推奨します。")

        elif choice == "5":
            # 終了
            print("👋 解決システムを終了します")
            break

        else:
            print("❌ 無効な選択です")

        print("\n" + "=" * 50)
        input("Enterキーで続行...")
        print()


if __name__ == "__main__":
    main()
