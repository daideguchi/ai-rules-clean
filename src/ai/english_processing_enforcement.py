#!/usr/bin/env python3
"""
🔤 English Processing Enforcement System - 技術処理英語強制システム
==================================================================
技術的処理を英語で強制実行するシステム
{{mistake_count}}回ミス防止・CLAUDE.mdルール遵守の一環として実装
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ProcessingLanguage(Enum):
    JAPANESE = "japanese"
    ENGLISH = "english"
    MIXED = "mixed"


class ProcessingType(Enum):
    DECLARATION = "declaration"  # 宣言（日本語）
    TECHNICAL = "technical"  # 技術処理（英語）
    REPORTING = "reporting"  # 報告（日本語）
    MIXED_CONTEXT = "mixed_context"


@dataclass
class LanguageRule:
    """言語使用ルール"""

    processing_type: ProcessingType
    required_language: ProcessingLanguage
    description: str
    patterns: List[str] = field(default_factory=list)
    enforcement_level: str = "mandatory"  # mandatory, recommended, optional
    violation_penalty: float = 1.0


@dataclass
class ProcessingContext:
    """処理コンテキスト"""

    content: str
    detected_language: ProcessingLanguage
    expected_language: ProcessingLanguage
    processing_type: ProcessingType
    confidence_score: float
    violations: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)


class EnglishProcessingEnforcement:
    """英語処理強制システム"""

    def __init__(self, project_root: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_root = Path(project_root)
        self.enforcement_log = (
            self.project_root / "runtime" / "logs" / "english_enforcement.log"
        )
        self.violation_archive = (
            self.project_root / "runtime" / "violations" / "language_violations.json"
        )

        # ディレクトリ作成
        self.enforcement_log.parent.mkdir(parents=True, exist_ok=True)
        self.violation_archive.parent.mkdir(parents=True, exist_ok=True)

        # 言語使用ルールの定義
        self.language_rules = self._define_language_rules()

        # 技術用語辞書（日本語→英語）
        self.technical_dictionary = self._load_technical_dictionary()

        # 言語検出パターン
        self.language_patterns = self._define_language_patterns()

        # 違反記録
        self.violation_history = self._load_violation_history()

    def _define_language_rules(self) -> List[LanguageRule]:
        """言語使用ルールの定義"""
        return [
            LanguageRule(
                processing_type=ProcessingType.DECLARATION,
                required_language=ProcessingLanguage.JAPANESE,
                description="宣言部分は日本語で記述（## 🎯 これから行うこと）",
                patterns=[r"##\s*🎯\s*これから行うこと", r"宣言", r"目標"],
                enforcement_level="mandatory",
                violation_penalty=0.8,
            ),
            LanguageRule(
                processing_type=ProcessingType.TECHNICAL,
                required_language=ProcessingLanguage.ENGLISH,
                description="技術的処理は英語で実行（Technical implementation）",
                patterns=[
                    r"def\s+\w+",
                    r"class\s+\w+",
                    r"import\s+\w+",
                    r"from\s+\w+",
                    r"function\s+\w+",
                    r"var\s+\w+",
                    r"const\s+\w+",
                    r"let\s+\w+",
                    r"system\s+\w+",
                    r"process\s+\w+",
                    r"execute\s+\w+",
                    r"implement\s+\w+",
                    r"database",
                    r"api",
                    r"server",
                    r"client",
                    r"network",
                    r"security",
                    r"algorithm",
                    r"data\s+structure",
                    r"performance",
                    r"optimization",
                ],
                enforcement_level="mandatory",
                violation_penalty=1.0,
            ),
            LanguageRule(
                processing_type=ProcessingType.REPORTING,
                required_language=ProcessingLanguage.JAPANESE,
                description="報告部分は日本語で記述（## ✅ 完遂報告）",
                patterns=[r"##\s*✅\s*完遂報告", r"報告", r"結果", r"完了"],
                enforcement_level="mandatory",
                violation_penalty=0.8,
            ),
        ]

    def _load_technical_dictionary(self) -> Dict[str, str]:
        """技術用語辞書の読み込み"""
        return {
            # システム関連
            "システム": "system",
            "処理": "processing",
            "実装": "implementation",
            "開発": "development",
            "設計": "design",
            "構築": "construction",
            "作成": "creation",
            "生成": "generation",
            "変換": "conversion",
            "変更": "modification",
            "修正": "correction",
            "改善": "improvement",
            "最適化": "optimization",
            "統合": "integration",
            "連携": "coordination",
            "管理": "management",
            "制御": "control",
            "監視": "monitoring",
            "検証": "verification",
            "テスト": "testing",
            "評価": "evaluation",
            "分析": "analysis",
            "解析": "parsing",
            "検索": "search",
            "抽出": "extraction",
            "フィルタ": "filtering",
            "ソート": "sorting",
            "並び替え": "sorting",
            # データ関連
            "データ": "data",
            "情報": "information",
            "データベース": "database",
            "ファイル": "file",
            "ディレクトリ": "directory",
            "フォルダ": "folder",
            "パス": "path",
            "設定": "configuration",
            "パラメータ": "parameter",
            "引数": "argument",
            "戻り値": "return value",
            "結果": "result",
            "出力": "output",
            "入力": "input",
            # プログラミング関連
            "関数": "function",
            "メソッド": "method",
            "クラス": "class",
            "オブジェクト": "object",
            "インスタンス": "instance",
            "変数": "variable",
            "定数": "constant",
            "配列": "array",
            "リスト": "list",
            "辞書": "dictionary",
            "ハッシュマップ": "hash map",
            "ループ": "loop",
            "条件分岐": "conditional",
            "例外": "exception",
            "エラー": "error",
            "バグ": "bug",
            "デバッグ": "debug",
            "コード": "code",
            "プログラム": "program",
            "スクリプト": "script",
            "ライブラリ": "library",
            "モジュール": "module",
            "パッケージ": "package",
            "フレームワーク": "framework",
            "ツール": "tool",
            "ユーティリティ": "utility",
            # インフラ関連
            "サーバー": "server",
            "クライアント": "client",
            "ネットワーク": "network",
            "セキュリティ": "security",
            "認証": "authentication",
            "認可": "authorization",
            "暗号化": "encryption",
            "プロトコル": "protocol",
            "インターフェース": "interface",
            "API": "API",
            "エンドポイント": "endpoint",
            "リクエスト": "request",
            "レスポンス": "response",
            "ステータス": "status",
            "ログ": "log",
            "ログファイル": "log file",
            "バックアップ": "backup",
            "復旧": "recovery",
            "災害復旧": "disaster recovery",
        }

    def _define_language_patterns(self) -> Dict[str, List[str]]:
        """言語検出パターンの定義"""
        return {
            "japanese": [
                r"[\u3040-\u309F]",  # ひらがな
                r"[\u30A0-\u30FF]",  # カタカナ
                r"[\u4E00-\u9FAF]",  # 漢字
                r"です",
                r"である",
                r"します",
                r"している",
                r"した",
                r"する",
                r"ます",
                r"ました",
                r"ません",
                r"でした",
                r"だった",
                r"だろう",
                r"として",
                r"による",
                r"について",
                r"において",
                r"により",
                r"を",
                r"が",
                r"に",
                r"で",
                r"から",
                r"まで",
                r"の",
                r"と",
                r"は",
            ],
            "english": [
                r"\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by)\b",
                r"\b(is|are|was|were|been|be|have|has|had|do|does|did)\b",
                r"\b(will|would|should|could|can|may|might|must|shall)\b",
                r"\b(this|that|these|those|here|there|where|when|how|why)\b",
                r"\b(function|class|method|variable|parameter|return|if|else|while|for)\b",
                r"\b(system|process|data|file|directory|configuration|implementation)\b",
            ],
        }

    def detect_language(self, content: str) -> Tuple[ProcessingLanguage, float]:
        """言語検出"""
        japanese_matches = 0
        english_matches = 0

        # 日本語パターンマッチング
        for pattern in self.language_patterns["japanese"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            japanese_matches += len(matches)

        # 英語パターンマッチング
        for pattern in self.language_patterns["english"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            english_matches += len(matches)

        total_matches = japanese_matches + english_matches

        if total_matches == 0:
            return ProcessingLanguage.MIXED, 0.0

        japanese_ratio = japanese_matches / total_matches
        english_ratio = english_matches / total_matches

        if japanese_ratio > 0.7:
            return ProcessingLanguage.JAPANESE, japanese_ratio
        elif english_ratio > 0.7:
            return ProcessingLanguage.ENGLISH, english_ratio
        else:
            return ProcessingLanguage.MIXED, max(japanese_ratio, english_ratio)

    def detect_processing_type(self, content: str) -> ProcessingType:
        """処理タイプの検出"""
        content.lower()

        # 宣言部分の検出
        if (
            re.search(r"##\s*🎯\s*これから行うこと", content)
            or "宣言" in content
            or "目標" in content
        ):
            return ProcessingType.DECLARATION

        # 報告部分の検出
        if (
            re.search(r"##\s*✅\s*完遂報告", content)
            or "報告" in content
            or "結果" in content
        ):
            return ProcessingType.REPORTING

        # 技術処理の検出
        technical_indicators = [
            r"def\s+\w+",
            r"class\s+\w+",
            r"import\s+\w+",
            r"from\s+\w+",
            r"function",
            r"method",
            r"implementation",
            r"system",
            r"process",
            r"database",
            r"api",
            r"server",
            r"algorithm",
            r"data structure",
        ]

        for pattern in technical_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                return ProcessingType.TECHNICAL

        return ProcessingType.MIXED_CONTEXT

    def enforce_language_rules(self, content: str) -> ProcessingContext:
        """言語ルールの強制適用"""
        # 言語とタイプの検出
        detected_language, confidence = self.detect_language(content)
        processing_type = self.detect_processing_type(content)

        # 適用すべきルールの決定
        applicable_rule = None
        for rule in self.language_rules:
            if rule.processing_type == processing_type:
                applicable_rule = rule
                break

        if not applicable_rule:
            # デフォルトルール：技術的内容は英語
            if self._is_technical_content(content):
                applicable_rule = LanguageRule(
                    processing_type=ProcessingType.TECHNICAL,
                    required_language=ProcessingLanguage.ENGLISH,
                    description="Technical content should be in English",
                    enforcement_level="recommended",
                    violation_penalty=0.5,
                )
            else:
                # ルールなし、現状維持
                return ProcessingContext(
                    content=content,
                    detected_language=detected_language,
                    expected_language=detected_language,
                    processing_type=processing_type,
                    confidence_score=confidence,
                )

        # 違反チェック
        violations = []
        corrections = []

        if detected_language != applicable_rule.required_language:
            violations.append(
                f"Language mismatch: Expected {applicable_rule.required_language.value}, got {detected_language.value}"
            )

            # 修正提案生成
            if applicable_rule.required_language == ProcessingLanguage.ENGLISH:
                corrections.extend(self._generate_english_corrections(content))
            elif applicable_rule.required_language == ProcessingLanguage.JAPANESE:
                corrections.extend(self._generate_japanese_corrections(content))

        # 違反を記録
        if violations:
            self._record_violation(content, violations, applicable_rule)

        return ProcessingContext(
            content=content,
            detected_language=detected_language,
            expected_language=applicable_rule.required_language,
            processing_type=processing_type,
            confidence_score=confidence,
            violations=violations,
            corrections=corrections,
        )

    def _is_technical_content(self, content: str) -> bool:
        """技術的内容の判定"""
        technical_keywords = [
            "function",
            "class",
            "method",
            "variable",
            "parameter",
            "system",
            "process",
            "algorithm",
            "data",
            "database",
            "api",
            "server",
            "client",
            "network",
            "security",
            "implementation",
            "development",
            "programming",
            "code",
            "def ",
            "class ",
            "import ",
            "from ",
            "return ",
            "if ",
            "else ",
            "while ",
            "for ",
            "try ",
            "except ",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in technical_keywords)

    def _generate_english_corrections(self, content: str) -> List[str]:
        """英語修正提案の生成"""
        corrections = []

        # 技術用語の日本語→英語変換
        for japanese_term, english_term in self.technical_dictionary.items():
            if japanese_term in content:
                corrections.append(f"Replace '{japanese_term}' with '{english_term}'")

        # 一般的な修正提案
        corrections.extend(
            [
                "Use English for technical descriptions",
                "Use English variable names and function names",
                "Use English comments in code",
                "Use English for system messages and log outputs",
            ]
        )

        return corrections

    def _generate_japanese_corrections(self, content: str) -> List[str]:
        """日本語修正提案の生成"""
        corrections = []

        # 英語→日本語変換（逆引き）
        for japanese_term, english_term in self.technical_dictionary.items():
            if english_term in content.lower():
                corrections.append(f"Replace '{english_term}' with '{japanese_term}'")

        # 一般的な修正提案
        corrections.extend(
            [
                "Use Japanese for declarations and explanations",
                "Use Japanese for user-facing messages",
                "Use Japanese for reports and summaries",
            ]
        )

        return corrections

    def _record_violation(
        self, content: str, violations: List[str], rule: LanguageRule
    ):
        """違反記録"""
        violation_record = {
            "timestamp": datetime.now().isoformat(),
            "content": content[:200] + "..." if len(content) > 200 else content,
            "violations": violations,
            "rule": {
                "processing_type": rule.processing_type.value,
                "required_language": rule.required_language.value,
                "description": rule.description,
                "enforcement_level": rule.enforcement_level,
                "violation_penalty": rule.violation_penalty,
            },
        }

        self.violation_history.append(violation_record)
        self._save_violation_history()

        # ログ出力
        self._log(f"Language violation: {', '.join(violations)}")

    def _load_violation_history(self) -> List[Dict[str, Any]]:
        """違反履歴の読み込み"""
        try:
            if self.violation_archive.exists():
                with open(self.violation_archive, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_violation_history(self):
        """違反履歴の保存"""
        try:
            with open(self.violation_archive, "w", encoding="utf-8") as f:
                json.dump(self.violation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"Failed to save violation history: {e}")

    def generate_enforcement_report(self) -> Dict[str, Any]:
        """強制実行レポートの生成"""
        total_violations = len(self.violation_history)

        if total_violations == 0:
            return {
                "status": "compliant",
                "total_violations": 0,
                "compliance_rate": 1.0,
                "recommendations": [],
                "enforcement_summary": self._generate_enforcement_summary(),
            }

        # 違反タイプ別集計
        violation_types = {}
        for violation in self.violation_history:
            rule_type = violation["rule"]["processing_type"]
            if rule_type not in violation_types:
                violation_types[rule_type] = 0
            violation_types[rule_type] += 1

        # 最近の違反（24時間以内）
        recent_violations = []
        now = datetime.now()
        for violation in self.violation_history:
            try:
                violation_time = datetime.fromisoformat(violation["timestamp"])
                if (now - violation_time).days == 0:
                    recent_violations.append(violation)
            except Exception:
                pass

        # 推奨事項生成
        recommendations = []
        if violation_types.get("technical", 0) > 0:
            recommendations.append("Use English for technical implementations")
        if violation_types.get("declaration", 0) > 0:
            recommendations.append(
                "Use Japanese for declarations (## 🎯 これから行うこと)"
            )
        if violation_types.get("reporting", 0) > 0:
            recommendations.append("Use Japanese for reports (## ✅ 完遂報告)")

        return {
            "status": "violations_detected",
            "total_violations": total_violations,
            "recent_violations": len(recent_violations),
            "violation_types": violation_types,
            "compliance_rate": max(0.0, 1.0 - (total_violations * 0.1)),
            "recommendations": recommendations,
            "enforcement_summary": self._generate_enforcement_summary(),
        }

    def _generate_enforcement_summary(self) -> str:
        """強制実行サマリーの生成"""
        total_violations = len(self.violation_history)

        if total_violations == 0:
            return "🎉 完全コンプライアンス：言語使用ルール違反なし"

        return f"⚠️ 言語使用ルール違反: {total_violations}件検出 - 改善が必要"

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"
        print(log_entry)

        try:
            with open(self.enforcement_log, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass


# デモンストレーション関数
def demo_english_processing_enforcement():
    """英語処理強制システムのデモンストレーション"""
    print("=== 英語処理強制システム デモ ===")

    enforcer = EnglishProcessingEnforcement()

    # テストケース
    test_cases = [
        {
            "title": "日本語宣言（適切）",
            "content": "## 🎯 これから行うこと\n\nデータベースシステムを改善します。",
        },
        {
            "title": "英語技術実装（適切）",
            "content": "def create_database_connection():\n    return Database.connect()",
        },
        {
            "title": "日本語技術実装（違反）",
            "content": "データベース接続を作成する関数を実装します。",
        },
        {
            "title": "英語宣言（違反）",
            "content": "## Goal: Implement database system\n\nWe will create a new database system.",
        },
        {
            "title": "日本語報告（適切）",
            "content": "## ✅ 完遂報告\n\nシステムの実装が完了しました。",
        },
    ]

    for test_case in test_cases:
        print(f"\n--- {test_case['title']} ---")
        context = enforcer.enforce_language_rules(test_case["content"])

        print(f"検出言語: {context.detected_language.value}")
        print(f"処理タイプ: {context.processing_type.value}")
        print(f"期待言語: {context.expected_language.value}")
        print(f"信頼度: {context.confidence_score:.2f}")

        if context.violations:
            print(f"違反: {', '.join(context.violations)}")
        else:
            print("✅ 違反なし")

        if context.corrections:
            print(f"修正提案: {context.corrections[0]}")

    # 強制実行レポート
    print("\n--- 強制実行レポート ---")
    report = enforcer.generate_enforcement_report()
    print(f"ステータス: {report['status']}")
    print(f"総違反数: {report['total_violations']}")
    print(f"コンプライアンス率: {report['compliance_rate']:.2f}")
    print(f"サマリー: {report['enforcement_summary']}")

    if report["recommendations"]:
        print("推奨事項:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")


if __name__ == "__main__":
    demo_english_processing_enforcement()
