#!/usr/bin/env python3
"""
AI制御ルールプロダクト構成の徹底的評価システム
O3 + Gemini による包括的分析と改善提案
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ComprehensiveStructureEvaluator:
    """構造評価システム"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.evaluation_result = {}

    def analyze_current_structure(self) -> Dict:
        """現在の構造分析"""
        structure = {
            "root_directories": [],
            "total_files": 0,
            "file_distribution": {},
            "key_components": [],
            "rule_files": [],
            "ai_specific_dirs": [],
            "complexity_metrics": {},
        }

        # ルートディレクトリ分析
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                structure["root_directories"].append(
                    {
                        "name": item.name,
                        "file_count": len(list(item.rglob("*"))),
                        "subdirs": len([d for d in item.iterdir() if d.is_dir()]),
                        "purpose": self._identify_directory_purpose(item.name),
                    }
                )

        # ファイル分布分析
        for ext in [".py", ".sh", ".md", ".json", ".yml", ".yaml"]:
            files = list(self.project_root.rglob(f"*{ext}"))
            structure["file_distribution"][ext] = len(files)
            structure["total_files"] += len(files)

        # 重要コンポーネント確認
        key_files = [
            "STATUS.md",
            "0-ROOT.yml",
            "CLAUDE.md",
            "Makefile",
            "pyproject.toml",
            ".gitignore",
        ]
        for key_file in key_files:
            if (self.project_root / key_file).exists():
                structure["key_components"].append(key_file)

        # ルールファイル確認
        rule_patterns = ["*rules*", "*RULE*", "*.mdc", "*policy*"]
        for pattern in rule_patterns:
            structure["rule_files"].extend(
                [
                    str(f.relative_to(self.project_root))
                    for f in self.project_root.rglob(pattern)
                    if f.is_file()
                ]
            )

        # AI特化ディレクトリ確認
        ai_dirs = ["data", "models", "api", "compliance", "runtime", "ai-agents"]
        for ai_dir in ai_dirs:
            if (self.project_root / ai_dir).exists():
                structure["ai_specific_dirs"].append(ai_dir)

        # 複雑さメトリクス
        structure["complexity_metrics"] = {
            "directory_depth": self._calculate_max_depth(),
            "circular_references": self._check_circular_references(),
            "orphaned_files": self._find_orphaned_files(),
            "duplicate_patterns": self._analyze_duplicate_patterns(),
        }

        return structure

    def _identify_directory_purpose(self, dir_name: str) -> str:
        """ディレクトリの目的識別"""
        purpose_map = {
            "src": "Source code",
            "docs": "Documentation",
            "tests": "Test files",
            "scripts": "Utility scripts",
            "data": "AI/ML data assets",
            "models": "ML models",
            "api": "API definitions",
            "compliance": "Governance & ethics",
            "runtime": "Runtime data",
            "config": "Configuration",
            "ops": "Operations",
            "validation": "Validation",
        }
        return purpose_map.get(dir_name.lower(), "Unknown/Custom")

    def _calculate_max_depth(self) -> int:
        """最大ディレクトリ深度計算"""
        max_depth = 0
        for path in self.project_root.rglob("*"):
            if path.is_dir():
                depth = len(path.relative_to(self.project_root).parts)
                max_depth = max(max_depth, depth)
        return max_depth

    def _check_circular_references(self) -> List[str]:
        """循環参照チェック"""
        # 簡易実装：シンボリックリンクの循環確認
        circular_refs = []
        for path in self.project_root.rglob("*"):
            if path.is_symlink():
                try:
                    target = path.resolve()
                    if not target.exists():
                        circular_refs.append(str(path))
                except Exception:
                    circular_refs.append(str(path))
        return circular_refs

    def _find_orphaned_files(self) -> List[str]:
        """孤立ファイル検出"""
        orphaned = []
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                # 親ディレクトリにREADMEがなく、一人ぼっちのファイル
                parent = file_path.parent
                siblings = [f for f in parent.iterdir() if f.is_file()]
                if len(siblings) == 1 and not any(
                    s.name.startswith("README") for s in parent.iterdir()
                ):
                    orphaned.append(str(file_path.relative_to(self.project_root)))
        return orphaned[:10]  # 最大10個まで

    def _analyze_duplicate_patterns(self) -> Dict:
        """重複パターン分析"""
        name_counts = {}
        for path in self.project_root.rglob("*"):
            if path.is_file():
                name = path.name
                if name not in name_counts:
                    name_counts[name] = 0
                name_counts[name] += 1

        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        return dict(sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10])

    def evaluate_ai_product_requirements(self, structure: Dict) -> Dict:
        """AI制御ルールプロダクトとしての要件評価"""
        requirements = {
            "ai_governance": {"score": 0, "max_score": 100, "checks": []},
            "rule_management": {"score": 0, "max_score": 100, "checks": []},
            "automation": {"score": 0, "max_score": 100, "checks": []},
            "scalability": {"score": 0, "max_score": 100, "checks": []},
        }

        # AI ガバナンス評価
        ai_gov_checks = [
            (
                "compliance/ directory exists",
                "compliance" in structure["ai_specific_dirs"],
                25,
            ),
            (
                "0-ROOT.yml constitutional rules",
                "0-ROOT.yml" in structure["key_components"],
                25,
            ),
            (
                "AI ethics documentation",
                any("ethics" in rf.lower() for rf in structure["rule_files"]),
                20,
            ),
            (
                "Model governance structure",
                "models" in structure["ai_specific_dirs"],
                20,
            ),
            ("Data governance structure", "data" in structure["ai_specific_dirs"], 10),
        ]

        for check_name, passed, points in ai_gov_checks:
            requirements["ai_governance"]["checks"].append(
                {
                    "name": check_name,
                    "passed": passed,
                    "points": points if passed else 0,
                }
            )
            if passed:
                requirements["ai_governance"]["score"] += points

        # ルール管理評価
        rule_mgmt_checks = [
            ("Hierarchical rule structure", len(structure["rule_files"]) >= 5, 30),
            (
                "Rule versioning system",
                any("version" in rf.lower() for rf in structure["rule_files"]),
                20,
            ),
            (
                "Automated rule validation",
                any("validate" in rf.lower() for rf in structure["rule_files"]),
                25,
            ),
            (
                "Rule documentation",
                len([rf for rf in structure["rule_files"] if rf.endswith(".md")]) >= 3,
                25,
            ),
        ]

        for check_name, passed, points in rule_mgmt_checks:
            requirements["rule_management"]["checks"].append(
                {
                    "name": check_name,
                    "passed": passed,
                    "points": points if passed else 0,
                }
            )
            if passed:
                requirements["rule_management"]["score"] += points

        # 自動化評価
        automation_checks = [
            (
                "Scripts directory",
                any(d["name"] == "scripts" for d in structure["root_directories"]),
                25,
            ),
            ("Runtime monitoring", "runtime" in structure["ai_specific_dirs"], 25),
            ("Automated status system", "STATUS.md" in structure["key_components"], 25),
            (
                "CI/CD integration",
                any(
                    "github" in rf.lower() or "workflow" in rf.lower()
                    for rf in structure["rule_files"]
                ),
                25,
            ),
        ]

        for check_name, passed, points in automation_checks:
            requirements["automation"]["checks"].append(
                {
                    "name": check_name,
                    "passed": passed,
                    "points": points if passed else 0,
                }
            )
            if passed:
                requirements["automation"]["score"] += points

        # スケーラビリティ評価
        scalability_checks = [
            (
                "Directory count optimization",
                len(structure["root_directories"]) <= 12,
                25,
            ),
            ("Modular API structure", "api" in structure["ai_specific_dirs"], 25),
            (
                "Configuration management",
                any(d["name"] == "config" for d in structure["root_directories"]),
                20,
            ),
            (
                "Low complexity",
                structure["complexity_metrics"]["directory_depth"] <= 6,
                30,
            ),
        ]

        for check_name, passed, points in scalability_checks:
            requirements["scalability"]["checks"].append(
                {
                    "name": check_name,
                    "passed": passed,
                    "points": points if passed else 0,
                }
            )
            if passed:
                requirements["scalability"]["score"] += points

        return requirements

    def generate_o3_evaluation_prompt(self, structure: Dict, requirements: Dict) -> str:
        """O3評価用プロンプト生成"""
        return f"""
COMPREHENSIVE PROJECT STRUCTURE EVALUATION REQUEST

## Project Overview
This is an AI control rule product with the following current structure:

### Root Directories ({len(structure["root_directories"])})
{chr(10).join([f"- {d['name']}: {d['file_count']} files, purpose: {d['purpose']}" for d in structure["root_directories"]])}

### File Distribution
{chr(10).join([f"- {ext}: {count} files" for ext, count in structure["file_distribution"].items()])}

### AI-Specific Components
{chr(10).join([f"- {comp}" for comp in structure["ai_specific_dirs"]])}

### Complexity Metrics
- Max directory depth: {structure["complexity_metrics"]["directory_depth"]}
- Duplicate file patterns: {len(structure["complexity_metrics"]["duplicate_patterns"])}
- Orphaned files: {len(structure["complexity_metrics"]["orphaned_files"])}

### Current AI Product Requirements Score
- AI Governance: {requirements["ai_governance"]["score"]}/100
- Rule Management: {requirements["rule_management"]["score"]}/100
- Automation: {requirements["automation"]["score"]}/100
- Scalability: {requirements["scalability"]["score"]}/100

## Evaluation Questions

Please provide a comprehensive evaluation addressing:

1. **STRUCTURAL EXCELLENCE**: How does this structure compare to enterprise-grade AI governance products? Rate 1-10 and explain.

2. **AI CONTROL PRODUCT FITNESS**: Is this structure optimal for an AI rule control system? What are the critical gaps?

3. **SCALABILITY CONCERNS**: Can this structure handle 10x growth in rules, models, and data? What would break first?

4. **SECURITY & GOVERNANCE**: How well does this support AI ethics, compliance, and auditability requirements?

5. **DEVELOPER EXPERIENCE**: How intuitive is this structure for AI engineers, governance teams, and operators?

6. **IMMEDIATE IMPROVEMENTS**: What are the top 5 most critical structural changes needed?

7. **ANTI-PATTERNS**: What anti-patterns do you see that could cause problems?

8. **INDUSTRY STANDARDS**: How does this compare to industry standards for AI governance platforms?

Please be brutally honest and specific in your recommendations.
"""

    def generate_gemini_evaluation_prompt(
        self, structure: Dict, requirements: Dict
    ) -> str:
        """Gemini評価用プロンプト生成"""
        return f"""
AI/ML PRODUCT ARCHITECTURE EVALUATION

## Context
Evaluating a production AI control and governance system structure for enterprise deployment.

## Current Architecture Analysis

### Directory Structure
{json.dumps(structure["root_directories"], indent=2)}

### AI/ML Specific Assessment
- Data management: {"✅" if "data" in structure["ai_specific_dirs"] else "❌"}
- Model governance: {"✅" if "models" in structure["ai_specific_dirs"] else "❌"}
- API standardization: {"✅" if "api" in structure["ai_specific_dirs"] else "❌"}
- Compliance framework: {"✅" if "compliance" in structure["ai_specific_dirs"] else "❌"}

### Technical Metrics
- Codebase size: {structure["total_files"]} files
- Max depth: {structure["complexity_metrics"]["directory_depth"]} levels
- Rule files: {len(structure["rule_files"])} files

## Gemini-Specific Evaluation Areas

1. **MLOps READINESS**: How well does this support ML model lifecycle management? Missing components?

2. **DATA GOVERNANCE**: Is the data/ structure sufficient for enterprise AI data management?

3. **MODEL VERSIONING**: How would you implement model versioning and experiment tracking in this structure?

4. **AI SAFETY**: Does this structure adequately support AI safety, testing, and validation workflows?

5. **MULTI-MODEL ORCHESTRATION**: Can this handle multiple AI models with different requirements?

6. **COMPLIANCE AUTOMATION**: How well does this support automated compliance checking and reporting?

7. **API GATEWAY PATTERNS**: Is the api/ structure suitable for microservices and API management?

8. **MONITORING & OBSERVABILITY**: What's missing for production AI system monitoring?

9. **DEPLOYMENT PATTERNS**: How would you structure this for container/K8s deployment?

10. **SECURITY ARCHITECTURE**: What security concerns do you see in this structure?

Please provide specific, actionable recommendations for each area.
"""

    def run_comprehensive_evaluation(self) -> Dict:
        """包括的評価実行"""
        print("🔍 包括的構造評価開始...")

        # 1. 現在構造分析
        structure = self.analyze_current_structure()
        print(
            f"✅ 構造分析完了: {len(structure['root_directories'])}ディレクトリ, {structure['total_files']}ファイル"
        )

        # 2. AI プロダクト要件評価
        requirements = self.evaluate_ai_product_requirements(structure)
        print(
            f"✅ 要件評価完了: 平均スコア {sum(req['score'] for req in requirements.values()) / 4:.1f}/100"
        )

        # 3. O3 評価
        print("🤖 O3による構造評価実行中...")
        o3_prompt = self.generate_o3_evaluation_prompt(structure, requirements)

        # 4. Gemini 評価
        print("🤖 Geminiによる AI/ML特化評価実行中...")
        gemini_prompt = self.generate_gemini_evaluation_prompt(structure, requirements)

        evaluation_result = {
            "timestamp": datetime.now().isoformat(),
            "structure_analysis": structure,
            "requirements_assessment": requirements,
            "o3_evaluation_prompt": o3_prompt,
            "gemini_evaluation_prompt": gemini_prompt,
            "overall_health_score": sum(req["score"] for req in requirements.values())
            / 4,
        }

        return evaluation_result

    def save_evaluation_results(self, results: Dict):
        """評価結果保存"""
        output_file = (
            self.project_root
            / "runtime"
            / f"structure-evaluation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"📊 評価結果保存: {output_file}")
        return output_file


def main():
    """メイン実行"""
    evaluator = ComprehensiveStructureEvaluator()

    print("🎯 AI制御ルールプロダクト構造評価システム")
    print("=" * 60)

    # 包括評価実行
    results = evaluator.run_comprehensive_evaluation()

    # 結果保存
    output_file = evaluator.save_evaluation_results(results)

    # サマリー表示
    print("\n📋 評価サマリー:")
    print(f"  全体健全性スコア: {results['overall_health_score']:.1f}/100")
    print(
        f"  ルートディレクトリ数: {len(results['structure_analysis']['root_directories'])}"
    )
    print(
        f"  AI特化コンポーネント: {len(results['structure_analysis']['ai_specific_dirs'])}"
    )
    print(f"  ルールファイル数: {len(results['structure_analysis']['rule_files'])}")

    print("\n🤖 AI評価プロンプトを確認:")
    print(f"  {output_file}")

    print("\n📋 次のステップ:")
    print("  1. O3とGeminiに評価プロンプトを送信")
    print("  2. 評価結果に基づく改善計画作成")
    print("  3. 構造最適化実行")

    return output_file


if __name__ == "__main__":
    main()
