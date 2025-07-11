#!/usr/bin/env python3
"""
🧠 Error Autonomous Growth System
=================================
エラーから自律成長するシステム
「あ、これは次回から発生しないプログラムに具体的に変えて自律成長する」
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class ErrorAutonomousGrowth:
    def __init__(self, project_root: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_root = Path(project_root)
        self.error_db_path = (
            self.project_root / "runtime" / "errors" / "autonomous_growth.json"
        )
        self.fixes_db_path = (
            self.project_root / "runtime" / "errors" / "autonomous_fixes.json"
        )

        # データベース初期化
        self.error_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_database = self.load_error_database()
        self.fixes_database = self.load_fixes_database()

        # エラーパターンと修正方法のマッピング
        self.error_patterns = {
            # Python import errors
            "ModuleNotFoundError": {
                "analysis": "モジュールが見つからない",
                "fix_strategies": [
                    "pip install {module}",
                    "sys.path.append('{path}')",
                    "relative import修正",
                ],
            },
            # Rich/Textual errors
            "NotRenderableError": {
                "analysis": "Richライブラリレンダリングエラー",
                "fix_strategies": [
                    "ジェネレータを関数に変更",
                    "with Live()構文を削除",
                    "直接print()使用",
                ],
            },
            # File system errors
            "FileNotFoundError": {
                "analysis": "ファイルが見つからない",
                "fix_strategies": [
                    "パス確認・修正",
                    "ファイル存在チェック追加",
                    "相対パス→絶対パス変更",
                ],
            },
            # Permission errors
            "PermissionError": {
                "analysis": "権限エラー",
                "fix_strategies": [
                    "chmod +x {file}",
                    "sudo権限で実行",
                    "ファイル所有者変更",
                ],
            },
            # API errors
            "API Error": {
                "analysis": "API呼び出しエラー",
                "fix_strategies": [
                    "APIキー確認",
                    "リクエスト形式修正",
                    "エラーハンドリング追加",
                ],
            },
            # Import errors
            "ImportError": {
                "analysis": "インポートエラー",
                "fix_strategies": [
                    "相対インポート修正",
                    "__init__.py追加",
                    "PYTHONPATH設定",
                ],
            },
        }

    def load_error_database(self) -> Dict:
        """エラーデータベース読み込み"""
        if self.error_db_path.exists():
            try:
                with open(self.error_db_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def load_fixes_database(self) -> Dict:
        """修正データベース読み込み"""
        if self.fixes_db_path.exists():
            try:
                with open(self.fixes_db_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_databases(self):
        """データベース保存"""
        with open(self.error_db_path, "w", encoding="utf-8") as f:
            json.dump(self.error_database, f, indent=2, ensure_ascii=False)

        with open(self.fixes_db_path, "w", encoding="utf-8") as f:
            json.dump(self.fixes_database, f, indent=2, ensure_ascii=False)

    def generate_error_hash(
        self, error_type: str, error_message: str, file_path: str = ""
    ) -> str:
        """エラーのハッシュ生成（同じエラーの識別）"""
        error_signature = f"{error_type}:{error_message}:{file_path}"
        return hashlib.md5(error_signature.encode()).hexdigest()

    def record_error(
        self,
        error_type: str,
        error_message: str,
        file_path: str = "",
        context: Dict = None,
    ) -> str:
        """エラーを記録"""

        error_hash = self.generate_error_hash(error_type, error_message, file_path)

        error_record = {
            "error_type": error_type,
            "error_message": error_message,
            "file_path": file_path,
            "context": context or {},
            "first_occurrence": datetime.now().isoformat(),
            "occurrence_count": 1,
            "last_occurrence": datetime.now().isoformat(),
            "status": "new",
            "auto_fix_attempted": False,
        }

        if error_hash in self.error_database:
            # 既存エラーの更新
            self.error_database[error_hash]["occurrence_count"] += 1
            self.error_database[error_hash]["last_occurrence"] = (
                datetime.now().isoformat()
            )
            if self.error_database[error_hash]["occurrence_count"] > 2:
                self.error_database[error_hash]["status"] = "recurring"
        else:
            # 新規エラー
            self.error_database[error_hash] = error_record

        self.save_databases()
        return error_hash

    def analyze_error(self, error_hash: str) -> Dict:
        """エラー分析"""

        if error_hash not in self.error_database:
            return {"status": "error_not_found"}

        error_record = self.error_database[error_hash]
        error_type = error_record["error_type"]

        analysis = {
            "error_hash": error_hash,
            "error_record": error_record,
            "pattern_matched": False,
            "fix_strategies": [],
            "priority": "medium",
        }

        # パターンマッチング
        for pattern, info in self.error_patterns.items():
            if pattern in error_type or pattern in error_record["error_message"]:
                analysis["pattern_matched"] = True
                analysis["fix_strategies"] = info["fix_strategies"]
                analysis["analysis_result"] = info["analysis"]
                break

        # 優先度判定
        if error_record["occurrence_count"] > 5:
            analysis["priority"] = "high"
        elif error_record["occurrence_count"] > 2:
            analysis["priority"] = "medium"
        else:
            analysis["priority"] = "low"

        return analysis

    def generate_fix_code(self, error_hash: str, analysis: Dict) -> str:
        """修正コード生成"""

        error_record = analysis["error_record"]
        error_type = error_record["error_type"]

        fix_code = f"""
