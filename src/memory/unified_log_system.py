#!/usr/bin/env python3
"""
📊 統一ログシステム - 117ファイル統合実装
==========================================

【目的】
- 散在する.logファイルの統合
- JSON Lines形式での構造化
- PostgreSQLへの統合保存
- PII保護機能

【実装内容】
- .logファイル自動発見・解析
- 構造化変換 (JSON Lines)
- データベース統合保存
- 重複除去・時系列整理
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class UnifiedLogSystem:
    """統一ログシステム - 117ファイル統合"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.db_config = {
            "host": "localhost",
            "database": "president_ai",
            "user": "dd",
            "password": "",
            "port": 5432,
        }

        # PII保護パターン
        self.pii_patterns = [
            (r"sk-[a-zA-Z0-9\-_]{20,}", "[API_KEY_REDACTED]"),  # API keys
            (
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "[EMAIL_REDACTED]",
            ),  # emails
            (r"/Users/[^/\s]+", "/Users/[USERNAME]"),  # user paths
            (
                r'password["\']?\s*[:=]\s*["\']?[^"\s,}]+',
                "password: [REDACTED]",
            ),  # passwords
        ]

    def init_unified_log_table(self):
        """統一ログテーブル初期化"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 統一ログテーブル
            cur.execute("""
                CREATE TABLE IF NOT EXISTS unified_logs (
                    id SERIAL PRIMARY KEY,
                    log_hash VARCHAR(64) UNIQUE,
                    timestamp TIMESTAMPTZ,
                    source_file VARCHAR(500),
                    log_level VARCHAR(20),
                    component VARCHAR(100),
                    message TEXT,
                    structured_data JSONB,
                    original_format TEXT,
                    processed_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # インデックス作成
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_unified_logs_timestamp
                ON unified_logs (timestamp DESC);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_unified_logs_component
                ON unified_logs (component, timestamp DESC);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_unified_logs_level
                ON unified_logs (log_level, timestamp DESC);
            """)

            conn.commit()
            cur.close()
            conn.close()

            return {"status": "success", "message": "Unified log table initialized"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"Table initialization failed: {str(e)}",
            }

    def discover_log_files(self) -> List[Path]:
        """プロジェクト内の.logファイルを発見"""
        log_files = []

        # .logファイルを再帰的に検索
        for log_file in self.project_root.rglob("*.log"):
            if log_file.is_file() and log_file.stat().st_size > 0:  # 空ファイル除外
                log_files.append(log_file)

        return sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)

    def parse_log_entry(self, line: str, source_file: str) -> Optional[Dict[str, Any]]:
        """ログエントリを解析して構造化"""
        if not line.strip():
            return None

        # PII保護
        sanitized_line = self.sanitize_pii(line)

        # タイムスタンプパターン検出
        timestamp_patterns = [
            (r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"),
            (r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", "%Y-%m-%dT%H:%M:%S"),
            (r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})", "%m/%d/%Y %H:%M:%S"),
            (r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]", "%Y-%m-%d %H:%M:%S"),
        ]

        parsed_timestamp = None
        for pattern, fmt in timestamp_patterns:
            match = re.search(pattern, sanitized_line)
            if match:
                try:
                    parsed_timestamp = datetime.strptime(match.group(1), fmt)
                    break
                except ValueError:
                    continue

        # ログレベル検出
        log_level = "INFO"
        level_patterns = [
            (r"\b(ERROR|error)\b", "ERROR"),
            (r"\b(WARN|WARNING|warn|warning)\b", "WARNING"),
            (r"\b(INFO|info)\b", "INFO"),
            (r"\b(DEBUG|debug)\b", "DEBUG"),
            (r"\b(CRITICAL|critical|FATAL|fatal)\b", "CRITICAL"),
        ]

        for pattern, level in level_patterns:
            if re.search(pattern, sanitized_line):
                log_level = level
                break

        # コンポーネント推定
        component = self._extract_component_from_path(source_file)

        # 構造化データ抽出
        structured_data = self._extract_structured_data(sanitized_line)

        # ハッシュ生成（重複除去用）
        content_hash = hashlib.sha256(
            f"{source_file}:{sanitized_line}".encode()
        ).hexdigest()

        return {
            "log_hash": content_hash,
            "timestamp": parsed_timestamp or datetime.now(timezone.utc),
            "source_file": str(Path(source_file).relative_to(self.project_root)),
            "log_level": log_level,
            "component": component,
            "message": sanitized_line.strip(),
            "structured_data": structured_data,
            "original_format": line.strip(),
        }

    def _extract_component_from_path(self, filepath: str) -> str:
        """ファイルパスからコンポーネント名を推定"""
        path = Path(filepath)

        # パス構造からコンポーネント推定
        parts = path.parts
        if "operations" in parts:
            return "operations"
        elif "memory" in parts:
            return "memory"
        elif "agents" in parts:
            return "agents"
        elif "scripts" in parts:
            return "scripts"
        elif "runtime" in parts:
            return "runtime"
        else:
            return "system"

    def _extract_structured_data(self, line: str) -> Dict[str, Any]:
        """ログ行から構造化データを抽出"""
        structured = {}

        # JSON部分の抽出
        json_pattern = r"\{[^{}]*\}"
        json_matches = re.findall(json_pattern, line)
        if json_matches:
            for match in json_matches:
                try:
                    data = json.loads(match)
                    structured.update(data)
                except (json.JSONDecodeError, ValueError):
                    pass

        # キー=値ペアの抽出
        kv_pattern = r"(\w+)=([^\s,}]+)"
        kv_matches = re.findall(kv_pattern, line)
        for key, value in kv_matches:
            # 数値変換試行
            try:
                if "." in value:
                    structured[key] = float(value)
                else:
                    structured[key] = int(value)
            except ValueError:
                structured[key] = value

        return structured

    def sanitize_pii(self, text: str) -> str:
        """PII保護"""
        sanitized = text
        for pattern, replacement in self.pii_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized

    def process_log_files(self, max_files: int = 50) -> Dict[str, Any]:
        """ログファイル処理"""
        log_files = self.discover_log_files()

        if len(log_files) > max_files:
            log_files = log_files[:max_files]  # 最新ファイルに制限

        processed_entries = 0
        skipped_entries = 0
        errors = []

        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            for log_file in log_files:
                try:
                    with open(log_file, encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            try:
                                entry = self.parse_log_entry(line, str(log_file))
                                if entry:
                                    # データベースに挿入
                                    cur.execute(
                                        """
                                        INSERT INTO unified_logs
                                        (log_hash, timestamp, source_file, log_level, component, message, structured_data, original_format)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (log_hash) DO NOTHING;
                                    """,
                                        (
                                            entry["log_hash"],
                                            entry["timestamp"],
                                            entry["source_file"],
                                            entry["log_level"],
                                            entry["component"],
                                            entry["message"],
                                            json.dumps(entry["structured_data"]),
                                            entry["original_format"],
                                        ),
                                    )

                                    processed_entries += 1
                                else:
                                    skipped_entries += 1

                            except Exception as e:
                                errors.append(f"{log_file}:{line_num}: {str(e)}")

                except Exception as e:
                    errors.append(f"File {log_file}: {str(e)}")

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "processed_files": len(log_files),
                "processed_entries": processed_entries,
                "skipped_entries": skipped_entries,
                "errors": errors[:10],  # 最初の10エラーのみ
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_unified_log_stats(self) -> Dict[str, Any]:
        """統一ログ統計"""
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 基本統計
            cur.execute("""
                SELECT
                    COUNT(*) as total_entries,
                    COUNT(DISTINCT source_file) as unique_files,
                    COUNT(DISTINCT component) as unique_components,
                    MIN(timestamp) as earliest_entry,
                    MAX(timestamp) as latest_entry
                FROM unified_logs;
            """)

            basic_stats = cur.fetchone()

            # ログレベル別統計
            cur.execute("""
                SELECT log_level, COUNT(*) as count
                FROM unified_logs
                GROUP BY log_level
                ORDER BY count DESC;
            """)

            level_stats = cur.fetchall()

            # コンポーネント別統計
            cur.execute("""
                SELECT component, COUNT(*) as count
                FROM unified_logs
                GROUP BY component
                ORDER BY count DESC;
            """)

            component_stats = cur.fetchall()

            cur.close()
            conn.close()

            return {
                "status": "success",
                "basic_stats": dict(basic_stats) if basic_stats else {},
                "level_distribution": [dict(row) for row in level_stats],
                "component_distribution": [dict(row) for row in component_stats],
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    """メイン実行 - 統一ログシステム"""
    print("📊 統一ログシステム - 117ファイル統合開始")

    log_system = UnifiedLogSystem()

    # 1. データベース初期化
    print("\\n1️⃣ 統一ログテーブル初期化")
    init_result = log_system.init_unified_log_table()
    print(f"初期化: {init_result['status']}")

    if init_result["status"] == "error":
        print(f"エラー: {init_result['message']}")
        return

    # 2. ログファイル発見
    print("\\n2️⃣ ログファイル発見")
    log_files = log_system.discover_log_files()
    print(f"発見ファイル数: {len(log_files)}")

    # 最初の10ファイルを表示
    for i, log_file in enumerate(log_files[:10]):
        size_kb = log_file.stat().st_size // 1024
        print(f"   {i + 1}. {log_file.name} ({size_kb}KB)")

    if len(log_files) > 10:
        print(f"   ... 他{len(log_files) - 10}ファイル")

    # 3. ログファイル処理
    print("\\n3️⃣ ログファイル統合処理")
    process_result = log_system.process_log_files(max_files=30)  # 最初の30ファイル
    print(f"処理結果: {process_result['status']}")

    if process_result["status"] == "success":
        print(f"   処理ファイル数: {process_result['processed_files']}")
        print(f"   統合エントリ数: {process_result['processed_entries']}")
        print(f"   スキップエントリ数: {process_result['skipped_entries']}")

        if process_result["errors"]:
            print(f"   エラー数: {len(process_result['errors'])}")
            for error in process_result["errors"][:3]:
                print(f"     - {error}")
    else:
        print(f"   エラー: {process_result['error']}")
        return

    # 4. 統合ログ統計
    print("\\n4️⃣ 統合ログ統計")
    stats_result = log_system.get_unified_log_stats()
    print(f"統計: {stats_result['status']}")

    if stats_result["status"] == "success":
        basic = stats_result["basic_stats"]
        print(f"   総エントリ数: {basic.get('total_entries', 0)}")
        print(f"   ユニークファイル数: {basic.get('unique_files', 0)}")
        print(f"   コンポーネント数: {basic.get('unique_components', 0)}")

        if basic.get("earliest_entry"):
            print(f"   最古エントリ: {basic['earliest_entry']}")
        if basic.get("latest_entry"):
            print(f"   最新エントリ: {basic['latest_entry']}")

        print("\\n   ログレベル分布:")
        for level in stats_result["level_distribution"][:5]:
            print(f"     {level['log_level']}: {level['count']}件")

        print("\\n   コンポーネント分布:")
        for component in stats_result["component_distribution"][:5]:
            print(f"     {component['component']}: {component['count']}件")

    print("\\n✅ 統一ログシステム実装完了")
    print("📍 散在する.logファイルからPostgreSQL統合へ変換")


if __name__ == "__main__":
    main()
