#!/usr/bin/env python3
"""
Tmux StatusBar Enforcer - 完璧なステータスバー設定システム
===========================================================
AIワーカーのステータスバーを完璧に設定・維持する自動システム

Features:
- ペインタイトル自動設定・監視
- リアルタイム状態表示
- 設定永続化・復旧
- カスタムステータスバー生成
- 自動リフレッシュ機能
"""

import json
import logging
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


@dataclass
class PaneConfig:
    """ペイン設定"""

    pane_id: str
    title: str
    role: str
    status_format: str
    color_scheme: str
    update_interval: int = 5


@dataclass
class StatusBarConfig:
    """ステータスバー設定"""

    session_name: str
    pane_configs: List[PaneConfig]
    status_line_format: str
    refresh_interval: int
    color_theme: str
    show_time: bool = True
    show_session_info: bool = True


class TmuxStatusBarEnforcer:
    """完璧なtmuxステータスバー設定・維持システム"""

    def __init__(self, project_root: str = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        )
        self.runtime_dir = self.project_root / "runtime"
        self.config_file = self.runtime_dir / "tmux_statusbar_config.json"
        self.running = False

        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.runtime_dir / "logs" / "tmux_statusbar.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("tmux-statusbar")

        # AI組織用デフォルト設定
        self.default_configs = self._create_default_configs()

        # 監視スレッド
        self.monitor_thread = None

    def _create_default_configs(self) -> Dict[str, StatusBarConfig]:
        """デフォルトステータスバー設定作成"""

        # AI組織マルチエージェント設定
        multiagent_panes = [
            PaneConfig(
                pane_id="0.0",
                title="👔 部長",
                role="BOSS1",
                status_format="#{pane_title} | #{pane_current_command} | #{pane_pid}",
                color_scheme="colour33",  # Blue
            ),
            PaneConfig(
                pane_id="0.1",
                title="💻 作業員1",
                role="WORKER1",
                status_format="#{pane_title} | #{pane_current_command} | #{pane_pid}",
                color_scheme="colour39",  # Blue gradient
            ),
            PaneConfig(
                pane_id="0.2",
                title="🔧 作業員2",
                role="WORKER2",
                status_format="#{pane_title} | #{pane_current_command} | #{pane_pid}",
                color_scheme="colour45",  # Blue gradient
            ),
            PaneConfig(
                pane_id="0.3",
                title="🎨 作業員3",
                role="WORKER3",
                status_format="#{pane_title} | #{pane_current_command} | #{pane_pid}",
                color_scheme="colour51",  # Blue gradient
            ),
        ]

        multiagent_config = StatusBarConfig(
            session_name="multiagent",
            pane_configs=multiagent_panes,
            status_line_format="🤖 AI組織システム | Active: #{session_attached} | Panes: #{session_windows} | %Y-%m-%d %H:%M:%S",
            refresh_interval=5,
            color_theme="professional",
            show_time=True,
            show_session_info=True,
        )

        # PRESIDENT設定
        president_config = StatusBarConfig(
            session_name="president",
            pane_configs=[
                PaneConfig(
                    pane_id="0",
                    title="👑 PRESIDENT",
                    role="PRESIDENT",
                    status_format="#{pane_title} | #{pane_current_command} | #{pane_pid}",
                    color_scheme="colour220",  # Gold
                )
            ],
            status_line_format="👑 PRESIDENT システム | %Y-%m-%d %H:%M:%S",
            refresh_interval=5,
            color_theme="executive",
            show_time=True,
            show_session_info=True,
        )

        return {"multiagent": multiagent_config, "president": president_config}

    def apply_perfect_statusbar_config(self, session_name: str) -> bool:
        """完璧なステータスバー設定適用"""
        try:
            self.logger.info(
                f"Applying perfect statusbar config for session: {session_name}"
            )

            config = self.default_configs.get(session_name)
            if not config:
                self.logger.error(f"No configuration found for session: {session_name}")
                return False

            # セッション存在確認
            if not self._session_exists(session_name):
                self.logger.error(f"Session {session_name} does not exist")
                return False

            # 基本ステータスバー設定
            success = True
            success &= self._apply_session_status_options(session_name, config)
            success &= self._apply_pane_configurations(session_name, config)
            success &= self._apply_status_line_format(session_name, config)
            success &= self._apply_color_scheme(session_name, config)

            if success:
                self.logger.info(
                    f"✅ Perfect statusbar configuration applied for {session_name}"
                )
                # 設定保存
                self._save_config(session_name, config)
                return True
            else:
                self.logger.error(
                    f"❌ Failed to apply statusbar configuration for {session_name}"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error applying statusbar config for {session_name}: {e}"
            )
            return False

    def _apply_session_status_options(
        self, session_name: str, config: StatusBarConfig
    ) -> bool:
        """セッション基本ステータス設定"""
        try:
            commands = [
                # ステータスバー有効化
                ["tmux", "set-option", "-t", session_name, "status", "on"],
                # ペインボーダーステータス設定
                ["tmux", "set-option", "-t", session_name, "pane-border-status", "top"],
                # ペインタイトル表示フォーマット（白色テキスト）
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "pane-border-format",
                    "#{?pane_active,#[bg=colour46#,fg=white],#[bg=colour240#,fg=white]} #{pane_title} #[default]",
                ],
                # ステータス更新間隔
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "status-interval",
                    str(config.refresh_interval),
                ],
                # ステータスバー位置
                ["tmux", "set-option", "-t", session_name, "status-position", "bottom"],
                # ステータスバー長さ
                ["tmux", "set-option", "-t", session_name, "status-left-length", "40"],
                ["tmux", "set-option", "-t", session_name, "status-right-length", "80"],
                # ペインタイトル自動設定許可
                ["tmux", "set-option", "-t", session_name, "allow-rename", "on"],
                ["tmux", "set-option", "-t", session_name, "automatic-rename", "off"],
            ]

            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Failed to execute: {' '.join(cmd)}")
                    self.logger.error(f"Error: {result.stderr}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error applying session status options: {e}")
            return False

    def _apply_pane_configurations(
        self, session_name: str, config: StatusBarConfig
    ) -> bool:
        """ペイン設定適用"""
        try:
            for pane_config in config.pane_configs:
                pane_target = f"{session_name}:{pane_config.pane_id}"

                # ペインタイトル設定
                cmd_title = [
                    "tmux",
                    "select-pane",
                    "-t",
                    pane_target,
                    "-T",
                    pane_config.title,
                ]
                result = subprocess.run(cmd_title, capture_output=True, text=True)

                if result.returncode != 0:
                    self.logger.warning(
                        f"Failed to set title for pane {pane_target}: {result.stderr}"
                    )
                    # エラーでも続行
                else:
                    self.logger.info(
                        f"✅ Set title '{pane_config.title}' for pane {pane_target}"
                    )

                # ペイン専用設定（存在する場合）
                if hasattr(pane_config, "color_scheme") and pane_config.color_scheme:
                    # ペインボーダー色設定
                    try:
                        cmd_color = [
                            "tmux",
                            "select-pane",
                            "-t",
                            pane_target,
                            "-P",
                            f"fg={pane_config.color_scheme}",
                        ]
                        subprocess.run(
                            cmd_color, capture_output=True, text=True, check=False
                        )
                    except Exception:
                        pass  # カラー設定失敗は無視

            return True

        except Exception as e:
            self.logger.error(f"Error applying pane configurations: {e}")
            return False

    def _apply_status_line_format(
        self, session_name: str, config: StatusBarConfig
    ) -> bool:
        """ステータスライン形式設定"""
        try:
            # セッション固有のステータスライン
            status_left = f"#[bg=colour33,fg=colour16,bold] {config.session_name.upper()} #[default]"

            if config.show_session_info:
                status_left += " #[fg=colour245]#S:#I.#P#[default]"

            status_right = ""
            if config.show_time:
                status_right = "#[fg=colour245]%Y-%m-%d #[fg=colour255,bold]%H:%M:%S"

            commands = [
                ["tmux", "set-option", "-t", session_name, "status-left", status_left],
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "status-right",
                    status_right,
                ],
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "status-style",
                    "bg=colour235,fg=colour255",
                ],
            ]

            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.warning(f"Failed to execute: {' '.join(cmd)}")

            return True

        except Exception as e:
            self.logger.error(f"Error applying status line format: {e}")
            return False

    def _apply_color_scheme(self, session_name: str, config: StatusBarConfig) -> bool:
        """カラースキーム適用"""
        try:
            if config.color_theme == "professional":
                # プロフェッショナルテーマ
                commands = [
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "pane-active-border-style",
                        "fg=colour46",
                    ],
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "pane-border-style",
                        "fg=colour240",
                    ],
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "window-status-current-style",
                        "bg=colour46,fg=colour16,bold",
                    ],
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "window-status-style",
                        "bg=colour240,fg=colour255",
                    ],
                ]
            elif config.color_theme == "executive":
                # エグゼクティブテーマ（PRESIDENT用）
                commands = [
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "pane-active-border-style",
                        "fg=colour220",
                    ],
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "pane-border-style",
                        "fg=colour240",
                    ],
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "window-status-current-style",
                        "bg=colour220,fg=colour16,bold",
                    ],
                    [
                        "tmux",
                        "set-option",
                        "-t",
                        session_name,
                        "window-status-style",
                        "bg=colour240,fg=colour255",
                    ],
                ]
            else:
                return True  # デフォルトカラー使用

            for cmd in commands:
                subprocess.run(cmd, capture_output=True, text=True, check=False)

            return True

        except Exception as e:
            self.logger.error(f"Error applying color scheme: {e}")
            return False

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

    def _save_config(self, session_name: str, config: StatusBarConfig):
        """設定保存"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # 既存設定読み込み
            configs = {}
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    configs = json.load(f)

            # 新しい設定追加
            configs[session_name] = asdict(config)
            configs["last_updated"] = datetime.now().isoformat()

            # 設定保存
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Configuration saved for {session_name}")

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")

    def start_continuous_monitoring(self):
        """継続的監視開始"""
        if self.running:
            self.logger.warning("Monitoring already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_sessions, daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Started continuous statusbar monitoring")

    def stop_monitoring(self):
        """監視停止"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Stopped statusbar monitoring")

    def _monitor_sessions(self):
        """セッション監視ループ"""
        while self.running:
            try:
                for session_name in self.default_configs.keys():
                    if self._session_exists(session_name):
                        # ステータスバー設定確認・修復
                        self._verify_and_fix_statusbar(session_name)

                time.sleep(30)  # 30秒間隔で監視

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)

    def _verify_and_fix_statusbar(self, session_name: str):
        """ステータスバー設定確認・修復"""
        try:
            # 現在の設定確認
            result = subprocess.run(
                ["tmux", "show-options", "-t", session_name, "pane-border-status"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0 or "top" not in result.stdout:
                self.logger.warning(
                    f"Statusbar configuration drift detected for {session_name}"
                )
                # 設定再適用
                self.apply_perfect_statusbar_config(session_name)

        except Exception as e:
            self.logger.error(f"Error verifying statusbar for {session_name}: {e}")

    def apply_all_sessions(self) -> Dict[str, bool]:
        """全セッション設定適用"""
        results = {}

        for session_name in self.default_configs.keys():
            if self._session_exists(session_name):
                results[session_name] = self.apply_perfect_statusbar_config(
                    session_name
                )
            else:
                self.logger.warning(f"Session {session_name} does not exist")
                results[session_name] = False

        return results

    def get_status_report(self) -> Dict[str, Any]:
        """ステータスバー状態レポート"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "sessions": {},
            "monitoring_active": self.running,
        }

        for session_name in self.default_configs.keys():
            if self._session_exists(session_name):
                # セッション詳細取得
                try:
                    result = subprocess.run(
                        [
                            "tmux",
                            "list-panes",
                            "-t",
                            session_name,
                            "-F",
                            "#{pane_id}:#{pane_title}:#{pane_current_command}",
                        ],
                        capture_output=True,
                        text=True,
                    )

                    panes = []
                    if result.returncode == 0:
                        for line in result.stdout.strip().split("\n"):
                            if line:
                                parts = line.split(":", 2)
                                if len(parts) >= 2:
                                    panes.append(
                                        {
                                            "pane_id": parts[0],
                                            "title": parts[1] if len(parts) > 1 else "",
                                            "command": parts[2]
                                            if len(parts) > 2
                                            else "",
                                        }
                                    )

                    report["sessions"][session_name] = {
                        "exists": True,
                        "panes": panes,
                        "pane_count": len(panes),
                    }

                except Exception as e:
                    report["sessions"][session_name] = {"exists": True, "error": str(e)}
            else:
                report["sessions"][session_name] = {"exists": False}

        return report


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="Tmux StatusBar Enforcer")
    parser.add_argument(
        "action",
        choices=["apply", "monitor", "status", "apply-all"],
        help="Action to perform",
    )
    parser.add_argument("--session", help="Specific session name")
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    enforcer = TmuxStatusBarEnforcer(args.project_root)

    if args.action == "apply":
        if not args.session:
            print("Error: --session required for apply action")
            sys.exit(1)

        success = enforcer.apply_perfect_statusbar_config(args.session)
        print(
            f"StatusBar configuration for {args.session}: {'SUCCESS' if success else 'FAILED'}"
        )

    elif args.action == "apply-all":
        results = enforcer.apply_all_sessions()
        print("StatusBar configuration results:")
        for session, success in results.items():
            print(f"  {session}: {'SUCCESS' if success else 'FAILED'}")

    elif args.action == "monitor":
        print("Starting continuous statusbar monitoring...")
        enforcer.start_continuous_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            enforcer.stop_monitoring()

    elif args.action == "status":
        report = enforcer.get_status_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
