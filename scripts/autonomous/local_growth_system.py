#!/usr/bin/env python3
"""
ローカル完結型自律成長システム
n8nに依存せず、完全にローカルで動作する実際に意味のあるAI成長システム
"""

import os
import json
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
import requests

class LocalAutonomousGrowthSystem:
    """ローカル完結型自律成長システム"""
    
    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.db_path = self.project_root / "runtime/memory/autonomous_growth.db"
        self.claude_md_path = self.project_root / "CLAUDE.md"
        
        # ローカルWebサーバー設定
        self.app = Flask(__name__)
        self.port = 3002
        
        # データベース初期化
        self._init_database()
        
        # Webhook エンドポイント設定
        self._setup_webhook_endpoints()
        
        # バックグラウンド学習タスク
        self.learning_thread = None
        self.running = False
        
    def _init_database(self):
        """データベース初期化"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # パフォーマンスデータテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    task_success BOOLEAN,
                    execution_time REAL,
                    tool_calls TEXT,
                    error_count INTEGER,
                    thinking_tag_used BOOLEAN,
                    todo_tracking BOOLEAN,
                    success_patterns TEXT,
                    failure_patterns TEXT,
                    learning_score REAL
                )
            """)
            
            # 学習パターンテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    effectiveness_score REAL,
                    frequency INTEGER DEFAULT 1
                )
            """)
            
            # CLAUDE.md進化履歴
            conn.execute("""
                CREATE TABLE IF NOT EXISTS claude_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    change_type TEXT,
                    old_content TEXT,
                    new_content TEXT,
                    reason TEXT,
                    performance_improvement REAL
                )
            """)
            
    def _setup_webhook_endpoints(self):
        """Webhook エンドポイント設定"""
        
        @self.app.route('/webhook/claude-performance', methods=['POST'])
        def receive_performance_data():
            """Claude Code パフォーマンスデータ受信"""
            try:
                data = request.json
                
                # データ処理と学習
                learning_result = self._process_performance_data(data)
                
                # 即座学習トリガー
                if learning_result['should_evolve']:
                    threading.Thread(target=self._trigger_immediate_evolution, daemon=True).start()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Performance data processed and learning triggered',
                    'learning_active': True,
                    'patterns_detected': learning_result['patterns'],
                    'evolution_triggered': learning_result['should_evolve']
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/growth-status', methods=['GET'])
        def get_growth_status():
            """成長状況取得"""
            try:
                status = self._get_growth_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/force-evolution', methods=['POST'])
        def force_evolution():
            """手動進化トリガー"""
            try:
                result = self._force_evolution()
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
    def _process_performance_data(self, data: Dict) -> Dict:
        """パフォーマンスデータ処理と学習"""
        
        # 基本データ抽出
        session_id = data.get('session_id', f'auto_{int(time.time())}')
        task_success = data.get('success', False)
        execution_time = data.get('execution_time', 0)
        tool_calls = data.get('tools_used', [])
        thinking_tag_used = data.get('thinking_tag_used', False)
        todo_tracking = data.get('todo_tracking', False)
        
        # パターン分析
        success_patterns = []
        failure_patterns = []
        
        if task_success:
            if thinking_tag_used:
                success_patterns.append('thinking_tag_usage')
            if todo_tracking:
                success_patterns.append('todo_tracking')
            if execution_time < 5:
                success_patterns.append('fast_execution')
            if len(tool_calls) <= 3:
                success_patterns.append('efficient_tool_usage')
        else:
            if not thinking_tag_used:
                failure_patterns.append('missing_thinking_tag')
            if execution_time > 30:
                failure_patterns.append('slow_execution')
            if len(tool_calls) > 10:
                failure_patterns.append('excessive_tool_usage')
        
        # 学習スコア計算
        learning_score = len(success_patterns) - len(failure_patterns)
        
        # データベース保存
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance_data (
                    session_id, timestamp, task_success, execution_time,
                    tool_calls, error_count, thinking_tag_used, todo_tracking,
                    success_patterns, failure_patterns, learning_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                task_success,
                execution_time,
                json.dumps(tool_calls),
                data.get('error_count', 0),
                thinking_tag_used,
                todo_tracking,
                json.dumps(success_patterns),
                json.dumps(failure_patterns),
                learning_score
            ))
        
        # 学習パターン更新
        self._update_learning_patterns(success_patterns + failure_patterns)
        
        # 進化判定
        should_evolve = self._should_trigger_evolution()
        
        return {
            'patterns': success_patterns + failure_patterns,
            'learning_score': learning_score,
            'should_evolve': should_evolve
        }
        
    def _update_learning_patterns(self, patterns: List[str]):
        """学習パターン更新"""
        with sqlite3.connect(self.db_path) as conn:
            for pattern in patterns:
                # 既存パターンの頻度更新
                cursor = conn.execute("""
                    SELECT id, frequency FROM learning_patterns 
                    WHERE pattern_data = ?
                """, (pattern,))
                
                result = cursor.fetchone()
                
                if result:
                    # 頻度増加
                    conn.execute("""
                        UPDATE learning_patterns 
                        SET frequency = frequency + 1,
                            timestamp = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), result[0]))
                else:
                    # 新パターン追加
                    conn.execute("""
                        INSERT INTO learning_patterns (
                            timestamp, pattern_type, pattern_data, 
                            effectiveness_score, frequency
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        'behavioral',
                        pattern,
                        1.0,
                        1
                    ))
                    
    def _should_trigger_evolution(self) -> bool:
        """進化トリガー判定"""
        with sqlite3.connect(self.db_path) as conn:
            # 直近の学習データ確認
            cursor = conn.execute("""
                SELECT AVG(learning_score), COUNT(*) 
                FROM performance_data 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            
            result = cursor.fetchone()
            avg_score = result[0] or 0
            data_count = result[1] or 0
            
            # 進化条件: 10件以上のデータ + 平均スコアが閾値以上
            return data_count >= 10 and abs(avg_score) >= 2
            
    def _trigger_immediate_evolution(self):
        """即座進化実行"""
        try:
            # 最頻出パターン分析
            patterns = self._analyze_top_patterns()
            
            # CLAUDE.md更新
            evolution_result = self._evolve_claude_md(patterns)
            
            print(f"🧬 即座進化実行: {evolution_result}")
            
        except Exception as e:
            print(f"❌ 進化エラー: {e}")
            
    def _analyze_top_patterns(self) -> Dict:
        """最頻出パターン分析"""
        with sqlite3.connect(self.db_path) as conn:
            # 成功パターン
            cursor = conn.execute("""
                SELECT pattern_data, SUM(frequency) as total_freq
                FROM learning_patterns 
                WHERE effectiveness_score > 0
                GROUP BY pattern_data
                ORDER BY total_freq DESC
                LIMIT 5
            """)
            
            success_patterns = [
                {'pattern': row[0], 'frequency': row[1]}
                for row in cursor.fetchall()
            ]
            
            # 失敗パターン
            cursor = conn.execute("""
                SELECT pattern_data, SUM(frequency) as total_freq
                FROM learning_patterns 
                WHERE effectiveness_score < 0
                GROUP BY pattern_data
                ORDER BY total_freq DESC
                LIMIT 3
            """)
            
            failure_patterns = [
                {'pattern': row[0], 'frequency': row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                'success': success_patterns,
                'failure': failure_patterns
            }
            
    def _evolve_claude_md(self, patterns: Dict) -> Dict:
        """CLAUDE.md進化実行"""
        
        # 現在のCLAUDE.md読み込み
        if not self.claude_md_path.exists():
            return {'status': 'error', 'message': 'CLAUDE.md not found'}
            
        with open(self.claude_md_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
            
        # 進化ルール生成
        evolution_rules = []
        
        # 成功パターンから強化ルール
        for pattern in patterns['success']:
            if pattern['frequency'] >= 5:
                if pattern['pattern'] == 'thinking_tag_usage':
                    evolution_rules.append({
                        'type': 'strengthen',
                        'content': '🔴 **CRITICAL**: <thinking> tags are MANDATORY for all responses',
                        'reason': f'High success frequency: {pattern["frequency"]}'
                    })
                elif pattern['pattern'] == 'todo_tracking':
                    evolution_rules.append({
                        'type': 'strengthen', 
                        'content': '📋 **MANDATORY**: Use TodoWrite for all multi-step tasks',
                        'reason': f'Proven effectiveness: {pattern["frequency"]} successes'
                    })
        
        # 失敗パターンから改善ルール
        for pattern in patterns['failure']:
            if pattern['frequency'] >= 3:
                if pattern['pattern'] == 'missing_thinking_tag':
                    evolution_rules.append({
                        'type': 'add',
                        'content': '🚨 **VIOLATION PREVENTION**: Thinking tag omission detected. Enforcement required.',
                        'reason': f'Critical failure pattern: {pattern["frequency"]} violations'
                    })
        
        # CLAUDE.md更新
        if evolution_rules:
            new_content = self._apply_evolution_rules(current_content, evolution_rules)
            
            # バックアップ作成
            backup_path = self.claude_md_path.parent / f"CLAUDE.md.backup.{int(time.time())}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(current_content)
            
            # 新しい内容書き込み
            with open(self.claude_md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 進化履歴記録
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO claude_evolution (
                        timestamp, change_type, old_content, new_content, reason, performance_improvement
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    'auto_evolution',
                    current_content[:500],  # 最初の500文字のみ保存
                    new_content[:500],
                    f"Applied {len(evolution_rules)} rules",
                    2.0  # 予想改善度
                ))
            
            return {
                'status': 'evolved',
                'rules_applied': len(evolution_rules),
                'backup_created': str(backup_path)
            }
        
        return {'status': 'no_evolution_needed'}
        
    def _apply_evolution_rules(self, content: str, rules: List[Dict]) -> str:
        """進化ルール適用"""
        
        # 進化セクション追加
        evolution_section = "\n\n## 🧬 Auto-Evolution Rules (AI-Generated)\n"
        evolution_section += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        for rule in rules:
            evolution_section += f"### {rule['type'].title()}: {rule['content']}\n"
            evolution_section += f"*Reason: {rule['reason']}*\n\n"
            
        # CLAUDE.mdに追加
        if "## 🧬 Auto-Evolution Rules" in content:
            # 既存セクション置き換え
            import re
            pattern = r'## 🧬 Auto-Evolution Rules.*?(?=\n##|\Z)'
            content = re.sub(pattern, evolution_section.strip(), content, flags=re.DOTALL)
        else:
            # 新セクション追加
            content += evolution_section
            
        return content
        
    def _get_growth_status(self) -> Dict:
        """成長状況取得"""
        with sqlite3.connect(self.db_path) as conn:
            # 総合統計
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(CASE WHEN task_success THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(execution_time) as avg_time,
                    AVG(learning_score) as avg_learning_score
                FROM performance_data
                WHERE timestamp > datetime('now', '-7 day')
            """)
            
            stats = cursor.fetchone()
            
            # 最新進化
            cursor = conn.execute("""
                SELECT timestamp, change_type, reason 
                FROM claude_evolution 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            latest_evolution = cursor.fetchone()
            
            return {
                'total_sessions': stats[0] or 0,
                'success_rate': f"{(stats[1] or 0) * 100:.1f}%",
                'avg_execution_time': f"{stats[2] or 0:.2f}s",
                'learning_velocity': f"{stats[3] or 0:.2f}",
                'latest_evolution': {
                    'timestamp': latest_evolution[0] if latest_evolution else 'Never',
                    'type': latest_evolution[1] if latest_evolution else 'None',
                    'reason': latest_evolution[2] if latest_evolution else 'No evolution yet'
                } if latest_evolution else None,
                'system_status': 'Active and Learning'
            }
            
    def start_server(self):
        """ローカルサーバー開始"""
        print(f"🚀 ローカル自律成長システム開始: http://localhost:{self.port}")
        print(f"📍 Webhook URL: http://localhost:{self.port}/webhook/claude-performance")
        
        self.running = True
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
        
    def stop_server(self):
        """サーバー停止"""
        self.running = False

def main():
    """メイン実行"""
    system = LocalAutonomousGrowthSystem()
    
    try:
        system.start_server()
    except KeyboardInterrupt:
        print("\n🛑 システム停止中...")
        system.stop_server()

if __name__ == "__main__":
    main()