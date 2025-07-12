#!/usr/bin/env python3
"""
🎯 Role Generation Engine - 役職自動生成エンジン
===============================================
要件定義・仕様書から動的に最適な役職を生成するシステム
プロジェクト特性に基づく適応的組織構成
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .ai_organization_system import DynamicRole


@dataclass
class ProjectRequirement:
    """プロジェクト要件"""

    category: str
    description: str
    complexity: float  # 0.1-1.0
    required_skills: List[str]
    estimated_effort: str
    priority: str


@dataclass
class RoleTemplate:
    """役職テンプレート"""

    name: str
    display_name: str
    icon: str
    trigger_keywords: List[str]
    base_responsibilities: List[str]
    authority_range: tuple  # (min, max)
    specialization_area: str
    collaboration_patterns: List[str]


class RoleGenerationEngine:
    """役職生成エンジン"""

    def __init__(self):
        self.role_templates = self._initialize_role_templates()
        self.skill_role_mapping = self._initialize_skill_mappings()
        self.complexity_thresholds = {
            "simple": 0.3,
            "moderate": 0.6,
            "complex": 0.8,
            "enterprise": 1.0,
        }

    def _initialize_role_templates(self) -> Dict[str, RoleTemplate]:
        """役職テンプレート初期化"""
        return {
            # 技術系役職
            "backend_developer": RoleTemplate(
                name="BACKEND_DEVELOPER",
                display_name="バックエンド開発者",
                icon="🔧",
                trigger_keywords=[
                    "api",
                    "database",
                    "server",
                    "backend",
                    "microservice",
                ],
                base_responsibilities=[
                    "API設計・実装",
                    "データベース設計",
                    "サーバー管理",
                    "パフォーマンス最適化",
                ],
                authority_range=(6, 8),
                specialization_area="backend_development",
                collaboration_patterns=[
                    "FRONTEND_DEVELOPER",
                    "DATABASE_ARCHITECT",
                    "DEVOPS_ENGINEER",
                ],
            ),
            "frontend_developer": RoleTemplate(
                name="FRONTEND_DEVELOPER",
                display_name="フロントエンド開発者",
                icon="💻",
                trigger_keywords=[
                    "ui",
                    "frontend",
                    "react",
                    "vue",
                    "javascript",
                    "css",
                ],
                base_responsibilities=[
                    "ユーザーインターフェース実装",
                    "レスポンシブデザイン",
                    "ユーザー体験最適化",
                    "フロントエンド架構設計",
                ],
                authority_range=(6, 8),
                specialization_area="frontend_development",
                collaboration_patterns=[
                    "UI_DESIGNER",
                    "BACKEND_DEVELOPER",
                    "UX_SPECIALIST",
                ],
            ),
            "devops_engineer": RoleTemplate(
                name="DEVOPS_ENGINEER",
                display_name="DevOpsエンジニア",
                icon="⚙️",
                trigger_keywords=[
                    "deployment",
                    "ci/cd",
                    "docker",
                    "kubernetes",
                    "infrastructure",
                ],
                base_responsibilities=[
                    "CI/CDパイプライン構築",
                    "インフラ管理",
                    "デプロイメント自動化",
                    "監視・ログ管理",
                ],
                authority_range=(7, 9),
                specialization_area="infrastructure",
                collaboration_patterns=[
                    "BACKEND_DEVELOPER",
                    "SECURITY_SPECIALIST",
                    "SYSTEM_ARCHITECT",
                ],
            ),
            # 設計・分析系役職
            "system_architect": RoleTemplate(
                name="SYSTEM_ARCHITECT",
                display_name="システムアーキテクト",
                icon="🏗️",
                trigger_keywords=[
                    "architecture",
                    "design",
                    "scalability",
                    "pattern",
                    "framework",
                ],
                base_responsibilities=[
                    "システム全体設計",
                    "技術スタック選定",
                    "拡張性設計",
                    "性能要件設計",
                ],
                authority_range=(8, 10),
                specialization_area="system_design",
                collaboration_patterns=[
                    "BACKEND_DEVELOPER",
                    "FRONTEND_DEVELOPER",
                    "DATABASE_ARCHITECT",
                ],
            ),
            "requirements_analyst": RoleTemplate(
                name="REQUIREMENTS_ANALYST",
                display_name="要件アナリスト",
                icon="📋",
                trigger_keywords=[
                    "requirements",
                    "specification",
                    "analysis",
                    "business",
                ],
                base_responsibilities=[
                    "要件定義・分析",
                    "仕様書作成",
                    "ステークホルダー調整",
                    "受け入れ基準定義",
                ],
                authority_range=(7, 9),
                specialization_area="business_analysis",
                collaboration_patterns=[
                    "SYSTEM_ARCHITECT",
                    "PROJECT_MANAGER",
                    "UI_DESIGNER",
                ],
            ),
            # UX/UI系役職
            "ui_designer": RoleTemplate(
                name="UI_DESIGNER",
                display_name="UIデザイナー",
                icon="🎨",
                trigger_keywords=["design", "ui", "interface", "mockup", "wireframe"],
                base_responsibilities=[
                    "UI設計・デザイン",
                    "プロトタイプ作成",
                    "デザインシステム構築",
                    "ユーザビリティテスト",
                ],
                authority_range=(5, 7),
                specialization_area="design",
                collaboration_patterns=[
                    "FRONTEND_DEVELOPER",
                    "UX_SPECIALIST",
                    "REQUIREMENTS_ANALYST",
                ],
            ),
            "ux_specialist": RoleTemplate(
                name="UX_SPECIALIST",
                display_name="UX専門家",
                icon="👥",
                trigger_keywords=[
                    "ux",
                    "user experience",
                    "usability",
                    "journey",
                    "persona",
                ],
                base_responsibilities=[
                    "ユーザー体験設計",
                    "ユーザビリティ分析",
                    "カスタマージャーニー設計",
                    "A/Bテスト設計",
                ],
                authority_range=(6, 8),
                specialization_area="user_experience",
                collaboration_patterns=[
                    "UI_DESIGNER",
                    "FRONTEND_DEVELOPER",
                    "DATA_ANALYST",
                ],
            ),
            # データ・AI系役職
            "data_engineer": RoleTemplate(
                name="DATA_ENGINEER",
                display_name="データエンジニア",
                icon="📊",
                trigger_keywords=["data", "pipeline", "etl", "analytics", "warehouse"],
                base_responsibilities=[
                    "データパイプライン構築",
                    "データウェアハウス設計",
                    "ETL処理実装",
                    "データ品質管理",
                ],
                authority_range=(7, 9),
                specialization_area="data_engineering",
                collaboration_patterns=[
                    "DATA_SCIENTIST",
                    "BACKEND_DEVELOPER",
                    "DATABASE_ARCHITECT",
                ],
            ),
            "ai_specialist": RoleTemplate(
                name="AI_SPECIALIST",
                display_name="AI専門家",
                icon="🤖",
                trigger_keywords=["ai", "ml", "machine learning", "neural", "model"],
                base_responsibilities=[
                    "AIモデル設計・実装",
                    "機械学習パイプライン構築",
                    "モデル評価・最適化",
                    "AI倫理・安全性確保",
                ],
                authority_range=(8, 10),
                specialization_area="artificial_intelligence",
                collaboration_patterns=[
                    "DATA_ENGINEER",
                    "DATA_SCIENTIST",
                    "BACKEND_DEVELOPER",
                ],
            ),
            # セキュリティ・品質系役職
            "security_specialist": RoleTemplate(
                name="SECURITY_SPECIALIST",
                display_name="セキュリティ専門家",
                icon="🔒",
                trigger_keywords=[
                    "security",
                    "auth",
                    "encryption",
                    "vulnerability",
                    "compliance",
                ],
                base_responsibilities=[
                    "セキュリティ設計・実装",
                    "脆弱性評価",
                    "認証・認可システム設計",
                    "コンプライアンス確保",
                ],
                authority_range=(8, 10),
                specialization_area="security",
                collaboration_patterns=[
                    "BACKEND_DEVELOPER",
                    "DEVOPS_ENGINEER",
                    "SYSTEM_ARCHITECT",
                ],
            ),
            "qa_engineer": RoleTemplate(
                name="QA_ENGINEER",
                display_name="品質保証エンジニア",
                icon="✅",
                trigger_keywords=["test", "quality", "qa", "automation", "validation"],
                base_responsibilities=[
                    "テスト戦略策定",
                    "自動テスト実装",
                    "品質評価・報告",
                    "テストデータ管理",
                ],
                authority_range=(6, 8),
                specialization_area="quality_assurance",
                collaboration_patterns=[
                    "BACKEND_DEVELOPER",
                    "FRONTEND_DEVELOPER",
                    "DEVOPS_ENGINEER",
                ],
            ),
            # 管理・調整系役職
            "project_manager": RoleTemplate(
                name="PROJECT_MANAGER",
                display_name="プロジェクトマネージャー",
                icon="📈",
                trigger_keywords=[
                    "project",
                    "management",
                    "schedule",
                    "coordination",
                    "delivery",
                ],
                base_responsibilities=[
                    "プロジェクト計画・管理",
                    "リソース調整",
                    "進捗管理・報告",
                    "リスク管理",
                ],
                authority_range=(7, 9),
                specialization_area="project_management",
                collaboration_patterns=[
                    "SYSTEM_ARCHITECT",
                    "REQUIREMENTS_ANALYST",
                    "PRESIDENT",
                ],
            ),
            "technical_writer": RoleTemplate(
                name="TECHNICAL_WRITER",
                display_name="技術文書担当",
                icon="📝",
                trigger_keywords=[
                    "documentation",
                    "manual",
                    "api doc",
                    "guide",
                    "wiki",
                ],
                base_responsibilities=[
                    "技術文書作成・維持",
                    "APIドキュメント管理",
                    "ユーザーマニュアル作成",
                    "知識共有促進",
                ],
                authority_range=(4, 6),
                specialization_area="documentation",
                collaboration_patterns=[
                    "BACKEND_DEVELOPER",
                    "FRONTEND_DEVELOPER",
                    "UI_DESIGNER",
                ],
            ),
        }

    def _initialize_skill_mappings(self) -> Dict[str, List[str]]:
        """スキル-役職マッピング"""
        return {
            # プログラミング言語
            "python": ["BACKEND_DEVELOPER", "DATA_ENGINEER", "AI_SPECIALIST"],
            "javascript": ["FRONTEND_DEVELOPER", "BACKEND_DEVELOPER"],
            "typescript": ["FRONTEND_DEVELOPER", "BACKEND_DEVELOPER"],
            "java": ["BACKEND_DEVELOPER", "SYSTEM_ARCHITECT"],
            "go": ["BACKEND_DEVELOPER", "DEVOPS_ENGINEER"],
            "rust": ["BACKEND_DEVELOPER", "SYSTEM_ARCHITECT"],
            # フレームワーク・技術
            "react": ["FRONTEND_DEVELOPER", "UI_DESIGNER"],
            "vue": ["FRONTEND_DEVELOPER"],
            "django": ["BACKEND_DEVELOPER"],
            "fastapi": ["BACKEND_DEVELOPER"],
            "docker": ["DEVOPS_ENGINEER", "BACKEND_DEVELOPER"],
            "kubernetes": ["DEVOPS_ENGINEER", "SYSTEM_ARCHITECT"],
            # データベース
            "postgresql": ["BACKEND_DEVELOPER", "DATA_ENGINEER"],
            "mongodb": ["BACKEND_DEVELOPER", "DATA_ENGINEER"],
            "redis": ["BACKEND_DEVELOPER", "SYSTEM_ARCHITECT"],
            # 専門分野
            "machine_learning": ["AI_SPECIALIST", "DATA_ENGINEER"],
            "cybersecurity": ["SECURITY_SPECIALIST"],
            "ui_design": ["UI_DESIGNER", "UX_SPECIALIST"],
            "project_management": ["PROJECT_MANAGER"],
            "business_analysis": ["REQUIREMENTS_ANALYST"],
        }

    def generate_roles_from_requirements(
        self, requirements: List[ProjectRequirement]
    ) -> List["DynamicRole"]:
        """要件からの役職生成"""
        from .ai_organization_system import DynamicRole

        generated_roles = []
        used_templates = set()

        # 1. 要件分析による役職特定
        for req in requirements:
            matching_templates = self._find_matching_templates(req)

            for template_name in matching_templates:
                if template_name not in used_templates:
                    template = self.role_templates[template_name]

                    # 動的役職生成
                    dynamic_role = DynamicRole(
                        name=template.name,
                        display_name=template.display_name,
                        icon=template.icon,
                        responsibilities=self._customize_responsibilities(
                            template, req
                        ),
                        authority_level=self._calculate_authority_level(template, req),
                        decision_scope=self._generate_decision_scope(template, req),
                        collaboration_requirements=self._generate_collaboration_requirements(
                            template
                        ),
                        generated_from=f"要件: {req.description}",
                        specialization=template.specialization_area,
                        required_skills=req.required_skills,
                    )

                    generated_roles.append(dynamic_role)
                    used_templates.add(template_name)

        # 2. 基本役職の確保（PRESIDENT, COORDINATORは必須）
        core_roles = self._ensure_core_roles_generated()
        for core_role in core_roles:
            if core_role.name not in [r.name for r in generated_roles]:
                generated_roles.append(core_role)

        # 3. 役職数の最適化（4-8役職が理想）
        generated_roles = self._optimize_role_count(generated_roles, requirements)

        return generated_roles

    def _find_matching_templates(self, requirement: ProjectRequirement) -> List[str]:
        """要件に合致するテンプレート検索"""
        matches = []
        req_text = requirement.description.lower()

        # キーワードマッチング
        for template_name, template in self.role_templates.items():
            match_score = 0

            # トリガーキーワードチェック
            for keyword in template.trigger_keywords:
                if keyword in req_text:
                    match_score += 2

            # スキルマッチング
            for skill in requirement.required_skills:
                if skill.lower() in self.skill_role_mapping:
                    if template_name in self.skill_role_mapping[skill.lower()]:
                        match_score += 3

            # カテゴリマッチング
            if requirement.category.lower() in template.specialization_area:
                match_score += 1

            if match_score >= 2:  # 閾値: 2ポイント以上
                matches.append(template_name)

        return matches

    def _customize_responsibilities(
        self, template: RoleTemplate, requirement: ProjectRequirement
    ) -> List[str]:
        """要件に基づく責任範囲カスタマイズ"""
        responsibilities = template.base_responsibilities.copy()

        # 要件の複雑度に応じて責任を追加
        if requirement.complexity > 0.7:
            responsibilities.append(f"高度な{template.specialization_area}設計")
            responsibilities.append("技術的リーダーシップ")

        # 要件固有の責任追加
        if "security" in requirement.description.lower():
            responsibilities.append("セキュリティ要件実装")

        if "performance" in requirement.description.lower():
            responsibilities.append("パフォーマンス最適化")

        return responsibilities

    def _calculate_authority_level(
        self, template: RoleTemplate, requirement: ProjectRequirement
    ) -> int:
        """権限レベル計算"""
        base_authority = (
            template.authority_range[0] + template.authority_range[1]
        ) // 2

        # 複雑度による調整
        complexity_bonus = int(requirement.complexity * 2)

        # 優先度による調整
        priority_bonus = 0
        if requirement.priority == "high":
            priority_bonus = 1
        elif requirement.priority == "critical":
            priority_bonus = 2

        final_authority = min(base_authority + complexity_bonus + priority_bonus, 10)
        return max(final_authority, template.authority_range[0])

    def _generate_decision_scope(
        self, template: RoleTemplate, requirement: ProjectRequirement
    ) -> List[str]:
        """意思決定範囲生成"""
        scope = [template.specialization_area]

        # 要件に基づく追加範囲
        if requirement.complexity > 0.6:
            scope.append("technical_architecture")

        if "integration" in requirement.description.lower():
            scope.append("system_integration")

        return scope

    def _generate_collaboration_requirements(self, template: RoleTemplate) -> List[str]:
        """協力要件生成"""
        requirements = []

        # テンプレートの協力パターンを基に生成
        for partner_role in template.collaboration_patterns:
            requirements.append(f"{partner_role}との密接な協力")

        # 共通協力要件
        requirements.extend(["PRESIDENTへの定期報告", "COORDINATORによる調整参加"])

        return requirements

    def _ensure_core_roles_generated(self) -> List["DynamicRole"]:
        """コア役職の生成確保"""
        from .ai_organization_system import DynamicRole

        core_roles = [
            DynamicRole(
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
            ),
            DynamicRole(
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
            ),
        ]

        return core_roles

    def _optimize_role_count(
        self, roles: List["DynamicRole"], requirements: List[ProjectRequirement]
    ) -> List["DynamicRole"]:
        """役職数最適化（4-8役職が理想）"""
        if len(roles) <= 8:
            return roles

        # 重要度順にソート（権限レベル + 要件マッチ度）
        def role_importance(role):
            base_score = role.authority_level

            # 要件マッチング度を加算
            match_score = 0
            for req in requirements:
                if any(skill in role.required_skills for skill in req.required_skills):
                    match_score += 1

            return base_score + match_score

        sorted_roles = sorted(roles, key=role_importance, reverse=True)

        # 上位8役職を選択（PRESIDENT, COORDINATORは必須保持）
        essential_roles = [
            r for r in sorted_roles if r.name in ["PRESIDENT", "COORDINATOR"]
        ]
        other_roles = [
            r for r in sorted_roles if r.name not in ["PRESIDENT", "COORDINATOR"]
        ]

        return essential_roles + other_roles[:6]  # 合計8役職


class ProjectRequirementsAnalyzer:
    """プロジェクト要件分析エンジン"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")

    def analyze_project_requirements(self) -> List[ProjectRequirement]:
        """プロジェクト要件分析"""
        requirements = []

        # 1. ドキュメントファイルからの要件抽出
        doc_requirements = self._extract_from_documents()
        requirements.extend(doc_requirements)

        # 2. コードベースからの要件推定
        code_requirements = self._infer_from_codebase()
        requirements.extend(code_requirements)

        # 3. 設定ファイルからの要件抽出
        config_requirements = self._extract_from_configs()
        requirements.extend(config_requirements)

        return requirements

    def _extract_from_documents(self) -> List[ProjectRequirement]:
        """ドキュメントファイルからの要件抽出"""
        requirements = []

        # README.mdの分析
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            req = self._analyze_readme_content(content)
            if req:
                requirements.append(req)

        # docs/ディレクトリの分析
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                content = doc_file.read_text(encoding="utf-8")
                req = self._analyze_document_content(content, str(doc_file))
                if req:
                    requirements.append(req)

        return requirements

    def _infer_from_codebase(self) -> List[ProjectRequirement]:
        """コードベースからの要件推定"""
        requirements = []

        # package.json分析（Node.js/JavaScript）
        package_json = self.project_root / "package.json"
        if package_json.exists():
            req = self._analyze_package_json(package_json)
            if req:
                requirements.append(req)

        # requirements.txt分析（Python）
        requirements_txt = self.project_root / "requirements.txt"
        if requirements_txt.exists():
            req = self._analyze_requirements_txt(requirements_txt)
            if req:
                requirements.append(req)

        # Dockerfileの分析
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            req = self._analyze_dockerfile(dockerfile)
            if req:
                requirements.append(req)

        return requirements

    def _extract_from_configs(self) -> List[ProjectRequirement]:
        """設定ファイルからの要件抽出"""
        requirements = []

        # .claude/settings.json分析
        claude_settings = self.project_root / ".claude" / "settings.json"
        if claude_settings.exists():
            req = self._analyze_claude_settings(claude_settings)
            if req:
                requirements.append(req)

        return requirements

    def _analyze_readme_content(self, content: str) -> Optional[ProjectRequirement]:
        """README内容分析"""
        # 技術キーワード抽出
        tech_keywords = re.findall(
            r"\b(python|javascript|react|vue|docker|api|database|ml|ai)\b",
            content.lower(),
        )

        if tech_keywords:
            return ProjectRequirement(
                category="general_development",
                description=f"README記載の技術要件: {', '.join(set(tech_keywords))}",
                complexity=min(len(set(tech_keywords)) * 0.1, 1.0),
                required_skills=list(set(tech_keywords)),
                estimated_effort="medium",
                priority="medium",
            )

        return None

    def _analyze_document_content(
        self, content: str, file_path: str
    ) -> Optional[ProjectRequirement]:
        """ドキュメント内容分析"""
        # ファイル名から要件カテゴリ推定
        filename = Path(file_path).stem.lower()

        if "api" in filename:
            category = "api_development"
        elif "ui" in filename or "frontend" in filename:
            category = "frontend_development"
        elif "security" in filename:
            category = "security"
        elif "architecture" in filename:
            category = "system_architecture"
        else:
            category = "documentation"

        # 複雑度推定（文書長と技術用語密度）
        tech_terms = len(
            re.findall(
                r"\b(implementation|integration|optimization|scalability)\b",
                content.lower(),
            )
        )
        complexity = min(tech_terms * 0.1, 1.0)

        return ProjectRequirement(
            category=category,
            description=f"{filename}文書の要件",
            complexity=complexity,
            required_skills=[category.replace("_", " ")],
            estimated_effort="medium",
            priority="medium",
        )

    def _analyze_package_json(
        self, package_json_path: Path
    ) -> Optional[ProjectRequirement]:
        """package.json分析"""
        try:
            with open(package_json_path) as f:
                data = json.load(f)

            dependencies = list(data.get("dependencies", {}).keys())
            dev_dependencies = list(data.get("devDependencies", {}).keys())

            all_deps = dependencies + dev_dependencies

            # フロントエンド技術検出
            frontend_frameworks = ["react", "vue", "angular", "svelte"]
            detected_frontend = [
                fw for fw in frontend_frameworks if any(fw in dep for dep in all_deps)
            ]

            if detected_frontend:
                return ProjectRequirement(
                    category="frontend_development",
                    description=f"フロントエンド開発: {', '.join(detected_frontend)}",
                    complexity=0.6,
                    required_skills=["javascript", "frontend"] + detected_frontend,
                    estimated_effort="medium",
                    priority="high",
                )

        except Exception:
            pass

        return None

    def _analyze_requirements_txt(
        self, requirements_path: Path
    ) -> Optional[ProjectRequirement]:
        """requirements.txt分析"""
        try:
            content = requirements_path.read_text()
            packages = [
                line.split("==")[0].split(">=")[0].strip()
                for line in content.split("\n")
                if line.strip()
            ]

            # AI/ML関連パッケージ検出
            ai_packages = ["tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"]
            detected_ai = [
                pkg for pkg in ai_packages if any(pkg in p for p in packages)
            ]

            if detected_ai:
                return ProjectRequirement(
                    category="ai_development",
                    description=f"AI/ML開発: {', '.join(detected_ai)}",
                    complexity=0.8,
                    required_skills=["python", "machine_learning"] + detected_ai,
                    estimated_effort="high",
                    priority="high",
                )

            # Web開発パッケージ検出
            web_packages = ["django", "flask", "fastapi"]
            detected_web = [
                pkg for pkg in web_packages if any(pkg in p for p in packages)
            ]

            if detected_web:
                return ProjectRequirement(
                    category="backend_development",
                    description=f"Webバックエンド開発: {', '.join(detected_web)}",
                    complexity=0.6,
                    required_skills=["python", "backend"] + detected_web,
                    estimated_effort="medium",
                    priority="high",
                )

        except Exception:
            pass

        return None

    def _analyze_dockerfile(
        self, dockerfile_path: Path
    ) -> Optional[ProjectRequirement]:
        """Dockerfile分析"""
        try:
            dockerfile_path.read_text()

            return ProjectRequirement(
                category="devops",
                description="Docker化・コンテナ運用",
                complexity=0.5,
                required_skills=["docker", "containerization", "devops"],
                estimated_effort="medium",
                priority="medium",
            )

        except Exception:
            pass

        return None

    def _analyze_claude_settings(
        self, settings_path: Path
    ) -> Optional[ProjectRequirement]:
        """Claude設定分析"""
        try:
            with open(settings_path) as f:
                json.load(f)

            # AI統合開発環境として分析
            return ProjectRequirement(
                category="ai_integration",
                description="AI統合開発環境・{{mistake_count}}回ミス防止システム",
                complexity=0.9,
                required_skills=["ai_integration", "development_tools", "automation"],
                estimated_effort="high",
                priority="critical",
            )

        except Exception:
            pass

        return None
