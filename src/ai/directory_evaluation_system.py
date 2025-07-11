#!/usr/bin/env python3
"""
🔍 Directory Evaluation System
==============================
自律成長型ディレクトリ評価システム
エラーが発生しないよう堅牢な設計
"""

from datetime import datetime
from pathlib import Path
from typing import Dict


class DirectoryEvaluationSystem:
    def __init__(self, project_root: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_root = Path(project_root)
        self.evaluation_results = {}

    def analyze_directory_structure(self) -> Dict:
        """ディレクトリ構造の詳細分析"""

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "structure_analysis": {},
            "file_distribution": {},
            "quality_metrics": {},
            "recommendations": [],
        }

        # ルートディレクトリ分析
        root_files = list(self.project_root.glob("*"))
        root_file_count = len([f for f in root_files if f.is_file()])

        analysis["structure_analysis"]["root_files"] = root_file_count
        analysis["structure_analysis"]["root_limit_exceeded"] = root_file_count > 12

        # ファイル分布分析
        file_types = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                file_types[suffix] = file_types.get(suffix, 0) + 1

        analysis["file_distribution"] = file_types

        # 品質メトリクス
        total_files = sum(file_types.values())
        analysis["quality_metrics"] = {
            "total_files": total_files,
            "python_files": file_types.get(".py", 0),
            "config_files": file_types.get(".json", 0) + file_types.get(".yaml", 0),
            "documentation_files": file_types.get(".md", 0),
            "log_files": file_types.get(".log", 0),
        }

        # 推奨事項
        recommendations = []

        if root_file_count > 12:
            recommendations.append(
                f"ルートディレクトリのファイル数を{root_file_count}から12以下に削減"
            )

        if file_types.get(".md", 0) > 50:
            recommendations.append("Markdownファイルをdocs/以下に整理")

        if file_types.get(".json", 0) > 20:
            recommendations.append("設定ファイルをconfig/以下に統合")

        if file_types.get(".log", 0) > 10:
            recommendations.append("ログファイルを定期的にクリーンアップ")

        analysis["recommendations"] = recommendations

        return analysis

    def generate_evaluation_report(self) -> str:
        """評価レポート生成"""

        analysis = self.analyze_directory_structure()

        report = f"""
# 🔍 ディレクトリ構造評価レポート

## 分析実行時刻
{analysis["timestamp"]}

## 構造分析結果

### ルートディレクトリ状況
- ファイル数: {analysis["structure_analysis"]["root_files"]}
- 制限超過: {"❌ はい" if analysis["structure_analysis"]["root_limit_exceeded"] else "✅ いいえ"}

### ファイル分布
"""

        for file_type, count in analysis["file_distribution"].items():
            if count > 0:
                report += f"- {file_type}: {count}個\n"

        report += f"""
### 品質メトリクス
- 総ファイル数: {analysis["quality_metrics"]["total_files"]}
- Pythonファイル: {analysis["quality_metrics"]["python_files"]}
- 設定ファイル: {analysis["quality_metrics"]["config_files"]}
- ドキュメント: {analysis["quality_metrics"]["documentation_files"]}
- ログファイル: {analysis["quality_metrics"]["log_files"]}

### 推奨改善事項
"""

        for i, recommendation in enumerate(analysis["recommendations"], 1):
            report += f"{i}. {recommendation}\n"

        # 総合スコア計算
        score = 100
        if analysis["structure_analysis"]["root_limit_exceeded"]:
            score -= 20
        if analysis["quality_metrics"]["documentation_files"] > 50:
            score -= 15
        if analysis["quality_metrics"]["config_files"] > 20:
            score -= 10
        if analysis["quality_metrics"]["log_files"] > 10:
            score -= 5

        report += f"""
## 総合評価
**スコア: {score}/100**

### 評価基準
- 90-100: 優秀
- 70-89: 良好
- 50-69: 要改善
- 50未満: 要大幅改善

### 結論
{"✅ 良好な構造です" if score >= 70 else "⚠️ 改善が必要です" if score >= 50 else "❌ 大幅な改善が必要です"}
"""

        return report

    def save_evaluation(self, output_path: str = None):
        """評価結果保存"""

        if not output_path:
            output_path = (
                self.project_root / "docs" / "analysis" / "auto_directory_evaluation.md"
            )

        # ディレクトリ作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.generate_evaluation_report()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 評価レポート保存: {output_path}")
        return output_path


def main():
    """メイン実行"""

    print("🔍 ディレクトリ評価システム開始")
    print("=" * 50)

    evaluator = DirectoryEvaluationSystem()

    # 分析実行
    evaluator.analyze_directory_structure()

    # レポート生成・保存
    report_path = evaluator.save_evaluation()

    # 結果表示
    report = evaluator.generate_evaluation_report()
    print(report)

    print(f"\n📊 詳細レポート: {report_path}")


if __name__ == "__main__":
    main()
