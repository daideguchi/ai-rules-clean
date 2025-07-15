#!/usr/bin/env python3
"""
🛡️ プロアクティブファイル保護システム - 多層防御実装
=======================================================

【目的】
- .cursor破壊事件の完全防止
- 事後対応から事前防止への転換
- 重要ファイルの多層保護機構

【技術仕様】
- レイヤー1: Git pre-commit hooks
- レイヤー2: ファイルシステムACL/属性
- レイヤー3: リアルタイム監視
- レイヤー4: 既存の.forbidden-move (事後検証)

【改善効果】
- 現在: ❌ 事後検証のみ → 破壊されてから発見
- 目標: ✅ 多層事前防御 → 破壊を根本的に阻止
"""

import hashlib
import json
import os
import platform
import stat
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ProtectedFile:
    """保護対象ファイル情報"""

    path: Path
    protection_level: str  # critical, important, moderate
    backup_enabled: bool
    monitoring_enabled: bool
    checksum: str = ""
    last_verified: str = ""


class GitHookManager:
    """Git hooks管理 - レイヤー1保護"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.hooks_dir = self.project_root / ".git/hooks"
        self.custom_hooks_dir = self.project_root / ".githooks"

    def setup_protection_hooks(self) -> Dict[str, bool]:
        """保護用Git hooksセットアップ"""
        results = {}

        # カスタムhooksディレクトリ作成
        self.custom_hooks_dir.mkdir(exist_ok=True)

        # Git設定でカスタムhooksディレクトリを指定
        try:
            subprocess.run(
                ["git", "config", "core.hooksPath", str(self.custom_hooks_dir)],
                cwd=self.project_root,
                check=True,
            )
            results["hooks_path_configured"] = True
        except subprocess.CalledProcessError:
            results["hooks_path_configured"] = False

        # 各hookの作成
        hooks = {
            "pre-commit": self._create_pre_commit_hook(),
            "pre-push": self._create_pre_push_hook(),
            "post-commit": self._create_post_commit_hook(),
        }

        for hook_name, hook_content in hooks.items():
            hook_path = self.custom_hooks_dir / hook_name
            try:
                with open(hook_path, "w") as f:
                    f.write(hook_content)
                os.chmod(hook_path, 0o700)
                results[hook_name] = True
            except Exception as e:
                results[hook_name] = False
                print(f"❌ {hook_name} hook作成失敗: {e}")

        return results

    def _create_pre_commit_hook(self) -> str:
        """pre-commit hook作成 - 重要ファイル変更ブロック"""
        return """#!/bin/bash
# 🛡️ PRESIDENT プロアクティブファイル保護システム
# 重要ファイルの変更を事前にブロック

echo "🔍 重要ファイル保護チェック実行中..."

# 保護対象ファイルリスト
PROTECTED_FILES=(
    ".env"
    ".mcp.json"
    ".cursor/rules/globals.mdc"
    ".cursor/rules/work-log.mdc"
    "src/ai/memory/core/"
    "ai-instructions/roles/"
    "scripts/load-env.sh"
    ".forbidden-move"
)

# ステージされた変更ファイルを取得
STAGED_FILES=$(git diff --cached --name-only)

# 保護チェック
BLOCKED_FILES=()
for file in $STAGED_FILES; do
    for protected in "${PROTECTED_FILES[@]}"; do
        if [[ "$file" == *"$protected"* ]]; then
            BLOCKED_FILES+=("$file")
            break
        fi
    done
done

