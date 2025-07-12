#!/usr/bin/env python3
"""
Pre-commit CI Prevention Validator
CI エラーを事前に防ぐための包括的検証システム
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


class PreCommitValidator:
    """CI防止のための事前検証システム"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0

    def log_error(self, message: str):
        """エラーを記録"""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """警告を記録"""
        self.warnings.append(message)
        print(f"⚠️ {message}")

    def log_success(self, message: str):
        """成功を記録"""
        self.checks_passed += 1
        print(f"✅ {message}")

    def run_check(self, check_name: str, check_func) -> bool:
        """チェックを実行"""
        self.checks_total += 1
        print(f"\n🔍 {check_name}")
        print("-" * 50)

        try:
            result = check_func()
            if result:
                self.log_success(f"{check_name} passed")
            return result
        except Exception as e:
            self.log_error(f"{check_name} failed with exception: {e}")
            return False

    def check_python_syntax(self) -> bool:
        """Python構文チェック"""
        python_files = list(self.project_root.rglob("*.py"))
        if not python_files:
            self.log_warning("No Python files found")
            return True

        failed_files = []
        for py_file in python_files:
            try:
                with open(py_file, encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                failed_files.append(f"{py_file}: {e}")
            except Exception as e:
                failed_files.append(f"{py_file}: {e}")

        if failed_files:
            for error in failed_files:
                self.log_error(f"Syntax error: {error}")
            return False

        return True

    def check_ruff_lint(self) -> bool:
        """Ruff linting チェック"""
        try:
            # Ruff が利用可能かチェック
            subprocess.run(['ruff', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_warning("Ruff not available, skipping lint check")
            return True

        try:
            result = subprocess.run(
                ['ruff', 'check', '.'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return True
            else:
                self.log_error("Ruff lint failures found:")
                print(result.stdout)
                print(result.stderr)

                # 自動修正を試行
                print("\n🔧 Attempting automatic fixes...")
                fix_result = subprocess.run(
                    ['ruff', 'check', '--fix', '.'],
                    capture_output=True,
                    text=True
                )

                if fix_result.returncode == 0:
                    self.log_success("Automatic fixes applied successfully")
                    return True
                else:
                    self.log_error("Automatic fixes failed")
                    return False

        except Exception as e:
            self.log_error(f"Ruff check failed: {e}")
            return False

    def check_secret_exposure(self) -> bool:
        """シークレット露出チェック"""
        secret_patterns = [
            r'sk-[a-zA-Z0-9_-]{20,}',  # OpenAI API keys
            r'sk-ant-api03-[a-zA-Z0-9_-]{95}',  # Anthropic API keys
            r'AKIA[0-9A-Z]{16}',  # AWS Access Key
            r'AIza[0-9A-Za-z_-]{35}',  # Google API Key
            r'ghp_[a-zA-Z0-9]{36}',  # GitHub Personal Access Token
        ]

        exposed_secrets = []

        # 検査対象外ファイル
        exclude_patterns = [
            r'\.git/',
            r'__pycache__/',
            r'\.pyc$',
            r'runtime/',
            r'\.backup$',
            r'node_modules/',
        ]

        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir():
                continue

            # 除外パターンチェック
            relative_path = file_path.relative_to(self.project_root)
            if any(re.search(pattern, str(relative_path)) for pattern in exclude_patterns):
                continue

            try:
                with open(file_path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in secret_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        exposed_secrets.append(f"{relative_path}: {match[:15]}...{match[-10:]}")

            except Exception:
                continue

        if exposed_secrets:
            for secret in exposed_secrets:
                self.log_error(f"Potential secret exposure: {secret}")
            return False

        return True

    def check_file_permissions(self) -> bool:
        """ファイル権限チェック"""
        script_files = []
        for pattern in ['*.py', '*.sh']:
            script_files.extend(self.project_root.rglob(pattern))

        permission_issues = []
        for script_file in script_files:
            if script_file.name.startswith(('setup', 'install', 'run', 'start')):
                if not os.access(script_file, os.X_OK):
                    permission_issues.append(str(script_file))

        if permission_issues:
            for issue in permission_issues:
                self.log_warning(f"Script may need execute permission: {issue}")

        return True

    def check_json_validity(self) -> bool:
        """JSON ファイルの妥当性チェック"""
        json_files = list(self.project_root.rglob("*.json"))
        invalid_files = []

        for json_file in json_files:
            try:
                with open(json_file, encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_files.append(f"{json_file}: {e}")
            except Exception as e:
                invalid_files.append(f"{json_file}: {e}")

        if invalid_files:
            for error in invalid_files:
                self.log_error(f"Invalid JSON: {error}")
            return False

        return True

    def check_role_limit_compliance(self) -> bool:
        """役職制限遵守チェック"""
        org_state_path = self.project_root / "src/memory/core/organization_state.json"
        if not org_state_path.exists():
            self.log_warning("organization_state.json not found")
            return True

        try:
            with open(org_state_path, encoding='utf-8') as f:
                data = json.load(f)

            roles = data.get('active_roles', [])
            role_count = len(roles)

            if role_count > 4:
                self.log_error(f"Role count exceeds limit: {role_count} > 4")

                # 自動修正を試行
                print("🔧 Attempting automatic role limit enforcement...")
                try:
                    subprocess.run([
                        'python3',
                        'src/memory/core/auto_role_manager.py',
                        'manage'
                    ], check=True, cwd=self.project_root)
                    self.log_success("Role limit automatically enforced")
                    return True
                except subprocess.CalledProcessError:
                    self.log_error("Failed to automatically enforce role limit")
                    return False

            return True

        except Exception as e:
            self.log_error(f"Failed to check role limit: {e}")
            return False

    def check_import_organization(self) -> bool:
        """import の整理チェック"""
        python_files = list(self.project_root.rglob("*.py"))
        disorganized_files = []

        for py_file in python_files:
            try:
                with open(py_file, encoding='utf-8') as f:
                    lines = f.readlines()

                # import の順序チェック（簡易版）
                import_lines = []
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')):
                        import_lines.append((i, line.strip()))

                if len(import_lines) > 1:
                    # 標準ライブラリ → サードパーティ → ローカル の順序かチェック
                    prev_type = 0
                    for line_num, import_line in import_lines:
                        current_type = self._classify_import(import_line)
                        if current_type < prev_type:
                            disorganized_files.append(str(py_file))
                            break
                        prev_type = current_type

            except Exception:
                continue

        if disorganized_files:
            for file_path in disorganized_files:
                self.log_warning(f"Import organization could be improved: {file_path}")

        return True

    def _classify_import(self, import_line: str) -> int:
        """import の種類を分類（0: 標準, 1: サードパーティ, 2: ローカル）"""
        if 'from .' in import_line or 'from src' in import_line:
            return 2  # ローカル

        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'subprocess',
            'logging', 're', 'typing', 'collections', 'itertools', 'functools'
        }

        module_name = import_line.split()[1].split('.')[0]
        if module_name in stdlib_modules:
            return 0  # 標準ライブラリ

        return 1  # サードパーティ

    def run_comprehensive_validation(self) -> bool:
        """包括的検証を実行"""
        print("🚀 Pre-commit CI Prevention Validator")
        print("=" * 60)
        print("Running comprehensive validation to prevent CI failures...")

        checks = [
            ("Python Syntax Check", self.check_python_syntax),
            ("Ruff Lint Check", self.check_ruff_lint),
            ("Secret Exposure Check", self.check_secret_exposure),
            ("File Permissions Check", self.check_file_permissions),
            ("JSON Validity Check", self.check_json_validity),
            ("Role Limit Compliance", self.check_role_limit_compliance),
            ("Import Organization", self.check_import_organization),
        ]

        all_passed = True
        for check_name, check_func in checks:
            if not self.run_check(check_name, check_func):
                all_passed = False

        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        print(f"✅ Checks passed: {self.checks_passed}/{self.checks_total}")

        if self.warnings:
            print(f"⚠️ Warnings: {len(self.warnings)}")
            for warning in self.warnings[:5]:  # 最初の5個まで表示
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more warnings")

        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors[:5]:  # 最初の5個まで表示
                print(f"  • {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")

        if all_passed and not self.errors:
            print("\n🎉 All validations passed! Safe to commit.")
            return True
        else:
            print("\n⚠️ Issues found. Please fix before committing to prevent CI failures.")
            return False


def main():
    """メイン実行"""
    validator = PreCommitValidator()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--fix":
            print("🔧 Running validation with automatic fixes...")
        elif sys.argv[1] == "--quick":
            print("⚡ Running quick validation...")

    success = validator.run_comprehensive_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()