"""
CLAUDE.md Integration System
CLAUDE.mdファイル統合・動的ルール適用システム
"""

import re
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable
from pathlib import Path
import threading
import logging


class RuleCategory(Enum):
    """ルールカテゴリ"""
    CRITICAL = "CRITICAL"           # 重要ルール（PRESIDENT宣言等）
    MANDATORY = "MANDATORY"         # 必須ルール（応答形式等）
    WORKFLOW = "WORKFLOW"           # ワークフロールール（手順等）
    PREFERENCE = "PREFERENCE"       # 設定ルール（言語等）
    INTEGRATION = "INTEGRATION"     # 統合ルール（MCP等）


class RuleType(Enum):
    """ルール種別"""
    COMMAND_EXECUTION = "COMMAND_EXECUTION"     # コマンド実行
    FILE_OPERATION = "FILE_OPERATION"          # ファイル操作
    RESPONSE_FORMAT = "RESPONSE_FORMAT"        # 応答形式
    VALIDATION_CHECK = "VALIDATION_CHECK"      # バリデーション
    SYSTEM_INTEGRATION = "SYSTEM_INTEGRATION"  # システム統合


class RuleEnforcementLevel(Enum):
    """ルール強制レベル"""
    IGNORE = "IGNORE"           # 無視（記録のみ）
    WARN = "WARN"              # 警告
    ENFORCE = "ENFORCE"        # 強制実行
    BLOCK = "BLOCK"            # ブロック


@dataclass
class ParsedRule:
    """解析済みルール"""
    rule_id: str
    category: RuleCategory
    rule_type: RuleType
    title: str
    description: str
    enforcement_level: RuleEnforcementLevel
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    file_patterns: List[str] = field(default_factory=list)
    validation_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "rule_id": self.rule_id,
            "category": self.category.value,
            "rule_type": self.rule_type.value,
            "title": self.title,
            "description": self.description,
            "enforcement_level": self.enforcement_level.value,
            "conditions": self.conditions,
            "actions": self.actions,
            "commands": self.commands,
            "file_patterns": self.file_patterns,
            "validation_patterns": self.validation_patterns,
            "metadata": self.metadata
        }


@dataclass
class RuleViolation:
    """ルール違反"""
    violation_id: str
    rule_id: str
    rule_title: str
    violation_type: str
    message: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "WARNING"
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "rule_title": self.rule_title,
            "violation_type": self.violation_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "severity": self.severity,
            "resolved": self.resolved
        }


