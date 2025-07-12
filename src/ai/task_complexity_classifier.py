#!/usr/bin/env python3
"""
Task Complexity Classification System
タスク複雑度判定・適切手法選択システム
PRESIDENT/指揮者による効率的タスク分類
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskComplexity(Enum):
    """タスク複雑度レベル"""

    SIMPLE = "simple"  # LEVEL 1: 直接実行（no thinking）
    STANDARD = "standard"  # LEVEL 2: 計画実行（<thinking>）
    COMPLEX = "complex"  # LEVEL 3: AI協業+ultrathink（<thinking>）
    CRITICAL = "critical"  # LEVEL 4: 完全協業+max ultrathink（<thinking>）


class ExecutionMethod(Enum):
    """実行手法"""

    DIRECT = "direct"  # LEVEL 1: 直接実行（no thinking）
    PLANNED = "planned"  # LEVEL 2: 計画実行（<thinking>）
    AI_COLLABORATION = "ai_collaboration"  # LEVEL 3: AI協業（ultrathink）
    FULL_COLLABORATION = "full_collaboration"  # LEVEL 4: 完全協業（max ultrathink）


class ThinkingLevel(Enum):
    """思考レベル"""

    NONE = "none"  # thinking不要
    STANDARD = "standard"  # <thinking>必須
    ULTRATHINK = "ultrathink"  # ultrathink深思考
    MAX_ULTRATHINK = "max_ultrathink"  # ultrathink最大深度


@dataclass
class TaskClassification:
    """タスク分類結果"""

    complexity: TaskComplexity
    execution_method: ExecutionMethod
    thinking_level: ThinkingLevel
    confidence: float
    reasoning: str
    estimated_time: int  # 分
    required_tools: List[str]
    required_files: List[str]
    ai_collaboration_needed: bool
    risk_level: str


class TaskComplexityClassifier:
    """タスク複雑度分類器"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.patterns = self._load_classification_patterns()

    def _load_classification_patterns(self) -> Dict[str, Any]:
        """分類パターン読み込み"""
        return {
            "simple_patterns": [
                # LEVEL 1: 直接実行パターン
                r"(?i)(show|display|list|view|read|check|status|info|get)",
                r"(?i)(what|where|which|how many|count)",
                r"(?i)(ls|pwd|whoami|date|echo)",
                r"(?i)(単純な|簡単な|確認|表示|リスト)",
            ],
            "standard_patterns": [
                # LEVEL 2: 計画実行パターン
                r"(?i)(edit|modify|update|change|replace|fix)",
                r"(?i)(add|remove|delete|create|write)",
                r"(?i)(copy|move|rename|chmod)",
                r"(?i)(run|execute|start|stop)",
                r"(?i)(編集|修正|更新|変更|追加|削除|作成)",
            ],
            "complex_patterns": [
                # LEVEL 3: AI協業+ultrathinkパターン
                r"(?i)(implement|develop|build|design|architect)",
                r"(?i)(refactor|restructure|optimize|migrate)",
                r"(?i)(integrate|configure|setup|install)",
                r"(?i)(test|debug|troubleshoot|analyze)",
                r"(?i)(実装|開発|構築|設計|統合|設定|テスト)",
            ],
            "critical_patterns": [
                # LEVEL 4: 完全協業+max ultrathinkパターン
                r"(?i)(strategy|architecture|framework|system)",
                r"(?i)(evaluate|assess|recommend|decide)",
                r"(?i)(research|investigate|explore|discover)",
                r"(?i)(coordinate|manage|orchestrate|govern)",
                r"(?i)(critical|system-wide|infrastructure|migration)",
                r"(?i)(戦略|アーキテクチャ|システム|評価|研究|調査|管理|重要|基盤)",
            ],
            "scale_indicators": {
                "file_count": {
                    "single": 1,  # TRIVIAL/SIMPLE
                    "few": 5,  # SIMPLE/COMPLEX
                    "many": 20,  # COMPLEX/AI_CONSULTATION
                },
                "time_indicators": {
                    "minutes": ["minute", "min", "quick", "fast", "分"],
                    "hours": ["hour", "時間", "long", "detailed"],
                    "days": ["day", "days", "日", "extensive", "comprehensive"],
                },
            },
        }

    def classify_task(
        self, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> TaskClassification:
        """タスク分類"""
        context = context or {}

        # 複数指標による分類
        complexity_scores = {
            TaskComplexity.SIMPLE: 0,
            TaskComplexity.STANDARD: 0,
            TaskComplexity.COMPLEX: 0,
            TaskComplexity.CRITICAL: 0,
        }

        # 1. パターンマッチング分析
        pattern_scores = self._analyze_patterns(task_description)
        for complexity, score in pattern_scores.items():
            complexity_scores[complexity] += score * 0.4

        # 2. 規模指標分析
        scale_scores = self._analyze_scale_indicators(task_description, context)
        for complexity, score in scale_scores.items():
            complexity_scores[complexity] += score * 0.3

        # 3. コンテキスト分析
        context_scores = self._analyze_context(task_description, context)
        for complexity, score in context_scores.items():
            complexity_scores[complexity] += score * 0.2

        # 4. キーワード密度分析
        keyword_scores = self._analyze_keyword_density(task_description)
        for complexity, score in keyword_scores.items():
            complexity_scores[complexity] += score * 0.1

        # 最高スコアの複雑度を選択
        max_complexity = max(complexity_scores.items(), key=lambda x: x[1])
        complexity = max_complexity[0]
        confidence = min(1.0, max_complexity[1])

        # 実行手法決定
        execution_method = self._determine_execution_method(
            complexity, task_description, context
        )

        # 思考レベル決定
        thinking_level = self._determine_thinking_level(complexity)

        # 詳細情報生成
        reasoning = self._generate_reasoning(
            complexity, complexity_scores, task_description
        )
        estimated_time = self._estimate_time(complexity, task_description)
        required_tools = self._identify_required_tools(task_description)
        required_files = self._get_required_files(complexity)
        ai_collaboration_needed = complexity in [
            TaskComplexity.COMPLEX,
            TaskComplexity.CRITICAL,
        ]
        risk_level = self._assess_risk_level(complexity, task_description)

        return TaskClassification(
            complexity=complexity,
            execution_method=execution_method,
            thinking_level=thinking_level,
            confidence=confidence,
            reasoning=reasoning,
            estimated_time=estimated_time,
            required_tools=required_tools,
            required_files=required_files,
            ai_collaboration_needed=ai_collaboration_needed,
            risk_level=risk_level,
        )

    def _analyze_patterns(self, task_description: str) -> Dict[TaskComplexity, float]:
        """パターン分析"""
        scores = dict.fromkeys(TaskComplexity, 0)

        # 各複雑度のパターンチェック
        patterns_map = {
            TaskComplexity.SIMPLE: self.patterns["simple_patterns"],
            TaskComplexity.STANDARD: self.patterns["standard_patterns"],
            TaskComplexity.COMPLEX: self.patterns["complex_patterns"],
            TaskComplexity.CRITICAL: self.patterns["critical_patterns"],
        }

        for complexity, patterns in patterns_map.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, task_description))
                scores[complexity] += matches * 0.25

        return scores

    def _analyze_scale_indicators(
        self, task_description: str, context: Dict[str, Any]
    ) -> Dict[TaskComplexity, float]:
        """規模指標分析"""
        scores = dict.fromkeys(TaskComplexity, 0)

        # ファイル数推定
        file_indicators = [
            "file",
            "files",
            "ファイル",
            "directory",
            "directories",
            "フォルダ",
        ]
        file_mentions = sum(
            task_description.lower().count(indicator) for indicator in file_indicators
        )

        if file_mentions == 0 or file_mentions == 1:
            scores[TaskComplexity.SIMPLE] += 0.3
            scores[TaskComplexity.STANDARD] += 0.2
        elif file_mentions <= 3:
            scores[TaskComplexity.STANDARD] += 0.4
            scores[TaskComplexity.COMPLEX] += 0.2
        else:
            scores[TaskComplexity.COMPLEX] += 0.3
            scores[TaskComplexity.CRITICAL] += 0.2

        # 時間指標
        time_indicators = self.patterns["scale_indicators"]["time_indicators"]
        for time_category, keywords in time_indicators.items():
            for keyword in keywords:
                if keyword in task_description.lower():
                    if time_category == "minutes":
                        scores[TaskComplexity.SIMPLE] += 0.2
                        scores[TaskComplexity.STANDARD] += 0.1
                    elif time_category == "hours":
                        scores[TaskComplexity.COMPLEX] += 0.3
                    elif time_category == "days":
                        scores[TaskComplexity.CRITICAL] += 0.4

        return scores

    def _analyze_context(
        self, task_description: str, context: Dict[str, Any]
    ) -> Dict[TaskComplexity, float]:
        """コンテキスト分析"""
        scores = dict.fromkeys(TaskComplexity, 0)

        # 既存のシステム複雑度
        if context.get("existing_system_complexity", "low") == "high":
            scores[TaskComplexity.COMPLEX] += 0.2
            scores[TaskComplexity.AI_CONSULTATION] += 0.3

        # エラー対応タスク
        if context.get("is_error_response", False):
            scores[TaskComplexity.SIMPLE] += 0.2
            scores[TaskComplexity.COMPLEX] += 0.1

        # 前回のミス履歴
        if context.get("previous_mistakes_count", 0) > 0:
            scores[TaskComplexity.COMPLEX] += 0.2
            scores[TaskComplexity.AI_CONSULTATION] += 0.3

        # ユーザーの緊急度
        urgency = context.get("urgency", "normal")
        if urgency == "high":
            scores[TaskComplexity.SIMPLE] += 0.2
        elif urgency == "low":
            scores[TaskComplexity.AI_CONSULTATION] += 0.1

        return scores

    def _analyze_keyword_density(
        self, task_description: str
    ) -> Dict[TaskComplexity, float]:
        """キーワード密度分析"""
        scores = dict.fromkeys(TaskComplexity, 0)

        words = task_description.lower().split()
        word_count = len(words)

        if word_count == 0:
            return scores

        # 複雑度別キーワード
        keywords = {
            TaskComplexity.SIMPLE: [
                "show",
                "list",
                "check",
                "get",
                "view",
                "see",
                "確認",
                "表示",
            ],
            TaskComplexity.STANDARD: [
                "edit",
                "fix",
                "change",
                "update",
                "add",
                "編集",
                "修正",
                "変更",
            ],
            TaskComplexity.COMPLEX: [
                "implement",
                "build",
                "create",
                "design",
                "setup",
                "実装",
                "構築",
                "設計",
            ],
            TaskComplexity.CRITICAL: [
                "analyze",
                "evaluate",
                "strategy",
                "research",
                "分析",
                "戦略",
                "研究",
            ],
        }

        for complexity, keyword_list in keywords.items():
            keyword_count = sum(words.count(keyword) for keyword in keyword_list)
            density = keyword_count / word_count
            scores[complexity] += density * 0.5

        return scores

    def _determine_execution_method(
        self, complexity: TaskComplexity, task_description: str, context: Dict[str, Any]
    ) -> ExecutionMethod:
        """実行手法決定"""
        # 複雑度ベースの基本マッピング
        method_map = {
            TaskComplexity.SIMPLE: ExecutionMethod.DIRECT,
            TaskComplexity.STANDARD: ExecutionMethod.PLANNED,
            TaskComplexity.COMPLEX: ExecutionMethod.AI_COLLABORATION,
            TaskComplexity.CRITICAL: ExecutionMethod.FULL_COLLABORATION,
        }

        return method_map[complexity]

    def _determine_thinking_level(self, complexity: TaskComplexity) -> ThinkingLevel:
        """思考レベル決定"""
        thinking_map = {
            TaskComplexity.SIMPLE: ThinkingLevel.NONE,  # LEVEL 1: thinking不要
            TaskComplexity.STANDARD: ThinkingLevel.STANDARD,  # LEVEL 2: <thinking>
            TaskComplexity.COMPLEX: ThinkingLevel.ULTRATHINK,  # LEVEL 3: ultrathink
            TaskComplexity.CRITICAL: ThinkingLevel.MAX_ULTRATHINK,  # LEVEL 4: max ultrathink
        }

        return thinking_map[complexity]

    def _get_required_files(self, complexity: TaskComplexity) -> List[str]:
        """複雑度ベースの必要ファイル一覧"""
        base_files = ["./CLAUDE.md", "./.claude/claude.md", ".cursor/rules/globals.mdc"]

        if complexity == TaskComplexity.SIMPLE:
            return base_files
        elif complexity == TaskComplexity.STANDARD:
            return base_files + ["docs/", "runtime/logs/"]
        elif complexity == TaskComplexity.COMPLEX:
            return base_files + ["docs/", "runtime/", "src/", "scripts/"]
        else:  # CRITICAL
            return base_files + [
                "docs/",
                "runtime/",
                "src/",
                "scripts/",
                "tests/",
                "config/",
            ]

    def _generate_reasoning(
        self,
        complexity: TaskComplexity,
        scores: Dict[TaskComplexity, float],
        task_description: str,
    ) -> str:
        """推論理由生成"""
        top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

        reasoning_parts = [
            f"Primary classification: {complexity.value} (score: {scores[complexity]:.2f})"
        ]

        if top_scores[1][1] > 0.1:
            reasoning_parts.append(
                f"Secondary consideration: {top_scores[1][0].value} (score: {top_scores[1][1]:.2f})"
            )

        # 特徴的要素の説明
        if "read" in task_description.lower() or "show" in task_description.lower():
            reasoning_parts.append("Reason: Information retrieval task")
        elif (
            "implement" in task_description.lower()
            or "build" in task_description.lower()
        ):
            reasoning_parts.append("Reason: Implementation task requiring planning")
        elif (
            "analyze" in task_description.lower()
            or "evaluate" in task_description.lower()
        ):
            reasoning_parts.append("Reason: Analysis task requiring expertise")

        return " | ".join(reasoning_parts)

    def _estimate_time(self, complexity: TaskComplexity, task_description: str) -> int:
        """時間見積もり（分）"""
        base_times = {
            TaskComplexity.SIMPLE: 5,
            TaskComplexity.STANDARD: 15,
            TaskComplexity.COMPLEX: 60,
            TaskComplexity.CRITICAL: 180,
        }

        base_time = base_times[complexity]

        # 修正要因
        if "quick" in task_description.lower() or "simple" in task_description.lower():
            base_time = int(base_time * 0.7)
        elif (
            "detailed" in task_description.lower()
            or "comprehensive" in task_description.lower()
        ):
            base_time = int(base_time * 1.5)

        return base_time

    def _identify_required_tools(self, task_description: str) -> List[str]:
        """必要ツール特定"""
        tools = []

        tool_patterns = {
            "git": ["git", "repository", "commit", "push", "リポジトリ"],
            "npm": ["npm", "node", "package", "install"],
            "python": ["python", "pip", "py", "script"],
            "make": ["make", "makefile", "build"],
            "docker": ["docker", "container", "image"],
            "editor": ["edit", "modify", "change", "編集", "修正"],
            "search": ["search", "find", "grep", "検索"],
            "ai_org": ["analyze", "evaluate", "strategy", "分析", "戦略"],
        }

        for tool, patterns in tool_patterns.items():
            if any(pattern in task_description.lower() for pattern in patterns):
                tools.append(tool)

        return tools

    def _assess_risk_level(
        self, complexity: TaskComplexity, task_description: str
    ) -> str:
        """リスクレベル評価"""
        risk_keywords = {
            "high": ["delete", "remove", "destroy", "force", "reset", "削除", "強制"],
            "medium": ["modify", "change", "update", "merge", "修正", "変更"],
            "low": ["read", "show", "list", "check", "表示", "確認"],
        }

        for risk_level, keywords in risk_keywords.items():
            if any(keyword in task_description.lower() for keyword in keywords):
                return risk_level

        # 複雑度ベースのデフォルト
        complexity_risk = {
            TaskComplexity.SIMPLE: "low",
            TaskComplexity.STANDARD: "low",
            TaskComplexity.COMPLEX: "medium",
            TaskComplexity.CRITICAL: "high",
        }

        return complexity_risk[complexity]

    def get_execution_recommendation(
        self, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """実行推奨事項取得"""
        classification = self.classify_task(task_description, context)

        recommendations = {
            ExecutionMethod.DIRECT: [
                "Proceed with direct execution (no thinking required)",
                "Use standard tools and commands",
                "Complete task immediately",
            ],
            ExecutionMethod.PLANNED: [
                "Use <thinking> tag for planning",
                "Break down into manageable steps",
                "Use TodoWrite tool for tracking",
            ],
            ExecutionMethod.AI_COLLABORATION: [
                "Use <thinking> tag with ultrathink approach",
                "Engage AI organization for consultation",
                "Use collaborative decision making",
                "Consider multiple perspectives",
            ],
            ExecutionMethod.FULL_COLLABORATION: [
                "Use <thinking> tag with maximum ultrathink depth",
                "Full AI organization collaboration required",
                "User confirmation before major changes",
                "Comprehensive risk assessment",
            ],
        }

        return {
            "classification": {
                "complexity": classification.complexity.value,
                "execution_method": classification.execution_method.value,
                "confidence": classification.confidence,
                "reasoning": classification.reasoning,
            },
            "execution_plan": {
                "estimated_time_minutes": classification.estimated_time,
                "required_tools": classification.required_tools,
                "risk_level": classification.risk_level,
                "recommendations": recommendations[classification.execution_method],
            },
            "efficiency_notes": [
                f"Task complexity: {classification.complexity.value}",
                f"Thinking level: {classification.thinking_level.value}",
                f"Recommended method: {classification.execution_method.value}",
                f"AI collaboration: {'Yes' if classification.ai_collaboration_needed else 'No'}",
                f"Estimated time: {classification.estimated_time} minutes",
                f"Risk level: {classification.risk_level}",
            ],
        }


def main():
    """メイン実行（テスト用）"""
    classifier = TaskComplexityClassifier()

    test_tasks = [
        "Show me the current git status",
        "Edit the README file to add installation instructions",
        "Implement a new authentication system with JWT tokens",
        "Analyze our system architecture and recommend critical improvements",
        "List all Python files in the project",
        "Debug the failing integration tests and fix issues",
        "Research and evaluate different database solutions for scalability",
    ]

    print("🧠 Task Complexity Classification Test")
    print("=" * 60)

    for i, task in enumerate(test_tasks, 1):
        print(f"\n📝 Test {i}: {task}")
        print("-" * 50)

        recommendation = classifier.get_execution_recommendation(task)
        classification = recommendation["classification"]
        execution_plan = recommendation["execution_plan"]

        print(f"🏷️  Complexity: {classification['complexity']}")
        print(f"🧠  Thinking: {recommendation['efficiency_notes'][1].split(': ')[1]}")
        print(f"⚙️  Method: {classification['execution_method']}")
        print(f"🤝 AI Collab: {recommendation['efficiency_notes'][3].split(': ')[1]}")
        print(f"🎯 Confidence: {classification['confidence']:.2f}")
        print(f"⏱️  Time: {execution_plan['estimated_time_minutes']} minutes")
        print(
            f"🛠️  Tools: {', '.join(execution_plan['required_tools']) if execution_plan['required_tools'] else 'None'}"
        )
        print(f"⚠️  Risk: {execution_plan['risk_level']}")
        print(f"💭 Reasoning: {classification['reasoning']}")


if __name__ == "__main__":
    main()
