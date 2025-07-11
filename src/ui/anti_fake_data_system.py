#!/usr/bin/env python3
"""
🚨 偽装データ防止システム - 史上最大タブー違反防止
==============================================
ダミーデータ・ハードコード・偽装を完全禁止
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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


class AntiFakeDataSystem:
    """偽装データ防止システム"""

    def __init__(self):
        self.violations = []
        self.banned_patterns = [
            # 日本語ダミーデータ
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
            # 英語ダミーデータ
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

    def validate_data_source(self, data: Any, source_info: str) -> bool:
        """データソースの検証"""
        if isinstance(data, str):
            for pattern in self.banned_patterns:
                if pattern in data:
                    self.violations.append(
                        {
                            "type": "FAKE_DATA_DETECTED",
                            "pattern": pattern,
                            "data": data,
                            "source": source_info,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    return False

        if isinstance(data, (list, dict)):
            data_str = str(data)
            for pattern in self.banned_patterns:
                if pattern in data_str:
                    self.violations.append(
                        {
                            "type": "FAKE_DATA_STRUCTURE",
                            "pattern": pattern,
                            "source": source_info,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    return False

        return True

    def enforce_real_data_only(self, func):
        """デコレータ: 実データのみ強制"""

        def wrapper(*args, **kwargs):
            # 関数名とソースの記録
            source_info = f"{func.__module__}.{func.__name__}"

            # 引数の検証
            for arg in args:
                if not self.validate_data_source(arg, source_info):
                    raise ValueError(f"🚨 FAKE DATA DETECTED in {source_info}: {arg}")

            for key, value in kwargs.items():
                if not self.validate_data_source(value, f"{source_info}.{key}"):
                    raise ValueError(
                        f"🚨 FAKE DATA DETECTED in {source_info}.{key}: {value}"
                    )

            # 実行
            result = func(*args, **kwargs)

            # 結果の検証
            if not self.validate_data_source(result, f"{source_info}.result"):
                raise ValueError(f"🚨 FAKE DATA RETURNED from {source_info}: {result}")

            return result

        return wrapper

    def get_real_system_data(self) -> Dict[str, Any]:
        """実際のシステムデータ取得"""
        try:
            # 実際の組織状態を読み込み
            org_file = (
                Path(__file__).parent.parent
                / "memory"
                / "core"
                / "organization_state.json"
            )
            if org_file.exists():
                with open(org_file, encoding="utf-8") as f:
                    org_data = json.load(f)
                    return org_data
            else:
                raise FileNotFoundError("組織状態ファイルが見つかりません")
        except Exception as e:
            raise RuntimeError(f"実データ取得失敗: {e}")

    def get_real_worker_states(self) -> List[Dict[str, Any]]:
        """実際のワーカー状態取得"""
        try:
            # セッション記録から実際の状態を取得
            session_file = (
                Path(__file__).parent.parent
                / "memory"
                / "core"
                / "session-records"
                / "current-session.json"
            )
            if session_file.exists():
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)
                    return session_data.get("worker_states", [])
            else:
                raise FileNotFoundError("セッションファイルが見つかりません")
        except Exception as e:
            raise RuntimeError(f"実ワーカー状態取得失敗: {e}")

    def generate_violation_report(self) -> str:
        """違反レポート生成"""
        if not self.violations:
            return "✅ 偽装データ検出なし"

        report = f"🚨 {len(self.violations)}件の偽装データ検出:\n"
        for violation in self.violations:
            report += f"- {violation['type']}: {violation['pattern']} in {violation['source']}\n"

        return report


# グローバル防止システム
ANTI_FAKE_SYSTEM = AntiFakeDataSystem()


def real_data_only(func):
    """実データのみ許可デコレータ"""
    return ANTI_FAKE_SYSTEM.enforce_real_data_only(func)


def validate_no_fake_data(data: Any, source: str = "unknown") -> bool:
    """偽装データ検証"""
    return ANTI_FAKE_SYSTEM.validate_data_source(data, source)


def get_real_system_state() -> Dict[str, Any]:
    """実際のシステム状態取得"""
    return ANTI_FAKE_SYSTEM.get_real_system_data()


def get_real_workers() -> List[Dict[str, Any]]:
    """実際のワーカー取得"""
    return ANTI_FAKE_SYSTEM.get_real_worker_states()


if __name__ == "__main__":
    print("🚨 偽装データ防止システム - テスト実行")

    # テスト実行
    try:
        real_data = get_real_system_state()
        print(f"✅ 実データ取得成功: {len(real_data)} 項目")

        # 偽装データテスト
        fake_data = "待機中"
        if not validate_no_fake_data(fake_data, "test"):
            print(f"🚨 偽装データ検出: {fake_data}")

        print(ANTI_FAKE_SYSTEM.generate_violation_report())

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
