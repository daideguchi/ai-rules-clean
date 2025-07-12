#!/usr/bin/env python3
"""
🎯 Conversation-Exit TODO Protocol - 会話終了時TODO明示プロトコル
================================================================
会話終了時に明確なTODOを抽出・整理・提示するシステム
継続性確保と{{mistake_count}}回ミス防止のための重要なコンポーネント
"""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TodoPriority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class ExtractedTodo:
    """抽出されたTODO項目"""

    id: str
    content: str
    priority: TodoPriority
    status: TodoStatus
    context: str
    source: str  # conversation, instruction, etc.
    estimated_effort: str  # minutes, hours, days
    dependencies: List[str] = field(default_factory=list)
    technical_requirements: List[str] = field(default_factory=list)
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence_score: float = 0.8


@dataclass
class ConversationContext:
    """会話コンテキスト"""

    conversation_id: str
    start_time: str
    end_time: Optional[str]
    total_messages: int
    key_topics: List[str]
    technical_domains: List[str]
    completion_status: str
    next_session_preparation: Dict[str, Any] = field(default_factory=dict)


class ConversationExitTodoProtocol:
    """会話終了時TODO明示プロトコル"""

    def __init__(self, project_root: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_root = Path(project_root)
        self.todo_archive_dir = self.project_root / "runtime" / "todo_archive"
        self.active_todos_file = self.project_root / "runtime" / "active_todos.json"
        self.conversation_history_dir = (
            self.project_root / "runtime" / "conversation_logs"
        )

        # ディレクトリ作成
        self.todo_archive_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_history_dir.mkdir(parents=True, exist_ok=True)

        # TODO抽出パターン
        self.todo_patterns = [
            r"(次に|今度|後で|後から|将来|次回)\s*(.{1,100}?)(?:[。\n]|$)",
            r"(TODO|ToDo|todo|やること|タスク|課題)[:：]?\s*(.{1,100}?)(?:[。\n]|$)",
            r"(実装|修正|追加|改善|対応|検討|調査|確認)\s*(する|すべき|が必要|を行う)\s*(.{1,100}?)(?:[。\n]|$)",
            r"(残って|未完了|未実装|未対応|未解決)\s*(.{1,100}?)(?:[。\n]|$)",
            r"(継続|引き続き|続いて|続けて)\s*(.{1,100}?)(?:[。\n]|$)",
            r"まだ\s*(.{1,100}?)(?:[。\n]|$)",
            r"(後で|あとで|今度|次回)\s*(.{1,100}?)(?:[。\n]|$)",
        ]

        # 技術ドメイン識別パターン
        self.technical_domains = {
            "frontend": [
                "react",
                "vue",
                "css",
                "html",
                "javascript",
                "typescript",
                "ui",
                "ux",
            ],
            "backend": [
                "api",
                "server",
                "database",
                "sql",
                "python",
                "node",
                "express",
            ],
            "infrastructure": [
                "docker",
                "kubernetes",
                "aws",
                "cloud",
                "deployment",
                "ci/cd",
            ],
            "ai_ml": [
                "machine learning",
                "ai",
                "neural",
                "model",
                "training",
                "inference",
            ],
            "security": ["security", "auth", "encryption", "vulnerability", "audit"],
            "testing": ["test", "testing", "qa", "unit test", "integration test"],
        }

        # アクティブTODOの読み込み
        self.active_todos = self._load_active_todos()

    def extract_todos_from_conversation(
        self, conversation_text: str, conversation_context: ConversationContext
    ) -> List[ExtractedTodo]:
        """会話からTODOを抽出"""
        extracted_todos = []

        # テキストを文単位で分割
        sentences = re.split(r"[。\n]", conversation_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 各パターンでマッチング
            for pattern in self.todo_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # タプルの場合、適切な部分を抽出
                        content = self._extract_content_from_match(match)
                    else:
                        content = match

                    if content and len(content.strip()) > 10:  # 最小長チェック
                        todo = self._create_todo_from_content(
                            content, sentence, conversation_context
                        )
                        if todo:
                            extracted_todos.append(todo)

        # 重複除去
        unique_todos = self._deduplicate_todos(extracted_todos)

        return unique_todos

    def _extract_content_from_match(self, match: tuple) -> str:
        """マッチしたタプルからコンテンツを抽出"""
        if len(match) >= 2:
            return match[1].strip()
        elif len(match) == 1:
            return match[0].strip()
        return ""

    def _create_todo_from_content(
        self, content: str, context: str, conversation_context: ConversationContext
    ) -> Optional[ExtractedTodo]:
        """コンテンツからTODOオブジェクトを作成"""
        # 無効なコンテンツをフィルタリング
        if len(content.strip()) < 10:
            return None

        # 技術要件を抽出
        technical_requirements = self._extract_technical_requirements(content)

        # 優先度を推定
        priority = self._estimate_priority(content, context)

        # 作業量を推定
        estimated_effort = self._estimate_effort(content)

        # 依存関係を推定
        dependencies = self._extract_dependencies(content)

        # 信頼度スコアを計算
        confidence_score = self._calculate_confidence_score(content, context)

        return ExtractedTodo(
            id=f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(content) % 10000}",
            content=content.strip(),
            priority=priority,
            status=TodoStatus.PENDING,
            context=context,
            source="conversation",
            estimated_effort=estimated_effort,
            dependencies=dependencies,
            technical_requirements=technical_requirements,
            confidence_score=confidence_score,
        )

    def _extract_technical_requirements(self, content: str) -> List[str]:
        """技術要件を抽出"""
        requirements = []
        content_lower = content.lower()

        for domain, keywords in self.technical_domains.items():
            if any(keyword in content_lower for keyword in keywords):
                requirements.append(domain)

        return requirements

    def _estimate_priority(self, content: str, context: str) -> TodoPriority:
        """優先度を推定"""
        content_lower = content.lower()
        context_lower = context.lower()

        # 緊急キーワード
        urgent_keywords = [
            "急",
            "緊急",
            "urgent",
            "critical",
            "asap",
            "今すぐ",
            "すぐに",
        ]
        high_keywords = ["重要", "必須", "important", "must", "should", "必要"]
        low_keywords = ["いずれ", "eventually", "sometime", "maybe", "できれば"]

        if any(
            keyword in content_lower or keyword in context_lower
            for keyword in urgent_keywords
        ):
            return TodoPriority.URGENT
        elif any(
            keyword in content_lower or keyword in context_lower
            for keyword in high_keywords
        ):
            return TodoPriority.HIGH
        elif any(
            keyword in content_lower or keyword in context_lower
            for keyword in low_keywords
        ):
            return TodoPriority.LOW
        else:
            return TodoPriority.MEDIUM

    def _estimate_effort(self, content: str) -> str:
        """作業量を推定"""
        content_lower = content.lower()

        # 大規模タスクのキーワード
        large_keywords = [
            "システム",
            "system",
            "設計",
            "design",
            "全体",
            "entire",
            "完全",
            "complete",
        ]
        small_keywords = [
            "修正",
            "fix",
            "調整",
            "adjust",
            "微調整",
            "tweak",
            "バグ",
            "bug",
        ]

        if any(keyword in content_lower for keyword in large_keywords):
            return "days"
        elif any(keyword in content_lower for keyword in small_keywords):
            return "minutes"
        else:
            return "hours"

    def _extract_dependencies(self, content: str) -> List[str]:
        """依存関係を抽出"""
        dependencies = []
        content_lower = content.lower()

        # 依存関係のキーワードパターン
        if "前に" in content_lower or "before" in content_lower:
            dependencies.append("prerequisite_required")
        if "後に" in content_lower or "after" in content_lower:
            dependencies.append("follow_up_task")
        if "と一緒に" in content_lower or "with" in content_lower:
            dependencies.append("parallel_task")

        return dependencies

    def _calculate_confidence_score(self, content: str, context: str) -> float:
        """信頼度スコアを計算"""
        base_score = 0.5

        # 具体性チェック
        if len(content.split()) >= 5:
            base_score += 0.2

        # 技術的具体性
        if any(
            domain in content.lower()
            for domain_keywords in self.technical_domains.values()
            for domain in domain_keywords
        ):
            base_score += 0.2

        # 明確な動詞の存在
        action_verbs = ["実装", "修正", "追加", "削除", "改善", "作成", "構築", "設計"]
        if any(verb in content for verb in action_verbs):
            base_score += 0.1

        return min(base_score, 1.0)

    def _deduplicate_todos(self, todos: List[ExtractedTodo]) -> List[ExtractedTodo]:
        """重複TODOを除去"""
        unique_todos = []
        seen_contents = set()

        for todo in todos:
            # 内容の正規化
            normalized_content = re.sub(r"\s+", " ", todo.content.lower().strip())

            # 類似度チェック（簡易版）
            is_duplicate = False
            for seen_content in seen_contents:
                if self._calculate_similarity(normalized_content, seen_content) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_todos.append(todo)
                seen_contents.add(normalized_content)

        return unique_todos

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """テキスト類似度を計算（簡易版）"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def generate_exit_todo_summary(
        self, conversation_text: str, conversation_context: ConversationContext
    ) -> Dict[str, Any]:
        """会話終了時TODO要約を生成"""
        # TODOを抽出
        extracted_todos = self.extract_todos_from_conversation(
            conversation_text, conversation_context
        )

        # 優先度別に分類
        prioritized_todos = {"urgent": [], "high": [], "medium": [], "low": []}

        for todo in extracted_todos:
            todo_dict = asdict(todo)
            # Enum値を文字列に変換
            todo_dict["priority"] = todo.priority.value
            todo_dict["status"] = todo.status.value
            prioritized_todos[todo.priority.value].append(todo_dict)

        # 技術ドメイン別に分類
        domain_todos = {}
        for todo in extracted_todos:
            for domain in todo.technical_requirements:
                if domain not in domain_todos:
                    domain_todos[domain] = []
                todo_dict = asdict(todo)
                todo_dict["priority"] = todo.priority.value
                todo_dict["status"] = todo.status.value
                domain_todos[domain].append(todo_dict)

        # 要約レポート生成
        summary = {
            "conversation_id": conversation_context.conversation_id,
            "generated_at": datetime.now().isoformat(),
            "total_todos_extracted": len(extracted_todos),
            "prioritized_todos": prioritized_todos,
            "domain_todos": domain_todos,
            "next_session_recommendations": self._generate_next_session_recommendations(
                extracted_todos
            ),
            "continuity_score": self._calculate_continuity_score(extracted_todos),
            "completion_status": self._assess_completion_status(
                extracted_todos, conversation_context
            ),
            "extracted_todos": [
                {
                    **asdict(todo),
                    "priority": todo.priority.value,
                    "status": todo.status.value,
                }
                for todo in extracted_todos
            ],
        }

        return summary

    def _generate_next_session_recommendations(
        self, todos: List[ExtractedTodo]
    ) -> List[str]:
        """次回セッションの推奨事項を生成"""
        recommendations = []

        # 緊急・高優先度タスクの推奨
        urgent_todos = [todo for todo in todos if todo.priority == TodoPriority.URGENT]
        high_todos = [todo for todo in todos if todo.priority == TodoPriority.HIGH]

        if urgent_todos:
            recommendations.append(f"緊急タスク {len(urgent_todos)} 件を最優先で対応")

        if high_todos:
            recommendations.append(f"高優先度タスク {len(high_todos)} 件の早期着手")

        # 技術ドメイン別推奨
        domain_counts = {}
        for todo in todos:
            for domain in todo.technical_requirements:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        if domain_counts:
            top_domain = max(domain_counts, key=domain_counts.get)
            recommendations.append(
                f"{top_domain} 分野のタスクが多数({domain_counts[top_domain]}件)"
            )

        return recommendations

    def _calculate_continuity_score(self, todos: List[ExtractedTodo]) -> float:
        """継続性スコアを計算"""
        if not todos:
            return 0.0

        # 信頼度スコアの平均
        avg_confidence = sum(todo.confidence_score for todo in todos) / len(todos)

        # 具体性スコア
        concrete_todos = sum(1 for todo in todos if todo.technical_requirements)
        concrete_score = concrete_todos / len(todos)

        # 優先度分散スコア
        priority_counts = {}
        for todo in todos:
            priority_counts[todo.priority] = priority_counts.get(todo.priority, 0) + 1

        priority_score = 0.8 if len(priority_counts) > 1 else 0.5

        return avg_confidence * 0.4 + concrete_score * 0.4 + priority_score * 0.2

    def _assess_completion_status(
        self, todos: List[ExtractedTodo], conversation_context: ConversationContext
    ) -> str:
        """完了状況を評価"""
        if not todos:
            return "完了・継続タスクなし"

        urgent_count = sum(1 for todo in todos if todo.priority == TodoPriority.URGENT)
        high_count = sum(1 for todo in todos if todo.priority == TodoPriority.HIGH)

        if urgent_count > 0:
            return f"緊急タスク残存({urgent_count}件)"
        elif high_count > 2:
            return f"高優先度タスク多数({high_count}件)"
        else:
            return "適切な進捗・継続準備完了"

    def format_exit_todo_display(self, todo_summary: Dict[str, Any]) -> str:
        """会話終了時TODO表示をフォーマット"""
        display_lines = []

        # ヘッダー
        display_lines.append("# 🎯 会話終了時TODO要約")
        display_lines.append("")
        display_lines.append(f"**生成時刻**: {todo_summary['generated_at']}")
        display_lines.append(f"**総TODO数**: {todo_summary['total_todos_extracted']}")
        display_lines.append(
            f"**継続性スコア**: {todo_summary['continuity_score']:.2f}"
        )
        display_lines.append(f"**完了状況**: {todo_summary['completion_status']}")
        display_lines.append("")

        # 優先度別TODO
        priority_labels = {
            "urgent": "🚨 緊急",
            "high": "⚡ 高優先度",
            "medium": "📋 中優先度",
            "low": "📝 低優先度",
        }

        for priority, label in priority_labels.items():
            todos = todo_summary["prioritized_todos"][priority]
            if todos:
                display_lines.append(f"## {label} ({len(todos)}件)")
                for todo in todos:
                    # ExtractedTodoオブジェクトか辞書かを判定
                    if isinstance(todo, dict):
                        content = todo["content"]
                        effort = todo["estimated_effort"]
                        tech_req = todo["technical_requirements"]
                        confidence = todo["confidence_score"]
                    else:
                        content = todo.content
                        effort = todo.estimated_effort
                        tech_req = todo.technical_requirements
                        confidence = todo.confidence_score

                    display_lines.append(f"- **{content}**")
                    display_lines.append(f"  - 作業量: {effort}")
                    if tech_req:
                        display_lines.append(f"  - 技術要件: {', '.join(tech_req)}")
                    display_lines.append(f"  - 信頼度: {confidence:.2f}")
                    display_lines.append("")

        # 次回セッション推奨
        if todo_summary["next_session_recommendations"]:
            display_lines.append("## 📅 次回セッション推奨事項")
            for rec in todo_summary["next_session_recommendations"]:
                display_lines.append(f"- {rec}")
            display_lines.append("")

        # 技術ドメイン別サマリー
        if todo_summary["domain_todos"]:
            display_lines.append("## 🛠️ 技術ドメイン別TODO")
            for domain, todos in todo_summary["domain_todos"].items():
                display_lines.append(f"- **{domain}**: {len(todos)}件")

        return "\n".join(display_lines)

    def save_todo_summary(self, todo_summary: Dict[str, Any]):
        """TODO要約を保存"""
        # アクティブTODOに追加
        for todo_data in todo_summary["extracted_todos"]:
            self.active_todos.append(todo_data)

        # アクティブTODOファイルを更新
        self._save_active_todos()

        # アーカイブにも保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.todo_archive_dir / f"todo_summary_{timestamp}.json"

        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(todo_summary, f, ensure_ascii=False, indent=2)

    def _load_active_todos(self) -> List[Dict[str, Any]]:
        """アクティブTODOを読み込み"""
        try:
            if self.active_todos_file.exists():
                with open(self.active_todos_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_active_todos(self):
        """アクティブTODOを保存"""
        try:
            with open(self.active_todos_file, "w", encoding="utf-8") as f:
                json.dump(self.active_todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"アクティブTODO保存エラー: {e}")


# デモンストレーション関数
def demo_conversation_exit_todo():
    """会話終了時TODOプロトコルのデモンストレーション"""
    print("=== 会話終了時TODOプロトコル デモ ===")

    protocol = ConversationExitTodoProtocol()

    # サンプル会話テキスト
    sample_conversation = """
    ユーザー: データベース設計を改善してください
    Claude: データベース設計を改善しました。次にフロントエンドのUI改修も必要です。
    ユーザー: 認証システムも追加してください
    Claude: 認証システムを実装しました。後でセキュリティ監査を実施する必要があります。
    テストケースの追加も今度行います。
    """

    # 会話コンテキスト
    context = ConversationContext(
        conversation_id="demo_conversation_001",
        start_time=datetime.now().isoformat(),
        end_time=None,
        total_messages=4,
        key_topics=["データベース", "認証", "UI"],
        technical_domains=["backend", "frontend", "security"],
        completion_status="partial",
    )

    # TODO要約生成
    todo_summary = protocol.generate_exit_todo_summary(sample_conversation, context)

    # 表示フォーマット
    formatted_display = protocol.format_exit_todo_display(todo_summary)

    print(formatted_display)

    # 保存
    protocol.save_todo_summary(todo_summary)

    print("\n✅ TODO要約が保存されました")


if __name__ == "__main__":
    demo_conversation_exit_todo()
