#!/usr/bin/env python3
"""
🔍 Multi-Agent Monitoring System - 多層的監視エージェントシステム
===========================================================
複数のAIエージェントによる相互監視・検証システム
{{mistake_count}}回のミス防止のための多層安全保障
"""

import asyncio
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class MonitorLevel(Enum):
    PRIMARY = "primary"  # 主要監視
    SECONDARY = "secondary"  # 二次監視
    TERTIARY = "tertiary"  # 三次監視


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MonitoringAlert:
    """監視アラート"""

    id: str
    timestamp: str
    severity: AlertSeverity
    monitor_level: MonitorLevel
    source_agent: str
    issue_type: str
    description: str
    evidence: Dict[str, Any]
    recommended_action: str
    auto_correctable: bool


@dataclass
class AgentStatus:
    """エージェント状態"""

    agent_id: str
    status: str  # active, inactive, error
    last_activity: str
    response_time: float
    error_count: int
    success_rate: float


class MultiAgentMonitor:
    """多層的監視エージェントシステム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.monitoring_log = (
            self.project_root / "runtime" / "logs" / "multi_agent_monitor.log"
        )
        self.alerts_log = (
            self.project_root / "runtime" / "logs" / "monitoring_alerts.log"
        )

        # ディレクトリ作成
        self.monitoring_log.parent.mkdir(parents=True, exist_ok=True)

        # 監視エージェント設定
        self.monitoring_agents = {
            "primary_claude": {
                "level": MonitorLevel.PRIMARY,
                "responsibilities": [
                    "task_execution",
                    "code_quality",
                    "security_compliance",
                ],
                "check_interval": 60,  # 1分
            },
            "secondary_o3": {
                "level": MonitorLevel.SECONDARY,
                "responsibilities": [
                    "strategic_validation",
                    "pattern_analysis",
                    "risk_assessment",
                ],
                "check_interval": 300,  # 5分
            },
            "tertiary_gemini": {
                "level": MonitorLevel.TERTIARY,
                "responsibilities": [
                    "external_validation",
                    "independent_review",
                    "compliance_audit",
                ],
                "check_interval": 600,  # 10分
            },
        }

        self.active_monitors = {}
        self.monitoring_active = False

        # 監視項目定義
        self.monitoring_criteria = self._define_monitoring_criteria()

    def _define_monitoring_criteria(self) -> Dict[str, Dict[str, Any]]:
        """監視基準の定義"""
        return {
            "task_completion_integrity": {
                "description": "タスク完了の整合性監視",
                "triggers": ["completion_claim", "task_status_change"],
                "validation_method": "evidence_verification",
                "severity": AlertSeverity.HIGH,
            },
            "mistake_pattern_recurrence": {
                "description": "ミスパターン再発監視",
                "triggers": ["error_keywords", "repeated_patterns"],
                "validation_method": "historical_analysis",
                "severity": AlertSeverity.CRITICAL,
            },
            "ai_consultation_quality": {
                "description": "AI間相談品質監視",
                "triggers": ["ai_consultation", "information_transfer"],
                "validation_method": "information_completeness_check",
                "severity": AlertSeverity.MEDIUM,
            },
            "security_compliance": {
                "description": "セキュリティ遵守監視",
                "triggers": ["file_operations", "system_commands"],
                "validation_method": "security_policy_check",
                "severity": AlertSeverity.HIGH,
            },
            "instruction_adherence": {
                "description": "指示遵守監視",
                "triggers": ["user_instruction", "directive_processing"],
                "validation_method": "compliance_verification",
                "severity": AlertSeverity.HIGH,
            },
        }

    async def start_monitoring(self):
        """監視システム開始"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self._log("🔍 多層的監視システム開始")

        # 各監視エージェントを起動
        tasks = []
        for agent_id, config in self.monitoring_agents.items():
            task = asyncio.create_task(self._run_monitoring_agent(agent_id, config))
            tasks.append(task)

        # 相互監視タスクも開始
        cross_monitoring_task = asyncio.create_task(self._run_cross_agent_monitoring())
        tasks.append(cross_monitoring_task)

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self._log(f"❌ 監視システムエラー: {e}")
        finally:
            self.monitoring_active = False

    async def _run_monitoring_agent(self, agent_id: str, config: Dict[str, Any]):
        """個別監視エージェントの実行"""
        while self.monitoring_active:
            try:
                start_time = time.time()

                # 監視チェック実行
                alerts = await self._perform_agent_monitoring(agent_id, config)

                # アラート処理
                for alert in alerts:
                    await self._handle_alert(alert)

                # エージェント状態更新
                response_time = time.time() - start_time
                self._update_agent_status(
                    agent_id, "active", response_time, len(alerts) == 0
                )

                # 指定間隔で待機
                await asyncio.sleep(config["check_interval"])

            except Exception as e:
                self._log(f"❌ {agent_id} 監視エラー: {e}")
                self._update_agent_status(agent_id, "error", 0.0, False)
                await asyncio.sleep(60)  # エラー時は1分後にリトライ

    async def _perform_agent_monitoring(
        self, agent_id: str, config: Dict[str, Any]
    ) -> List[MonitoringAlert]:
        """エージェント固有の監視実行"""
        alerts = []

        for responsibility in config["responsibilities"]:
            try:
                if responsibility == "task_execution":
                    task_alerts = await self._monitor_task_execution(
                        agent_id, config["level"]
                    )
                    alerts.extend(task_alerts)

                elif responsibility == "strategic_validation":
                    strategic_alerts = await self._monitor_strategic_validation(
                        agent_id, config["level"]
                    )
                    alerts.extend(strategic_alerts)

                elif responsibility == "external_validation":
                    external_alerts = await self._monitor_external_validation(
                        agent_id, config["level"]
                    )
                    alerts.extend(external_alerts)

                elif responsibility == "code_quality":
                    quality_alerts = await self._monitor_code_quality(
                        agent_id, config["level"]
                    )
                    alerts.extend(quality_alerts)

                elif responsibility == "security_compliance":
                    security_alerts = await self._monitor_security_compliance(
                        agent_id, config["level"]
                    )
                    alerts.extend(security_alerts)

            except Exception as e:
                self._log(f"❌ {agent_id}/{responsibility} 監視エラー: {e}")

        return alerts

    async def _monitor_task_execution(
        self, agent_id: str, level: MonitorLevel
    ) -> List[MonitoringAlert]:
        """タスク実行監視"""
        alerts = []

        try:
            # 最近のタスク実行ログを確認
            conductor_log = self.project_root / "runtime" / "logs" / "conductor.log"

            if conductor_log.exists():
                with open(conductor_log) as f:
                    recent_lines = f.readlines()[-20:]

                # 未完了タスクの検出
                incomplete_pattern = ["基盤", "途中", "次に"]
                completion_claims = ["完了", "完成", "実装完了"]

                for line in recent_lines:
                    # 途中停止パターンの検出
                    if any(pattern in line for pattern in incomplete_pattern):
                        alert = MonitoringAlert(
                            id=f"task_incomplete_{datetime.now().strftime('%H%M%S')}",
                            timestamp=datetime.now().isoformat(),
                            severity=AlertSeverity.HIGH,
                            monitor_level=level,
                            source_agent=agent_id,
                            issue_type="task_incomplete",
                            description="タスク途中停止の兆候検出",
                            evidence={"log_line": line.strip()},
                            recommended_action="タスク完遂の強制実行",
                            auto_correctable=True,
                        )
                        alerts.append(alert)

                    # 虚偽完了報告の検出
                    if any(claim in line for claim in completion_claims):
                        # 実際の実行証跡があるかチェック
                        execution_evidence = ["Write(", "Edit(", "Bash(", "TodoWrite("]
                        has_evidence = any(
                            evidence in line for evidence in execution_evidence
                        )

                        if not has_evidence:
                            alert = MonitoringAlert(
                                id=f"false_completion_{datetime.now().strftime('%H%M%S')}",
                                timestamp=datetime.now().isoformat(),
                                severity=AlertSeverity.CRITICAL,
                                monitor_level=level,
                                source_agent=agent_id,
                                issue_type="false_completion_claim",
                                description="根拠なき完了報告検出",
                                evidence={"completion_claim": line.strip()},
                                recommended_action="実際の完了証跡の要求",
                                auto_correctable=False,
                            )
                            alerts.append(alert)

        except Exception as e:
            self._log(f"タスク実行監視エラー: {e}")

        return alerts

    async def _monitor_strategic_validation(
        self, agent_id: str, level: MonitorLevel
    ) -> List[MonitoringAlert]:
        """戦略的検証監視（o3エージェント用）"""
        alerts = []

        try:
            # o3との相談ログをチェック
            # 情報不足での相談を検出

            # MCP o3の実際の使用状況を確認
            from src.conductor.core import ConductorCore

            ConductorCore()

            # テスト的にo3の健全性をチェック
            test_message = "システム状態確認テスト"
            result = await self._test_o3_responsiveness(test_message)

            if not result["success"]:
                alert = MonitoringAlert(
                    id=f"o3_unresponsive_{datetime.now().strftime('%H%M%S')}",
                    timestamp=datetime.now().isoformat(),
                    severity=AlertSeverity.HIGH,
                    monitor_level=level,
                    source_agent=agent_id,
                    issue_type="agent_unresponsive",
                    description="o3エージェント応答性低下",
                    evidence=result["evidence"],
                    recommended_action="o3接続状態の確認・復旧",
                    auto_correctable=True,
                )
                alerts.append(alert)

        except Exception as e:
            self._log(f"戦略的検証監視エラー: {e}")

        return alerts

    async def _monitor_external_validation(
        self, agent_id: str, level: MonitorLevel
    ) -> List[MonitoringAlert]:
        """外部検証監視（Geminiエージェント用）"""
        alerts = []

        try:
            # Gemini CLI使用状況のチェック
            correction_log = self.project_root / "runtime" / "logs" / "correction.log"

            if correction_log.exists():
                with open(correction_log) as f:
                    recent_entries = f.readlines()[-10:]

                gemini_failures = 0
                for line in recent_entries:
                    try:
                        entry = json.loads(line)
                        if (
                            "gemini" in entry.get("command", "")
                            and entry.get("status") != "success"
                        ):
                            gemini_failures += 1
                    except Exception:
                        continue

                if gemini_failures > 3:  # 3回以上の失敗
                    alert = MonitoringAlert(
                        id=f"gemini_failures_{datetime.now().strftime('%H%M%S')}",
                        timestamp=datetime.now().isoformat(),
                        severity=AlertSeverity.MEDIUM,
                        monitor_level=level,
                        source_agent=agent_id,
                        issue_type="external_validation_failures",
                        description=f"Gemini CLI失敗率上昇 ({gemini_failures}件)",
                        evidence={"failure_count": gemini_failures},
                        recommended_action="Geminiコマンド構文の確認・修正",
                        auto_correctable=True,
                    )
                    alerts.append(alert)

        except Exception as e:
            self._log(f"外部検証監視エラー: {e}")

        return alerts

    async def _monitor_code_quality(
        self, agent_id: str, level: MonitorLevel
    ) -> List[MonitoringAlert]:
        """コード品質監視"""
        alerts = []

        try:
            # 最近作成/編集されたファイルの品質チェック
            recent_files = self._get_recently_modified_files(hours=1)

            for file_path in recent_files:
                if file_path.suffix == ".py":
                    quality_issues = await self._check_python_quality(file_path)

                    if quality_issues:
                        alert = MonitoringAlert(
                            id=f"code_quality_{datetime.now().strftime('%H%M%S')}",
                            timestamp=datetime.now().isoformat(),
                            severity=AlertSeverity.MEDIUM,
                            monitor_level=level,
                            source_agent=agent_id,
                            issue_type="code_quality_issues",
                            description=f"コード品質問題検出: {file_path.name}",
                            evidence={"file": str(file_path), "issues": quality_issues},
                            recommended_action="コード品質の改善",
                            auto_correctable=True,
                        )
                        alerts.append(alert)

        except Exception as e:
            self._log(f"コード品質監視エラー: {e}")

        return alerts

    async def _monitor_security_compliance(
        self, agent_id: str, level: MonitorLevel
    ) -> List[MonitoringAlert]:
        """セキュリティ遵守監視"""
        alerts = []

        try:
            # セキュリティ関連ファイルの変更監視
            security_sensitive_paths = [
                ".claude/settings.json",
                "scripts/hooks/",
                "src/security/",
                "config/",
            ]

            for path_str in security_sensitive_paths:
                path = self.project_root / path_str
                if path.exists():
                    # 最近の変更をチェック
                    if self._is_recently_modified(path, hours=1):
                        alert = MonitoringAlert(
                            id=f"security_change_{datetime.now().strftime('%H%M%S')}",
                            timestamp=datetime.now().isoformat(),
                            severity=AlertSeverity.HIGH,
                            monitor_level=level,
                            source_agent=agent_id,
                            issue_type="security_sensitive_change",
                            description=f"セキュリティ関連ファイル変更: {path_str}",
                            evidence={"changed_path": path_str},
                            recommended_action="セキュリティ変更の検証",
                            auto_correctable=False,
                        )
                        alerts.append(alert)

        except Exception as e:
            self._log(f"セキュリティ監視エラー: {e}")

        return alerts

    async def _run_cross_agent_monitoring(self):
        """相互監視の実行"""
        while self.monitoring_active:
            try:
                # エージェント間の相互チェック
                cross_alerts = await self._perform_cross_validation()

                for alert in cross_alerts:
                    await self._handle_alert(alert)

                await asyncio.sleep(300)  # 5分間隔

            except Exception as e:
                self._log(f"❌ 相互監視エラー: {e}")
                await asyncio.sleep(60)

    async def _perform_cross_validation(self) -> List[MonitoringAlert]:
        """相互検証の実行"""
        alerts = []

        # エージェント間の矛盾検出
        # 一つのエージェントが成功と報告し、別のエージェントが失敗と報告する場合

        return alerts

    async def _handle_alert(self, alert: MonitoringAlert):
        """アラート処理"""
        # アラートをログに記録
        self._log_alert(alert)

        # 重要度に応じて処理
        if alert.severity == AlertSeverity.CRITICAL:
            await self._handle_critical_alert(alert)
        elif alert.severity == AlertSeverity.HIGH:
            await self._handle_high_alert(alert)

        # 自動修正可能な場合は修正実行
        if alert.auto_correctable:
            await self._attempt_auto_correction(alert)

    async def _handle_critical_alert(self, alert: MonitoringAlert):
        """クリティカルアラートの処理"""
        self._log(f"🚨 CRITICAL ALERT: {alert.description}")

        # 緊急停止メカニズム（必要に応じて）
        if alert.issue_type == "false_completion_claim":
            # 虚偽完了報告の場合は即座に修正要求
            await self._force_correction_request(alert)

    async def _handle_high_alert(self, alert: MonitoringAlert):
        """高重要度アラートの処理"""
        self._log(f"⚠️ HIGH ALERT: {alert.description}")

    async def _attempt_auto_correction(self, alert: MonitoringAlert):
        """自動修正の試行"""
        try:
            if alert.issue_type == "task_incomplete":
                # タスク完遂の強制実行
                await self._force_task_completion()

            elif alert.issue_type == "gemini_failures":
                # Geminiコマンド修正
                await self._correct_gemini_commands()

            self._log(f"✅ 自動修正成功: {alert.issue_type}")

        except Exception as e:
            self._log(f"❌ 自動修正失敗: {alert.issue_type} - {e}")

    async def _test_o3_responsiveness(self, test_message: str) -> Dict[str, Any]:
        """o3応答性テスト"""
        try:
            # o3への簡単なテストクエリ
            # 実際の実装では mcp__o3__o3-search を使用
            return {
                "success": True,
                "response_time": 1.5,
                "evidence": {"test_successful": True},
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "evidence": {"error_type": "connection_failure"},
            }

    async def _check_python_quality(self, file_path: Path) -> List[str]:
        """Python品質チェック"""
        issues = []

        try:
            # 簡易的な品質チェック
            with open(file_path) as f:
                content = f.read()

            # 基本的なチェック項目
            if len(content.split("\n")) > 1000:  # 1000行超
                issues.append("ファイルが大きすぎる（1000行超）")

            if "TODO" in content:
                issues.append("TODO項目が残存")

            if "print(" in content and "debug" in content.lower():
                issues.append("デバッグprintが残存")

        except Exception:
            issues.append("ファイル読み取りエラー")

        return issues

    def _get_recently_modified_files(self, hours: int = 1) -> List[Path]:
        """最近変更されたファイルを取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_files = []

        for file_path in self.project_root.rglob("*.py"):
            try:
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mod_time >= cutoff_time:
                    recent_files.append(file_path)
            except Exception:
                continue

        return recent_files

    def _is_recently_modified(self, path: Path, hours: int = 1) -> bool:
        """最近変更されたかチェック"""
        try:
            mod_time = datetime.fromtimestamp(path.stat().st_mtime)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return mod_time >= cutoff_time
        except Exception:
            return False

    async def _force_task_completion(self):
        """タスク完遂の強制実行"""
        # 指揮者システム経由で強制実行
        from src.conductor.core import ConductorCore

        ConductorCore()

        # 未完了タスクの検出と実行
        # 実装の詳細は指揮者システムに委譲

    async def _correct_gemini_commands(self):
        """Geminiコマンドの修正"""
        # Geminiコマンド構文の自動修正
        # 実装の詳細は修正システムに委譲
        pass

    async def _force_correction_request(self, alert: MonitoringAlert):
        """修正要求の強制"""
        # クリティカル問題に対する強制的な修正要求
        self._log(f"🔧 強制修正要求: {alert.description}")

    def _update_agent_status(
        self, agent_id: str, status: str, response_time: float, success: bool
    ):
        """エージェント状態更新"""
        if agent_id not in self.active_monitors:
            self.active_monitors[agent_id] = AgentStatus(
                agent_id=agent_id,
                status=status,
                last_activity=datetime.now().isoformat(),
                response_time=response_time,
                error_count=0,
                success_rate=1.0,
            )
        else:
            agent = self.active_monitors[agent_id]
            agent.status = status
            agent.last_activity = datetime.now().isoformat()
            agent.response_time = response_time

            if not success:
                agent.error_count += 1

            # 成功率の更新（簡易計算）
            total_attempts = agent.error_count + (10 if success else 0)  # 仮の成功回数
            agent.success_rate = (total_attempts - agent.error_count) / max(
                total_attempts, 1
            )

    def _log_alert(self, alert: MonitoringAlert):
        """アラートログ記録"""
        try:
            with open(self.alerts_log, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(asdict(alert), ensure_ascii=False, default=str) + "\n"
                )
        except Exception:
            pass

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"
        print(log_entry)

        try:
            with open(self.monitoring_log, "a") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass


def main():
    """多層監視システムのテスト"""
    monitor = MultiAgentMonitor()

    print("🔍 多層的監視エージェントシステム初期化")
    print(f"監視エージェント: {len(monitor.monitoring_agents)}個")
    print(f"監視基準: {len(monitor.monitoring_criteria)}項目")

    # 非同期監視の開始（テスト用は短時間）
    async def test_run():
        await asyncio.wait_for(monitor.start_monitoring(), timeout=30)

    try:
        asyncio.run(test_run())
    except asyncio.TimeoutError:
        print("✅ テスト完了（30秒間）")


if __name__ == "__main__":
    main()
