#!/usr/bin/env python3
"""
自律成長フックシステム - 超軽量・高効率パフォーマンス追跡
Claude Code Hooks と統合して最小負荷で最大効果を実現
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from ai.autonomous_growth_engine import AutonomousGrowthEngine, PerformanceMetrics
except ImportError:
    # フォールバック: 軽量版実装
    class LightweightGrowthEngine:
        def __init__(self):
            self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
            self.db_path = self.project_root / "runtime" / "memory" / "lightweight_growth.db"
            self._init_lightweight_db()

        def _init_lightweight_db(self):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS quick_metrics (
                        timestamp TEXT,
                        hook_type TEXT,
                        tool_name TEXT,
                        success INTEGER,
                        duration REAL,
                        details TEXT
                    )
                """)

        def log_quick_metric(self, hook_type: str, tool_name: str,
                           success: bool, duration: float, details: Dict):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO quick_metrics
                    (timestamp, hook_type, tool_name, success, duration, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    hook_type,
                    tool_name,
                    1 if success else 0,
                    duration,
                    json.dumps(details, default=str)
                ))

class AutonomousGrowthHook:
    """Claude Code Hook システム統合 - 超軽量版"""

    def __init__(self):
        # 環境変数から設定読み込み
        self.project_root = Path(os.getenv('PROJECT_ROOT', '/Users/dd/Desktop/1_dev/coding-rule2'))
        self.n8n_webhook = os.getenv('N8N_WEBHOOK_URL', 'https://n8n.cloud/webhook/claude-performance')
        self.enabled = os.getenv('AUTONOMOUS_GROWTH_ENABLED', 'true').lower() == 'true'

        # フック状態追跡（メモリ内）
        self.session_data = {}
        self.performance_cache = []

        # 成長エンジン初期化（軽量モード）
        try:
            self.growth_engine = AutonomousGrowthEngine()
        except Exception:
            self.growth_engine = LightweightGrowthEngine()

        # 統計カウンター
        self.stats = {
            'total_hooks': 0,
            'successful_tools': 0,
            'failed_tools': 0,
            'avg_execution_time': 0
        }

    def on_session_start(self, session_id: str):
        """セッション開始フック - 軽量初期化"""
        if not self.enabled:
            return

        self.session_data[session_id] = {
            'start_time': time.time(),
            'tools_used': [],
            'errors': [],
            'thinking_tag_count': 0,
            'todo_usage': False
        }

        # 超軽量ログ記録
        self._log_lightweight_event('session_start', session_id, {})

    def on_tool_use_pre(self, session_id: str, tool_name: str, parameters: Dict):
        """ツール使用前フック - 最小追跡"""
        if not self.enabled or session_id not in self.session_data:
            return

        self.session_data[session_id]['tools_used'].append({
            'name': tool_name,
            'start_time': time.time(),
            'parameters_count': len(parameters) if parameters else 0
        })

        self.stats['total_hooks'] += 1

    def on_tool_use_post(self, session_id: str, tool_name: str, success: bool,
                        result: Any = None, error: Optional[str] = None):
        """ツール使用後フック - パフォーマンス集計"""
        if not self.enabled or session_id not in self.session_data:
            return

        session = self.session_data[session_id]

        # 実行時間計算
        tool_entry = None
        for tool in reversed(session['tools_used']):
            if tool['name'] == tool_name and 'duration' not in tool:
                tool_entry = tool
                break

        if tool_entry:
            duration = time.time() - tool_entry['start_time']
            tool_entry['duration'] = duration
            tool_entry['success'] = success

            # 統計更新
            if success:
                self.stats['successful_tools'] += 1
            else:
                self.stats['failed_tools'] += 1
                session['errors'].append({
                    'tool': tool_name,
                    'error': str(error) if error else 'unknown',
                    'timestamp': time.time()
                })

            # 平均実行時間更新
            total_tools = self.stats['successful_tools'] + self.stats['failed_tools']
            if total_tools > 0:
                current_avg = self.stats['avg_execution_time']
                self.stats['avg_execution_time'] = (
                    (current_avg * (total_tools - 1) + duration) / total_tools
                )

            # 特殊パターン検出
            self._detect_patterns(session_id, tool_name, success, duration)

    def on_session_stop(self, session_id: str):
        """セッション終了フック - 総合評価と学習"""
        if not self.enabled or session_id not in self.session_data:
            return

        session = self.session_data[session_id]
        total_duration = time.time() - session['start_time']

        # セッション総合評価
        session_metrics = self._calculate_session_metrics(session, total_duration)

        # n8nへの非同期送信（失敗時は無視）
        self._send_to_n8n_async(session_metrics)

        # 軽量成長エンジンにデータ送信
        self._trigger_learning(session_metrics)

        # メモリクリーンアップ
        del self.session_data[session_id]

    def _detect_patterns(self, session_id: str, tool_name: str, success: bool, duration: float):
        """軽量パターン検出"""
        session = self.session_data[session_id]

        # thinking tag 使用パターン
        if 'thinking' in str(tool_name).lower():
            session['thinking_tag_count'] += 1

        # TodoWrite 使用パターン
        if tool_name == 'TodoWrite':
            session['todo_usage'] = True

        # 高速実行パターン
        if success and duration < 1.0:
            self._log_lightweight_event('fast_execution', session_id, {
                'tool': tool_name,
                'duration': duration
            })

        # エラーパターン
        elif not success:
            self._log_lightweight_event('execution_error', session_id, {
                'tool': tool_name,
                'duration': duration
            })

    def _calculate_session_metrics(self, session: Dict, total_duration: float) -> Dict:
        """セッション指標計算"""
        tools = session['tools_used']
        successful_tools = [t for t in tools if t.get('success', False)]

        return {
            'session_summary': {
                'total_duration': total_duration,
                'tools_count': len(tools),
                'success_rate': len(successful_tools) / max(len(tools), 1),
                'avg_tool_time': sum(t.get('duration', 0) for t in tools) / max(len(tools), 1),
                'error_count': len(session['errors']),
                'thinking_usage': session['thinking_tag_count'] > 0,
                'todo_usage': session['todo_usage']
            },
            'patterns': {
                'efficient_execution': len([t for t in tools if t.get('duration', 99) < 1.0]),
                'error_prone_tools': [e['tool'] for e in session['errors']],
                'tool_sequence': [t['name'] for t in tools]
            },
            'learning_signals': {
                'positive': len(successful_tools),
                'negative': len(session['errors']),
                'efficiency_score': 100 / max(total_duration, 1) * len(successful_tools)
            }
        }

    def _send_to_n8n_async(self, metrics: Dict):
        """n8n非同期送信（失敗時は無視）"""
        try:
            # バックグラウンド送信
            import threading

            def send_request():
                try:
                    requests.post(
                        self.n8n_webhook,
                        json=metrics,
                        timeout=5  # 短いタイムアウト
                    )
                except Exception:
                    pass  # 失敗は無視

            threading.Thread(target=send_request, daemon=True).start()

        except Exception:
            pass  # スレッド作成失敗も無視

    def _trigger_learning(self, metrics: Dict):
        """学習トリガー"""
        try:
            if hasattr(self.growth_engine, 'log_quick_metric'):
                # 軽量エンジンの場合
                self.growth_engine.log_quick_metric(
                    'session_summary',
                    'session',
                    metrics['session_summary']['success_rate'] > 0.8,
                    metrics['session_summary']['total_duration'],
                    metrics
                )
            else:
                # フル機能エンジンの場合
                # 詳細な学習処理
                pass

        except Exception:
            pass  # 学習失敗は無視

    def _log_lightweight_event(self, event_type: str, session_id: str, data: Dict):
        """超軽量イベントログ"""
        # メモリ内キャッシュに保存（定期的にフラッシュ）
        self.performance_cache.append({
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'session': session_id,
            'data': data
        })

        # キャッシュサイズ制限
        if len(self.performance_cache) > 1000:
            self.performance_cache = self.performance_cache[-500:]  # 半分削除

    def get_current_stats(self) -> Dict:
        """現在の統計取得"""
        return {
            'hook_stats': self.stats.copy(),
            'active_sessions': len(self.session_data),
            'cache_size': len(self.performance_cache),
            'enabled': self.enabled
        }

