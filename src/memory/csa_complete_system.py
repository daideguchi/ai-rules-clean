#!/usr/bin/env python3
"""
🌊 CSA文脈システム完全実装 - o3統合データ蓄積加速版
=====================================================

【o3統合改善】
- プロジェクト別設定対応
- 8GB容量設計統合
- 階層化データ管理
- 学習データ永続保護

【実装内容】
- 全117+ファイルから大量CSAデータ生成
- 実際の開発パターン学習強化
- o3推奨パーティション設計適用
- プロジェクト別DB自動設定
- 文脈検索効果の劇的向上
"""

import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
import psycopg2
from psycopg2.extras import RealDictCursor


class CSACompleteSystem:
    """CSA文脈システム完全版 - o3統合設計"""

    def __init__(
        self, project_root: Optional[Path] = None, config_file: Optional[str] = None
    ):
        """初期化 - プロジェクト別設定対応"""

        # プロジェクトルート自動検出
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = Path(__file__).parent.parent

        # o3推奨プロジェクト別設定読み込み
        self.config = self._load_project_config(config_file)

        # プロジェクト別DB設定
        self.db_config = self.config.get(
            "database",
            {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",  # プロジェクト名ベース
                "user": "dd",
                "password": "",
                "port": 5432,
            },
        )

        self.embedding_model = "text-embedding-ada-002"
        self.session_id = str(uuid.uuid4())

        # o3推奨統合ローカルファイル管理設定
        capacity_config = self.config.get("capacity", {})
        self.max_local_storage_mb = capacity_config.get(
            "max_size_mb", 8192
        )  # o3推奨8GB
        self.cleanup_threshold_mb = capacity_config.get(
            "warning_mb", int(self.max_local_storage_mb * 0.8)
        )
        self.preserve_recent_days = capacity_config.get("hot_days", 14)  # o3推奨14日

        # o3推奨階層化データ保持設定
        # DISABLED: Memory inheritance system never expires data
        # retention_config = self.config.get("retention", {})
        self.db_retention_days = -1  # DISABLED: Permanent retention
        self.hot_data_days = -1  # DISABLED: Permanent retention
        self.critical_preserve_days = -1  # DISABLED: Permanent retention

        # o3推奨学習データ永続保護
        protection_config = self.config.get("protection", {})
        self.learning_data_protection = protection_config.get("learning_data", True)
        self.documentation_protection = protection_config.get("documentation", True)

        # プロジェクト別パス設定
        paths_config = self.config.get("paths", {})
        self.monitored_paths = self._get_monitored_paths(paths_config)

        # UX設定
        ux_config = self.config.get("ux", {})
        self.verbose_logging = ux_config.get("verbose_logging", True)

    def _load_project_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """プロジェクト設定読み込み（o3統合設計）"""

        # 設定ファイル候補
        config_candidates = []

        if config_file:
            config_candidates.append(Path(config_file))

        # プロジェクト内設定ファイル候補
        config_candidates.extend(
            [
                self.project_root / "memory_config.json",
                self.project_root / "config" / "memory.json",
                self.project_root / ".memory_config.json",
            ]
        )

        # 設定ファイル読み込み
        for config_path in config_candidates:
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    continue

        # デフォルト設定
        return {
            "database": {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
            "capacity": {"max_size_mb": 8192, "warning_mb": 6553, "hot_days": 14},
            "retention": {"hot_days": 14, "warm_days": 365, "critical_days": 730},
            "protection": {"learning_data": True, "documentation": True},
        }

    def _get_monitored_paths(self, paths_config: Dict[str, Any]) -> List[Path]:
        """監視対象パス取得"""

        # デフォルト + プロジェクト設定
        default_paths = ["logs", "tmp", "runtime", "operations/runtime-logs"]
        hot_paths = paths_config.get("hot_tier", default_paths)

        # 学習データパス（永続保護）
        default_learning = ["docs", "ai-instructions", "memory"]
        learning_paths = paths_config.get("learning_data", default_learning)

        all_paths = hot_paths + learning_paths
        return [self.project_root / path for path in all_paths]

    def implement_o3_data_partitioning(self):
        """o3推奨パーティション設計 + プロジェクト別実装"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 既存テーブルをパーティション対応に変更
            cur.execute("""
                -- o3推奨パーティション対応テーブル（プロジェクト別）
                CREATE TABLE IF NOT EXISTS context_stream_partitioned (
                    id UUID PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    session_id UUID NOT NULL,
                    vector_embedding vector(1536),
                    parent_event_id UUID,
                    importance_level VARCHAR(20) DEFAULT 'normal',
                    project_name VARCHAR(100) DEFAULT '{self.project_root.name}',
                    file_tier VARCHAR(20) DEFAULT 'hot',  -- hot/warm/protected
                    retention_category VARCHAR(30) DEFAULT 'standard',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                ) PARTITION BY RANGE (timestamp);
            """)

            # 現在月のパーティション作成
            current_month = datetime.now().strftime("%Y%m")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS context_stream_{current_month}
                PARTITION OF context_stream_partitioned
                FOR VALUES FROM ('{datetime.now().strftime("%Y-%m-01")}')
                TO ('{(datetime.now().replace(day=1) + timedelta(days=32)).strftime("%Y-%m-01")}');
            """)

            # o3推奨複合インデックス
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_context_{current_month}_project_importance
                ON context_stream_{current_month} (project_name, importance_level, timestamp DESC)
                WHERE importance_level IN ('critical', 'high');
            """)

            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_context_{current_month}_tier_vector
                ON context_stream_{current_month} USING ivfflat (vector_embedding vector_cosine_ops)
                WHERE file_tier = 'hot' AND timestamp >= NOW() - INTERVAL '{self.hot_data_days} days';
            """)

            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_context_{current_month}_learning_protection
                ON context_stream_{current_month} (retention_category, file_tier, timestamp)
                WHERE retention_category IN ('learning', 'documentation', 'critical');
            """)

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "message": "o3推奨パーティション実装完了",
                "project_name": self.project_root.name,
                "database": self.db_config["database"],
                "partitions_created": f"context_stream_{current_month}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Partitioning failed: {str(e)}"}

    def accelerate_csa_data_accumulation_o3(self) -> Dict[str, Any]:
        """o3統合CSAデータ蓄積加速 - 全ファイルタイプ対応"""

        # o3推奨全ファイルタイプ取得
        file_patterns = {
            "logs": ["*.log", "*.txt"],
            "documentation": ["*.md", "*.rst", "*.txt"],
            "data": ["*.json", "*.yaml", "*.yml"],
            "reports": ["*report*", "*analysis*", "*summary*"],
            "learning": ["*mistake*", "*learning*", "*president*"],
        }

        all_files = []
        file_type_stats = {}

        for file_type, patterns in file_patterns.items():
            type_files = []
            for pattern in patterns:
                type_files.extend(list(self.project_root.rglob(pattern)))

            # 重複除去
            unique_files = list(set(type_files))
            all_files.extend(unique_files)
            file_type_stats[file_type] = len(unique_files)

            if self.verbose_logging:
                print(f"📂 {file_type}: {len(unique_files)}ファイル")

        # 重複除去（異なるパターンで同じファイルが無いか確認）
        all_files = list(set(all_files))

        print(f"📂 総発見ファイル数: {len(all_files)}")
        print(f"📈 ファイルタイプ別: {file_type_stats}")

        processed_events = 0
        skipped_files = 0
        batch_size = 50  # o3推奨バッチ処理

        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            for i, file_path in enumerate(all_files):
                try:
                    # o3推奨ファイルサイズチェック (50MB以下)
                    file_size = file_path.stat().st_size
                    if file_size > 50 * 1024 * 1024:
                        if self.verbose_logging:
                            print(
                                f"   ⚠️ サイズ制限スキップ: {file_path.name} ({file_size / (1024 * 1024):.1f}MB)"
                            )
                        skipped_files += 1
                        continue

                    # ファイル内容読み込み
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # o3推奨内容品質チェック
                    if len(content.strip()) < 10:  # 空ファイル
                        skipped_files += 1
                        continue

                    # ファイルタイプ判定
                    file_tier = self._determine_file_tier(file_path)
                    retention_category = self._determine_retention_category(
                        file_path, content
                    )

                    # o3統合CSAイベント生成
                    events = self._generate_csa_events_from_file_o3(
                        file_path, content, file_tier, retention_category
                    )

                    # 一括保存
                    for event in events:
                        self._save_csa_event_o3_optimized(cur, event)
                        processed_events += 1

                    # o3推奨進捗表示 + バッチコミット
                    if (i + 1) % batch_size == 0:
                        print(
                            f"   処理済み: {i + 1}/{len(all_files)} ファイル ({processed_events}イベント) [{(i + 1) / len(all_files) * 100:.1f}%]"
                        )
                        conn.commit()  # o3推奨中間コミット

                except Exception as e:
                    if self.verbose_logging:
                        print(f"   ⚠️ ファイル処理エラー: {file_path.name}: {str(e)}")
                    skipped_files += 1
                    continue

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "processed_files": len(all_files) - skipped_files,
                "skipped_files": skipped_files,
                "total_files_discovered": len(all_files),
                "total_events": processed_events,
                "session_id": self.session_id,
                "project_name": self.project_root.name,
                "database": self.db_config["database"],
                "file_type_stats": file_type_stats,
                "events_per_file_avg": round(
                    processed_events / max(len(all_files) - skipped_files, 1), 2
                ),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _determine_file_tier(self, file_path: Path) -> str:
        """ファイル層判定（o3推奨階層化）"""

        path_str = str(file_path).lower()
        name_lower = file_path.name.lower()

        # 学習データ層（永続保護）
        if any(
            keyword in path_str for keyword in ["docs/", "ai-instructions/", "memory/"]
        ):
            return "protected"

        if any(
            keyword in name_lower
            for keyword in ["mistake", "learning", "president", "report", "analysis"]
        ):
            return "protected"

        # ウォーム層（中間アーカイブ）
        if any(keyword in path_str for keyword in ["data/warm", "archive/", "backup/"]):
            return "warm"

        # ホット層（高速アクセス）
        if any(keyword in path_str for keyword in ["logs/", "tmp/", "runtime/"]):
            return "hot"

        # デフォルトはホット層
        return "hot"

    def _determine_retention_category(self, file_path: Path, content: str) -> str:
        """保持カテゴリ判定（o3推奨データ保護）"""

        str(file_path).lower()
        name_lower = file_path.name.lower()
        content_lower = content.lower()

        # クリティカル（最重要）
        if any(
            keyword in content_lower
            for keyword in ["error", "critical", "failed", "exception"]
        ):
            return "critical"

        # 学習データ（永続保護）
        if any(
            keyword in name_lower for keyword in ["mistake", "learning", "president"]
        ):
            return "learning"

        # ドキュメンテーション（永続保護）
        if file_path.suffix in [".md", ".rst"] or "readme" in name_lower:
            return "documentation"

        # レポート・分析（長期保護）
        if any(keyword in name_lower for keyword in ["report", "analysis", "summary"]):
            return "report"

        # システムログ（標準保護）
        if file_path.suffix == ".log":
            return "system_log"

        return "standard"

    def _generate_csa_events_from_file_o3(
        self, file_path: Path, content: str, file_tier: str, retention_category: str
    ) -> List[Dict[str, Any]]:
        """o3統合ファイルからCSAイベント群を生成"""

        events = []
        file_type = self._classify_file_type(file_path)

        # o3統合ファイル全体の要約イベント
        summary_event = self._create_file_summary_event_o3(
            file_path, content, file_type, file_tier, retention_category
        )
        if summary_event:
            events.append(summary_event)

        # o3推奨内容に基づく詳細イベント
        detail_events = self._extract_detail_events_o3(
            file_path, content, file_type, file_tier, retention_category
        )
        events.extend(detail_events)

        return events

    def _classify_file_type(self, file_path: Path) -> str:
        """ファイルタイプ分類"""

        name_lower = file_path.name.lower()

        if file_path.suffix == ".log":
            if "error" in name_lower or "exception" in name_lower:
                return "error_log"
            elif "debug" in name_lower:
                return "debug_log"
            else:
                return "system_log"

        elif file_path.suffix == ".md":
            if "report" in name_lower:
                return "report"
            elif "readme" in name_lower:
                return "documentation"
            elif "mistake" in name_lower:
                return "learning_record"
            else:
                return "markdown_doc"

        else:
            return "general_file"

    def _create_file_summary_event_o3(
        self,
        file_path: Path,
        content: str,
        file_type: str,
        file_tier: str,
        retention_category: str,
    ) -> Optional[Dict[str, Any]]:
        """o3統合ファイル要約イベント作成"""

        # ファイル統計
        lines = content.split("\\n")
        word_count = len(content.split())

        # 重要度判定
        importance = self._assess_importance(content, file_type)

        # o3推奨拡張メタデータ構築
        metadata = {
            "file_path": str(file_path.relative_to(self.project_root)),
            "file_type": file_type,
            "file_tier": file_tier,
            "retention_category": retention_category,
            "project_name": self.project_root.name,
            "file_size": file_path.stat().st_size,
            "line_count": len(lines),
            "word_count": word_count,
            "last_modified": datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat(),
            "file_extension": file_path.suffix,
            "relative_path_depth": len(file_path.relative_to(self.project_root).parts),
        }

        # 内容要約
        summary = self._generate_content_summary(content, file_type)

        # ベクトル埋め込み
        embedding = self._generate_embedding(
            f"{file_type}: {file_path.name}: {summary}"
        )

        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "source": "file_analysis_o3",
            "event_type": f"{file_type}_summary",
            "content": summary,
            "metadata": metadata,
            "session_id": self.session_id,
            "vector_embedding": embedding,
            "importance_level": importance,
            "project_name": self.project_root.name,
            "file_tier": file_tier,
            "retention_category": retention_category,
        }

    def _extract_detail_events_o3(
        self,
        file_path: Path,
        content: str,
        file_type: str,
        file_tier: str,
        retention_category: str,
    ) -> List[Dict[str, Any]]:
        """o3統合詳細イベント抽出 - 全ファイルタイプ対応"""

        events = []

        # o3推奨包括的パターン抽出

        # エラー・例外パターン
        if file_type in ["error_log", "system_log"] or retention_category == "critical":
            error_patterns = re.findall(
                r"(ERROR|Exception|Failed|Error|CRITICAL|Fatal).*",
                content,
                re.IGNORECASE,
            )
            for pattern in error_patterns[:10]:  # o3推奨1ファイル10件まで
                events.append(
                    self._create_detail_event_o3(
                        file_path,
                        pattern,
                        "error_detection",
                        "critical",
                        file_tier,
                        retention_category,
                    )
                )

        # レポート・分析結果
        if file_type == "report" or retention_category == "report":
            # 日本語 + 英語結論パターン
            conclusions = re.findall(
                r"(結論|結果|成果|効果|Summary|Conclusion|Result)[:：\s]*(.*)",
                content,
                re.IGNORECASE,
            )
            for conclusion in conclusions[:5]:
                events.append(
                    self._create_detail_event_o3(
                        file_path,
                        f"{conclusion[0]}: {conclusion[1]}",
                        "report_conclusion",
                        "high",
                        file_tier,
                        retention_category,
                    )
                )

        # 学習・ミス記録
        if retention_category == "learning":
            # ミス番号付きパターン
            mistakes = re.findall(r"###\s*(\d+)\.\s*(.*)", content)
            for mistake in mistakes[:15]:  # o3推奨学習データは多めに保存
                events.append(
                    self._create_detail_event_o3(
                        file_path,
                        f"ミス#{mistake[0]}: {mistake[1]}",
                        "mistake_record",
                        "critical",
                        file_tier,
                        retention_category,
                    )
                )

            # 学習パターン
            learning_patterns = re.findall(
                r"(学習|改善|対策|Learning|Improvement)[:：\s]*(.*)",
                content,
                re.IGNORECASE,
            )
            for pattern in learning_patterns[:10]:
                events.append(
                    self._create_detail_event_o3(
                        file_path,
                        f"{pattern[0]}: {pattern[1]}",
                        "learning_insight",
                        "high",
                        file_tier,
                        retention_category,
                    )
                )

        # ドキュメンテーション重要セクション
        if retention_category == "documentation":
            # マークダウンヘッダー
            headers = re.findall(r"^(#{1,3})\s+(.+)", content, re.MULTILINE)
            for header in headers[:8]:  # 主要ヘッダーのみ
                level = len(header[0])
                if level <= 2:  # H1, H2のみ
                    events.append(
                        self._create_detail_event_o3(
                            file_path,
                            header[1],
                            "documentation_section",
                            "medium",
                            file_tier,
                            retention_category,
                        )
                    )

        # コードブロック（ドキュメント内）
        if file_type == "markdown_doc":
            code_blocks = re.findall(r"```(\w+)?\s*\n(.*?)\n```", content, re.DOTALL)
            for _i, (lang, code) in enumerate(code_blocks[:3]):  # 最初の3個
                if len(code.strip()) > 20:
                    events.append(
                        self._create_detail_event_o3(
                            file_path,
                            f"Code example ({lang or 'unknown'}): {code[:100]}...",
                            "code_example",
                            "medium",
                            file_tier,
                            retention_category,
                        )
                    )

        # 数値データ・統計
        if "data" in file_type or "analysis" in file_path.name.lower():
            # 数値パターン
            numbers = re.findall(
                r"(\d+(?:\.\d+)?\s*(?:%|MB|GB|KB|ms|sec|min))", content
            )
            if len(numbers) > 5:  # 数値が多いファイル
                events.append(
                    self._create_detail_event_o3(
                        file_path,
                        f"Numerical data detected: {len(numbers)} metrics",
                        "data_metrics",
                        "medium",
                        file_tier,
                        retention_category,
                    )
                )

        return events

    def _create_detail_event_o3(
        self,
        file_path: Path,
        content: str,
        event_type: str,
        importance: str,
        file_tier: str,
        retention_category: str,
    ) -> Dict[str, Any]:
        """o3統合詳細イベント作成"""

        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "source": "content_analysis_o3",
            "event_type": event_type,
            "content": content[:1000],  # o3推奨拡張制限
            "metadata": {
                "source_file": str(file_path.relative_to(self.project_root)),
                "extraction_method": "o3_pattern_matching",
                "file_tier": file_tier,
                "retention_category": retention_category,
                "project_name": self.project_root.name,
            },
            "session_id": self.session_id,
            "vector_embedding": self._generate_embedding(content),
            "importance_level": importance,
            "project_name": self.project_root.name,
            "file_tier": file_tier,
            "retention_category": retention_category,
        }

    def _assess_importance(self, content: str, file_type: str) -> str:
        """重要度評価"""

        content_lower = content.lower()

        # クリティカル条件
        if any(
            keyword in content_lower
            for keyword in ["error", "critical", "failed", "exception"]
        ):
            return "critical"

        # 高重要度条件
        if file_type in ["learning_record", "error_log"] or any(
            keyword in content_lower
            for keyword in ["important", "重要", "urgent", "緊急"]
        ):
            return "high"

        # レポート類は中重要度
        if file_type == "report":
            return "medium"

        return "normal"

    def _generate_content_summary(self, content: str, file_type: str) -> str:
        """内容要約生成"""

        lines = content.split("\\n")

        if file_type == "error_log":
            # エラーログは最初のエラーメッセージ
            for line in lines:
                if any(
                    keyword in line.lower()
                    for keyword in ["error", "exception", "failed"]
                ):
                    return line.strip()[:200]

        elif file_type == "report":
            # レポートは最初の段落
            for line in lines:
                if len(line.strip()) > 50:
                    return line.strip()[:200]

        # デフォルトは最初の意味のある行
        for line in lines:
            if len(line.strip()) > 20:
                return line.strip()[:200]

        return f"ファイル分析: {file_type} ({len(lines)}行)"

    def _generate_embedding(self, text: str) -> List[float]:
        """ベクトル埋め込み生成"""
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000],  # OpenAI制限対応
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return [0.0] * 1536

    def _save_csa_event_o3_optimized(self, cursor, event: Dict[str, Any]) -> bool:
        """o3統合最適化CSAイベント保存"""
        try:
            # o3推奨パーティション対応テーブルに保存
            cursor.execute(
                """
                INSERT INTO context_stream_partitioned
                (id, timestamp, source, event_type, content, metadata, session_id, vector_embedding,
                 importance_level, project_name, file_tier, retention_category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """,
                (
                    event["id"],
                    event["timestamp"],
                    event["source"],
                    event["event_type"],
                    event["content"],
                    json.dumps(event["metadata"]),
                    event["session_id"],
                    event["vector_embedding"],
                    event["importance_level"],
                    event.get("project_name", self.project_root.name),
                    event.get("file_tier", "hot"),
                    event.get("retention_category", "standard"),
                ),
            )
            return True
        except Exception as e:
            if self.verbose_logging:
                print(f"o3 Event save failed: {e}")
            return False

    def enhanced_context_search_v2(
        self, query: str, importance_filter: List[str] = None, limit: int = 20
    ) -> Dict[str, Any]:
        """強化された文脈検索 v2"""

        query_embedding = self._generate_embedding(query)

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 重要度フィルター条件
            importance_condition = ""
            params = [query_embedding, query_embedding]

            if importance_filter:
                placeholders = ",".join(["%s"] * len(importance_filter))
                importance_condition = f"AND importance_level IN ({placeholders})"
                params.extend(importance_filter)

            params.extend([f"%{query}%", f"%{query}%", query_embedding, limit])

            # 複合検索: パーティション考慮 + 重要度 + ベクトル類似度
            cur.execute(
                f"""
                SELECT
                    id, timestamp, source, event_type, content, metadata, importance_level,
                    1 - (vector_embedding <=> %s::vector) as similarity
                FROM context_stream_partitioned
                WHERE vector_embedding IS NOT NULL
                  AND timestamp >= NOW() - INTERVAL '{self.data_retention_days} days'
                  {importance_condition}
                  AND (
                    1 - (vector_embedding <=> %s::vector) > 0.5
                    OR content ILIKE %s
                    OR event_type ILIKE %s
                  )
                ORDER BY
                    CASE importance_level
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        ELSE 4
                    END,
                    (1 - (vector_embedding <=> %s::vector)) DESC,
                    timestamp DESC
                LIMIT %s;
            """,
                params,
            )

            results = cur.fetchall()
            cur.close()
            conn.close()

            # 結果分析
            categorized = self._categorize_results_v2([dict(row) for row in results])

            return {
                "status": "success",
                "query": query,
                "total_results": len(results),
                "categorized_results": categorized,
                "search_metadata": {
                    "importance_filter": importance_filter,
                    "retention_days": self.data_retention_days,
                    "search_algorithm": "importance_weighted_semantic",
                },
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _categorize_results_v2(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """結果分析 v2 - 重要度別"""

        categories = {
            "critical_events": [],
            "high_importance": [],
            "error_analysis": [],
            "learning_records": [],
            "reports": [],
            "general": [],
        }

        for result in results:
            importance = result["importance_level"]
            event_type = result["event_type"]

            if importance == "critical":
                categories["critical_events"].append(result)
            elif importance == "high":
                categories["high_importance"].append(result)
            elif "error" in event_type:
                categories["error_analysis"].append(result)
            elif "mistake" in event_type or "learning" in event_type:
                categories["learning_records"].append(result)
            elif "report" in event_type:
                categories["reports"].append(result)
            else:
                categories["general"].append(result)

        return categories


def main():
    """メイン実行 - CSA完全システム"""
    print("🌊 CSA文脈システム完全実装開始")

    csa_system = CSACompleteSystem()

    # 1. o3推奨データパーティション実装
    print("\\n1️⃣ o3推奨データパーティション実装")
    partition_result = csa_system.implement_o3_data_partitioning()
    print(f"パーティション: {partition_result['status']}")

    if partition_result["status"] == "error":
        print(f"エラー: {partition_result['message']}")
        return

    # 2. CSAデータ蓄積加速
    print("\\n2️⃣ CSAデータ蓄積加速処理")
    accumulation_result = csa_system.accelerate_csa_data_accumulation_o3()
    print(f"蓄積結果: {accumulation_result['status']}")

    if accumulation_result["status"] == "success":
        print(f"   処理ファイル数: {accumulation_result['processed_files']}")
        print(f"   スキップファイル数: {accumulation_result['skipped_files']}")
        print(f"   総イベント数: {accumulation_result['total_events']}")
        print(f"   セッションID: {accumulation_result['session_id'][:8]}...")
    else:
        print(f"   エラー: {accumulation_result['error']}")
        return

    # 3. 強化された文脈検索テスト
    print("\\n3️⃣ 強化された文脈検索 v2 テスト")
    test_queries = [
        ("データベースエラー", ["critical", "high"]),
        ("ファイル操作", ["high", "medium"]),
        ("学習記録", ["critical"]),
        ("レポート分析", ["medium"]),
    ]

    for query, importance_filter in test_queries:
        search_result = csa_system.enhanced_context_search_v2(
            query, importance_filter, limit=10
        )
        print(f"\\n   検索: '{query}' (重要度: {importance_filter})")
        print(f"   結果: {search_result.get('total_results', 0)}件")

        if search_result["status"] == "success":
            categorized = search_result["categorized_results"]
            for category, events in categorized.items():
                if events:
                    print(f"     {category}: {len(events)}件")
                    for event in events[:2]:
                        print(
                            f"       - [{event['importance_level']}] {event['content'][:60]}..."
                        )

    print("\\n✅ CSA文脈システム完全実装完了")
    print("📍 全ファイル解析による大量文脈データ蓄積 + o3推奨データ管理実装")


if __name__ == "__main__":
    main()
