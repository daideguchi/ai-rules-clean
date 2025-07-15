# 🚨 偽装データ強制検出・停止システム
BANNED_FAKE_DATA = [
    "待機中",
    "処理中",
    "完了",
    "エラー",
    "テスト",
    "サンプル",
    "ダミー",
    "仮データ",
    "適当",
    "とりあえず",
    "temp",
    "dummy",
    "fake",
    "mock",
    "test",
    "sample",
    "placeholder",
    "Processing task",
    "Task completed",
    "Idle",
    "Active",
    "random",
    "lorem",
    "ipsum",
    "example",
    "demo",
]


def _enforce_no_fake_data(data):
    if isinstance(data, str):
        for banned in BANNED_FAKE_DATA:
            if banned in data:
                raise SystemExit(f"🚨 偽装データ検出で強制停止: {banned} in {data}")
    elif isinstance(data, (list, dict)):
        data_str = str(data)
        for banned in BANNED_FAKE_DATA:
            if banned in data_str:
                raise SystemExit(f"🚨 偽装データ検出で強制停止: {banned}")
    return data


# 全ての関数実行時に検証
original_print = print


def print(*args, **kwargs):
    for arg in args:
        _enforce_no_fake_data(arg)
    return original_print(*args, **kwargs)


#!/usr/bin/env python3
"""
🎯 自動役職配置システム
===================
要件定義・仕様書から自動でワーカー役職を配置するシステム
"""

import json  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Dict, List, Tuple  # noqa: E402


@dataclass
class RoleRequirement:
    """役職要件定義"""

    keywords: List[str]
    role_name: str
    display_name: str
    icon: str
    specialization: str
    authority_level: int
    default_todo: str
    default_action: str
    default_milestone: str
    priority: str