# Claude Code Hook エントリーポイント
def claude_code_hook_handler(hook_type: str, **kwargs):
    """Claude Code Hook メインハンドラー"""

    # グローバルインスタンス（シングルトン）
    if not hasattr(claude_code_hook_handler, '_instance'):
        claude_code_hook_handler._instance = AutonomousGrowthHook()

    hook = claude_code_hook_handler._instance

    try:
        if hook_type == 'session_start':
            hook.on_session_start(kwargs.get('session_id', 'unknown'))

        elif hook_type == 'tool_use_pre':
            hook.on_tool_use_pre(
                kwargs.get('session_id', 'unknown'),
                kwargs.get('tool_name', 'unknown'),
                kwargs.get('parameters', {})
            )

        elif hook_type == 'tool_use_post':
            hook.on_tool_use_post(
                kwargs.get('session_id', 'unknown'),
                kwargs.get('tool_name', 'unknown'),
                kwargs.get('success', False),
                kwargs.get('result'),
                kwargs.get('error')
            )

        elif hook_type == 'session_stop':
            hook.on_session_stop(kwargs.get('session_id', 'unknown'))

    except Exception:
        # フック失敗は Claude Code の動作を妨げない
        pass

# CLI エントリーポイント
def main():
    """CLIメイン実行"""
    hook = AutonomousGrowthHook()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'stats':
            stats = hook.get_current_stats()
            print("📊 Autonomous Growth Hook Statistics:")
            print(f"   Total Hooks: {stats['hook_stats']['total_hooks']}")
            print(f"   Success Rate: {stats['hook_stats']['successful_tools']} / {stats['hook_stats']['successful_tools'] + stats['hook_stats']['failed_tools']}")
            print(f"   Avg Execution Time: {stats['hook_stats']['avg_execution_time']:.2f}s")
            print(f"   Active Sessions: {stats['active_sessions']}")
            print(f"   Cache Size: {stats['cache_size']}")
            print(f"   Enabled: {stats['enabled']}")

        elif command == 'test':
            # テスト実行
            print("🧪 Testing Autonomous Growth Hook...")
            hook.on_session_start('test_session')
            hook.on_tool_use_pre('test_session', 'Read', {'file_path': 'test.py'})
            time.sleep(0.1)
            hook.on_tool_use_post('test_session', 'Read', True)
            hook.on_session_stop('test_session')
            print("✅ Test completed successfully")

        elif command == 'enable':
            os.environ['AUTONOMOUS_GROWTH_ENABLED'] = 'true'
            print("✅ Autonomous Growth Hook enabled")

        elif command == 'disable':
            os.environ['AUTONOMOUS_GROWTH_ENABLED'] = 'false'
            print("❌ Autonomous Growth Hook disabled")

    else:
        print("Autonomous Growth Hook - Usage:")
        print("  python autonomous_growth_hook.py stats   - Show statistics")
        print("  python autonomous_growth_hook.py test    - Run test")
        print("  python autonomous_growth_hook.py enable  - Enable hook")
        print("  python autonomous_growth_hook.py disable - Disable hook")

if __name__ == "__main__":
    main()