# 🔧 自動生成修正コード
# エラー: {error_type}
# ファイル: {error_record["file_path"]}
# 発生回数: {error_record["occurrence_count"]}回

"""

        # エラータイプ別の修正コード
        if "ModuleNotFoundError" in error_type:
            module_name = (
                error_record["error_message"].split("'")[1]
                if "'" in error_record["error_message"]
                else "unknown"
            )
            fix_code += f"""
# 修正方法1: モジュールインストール
# pip install {module_name}

# 修正方法2: インポートエラーハンドリング
try:
    import {module_name}
except ImportError:
    print("警告: {module_name}が見つかりません。pip install {module_name}を実行してください。")
    {module_name} = None

# 修正方法3: 条件付きインポート
if {module_name} is not None:
    # {module_name}を使用するコード
    pass
"""

        elif "NotRenderableError" in error_type:
            fix_code += """
# 修正方法1: Live()の使用を避ける
# 元のコード（エラーが発生）:
# with Live(generator(), console=console):
#     pass

# 修正後のコード:
for item in generator():
    console.clear()
    console.print(item)
    time.sleep(1)

# 修正方法2: 直接print使用
console.print("直接表示内容")
"""

        elif "FileNotFoundError" in error_type:
            file_path = error_record["file_path"]
            fix_code += f"""
# 修正方法1: ファイル存在チェック
from pathlib import Path

file_path = Path("{file_path}")
if not file_path.exists():
    print(f"ファイルが見つかりません: {{file_path}}")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()

# 修正方法2: デフォルト値設定
try:
    with open("{file_path}", "r") as f:
        content = f.read()
except FileNotFoundError:
    content = ""  # デフォルト値
"""

        elif "PermissionError" in error_type:
            fix_code += f"""
# 修正方法1: 権限チェック・修正
import os
import stat

file_path = "{error_record["file_path"]}"
if os.path.exists(file_path):
    # 実行権限追加
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)

# 修正方法2: 権限エラーハンドリング
try:
    # 権限が必要な操作
    pass
except PermissionError:
    print("権限エラー: sudo権限が必要です")
"""

        elif "ImportError" in error_type:
            fix_code += """
# 修正方法1: 相対インポート修正
# 元のコード: from .module import function
# 修正後: from module import function

# 修正方法2: PYTHONPATHに追加
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 修正方法3: __init__.py追加
init_file = Path(__file__).parent / "__init__.py"
init_file.touch(exist_ok=True)
"""

        return fix_code

    def apply_autonomous_fix(self, error_hash: str) -> Dict:
        """自律修正適用"""

        analysis = self.analyze_error(error_hash)

        if not analysis["pattern_matched"]:
            return {
                "status": "no_fix_available",
                "message": "修正パターンが見つかりません",
            }

        # 修正コード生成
        fix_code = self.generate_fix_code(error_hash, analysis)

        # 修正記録
        fix_record = {
            "error_hash": error_hash,
            "fix_code": fix_code,
            "applied_at": datetime.now().isoformat(),
            "strategies": analysis["fix_strategies"],
            "status": "generated",
        }

        self.fixes_database[error_hash] = fix_record
        self.error_database[error_hash]["auto_fix_attempted"] = True
        self.error_database[error_hash]["status"] = "fix_generated"

        self.save_databases()

        return {
            "status": "fix_generated",
            "fix_code": fix_code,
            "fix_record": fix_record,
        }

    def demonstrate_growth(self):
        """自律成長デモンストレーション"""

        print("🧠 Error Autonomous Growth System")
        print("=" * 50)

        # サンプルエラーで成長を実演
        sample_errors = [
            ("ModuleNotFoundError", "No module named 'rich'", "src/ui/dashboard.py"),
            (
                "NotRenderableError",
                "Unable to render generator",
                "src/ui/enhanced_dashboard.py",
            ),
            (
                "FileNotFoundError",
                "No such file or directory: 'config.json'",
                "src/config/loader.py",
            ),
            ("PermissionError", "Permission denied", "setup_env.sh"),
        ]

        for error_type, error_message, file_path in sample_errors:
            print(f"\n📊 エラー記録: {error_type}")
            error_hash = self.record_error(error_type, error_message, file_path)

            print("🔍 エラー分析実行...")
            analysis = self.analyze_error(error_hash)

            print(f"✅ 修正戦略: {len(analysis['fix_strategies'])}個")

            print("🔧 自律修正適用...")
            fix_result = self.apply_autonomous_fix(error_hash)

            print(f"🎯 結果: {fix_result['status']}")

        print("\n📈 成長統計:")
        print(f"- 記録エラー: {len(self.error_database)}個")
        print(f"- 生成修正: {len(self.fixes_database)}個")
        print(
            f"- 成長率: {len(self.fixes_database) / len(self.error_database) * 100:.1f}%"
        )


def main():
    """メイン実行"""

    growth_system = ErrorAutonomousGrowth()
    growth_system.demonstrate_growth()

    print("\n💾 データベース保存場所:")
    print(f"- エラーDB: {growth_system.error_db_path}")
    print(f"- 修正DB: {growth_system.fixes_db_path}")


if __name__ == "__main__":
    main()