class CLAUDEMdParser:
    """CLAUDE.mdファイル解析器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # 解析パターン
        self.section_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
        self.command_pattern = re.compile(r'`([^`]+)`')
        self.emphasis_pattern = re.compile(r'\*\*(.*?)\*\*')
        self.critical_pattern = re.compile(r'🔴|CRITICAL|必須|MANDATORY', re.IGNORECASE)
    
    def parse_claude_md(self, file_path: Path) -> Dict[str, Any]:
        """CLAUDE.mdファイル解析"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"CLAUDE.md file not found: {file_path}")
            
            content = file_path.read_text(encoding='utf-8')
            
            # ファイルハッシュ計算
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # セクション解析
            sections = self._parse_sections(content)
            
            # ルール抽出
            rules = self._extract_rules(sections, content)
            
            # コマンド抽出
            commands = self._extract_commands(content)
            
            # ファイルパターン抽出
            file_patterns = self._extract_file_patterns(content)
            
            return {
                "file_path": str(file_path),
                "content_hash": content_hash,
                "parse_timestamp": datetime.now().isoformat(),
                "sections": sections,
                "rules": [rule.to_dict() for rule in rules],
                "commands": commands,
                "file_patterns": file_patterns,
                "metadata": {
                    "section_count": len(sections),
                    "rule_count": len(rules),
                    "command_count": len(commands),
                    "content_length": len(content)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse CLAUDE.md: {e}")
            raise
    
    def _parse_sections(self, content: str) -> List[Dict[str, Any]]:
        """セクション解析"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for line_num, line in enumerate(lines, 1):
            match = self.section_pattern.match(line)
            if match:
                # 前のセクションを保存
                if current_section:
                    sections.append(current_section)
                
                # 新しいセクション開始
                title = match.group(1).strip()
                level = len(line) - len(line.lstrip('#'))
                
                current_section = {
                    "title": title,
                    "level": level,
                    "start_line": line_num,
                    "content": [],
                    "is_critical": bool(self.critical_pattern.search(title))
                }
            elif current_section:
                current_section["content"].append(line)
        
        # 最後のセクションを保存
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_rules(self, sections: List[Dict[str, Any]], content: str) -> List[ParsedRule]:
        """ルール抽出"""
        rules = []
        
        for section in sections:
            section_content = '\n'.join(section["content"])
            
            # セクションタイトルから基本情報を推定
            category = self._determine_rule_category(section["title"])
            rule_type = self._determine_rule_type(section_content)
            enforcement_level = self._determine_enforcement_level(section["title"], section_content)
            
            # ルール作成
            rule = ParsedRule(
                rule_id=f"rule_{hashlib.md5(section['title'].encode()).hexdigest()[:8]}",
                category=category,
                rule_type=rule_type,
                title=section["title"],
                description=section_content[:200] + "..." if len(section_content) > 200 else section_content,
                enforcement_level=enforcement_level,
                conditions=self._extract_conditions(section_content),
                actions=self._extract_actions(section_content),
                commands=self._extract_commands(section_content),
                file_patterns=self._extract_file_patterns(section_content),
                validation_patterns=self._extract_validation_patterns(section_content),
                metadata={
                    "section_level": section["level"],
                    "start_line": section["start_line"],
                    "is_critical": section["is_critical"],
                    "content_length": len(section_content)
                }
            )
            
            rules.append(rule)
        
        return rules
    
    def _determine_rule_category(self, title: str) -> RuleCategory:
        """ルールカテゴリ決定"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['president', '重要', 'critical', '必須']):
            return RuleCategory.CRITICAL
        elif any(keyword in title_lower for keyword in ['mandatory', '応答', 'template', 'format']):
            return RuleCategory.MANDATORY
        elif any(keyword in title_lower for keyword in ['workflow', '手順', 'procedure', 'process']):
            return RuleCategory.WORKFLOW
        elif any(keyword in title_lower for keyword in ['mcp', 'integration', '統合', 'ai']):
            return RuleCategory.INTEGRATION
        else:
            return RuleCategory.PREFERENCE
    
    def _determine_rule_type(self, content: str) -> RuleType:
        """ルール種別決定"""
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['bash', 'command', 'make', 'python']):
            return RuleType.COMMAND_EXECUTION
        elif any(keyword in content_lower for keyword in ['file', 'path', 'directory', 'folder']):
            return RuleType.FILE_OPERATION
        elif any(keyword in content_lower for keyword in ['response', '応答', 'format', 'template']):
            return RuleType.RESPONSE_FORMAT
        elif any(keyword in content_lower for keyword in ['check', 'validate', 'verify', '確認']):
            return RuleType.VALIDATION_CHECK
        elif any(keyword in content_lower for keyword in ['mcp', 'integration', '統合', 'system']):
            return RuleType.SYSTEM_INTEGRATION
        else:
            return RuleType.VALIDATION_CHECK
    
    def _determine_enforcement_level(self, title: str, content: str) -> RuleEnforcementLevel:
        """強制レベル決定"""
        text = (title + " " + content).lower()
        
        if any(keyword in text for keyword in ['critical', '必須', 'mandatory', '禁止', 'block']):
            return RuleEnforcementLevel.ENFORCE
        elif any(keyword in text for keyword in ['warning', '注意', 'warn']):
            return RuleEnforcementLevel.WARN
        elif any(keyword in text for keyword in ['ignore', '無視']):
            return RuleEnforcementLevel.IGNORE
        else:
            return RuleEnforcementLevel.ENFORCE
    
    def _extract_conditions(self, content: str) -> List[str]:
        """条件抽出"""
        conditions = []
        
        # "if", "when", "条件"等のパターンを探す
        condition_patterns = [
            r'if\s+(.+)',
            r'when\s+(.+)',
            r'条件[：:]\s*(.+)',
            r'場合[：:]\s*(.+)'
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            conditions.extend(matches)
        
        return conditions
    
    def _extract_actions(self, content: str) -> List[str]:
        """アクション抽出"""
        actions = []
        
        # アクションパターンを探す
        action_patterns = [
            r'実行[：:]?\s*(.+)',
            r'execute\s+(.+)',
            r'run\s+(.+)',
            r'→\s*(.+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            actions.extend(matches)
        
        return actions
    
    def _extract_commands(self, content: str) -> List[str]:
        """コマンド抽出"""
        commands = []
        
        # コードブロックからコマンド抽出
        code_matches = self.code_block_pattern.findall(content)
        for lang, code in code_matches:
            if lang in ['bash', 'sh', 'shell', '']:
                commands.extend(line.strip() for line in code.split('\n') if line.strip())
        
        # インラインコマンド抽出
        inline_commands = self.command_pattern.findall(content)
        commands.extend(cmd for cmd in inline_commands if any(word in cmd for word in ['make', 'python', 'bash', 'cd', 'ls']))
        
        return list(set(commands))  # 重複除去
    
    def _extract_file_patterns(self, content: str) -> List[str]:
        """ファイルパターン抽出"""
        patterns = []
        
        # ファイルパスパターン
        file_patterns = [
            r'runtime/[\w/.-]+',
            r'src/[\w/.-]+',
            r'tests/[\w/.-]+',
            r'docs/[\w/.-]+',
            r'config/[\w/.-]+',
            r'[\w/.-]*\.py',
            r'[\w/.-]*\.json',
            r'[\w/.-]*\.md'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            patterns.extend(matches)
        
        return list(set(patterns))
    
    def _extract_validation_patterns(self, content: str) -> List[str]:
        """バリデーションパターン抽出"""
        patterns = []
        
        # バリデーション関連パターン
        validation_keywords = ['check', 'verify', 'validate', '確認', '検証', 'test']
        
        for keyword in validation_keywords:
            pattern = rf'{keyword}\s+(.+?)(?:\.|$)'
            matches = re.findall(pattern, content, re.IGNORECASE)
            patterns.extend(matches)
        
        return patterns


class RuleEnforcementEngine:
    """ルール強制実行エンジン"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.active_rules: Dict[str, ParsedRule] = {}
        self.violation_handlers: List[Callable[[RuleViolation], None]] = []
        self.violations_history: List[RuleViolation] = []
        self._lock = threading.Lock()
    
    def load_rules(self, rules: List[ParsedRule]) -> None:
        """ルール読み込み"""
        with self._lock:
            self.active_rules.clear()
            for rule in rules:
                self.active_rules[rule.rule_id] = rule
        
        self.logger.info(f"Loaded {len(rules)} rules into enforcement engine")
    
    def add_violation_handler(self, handler: Callable[[RuleViolation], None]) -> None:
        """違反ハンドラー追加"""
        self.violation_handlers.append(handler)
    
    def check_command_execution(self, command: str, context: Dict[str, Any]) -> List[RuleViolation]:
        """コマンド実行チェック"""
        violations = []
        
        for rule in self.active_rules.values():
            if rule.rule_type != RuleType.COMMAND_EXECUTION:
                continue
            
            # 必須コマンドチェック
            if rule.category == RuleCategory.CRITICAL:
                for required_cmd in rule.commands:
                    if required_cmd in ['make declare-president', 'python3 scripts/hooks/critical_failure_prevention.py']:
                        if required_cmd not in context.get('executed_commands', []):
                            violation = self._create_violation(
                                rule, 
                                "MISSING_CRITICAL_COMMAND",
                                f"Critical command not executed: {required_cmd}",
                                context
                            )
                            violations.append(violation)
        
        return violations
    
    def check_file_operation(self, file_path: str, operation: str, context: Dict[str, Any]) -> List[RuleViolation]:
        """ファイル操作チェック"""
        violations = []
        
        for rule in self.active_rules.values():
            if rule.rule_type != RuleType.FILE_OPERATION:
                continue
            
            # ファイルパターンチェック
            for pattern in rule.file_patterns:
                if re.match(pattern, file_path):
                    if rule.enforcement_level == RuleEnforcementLevel.BLOCK:
                        violation = self._create_violation(
                            rule,
                            "BLOCKED_FILE_OPERATION", 
                            f"File operation blocked: {operation} on {file_path}",
                            context
                        )
                        violations.append(violation)
        
        return violations
    
    def check_response_format(self, response: str, context: Dict[str, Any]) -> List[RuleViolation]:
        """応答形式チェック"""
        violations = []
        
        for rule in self.active_rules.values():
            if rule.rule_type != RuleType.RESPONSE_FORMAT:
                continue
            
            # 必須パターンチェック
            for pattern in rule.validation_patterns:
                if not re.search(pattern, response):
                    violation = self._create_violation(
                        rule,
                        "INVALID_RESPONSE_FORMAT",
                        f"Response missing required pattern: {pattern}",
                        context
                    )
                    violations.append(violation)
        
        return violations
    
    def validate_session_requirements(self, session_data: Dict[str, Any]) -> List[RuleViolation]:
        """セッション要件バリデーション"""
        violations = []
        
        for rule in self.active_rules.values():
            if rule.rule_type != RuleType.VALIDATION_CHECK:
                continue
            
            # セッション開始時の必須チェック
            if rule.category == RuleCategory.CRITICAL:
                required_checks = ['president_declaration', 'memory_inheritance', 'system_status']
                
                for check in required_checks:
                    if not session_data.get(check, False):
                        violation = self._create_violation(
                            rule,
                            "MISSING_SESSION_REQUIREMENT",
                            f"Missing required session check: {check}",
                            {"session_data": session_data}
                        )
                        violations.append(violation)
        
        return violations
    
    def _create_violation(self, rule: ParsedRule, violation_type: str, 
                         message: str, context: Dict[str, Any]) -> RuleViolation:
        """違反作成"""
        violation = RuleViolation(
            violation_id=f"viol_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.violations_history)}",
            rule_id=rule.rule_id,
            rule_title=rule.title,
            violation_type=violation_type,
            message=message,
            timestamp=datetime.now(),
            context=context,
            severity="CRITICAL" if rule.category == RuleCategory.CRITICAL else "WARNING"
        )
        
        # 違反記録
        with self._lock:
            self.violations_history.append(violation)
        
        # ハンドラー実行
        for handler in self.violation_handlers:
            try:
                handler(violation)
            except Exception as e:
                self.logger.error(f"Violation handler failed: {e}")
        
        return violation
    
    def get_active_violations(self) -> List[RuleViolation]:
        """アクティブ違反取得"""
        with self._lock:
            return [v for v in self.violations_history if not v.resolved]
    
    def resolve_violation(self, violation_id: str) -> bool:
        """違反解決"""
        with self._lock:
            for violation in self.violations_history:
                if violation.violation_id == violation_id:
                    violation.resolved = True
                    return True
        return False
    
    def export_enforcement_data(self) -> Dict[str, Any]:
        """強制実行データエクスポート"""
        with self._lock:
            return {
                "active_rules": {rule_id: rule.to_dict() for rule_id, rule in self.active_rules.items()},
                "violations_summary": {
                    "total_violations": len(self.violations_history),
                    "active_violations": len([v for v in self.violations_history if not v.resolved]),
                    "critical_violations": len([v for v in self.violations_history if v.severity == "CRITICAL" and not v.resolved])
                },
                "recent_violations": [v.to_dict() for v in self.violations_history[-10:]]
            }


class CLAUDEMdIntegrationSystem:
    """CLAUDE.md統合システム"""
    
    def __init__(self, claude_md_path: Path, logger: Optional[logging.Logger] = None):
        self.claude_md_path = claude_md_path
        self.logger = logger or logging.getLogger(__name__)
        
        # コンポーネント
        self.parser = CLAUDEMdParser(self.logger)
        self.enforcement_engine = RuleEnforcementEngine(self.logger)
        
        # 状態
        self.last_parsed_hash: Optional[str] = None
        self.last_parse_time: Optional[datetime] = None
        self.auto_reload = True
        self.reload_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        
        # 初期読み込み
        self.reload_claude_md()
        
        # デフォルト違反ハンドラー
        self.enforcement_engine.add_violation_handler(self._log_violation)
    
    def _log_violation(self, violation: RuleViolation) -> None:
        """違反ログ出力"""
        level = logging.CRITICAL if violation.severity == "CRITICAL" else logging.WARNING
        self.logger.log(level, f"RULE VIOLATION: {violation.message}")
    
    def reload_claude_md(self) -> bool:
        """CLAUDE.md再読み込み"""
        try:
            if not self.claude_md_path.exists():
                self.logger.warning(f"CLAUDE.md not found: {self.claude_md_path}")
                return False
            
            # 解析実行
            parsed_data = self.parser.parse_claude_md(self.claude_md_path)
            
            # ハッシュチェック（変更検出）
            current_hash = parsed_data["content_hash"]
            if current_hash == self.last_parsed_hash:
                self.logger.debug("CLAUDE.md unchanged, skipping reload")
                return True
            
            # ルール読み込み
            rules = [ParsedRule(**rule_data) for rule_data in parsed_data["rules"]]
            self.enforcement_engine.load_rules(rules)
            
            # 状態更新
            self.last_parsed_hash = current_hash
            self.last_parse_time = datetime.now()
            
            self.logger.info(f"CLAUDE.md reloaded: {len(rules)} rules loaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload CLAUDE.md: {e}")
            return False
    
    def start_auto_reload(self, interval_seconds: int = 60) -> None:
        """自動再読み込み開始"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.reload_thread = threading.Thread(
            target=self._auto_reload_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.reload_thread.start()
        self.logger.info("CLAUDE.md auto-reload started")
    
    def stop_auto_reload(self) -> None:
        """自動再読み込み停止"""
        self.is_monitoring = False
        if self.reload_thread:
            self.reload_thread.join(timeout=5)
        self.logger.info("CLAUDE.md auto-reload stopped")
    
    def _auto_reload_loop(self, interval_seconds: int) -> None:
        """自動再読み込みループ"""
        import time
        while self.is_monitoring:
            try:
                self.reload_claude_md()
                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Error in auto-reload loop: {e}")
                time.sleep(5)
    
    def validate_session_start(self, context: Dict[str, Any]) -> List[RuleViolation]:
        """セッション開始バリデーション"""
        return self.enforcement_engine.validate_session_requirements(context)
    
    def check_command(self, command: str, context: Dict[str, Any]) -> List[RuleViolation]:
        """コマンドチェック"""
        return self.enforcement_engine.check_command_execution(command, context)
    
    def check_file_operation(self, file_path: str, operation: str, context: Dict[str, Any]) -> List[RuleViolation]:
        """ファイル操作チェック"""
        return self.enforcement_engine.check_file_operation(file_path, operation, context)
    
    def check_response(self, response: str, context: Dict[str, Any]) -> List[RuleViolation]:
        """応答チェック"""
        return self.enforcement_engine.check_response_format(response, context)
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状況取得"""
        return {
            "claude_md_path": str(self.claude_md_path),
            "last_parse_time": self.last_parse_time.isoformat() if self.last_parse_time else None,
            "last_parsed_hash": self.last_parsed_hash,
            "auto_reload_active": self.is_monitoring,
            "active_rules_count": len(self.enforcement_engine.active_rules),
            "active_violations_count": len(self.enforcement_engine.get_active_violations()),
            "enforcement_data": self.enforcement_engine.export_enforcement_data()
        }