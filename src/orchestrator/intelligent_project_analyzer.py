#!/usr/bin/env python3
"""
Intelligent Project Analyzer - AI組織自動配置システム
=====================================================
プロジェクト要件分析とAIワーカー最適配置を自動実行

Features:
- プロジェクト全体スキャン・解析
- 要件定義書・仕様書の自動解析
- 適切なAI役職の自動決定（最低4ワーカー+PRESIDENT）
- tmux-based Claude Code並列起動
- ダッシュボード統合監視
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


@dataclass
class ProjectAnalysis:
    """プロジェクト分析結果"""

    project_type: str  # web_dev, ai_system, data_analysis, etc.
    complexity_level: str  # simple, moderate, complex, enterprise
    key_technologies: List[str]
    primary_objectives: List[str]
    required_expertise: List[str]
    estimated_team_size: int
    recommended_roles: List[str]
    critical_files: List[str]
    analysis_confidence: float


@dataclass
class AIWorkerRole:
    """AIワーカー役職定義"""

    role_id: str
    role_name: str
    display_name: str
    expertise_areas: List[str]
    responsibilities: List[str]
    priority: int  # 1=highest, 5=lowest


class IntelligentProjectAnalyzer:
    """プロジェクト自動分析・AI配置システム"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        )
        self.runtime_dir = self.project_root / "runtime"
        self.analysis_cache = self.runtime_dir / "project_analysis_cache.json"

        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.runtime_dir / "logs" / "project_analyzer.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("project-analyzer")

        # AI役職テンプレート
        self.role_templates = self._load_role_templates()

        # 分析対象ファイル
        self.critical_analysis_files = [
            "Index.md",
            "CLAUDE.md",
            "README.md",
            "startup_checklist.md",
            "docs/01_concepts/",
            "docs/02_guides/",
            "docs/03_processes/",
            "docs/04_reference/",
            "src/",
            "tests/",
            "requirements.txt",
            "package.json",
            "pyproject.toml",
            "Makefile",
        ]

    def _load_role_templates(self) -> Dict[str, AIWorkerRole]:
        """AI役職テンプレート読み込み"""
        return {
            "PRESIDENT": AIWorkerRole(
                role_id="PRESIDENT",
                role_name="Executive President",
                display_name="👑 PRESIDENT",
                expertise_areas=[
                    "strategic_planning",
                    "coordination",
                    "quality_assurance",
                ],
                responsibilities=[
                    "Overall project leadership",
                    "Quality control",
                    "Team coordination",
                ],
                priority=1,
            ),
            "TECH_LEAD": AIWorkerRole(
                role_id="TECH_LEAD",
                role_name="Technical Lead",
                display_name="🏗️ TECH_LEAD",
                expertise_areas=["architecture", "code_review", "technical_decisions"],
                responsibilities=[
                    "Technical architecture",
                    "Code quality",
                    "Technical decisions",
                ],
                priority=2,
            ),
            "FULL_STACK_DEV": AIWorkerRole(
                role_id="FULL_STACK_DEV",
                role_name="Full Stack Developer",
                display_name="💻 FULL_STACK",
                expertise_areas=["frontend", "backend", "integration"],
                responsibilities=[
                    "Feature implementation",
                    "Integration work",
                    "End-to-end development",
                ],
                priority=2,
            ),
            "QA_SPECIALIST": AIWorkerRole(
                role_id="QA_SPECIALIST",
                role_name="QA Specialist",
                display_name="🧪 QA_SPEC",
                expertise_areas=["testing", "quality_assurance", "automation"],
                responsibilities=[
                    "Test planning",
                    "Quality validation",
                    "Bug detection",
                ],
                priority=3,
            ),
            "AI_SPECIALIST": AIWorkerRole(
                role_id="AI_SPECIALIST",
                role_name="AI/ML Specialist",
                display_name="🤖 AI_SPEC",
                expertise_areas=["machine_learning", "ai_systems", "data_processing"],
                responsibilities=[
                    "AI/ML implementation",
                    "Model optimization",
                    "Intelligence systems",
                ],
                priority=2,
            ),
            "SECURITY_SPEC": AIWorkerRole(
                role_id="SECURITY_SPEC",
                role_name="Security Specialist",
                display_name="🛡️ SEC_SPEC",
                expertise_areas=["security", "compliance", "risk_assessment"],
                responsibilities=[
                    "Security implementation",
                    "Compliance checking",
                    "Risk mitigation",
                ],
                priority=3,
            ),
            "DEVOPS_SPEC": AIWorkerRole(
                role_id="DEVOPS_SPEC",
                role_name="DevOps Specialist",
                display_name="⚙️ DEVOPS",
                expertise_areas=["deployment", "infrastructure", "automation"],
                responsibilities=["CI/CD", "Infrastructure", "Deployment automation"],
                priority=3,
            ),
            "DOC_SPECIALIST": AIWorkerRole(
                role_id="DOC_SPECIALIST",
                role_name="Documentation Specialist",
                display_name="📚 DOC_SPEC",
                expertise_areas=["documentation", "technical_writing", "user_guides"],
                responsibilities=["Documentation", "User guides", "Technical writing"],
                priority=4,
            ),
        }

    def analyze_project_comprehensively(self) -> ProjectAnalysis:
        """包括的プロジェクト分析"""
        self.logger.info("Starting comprehensive project analysis...")

        # 各分析コンポーネント実行
        structure_analysis = self._analyze_project_structure()
        documentation_analysis = self._analyze_documentation()
        technology_analysis = self._analyze_technologies()
        complexity_analysis = self._analyze_complexity()

        # 分析結果統合
        project_type = self._determine_project_type(
            structure_analysis, technology_analysis
        )
        complexity_level = complexity_analysis["level"]
        key_technologies = technology_analysis["technologies"]
        primary_objectives = documentation_analysis["objectives"]
        required_expertise = self._determine_required_expertise(
            project_type, key_technologies
        )

        # チームサイズとワーカー役職決定
        team_size, recommended_roles = self._determine_optimal_team_composition(
            project_type, complexity_level, required_expertise
        )

        analysis = ProjectAnalysis(
            project_type=project_type,
            complexity_level=complexity_level,
            key_technologies=key_technologies,
            primary_objectives=primary_objectives,
            required_expertise=required_expertise,
            estimated_team_size=team_size,
            recommended_roles=recommended_roles,
            critical_files=self._identify_critical_files(),
            analysis_confidence=self._calculate_confidence(
                structure_analysis, documentation_analysis
            ),
        )

        # 分析結果キャッシュ
        self._cache_analysis(analysis)

        self.logger.info(
            f"Project analysis completed: {project_type} ({complexity_level})"
        )
        return analysis

    def _analyze_project_structure(self) -> Dict[str, Any]:
        """プロジェクト構造分析"""
        structure = {
            "src_dirs": [],
            "test_dirs": [],
            "config_files": [],
            "documentation_dirs": [],
            "total_files": 0,
            "total_python_files": 0,
            "total_js_files": 0,
            "has_ai_components": False,
            "has_web_components": False,
            "has_database": False,
        }

        for root, _dirs, files in os.walk(self.project_root):
            rel_path = Path(root).relative_to(self.project_root)

            # ディレクトリ分類
            if "src" in str(rel_path) or "source" in str(rel_path):
                structure["src_dirs"].append(str(rel_path))
            if "test" in str(rel_path) or "spec" in str(rel_path):
                structure["test_dirs"].append(str(rel_path))
            if "docs" in str(rel_path) or "documentation" in str(rel_path):
                structure["documentation_dirs"].append(str(rel_path))

            # ファイル分析
            for file in files:
                structure["total_files"] += 1

                if file.endswith((".py", ".pyi")):
                    structure["total_python_files"] += 1

                    # AI関連コンポーネント検出
                    if any(
                        keyword in file.lower()
                        for keyword in ["ai", "ml", "neural", "model", "learning"]
                    ):
                        structure["has_ai_components"] = True

                elif file.endswith((".js", ".ts", ".jsx", ".tsx")):
                    structure["total_js_files"] += 1
                    structure["has_web_components"] = True

                elif file.endswith((".sql", ".db", ".sqlite")):
                    structure["has_database"] = True

                elif file in [
                    "requirements.txt",
                    "package.json",
                    "Makefile",
                    "docker-compose.yml",
                ]:
                    structure["config_files"].append(file)

        return structure

    def _analyze_documentation(self) -> Dict[str, Any]:
        """ドキュメント分析"""
        docs_analysis = {
            "objectives": [],
            "features": [],
            "requirements": [],
            "complexity_indicators": [],
        }

        # 重要ドキュメント読み込み・解析
        key_docs = ["README.md", "CLAUDE.md", "Index.md", "startup_checklist.md"]

        for doc_file in key_docs:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                content = doc_path.read_text(encoding="utf-8", errors="ignore")

                # 目的・機能抽出
                objectives = re.findall(
                    r"(?:目的|目標|objectives?|goals?)[:\s]*([^\n]+)",
                    content,
                    re.IGNORECASE,
                )
                docs_analysis["objectives"].extend(objectives)

                features = re.findall(
                    r"(?:機能|features?|capabilities)[:\s]*([^\n]+)",
                    content,
                    re.IGNORECASE,
                )
                docs_analysis["features"].extend(features)

                # 複雑性指標
                if "AI" in content or "machine learning" in content.lower():
                    docs_analysis["complexity_indicators"].append("ai_complexity")
                if (
                    "microservice" in content.lower()
                    or "distributed" in content.lower()
                ):
                    docs_analysis["complexity_indicators"].append(
                        "architecture_complexity"
                    )
                if (
                    "enterprise" in content.lower()
                    or "enterprise-grade" in content.lower()
                ):
                    docs_analysis["complexity_indicators"].append(
                        "enterprise_complexity"
                    )

        return docs_analysis

    def _analyze_technologies(self) -> Dict[str, Any]:
        """技術スタック分析"""
        technologies = set()

        # requirements.txt分析
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            for line in content.split("\n"):
                if line.strip() and not line.startswith("#"):
                    pkg = line.split("==")[0].split(">=")[0].split("~=")[0].strip()
                    technologies.add(pkg)

        # package.json分析
        pkg_file = self.project_root / "package.json"
        if pkg_file.exists():
            try:
                pkg_data = json.loads(pkg_file.read_text())
                for deps in [
                    pkg_data.get("dependencies", {}),
                    pkg_data.get("devDependencies", {}),
                ]:
                    technologies.update(deps.keys())
            except json.JSONDecodeError:
                pass

        # pyproject.toml分析
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            content = pyproject_file.read_text()
            # 簡易TOML解析
            deps_section = re.search(
                r"\[tool\.poetry\.dependencies\](.*?)\[", content, re.DOTALL
            )
            if deps_section:
                for line in deps_section.group(1).split("\n"):
                    if "=" in line:
                        dep = line.split("=")[0].strip().strip('"')
                        if dep:
                            technologies.add(dep)

        return {"technologies": list(technologies)}

    def _analyze_complexity(self) -> Dict[str, Any]:
        """複雑性分析"""
        complexity_score = 0
        indicators = []

        # ファイル数による複雑性
        total_files = sum(1 for _ in self.project_root.rglob("*") if _.is_file())
        if total_files > 1000:
            complexity_score += 3
            indicators.append("large_codebase")
        elif total_files > 500:
            complexity_score += 2
            indicators.append("medium_codebase")
        elif total_files > 100:
            complexity_score += 1
            indicators.append("small_codebase")

        # ディレクトリ構造による複雑性
        if (self.project_root / "src").exists():
            complexity_score += 1
        if (self.project_root / "tests").exists():
            complexity_score += 1
        if (self.project_root / "docs").exists():
            complexity_score += 1

        # 技術的複雑性
        if (self.project_root / "docker-compose.yml").exists():
            complexity_score += 2
            indicators.append("containerized")
        if (self.project_root / ".github").exists():
            complexity_score += 1
            indicators.append("ci_cd")

        # 複雑性レベル決定
        if complexity_score >= 8:
            level = "enterprise"
        elif complexity_score >= 5:
            level = "complex"
        elif complexity_score >= 3:
            level = "moderate"
        else:
            level = "simple"

        return {"level": level, "score": complexity_score, "indicators": indicators}

    def _determine_project_type(self, structure: Dict, technology: Dict) -> str:
        """プロジェクトタイプ決定"""
        technologies = {tech.lower() for tech in technology["technologies"]}

        # AI/MLプロジェクト
        ai_keywords = {
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "pandas",
            "numpy",
            "transformers",
        }
        if structure["has_ai_components"] or ai_keywords.intersection(technologies):
            return "ai_system"

        # Webアプリケーション
        web_keywords = {
            "react",
            "vue",
            "angular",
            "express",
            "flask",
            "django",
            "fastapi",
        }
        if structure["has_web_components"] or web_keywords.intersection(technologies):
            return "web_application"

        # データ分析
        data_keywords = {"jupyter", "matplotlib", "seaborn", "plotly", "streamlit"}
        if data_keywords.intersection(technologies):
            return "data_analysis"

        # インフラ・DevOps
        infra_keywords = {"docker", "kubernetes", "terraform", "ansible"}
        if infra_keywords.intersection(technologies):
            return "infrastructure"

        # デフォルト
        return "general_software"

    def _determine_required_expertise(
        self, project_type: str, technologies: List[str]
    ) -> List[str]:
        """必要専門知識決定"""
        expertise = set()

        # プロジェクトタイプ別
        type_expertise = {
            "ai_system": ["machine_learning", "data_processing", "ai_systems"],
            "web_application": ["frontend", "backend", "database"],
            "data_analysis": ["data_processing", "visualization", "statistics"],
            "infrastructure": ["deployment", "automation", "monitoring"],
            "general_software": ["programming", "testing", "documentation"],
        }

        expertise.update(type_expertise.get(project_type, []))

        # 技術スタック別
        tech_lower = [tech.lower() for tech in technologies]
        if any(t in tech_lower for t in ["security", "auth", "oauth"]):
            expertise.add("security")
        if any(t in tech_lower for t in ["test", "pytest", "jest"]):
            expertise.add("testing")
        if any(t in tech_lower for t in ["docker", "k8s", "kubernetes"]):
            expertise.add("deployment")

        return list(expertise)

    def _determine_optimal_team_composition(
        self, project_type: str, complexity: str, expertise: List[str]
    ) -> Tuple[int, List[str]]:
        """最適チーム構成決定"""
        base_roles = ["PRESIDENT"]  # PRESIDENTは常に含む

        # プロジェクトタイプ別推奨役職
        type_roles = {
            "ai_system": [
                "AI_SPECIALIST",
                "TECH_LEAD",
                "QA_SPECIALIST",
                "DOC_SPECIALIST",
            ],
            "web_application": [
                "FULL_STACK_DEV",
                "TECH_LEAD",
                "QA_SPECIALIST",
                "SECURITY_SPEC",
            ],
            "data_analysis": [
                "AI_SPECIALIST",
                "FULL_STACK_DEV",
                "QA_SPECIALIST",
                "DOC_SPECIALIST",
            ],
            "infrastructure": [
                "DEVOPS_SPEC",
                "SECURITY_SPEC",
                "TECH_LEAD",
                "QA_SPECIALIST",
            ],
            "general_software": [
                "FULL_STACK_DEV",
                "TECH_LEAD",
                "QA_SPECIALIST",
                "DOC_SPECIALIST",
            ],
        }

        recommended = type_roles.get(project_type, type_roles["general_software"])

        # 複雑性に応じた調整
        if complexity in ["complex", "enterprise"]:
            if "SECURITY_SPEC" not in recommended:
                recommended.append("SECURITY_SPEC")
            if "DEVOPS_SPEC" not in recommended and len(recommended) < 6:
                recommended.append("DEVOPS_SPEC")

        # 最低4ワーカー保証
        if len(recommended) < 4:
            missing = 4 - len(recommended)
            extras = ["FULL_STACK_DEV", "QA_SPECIALIST", "DOC_SPECIALIST", "TECH_LEAD"]
            for extra in extras[:missing]:
                if extra not in recommended:
                    recommended.append(extra)

        all_roles = base_roles + recommended
        return len(all_roles), all_roles

    def _identify_critical_files(self) -> List[str]:
        """重要ファイル特定"""
        critical = []

        standard_files = [
            "README.md",
            "CLAUDE.md",
            "Index.md",
            "Makefile",
            "requirements.txt",
        ]
        for file in standard_files:
            if (self.project_root / file).exists():
                critical.append(file)

        # src/配下の主要ファイル
        src_dir = self.project_root / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if py_file.stat().st_size > 1000:  # 1KB以上
                    critical.append(str(py_file.relative_to(self.project_root)))

        return critical[:20]  # 上位20ファイル

    def _calculate_confidence(self, structure: Dict, documentation: Dict) -> float:
        """分析信頼度計算"""
        confidence = 0.5  # ベース信頼度

        # 構造的要素による信頼度向上
        if structure["src_dirs"]:
            confidence += 0.1
        if structure["test_dirs"]:
            confidence += 0.1
        if structure["documentation_dirs"]:
            confidence += 0.1

        # ドキュメント品質による信頼度向上
        if documentation["objectives"]:
            confidence += 0.1
        if documentation["features"]:
            confidence += 0.1

        return min(confidence, 1.0)

    def _cache_analysis(self, analysis: ProjectAnalysis):
        """分析結果キャッシュ"""
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis": asdict(analysis),
        }

        self.analysis_cache.parent.mkdir(parents=True, exist_ok=True)
        with open(self.analysis_cache, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def launch_ai_organization(self, analysis: ProjectAnalysis) -> bool:
        """AI組織自動起動"""
        self.logger.info(
            f"Launching AI organization for {analysis.project_type} project"
        )

        try:
            # 既存セッションクリーンアップ
            self._cleanup_existing_sessions()

            # AI組織設定ファイル作成（ai-team.shの要件）
            self._ensure_ai_org_configuration()

            # 既存ai-team.shを使用してtmux起動
            ai_team_script = self.project_root / "scripts/tools/system/ai-team.sh"

            if not ai_team_script.exists():
                self.logger.error(f"AI team script not found: {ai_team_script}")
                return False

            # Direct tmux AI organization launch (bypassing interactive confirmation)
            success = self._launch_tmux_ai_organization_direct()

            if success:
                result = type("Result", (), {"returncode": 0})()
            else:
                result = type(
                    "Result",
                    (),
                    {
                        "returncode": 1,
                        "stdout": "",
                        "stderr": "Direct tmux launch failed",
                    },
                )()

            # Fallback to ai-team.sh with automatic confirmation
            if not success:
                result = self._launch_with_auto_confirmation(ai_team_script)

            if result.returncode == 0:
                self.logger.info("AI organization launched successfully")

                # 役職特化メッセージ送信
                self._send_specialized_instructions(analysis)
                return True
            else:
                self.logger.error("Failed to launch AI organization:")
                self.logger.error(f"Return code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error launching AI organization: {e}")
            return False

    def _cleanup_existing_sessions(self):
        """既存tmuxセッションクリーンアップ"""
        sessions_to_cleanup = ["president", "multiagent"]

        for session in sessions_to_cleanup:
            try:
                # Check if session exists
                result = subprocess.run(
                    ["tmux", "has-session", "-t", session],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    self.logger.info(f"Cleaning up existing session: {session}")
                    subprocess.run(["tmux", "kill-session", "-t", session], check=True)
                    self.logger.info(f"Session {session} cleaned up successfully")

            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Failed to cleanup session {session}: {e}")

    def _ensure_ai_org_configuration(self):
        """AI組織設定ファイル確保"""
        config_file = self.project_root / ".ai-org-configured"

        if not config_file.exists():
            self.logger.info("Creating AI organization configuration file")
            config_file.touch()
            self.logger.info("AI organization configuration file created")
        else:
            self.logger.info("AI organization configuration file already exists")

    def _launch_tmux_ai_organization_direct(self) -> bool:
        """直接tmuxコマンドでAI組織起動"""
        try:
            self.logger.info("Launching AI organization via direct tmux commands")

            # Step 1: Start PRESIDENT session
            subprocess.run(
                [
                    "tmux",
                    "new-session",
                    "-d",
                    "-s",
                    "president",
                    "-c",
                    str(self.project_root),
                ],
                check=True,
            )

            subprocess.run(
                [
                    "tmux",
                    "send-keys",
                    "-t",
                    "president",
                    "claude --dangerously-skip-permissions",
                    "C-m",
                ],
                check=True,
            )

            # Step 2: Start multiagent session with 4 panes
            subprocess.run(
                [
                    "tmux",
                    "new-session",
                    "-d",
                    "-s",
                    "multiagent",
                    "-c",
                    str(self.project_root),
                ],
                check=True,
            )

            # Split into 4 panes
            subprocess.run(
                ["tmux", "split-window", "-h", "-t", "multiagent"], check=True
            )
            subprocess.run(
                ["tmux", "split-window", "-v", "-t", "multiagent:0.0"], check=True
            )
            subprocess.run(
                ["tmux", "split-window", "-v", "-t", "multiagent:0.1"], check=True
            )
            subprocess.run(
                ["tmux", "select-layout", "-t", "multiagent", "tiled"], check=True
            )

            # Set pane titles and start Claude instances
            titles = [
                "👔：BOSS1：統括管理",
                "💻：WORKER1：開発実装",
                "🔧：WORKER2：品質管理",
                "🎨：WORKER3：設計文書",
            ]
            for i in range(4):
                subprocess.run(
                    ["tmux", "select-pane", "-t", f"multiagent:0.{i}", "-T", titles[i]],
                    check=True,
                )

                subprocess.run(
                    [
                        "tmux",
                        "send-keys",
                        "-t",
                        f"multiagent:0.{i}",
                        "claude --dangerously-skip-permissions",
                        "C-m",
                    ],
                    check=True,
                )
                time.sleep(3)  # Longer delay for proper initialization

            # Wait for Claude initialization and send Enter to complete setup
            self.logger.info("Waiting for Claude instances to initialize...")
            time.sleep(10)  # Wait for all instances to start

            # Send Enter to complete Claude initialization
            for i in range(4):
                subprocess.run(
                    ["tmux", "send-keys", "-t", f"multiagent:0.{i}", "C-m"], check=True
                )
                time.sleep(1)

            # Also send Enter to PRESIDENT
            subprocess.run(["tmux", "send-keys", "-t", "president", "C-m"], check=True)

            # Wait for final initialization
            time.sleep(5)

            # Verify initialization
            self._verify_claude_initialization()

            # Configure status bar with perfect enforcer
            self._apply_perfect_statusbar_system()

            # Start worker status monitoring
            self._start_worker_status_monitoring()

            self.logger.info("AI organization launched successfully via direct tmux")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to launch AI organization via direct tmux: {e}")
            return False

    def _verify_claude_initialization(self):
        """Verify Claude instances are properly initialized"""
        panes_to_check = ["president"] + [f"multiagent:0.{i}" for i in range(4)]

        for pane in panes_to_check:
            try:
                result = subprocess.run(
                    ["tmux", "capture-pane", "-t", pane, "-p"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                content = result.stdout.strip()
                if "How can I help" in content:
                    self.logger.info(f"✅ {pane}: Claude initialized successfully")
                else:
                    self.logger.warning(
                        f"⚠️  {pane}: Claude may not be fully initialized"
                    )
                    # Try sending another Enter
                    subprocess.run(["tmux", "send-keys", "-t", pane, "C-m"], check=True)

            except Exception as e:
                self.logger.error(f"Failed to verify {pane}: {e}")

    def _apply_perfect_statusbar_system(self):
        """完璧なステータスバーシステム適用"""
        try:
            from src.orchestrator.tmux_statusbar_enforcer import TmuxStatusBarEnforcer

            self.logger.info("Applying perfect statusbar system...")
            enforcer = TmuxStatusBarEnforcer(str(self.project_root))

            # 全セッション設定適用
            results = enforcer.apply_all_sessions()

            success_count = sum(1 for result in results.values() if result)
            total_count = len(results)

            self.logger.info(
                f"StatusBar configuration: {success_count}/{total_count} sessions successful"
            )

            # 継続監視開始
            enforcer.start_continuous_monitoring()
            self.logger.info(
                "✅ Perfect statusbar system activated with continuous monitoring"
            )

        except Exception as e:
            self.logger.error(f"Error applying perfect statusbar system: {e}")
            # フォールバック: 基本設定
            self._apply_basic_statusbar_fallback()

    def _apply_basic_statusbar_fallback(self):
        """基本ステータスバー設定（フォールバック）"""
        try:
            self.logger.info("Applying basic statusbar fallback...")

            sessions = ["president", "multiagent"]
            for session in sessions:
                if self._session_exists(session):
                    subprocess.run(
                        ["tmux", "set-option", "-t", session, "status", "on"],
                        check=True,
                    )
                    subprocess.run(
                        [
                            "tmux",
                            "set-option",
                            "-t",
                            session,
                            "pane-border-status",
                            "top",
                        ],
                        check=True,
                    )
                    subprocess.run(
                        [
                            "tmux",
                            "set-option",
                            "-t",
                            session,
                            "pane-border-format",
                            "#{pane_title}",
                        ],
                        check=True,
                    )

            self.logger.info("Basic statusbar fallback applied")

        except Exception as e:
            self.logger.error(f"Error in statusbar fallback: {e}")

    def _session_exists(self, session_name: str) -> bool:
        """セッション存在確認"""
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _start_worker_status_monitoring(self):
        """ワーカーステータス監視開始"""
        try:
            # 役職とタスクのリアルタイム表示を優先
            from src.orchestrator.realtime_task_display_system import (
                RealtimeTaskDisplaySystem,
            )

            self.logger.info("Starting realtime task display system...")
            task_display = RealtimeTaskDisplaySystem(str(self.project_root))

            # バックグラウンドで監視開始
            import threading

            display_thread = threading.Thread(
                target=task_display.start_monitoring, daemon=True
            )
            display_thread.start()

            self.logger.info("✅ Realtime task display system activated")

            # 既存のワーカーステータス監視も起動（補助的に）
            try:
                from src.orchestrator.ai_worker_status_monitor import (
                    AIWorkerStatusMonitor,
                )

                monitor = AIWorkerStatusMonitor(str(self.project_root))
                monitor_thread = threading.Thread(
                    target=monitor.start_monitoring, daemon=True
                )
                monitor_thread.start()
                self.logger.info("✅ Worker status monitoring also activated")
            except Exception:
                pass  # 補助システムなので失敗しても続行

        except Exception as e:
            self.logger.error(f"Error starting task display system: {e}")

    def _launch_with_auto_confirmation(self, ai_team_script: Path) -> object:
        """ai-team.shに自動確認を送信して起動"""
        try:
            self.logger.info("Attempting AI organization launch with auto-confirmation")

            # Use 'yes' command to automatically confirm
            result = subprocess.run(
                ["sh", "-c", f"echo 'Y' | {ai_team_script} start"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            return result

        except Exception as e:
            self.logger.error(f"Auto-confirmation launch failed: {e}")
            return type(
                "Result", (), {"returncode": 1, "stdout": "", "stderr": str(e)}
            )()

    def _send_specialized_instructions(self, analysis: ProjectAnalysis):
        """専門化指示送信（全ワーカーに送信+エンター処理）"""
        time.sleep(8)  # AI組織起動待機（より長めに）

        # PRESIDENT向けプロジェクト概要
        president_msg = f"""
プロジェクト分析完了。以下のプロジェクト特性に基づいてチームを指揮してください：

📊 プロジェクト分析結果:
- タイプ: {analysis.project_type}
- 複雑度: {analysis.complexity_level}
- 主要技術: {", ".join(analysis.key_technologies[:5])}
- 推奨チーム: {", ".join(analysis.recommended_roles)}

🎯 主要目標:
{chr(10).join(f"- {obj}" for obj in analysis.primary_objectives[:3])}

各ワーカーに専門分野を割り当て、効率的なタスク分散を実行してください。
        """

        # マルチエージェント向け基本指示
        worker_base_msg = f"""
🚀 AI組織システム稼働開始

プロジェクト: {analysis.project_type} ({analysis.complexity_level})
技術スタック: {", ".join(analysis.key_technologies[:3])}

各自の専門分野を活かして効率的にタスクを実行してください。
不明な点があればPRESIDENTに確認してください。
        """

        try:
            # PRESIDENT向け詳細指示送信
            self._send_message_with_enter("president", president_msg)
            self.logger.info("✅ Specialized instructions sent to PRESIDENT")

            time.sleep(3)  # ワーカー指示前の待機

            # 各ワーカーに基本指示送信
            worker_panes = [f"multiagent:0.{i}" for i in range(4)]
            worker_roles = ["BOSS1", "WORKER1", "WORKER2", "WORKER3"]

            for _i, (pane, role) in enumerate(zip(worker_panes, worker_roles)):
                role_specific_msg = f"{worker_base_msg}\n\n👔 あなたの役職: {role}"
                self._send_message_with_enter(pane, role_specific_msg)
                self.logger.info(f"✅ Instructions sent to {role} ({pane})")
                time.sleep(2)  # 各ワーカー間の間隔

            self.logger.info("🎉 All specialized instructions sent successfully")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to send instructions: {e}")
        except Exception as e:
            self.logger.error(f"Error in instruction sending: {e}")

    def _send_message_with_enter(self, pane_target: str, message: str):
        """メッセージ送信後に確実にエンターを押す"""
        try:
            # 1. メッセージをプロンプトにセット（send-keysで文字列送信）
            subprocess.run(
                ["tmux", "send-keys", "-t", pane_target, message], check=True
            )

            time.sleep(1)  # セット後の短い待機

            # 2. エンターキーで送信実行
            subprocess.run(["tmux", "send-keys", "-t", pane_target, "C-m"], check=True)

            self.logger.debug(f"Message sent to {pane_target} with Enter")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to send message to {pane_target}: {e}")
            raise


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="Intelligent Project Analyzer")
    parser.add_argument(
        "action", choices=["analyze", "launch", "full"], help="Action to perform"
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    analyzer = IntelligentProjectAnalyzer(args.project_root)

    if args.action == "analyze":
        analysis = analyzer.analyze_project_comprehensively()
        print(json.dumps(asdict(analysis), indent=2, ensure_ascii=False))

    elif args.action == "launch":
        # 既存分析を使用してAI組織起動
        if analyzer.analysis_cache.exists():
            cache_data = json.load(open(analyzer.analysis_cache))
            analysis = ProjectAnalysis(**cache_data["analysis"])
            success = analyzer.launch_ai_organization(analysis)
            print(f"AI Organization Launch: {'SUCCESS' if success else 'FAILED'}")
        else:
            print("No cached analysis found. Run 'analyze' first.")

    elif args.action == "full":
        # 完全自動実行
        analysis = analyzer.analyze_project_comprehensively()
        print("Project Analysis Completed")
        print(f"Project Type: {analysis.project_type}")
        print(f"Complexity: {analysis.complexity_level}")
        print(f"Recommended Team: {', '.join(analysis.recommended_roles)}")

        success = analyzer.launch_ai_organization(analysis)
        print(f"AI Organization Launch: {'SUCCESS' if success else 'FAILED'}")


if __name__ == "__main__":
    main()
