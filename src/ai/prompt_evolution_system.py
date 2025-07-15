#!/usr/bin/env python3
"""
自動プロンプト進化システム - Autonomous Prompt Evolution System
パフォーマンスデータに基づいてCLAUDE.mdを自動最適化
"""

import re
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class PromptRule:
    """プロンプトルール"""
    rule_id: str
    content: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'thinking', 'todo', 'safety', 'efficiency'
    effectiveness_score: float
    usage_frequency: int
    last_updated: str

@dataclass
class EvolutionChange:
    """進化変更"""
    change_type: str  # 'add', 'modify', 'remove', 'strengthen'
    rule_id: str
    old_content: Optional[str]
    new_content: str
    reason: str
    confidence_score: float

class PromptEvolutionSystem:
    """自動プロンプト進化システム"""
    
    def __init__(self, project_root: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_root = Path(project_root)
        self.claude_md_path = self.project_root / "CLAUDE.md"
        self.db_path = self.project_root / "runtime" / "memory" / "ai_growth.db"
        self.evolution_log_path = self.project_root / "runtime" / "logs" / "prompt_evolution.log"
        
        # バックアップディレクトリ
        self.backup_dir = self.project_root / "runtime" / "claude_md_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # ログ設定
        self.logger = self._setup_logger()
        
        # 進化設定
        self.evolution_config = {
            'min_data_points': 10,      # 最小データポイント数
            'confidence_threshold': 0.75, # 信頼度閾値
            'safety_threshold': 0.85,   # 安全性閾値（パフォーマンス低下防止）
            'max_rules_per_day': 5,     # 日次最大ルール変更数
            'rollback_threshold': 0.80  # ロールバック閾値
        }
        
        # 現在のルール解析
        self.current_rules = self._parse_current_rules()
        
    def _setup_logger(self) -> logging.Logger:
        """ログシステム設定"""
        logger = logging.getLogger('prompt_evolution')
        logger.setLevel(logging.INFO)
        
        self.evolution_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(self.evolution_log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    def _parse_current_rules(self) -> Dict[str, PromptRule]:
        """現在のCLAUDE.mdルール解析"""
        if not self.claude_md_path.exists():
            return {}
            
        with open(self.claude_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        rules = {}
        
        # 重要ルールパターン抽出
        patterns = {
            'thinking_mandatory': r'<thinking>.*?必須|MANDATORY.*?thinking',
            'todo_tracking': r'TodoWrite.*?必須|MANDATORY.*?TodoWrite',
            'file_safety': r'Read.*?before.*?Edit|Edit前.*?Read',
            'error_handling': r'エラー.*?処理|error.*?handling',
            'president_declaration': r'PRESIDENT.*?宣言|宣言.*?PRESIDENT'
        }
        
        for category, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for i, match in enumerate(matches):
                rule_id = f"{category}_{i+1}"
                rules[rule_id] = PromptRule(
                    rule_id=rule_id,
                    content=match.group(),
                    priority='high',
                    category=category,
                    effectiveness_score=0.0,
                    usage_frequency=0,
                    last_updated=datetime.now().isoformat()
                )
                
        return rules
        
    def analyze_performance_patterns(self, days: int = 7) -> Dict[str, List[Dict]]:
        """パフォーマンスパターン分析"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 成功パターン分析
                cursor = conn.execute("""
                    SELECT success_patterns, COUNT(*) as frequency,
                           AVG(execution_time) as avg_time,
                           AVG(error_count) as avg_errors
                    FROM ai_performance_log 
                    WHERE timestamp > datetime('now', '-{} day')
                      AND task_success = 1
                      AND success_patterns IS NOT NULL
                    GROUP BY success_patterns
                    ORDER BY frequency DESC
                """.format(days))
                
                success_patterns = []
                for row in cursor.fetchall():
                    try:
                        patterns = json.loads(row[0])
                        success_patterns.append({
                            'patterns': patterns,
                            'frequency': row[1],
                            'avg_time': row[2],
                            'avg_errors': row[3],
                            'effectiveness': row[1] / max(row[2], 1)  # 頻度/時間
                        })
                    except:
                        continue
                        
                # 失敗パターン分析
                cursor = conn.execute("""
                    SELECT failure_patterns, COUNT(*) as frequency,
                           AVG(execution_time) as avg_time,
                           AVG(error_count) as avg_errors
                    FROM ai_performance_log 
                    WHERE timestamp > datetime('now', '-{} day')
                      AND task_success = 0
                      AND failure_patterns IS NOT NULL
                    GROUP BY failure_patterns
                    ORDER BY frequency DESC
                """.format(days))
                
                failure_patterns = []
                for row in cursor.fetchall():
                    try:
                        patterns = json.loads(row[0])
                        failure_patterns.append({
                            'patterns': patterns,
                            'frequency': row[1],
                            'avg_time': row[2],
                            'avg_errors': row[3],
                            'severity': row[1] * row[3]  # 頻度 × エラー数
                        })
                    except:
                        continue
                        
                return {
                    'success_patterns': success_patterns,
                    'failure_patterns': failure_patterns
                }
                
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return {'success_patterns': [], 'failure_patterns': []}
            
    def generate_evolution_changes(self, patterns: Dict[str, List[Dict]]) -> List[EvolutionChange]:
        """進化変更生成"""
        changes = []
        
        # 成功パターンから新しいルール生成
        for pattern_data in patterns['success_patterns']:
            if pattern_data['frequency'] >= 5 and pattern_data['effectiveness'] > 2:
                changes.extend(self._generate_success_based_changes(pattern_data))
                
        # 失敗パターンから改善ルール生成
        for pattern_data in patterns['failure_patterns']:
            if pattern_data['frequency'] >= 3:
                changes.extend(self._generate_failure_based_changes(pattern_data))
                
        # 信頼度によるフィルタリング
        high_confidence_changes = [
            c for c in changes 
            if c.confidence_score >= self.evolution_config['confidence_threshold']
        ]
        
        return high_confidence_changes[:self.evolution_config['max_rules_per_day']]
        
    def _generate_success_based_changes(self, pattern_data: Dict) -> List[EvolutionChange]:
        """成功パターンベースの変更生成"""
        changes = []
        patterns = pattern_data['patterns']
        
        if 'thinking_tag_usage' in patterns:
            changes.append(EvolutionChange(
                change_type='strengthen',
                rule_id='thinking_enforcement',
                old_content=None,
                new_content='🔴 **CRITICAL MANDATORY**: All responses MUST start with <thinking> tag - NO EXCEPTIONS',
                reason=f'High success correlation: {pattern_data["frequency"]} instances',
                confidence_score=min(pattern_data['effectiveness'] / 10, 1.0)
            ))
            
        if 'todo_tracking' in patterns:
            changes.append(EvolutionChange(
                change_type='strengthen',
                rule_id='todo_enforcement',
                old_content=None,
                new_content='🔴 **MANDATORY**: Use TodoWrite for ALL multi-step tasks - Track progress religiously',
                reason=f'Proven effectiveness: {pattern_data["effectiveness"]:.2f} score',
                confidence_score=min(pattern_data['frequency'] / 20, 1.0)
            ))
            
        if 'read_before_edit' in patterns:
            changes.append(EvolutionChange(
                change_type='add',
                rule_id='file_safety_protocol',
                old_content=None,
                new_content='⚠️ **SAFETY PROTOCOL**: ALWAYS use Read tool before Edit tool - NO direct editing',
                reason=f'Safety pattern confirmed: {pattern_data["frequency"]} safe operations',
                confidence_score=min(pattern_data['frequency'] / 15, 1.0)
            ))
            
        return changes
        
    def _generate_failure_based_changes(self, pattern_data: Dict) -> List[EvolutionChange]:
        """失敗パターンベースの変更生成"""
        changes = []
        patterns = pattern_data['patterns']
        
        if 'missing_thinking_tag' in patterns:
            changes.append(EvolutionChange(
                change_type='add',
                rule_id='thinking_violation_prevention',
                old_content=None,
                new_content='🚨 **VIOLATION PREVENTION**: Thinking tag omission detected. Immediate enforcement required.',
                reason=f'Critical failure pattern: {pattern_data["frequency"]} violations',
                confidence_score=min(pattern_data['severity'] / 50, 1.0)
            ))
            
        if 'execution_errors' in patterns:
            changes.append(EvolutionChange(
                change_type='add',
                rule_id='error_prevention_protocol',
                old_content=None,
                new_content='🛡️ **ERROR PREVENTION**: Validate all tool outputs before proceeding - Double-check everything',
                reason=f'Error reduction needed: {pattern_data["avg_errors"]:.2f} avg errors',
                confidence_score=min(pattern_data['frequency'] / 10, 1.0)
            ))
            
        return changes
        
    def apply_evolution_changes(self, changes: List[EvolutionChange]) -> bool:
        """進化変更適用"""
        if not changes:
            self.logger.info("No evolution changes to apply")
            return True
            
        # バックアップ作成
        backup_success = self._create_backup()
        if not backup_success:
            self.logger.error("Backup creation failed - Aborting evolution")
            return False
            
        try:
            # CLAUDE.md読み込み
            with open(self.claude_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 変更適用
            for change in changes:
                content = self._apply_single_change(content, change)
                self.logger.info(f"Applied change: {change.change_type} - {change.rule_id}")
                
            # 安全性検証
            if self._validate_evolved_content(content):
                # ファイル書き込み
                with open(self.claude_md_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # 変更ログ記録
                self._log_evolution_changes(changes)
                
                self.logger.info(f"Successfully applied {len(changes)} evolution changes")
                return True
            else:
                self.logger.warning("Evolved content failed validation - Reverting")
                return False
                
        except Exception as e:
            self.logger.error(f"Evolution application failed: {e}")
            # 自動復旧
            self._restore_from_backup()
            return False
            
    def _apply_single_change(self, content: str, change: EvolutionChange) -> str:
        """単一変更適用"""
        if change.change_type == 'add':
            # 適切な位置に新ルール追加
            insertion_point = self._find_insertion_point(content, change.rule_id)
            new_rule = f"\n### 🔄 Auto-Evolution Rule: {change.rule_id}\n{change.new_content}\n"
            content = content[:insertion_point] + new_rule + content[insertion_point:]
            
        elif change.change_type == 'strengthen':
            # 既存ルールの強化
            if change.old_content:
                content = content.replace(change.old_content, change.new_content)
            else:
                # 新しい強化ルール追加
                strengthening_section = f"\n## 🔥 Evolution-Strengthened Rules\n### {change.rule_id}\n{change.new_content}\n"
                content = self._insert_after_section(content, "## 🔴 最優先必須", strengthening_section)
                
        elif change.change_type == 'modify':
            if change.old_content:
                content = content.replace(change.old_content, change.new_content)
                
        elif change.change_type == 'remove':
            if change.old_content:
                content = content.replace(change.old_content, "")
                
        return content
        
    def _find_insertion_point(self, content: str, rule_category: str) -> int:
        """挿入ポイント検索"""
        # カテゴリ別の挿入ポイント
        insertion_markers = {
            'thinking': "## 🔴 厳格応答プロトコル",
            'todo': "### TodoWrite",
            'safety': "## 🔒 Safety Mechanisms",
            'efficiency': "### Task・サブエージェントシステム"
        }
        
        for category, marker in insertion_markers.items():
            if category in rule_category:
                match = re.search(marker, content)
                if match:
                    return match.end()
                    
        # デフォルト：ファイル末尾に追加
        return len(content)
        
    def _insert_after_section(self, content: str, section_marker: str, new_content: str) -> str:
        """セクション後に挿入"""
        match = re.search(section_marker, content)
        if match:
            # 次のセクション（##）まで検索
            next_section = re.search(r'\n##', content[match.end():])
            if next_section:
                insertion_point = match.end() + next_section.start()
            else:
                insertion_point = len(content)
            return content[:insertion_point] + new_content + content[insertion_point:]
        return content + new_content
        
    def _validate_evolved_content(self, content: str) -> bool:
        """進化後コンテンツ検証"""
        # 基本構造チェック
        required_sections = [
            "## 🔴 最優先必須",
            "CLAUDE.md",
            "記憶継承システム"
        ]
        
        for section in required_sections:
            if section not in content:
                self.logger.warning(f"Missing required section: {section}")
                return False
                
        # ファイルサイズチェック（極端な増加防止）
        if len(content) > 50000:  # 50KB制限
            self.logger.warning("Evolved content too large")
            return False
            
        # 重複ルールチェック
        if self._has_duplicate_rules(content):
            self.logger.warning("Duplicate rules detected")
            return False
            
        return True
        
    def _has_duplicate_rules(self, content: str) -> bool:
        """重複ルール検出"""
        # 同じルール内容の重複チェック
        rule_contents = re.findall(r'###.*?\n(.+?)(?=\n###|\n##|$)', content, re.DOTALL)
        unique_rules = set()
        
        for rule in rule_contents:
            rule_hash = hashlib.md5(rule.strip().encode()).hexdigest()
            if rule_hash in unique_rules:
                return True
            unique_rules.add(rule_hash)
            
        return False
        
    def _create_backup(self) -> bool:
        """バックアップ作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"CLAUDE.md.{timestamp}.backup"
            
            if self.claude_md_path.exists():
                with open(self.claude_md_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                        
                self.logger.info(f"Backup created: {backup_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False
            
    def _restore_from_backup(self) -> bool:
        """バックアップから復旧"""
        try:
            # 最新のバックアップファイル検索
            backup_files = list(self.backup_dir.glob("CLAUDE.md.*.backup"))
            if not backup_files:
                return False
                
            latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_backup, 'r', encoding='utf-8') as src:
                with open(self.claude_md_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                    
            self.logger.info(f"Restored from backup: {latest_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            return False
            
    def _log_evolution_changes(self, changes: List[EvolutionChange]):
        """進化変更ログ記録"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for change in changes:
                    conn.execute("""
                        INSERT INTO ai_evolution_log (
                            timestamp, new_rules, deprecated_rules, evolution_score,
                            auto_applied, requires_review
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        json.dumps([asdict(change)]),
                        "[]",
                        change.confidence_score,
                        True,
                        change.confidence_score < 0.9
                    ))
                    
        except Exception as e:
            self.logger.error(f"Evolution logging failed: {e}")
            
    def run_daily_evolution(self) -> Dict:
        """日次進化実行"""
        self.logger.info("Starting daily evolution process")
        
        # パフォーマンスパターン分析
        patterns = self.analyze_performance_patterns()
        
        if not patterns['success_patterns'] and not patterns['failure_patterns']:
            self.logger.info("Insufficient data for evolution")
            return {'status': 'skipped', 'reason': 'insufficient_data'}
            
        # 進化変更生成
        changes = self.generate_evolution_changes(patterns)
        
        if not changes:
            self.logger.info("No evolution changes generated")
            return {'status': 'skipped', 'reason': 'no_changes_needed'}
            
        # 変更適用
        success = self.apply_evolution_changes(changes)
        
        result = {
            'status': 'success' if success else 'failed',
            'changes_applied': len(changes) if success else 0,
            'patterns_analyzed': {
                'success_patterns': len(patterns['success_patterns']),
                'failure_patterns': len(patterns['failure_patterns'])
            },
            'evolution_summary': [asdict(c) for c in changes] if success else []
        }
        
        self.logger.info(f"Daily evolution completed: {result['status']}")
        return result

def main():
    """メイン実行関数"""
    import sys
    
    evolution_system = PromptEvolutionSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'evolve':
            result = evolution_system.run_daily_evolution()
            print("🧬 Daily Evolution Results:")
            print(f"   Status: {result['status']}")
            print(f"   Changes Applied: {result['changes_applied']}")
            print(f"   Success Patterns: {result['patterns_analyzed']['success_patterns']}")
            print(f"   Failure Patterns: {result['patterns_analyzed']['failure_patterns']}")
            
        elif command == 'analyze':
            patterns = evolution_system.analyze_performance_patterns()
            print("📊 Performance Pattern Analysis:")
            print(f"   Success Patterns: {len(patterns['success_patterns'])}")
            print(f"   Failure Patterns: {len(patterns['failure_patterns'])}")
            
            for i, pattern in enumerate(patterns['success_patterns'][:5]):
                print(f"   Top Success #{i+1}: {pattern['patterns']} (freq: {pattern['frequency']})")
                
        elif command == 'backup':
            success = evolution_system._create_backup()
            print(f"💾 Backup: {'Success' if success else 'Failed'}")
            
    else:
        print("Prompt Evolution System - Usage:")
        print("  python prompt_evolution_system.py evolve  - Run daily evolution")
        print("  python prompt_evolution_system.py analyze - Analyze patterns")
        print("  python prompt_evolution_system.py backup  - Create backup")

if __name__ == "__main__":
    main()