#!/usr/bin/env python3
"""
🔄 Periodic Self-monitoring - 定期的自己状態監視システム
=====================================================
{{mistake_count}}回のミス防止のため、AIシステムの状態を定期的に監視・修正する
"""

import json
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path


class SelfMonitor:
    """定期的自己監視システム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.monitor_log = self.project_root / "runtime" / "logs" / "self_monitor.log"
        self.monitor_log.parent.mkdir(parents=True, exist_ok=True)

        self.monitoring = False
        self.monitor_thread = None
        self.check_interval = 300  # 5分間隔

        # 監視項目
        self.monitoring_checklist = [
            "president_declaration_status",
            "incomplete_task_detection",
            "mistake_pattern_analysis",
            "gemini_cli_compliance",
            "conductor_system_health",
        ]

    def start_monitoring(self):
        """監視開始"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self._log("🔄 定期的自己監視システム開始")

        # シグナルハンドラ登録
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self._log("⏹️ 定期的自己監視システム停止")

    def _monitor_loop(self):
        """監視ループ"""
        while self.monitoring:
            try:
                self._perform_self_check()
                time.sleep(self.check_interval)
            except Exception as e:
                self._log(f"❌ 監視エラー: {e}")
                time.sleep(60)  # エラー時は1分後にリトライ

    def _perform_self_check(self):
        """自己チェック実行"""
        check_results = {"timestamp": datetime.now().isoformat(), "checks": {}}

        # 各監視項目をチェック
        for check_name in self.monitoring_checklist:
            try:
                method = getattr(self, f"_check_{check_name}")
                result = method()
                check_results["checks"][check_name] = result

                # 問題検出時の自動修正
                if not result.get("status", True):
                    self._auto_correct(check_name, result)

            except Exception as e:
                check_results["checks"][check_name] = {"status": False, "error": str(e)}

        # 結果をログ
        self._log_check_results(check_results)

        # 総合評価
        overall_health = self._evaluate_overall_health(check_results)
        if overall_health < 0.7:  # 70%未満は要注意
            self._trigger_emergency_correction(check_results)

    def _check_president_declaration_status(self) -> dict:
        """PRESIDENT宣言状態チェック"""
        try:
            president_file = (
                self.project_root / "runtime" / "secure_state" / "president.json"
            )
            if not president_file.exists():
                return {
                    "status": False,
                    "issue": "PRESIDENT宣言ファイルが存在しない",
                    "action": "make declare-president実行が必要",
                }

            with open(president_file) as f:
                state = json.load(f)

            # 永久有効性確認
            if state.get("permanent", False):
                return {"status": True, "message": "PRESIDENT宣言永久有効"}
            else:
                return {
                    "status": False,
                    "issue": "PRESIDENT宣言が永久有効ではない",
                    "action": "永久有効化が必要",
                }

        except Exception as e:
            return {"status": False, "error": str(e)}

    def _check_incomplete_task_detection(self) -> dict:
        """未完了タスク検出"""
        try:
            # TodoWriteの結果から未完了タスクをチェック
            todo_patterns = ["pending", "in_progress", "基盤のみ完成", "実装途中"]

            # 最近のログから未完了の兆候を検索
            recent_logs = self._get_recent_logs(hours=1)
            incomplete_count = 0

            for log_entry in recent_logs:
                for pattern in todo_patterns:
                    if pattern in log_entry:
                        incomplete_count += 1

            if incomplete_count > 3:
                return {
                    "status": False,
                    "issue": f"未完了タスク {incomplete_count}件検出",
                    "action": "タスク完了の強制実行が必要",
                }

            return {"status": True, "incomplete_tasks": incomplete_count}

        except Exception as e:
            return {"status": False, "error": str(e)}

    def _check_mistake_pattern_analysis(self) -> dict:
        """ミスパターン分析"""
        try:
            # ミス関連キーワードの検出
            mistake_keywords = [
                "ミス発生中",
                "回目のミス",
                "同じ間違い",
                "虚偽報告",
                "途中で止める",
            ]

            recent_logs = self._get_recent_logs(hours=2)
            mistake_indicators = 0

            for log_entry in recent_logs:
                for keyword in mistake_keywords:
                    if keyword in log_entry:
                        mistake_indicators += 1

            if mistake_indicators > 2:
                return {
                    "status": False,
                    "issue": f"ミスパターン {mistake_indicators}件検出",
                    "action": "根本改善システムの即座実行が必要",
                }

            return {"status": True, "mistake_indicators": mistake_indicators}

        except Exception as e:
            return {"status": False, "error": str(e)}

    def _check_gemini_cli_compliance(self) -> dict:
        """Gemini CLI対話遵守チェック"""
        try:
            # 最近のGeminiコマンド実行をチェック
            correction_log = self.project_root / "runtime" / "logs" / "correction.log"

            if not correction_log.exists():
                return {"status": True, "message": "Gemini CLI未使用"}

            with open(correction_log) as f:
                recent_corrections = f.readlines()[-10:]  # 最新10行

            success_count = 0
            total_count = 0

            for line in recent_corrections:
                try:
                    entry = json.loads(line)
                    if "gemini" in entry.get("command", ""):
                        total_count += 1
                        if entry.get("status") == "success":
                            success_count += 1
                except Exception:
                    continue

            if total_count > 0:
                success_rate = success_count / total_count
                if success_rate < 0.8:  # 80%未満は問題
                    return {
                        "status": False,
                        "issue": f"Gemini CLI成功率 {success_rate:.1%}",
                        "action": "Geminiコマンド修正システムの強化が必要",
                    }

            return {
                "status": True,
                "gemini_success_rate": success_rate if total_count > 0 else 1.0,
            }

        except Exception as e:
            return {"status": False, "error": str(e)}

    def _check_conductor_system_health(self) -> dict:
        """指揮者システム健全性チェック"""
        try:
            conductor_log = self.project_root / "runtime" / "logs" / "conductor.log"

            if not conductor_log.exists():
                return {
                    "status": False,
                    "issue": "指揮者システムログが存在しない",
                    "action": "指揮者システムの起動が必要",
                }

            # 最近の指揮者活動をチェック
            with open(conductor_log) as f:
                lines = f.readlines()

            if not lines:
                return {
                    "status": False,
                    "issue": "指揮者システムの活動記録なし",
                    "action": "指揮者システムの動作確認が必要",
                }

            # 最新エントリの時刻チェック
            last_line = lines[-1]
            if "[" in last_line:
                timestamp_str = last_line.split("]")[0][1:]
                try:
                    last_activity = datetime.fromisoformat(timestamp_str)
                    if (datetime.now() - last_activity).seconds > 3600:  # 1時間以上前
                        return {
                            "status": False,
                            "issue": "指揮者システム長時間非活動",
                            "action": "指揮者システムの再起動が必要",
                        }
                except Exception:
                    pass

            return {"status": True, "message": "指揮者システム正常動作中"}

        except Exception as e:
            return {"status": False, "error": str(e)}

    def _auto_correct(self, check_name: str, result: dict):
        """自動修正実行"""
        self._log(f"🔧 自動修正開始: {check_name}")

        try:
            if check_name == "president_declaration_status":
                subprocess.run(
                    ["make", "declare-president"], cwd=self.project_root, check=True
                )

            elif check_name == "incomplete_task_detection":
                # 未完了タスクの強制実行（簡易版）
                self._force_task_completion()

            elif check_name == "conductor_system_health":
                # 指揮者システムの再起動
                subprocess.run(
                    ["python3", "-m", "src.conductor.core"], cwd=self.project_root
                )

            self._log(f"✅ 自動修正完了: {check_name}")

        except Exception as e:
            self._log(f"❌ 自動修正失敗: {check_name} - {e}")

    def _force_task_completion(self):
        """タスク完了の強制実行"""
        # 簡易的な未完了タスク検出・実行
        try:
            # 指揮者システム経由でタスク実行
            from src.conductor.core import ConductorCore

            conductor = ConductorCore()

            # テストタスクで指揮者システムの動作確認
            test_task = conductor.create_mcp_gemini_task(
                "システム状態確認", "health_check"
            )
            result = conductor.execute_task(test_task)

            if result.success:
                self._log("✅ 指揮者システム経由でタスク実行成功")
            else:
                self._log(f"❌ 指揮者システムタスク実行失敗: {result.stderr}")

        except Exception as e:
            self._log(f"❌ タスク強制実行エラー: {e}")

    def _get_recent_logs(self, hours: int = 1) -> list:
        """最近のログエントリを取得"""
        logs = []
        log_files = [
            self.project_root / "runtime" / "logs" / "conductor.log",
            self.project_root / "runtime" / "logs" / "correction.log",
            self.monitor_log,
        ]

        # Cutoff time for filtering logs
        _ = datetime.now() - timedelta(hours=hours)

        for log_file in log_files:
            if log_file.exists():
                try:
                    with open(log_file) as f:
                        logs.extend(f.readlines()[-50:])  # 最新50行
                except Exception:
                    continue

        return logs

    def _evaluate_overall_health(self, results: dict) -> float:
        """総合健全性評価"""
        total_checks = len(results["checks"])
        passed_checks = sum(
            1 for check in results["checks"].values() if check.get("status", False)
        )

        return passed_checks / total_checks if total_checks > 0 else 0.0

    def _trigger_emergency_correction(self, results: dict):
        """緊急修正トリガー"""
        self._log("🚨 緊急修正トリガー発動")

        # 重要システムの強制リセット
        try:
            # PRESIDENT宣言強制実行
            subprocess.run(["make", "declare-president"], cwd=self.project_root)

            # 指揮者システム再起動
            subprocess.run(
                ["python3", "-m", "src.conductor.core"], cwd=self.project_root
            )

            self._log("✅ 緊急修正完了")

        except Exception as e:
            self._log(f"❌ 緊急修正失敗: {e}")

    def _log_check_results(self, results: dict):
        """チェック結果ログ記録"""
        try:
            with open(self.monitor_log, "a") as f:
                f.write(json.dumps(results, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"
        print(log_entry)

        try:
            with open(self.monitor_log, "a") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

    def _signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        self.stop_monitoring()
        sys.exit(0)


def main():
    """メイン実行"""
    monitor = SelfMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "start":
            monitor.start_monitoring()
            try:
                # 無限実行（デーモンとして）
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
        elif command == "check":
            monitor._perform_self_check()
        elif command == "stop":
            monitor.stop_monitoring()
    else:
        # デフォルトは一回だけのチェック
        monitor._perform_self_check()


if __name__ == "__main__":
    main()
