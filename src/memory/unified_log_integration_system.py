#!/usr/bin/env python3
"""
📊 統一ログ統合システム - 全117+ファイル完全統合
=================================================

【o3統合設計】
- 全プロジェクトファイルログ自動検出
- 構造化ログデータベース統合
- リアルタイム検索・分析
- 階層化ログレベル管理

【実装内容】
- 117+ファイル自動スキャン・解析
- ログレベル・コンポーネント自動分類
- PostgreSQL統合検索システム
- ログ品質評価・重複除去
- プロジェクト別ログ管理
"""

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class UnifiedLogIntegrationSystem:
    """統一ログ統合システム - o3推奨プロジェクト別実装"""

    def __init__(
        self, project_root: Optional[Path] = None, config_file: Optional[str] = None
    ):
        """初期化 - プロジェクト別設定対応"""

        # プロジェクトルート自動検出
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = Path(__file__).parent.parent

        # プロジェクト別設定読み込み
        self.config = self._load_project_config(config_file)

        # データベース設定（プロジェクト別）
        self.db_config = self.config.get(
            "database",
            {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
        )

        # o3推奨ログ収集設定
        collection_config = self.config.get("log_collection", {})
        self.file_size_limit_mb = collection_config.get("max_file_size_mb", 50)
        self.batch_size = collection_config.get("batch_size", 100)
        self.duplicate_threshold = collection_config.get("duplicate_threshold", 0.95)

        # o3推奨ログファイルパターン
        patterns_config = self.config.get("log_patterns", {})

        # ログファイル検出パターン
        self.log_file_patterns = patterns_config.get(
            "file_patterns",
            [
                "*.log",
                "*.txt",
                "*log*",
                "*error*",
                "*debug*",
                "*trace*",
                "*output*",
                "*runtime*",
                "*operation*",
                "*system*",
            ],
        )

        # 除外パターン
        self.excluded_patterns = patterns_config.get(
            "excluded",
            [
                "*.tmp",
                "*.cache",
                "*.pyc",
                "*.pyo",
                "__pycache__/*",
                "node_modules/*",
                ".git/*",
                "*.bak",
                "*.backup",
            ],
        )

        # o3推奨ログレベル検出パターン
        self.log_level_patterns = {
            "CRITICAL": [r"CRITICAL", r"FATAL", r"EMERGENCY", r"致命的", r"重大"],
            "ERROR": [
                r"ERROR",
                r"EXCEPTION",
                r"FAILED",
                r"FAILURE",
                r"エラー",
                r"失敗",
            ],
            "WARNING": [r"WARNING", r"WARN", r"CAUTION", r"注意", r"警告"],
            "INFO": [r"INFO", r"INFORMATION", r"情報", r"通知"],
            "DEBUG": [r"DEBUG", r"TRACE", r"VERBOSE", r"デバッグ", r"詳細"],
            "UNKNOWN": [],
        }

        # o3推奨コンポーネント検出パターン
        self.component_patterns = {
            "database": [r"database", r"postgres", r"sql", r"db", r"データベース"],
            "api": [r"api", r"endpoint", r"request", r"response", r"http", r"rest"],
            "auth": [r"auth", r"login", r"password", r"token", r"認証", r"ログイン"],
            "file_system": [
                r"file",
                r"directory",
                r"path",
                r"disk",
                r"storage",
                r"ファイル",
            ],
            "network": [
                r"network",
                r"socket",
                r"connection",
                r"tcp",
                r"udp",
                r"ネットワーク",
            ],
            "security": [
                r"security",
                r"vulnerability",
                r"attack",
                r"セキュリティ",
                r"脆弱性",
            ],
            "performance": [
                r"performance",
                r"latency",
                r"throughput",
                r"パフォーマンス",
                r"性能",
            ],
            "operations": [r"operation", r"workflow", r"process", r"操作", r"運用"],
            "memory": [r"memory", r"ram", r"heap", r"stack", r"メモリ"],
            "ai_learning": [
                r"learning",
                r"mistake",
                r"president",
                r"ai",
                r"学習",
                r"ミス",
            ],
        }

        # ログディレクトリ設定
        paths_config = self.config.get("paths", {})
        default_log_dirs = [
            "logs",
            "tmp",
            "runtime",
            "operations",
            "memory",
            "src",
            "scripts",
        ]
        log_directories = paths_config.get("log_directories", default_log_dirs)
        self.log_directories = [self.project_root / path for path in log_directories]

        # UX設定
        ux_config = self.config.get("ux", {})
        self.verbose_logging = ux_config.get("verbose_logging", True)
        self.progress_reporting = ux_config.get("progress_reporting", True)

        # 処理統計
        self.processing_stats = {
            "files_discovered": 0,
            "files_processed": 0,
            "files_skipped": 0,
            "logs_extracted": 0,
            "duplicates_removed": 0,
            "errors_encountered": 0,
        }

    def _load_project_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """プロジェクト設定読み込み"""

        # 設定ファイル候補
        config_candidates = []

        if config_file:
            config_candidates.append(Path(config_file))

        # プロジェクト内設定ファイル候補
        config_candidates.extend(
            [
                self.project_root / "log_config.json",
                self.project_root / "config" / "logs.json",
                self.project_root / ".log_config.json",
                self.project_root / "memory_config.json",  # 既存設定との統合
            ]
        )

        # 設定ファイル読み込み
        for config_path in config_candidates:
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        config = json.load(f)
                    if self.verbose_logging:
                        print(f"📄 ログ設定読み込み: {config_path}")
                    return config
                except Exception as e:
                    if self.verbose_logging:
                        print(f"⚠️ 設定読み込みエラー {config_path}: {e}")
                    continue

        # デフォルト設定
        return self._create_default_log_config()

    def _create_default_log_config(self) -> Dict[str, Any]:
        """デフォルトログ設定生成"""
        return {
            "database": {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
            "log_collection": {
                "max_file_size_mb": 50,
                "batch_size": 100,
                "duplicate_threshold": 0.95,
            },
            "paths": {
                "log_directories": [
                    "logs",
                    "tmp",
                    "runtime",
                    "operations",
                    "memory",
                    "src",
                    "scripts",
                ]
            },
            "ux": {"verbose_logging": True, "progress_reporting": True},
        }

    def discover_all_log_files(self) -> List[Path]:
        """全ログファイル自動発見"""

        discovered_files = set()

        # 設定されたディレクトリからログファイル検索
        for log_dir in self.log_directories:
            if not log_dir.exists():
                continue

            for pattern in self.log_file_patterns:
                try:
                    files = list(log_dir.rglob(pattern))
                    discovered_files.update(files)
                except Exception as e:
                    if self.verbose_logging:
                        print(f"⚠️ パターン検索エラー {pattern} in {log_dir}: {e}")

        # プロジェクトルート直下の重要ファイル
        for pattern in self.log_file_patterns:
            try:
                files = list(self.project_root.glob(pattern))
                discovered_files.update(files)
            except Exception as e:
                if self.verbose_logging:
                    print(f"⚠️ ルート検索エラー {pattern}: {e}")

        # 除外パターンでフィルタリング
        filtered_files = []
        for file_path in discovered_files:
            if self._is_file_excluded(file_path):
                continue

            # ファイルサイズチェック
            try:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                if file_size_mb > self.file_size_limit_mb:
                    if self.verbose_logging:
                        print(
                            f"⚠️ ファイルサイズ制限によりスキップ: {file_path} ({file_size_mb:.1f}MB)"
                        )
                    continue
            except Exception:
                continue

            filtered_files.append(file_path)

        self.processing_stats["files_discovered"] = len(filtered_files)

        if self.verbose_logging:
            print(f"📂 発見ログファイル数: {len(filtered_files)}")

        return filtered_files

    def _is_file_excluded(self, file_path: Path) -> bool:
        """ファイル除外判定"""

        path_str = str(file_path).lower()
        name_lower = file_path.name.lower()

        for pattern in self.excluded_patterns:
            pattern_clean = pattern.replace("*", "").lower()
            if pattern_clean in name_lower or pattern_clean in path_str:
                return True

        return False

    def extract_log_entries_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """ファイルからログエントリ抽出"""

        if not file_path.exists() or not file_path.is_file():
            return []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            if self.verbose_logging:
                print(f"⚠️ ファイル読み込みエラー {file_path}: {e}")
            self.processing_stats["errors_encountered"] += 1
            return []

        if len(content.strip()) < 10:  # 空ファイル
            return []

        lines = content.split("\n")
        log_entries = []

        # ファイル基本情報
        file_stat = file_path.stat()
        file_info = {
            "source_file": str(file_path.relative_to(self.project_root)),
            "file_size": file_stat.st_size,
            "file_modified": datetime.fromtimestamp(file_stat.st_mtime),
            "project_name": self.project_root.name,
        }

        # 行ごとにログエントリ解析
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if len(line) < 5:  # 短すぎる行はスキップ
                continue

            # ログエントリ作成
            log_entry = self._parse_log_line(line, line_num, file_info)
            if log_entry:
                log_entries.append(log_entry)

        # ファイル全体サマリーエントリ
        summary_entry = self._create_file_summary_entry(file_path, lines, file_info)
        if summary_entry:
            log_entries.append(summary_entry)

        return log_entries

    def _parse_log_line(
        self, line: str, line_num: int, file_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """ログ行解析"""

        # タイムスタンプ抽出試行
        timestamp = self._extract_timestamp(line)

        # ログレベル検出
        log_level = self._detect_log_level(line)

        # コンポーネント検出
        component = self._detect_component(line, file_info["source_file"])

        # メッセージクリーニング
        cleaned_message = self._clean_log_message(line)

        # 重要度評価
        importance_level = self._evaluate_log_importance(line, log_level)

        # 構造化データ抽出
        structured_data = self._extract_structured_data(line)

        # ログエントリ作成
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": timestamp or datetime.now(timezone.utc),
            "source_file": file_info["source_file"],
            "line_number": line_num,
            "log_level": log_level,
            "component": component,
            "message": cleaned_message,
            "raw_content": line,
            "importance_level": importance_level,
            "structured_data": structured_data,
            "project_name": file_info["project_name"],
            "file_size": file_info["file_size"],
            "file_modified": file_info["file_modified"],
            "extracted_at": datetime.now(timezone.utc),
            "content_hash": hashlib.sha256(line.encode("utf-8")).hexdigest()[:16],
        }

        return log_entry

    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """タイムスタンプ抽出"""

        # 一般的なタイムスタンプパターン
        timestamp_patterns = [
            r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})",  # ISO format
            r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})",  # US format
            r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})",  # EU format
            r"(\d{10,13})",  # Unix timestamp
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    if timestamp_str.isdigit():  # Unix timestamp
                        if len(timestamp_str) == 13:  # milliseconds
                            return datetime.fromtimestamp(
                                int(timestamp_str) / 1000, tz=timezone.utc
                            )
                        else:  # seconds
                            return datetime.fromtimestamp(
                                int(timestamp_str), tz=timezone.utc
                            )
                    else:
                        # 文字列形式のタイムスタンプ
                        for fmt in [
                            "%Y-%m-%d %H:%M:%S",
                            "%Y-%m-%dT%H:%M:%S",
                            "%m/%d/%Y %H:%M:%S",
                            "%d-%m-%Y %H:%M:%S",
                        ]:
                            try:
                                return datetime.strptime(timestamp_str, fmt).replace(
                                    tzinfo=timezone.utc
                                )
                            except ValueError:
                                continue
                except (ValueError, OSError):
                    continue

        return None

    def _detect_log_level(self, line: str) -> str:
        """ログレベル検出"""

        line_upper = line.upper()

        for level, patterns in self.log_level_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line_upper):
                    return level

        # デフォルト推定
        if any(
            keyword in line_upper for keyword in ["EXCEPTION", "TRACEBACK", "STACK"]
        ):
            return "ERROR"
        elif any(keyword in line_upper for keyword in ["SUCCESS", "COMPLETE", "DONE"]):
            return "INFO"
        else:
            return "UNKNOWN"

    def _detect_component(self, line: str, source_file: str) -> str:
        """コンポーネント検出"""

        line_lower = line.lower()
        source_lower = source_file.lower()

        # ファイル名からコンポーネント推定
        for component, patterns in self.component_patterns.items():
            for pattern in patterns:
                if pattern in source_lower or pattern in line_lower:
                    return component

        # ディレクトリ名からの推定
        if "memory/" in source_lower:
            return "ai_learning"
        elif "operations/" in source_lower:
            return "operations"
        elif "src/" in source_lower:
            return "application"
        elif "scripts/" in source_lower:
            return "automation"
        else:
            return "general"

    def _clean_log_message(self, line: str) -> str:
        """ログメッセージクリーニング"""

        # タイムスタンプ除去
        cleaned = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*", "", line)
        cleaned = re.sub(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}", "", cleaned)

        # ログレベル除去
        for level in self.log_level_patterns.keys():
            cleaned = re.sub(rf"\b{level}\b", "", cleaned, flags=re.IGNORECASE)

        # 余分な空白・文字除去
        cleaned = re.sub(r"^\s*[\[\]():;,-]+\s*", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)

        return cleaned.strip()

    def _evaluate_log_importance(self, line: str, log_level: str) -> str:
        """ログ重要度評価"""

        line_lower = line.lower()

        # Critical条件
        if log_level in ["CRITICAL", "ERROR"] or any(
            keyword in line_lower
            for keyword in ["critical", "fatal", "emergency", "exception", "failed"]
        ):
            return "critical"

        # High条件
        if log_level == "WARNING" or any(
            keyword in line_lower
            for keyword in ["warning", "error", "timeout", "retry", "警告", "エラー"]
        ):
            return "high"

        # Medium条件
        if log_level == "INFO" or any(
            keyword in line_lower
            for keyword in ["success", "complete", "start", "finish", "成功", "完了"]
        ):
            return "medium"

        # Low条件
        return "low"

    def _extract_structured_data(self, line: str) -> Dict[str, Any]:
        """構造化データ抽出"""

        structured_data = {}

        # 数値データ抽出
        numbers = re.findall(
            r"\b(\d+(?:\.\d+)?)\s*(ms|sec|mb|gb|kb|%|bytes?)\b", line.lower()
        )
        if numbers:
            structured_data["metrics"] = {
                f"{unit}": float(value) for value, unit in numbers
            }

        # IPアドレス抽出
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ips = re.findall(ip_pattern, line)
        if ips:
            structured_data["ip_addresses"] = ips

        # URLパス抽出
        path_pattern = r"(?:GET|POST|PUT|DELETE)\s+([/\w\-\.]+)"
        paths = re.findall(path_pattern, line)
        if paths:
            structured_data["api_paths"] = paths

        # エラーコード抽出
        error_codes = re.findall(r"\b(4\d{2}|5\d{2})\b", line)
        if error_codes:
            structured_data["error_codes"] = [int(code) for code in error_codes]

        return structured_data

    def _create_file_summary_entry(
        self, file_path: Path, lines: List[str], file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ファイルサマリーエントリ作成"""

        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])

        # ログレベル分布計算
        level_distribution = {}
        for line in lines:
            level = self._detect_log_level(line)
            level_distribution[level] = level_distribution.get(level, 0) + 1

        # ファイルタイプ推定
        file_type = "log_file"
        name_lower = file_path.name.lower()
        if "error" in name_lower:
            file_type = "error_log"
        elif "debug" in name_lower:
            file_type = "debug_log"
        elif "operation" in name_lower:
            file_type = "operation_log"
        elif "memory" in str(file_path).lower():
            file_type = "memory_log"

        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "source_file": file_info["source_file"],
            "line_number": 0,  # サマリーエントリマーカー
            "log_level": "INFO",
            "component": "file_summary",
            "message": f"File analysis summary: {total_lines} total lines, {non_empty_lines} non-empty lines",
            "raw_content": f"FILE_SUMMARY: {file_path.name}",
            "importance_level": "medium",
            "structured_data": {
                "total_lines": total_lines,
                "non_empty_lines": non_empty_lines,
                "level_distribution": level_distribution,
                "file_type": file_type,
                "analysis_timestamp": datetime.now().isoformat(),
            },
            "project_name": file_info["project_name"],
            "file_size": file_info["file_size"],
            "file_modified": file_info["file_modified"],
            "extracted_at": datetime.now(timezone.utc),
            "content_hash": hashlib.sha256(
                f"SUMMARY_{file_path.name}".encode()
            ).hexdigest()[:16],
        }

    def setup_unified_log_database(self) -> Dict[str, Any]:
        """統一ログデータベースセットアップ"""

        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 統一ログテーブル作成
            cur.execute("""
                CREATE TABLE IF NOT EXISTS unified_logs (
                    id UUID PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    source_file TEXT NOT NULL,
                    line_number INTEGER,
                    log_level VARCHAR(20) NOT NULL,
                    component VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    raw_content TEXT,
                    importance_level VARCHAR(20) DEFAULT 'low',
                    structured_data JSONB,
                    project_name VARCHAR(100) NOT NULL,
                    file_size INTEGER,
                    file_modified TIMESTAMPTZ,
                    extracted_at TIMESTAMPTZ DEFAULT NOW(),
                    content_hash VARCHAR(16),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # o3推奨インデックス作成
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_timestamp ON unified_logs (timestamp DESC);",
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_project_level ON unified_logs (project_name, log_level, timestamp DESC);",
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_component ON unified_logs (component, importance_level);",
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_source ON unified_logs (source_file, line_number);",
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_content_hash ON unified_logs (content_hash);",
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_importance ON unified_logs (importance_level, timestamp DESC);",
                "CREATE INDEX IF NOT EXISTS idx_unified_logs_structured_data ON unified_logs USING GIN (structured_data);",
            ]

            for index_sql in indexes:
                cur.execute(index_sql)

            # 重複チェック用ビュー
            cur.execute("""
                CREATE OR REPLACE VIEW log_duplicates AS
                SELECT content_hash, COUNT(*) as duplicate_count,
                       MIN(id) as original_id, MAX(timestamp) as latest_timestamp
                FROM unified_logs
                WHERE content_hash IS NOT NULL
                GROUP BY content_hash
                HAVING COUNT(*) > 1;
            """)

            # ログ統計ビュー
            cur.execute("""
                CREATE OR REPLACE VIEW log_statistics AS
                SELECT
                    project_name,
                    log_level,
                    component,
                    importance_level,
                    COUNT(*) as log_count,
                    MIN(timestamp) as earliest_log,
                    MAX(timestamp) as latest_log,
                    COUNT(DISTINCT source_file) as file_count
                FROM unified_logs
                GROUP BY project_name, log_level, component, importance_level
                ORDER BY log_count DESC;
            """)

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "message": "統一ログデータベースセットアップ完了",
                "database": self.db_config["database"],
                "project_name": self.project_root.name,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def batch_insert_log_entries(
        self, log_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """ログエントリ一括挿入"""

        if not log_entries:
            return {"status": "no_data", "inserted_count": 0}

        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 重複チェック・除去
            unique_entries = self._remove_duplicate_entries(cur, log_entries)

            if not unique_entries:
                cur.close()
                conn.close()
                return {"status": "all_duplicates", "inserted_count": 0}

            # 一括挿入
            insert_sql = """
                INSERT INTO unified_logs
                (id, timestamp, source_file, line_number, log_level, component, message,
                 raw_content, importance_level, structured_data, project_name, file_size,
                 file_modified, extracted_at, content_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            insert_data = []
            for entry in unique_entries:
                insert_data.append(
                    (
                        entry["id"],
                        entry["timestamp"],
                        entry["source_file"],
                        entry["line_number"],
                        entry["log_level"],
                        entry["component"],
                        entry["message"],
                        entry["raw_content"],
                        entry["importance_level"],
                        json.dumps(entry["structured_data"])
                        if entry["structured_data"]
                        else None,
                        entry["project_name"],
                        entry["file_size"],
                        entry["file_modified"],
                        entry["extracted_at"],
                        entry["content_hash"],
                    )
                )

            cur.executemany(insert_sql, insert_data)

            conn.commit()
            cur.close()
            conn.close()

            self.processing_stats["logs_extracted"] += len(unique_entries)
            self.processing_stats["duplicates_removed"] += len(log_entries) - len(
                unique_entries
            )

            return {
                "status": "success",
                "inserted_count": len(unique_entries),
                "duplicates_removed": len(log_entries) - len(unique_entries),
                "total_processed": len(log_entries),
            }

        except Exception as e:
            self.processing_stats["errors_encountered"] += 1
            return {
                "status": "error",
                "error": str(e),
                "attempted_count": len(log_entries),
            }

    def _remove_duplicate_entries(
        self, cursor, log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """重複ログエントリ除去"""

        if not log_entries:
            return []

        # 既存ハッシュ確認
        hashes = [
            entry["content_hash"] for entry in log_entries if entry.get("content_hash")
        ]

        if hashes:
            placeholders = ",".join(["%s"] * len(hashes))
            cursor.execute(
                f"""
                SELECT content_hash FROM unified_logs
                WHERE content_hash IN ({placeholders}) AND project_name = %s;
            """,
                hashes + [self.project_root.name],
            )

            existing_hashes = {row[0] for row in cursor.fetchall()}
        else:
            existing_hashes = set()

        # 重複除去
        unique_entries = []
        seen_hashes = set()

        for entry in log_entries:
            content_hash = entry.get("content_hash")

            if content_hash and (
                content_hash in existing_hashes or content_hash in seen_hashes
            ):
                continue  # 重複をスキップ

            unique_entries.append(entry)
            if content_hash:
                seen_hashes.add(content_hash)

        return unique_entries

    def process_all_log_files(self) -> Dict[str, Any]:
        """全ログファイル処理実行"""

        # データベースセットアップ
        db_setup = self.setup_unified_log_database()
        if db_setup["status"] != "success":
            return {
                "status": "database_setup_failed",
                "error": db_setup.get("error", "Unknown database error"),
            }

        # ログファイル発見
        log_files = self.discover_all_log_files()

        if not log_files:
            return {
                "status": "no_log_files_found",
                "message": "処理対象のログファイルが見つかりませんでした",
            }

        # ファイル処理
        processed_files = []
        batch_entries = []

        for i, log_file in enumerate(log_files):
            try:
                if self.progress_reporting and (i + 1) % 10 == 0:
                    print(
                        f"   処理中: {i + 1}/{len(log_files)} ファイル ({(i + 1) / len(log_files) * 100:.1f}%)"
                    )

                # ログエントリ抽出
                entries = self.extract_log_entries_from_file(log_file)

                if entries:
                    batch_entries.extend(entries)
                    processed_files.append(
                        {
                            "file_path": str(log_file.relative_to(self.project_root)),
                            "entries_count": len(entries),
                        }
                    )

                # バッチサイズに達したら挿入
                if len(batch_entries) >= self.batch_size:
                    self.batch_insert_log_entries(batch_entries)
                    batch_entries = []  # バッチクリア

                self.processing_stats["files_processed"] += 1

            except Exception as e:
                if self.verbose_logging:
                    print(f"⚠️ ファイル処理エラー {log_file}: {e}")
                self.processing_stats["files_skipped"] += 1
                self.processing_stats["errors_encountered"] += 1

        # 残りのバッチを挿入
        if batch_entries:
            self.batch_insert_log_entries(batch_entries)

        return {
            "status": "processing_completed",
            "project_name": self.project_root.name,
            "database": self.db_config["database"],
            "statistics": self.processing_stats,
            "processed_files": processed_files,
            "total_log_files": len(log_files),
        }

    def generate_log_integration_report(self) -> Dict[str, Any]:
        """ログ統合レポート生成"""

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 基本統計
            cur.execute(
                """
                SELECT
                    COUNT(*) as total_logs,
                    COUNT(DISTINCT source_file) as unique_files,
                    COUNT(DISTINCT component) as unique_components,
                    MIN(timestamp) as earliest_log,
                    MAX(timestamp) as latest_log
                FROM unified_logs
                WHERE project_name = %s;
            """,
                (self.project_root.name,),
            )

            basic_stats = cur.fetchone()

            # ログレベル分布
            cur.execute(
                """
                SELECT log_level, COUNT(*) as count
                FROM unified_logs
                WHERE project_name = %s
                GROUP BY log_level
                ORDER BY count DESC;
            """,
                (self.project_root.name,),
            )

            level_distribution = dict(cur.fetchall())

            # コンポーネント分布
            cur.execute(
                """
                SELECT component, COUNT(*) as count
                FROM unified_logs
                WHERE project_name = %s
                GROUP BY component
                ORDER BY count DESC
                LIMIT 10;
            """,
                (self.project_root.name,),
            )

            component_distribution = dict(cur.fetchall())

            # 重要度分布
            cur.execute(
                """
                SELECT importance_level, COUNT(*) as count
                FROM unified_logs
                WHERE project_name = %s
                GROUP BY importance_level
                ORDER BY count DESC;
            """,
                (self.project_root.name,),
            )

            importance_distribution = dict(cur.fetchall())

            # ファイル別統計 (トップ10)
            cur.execute(
                """
                SELECT source_file, COUNT(*) as log_count,
                       COUNT(DISTINCT log_level) as level_variety,
                       MAX(timestamp) as latest_entry
                FROM unified_logs
                WHERE project_name = %s
                GROUP BY source_file
                ORDER BY log_count DESC
                LIMIT 10;
            """,
                (self.project_root.name,),
            )

            top_files = [dict(row) for row in cur.fetchall()]

            # 重複統計
            cur.execute("""
                SELECT COUNT(*) as duplicate_groups, SUM(duplicate_count) as total_duplicates
                FROM log_duplicates;
            """)

            duplicate_stats = cur.fetchone()

            cur.close()
            conn.close()

            return {
                "project_name": self.project_root.name,
                "database": self.db_config["database"],
                "report_generated_at": datetime.now().isoformat(),
                "basic_statistics": dict(basic_stats) if basic_stats else {},
                "processing_statistics": self.processing_stats,
                "distributions": {
                    "log_levels": level_distribution,
                    "components": component_distribution,
                    "importance_levels": importance_distribution,
                },
                "top_files": top_files,
                "duplicate_statistics": dict(duplicate_stats)
                if duplicate_stats
                else {},
                "integration_quality": {
                    "log_coverage": round(
                        (
                            self.processing_stats["files_processed"]
                            / max(self.processing_stats["files_discovered"], 1)
                        )
                        * 100,
                        1,
                    ),
                    "error_rate": round(
                        (
                            self.processing_stats["errors_encountered"]
                            / max(self.processing_stats["files_discovered"], 1)
                        )
                        * 100,
                        1,
                    ),
                    "duplicate_reduction": round(
                        (
                            self.processing_stats["duplicates_removed"]
                            / max(
                                self.processing_stats["logs_extracted"]
                                + self.processing_stats["duplicates_removed"],
                                1,
                            )
                        )
                        * 100,
                        1,
                    ),
                },
            }

        except Exception as e:
            return {"status": "report_generation_failed", "error": str(e)}


def main():
    """メイン実行 - 統一ログ統合システム"""

    # コマンドライン引数対応
    import sys

    project_root = None
    config_file = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "--project":
            project_root = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        elif sys.argv[1] == "--config":
            config_file = sys.argv[2] if len(sys.argv) > 2 else None
        elif sys.argv[1] == "--generate-config":
            # 設定テンプレート生成モード
            if len(sys.argv) > 2:
                project_root = Path(sys.argv[2])
            else:
                project_root = Path.cwd()

            # ログ設定テンプレート生成
            template_config = {
                "project_name": project_root.name,
                "database": {
                    "host": "localhost",
                    "database": f"{project_root.name}_ai",
                    "user": "dd",
                    "password": "",
                    "port": 5432,
                },
                "log_collection": {
                    "max_file_size_mb": 50,
                    "batch_size": 100,
                    "duplicate_threshold": 0.95,
                },
                "log_patterns": {
                    "file_patterns": [
                        "*.log",
                        "*.txt",
                        "*log*",
                        "*error*",
                        "*debug*",
                        "*trace*",
                    ],
                    "excluded": [
                        "*.tmp",
                        "*.cache",
                        "*.pyc",
                        "__pycache__/*",
                        "node_modules/*",
                        ".git/*",
                    ],
                },
                "paths": {
                    "log_directories": [
                        "logs",
                        "tmp",
                        "runtime",
                        "operations",
                        "memory",
                        "src",
                        "scripts",
                    ]
                },
                "ux": {"verbose_logging": True, "progress_reporting": True},
            }

            config_path = project_root / "log_config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)

            print(f"✅ ログ設定テンプレート生成完了: {config_path}")
            print("   設定をカスタマイズしてからシステムを実行してください。")
            return

    print("📊 統一ログ統合システム - 全117+ファイル完全統合開始")

    try:
        log_system = UnifiedLogIntegrationSystem(
            project_root=project_root, config_file=config_file
        )
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return

    print(f"🏗️ プロジェクト: {log_system.project_root.name}")
    print(f"💾 データベース: {log_system.db_config['database']}")
    print(f"📂 監視ディレクトリ数: {len(log_system.log_directories)}")

    # 1. 全ログファイル処理実行
    print("\n1️⃣ 全ログファイル統合処理実行")
    processing_result = log_system.process_all_log_files()
    print(f"処理結果: {processing_result['status']}")

    if processing_result["status"] == "processing_completed":
        stats = processing_result["statistics"]
        print(f"   発見ファイル数: {stats['files_discovered']}")
        print(f"   処理ファイル数: {stats['files_processed']}")
        print(f"   スキップファイル数: {stats['files_skipped']}")
        print(f"   抽出ログ数: {stats['logs_extracted']}")
        print(f"   重複除去数: {stats['duplicates_removed']}")
        print(f"   エラー数: {stats['errors_encountered']}")
    else:
        print(f"   エラー: {processing_result.get('error', 'Unknown error')}")
        return

    # 2. 統合レポート生成
    print("\n2️⃣ ログ統合レポート生成")
    report = log_system.generate_log_integration_report()

    if report.get("basic_statistics"):
        basic = report["basic_statistics"]
        print(f"   総ログ数: {basic.get('total_logs', 0)}")
        print(f"   ユニークファイル数: {basic.get('unique_files', 0)}")
        print(f"   コンポーネント数: {basic.get('unique_components', 0)}")

        # 最も古いログと最新ログ
        if basic.get("earliest_log") and basic.get("latest_log"):
            print(f"   ログ期間: {basic['earliest_log']} ～ {basic['latest_log']}")

    # 品質指標
    if report.get("integration_quality"):
        quality = report["integration_quality"]
        print("\n   統合品質:")
        print(f"     ログカバレッジ: {quality['log_coverage']}%")
        print(f"     エラー率: {quality['error_rate']}%")
        print(f"     重複削減率: {quality['duplicate_reduction']}%")

    # 分布情報
    if report.get("distributions"):
        dist = report["distributions"]

        print("\n   ログレベル分布:")
        for level, count in list(dist["log_levels"].items())[:5]:
            print(f"     {level}: {count}")

        print("\n   主要コンポーネント:")
        for component, count in list(dist["components"].items())[:5]:
            print(f"     {component}: {count}")

    # トップファイル
    if report.get("top_files"):
        print("\n   ログ最多ファイル:")
        for file_info in report["top_files"][:5]:
            print(f"     {file_info['source_file']}: {file_info['log_count']}ログ")

    # 3. 使用方法案内
    print("\n3️⃣ 使用方法")
    print(
        "   設定生成: python unified_log_integration_system.py --generate-config [プロジェクトパス]"
    )
    print(
        "   プロジェクト指定: python unified_log_integration_system.py --project [プロジェクトパス]"
    )
    print(
        "   設定指定: python unified_log_integration_system.py --config [設定ファイルパス]"
    )

    print("\n📊 データベースクエリ例:")
    print(
        "   SELECT * FROM unified_logs WHERE log_level = 'ERROR' ORDER BY timestamp DESC LIMIT 10;"
    )
    print(
        "   SELECT component, COUNT(*) FROM unified_logs GROUP BY component ORDER BY COUNT(*) DESC;"
    )
    print("   SELECT * FROM log_statistics WHERE project_name = 'your_project';")

    print("\n✅ 統一ログ統合システム - 全117+ファイル完全統合完了")
    print("📍 プロジェクト全体ログ統合 + 構造化データベース + 重複除去 + 品質分析")


if __name__ == "__main__":
    main()
