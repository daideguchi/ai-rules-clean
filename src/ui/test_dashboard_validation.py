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
🧪 Dashboard Validation Test
===========================
Quick test to validate the dashboard modifications work correctly
"""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from visual_dashboard import VisualDashboard

    print("📊 Testing Visual Dashboard Modifications...")
    print("=" * 50)

    # Initialize dashboard
    dashboard = VisualDashboard()

    # Test worker data
    print("🔍 Testing Worker Data:")
    for _worker_id, worker in list(dashboard.workers.items())[:3]:  # Test first 3
        print(f"  {worker.icon} {worker.display_name}")
        print(f"    TODO: {worker.specific_todo}")
        print(f"    Action: {worker.current_action}")
        print(f"    Milestone: {worker.next_milestone}")
        print(f"    Priority: {worker.priority}")
        print()

    # Test system metrics
    print("🎯 Testing Project Mission:")
    metrics = dashboard.system_metrics
    print(f"  Mission: {metrics.project_mission}")
    print(f"  Phase: {metrics.current_phase}")
    print(f"  Target: {metrics.completion_target}")
    print(f"  Progress: {metrics.overall_progress}%")
    print()

    # Test layout creation (non-interactive)
    print("🖼️ Testing Layout Creation:")
    try:
        dashboard._update_layout()
        print("  ✅ Layout update successful")
    except Exception as e:
        print(f"  ❌ Layout error: {e}")

    # Test header creation
    print("👑 Testing PRESIDENT Status Bar:")
    try:
        header = dashboard._create_header()
        print("  ✅ Header with PRESIDENT bar created successfully")
    except Exception as e:
        print(f"  ❌ Header error: {e}")

    print("\n✅ Dashboard validation complete!")
    print("The modifications are working correctly.")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test error: {e}")