# ブロックされたファイルがある場合
if [ ${#BLOCKED_FILES[@]} -gt 0 ]; then
    echo "🚨 重要ファイル変更ブロック!"
    echo "以下のファイルは保護されています:"
    for blocked in "${BLOCKED_FILES[@]}"; do
        echo "  ❌ $blocked"
    done
    echo ""
    echo "💡 保護解除方法:"
    echo "  1. git reset HEAD <file>  # ステージング解除"
    echo "  2. .forbidden-move を確認"
    echo "  3. 必要に応じて保護レベルを調整"
    echo ""
    exit 1
fi

echo "✅ 重要ファイル保護チェック完了"

# 追加チェック: 巨大ファイル検出
MAX_SIZE_MB=10
LARGE_FILES=$(git diff --cached --name-only | xargs -I {} sh -c 'if [ -f "{}" ] && [ $(stat -f%z "{}" 2>/dev/null || stat -c%s "{}" 2>/dev/null) -gt '$((MAX_SIZE_MB * 1024 * 1024))' ]; then echo "{}"; fi')

if [ ! -z "$LARGE_FILES" ]; then
    echo "⚠️  巨大ファイル検出 (>${MAX_SIZE_MB}MB):"
    echo "$LARGE_FILES"
    echo "Git LFS使用を検討してください"
fi

exit 0
"""

    def _create_pre_push_hook(self) -> str:
        """pre-push hook作成 - 機密情報チェック"""
        return """#!/bin/bash
# 🔒 機密情報流出防止チェック

echo "🔍 機密情報チェック実行中..."

# APIキーパターン検出
API_KEY_PATTERNS=(
    "sk-[a-zA-Z0-9]{48}"
    "AIza[a-zA-Z0-9_-]{35}"
    "AKIA[0-9A-Z]{16}"
)

SENSITIVE_FOUND=false
for pattern in "${API_KEY_PATTERNS[@]}"; do
    if git log --oneline -n 10 | xargs git show | grep -E "$pattern" > /dev/null; then
        echo "🚨 APIキーパターン検出: $pattern"
        SENSITIVE_FOUND=true
    fi
done

if [ "$SENSITIVE_FOUND" = true ]; then
    echo "❌ 機密情報が含まれているためpushをブロックしました"
    echo "💡 修正方法:"
    echo "  1. git log --oneline で該当コミットを確認"
    echo "  2. git rebase -i でコミット修正"
    echo "  3. .env.example を使用して機密情報を除外"
    exit 1
fi

echo "✅ 機密情報チェック完了"
exit 0
"""

    def _create_post_commit_hook(self) -> str:
        """post-commit hook作成 - 保護ファイル検証"""
        return """#!/bin/bash
# 📊 コミット後の保護ファイル検証

echo "🔍 保護ファイル整合性チェック..."

# 重要ファイルの存在確認
CRITICAL_FILES=(
    ".env"
    ".cursor/rules/globals.mdc"
    "src/ai/memory/core/session-bridge.sh"
)

MISSING_FILES=()
for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "⚠️  重要ファイル欠損検出:"
    for missing in "${MISSING_FILES[@]}"; do
        echo "  ❌ $missing"
    done
    echo "💡 緊急復旧が必要です"
fi

echo "✅ 保護ファイル検証完了"
"""


class FileSystemProtector:
    """ファイルシステム保護 - レイヤー2保護"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"

    def apply_file_attributes(
        self, protected_files: List[ProtectedFile]
    ) -> Dict[str, bool]:
        """ファイル属性による保護適用"""
        results = {}

        for pfile in protected_files:
            if not pfile.path.exists():
                results[str(pfile.path)] = False
                continue

            try:
                if pfile.protection_level == "critical":
                    # 最高レベル保護
                    if self.is_macos:
                        # macOS: uchg (user immutable) フラグ
                        subprocess.run(["chflags", "uchg", str(pfile.path)], check=True)
                    elif self.is_linux:
                        # Linux: immutable属性
                        subprocess.run(["chattr", "+i", str(pfile.path)], check=True)

                    # 読み取り専用設定
                    pfile.path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

                elif pfile.protection_level == "important":
                    # 重要レベル保護 (読み取り専用)
                    pfile.path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

                results[str(pfile.path)] = True

            except (subprocess.CalledProcessError, PermissionError) as e:
                results[str(pfile.path)] = False
                print(f"⚠️  ファイル保護適用失敗 {pfile.path}: {e}")

        return results

    def remove_file_attributes(
        self, protected_files: List[ProtectedFile]
    ) -> Dict[str, bool]:
        """保護属性解除"""
        results = {}

        for pfile in protected_files:
            if not pfile.path.exists():
                continue

            try:
                if self.is_macos:
                    subprocess.run(
                        ["chflags", "nouchg", str(pfile.path)], check=False
                    )  # エラーは無視
                elif self.is_linux:
                    subprocess.run(
                        ["chattr", "-i", str(pfile.path)], check=False
                    )  # エラーは無視

                # 通常の権限に戻す
                pfile.path.chmod(
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                )
                results[str(pfile.path)] = True

            except Exception as e:
                results[str(pfile.path)] = False
                print(f"⚠️  保護解除失敗 {pfile.path}: {e}")

        return results


class FileIntegrityMonitor:
    """ファイル整合性監視 - レイヤー3保護"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.integrity_db = self.project_root / ".file_integrity.json"

    def calculate_checksum(self, file_path: Path) -> str:
        """ファイルのチェックサム計算"""
        if not file_path.exists():
            return ""

        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""

    def create_integrity_baseline(
        self, protected_files: List[ProtectedFile]
    ) -> Dict[str, str]:
        """整合性ベースライン作成"""
        baseline = {}

        for pfile in protected_files:
            checksum = self.calculate_checksum(pfile.path)
            if checksum:
                baseline[str(pfile.path)] = {
                    "checksum": checksum,
                    "last_verified": datetime.now().isoformat(),
                    "protection_level": pfile.protection_level,
                }

        # ベースライン保存
        with open(self.integrity_db, "w") as f:
            json.dump(baseline, f, indent=2)

        return baseline

    def verify_integrity(self) -> Dict[str, Any]:
        """ファイル整合性検証"""
        if not self.integrity_db.exists():
            return {"error": "整合性ベースラインが存在しません"}

        with open(self.integrity_db) as f:
            baseline = json.load(f)

        verification_results = {
            "timestamp": datetime.now().isoformat(),
            "verified_files": 0,
            "modified_files": [],
            "missing_files": [],
            "errors": [],
        }

        for file_path, file_info in baseline.items():
            path = Path(file_path)

            if not path.exists():
                verification_results["missing_files"].append(file_path)
                continue

            current_checksum = self.calculate_checksum(path)
            if current_checksum != file_info["checksum"]:
                verification_results["modified_files"].append(
                    {
                        "file": file_path,
                        "expected_checksum": file_info["checksum"],
                        "current_checksum": current_checksum,
                        "protection_level": file_info["protection_level"],
                    }
                )
            else:
                verification_results["verified_files"] += 1

        return verification_results


class ProactiveFileGuard:
    """統合プロアクティブファイル保護システム"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.git_hook_manager = GitHookManager(project_root)
        self.fs_protector = FileSystemProtector(project_root)
        self.integrity_monitor = FileIntegrityMonitor(project_root)

        # 保護対象ファイル定義
        self.protected_files = self._load_protected_files()

    def _load_protected_files(self) -> List[ProtectedFile]:
        """保護対象ファイルの読み込み"""
        # .forbidden-moveから読み込み
        forbidden_move_file = self.project_root / ".forbidden-move"
        protected_files = []

        if forbidden_move_file.exists():
            with open(forbidden_move_file, encoding="utf-8") as f:
                content = f.read()

            # パース（簡易版）
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # ファイルパス抽出
                    parts = line.split()
                    if parts:
                        file_path = self.project_root / parts[0]

                        # 保護レベル判定
                        if "最重要" in line or "即座にシステム破綻" in line:
                            protection_level = "critical"
                        elif "重要" in line:
                            protection_level = "important"
                        else:
                            protection_level = "moderate"

                        protected_files.append(
                            ProtectedFile(
                                path=file_path,
                                protection_level=protection_level,
                                backup_enabled=True,
                                monitoring_enabled=True,
                            )
                        )

        return protected_files

    def enable_full_protection(self) -> Dict[str, Any]:
        """全層保護の有効化"""
        print("🛡️ プロアクティブファイル保護システム有効化中...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "git_hooks": {},
            "file_attributes": {},
            "integrity_baseline": {},
            "total_protected_files": len(self.protected_files),
        }

        # レイヤー1: Git hooks
        print("📋 レイヤー1: Git hooks設定...")
        results["git_hooks"] = self.git_hook_manager.setup_protection_hooks()

        # レイヤー2: ファイルシステム保護
        print("🔒 レイヤー2: ファイル属性保護...")
        results["file_attributes"] = self.fs_protector.apply_file_attributes(
            self.protected_files
        )

        # レイヤー3: 整合性ベースライン
        print("📊 レイヤー3: 整合性ベースライン作成...")
        results["integrity_baseline"] = (
            self.integrity_monitor.create_integrity_baseline(self.protected_files)
        )

        # 設定保存
        config_file = self.project_root / ".proactive_protection.json"
        with open(config_file, "w") as f:
            json.dump(results, f, indent=2)

        print("✅ プロアクティブファイル保護システム有効化完了")
        return results

    def disable_protection(self) -> Dict[str, Any]:
        """保護の無効化（メンテナンス用）"""
        print("🔧 保護システム無効化中...")

        # ファイル属性解除
        results = self.fs_protector.remove_file_attributes(self.protected_files)

        print("✅ 保護システム無効化完了")
        return results

    def verify_protection_status(self) -> Dict[str, Any]:
        """保護状態の確認"""
        return {
            "timestamp": datetime.now().isoformat(),
            "git_hooks_configured": (self.project_root / ".githooks").exists(),
            "integrity_verification": self.integrity_monitor.verify_integrity(),
            "protected_files_count": len(self.protected_files),
        }


def main():
    """メイン実行 - 保護システムテスト"""
    project_root = Path(__file__).parent.parent.parent.parent

    # プロアクティブ保護システム初期化
    guard = ProactiveFileGuard(project_root)

    print("🛡️ プロアクティブファイル保護システム テスト")
    print(f"📁 プロジェクトルート: {project_root}")
    print(f"🔒 保護対象ファイル数: {len(guard.protected_files)}")

    # 保護有効化
    guard.enable_full_protection()

    # 状態確認
    status = guard.verify_protection_status()

    print("\n📊 保護状態確認:")
    print(f"  - Git hooks: {'✅' if status['git_hooks_configured'] else '❌'}")
    print(
        f"  - 整合性ベースライン: {'✅' if status['integrity_verification'].get('verified_files', 0) > 0 else '❌'}"
    )

    # 重要: テスト後は保護を無効化
    print("\n🔧 テスト完了 - 保護無効化...")
    guard.disable_protection()


if __name__ == "__main__":
    main()
