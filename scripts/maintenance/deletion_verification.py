#!/usr/bin/env python3
"""
削除ファイル検証システム
======================

削除されたファイルの検証と復旧必要分の特定
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class DeletionVerification:
    """削除ファイル検証システム"""

    def __init__(self):
        self.project_root = project_root
        self.backup_dir = self.project_root / "runtime" / "config_backups"
        self.verification_report = (
            self.project_root / "runtime" / "deletion_verification_report.json"
        )

        # 削除されたファイルの記録
        self.deleted_files = {
            "cleaned_files": [
                "test/ai_learning_test.py",
                "runtime/dynamic_mode_test.py",
                "tests/integration_test.py",
                "src/ai/apply_autonomous_fix.py",
                "scripts/setup/quick_api_setup.py",
                "scripts/setup/cloudflare_zero_trust_setup.py",
                "scripts/setup/complete_setup.py",
                "scripts/setup/n8n_auto_setup.py",
                "scripts/setup/supabase_rls_auto_setup.py",
                "scripts/setup/n8n_supabase_debug.py",
                "scripts/setup/simple_n8n_setup.py",
                "scripts/autonomous/supabase_setup.py",
                "tests/integration/test_supabase_final.py",
            ],
            "virtual_env_files": [".venv/", "venv/"],
            "log_files": [
                "runtime/logs/",
                "logs/",
                "runtime/session_violations.log",
                "runtime/president_declaration.log",
                "runtime/template_integrity/",
                "runtime/instruction_logs/",
                "runtime/compression_events.log",
            ],
            "config_files": [
                "config/.mcp.json",
                "config/security/api_keys.json",
                "config/security/rbac_config.json",
                "config/integrations/integration_config.json",
                "config/claude-settings-envvar.json",
                "runtime/log_management_config.json",
                "runtime/mistakes/mistake_config.json",
                "runtime/unified_interceptor_config.json",
            ],
            "duplicate_files": [
                "scripts/setup/n8n_debug_execution.py",
                "scripts/setup/n8n_detailed_error_analysis.py",
                "scripts/setup/n8n_fix_http_node.py",
                "scripts/setup/n8n_debug_webhook.py",
                "scripts/setup/n8n_detailed_error.py",
                "scripts/setup/n8n_full_debug.py",
                "scripts/setup/n8n_create_simple_workflow.py",
                "scripts/setup/n8n_recreate_simple_workflow.py",
                "scripts/setup/ultimate_n8n_solution.py",
                "scripts/setup/hybrid_ultimate_solution.py",
                "scripts/setup/ultimate_solution.py",
                "scripts/setup/hybrid-final.py",
                "scripts/setup/create_working_final_workflow.py",
                "scripts/setup/n8n_complete_rebuild.py",
                "scripts/setup/final_production_test.sh",
                "scripts/setup/final_zero_trust_setup.sh",
            ],
        }

        # 重要度分類
        self.importance_levels = {
            "critical": [
                "src/conductor/core.py",
                "src/enforcement/reference_monitor.py",
                "src/memory/user_prompt_recorder.py",
                "scripts/tools/unified-president-tool.py",
                "CLAUDE.md",
                "Makefile",
            ],
            "high": [
                "src/ai/constitutional_ai.py",
                "src/enforcement/lightweight_president.py",
                "src/enforcement/escalation_system.py",
                "src/enforcement/hook_integration.py",
                "scripts/hooks/critical_failure_prevention.py",
            ],
            "medium": [
                "src/orchestrator/intelligent_project_analyzer.py",
                "scripts/automation/smart_ai_org_launcher.py",
                "config/unified_config.json",
                "src/config/config_loader.py",
            ],
            "low": ["tests/", "docs/", "scripts/setup/"],
        }

    def verify_critical_files(self) -> Dict[str, bool]:
        """重要ファイルの存在確認"""
        results = {}

        for importance, files in self.importance_levels.items():
            for file_path in files:
                full_path = self.project_root / file_path
                if full_path.is_file() or full_path.is_dir():
                    results[file_path] = True
                else:
                    results[file_path] = False
                    print(f"❌ {importance.upper()} ファイル欠損: {file_path}")

        return results

    def analyze_deleted_files(self) -> Dict[str, any]:
        """削除されたファイルの分析"""
        analysis = {
            "total_deleted": 0,
            "categories": {},
            "recovery_needed": [],
            "safe_deletions": [],
        }

        for category, files in self.deleted_files.items():
            analysis["categories"][category] = {"count": len(files), "files": files}
            analysis["total_deleted"] += len(files)

            # 復旧必要性の判定
            if category == "cleaned_files":
                for file_path in files:
                    if self._is_recovery_needed(file_path):
                        analysis["recovery_needed"].append(file_path)
                    else:
                        analysis["safe_deletions"].append(file_path)
            else:
                analysis["safe_deletions"].extend(files)

        return analysis

    def _is_recovery_needed(self, file_path: str) -> bool:
        """復旧必要性の判定"""
        # 重要ファイルリストとの照合
        for _importance, files in self.importance_levels.items():
            if file_path in files or any(file_path.startswith(f) for f in files):
                return True

        # 特定のパターンの確認
        recovery_patterns = [
            "src/ai/constitutional_ai.py",
            "src/memory/",
            "src/enforcement/",
            "scripts/tools/",
            "config/",
        ]

        for pattern in recovery_patterns:
            if file_path.startswith(pattern):
                return True

        return False

    def check_backup_availability(self) -> Dict[str, bool]:
        """バックアップの可用性確認"""
        backup_status = {}

        # 設定ファイルのバックアップ確認
        for backup_file in self.backup_dir.glob("*.json"):
            backup_status[backup_file.name] = backup_file.exists()

        # Gitバックアップの確認
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "10"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            backup_status["git_history"] = result.returncode == 0
        except Exception:
            backup_status["git_history"] = False

        return backup_status

    def generate_recovery_plan(self) -> Dict[str, any]:
        """復旧計画の生成"""
        analysis = self.analyze_deleted_files()
        self.check_backup_availability()

        recovery_plan = {
            "immediate_actions": [],
            "medium_priority": [],
            "low_priority": [],
            "no_action_needed": [],
        }

        # 復旧必要ファイルの分類
        for file_path in analysis["recovery_needed"]:
            if any(
                file_path.startswith(pattern)
                for pattern in ["src/ai/", "src/memory/", "src/enforcement/"]
            ):
                recovery_plan["immediate_actions"].append(
                    {
                        "file": file_path,
                        "reason": "Core system component",
                        "action": "Recreate from backup or git history",
                    }
                )
            elif file_path.startswith("scripts/tools/"):
                recovery_plan["medium_priority"].append(
                    {
                        "file": file_path,
                        "reason": "Important tooling",
                        "action": "Recreate if needed",
                    }
                )
            else:
                recovery_plan["low_priority"].append(
                    {
                        "file": file_path,
                        "reason": "Optional component",
                        "action": "Recreate only if required",
                    }
                )

        # 安全な削除の確認
        recovery_plan["no_action_needed"] = analysis["safe_deletions"]

        return recovery_plan

    def restore_from_backup(self, file_path: str) -> bool:
        """バックアップからの復旧"""
        # 設定ファイルの復旧
        for backup_file in self.backup_dir.glob("*.json"):
            if file_path in backup_file.name:
                try:
                    target_path = self.project_root / file_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(backup_file) as src:
                        with open(target_path, "w") as dst:
                            dst.write(src.read())

                    print(f"✅ 復旧完了: {file_path}")
                    return True
                except Exception as e:
                    print(f"❌ 復旧失敗: {file_path} - {e}")
                    return False

        return False

    def run_verification(self) -> Dict[str, any]:
        """検証メイン実行"""
        print("🔍 削除ファイル検証開始")
        print("=" * 50)

        # 1. 重要ファイルの存在確認
        print("\n1. 重要ファイルの存在確認")
        critical_files = self.verify_critical_files()
        missing_critical = [f for f, exists in critical_files.items() if not exists]

        if missing_critical:
            print(f"❌ 重要ファイル欠損: {len(missing_critical)}件")
            for file_path in missing_critical:
                print(f"  - {file_path}")
        else:
            print("✅ 重要ファイルはすべて存在します")

        # 2. 削除されたファイルの分析
        print("\n2. 削除されたファイルの分析")
        analysis = self.analyze_deleted_files()
        print(f"📊 削除ファイル総数: {analysis['total_deleted']}")
        print(f"🔄 復旧必要: {len(analysis['recovery_needed'])}件")
        print(f"✅ 安全な削除: {len(analysis['safe_deletions'])}件")

        # 3. バックアップ可用性確認
        print("\n3. バックアップ可用性確認")
        backup_status = self.check_backup_availability()
        available_backups = sum(backup_status.values())
        print(f"💾 利用可能バックアップ: {available_backups}件")

        # 4. 復旧計画生成
        print("\n4. 復旧計画生成")
        recovery_plan = self.generate_recovery_plan()
        print(f"🚨 即座対応: {len(recovery_plan['immediate_actions'])}件")
        print(f"⚠️ 中優先: {len(recovery_plan['medium_priority'])}件")
        print(f"ℹ️ 低優先: {len(recovery_plan['low_priority'])}件")
        print(f"✅ 対応不要: {len(recovery_plan['no_action_needed'])}件")

        # 5. 即座対応が必要なファイルの復旧
        print("\n5. 即座対応ファイルの復旧")
        restored_count = 0
        for action in recovery_plan["immediate_actions"]:
            if self.restore_from_backup(action["file"]):
                restored_count += 1

        print(f"✅ 復旧完了: {restored_count}件")

        # 結果レポート
        verification_result = {
            "verification_completed": True,
            "timestamp": datetime.now().isoformat(),
            "critical_files_status": critical_files,
            "missing_critical_files": missing_critical,
            "deletion_analysis": analysis,
            "backup_status": backup_status,
            "recovery_plan": recovery_plan,
            "restored_files": restored_count,
        }

        # レポート保存
        with open(self.verification_report, "w") as f:
            json.dump(verification_result, f, indent=2)

        print(f"\n📝 検証レポート保存: {self.verification_report}")

        return verification_result


def main():
    """メイン実行"""
    verifier = DeletionVerification()

    try:
        result = verifier.run_verification()

        if result["missing_critical_files"]:
            print("\n⚠️ 重要ファイルが不足しています")
            print("💡 必要に応じて復旧を実行してください")
        else:
            print("\n✅ 削除ファイル検証完了")
            print("💡 重要ファイルの損失はありません")

    except Exception as e:
        print(f"\n❌ 検証中にエラーが発生: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
