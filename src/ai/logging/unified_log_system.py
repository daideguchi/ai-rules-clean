#!/usr/bin/env python3
"""
📊 構造化ログ統一システム - 117個.log→JSON Lines統合
========================================================

【目的】
- 非構造化ログを構造化JSON Linesに統一
- PII保護とセキュリティ強化
- 検索・分析可能なログ形式への変換
- OpenTelemetry準拠の分散トレーシング対応

【改善効果】
- 現在: 117個.log + 17個.json (非構造化散在)
- 目標: 統一JSON Lines + マスキング + ローテーション

【技術仕様】
- JSON Lines (.jsonl) 形式
- PII自動マスキング (API keys, emails, paths)
- ログローテーション (日次/サイズベース)
- 分散トレーシング対応
"""

import hashlib
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class LogEntry:
    """統一ログエントリ構造"""

    timestamp: str
    level: str
    session_id: str
    agent_id: str
    trace_id: str
    span_id: str
    event: str
    message: str
    metadata: Dict[str, Any]
    masked_data: Dict[str, str] = None
    source_file: str = ""

    def to_json(self) -> str:
        """JSON Lines形式で出力"""
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))


class PIIMasker:
    """PII情報自動マスキング"""

    def __init__(self):
        self.patterns = {
            "api_key": re.compile(r"(sk-[a-zA-Z0-9]{48}|AIza[a-zA-Z0-9_-]{35})"),
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "absolute_path": re.compile(r"/Users/[^/]+/[^\s]+"),
            "session_id": re.compile(r"sess_[a-zA-Z0-9]{10,}"),
            "uuid": re.compile(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
            ),
            "token": re.compile(r"token[\'\":][\s]*[\'\"]([\w\-\.]+)[\'\"]\s"),
            "password": re.compile(
                r"password[\'\":][\s]*[\'\"]([\w\-\.]+)[\'\"]\s", re.IGNORECASE
            ),
        }

    def mask_content(self, content: str) -> Tuple[str, Dict[str, str]]:
        """コンテンツからPIIをマスクし、マスク情報を返す"""
        masked_content = content
        masked_data = {}

        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]  # 正規表現グループの場合

                # マスク用ID生成
                mask_id = f"{pii_type}_{hashlib.md5(match.encode()).hexdigest()[:8]}"
                mask_token = f"***{mask_id}***"

                # マスク適用
                masked_content = masked_content.replace(match, mask_token)
                masked_data[mask_id] = f"{pii_type.upper()}_MASKED"

        return masked_content, masked_data