class AutoRoleAssignmentSystem:
    """自動役職配置システム"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # 役職定義テンプレート
        self.role_templates = {
            "president": RoleRequirement(
                keywords=["統括", "指揮", "決定", "承認", "全体", "最高"],
                role_name="PRESIDENT",
                display_name="プレジデント",
                icon="👑",
                specialization="strategic_leadership",
                authority_level=10,
                default_todo="全体統括・最終承認",
                default_action="プロジェクト全体監督",
                default_milestone="完全運用開始",
                priority="CRITICAL",
            ),
            "coordinator": RoleRequirement(
                keywords=["調整", "協調", "連携", "タスク管理", "進捗"],
                role_name="COORDINATOR",
                display_name="コーディネーター",
                icon="🔄",
                specialization="coordination",
                authority_level=8,
                default_todo="タスク調整・進捗管理",
                default_action="ワーカー間協調制御",
                default_milestone="完全同期達成",
                priority="HIGH",
            ),
            "requirements_analyst": RoleRequirement(
                keywords=["要件", "仕様", "分析", "定義", "ユーザー"],
                role_name="REQUIREMENTS_ANALYST",
                display_name="要件アナリスト",
                icon="📋",
                specialization="requirements_analysis",
                authority_level=7,
                default_todo="要件分析・仕様確認",
                default_action="ユーザー要求詳細分析",
                default_milestone="要件完全確定",
                priority="HIGH",
            ),
            "system_architect": RoleRequirement(
                keywords=["アーキテクチャ", "設計", "構造", "システム"],
                role_name="SYSTEM_ARCHITECT",
                display_name="システムアーキテクト",
                icon="🏗️",
                specialization="system_architecture",
                authority_level=8,
                default_todo="システム設計・構造最適化",
                default_action="アーキテクチャ設計",
                default_milestone="設計完了承認",
                priority="MEDIUM",
            ),
            "data_engineer": RoleRequirement(
                keywords=["データ", "DB", "データベース", "処理", "同期"],
                role_name="DATA_ENGINEER",
                display_name="データエンジニア",
                icon="📊",
                specialization="data_engineering",
                authority_level=8,
                default_todo="データ処理・DB管理",
                default_action="リアルタイムデータ処理",
                default_milestone="データ同期完了",
                priority="HIGH",
            ),
            "security_specialist": RoleRequirement(
                keywords=["セキュリティ", "安全", "保護", "監査", "脆弱性"],
                role_name="SECURITY_SPECIALIST",
                display_name="セキュリティ専門家",
                icon="🔒",
                specialization="security",
                authority_level=9,
                default_todo="セキュリティ監査・保護",
                default_action="安全性確認・スキャン",
                default_milestone="セキュリティ承認",
                priority="HIGH",
            ),
            "project_manager": RoleRequirement(
                keywords=["プロジェクト", "管理", "スケジュール", "マイルストーン"],
                role_name="PROJECT_MANAGER",
                display_name="プロジェクトマネージャー",
                icon="📈",
                specialization="project_management",
                authority_level=6,
                default_todo="プロジェクト管理・進捗追跡",
                default_action="全体進捗管理",
                default_milestone="プロジェクト完了",
                priority="MEDIUM",
            ),
            "devops_engineer": RoleRequirement(
                keywords=["DevOps", "運用", "インフラ", "配備", "自動化"],
                role_name="DEVOPS_ENGINEER",
                display_name="DevOpsエンジニア",
                icon="⚙️",
                specialization="devops",
                authority_level=8,
                default_todo="運用・インフラ管理",
                default_action="システム運用準備",
                default_milestone="運用環境完全構築",
                priority="HIGH",
            ),
        }

    def scan_requirements_documents(self) -> Dict[str, int]:
        """要件定義・仕様書からキーワードスキャン"""
        keyword_scores = {}

        # 初期化
        for _role_key, role_template in self.role_templates.items():
            for keyword in role_template.keywords:
                keyword_scores[keyword] = 0

        # スキャン対象ディレクトリ・ファイル
        scan_paths = [
            self.project_root / "docs",
            self.project_root / "README.md",
            self.project_root / "CLAUDE.md",
            self.project_root / "src" / "CLAUDE.md",
        ]

        for path in scan_paths:
            if path.exists():
                if path.is_file():
                    self._scan_file(path, keyword_scores)
                else:
                    # ディレクトリ内の全.mdファイルをスキャン
                    for md_file in path.rglob("*.md"):
                        self._scan_file(md_file, keyword_scores)

        return keyword_scores

    def _scan_file(self, file_path: Path, keyword_scores: Dict[str, int]):
        """単一ファイルのキーワードスキャン"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read().lower()

                for keyword in keyword_scores.keys():
                    # 日本語・英語両方に対応
                    count = content.count(keyword.lower())
                    if count > 0:
                        keyword_scores[keyword] += count
                        print(f"  🔍 {file_path.name}: '{keyword}' found {count} times")

        except Exception as e:
            print(f"⚠️ スキャンエラー ({file_path}): {e}")

    def assign_roles_from_requirements(
        self,
    ) -> List[Tuple[str, str, str, str, int, str, str, str, str, str, str, int]]:
        """要件から役職を自動配置"""
        print("🔍 要件定義・仕様書からキーワードスキャン開始...")

        keyword_scores = self.scan_requirements_documents()
        role_scores = {}

        # 役職ごとのスコア計算
        for role_key, role_template in self.role_templates.items():
            total_score = 0
            for keyword in role_template.keywords:
                total_score += keyword_scores.get(keyword, 0)

            role_scores[role_key] = {"score": total_score, "template": role_template}

            print(f"  📊 {role_template.display_name}: スコア {total_score}")

        # スコア順でソート
        sorted_roles = sorted(
            role_scores.items(), key=lambda x: x[1]["score"], reverse=True
        )

        assigned_workers = []

        print("\n🎯 自動役職配置結果:")
        for _i, (_role_key, role_data) in enumerate(sorted_roles):
            template = role_data["template"]
            score = role_data["score"]

            # 進捗をスコアベースで設定
            progress = min(95, 50 + (score * 5))

            worker_tuple = (
                template.role_name,
                template.display_name,
                template.icon,
                template.specialization,
                template.authority_level,
                template.default_todo,
                f"要件スコア: {score}",
                template.default_action,
                template.default_milestone,
                template.priority,
                "15:00",  # default deadline
                progress,
            )

            assigned_workers.append(worker_tuple)

            print(f"  {template.icon} {template.display_name} (スコア: {score})")
            print(f"    TODO: {template.default_todo}")
            print(f"    進捗: {progress}%")

        return assigned_workers

    def save_role_assignment(self, workers: List[Tuple], output_path: Path = None):
        """役職配置結果を保存"""
        if output_path is None:
            output_path = self.project_root / "runtime" / "auto_role_assignment.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        assignment_data = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "workers": [],
        }

        for worker in workers:
            assignment_data["workers"].append(
                {
                    "role_name": worker[0],
                    "display_name": worker[1],
                    "icon": worker[2],
                    "specialization": worker[3],
                    "authority_level": worker[4],
                    "todo": worker[5],
                    "action": worker[7],
                    "milestone": worker[8],
                    "priority": worker[9],
                    "progress": worker[11],
                }
            )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(assignment_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 役職配置結果保存: {output_path}")


def main():
    """テスト実行"""
    project_root = Path(__file__).parent.parent.parent
    system = AutoRoleAssignmentSystem(project_root)

    print("🎯 自動役職配置システム")
    print("=" * 50)

    workers = system.assign_roles_from_requirements()
    system.save_role_assignment(workers)

    print("\n✅ 自動役職配置完了!")


if __name__ == "__main__":
    main()
