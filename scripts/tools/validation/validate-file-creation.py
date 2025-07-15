#!/usr/bin/env python3
"""
[LEGACY WRAPPER] 厳格ファイル作成検証システム

このスクリプトは unified-validation-tool.py に統合されました。
Phase 6 統合完了 - レガシー互換性のためのwrapperスクリプト

新しい使用方法:
  scripts/tools/unified-validation-tool.py file-validate <paths>
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

print("⚠️  [LEGACY] validate-file-creation.py は統合されました")
print("📦 unified-validation-tool.py file-validate に移行してください")
print("")
print("🔄 自動転送中...")

# 統合ツールの実行
script_dir = Path(__file__).parent
unified_tool = script_dir.parent / "unified-validation-tool.py"

# 引数変換
args = ["file-validate"]
for arg in sys.argv[1:]:
    if arg == "--fix":
        args.append("--auto-fix")
    elif arg in ["-d", "--directory"]:
        args.append("--directory")
    else:
        args.append(arg)

if len(args) == 1:  # パス引数がない場合
    args.append("test-file.txt")

os.execv(sys.executable, [sys.executable, str(unified_tool)] + args)


class FileCreationValidator:
    """エンタープライズグレードのファイル作成検証"""

    def __init__(self):
        self.root = Path(__file__).resolve().parents[1]

        # 検証ルール定義
        self.rules = {
            "naming": {
                "pattern": r"^[a-z0-9]+(-[a-z0-9]+)*$",
                "max_length": {"file": 50, "folder": 40},
                "forbidden_patterns": [r"^[0-9]", r"--", r"-$", r"^-"],
                "reserved_words": {
                    "windows": ["con", "prn", "aux", "nul"]
                    + [f"com{i}" for i in range(1, 10)]
                    + [f"lpt{i}" for i in range(1, 10)],
                    "unix": [".", "..", "~"],
                },
            },
            "structure": {
                "max_depth": 5,
                "placement": {
                    "scripts": {
                        "allowed": [".sh", ".py"],
                        "forbidden": [".md", ".txt", ".json"],
                    },
                    "docs": {
                        "allowed": [".md", ".txt", ".rst"],
                        "forbidden": [".sh", ".py", ".js"],
                    },
                    "config": {
                        "allowed": [".json", ".yml", ".yaml", ".toml", ".env"],
                        "forbidden": [".sh", ".py", ".md"],
                    },
                    "src": {
                        "allowed": [".py", ".js", ".ts", ".jsx", ".tsx"],
                        "forbidden": [".sh", ".md"],
                    },
                },
            },
            "security": {
                "sensitive_patterns": [
                    "secret",
                    "key",
                    "password",
                    "token",
                    "credential",
                    "private",
                ],
                "data_tags": ["-public", "-internal", "-confidential"],
            },
        }

        self.violations = []
        self.warnings = []

    def validate_file_creation(
        self, file_path: str, is_directory: bool = False
    ) -> Tuple[bool, List[str], List[str]]:
        """
        ファイル/フォルダ作成の完全検証

        Returns:
            (is_valid, errors, warnings)
        """
        self.violations = []
        self.warnings = []

        path = Path(file_path)
        name = path.name

        # Phase 1: 命名検証
        self._validate_naming(name, is_directory)

        # Phase 2: 構造検証
        self._validate_structure(path, is_directory)

        # Phase 3: セキュリティ検証
        self._validate_security(path)

        # Phase 4: プラットフォーム互換性
        self._validate_platform_compatibility(name)

        return len(self.violations) == 0, self.violations, self.warnings

    def _validate_naming(self, name: str, is_directory: bool):
        """命名規則検証"""
        # 基本パターンチェック
        if not re.match(self.rules["naming"]["pattern"], name.split(".")[0]):
            self.violations.append(
                f"❌ Invalid name pattern: '{name}' - must use only lowercase letters, numbers, and hyphens"
            )

        # 長さチェック
        max_len = self.rules["naming"]["max_length"][
            "folder" if is_directory else "file"
        ]
        if len(name) > max_len:
            self.violations.append(
                f"❌ Name too long: {len(name)} chars (max: {max_len})"
            )

        # 禁止パターンチェック
        base_name = name.split(".")[0]
        for pattern in self.rules["naming"]["forbidden_patterns"]:
            if re.search(pattern, base_name):
                self.violations.append(
                    f"❌ Forbidden pattern '{pattern}' found in: '{name}'"
                )

        # 拡張子検証（ファイルのみ）
        if not is_directory and "." in name:
            parts = name.split(".")
            if len(parts) > 2:
                self.violations.append(f"❌ Multiple dots forbidden: '{name}'")
            if len(parts) > 1 and len(parts[-1]) > 10:
                self.violations.append(
                    f"❌ Extension too long: '.{parts[-1]}' (max: 10 chars)"
                )

    def _validate_structure(self, path: Path, is_directory: bool):
        """構造ルール検証"""
        # 階層深度チェック
        depth = len(path.parts)
        if depth > self.rules["structure"]["max_depth"]:
            self.violations.append(
                f"❌ Path too deep: {depth} levels (max: {self.rules['structure']['max_depth']})"
            )

        # ディレクトリ配置ルール
        if not is_directory:
            for dir_type, rules in self.rules["structure"]["placement"].items():
                if f"/{dir_type}/" in str(path):
                    ext = path.suffix
                    if ext in rules["forbidden"]:
                        self.violations.append(
                            f"❌ File type '{ext}' not allowed in {dir_type}/"
                        )
                    elif rules["allowed"] and ext not in rules["allowed"]:
                        self.warnings.append(
                            f"⚠️  Unusual file type '{ext}' in {dir_type}/"
                        )

    def _validate_security(self, path: Path):
        """セキュリティ検証"""
        name_lower = path.name.lower()

        # 機密情報パターン検出
        for pattern in self.rules["security"]["sensitive_patterns"]:
            if pattern in name_lower:
                self.violations.append(
                    f"❌ Sensitive pattern '{pattern}' detected in filename"
                )

        # プロダクション環境チェック
        path_str = str(path).lower()
        if any(prod in path_str for prod in ["prod/", "production/"]):
            self.warnings.append(
                "⚠️  Production path detected - ensure proper access controls"
            )

    def _validate_platform_compatibility(self, name: str):
        """プラットフォーム互換性検証"""
        # Windows予約語チェック
        name_lower = name.lower().split(".")[0]
        for reserved in self.rules["naming"]["reserved_words"]["windows"]:
            if name_lower == reserved:
                self.violations.append(f"❌ Windows reserved word: '{name}'")

        # 大文字小文字の衝突可能性
        if name != name.lower():
            self.violations.append(
                f"❌ Must be lowercase to prevent case conflicts: '{name}'"
            )

    def auto_fix_name(self, name: str, is_directory: bool = False) -> str:
        """不正な名前を自動修正"""
        # ベース名と拡張子を分離
        if not is_directory and "." in name:
            parts = name.rsplit(".", 1)
            base_name = parts[0]
            extension = parts[1].lower()
        else:
            base_name = name
            extension = None

        # 修正処理
        fixed = base_name.lower()
        fixed = re.sub(r"[^a-z0-9\-]", "-", fixed)
        fixed = re.sub(r"-+", "-", fixed)
        fixed = fixed.strip("-")

        # 数字開始の修正
        if fixed and fixed[0].isdigit():
            fixed = "file-" + fixed

        # 長さ制限
        max_len = self.rules["naming"]["max_length"][
            "folder" if is_directory else "file"
        ]
        if extension:
            max_len -= len(extension) + 1

        if len(fixed) > max_len:
            fixed = fixed[: max_len - 3] + "..."

        # 拡張子を再結合
        if extension:
            fixed = f"{fixed}.{extension}"

        return fixed

    def generate_metadata(self, file_path: str) -> Dict:
        """必須メタデータ生成"""
        return {
            "path": file_path,
            "owner": os.environ.get("USER", "unknown"),
            "purpose": "TODO: Add purpose description",
            "created_date": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "expires": None,
            "validated": True,
            "auto_fixed": False,
        }

    def create_validation_report(self, results: List[Dict]) -> str:
        """検証レポート生成"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_files": len(results),
            "violations": sum(1 for r in results if not r["valid"]),
            "warnings": sum(len(r.get("warnings", [])) for r in results),
            "auto_fixed": sum(1 for r in results if r.get("auto_fixed")),
            "details": results,
        }

        report_path = (
            self.root
            / "runtime"
            / f"file-validation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(report_path)


def main():
    """CLIエントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(description="厳格ファイル作成検証")
    parser.add_argument("paths", nargs="+", help="検証対象のファイル/フォルダパス")
    parser.add_argument("--fix", action="store_true", help="自動修正を適用")
    parser.add_argument(
        "--directory", "-d", action="store_true", help="ディレクトリとして検証"
    )
    parser.add_argument("--strict", action="store_true", help="警告もエラーとして扱う")

    args = parser.parse_args()

    validator = FileCreationValidator()
    results = []
    has_error = False

    for path in args.paths:
        print(f"\n🔍 Validating: {path}")

        valid, errors, warnings = validator.validate_file_creation(path, args.directory)

        result = {"path": path, "valid": valid, "errors": errors, "warnings": warnings}

        if not valid:
            has_error = True
            for error in errors:
                print(f"   {error}")

            if args.fix:
                fixed_name = validator.auto_fix_name(Path(path).name, args.directory)
                print(f"   🔧 Auto-fix suggestion: '{fixed_name}'")
                result["auto_fixed"] = True
                result["fixed_name"] = fixed_name

        if warnings and (args.strict or not valid):
            for warning in warnings:
                print(f"   {warning}")

        if valid and not warnings:
            print("   ✅ All validations passed")

        # メタデータ生成
        if valid or args.fix:
            metadata = validator.generate_metadata(path)
            result["metadata"] = metadata

        results.append(result)

    # レポート生成
    if len(results) > 1:
        report_path = validator.create_validation_report(results)
        print(f"\n📊 Validation report: {report_path}")

    sys.exit(1 if has_error and not args.fix else 0)


if __name__ == "__main__":
    main()
# === Audio Hooks Integration ===
try:
    import sys

    sys.path.append("src/hooks")
    from audio_hooks_system import emit_validation_result

    def emit_validation_hook(path: str, passed: bool, details: dict = None):
        """検証結果をhooksシステムに送信"""
        emit_validation_result(path, passed, details or {})

except ImportError:

    def emit_validation_hook(path: str, passed: bool, details: dict = None):
        pass  # フォールバック：何もしない