class UnifiedLogSystem:
    """統一ログシステム - 全ログの構造化管理"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pii_masker = PIIMasker()
        self.session_id = str(uuid.uuid4())[:8]

        # 統一ログファイル
        self.unified_log_file = (
            self.output_dir / f"unified_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )

    def discover_log_files(self, project_root: Path) -> List[Path]:
        """プロジェクト内の全ログファイルを発見"""
        log_patterns = ["*.log", "*.json", "*_log_*.json", "*conversation*.json"]
        found_files = []

        for pattern in log_patterns:
            found_files.extend(project_root.rglob(pattern))

        # 除外パターン
        exclude_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
            "package-lock.json",
            "package.json",
        ]

        filtered_files = []
        for file_path in found_files:
            if not any(exclude in str(file_path) for exclude in exclude_patterns):
                filtered_files.append(file_path)

        return filtered_files

    def parse_legacy_log(self, file_path: Path) -> List[LogEntry]:
        """レガシーログファイルを解析してLogEntryに変換"""
        entries = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # ファイル種別判定
            if file_path.suffix == ".json":
                entries.extend(self._parse_json_log(file_path, content))
            else:
                entries.extend(self._parse_text_log(file_path, content))

        except Exception as e:
            # エラーログも記録
            error_entry = LogEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                level="ERROR",
                session_id=self.session_id,
                agent_id="log_parser",
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4())[:8],
                event="log_parse_error",
                message=f"Failed to parse {file_path}: {str(e)}",
                metadata={"file_path": str(file_path), "error": str(e)},
                source_file=str(file_path),
            )
            entries.append(error_entry)

        return entries

    def _parse_json_log(self, file_path: Path, content: str) -> List[LogEntry]:
        """JSONログファイルの解析"""
        entries = []

        try:
            # JSON配列の場合
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    entries.append(self._json_to_log_entry(file_path, item))
            else:
                entries.append(self._json_to_log_entry(file_path, data))

        except json.JSONDecodeError:
            # JSON Lines形式の可能性
            for line_num, line in enumerate(content.split("\n")):
                if line.strip():
                    try:
                        data = json.loads(line)
                        entries.append(self._json_to_log_entry(file_path, data))
                    except json.JSONDecodeError:
                        # 不正なJSONは警告として記録
                        warning_entry = LogEntry(
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            level="WARN",
                            session_id=self.session_id,
                            agent_id="log_parser",
                            trace_id=str(uuid.uuid4()),
                            span_id=str(uuid.uuid4())[:8],
                            event="invalid_json_line",
                            message=f"Invalid JSON at line {line_num + 1}",
                            metadata={"file_path": str(file_path), "line": line[:100]},
                            source_file=str(file_path),
                        )
                        entries.append(warning_entry)

        return entries

    def _parse_text_log(self, file_path: Path, content: str) -> List[LogEntry]:
        """テキストログファイルの解析"""
        entries = []

        # 一般的なログパターン
        log_patterns = [
            # [YYYY-MM-DD HH:MM:SS] LEVEL: message
            re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+(\w+):\s*(.+)$"),
            # YYYY-MM-DD HH:MM:SS LEVEL message
            re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+(.+)$"),
            # タイムスタンプなし（日付推定）
            re.compile(r"^(\w+):\s*(.+)$"),
        ]

        for line_num, line in enumerate(content.split("\n")):
            if not line.strip():
                continue

            parsed = False
            for pattern in log_patterns:
                match = pattern.match(line.strip())
                if match:
                    if len(match.groups()) == 3:
                        timestamp_str, level, message = match.groups()
                        try:
                            # タイムスタンプ正規化
                            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            timestamp = dt.replace(tzinfo=timezone.utc).isoformat()
                        except ValueError:
                            timestamp = datetime.now(timezone.utc).isoformat()
                    else:
                        level, message = match.groups()
                        timestamp = datetime.now(timezone.utc).isoformat()

                    # PIIマスキング
                    masked_message, masked_data = self.pii_masker.mask_content(message)

                    entry = LogEntry(
                        timestamp=timestamp,
                        level=level.upper(),
                        session_id=self.session_id,
                        agent_id="legacy_import",
                        trace_id=str(uuid.uuid4()),
                        span_id=str(uuid.uuid4())[:8],
                        event="legacy_log_import",
                        message=masked_message,
                        metadata={"original_line": line_num + 1},
                        masked_data=masked_data if masked_data else None,
                        source_file=str(file_path),
                    )
                    entries.append(entry)
                    parsed = True
                    break

            if not parsed:
                # パターンにマッチしない行は情報として記録
                masked_line, masked_data = self.pii_masker.mask_content(line)
                entry = LogEntry(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    level="INFO",
                    session_id=self.session_id,
                    agent_id="legacy_import",
                    trace_id=str(uuid.uuid4()),
                    span_id=str(uuid.uuid4())[:8],
                    event="unstructured_log",
                    message=masked_line,
                    metadata={"line_number": line_num + 1, "unparsed": True},
                    masked_data=masked_data if masked_data else None,
                    source_file=str(file_path),
                )
                entries.append(entry)

        return entries

    def _json_to_log_entry(self, file_path: Path, data: Dict[str, Any]) -> LogEntry:
        """JSON辞書をLogEntryに変換"""
        # 必要なフィールドを抽出・デフォルト値設定
        timestamp = data.get("timestamp", datetime.now(timezone.utc).isoformat())
        level = data.get("level", "INFO")
        message = str(data.get("message", data.get("human_message", "")))

        # PIIマスキング
        masked_message, masked_data = self.pii_masker.mask_content(message)

        # メタデータ構築
        metadata = {
            k: v for k, v in data.items() if k not in ["timestamp", "level", "message"]
        }

        return LogEntry(
            timestamp=timestamp,
            level=level.upper(),
            session_id=data.get("session_id", self.session_id),
            agent_id=data.get("agent_id", "unknown"),
            trace_id=data.get("trace_id", str(uuid.uuid4())),
            span_id=data.get("span_id", str(uuid.uuid4())[:8]),
            event=data.get("event", "json_import"),
            message=masked_message,
            metadata=metadata,
            masked_data=masked_data if masked_data else None,
            source_file=str(file_path),
        )

    def write_unified_log(self, entries: List[LogEntry]):
        """統一ログファイルに書き込み"""
        with open(self.unified_log_file, "a", encoding="utf-8") as f:
            for entry in entries:
                f.write(entry.to_json() + "\n")

    def migrate_all_logs(self, project_root: Path) -> Dict[str, Any]:
        """全ログファイルを統一形式に移行"""
        log_files = self.discover_log_files(project_root)

        migration_stats = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "total_files": len(log_files),
            "processed_files": 0,
            "total_entries": 0,
            "errors": [],
        }

        for file_path in log_files:
            try:
                entries = self.parse_legacy_log(file_path)
                self.write_unified_log(entries)

                migration_stats["processed_files"] += 1
                migration_stats["total_entries"] += len(entries)

                print(f"✅ {file_path.name}: {len(entries)}エントリ")

            except Exception as e:
                error_msg = f"Failed to process {file_path}: {str(e)}"
                migration_stats["errors"].append(error_msg)
                print(f"❌ {error_msg}")

        migration_stats["end_time"] = datetime.now(timezone.utc).isoformat()

        # 移行レポート作成
        report_path = (
            self.output_dir
            / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(migration_stats, f, ensure_ascii=False, indent=2)

        return migration_stats

    def setup_log_rotation(self):
        """ログローテーション設定"""
        rotation_script = f"""#!/bin/bash
