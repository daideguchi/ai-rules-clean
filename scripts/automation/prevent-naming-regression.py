#!/usr/bin/env python3
"""
命名退行防止システム - 自動監視・検出・修正
"""

import subprocess
from datetime import datetime
from pathlib import Path


class NamingRegressionPreventer:
    def __init__(self):
        self.forbidden_terms = [
            "セキュアPRESIDENT宣言",
            "🔴 セキュアPRESIDENT",
            "PRESIDENT宣言システム",
            "セキュアPRESIDENT宣言開始",
            "セキュアPRESIDENT宣言完了",
        ]

        self.preferred_terms = {
            "セキュアPRESIDENT宣言": "ルール確認",
            "🔴 セキュアPRESIDENT": "✅ ルール確認",
            "PRESIDENT宣言システム": "ルール確認システム",
            "セキュアPRESIDENT宣言開始": "ルール確認開始",
            "セキュアPRESIDENT宣言完了": "ルール確認完了",
        }

        self.excluded_dirs = [".git", "__pycache__", "venv", "node_modules"]

    def detect_violations(self):
        """命名違反検出"""
        violations = []

        for term in self.forbidden_terms:
            try:
                # grep実行
                result = subprocess.run(
                    [
                        "grep",
                        "-r",
                        term,
                        ".",
                        "--exclude-dir=" + ",".join(self.excluded_dirs),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd(),
                )

                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            violations.append(
                                {
                                    "term": term,
                                    "location": line.split(":", 1)[0]
                                    if ":" in line
                                    else line,
                                    "content": line,
                                    "suggested_fix": self.preferred_terms.get(
                                        term, "ルール確認"
                                    ),
                                }
                            )
            except Exception as e:
                print(f"⚠️ 検索エラー: {term} - {e}")

        return violations

    def auto_fix_violations(self, violations):
        """自動修正実行"""
        fixed_files = set()

        for violation in violations:
            term = violation["term"]
            file_path = violation["location"]
            suggested_fix = violation["suggested_fix"]

            try:
                file_obj = Path(file_path)
                if file_obj.exists() and file_obj.is_file():
                    # ファイル読み込み
                    content = file_obj.read_text(encoding="utf-8")

                    # 置換実行
                    if term in content:
                        new_content = content.replace(term, suggested_fix)
                        file_obj.write_text(new_content, encoding="utf-8")
                        fixed_files.add(file_path)
                        print(f"✅ 自動修正: {file_path}")
                        print(f"   {term} → {suggested_fix}")

            except Exception as e:
                print(f"❌ 修正エラー: {file_path} - {e}")

        return list(fixed_files)

    def create_prevention_hook(self):
        """Pre-commitフック作成"""
        hook_content = """#!/bin/bash
# 命名退行防止フック

echo "🔍 命名規則チェック実行中..."

# 禁止表記チェック
VIOLATIONS=0

while IFS= read -r term; do
    if grep -r "$term" . --exclude-dir=.git --exclude-dir=__pycache__ >/dev/null 2>&1; then
        echo "❌ 禁止表記検出: $term"
        echo "   正しい表記: ルール確認"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done << 'EOF'
セキュアPRESIDENT宣言
🔴 セキュアPRESIDENT
PRESIDENT宣言システム
EOF

if [ $VIOLATIONS -gt 0 ]; then
    echo ""
    echo "❌ 命名規則違反が検出されました"
    echo "   自動修正: python3 scripts/automation/prevent-naming-regression.py --fix"
    exit 1
fi

echo "✅ 命名規則チェック完了"
"""

        hook_path = Path(".git/hooks/pre-commit")
        hook_path.parent.mkdir(parents=True, exist_ok=True)

        if hook_path.exists():
            # 既存フックに追加
            existing_content = hook_path.read_text()
            if "命名退行防止フック" not in existing_content:
                hook_path.write_text(existing_content + "\n" + hook_content)
        else:
            # 新規フック作成
            hook_path.write_text(hook_content)

        # 実行権限付与
        hook_path.chmod(0o755)
        print(f"✅ Pre-commitフック設置: {hook_path}")

    def generate_report(self, violations, fixed_files):
        """修正レポート生成"""
        report_content = f"""# 命名退行防止レポート

**実行日時**: {datetime.now().isoformat()}
**検出違反**: {len(violations)}件
**修正ファイル**: {len(fixed_files)}件

## 検出された違反

"""

        for violation in violations:
            report_content += (
                f"- **{violation['term']}** in `{violation['location']}`\n"
            )
            report_content += f"  推奨修正: `{violation['suggested_fix']}`\n\n"

        if fixed_files:
            report_content += "## 自動修正されたファイル\n\n"
            for file_path in fixed_files:
                report_content += f"- `{file_path}`\n"

        report_content += """
## 防止策

1. **Pre-commitフック**: 自動的に禁止表記をブロック
2. **定期監査**: 週次での自動チェック実行
3. **自動修正**: 違反検出時の即座修正

---
**防止システム**: scripts/automation/prevent-naming-regression.py
"""

        report_path = Path("runtime/mistake_prevention/naming_regression_report.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_content)

        return report_path


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description="命名退行防止システム")
    parser.add_argument("--fix", action="store_true", help="自動修正実行")
    parser.add_argument(
        "--setup-hook", action="store_true", help="Pre-commitフック設置"
    )
    args = parser.parse_args()

    preventer = NamingRegressionPreventer()

    print("🛡️ 命名退行防止システム")
    print("=" * 30)

    # 違反検出
    violations = preventer.detect_violations()

    if violations:
        print(f"⚠️ {len(violations)}件の命名違反を検出")

        # 詳細表示
        for violation in violations[:5]:  # 最初の5件のみ表示
            print(f"   ❌ {violation['term']} in {violation['location']}")

        if len(violations) > 5:
            print(f"   ... 他 {len(violations) - 5}件")

        # 自動修正オプション
        if args.fix:
            print("\n🔧 自動修正実行中...")
            fixed_files = preventer.auto_fix_violations(violations)
            print(f"✅ {len(fixed_files)}ファイルを修正完了")
        else:
            print("\n💡 自動修正: --fix オプションを使用")
    else:
        print("✅ 命名違反は検出されませんでした")

    # Pre-commitフック設置
    if args.setup_hook:
        print("\n🔗 Pre-commitフック設置中...")
        preventer.create_prevention_hook()

    # レポート生成
    if violations:
        fixed_files = []
        if args.fix:
            fixed_files = preventer.auto_fix_violations(violations)

        report_path = preventer.generate_report(violations, fixed_files)
        print(f"\n📄 詳細レポート: {report_path}")


if __name__ == "__main__":
    main()
