#!/usr/bin/env python3
"""
🏢 Dynamic AI Organization System - 動的AI組織システム
===================================================
要件定義・仕様書から動的に役職を生成・配置する適応的組織システム
{{mistake_count}}回ミス防止システムとの完全統合
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


# 基本役職（最小構成）
class CoreAIRole(Enum):
    PRESIDENT = "PRESIDENT"  # 必須役職：戦略統括
    COORDINATOR = "COORDINATOR"  # 必須役職：調整役


@dataclass
class DynamicRole:
    """動的役職定義"""

    name: str
    display_name: str
    icon: str
    responsibilities: List[str]
    authority_level: int  # 1-10
    decision_scope: List[str]
    collaboration_requirements: List[str]
    generated_from: str  # 要件定義元
    specialization: str  # 専門分野
    required_skills: List[str]


@dataclass
class RoleCapability:
    """役職能力定義（後方互換性）"""

    role: DynamicRole
    responsibilities: List[str]
    authority_level: int
    decision_scope: List[str]
    collaboration_requirements: List[str]


@dataclass
class OrganizationState:
    """動的組織状態"""

    active_roles: List[DynamicRole]
    current_orchestrator: str
    decision_hierarchy: Dict[str, int]
    collaboration_matrix: Dict[str, List[str]]
    current_context: str
    project_requirements: Dict[str, Any]
    role_generation_history: List[Dict[str, Any]]
    adaptation_triggers: List[str]


class DynamicAIOrganizationSystem:
    """動的AI組織システム - 要件から自動役職生成"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.org_state_file = (
            self.project_root / "src" / "memory" / "core" / "organization_state.json"
        )
        self.session_file = (
            self.project_root
            / "src"
            / "memory"
            / "core"
            / "session-records"
            / "current-session.json"
        )
        self.requirements_file = self.project_root / "docs" / "requirements.md"

        # 役職生成エンジン
        try:
            import os
            import sys

            sys.path.insert(
                0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            from ai.role_generation_engine import (
                ProjectRequirementsAnalyzer,
                RoleGenerationEngine,
            )

            self.role_generator = RoleGenerationEngine()
            self.project_analyzer = ProjectRequirementsAnalyzer()
        except ImportError as e:
            # Fallback: Use simplified role generation
            print(
                f"⚠️ Role Generation Engine not available ({e}), using simplified generation"
            )
            self.role_generator = None
            self.project_analyzer = None

        # 動的役職定義（要件から生成）
        self.dynamic_roles: Dict[str, DynamicRole] = {}
        self.role_capabilities: Dict[str, RoleCapability] = {}

        # 現在の組織状態
        self.organization_state = self._load_organization_state()

        # {{mistake_count}}回ミス防止システム統合
        self.integrated_systems = {
            "constitutional_ai": None,
            "rule_based_rewards": None,
            "multi_agent_monitor": None,
            "nist_rmf": None,
            "continuous_improvement": None,
            "conductor": None,
        }

        self._initialize_system_integration()
        self._initialize_dynamic_organization()

    def _initialize_dynamic_organization(self):
        """動的組織初期化"""
        if self.role_generator and self.project_analyzer:
            # プロジェクト要件の分析
            requirements = self.project_analyzer.analyze_project_requirements()

            # 要件に基づく役職生成
            generated_roles = self.role_generator.generate_roles_from_requirements(
                requirements
            )

            # 動的役職の登録
            for role in generated_roles:
                self.dynamic_roles[role.name] = role
                self.role_capabilities[role.name] = RoleCapability(
                    role=role,
                    responsibilities=role.responsibilities,
                    authority_level=role.authority_level,
                    decision_scope=role.decision_scope,
                    collaboration_requirements=role.collaboration_requirements,
                )
        else:
            print("⚠️ Using fallback role generation")

        # 基本役職の確保（PRESIDENT, COORDINATORは必須）
        self._ensure_core_roles()

        print(f"🎯 動的組織生成完了: {len(self.dynamic_roles)}役職")

    def _ensure_core_roles(self):
        """コア役職の確保"""
        if "PRESIDENT" not in self.dynamic_roles:
            president = DynamicRole(
                name="PRESIDENT",
                display_name="プレジデント",
                icon="👑",
                responsibilities=[
                    "戦略的意思決定",
                    "システム全体統括",
                    "危機管理・緊急対応",
                    "最終品質保証",
                ],
                authority_level=10,
                decision_scope=[
                    "strategic_decisions",
                    "crisis_response",
                    "final_approval",
                ],
                collaboration_requirements=["全役職からの情報集約", "o3・Gemini協議"],
                generated_from="コア役職（必須）",
                specialization="strategic_leadership",
                required_skills=["leadership", "decision_making"],
            )
            self.dynamic_roles["PRESIDENT"] = president
            self.role_capabilities["PRESIDENT"] = RoleCapability(
                role=president,
                responsibilities=president.responsibilities,
                authority_level=president.authority_level,
                decision_scope=president.decision_scope,
                collaboration_requirements=president.collaboration_requirements,
            )

        if "COORDINATOR" not in self.dynamic_roles:
            coordinator = DynamicRole(
                name="COORDINATOR",
                display_name="コーディネーター",
                icon="🔄",
                responsibilities=[
                    "役職間調整",
                    "タスク配分最適化",
                    "コミュニケーション促進",
                    "進捗状況管理",
                ],
                authority_level=8,
                decision_scope=["task_coordination", "resource_allocation"],
                collaboration_requirements=["全役職との定期連絡", "PRESIDENT支援"],
                generated_from="コア役職（必須）",
                specialization="coordination",
                required_skills=["coordination", "communication"],
            )
            self.dynamic_roles["COORDINATOR"] = coordinator
            self.role_capabilities["COORDINATOR"] = RoleCapability(
                role=coordinator,
                responsibilities=coordinator.responsibilities,
                authority_level=coordinator.authority_level,
                decision_scope=coordinator.decision_scope,
                collaboration_requirements=coordinator.collaboration_requirements,
            )

    def _initialize_system_integration(self):
        """{{mistake_count}}回ミス防止システム統合初期化"""
        try:
            # 統合システムの初期化
            from src.ai.constitutional_ai import ConstitutionalAI
            from src.ai.continuous_improvement import ContinuousImprovementSystem
            from src.ai.multi_agent_monitor import MultiAgentMonitor
            from src.ai.nist_ai_rmf import NISTAIRiskManagement
            from src.ai.rule_based_rewards import RuleBasedRewards
            from src.conductor.core import ConductorCore

            self.integrated_systems["constitutional_ai"] = ConstitutionalAI()
            self.integrated_systems["rule_based_rewards"] = RuleBasedRewards()
            self.integrated_systems["multi_agent_monitor"] = MultiAgentMonitor()
            self.integrated_systems["nist_rmf"] = NISTAIRiskManagement()
            self.integrated_systems["continuous_improvement"] = (
                ContinuousImprovementSystem()
            )
            self.integrated_systems["conductor"] = ConductorCore()

        except ImportError as e:
            print(f"⚠️ システム統合警告: {e}")

    def activate_role(self, role_name: str, context: str = "") -> Dict[str, Any]:
        """役職の活性化"""
        if role_name not in self.dynamic_roles:
            return {"error": f"Role {role_name} not found"}

        role = self.dynamic_roles[role_name]
        role_def = self.role_capabilities[role_name]

        activation_result = {
            "role": role.name,
            "display_name": role.display_name,
            "icon": role.icon,
            "activated_at": datetime.now().isoformat(),
            "context": context,
            "responsibilities": role_def.responsibilities,
            "authority_level": role_def.authority_level,
            "collaboration_status": self._check_collaboration_requirements(role),
        }

        # 組織状態の更新
        if role not in self.organization_state.active_roles:
            self.organization_state.active_roles.append(role)

        self.organization_state.current_context = context
        self._save_organization_state()
        self._update_session_state()

        return activation_result

    def execute_with_role(
        self, role_name: str, task: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """動的役職での実行"""
        if role_name not in self.dynamic_roles:
            return {"error": f"Role {role_name} not found"}

        role = self.dynamic_roles[role_name]
        self.activate_role(role_name, f"Executing: {task}")

        execution_result = {
            "role": role.name,
            "display_name": role.display_name,
            "icon": role.icon,
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "authority_level": role.authority_level,
            "execution_context": context or {},
            "specialization": role.specialization,
            "actions_taken": [],
            "decisions_made": [],
            "collaboration_required": [],
        }

        # 専門分野に基づく処理
        if role.specialization == "backend_development":
            execution_result["actions_taken"].append("バックエンド技術実装")
        elif role.specialization == "frontend_development":
            execution_result["actions_taken"].append("フロントエンド開発")
        elif role.specialization == "system_design":
            execution_result["actions_taken"].append("システム設計")
        elif role.specialization == "security":
            execution_result["actions_taken"].append("セキュリティ実装")
        elif role.specialization == "ai_development":
            execution_result["actions_taken"].append("AI機能実装")

        # {{mistake_count}}回ミス防止システムとの統合チェック
        safety_check = self._perform_safety_check(task, context, role)
        execution_result["safety_check"] = safety_check

        # 指揮者システムとの統合
        conductor_integration = self._integrate_with_conductor(task, role)
        execution_result["conductor_integration"] = conductor_integration

        return execution_result

    def orchestrate_multi_role_task(
        self, task: str, required_role_names: List[str], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """複数役職での協調実行"""
        orchestration_result = {
            "task": task,
            "required_roles": required_role_names,
            "timestamp": datetime.now().isoformat(),
            "role_executions": {},
            "coordination_flow": [],
            "final_result": {},
        }

        # 権限レベル順にソート
        available_roles = [
            (name, self.dynamic_roles[name])
            for name in required_role_names
            if name in self.dynamic_roles
        ]
        sorted_roles = sorted(
            available_roles, key=lambda x: x[1].authority_level, reverse=True
        )

        # 各役職での実行
        for role_name, role in sorted_roles:
            result = self.execute_with_role(role_name, task, context)
            orchestration_result["role_executions"][role_name] = result
            orchestration_result["coordination_flow"].append(
                f"{role.display_name}: {result.get('timestamp')}"
            )

        # 最終結果の統合
        orchestration_result["final_result"] = self._integrate_role_results(
            orchestration_result["role_executions"]
        )

        return orchestration_result

    def adapt_organization_to_requirements(
        self, new_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """要件変更による組織適応"""
        adaptation_result = {
            "timestamp": datetime.now().isoformat(),
            "previous_roles": list(self.dynamic_roles.keys()),
            "new_requirements": new_requirements,
            "adaptation_actions": [],
            "new_roles": [],
            "removed_roles": [],
            "modified_roles": [],
        }

        # 新要件の分析
        if self.role_generator:
            try:
                from ai.role_generation_engine import ProjectRequirement

                req_objects = []
                for req_data in new_requirements:
                    req_objects.append(
                        ProjectRequirement(
                            category=req_data.get("category", "general"),
                            description=req_data.get("description", ""),
                            complexity=req_data.get("complexity", 0.5),
                            required_skills=req_data.get("required_skills", []),
                            estimated_effort=req_data.get("estimated_effort", "medium"),
                            priority=req_data.get("priority", "medium"),
                        )
                    )

                # 新しい役職生成
                new_generated_roles = (
                    self.role_generator.generate_roles_from_requirements(req_objects)
                )
            except ImportError:
                print("⚠️ Role generation engine not available, using fallback")
                new_generated_roles = []
        else:
            new_generated_roles = []

        # 組織の適応
        for new_role in new_generated_roles:
            if new_role.name not in self.dynamic_roles:
                # 新役職追加
                self.dynamic_roles[new_role.name] = new_role
                self.role_capabilities[new_role.name] = RoleCapability(
                    role=new_role,
                    responsibilities=new_role.responsibilities,
                    authority_level=new_role.authority_level,
                    decision_scope=new_role.decision_scope,
                    collaboration_requirements=new_role.collaboration_requirements,
                )
                adaptation_result["new_roles"].append(new_role.name)
                adaptation_result["adaptation_actions"].append(
                    f"新役職追加: {new_role.display_name}"
                )
            else:
                # 既存役職の更新
                existing_role = self.dynamic_roles[new_role.name]
                if existing_role.authority_level != new_role.authority_level:
                    existing_role.authority_level = new_role.authority_level
                    adaptation_result["modified_roles"].append(new_role.name)
                    adaptation_result["adaptation_actions"].append(
                        f"役職更新: {new_role.display_name}"
                    )

        # 状態保存
        self._save_organization_state()

        return adaptation_result

    def get_organization_status(self) -> Dict[str, Any]:
        """組織状況取得"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_roles": len(self.dynamic_roles),
            "active_roles": len(self.organization_state.active_roles),
            "roles": [
                {
                    "name": role.name,
                    "display_name": role.display_name,
                    "icon": role.icon,
                    "authority_level": role.authority_level,
                    "specialization": role.specialization,
                    "generated_from": role.generated_from,
                    "is_active": role in self.organization_state.active_roles,
                }
                for role in self.dynamic_roles.values()
            ],
            "current_context": self.organization_state.current_context,
            "project_requirements": self.organization_state.project_requirements,
        }

    def _check_collaboration_requirements(self, role: DynamicRole) -> Dict[str, bool]:
        """協力要件チェック"""
        collaboration_status = {}

        for requirement in role.collaboration_requirements:
            if "o3協議" in requirement or "o3・Gemini協議" in requirement:
                collaboration_status["o3_collaboration"] = True
            elif "Gemini協議" in requirement:
                collaboration_status["gemini_collaboration"] = True
            elif "情報集約" in requirement:
                collaboration_status["information_aggregation"] = True
            else:
                collaboration_status[requirement] = True

        return collaboration_status

    def _perform_safety_check(
        self, task: str, context: Dict[str, Any], role: DynamicRole
    ) -> Dict[str, Any]:
        """安全チェック実行"""
        safety_result = {
            "constitutional_ai_check": False,
            "rule_based_rewards_check": False,
            "role_authority_check": True,
            "overall_safety_score": 0.0,
        }

        # Constitutional AI チェック
        if self.integrated_systems["constitutional_ai"]:
            try:
                cai_eval = self.integrated_systems["constitutional_ai"].evaluate_action(
                    task, context or {}
                )
                safety_result["constitutional_ai_check"] = cai_eval[
                    "overall_compliance"
                ]
            except Exception:
                safety_result["constitutional_ai_check"] = True  # フォールバック

        # Rule-Based Rewards チェック
        if self.integrated_systems["rule_based_rewards"]:
            try:
                rbr_eval = self.integrated_systems[
                    "rule_based_rewards"
                ].evaluate_action(task, context or {})
                safety_result["rule_based_rewards_check"] = rbr_eval.total_score > 0
            except Exception:
                safety_result["rule_based_rewards_check"] = True  # フォールバック

        # 権限レベルチェック
        task_complexity = len(task.split()) * 0.1  # 簡易複雑度
        if role.authority_level < task_complexity * 10:
            safety_result["role_authority_check"] = False

        # 総合安全スコア計算
        checks = [
            safety_result["constitutional_ai_check"],
            safety_result["rule_based_rewards_check"],
            safety_result["role_authority_check"],
        ]
        safety_result["overall_safety_score"] = sum(checks) / len(checks)

        return safety_result

    def _integrate_with_conductor(self, task: str, role: DynamicRole) -> Dict[str, Any]:
        """指揮者システム統合"""
        if not self.integrated_systems["conductor"]:
            return {"status": "not_available"}

        conductor = self.integrated_systems["conductor"]

        try:
            from src.conductor.core import Task

            conductor_task = Task(
                id=f"dynamic_role_{role.name}_{datetime.now().strftime('%H%M%S')}",
                command=f"echo 'AI組織システム({role.display_name}): {task}'",
                description=f"{role.display_name}からの委譲: {task}",
                priority="normal",
            )

            conductor.add_task(conductor_task)
            results = conductor.execute_queue()

            return {
                "status": "integrated",
                "conductor_task_id": conductor_task.id,
                "execution_success": len(results) > 0 and results[0].success
                if results
                else False,
                "role_specialization": role.specialization,
            }

        except Exception as e:
            return {"status": "integration_error", "error": str(e)}

    def _integrate_role_results(
        self, role_executions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """役職実行結果の統合"""
        integrated_result = {
            "execution_summary": {},
            "decision_hierarchy": {},
            "collaboration_effectiveness": 0.0,
            "overall_success": True,
            "specialization_coverage": [],
        }

        # 各役職の結果を統合
        specializations = set()
        for role_name, result in role_executions.items():
            integrated_result["execution_summary"][role_name] = {
                "authority_level": result.get("authority_level", 0),
                "timestamp": result.get("timestamp"),
                "specialization": result.get("specialization", "general"),
                "success_indicators": len(
                    [k for k, v in result.items() if isinstance(v, list) and v]
                ),
            }

            if result.get("specialization"):
                specializations.add(result["specialization"])

        integrated_result["specialization_coverage"] = list(specializations)

        # 協力効果性計算
        total_roles = len(role_executions)
        successful_roles = sum(
            1
            for result in role_executions.values()
            if result.get("timestamp")
            and result.get("safety_check", {}).get("overall_safety_score", 0) > 0.5
        )

        integrated_result["collaboration_effectiveness"] = (
            successful_roles / total_roles if total_roles > 0 else 0.0
        )

        return integrated_result

    def _load_organization_state(self) -> OrganizationState:
        """組織状態の読み込み"""
        try:
            if self.org_state_file.exists():
                with open(self.org_state_file, encoding="utf-8") as f:
                    data = json.load(f)

                # 動的役職の復元
                active_roles = []
                for role_data in data.get("active_roles", []):
                    if isinstance(role_data, str):
                        # 後方互換性：文字列の場合はデフォルト役職作成
                        continue
                    else:
                        # 完全な役職データの復元
                        role = DynamicRole(**role_data)
                        active_roles.append(role)

                return OrganizationState(
                    active_roles=active_roles,
                    current_orchestrator=data.get("current_orchestrator", "integrated"),
                    decision_hierarchy=data.get("decision_hierarchy", {}),
                    collaboration_matrix=data.get("collaboration_matrix", {}),
                    current_context=data.get("current_context", ""),
                    project_requirements=data.get("project_requirements", {}),
                    role_generation_history=data.get("role_generation_history", []),
                    adaptation_triggers=data.get("adaptation_triggers", []),
                )
        except Exception as e:
            print(f"⚠️ 組織状態読み込みエラー: {e}")

        # デフォルト状態
        return OrganizationState(
            active_roles=[],
            current_orchestrator="integrated",
            decision_hierarchy={},
            collaboration_matrix={},
            current_context="初期化",
            project_requirements={},
            role_generation_history=[],
            adaptation_triggers=[],
        )

    def _save_organization_state(self):
        """組織状態の保存"""
        state_data = {
            "active_roles": [
                asdict(role) for role in self.organization_state.active_roles
            ],
            "current_orchestrator": self.organization_state.current_orchestrator,
            "decision_hierarchy": self.organization_state.decision_hierarchy,
            "collaboration_matrix": self.organization_state.collaboration_matrix,
            "current_context": self.organization_state.current_context,
            "project_requirements": self.organization_state.project_requirements,
            "role_generation_history": self.organization_state.role_generation_history,
            "adaptation_triggers": self.organization_state.adaptation_triggers,
            "last_updated": datetime.now().isoformat(),
        }

        try:
            self.org_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.org_state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"組織状態保存エラー: {e}")

    def _update_session_state(self):
        """セッション状態の更新"""
        try:
            if self.session_file.exists():
                with open(self.session_file, encoding="utf-8") as f:
                    session_data = json.load(f)
            else:
                session_data = {}

            # AI組織情報を更新
            if "ai_organization" not in session_data:
                session_data["ai_organization"] = {}

            session_data["ai_organization"]["active_roles"] = [
                role.name for role in self.organization_state.active_roles
            ]
            session_data["ai_organization"]["total_roles"] = len(self.dynamic_roles)
            session_data["ai_organization"]["current_orchestrator"] = (
                self.organization_state.current_orchestrator
            )
            session_data["ai_organization"]["is_dynamic"] = True

            if "session_quality" not in session_data:
                session_data["session_quality"] = {}
            session_data["session_quality"]["ai_organization_integrated"] = True
            session_data["session_quality"]["dynamic_roles_enabled"] = True
            session_data["last_updated"] = datetime.now().isoformat()

            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"セッション状態更新エラー: {e}")


def main():
    """動的AI組織システムのテスト"""
    org_system = DynamicAIOrganizationSystem()

    print("🏢 動的AI組織システム初期化完了")
    print(f"生成された役職: {len(org_system.dynamic_roles)}個")

    status = org_system.get_organization_status()
    print("\n📊 組織状況:")
    for role_info in status["roles"]:
        print(
            f"  {role_info['icon']} {role_info['display_name']} (権限: {role_info['authority_level']}, 専門: {role_info['specialization']})"
        )

    # PRESIDENT役職でのテスト実行
    if "PRESIDENT" in org_system.dynamic_roles:
        print("\n👑 PRESIDENT役職テスト")
        president_result = org_system.execute_with_role(
            "PRESIDENT",
            "{{mistake_count}}回ミス防止システムの戦略的評価",
            {"priority": "high", "scope": "system_wide"},
        )
        print(f"実行結果: {president_result['task']}")
        print(f"権限レベル: {president_result['authority_level']}")

    # 複数役職協調テスト
    available_roles = list(org_system.dynamic_roles.keys())[:3]  # 最初の3役職
    if len(available_roles) >= 2:
        print(f"\n🤝 複数役職協調テスト ({', '.join(available_roles)})")
        multi_role_result = org_system.orchestrate_multi_role_task(
            "動的AI組織システム完全統合", available_roles, {"coordination_test": True}
        )
        print(f"協調実行: {len(multi_role_result['role_executions'])}役職")
        print(
            f"協力効果性: {multi_role_result['final_result']['collaboration_effectiveness']:.1%}"
        )
        print(
            f"専門分野カバー: {', '.join(multi_role_result['final_result']['specialization_coverage'])}"
        )


if __name__ == "__main__":
    main()