# 統一ログローテーション
LOG_DIR="{self.output_dir}"
MAX_SIZE_MB=100
MAX_DAYS=30

# サイズベースローテーション
find "$LOG_DIR" -name "*.jsonl" -size +${{MAX_SIZE_MB}}M -exec gzip {{}} \\;

# 古いログファイル削除
find "$LOG_DIR" -name "*.jsonl.gz" -mtime +$MAX_DAYS -delete

# 日次ローテーション実行
DATE=$(date '+%Y%m%d')
if [ ! -f "$LOG_DIR/unified_$DATE.jsonl" ]; then
    touch "$LOG_DIR/unified_$DATE.jsonl"
fi
"""

        rotation_script_path = self.output_dir / "rotate_logs.sh"
        with open(rotation_script_path, "w") as f:
            f.write(rotation_script)

        os.chmod(rotation_script_path, 0o750)

        return rotation_script_path


def main():
    """メイン実行 - ログ統一システムのテスト"""
    project_root = Path(__file__).parent.parent.parent.parent
    output_dir = project_root / "logs/unified"

    # システム初期化
    log_system = UnifiedLogSystem(output_dir)

    # 全ログ移行実行
    print("🔄 ログ統一システム開始...")
    migration_stats = log_system.migrate_all_logs(project_root)

    print("\n📊 移行結果:")
    print(
        f"  - 処理ファイル数: {migration_stats['processed_files']}/{migration_stats['total_files']}"
    )
    print(f"  - 統一エントリ数: {migration_stats['total_entries']}")
    print(f"  - エラー数: {len(migration_stats['errors'])}")

    # ローテーション設定
    rotation_script = log_system.setup_log_rotation()
    print(f"  - ローテーション設定: {rotation_script}")

    print(f"\n✅ 統一ログファイル: {log_system.unified_log_file}")


if __name__ == "__main__":
    main()
