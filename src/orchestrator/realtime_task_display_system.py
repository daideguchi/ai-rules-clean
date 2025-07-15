#!/usr/bin/env python3
"""
Realtime Task Display System - 役職とタスクのリアルタイム表示
=============================================================
AIワーカーの役職と実行中タスクを正確に表示する本質的システム

Core Features:
- 役職の明確な表示
- 実行中タスクのリアルタイム追跡
- Claude Code出力からのタスク抽出
- 最小限の装飾で最大限の情報提供
"""

import json
import logging
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


@dataclass
class TaskInfo:
    """タスク情報"""

    task_type: str  # "command", "analysis", "implementation", "thinking"
    task_description: str
    started_at: datetime
    progress: Optional[str] = None
    target_files: Optional[List[str]] = None


@dataclass
class WorkerTaskState:
    """ワーカーのタスク状態"""

    pane_id: str
    role: str
    current_task: Optional[TaskInfo]
    last_update: datetime
    is_active: bool


class RealtimeTaskDisplaySystem:
    """役職とタスクのリアルタイム表示システム"""

    def __init__(self, project_root: str = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        )
        self.runtime_dir = self.project_root / "runtime"
        self.running = False

        # 言語設定（デフォルト：日本語）
        self.language = self._load_language_preference()
        self.language_config_file = self.runtime_dir / "language_config.json"

        # ログ設定
        logging.basicConfig(
            level=logging.DEBUG,  # Debug level for troubleshooting
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.runtime_dir / "logs" / "task_display.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("task-display")

        # ワーカー設定（日本語役職名）
        self.worker_configs = {
            "president": {"0": {"role": "社長", "title_prefix": "社長"}},
            "multiagent": {
                "0.0": {"role": "部長", "title_prefix": "部長"},
                "0.1": {"role": "作業員1", "title_prefix": "作業員1"},
                "0.2": {"role": "作業員2", "title_prefix": "作業員2"},
                "0.3": {"role": "作業員3", "title_prefix": "作業員3"},
            },
        }

        # タスク状態管理
        self.worker_states: Dict[str, WorkerTaskState] = {}

        # タスク検出パターン
        self.task_patterns = {
            # Claude Codeのコマンド実行パターン
            "command": [
                r">\s*(.+)",  # プロンプト入力
                r"Running:\s*(.+)",
                r"Executing:\s*(.+)",
                r"▶\s*(.+)",  # Claude Code実行インジケータ
            ],
            # 分析・思考パターン
            "analysis": [
                r"Analyzing\s+(.+)",
                r"Searching\s+for\s+(.+)",
                r"Looking\s+at\s+(.+)",
                r"Checking\s+(.+)",
                r"Reading\s+(.+)",
            ],
            # 実装・編集パターン
            "implementation": [
                r"Writing\s+to\s+(.+)",
                r"Editing\s+(.+)",
                r"Creating\s+(.+)",
                r"Updating\s+(.+)",
                r"Modifying\s+(.+)",
            ],
            # 思考中パターン
            "thinking": [
                r"Thinking\s+about\s+(.+)",
                r"Considering\s+(.+)",
                r"Planning\s+(.+)",
            ],
        }

        # ファイルパス検出パターン
        self.file_patterns = [
            r"([\/\w\-\.]+\.(py|js|ts|md|json|yaml|yml))",
            r"src\/[\w\/\-\.]+",
            r"tests\/[\w\/\-\.]+",
        ]

        # 監視スレッド
        self.monitor_thread = None

        # 英語→日本語翻訳辞書
        self.task_translation_dict = {
            # 一般的なタスク
            "analyze": "分析",
            "check": "確認",
            "list": "一覧表示",
            "create": "作成",
            "update": "更新",
            "delete": "削除",
            "search": "検索",
            "find": "検索",
            "read": "読み込み",
            "write": "書き込み",
            "edit": "編集",
            "modify": "変更",
            "fix": "修正",
            "debug": "デバッグ",
            "test": "テスト",
            "run": "実行",
            "execute": "実行",
            "install": "インストール",
            "configure": "設定",
            "setup": "セットアップ",
            "deploy": "デプロイ",
            "build": "ビルド",
            "compile": "コンパイル",
            "review": "レビュー",
            "refactor": "リファクタリング",
            "optimize": "最適化",
            "validate": "検証",
            "verify": "確認",
            "implement": "実装",
            "develop": "開発",
            "design": "設計",
            "plan": "計画",
            # ファイル・ディレクトリ関連
            "files": "ファイル",
            "directory": "ディレクトリ",
            "folder": "フォルダ",
            "project": "プロジェクト",
            "structure": "構造",
            "code": "コード",
            "script": "スクリプト",
            "function": "関数",
            "class": "クラス",
            "module": "モジュール",
            "package": "パッケージ",
            "library": "ライブラリ",
            "framework": "フレームワーク",
            "database": "データベース",
            "config": "設定",
            "configuration": "設定",
            "documentation": "ドキュメント",
            "readme": "README",
            # 技術用語
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "html": "HTML",
            "css": "CSS",
            "json": "JSON",
            "yaml": "YAML",
            "xml": "XML",
            "sql": "SQL",
            "api": "API",
            "rest": "REST",
            "http": "HTTP",
            "https": "HTTPS",
            "git": "Git",
            "github": "GitHub",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            # 状態・動作
            "working": "作業中",
            "processing": "処理中",
            "loading": "読み込み中",
            "waiting": "待機中",
            "ready": "準備完了",
            "complete": "完了",
            "finished": "終了",
            "started": "開始",
            "running": "実行中",
            "stopped": "停止",
            "failed": "失敗",
            "error": "エラー",
            "success": "成功",
            "warning": "警告",
            # その他
            "all": "全て",
            "current": "現在の",
            "new": "新しい",
            "old": "古い",
            "latest": "最新",
            "previous": "前の",
            "next": "次の",
            "first": "最初",
            "last": "最後",
            "summary": "要約",
            "overview": "概要",
            "details": "詳細",
            "information": "情報",
            "data": "データ",
            "content": "内容",
            "status": "状態",
            "report": "レポート",
            "log": "ログ",
            "history": "履歴",
            "backup": "バックアップ",
            "restore": "復元",
            "sync": "同期",
            "merge": "マージ",
            "branch": "ブランチ",
            "commit": "コミット",
            "push": "プッシュ",
            "pull": "プル",
            "clone": "クローン",
            "fork": "フォーク",
        }

        # 役職翻訳辞書（日本語）
        self.role_translation_dict = {
            "PRESIDENT": "社長",
            "BOSS1": "部長",
            "WORKER1": "作業員1",
            "WORKER2": "作業員2",
            "WORKER3": "作業員3",
            "MANAGER": "管理者",
            "DEVELOPER": "開発者",
            "DESIGNER": "設計者",
            "TESTER": "テスター",
            "ANALYST": "分析者",
            "ARCHITECT": "アーキテクト",
            "LEAD": "リーダー",
            "SENIOR": "シニア",
            "JUNIOR": "ジュニア",
        }

        # 役職英語辞書（English版）
        self.role_english_dict = {
            "PRESIDENT": "President",
            "BOSS1": "Manager",
            "WORKER1": "Worker 1",
            "WORKER2": "Worker 2",
            "WORKER3": "Worker 3",
            "MANAGER": "Manager",
            "DEVELOPER": "Developer",
            "DESIGNER": "Designer",
            "TESTER": "Tester",
            "ANALYST": "Analyst",
            "ARCHITECT": "Architect",
            "LEAD": "Lead",
            "SENIOR": "Senior",
            "JUNIOR": "Junior",
        }

    def start_monitoring(self):
        """監視開始"""
        if self.running:
            self.logger.warning("Monitoring already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("✅ Realtime Task Display System started")

    def stop_monitoring(self):
        """監視停止"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Task Display System stopped")

    def _monitor_loop(self):
        """メイン監視ループ"""
        while self.running:
            try:
                # 全ワーカーのタスク状態更新
                for session_name, panes in self.worker_configs.items():
                    if self._session_exists(session_name):
                        for pane_id, config in panes.items():
                            self._update_worker_task(session_name, pane_id, config)

                # ステータスバー更新
                self._update_all_statusbars()

                time.sleep(2)  # 2秒間隔で更新

            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(5)

    def _update_worker_task(self, session: str, pane_id: str, config: Dict):
        """個別ワーカーのタスク更新"""
        try:
            pane_target = f"{session}:{pane_id}"

            # ペイン内容取得（最新50行）
            content = self._get_pane_content(pane_target, lines=50)

            # タスク抽出
            task_info = self._extract_task_info(content)

            # 状態更新
            state = WorkerTaskState(
                pane_id=pane_target,
                role=config["role"],
                current_task=task_info,
                last_update=datetime.now(),
                is_active=(task_info is not None),
            )

            self.worker_states[pane_target] = state

            if task_info:
                self.logger.debug(
                    f"{config['role']}: {task_info.task_description[:50]}"
                )

        except Exception as e:
            self.logger.error(f"Error updating worker {pane_target}: {e}")
            # Debug: Show pane content for troubleshooting
            if self.logger.level <= logging.DEBUG:
                content = self._get_pane_content(pane_target, lines=10)
                self.logger.debug(f"Pane content for {pane_target}: {content[:200]}")

    def _extract_task_info(self, content: str) -> Optional[TaskInfo]:
        """ペイン内容からタスク情報抽出"""
        if not content:
            return None

        self.logger.debug(f"Analyzing content: {content[:100]}...")

        # 最新の行から逆順に検索（最新のタスクを優先）
        lines = content.strip().split("\n")
        recent_lines = lines[-30:]  # 最新30行に注目

        # まず、入力プロンプト（> で始まる行とその後の行）を最優先で検索
        for line in reversed(recent_lines):
            # >で始まる行をユーザー入力として検出
            match = re.search(r"│\s*>\s*(.+)", line)
            if match:
                task_description = match.group(1).strip()

                # タスク説明が有効か確認
                if self._is_valid_task(task_description):
                    # ファイル情報抽出
                    target_files = self._extract_file_references(task_description)

                    return TaskInfo(
                        task_type="command",
                        task_description=self._clean_task_description(task_description),
                        started_at=datetime.now(),
                        target_files=target_files,
                    )

            # 入力済みタスク（スペースで始まる行）も検出
            match = re.search(r"│\s{2,}([^│\s].+)", line)
            if match:
                task_description = match.group(1).strip()

                # タスク説明が有効か確認（より緩い条件）
                if len(task_description) > 10 and not any(
                    x in task_description.lower()
                    for x in ["welcome", "tip:", "help", "approaching"]
                ):
                    # ファイル情報抽出
                    target_files = self._extract_file_references(task_description)

                    return TaskInfo(
                        task_type="command",
                        task_description=self._clean_task_description(task_description),
                        started_at=datetime.now(),
                        target_files=target_files,
                    )

        # 次に、その他のパターンマッチング
        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                for line in reversed(recent_lines):
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        task_description = match.group(1).strip()

                        # タスク説明が有効か確認
                        if self._is_valid_task(task_description):
                            # ファイル情報抽出
                            target_files = self._extract_file_references(
                                task_description
                            )

                            return TaskInfo(
                                task_type=task_type,
                                task_description=self._clean_task_description(
                                    task_description
                                ),
                                started_at=datetime.now(),
                                target_files=target_files,
                            )

        # Claude Code特有のパターン
        # "How can I help"の後の入力を探す
        for i, line in enumerate(lines):
            if "How can I help" in line and i < len(lines) - 1:
                # 次の非空行を探す
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith(("?", "#", "//")):
                        return TaskInfo(
                            task_type="command",
                            task_description=next_line[:100],  # 100文字制限
                            started_at=datetime.now(),
                        )

        return None

    def _is_valid_task(self, task_desc: str) -> bool:
        """有効なタスク説明かチェック"""
        # 無効なパターン
        invalid_patterns = [
            r"^\s*$",  # 空白のみ
            r"^[>\$#]+\s*$",  # プロンプトのみ
            r"^Enter to",  # UIプロンプト
            r"^Press",  # キー入力指示
            r"^\?",  # ヘルプ
        ]

        for pattern in invalid_patterns:
            if re.match(pattern, task_desc):
                return False

        # 最小長チェック
        return len(task_desc.strip()) > 3

    def _clean_task_description(self, task_desc: str) -> str:
        """タスク説明のクリーニング"""
        # 不要な文字を削除
        task_desc = re.sub(r"^[>\$#\s]+", "", task_desc)
        task_desc = re.sub(r"\s+", " ", task_desc)

        # 長すぎる場合は切り詰め
        if len(task_desc) > 60:
            task_desc = task_desc[:57] + "..."

        return task_desc.strip()

    def _extract_file_references(self, text: str) -> List[str]:
        """テキストからファイル参照を抽出"""
        files = []
        for pattern in self.file_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    files.append(match[0])
                else:
                    files.append(match)
        return list(set(files))[:3]  # 最大3ファイル

    def _translate_task(self, task_description: str) -> str:
        """言語設定に応じてタスク説明を翻訳"""
        if self.language == "en":
            return task_description  # 英語の場合はそのまま返す

        # 日本語翻訳
        return self._translate_task_to_japanese(task_description)

    def _translate_task_to_japanese(self, task_description: str) -> str:
        """タスク説明を日本語に翻訳"""
        # 元の文を保持
        original_task = task_description
        translated_task = task_description.lower()

        # フレーズ単位でより自然な翻訳（先に適用）
        phrase_translations = {
            # 完全な文のパターン
            r"create\s+a\s+new\s+(.+)\s+function\s+to\s+handle\s+(.+)\s+processing": r"\2処理を行う新しい\1関数を作成",
            r"analyze\s+current\s+project\s+structure\s+and\s+provide\s+summary": r"現在のプロジェクト構造を分析し要約を提供",
            r"list\s+all\s+python\s+files\s+in\s+src/\s+directory": r"src/ディレクトリ内の全てのPythonファイルを一覧表示",
            r"check\s+if\s+(.+)\s+is\s+working\s+properly": r"\1が正常に動作しているかを確認",
            r"how\s+does\s+(.+)\.json\s+work\?": r"\1.jsonの動作原理",
            # 動詞 + 名詞のパターン
            r"analyze\s+(.+)\s+structure": r"\1構造を分析",
            r"check\s+if\s+(.+)\s+is\s+working": r"\1の動作を確認",
            r"list\s+all\s+(.+)\s+files": r"全ての\1ファイルを一覧表示",
            r"create\s+a\s+new\s+(.+)": r"新しい\1を作成",
            r"create\s+(.+)\s+file": r"\1ファイルを作成",
            r"update\s+(.+)\s+file": r"\1ファイルを更新",
            r"refactor\s+(.+)\.json": r"\1.jsonをリファクタリング",
            r"refactor\s+(.+)": r"\1をリファクタリング",
            r"provide\s+(.+)\s+summary": r"\1の要約を提供",
            r"(.+)\s+in\s+(.+)\s+directory": r"\2ディレクトリ内の\1",
            r"(.+)\s+files\s+in\s+(.+)": r"\2内の\1ファイル",
            # Try パターン（Claude Codeでよく出現）
            r'try\s+"([^"]+)"': r"「\1」を試行",
            r"try\s+(.+)": r"\1を試行",
            # その他のパターン
            r"(.+)\s+properly": r"\1が正常に動作するか",
            r"current\s+(.+)": r"現在の\1",
            r"all\s+(.+)": r"全ての\1",
            r"a\s+new\s+(.+)": r"新しい\1",
            r"to\s+handle\s+(.+)": r"\1を処理する",
        }

        # フレーズ翻訳を適用（先に長いパターンから）
        for pattern, replacement in phrase_translations.items():
            if re.search(pattern, translated_task, flags=re.IGNORECASE):
                translated_task = re.sub(
                    pattern, replacement, translated_task, flags=re.IGNORECASE
                )
                # フレーズマッチした場合は早期返却
                return translated_task

        # フレーズマッチしなかった場合、単語単位で翻訳
        words = re.findall(r"\b\w+\b", translated_task)
        for word in words:
            if word in self.task_translation_dict:
                # 単語境界を考慮した置換
                pattern = r"\b" + re.escape(word) + r"\b"
                translated_task = re.sub(
                    pattern,
                    self.task_translation_dict[word],
                    translated_task,
                    flags=re.IGNORECASE,
                )

        # 翻訳が改善されているかチェック
        if len(translated_task) > 0 and any(
            char in translated_task
            for char in "あいうえおかきくけこさしすせそたちつてと"
        ):
            return translated_task
        else:
            # 翻訳がうまくいかない場合は元のタスクを返す
            return original_task

    def _load_language_preference(self) -> str:
        """言語設定を読み込み（デフォルト：日本語）"""
        config_file = self.runtime_dir / "language_config.json"
        try:
            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("language", "ja")
        except Exception:
            pass
        return "ja"  # デフォルトは日本語

    def set_language(self, language: str) -> bool:
        """言語設定を変更"""
        if language not in ["ja", "en"]:
            self.logger.error(f"Unsupported language: {language}. Use 'ja' or 'en'")
            return False

        try:
            self.language = language

            # 設定保存
            config = {"language": language, "updated_at": datetime.now().isoformat()}
            self.language_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.language_config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.logger.info(
                f"Language changed to: {'Japanese' if language == 'ja' else 'English'}"
            )

            # 即座にステータスバー更新
            self._update_all_statusbars()
            return True

        except Exception as e:
            self.logger.error(f"Error setting language: {e}")
            return False

    def _translate_role(self, role: str) -> str:
        """言語設定に応じて役職を翻訳"""
        if self.language == "ja":
            return self.role_translation_dict.get(role, role)
        else:  # English
            return self.role_english_dict.get(role, role)

    def _update_all_statusbars(self):
        """全ワーカーのステータスバー更新"""
        self.logger.debug(f"Updating statusbars for {len(self.worker_states)} workers")

        for pane_target, state in self.worker_states.items():
            try:
                # 役職とタスクを設定言語に翻訳
                translated_role = self._translate_role(state.role)

                if state.current_task:
                    translated_task = self._translate_task(
                        state.current_task.task_description
                    )
                    title = f"{translated_role}: {translated_task}"
                    self.logger.debug(
                        f"Setting {self.language.upper()} title for {pane_target}: {title}"
                    )
                else:
                    idle_text = "待機中" if self.language == "ja" else "Idle"
                    title = f"{translated_role}: [{idle_text}]"
                    self.logger.debug(
                        f"Setting idle {self.language.upper()} title for {pane_target}: {title}"
                    )

                # tmuxペインタイトル更新
                result = subprocess.run(
                    ["tmux", "select-pane", "-t", pane_target, "-T", title],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    self.logger.error(
                        f"Failed to set title for {pane_target}: {result.stderr}"
                    )
                else:
                    self.logger.debug(f"Successfully updated title for {pane_target}")

            except Exception as e:
                self.logger.error(f"Error updating statusbar for {pane_target}: {e}")

    def _get_pane_content(self, pane_target: str, lines: int = 50) -> str:
        """ペイン内容取得"""
        try:
            # 最新N行を取得
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", pane_target, "-p", "-S", f"-{lines}"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except Exception:
            return ""

    def _session_exists(self, session_name: str) -> bool:
        """セッション存在確認"""
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_current_tasks(self) -> Dict[str, Any]:
        """現在のタスク一覧取得（日本語）"""
        tasks = {}
        for _pane_target, state in self.worker_states.items():
            translated_role = self._translate_role(state.role)

            if state.current_task:
                translated_task = self._translate_task(
                    state.current_task.task_description
                )
                tasks[translated_role] = {
                    "task": translated_task,
                    "original_task": state.current_task.task_description,  # 元のタスクも保持
                    "type": state.current_task.task_type,
                    "files": state.current_task.target_files,
                    "started": state.current_task.started_at.isoformat(),
                }
            else:
                idle_text = "待機中" if self.language == "ja" else "Idle"
                tasks[translated_role] = {"task": idle_text, "type": "idle"}

        return {
            "timestamp": datetime.now().isoformat(),
            "language": self.language,
            "tasks": tasks,
            "active_workers": sum(
                1 for s in self.worker_states.values() if s.is_active
            ),
        }

    def force_update(self):
        """強制更新"""
        self.logger.info("Forcing task display update...")
        for session_name, panes in self.worker_configs.items():
            if self._session_exists(session_name):
                for pane_id, config in panes.items():
                    self._update_worker_task(session_name, pane_id, config)
        self._update_all_statusbars()


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="Realtime Task Display System")
    parser.add_argument(
        "action",
        choices=["start", "status", "update", "set-language"],
        help="Action to perform",
    )
    parser.add_argument(
        "--language",
        choices=["ja", "en"],
        help="Language setting (ja=Japanese, en=English)",
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    system = RealtimeTaskDisplaySystem(args.project_root)

    if args.action == "start":
        print("Starting Realtime Task Display System...")
        system.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping system...")
            system.stop_monitoring()

    elif args.action == "status":
        tasks = system.get_current_tasks()
        print(json.dumps(tasks, indent=2, ensure_ascii=False))

    elif args.action == "update":
        system.force_update()
        print("Task display updated")

    elif args.action == "set-language":
        if not args.language:
            print("Error: --language required for set-language action")
            print("Usage: --language ja (Japanese) or --language en (English)")
            sys.exit(1)

        success = system.set_language(args.language)
        if success:
            lang_name = "Japanese" if args.language == "ja" else "English"
            print(f"Language changed to: {lang_name}")
        else:
            print("Failed to change language")


if __name__ == "__main__":
    main()
