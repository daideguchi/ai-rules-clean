#!/usr/bin/env python3
"""
ミスパターン自動更新システム
同じミスの再発を即座に検出し、より強力な防止策を追加
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MISTAKES_DB = PROJECT_ROOT / "src/memory/persistent-learning/mistakes-database.json"


def add_absolute_path_pattern():
    """絶対パス使用ミスのパターンを強化追加"""

    # 現在のミスデータベースを読み込み
    with open(MISTAKES_DB, encoding="utf-8") as f:
        mistakes_db = json.load(f)

    # 新しい強化パターンを追加
    new_pattern = {
        "id": "mistake_079_absolute_path_repetition",
        "type": "絶対パス再使用",
        "pattern": r"/Users/[^/]+/Desktop",
        "severity": "critical",
        "prevention": "相対パス強制 + 自動検出 + 即座修正",
        "trigger_action": "immediate_fix",
        "auto_learned": True,
        "repetition_count": 2,
        "last_occurrence": datetime.now().isoformat(),
        "description": "過去に指摘済みの絶対パス問題を再度犯した",
        "escalated_prevention": [
            "ファイル保存前に絶対パス自動チェック",
            "相対パスへの自動変換",
            "違反時は作業一時停止",
        ],
    }

    # 既存の絶対パスパターンを更新または追加
    existing_pattern = None
    for pattern in mistakes_db["critical_patterns"]:
        if pattern.get("type") == "絶対パス使用":
            existing_pattern = pattern
            break

    if existing_pattern:
        # 既存パターンを強化
        existing_pattern["repetition_count"] = (
            existing_pattern.get("repetition_count", 1) + 1
        )
        existing_pattern["severity"] = "critical"
        existing_pattern["escalated_prevention"] = new_pattern["escalated_prevention"]
        existing_pattern["last_occurrence"] = new_pattern["last_occurrence"]
    else:
        # 新パターンとして追加
        mistakes_db["critical_patterns"].append(new_pattern)

    mistakes_db["total_mistakes"] += 1

    # データベースを保存
    with open(MISTAKES_DB, "w", encoding="utf-8") as f:
        json.dump(mistakes_db, f, ensure_ascii=False, indent=2)

    print("🚨 絶対パス再使用ミスを学習しました - より強力な防止策を追加")


if __name__ == "__main__":
    add_absolute_path_pattern()
