#!/usr/bin/env python3
"""
🎮 Claude Code 4-Pane Launcher - 4分割ペイン同時起動システム
==========================================================

Claude Code環境で4つのペインを同時起動し、各ペインに異なる役職を配置
プレジデント統括の下で並列処理を実現
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ClaudeCode4PaneLauncher:
    """Claude Code 4分割ペイン起動システム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.venv_path = self.project_root / ".venv"
        self.config_dir = self.project_root / "config"
        self.runtime_dir = self.project_root / "runtime"

        # 4分割ペイン構成
        self.pane_config = {
            "pane_1": {
                "role": "PRESIDENT",
                "display_name": "プレジデント",
                "icon": "👑",
                "authority": 10,
                "responsibilities": [
                    "全体戦略統括",
                    "意思決定",
                    "品質管理",
                    "最終承認",
                ],
                "command": "python3 src/ui/visual_dashboard.py dashboard",
                "priority": "CRITICAL",
            },
            "pane_2": {
                "role": "COORDINATOR",
                "display_name": "コーディネーター",
                "icon": "🔄",
                "authority": 8,
                "responsibilities": [
                    "タスク調整",
                    "進捗管理",
                    "リソース配分",
                    "チーム連携",
                ],
                "command": "python3 src/ai/ai_organization_system.py",
                "priority": "HIGH",
            },
            "pane_3": {
                "role": "ANALYST",
                "display_name": "要件アナリスト",
                "icon": "📋",
                "authority": 7,
                "responsibilities": ["要件分析", "仕様策定", "品質確認", "文書化"],
                "command": "python3 src/memory/unified_memory_manager.py",
                "priority": "HIGH",
            },
            "pane_4": {
                "role": "ENGINEER",
                "display_name": "システムエンジニア",
                "icon": "🔧",
                "authority": 6,
                "responsibilities": [
                    "システム実装",
                    "技術検証",
                    "コード生成",
                    "テスト実行",
                ],
                "command": "python3 src/conductor/core.py",
                "priority": "MEDIUM",
            },
        }

        # プロセス管理
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.process_status: Dict[str, str] = {}
        self.startup_order = ["pane_1", "pane_2", "pane_3", "pane_4"]

        # 設定ファイル
        self.session_file = self.runtime_dir / "pane_session.json"
        self.status_file = self.runtime_dir / "pane_status.json"

        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def launch_4pane_system(self) -> bool:
        """4分割ペインシステム起動"""
        print("🎮 Claude Code 4-Pane System Launcher")
        print("=" * 50)

        try:
            # 前準備
            self._prepare_environment()

            # セッション初期化
            self._initialize_session()

            # ペイン順次起動
            for pane_id in self.startup_order:
                success = self._launch_pane(pane_id)
                if not success:
                    print(f"❌ Failed to launch {pane_id}")
                    return False

                # 起動間隔
                time.sleep(2)

            # 起動完了確認
            self._verify_all_panes()

            # 監視モード開始
            self._start_monitoring()

            return True

        except Exception as e:
            print(f"❌ 4-Pane launch failed: {e}")
            self._cleanup_processes()
            return False

    def _prepare_environment(self):
        """環境準備"""
        print("🔧 Preparing environment...")

        # 必須ディレクトリ作成
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        # 仮想環境確認
        if not self.venv_path.exists():
            raise Exception("Virtual environment not found. Run setup first.")

        # 依存関係確認
        self._check_dependencies()

        print("✅ Environment prepared")

    def _check_dependencies(self):
        """依存関係確認"""
        activate_cmd = f"source {self.venv_path}/bin/activate"

        required_modules = ["rich", "pydantic", "psycopg2", "asyncio"]

        for module in required_modules:
            cmd = f"{activate_cmd} && python3 -c 'import {module}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"Missing dependency: {module}")

    def _initialize_session(self):
        """セッション初期化"""
        print("📋 Initializing session...")

        session_data = {
            "session_id": f"4pane_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "panes": self.pane_config,
            "status": "initializing",
            "processes": {},
        }

        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        print("✅ Session initialized")

    def _launch_pane(self, pane_id: str) -> bool:
        """個別ペイン起動"""
        pane_config = self.pane_config[pane_id]

        print(f"🚀 Launching {pane_id}: {pane_config['display_name']}")

        try:
            # 環境変数設定
            env = os.environ.copy()
            env["PANE_ID"] = pane_id
            env["PANE_ROLE"] = pane_config["role"]
            env["PANE_AUTHORITY"] = str(pane_config["authority"])
            env["PYTHONPATH"] = str(self.project_root)

            # 仮想環境アクティベート + コマンド実行
            activate_cmd = f"source {self.venv_path}/bin/activate"
            full_command = (
                f"{activate_cmd} && cd {self.project_root} && {pane_config['command']}"
            )

            # プロセス起動
            process = subprocess.Popen(
                full_command,
                shell=True,
                env=env,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid,  # プロセスグループ作成
            )

            # プロセス登録
            self.running_processes[pane_id] = process
            self.process_status[pane_id] = "running"

            # 起動確認
            time.sleep(1)
            if process.poll() is None:  # まだ動作中
                print(f"✅ {pane_id} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {pane_id} failed to start:")
                print(f"   stdout: {stdout}")
                print(f"   stderr: {stderr}")
                return False

        except Exception as e:
            print(f"❌ Error launching {pane_id}: {e}")
            return False

    def _verify_all_panes(self):
        """全ペイン起動確認"""
        print("🔍 Verifying all panes...")

        all_running = True
        for pane_id, process in self.running_processes.items():
            if process.poll() is not None:  # プロセス終了
                print(f"❌ {pane_id} is not running")
                all_running = False
            else:
                print(f"✅ {pane_id} is running (PID: {process.pid})")

        if all_running:
            print("🎉 All panes are running successfully!")
        else:
            raise Exception("Some panes failed to start")

    def _start_monitoring(self):
        """監視モード開始"""
        print("👁️  Starting monitoring mode...")
        print("Press Ctrl+C to stop all panes")

        try:
            while True:
                # プロセス状態確認
                for pane_id, process in self.running_processes.items():
                    if process.poll() is not None:  # プロセス終了
                        print(f"⚠️  {pane_id} has stopped unexpectedly")
                        self.process_status[pane_id] = "stopped"

                        # 自動再起動（オプション）
                        if self._should_restart(pane_id):
                            print(f"🔄 Restarting {pane_id}...")
                            self._launch_pane(pane_id)

                # ステータス更新
                self._update_status()

                # 監視間隔
                time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
        finally:
            self._cleanup_processes()

    def _should_restart(self, pane_id: str) -> bool:
        """自動再起動判定"""
        # PRESIDENT は常に再起動
        if pane_id == "pane_1":
            return True

        # 他のペインは3回まで再起動
        restart_count = self.process_status.get(f"{pane_id}_restart_count", 0)
        return restart_count < 3

    def _update_status(self):
        """ステータス更新"""
        status_data = {
            "updated_at": datetime.now().isoformat(),
            "panes": {},
            "system_status": "running",
        }

        for pane_id, process in self.running_processes.items():
            status_data["panes"][pane_id] = {
                "pid": process.pid,
                "status": "running" if process.poll() is None else "stopped",
                "role": self.pane_config[pane_id]["role"],
                "display_name": self.pane_config[pane_id]["display_name"],
            }

        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to update status: {e}")

    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        print(f"\n🚨 Received signal {signum}, shutting down...")
        self._cleanup_processes()
        sys.exit(0)

    def _cleanup_processes(self):
        """プロセスクリーンアップ"""
        print("🧹 Cleaning up processes...")

        for pane_id, process in self.running_processes.items():
            if process.poll() is None:  # まだ動作中
                try:
                    # プロセスグループ全体を終了
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                    # 猶予時間
                    time.sleep(2)

                    # 強制終了
                    if process.poll() is None:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)

                    print(f"✅ {pane_id} terminated")

                except Exception as e:
                    print(f"⚠️  Error terminating {pane_id}: {e}")

        print("✅ All processes cleaned up")

    def get_pane_status(self) -> Dict[str, Any]:
        """ペイン状態取得"""
        if not self.status_file.exists():
            return {"error": "Status file not found"}

        try:
            with open(self.status_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to read status: {e}"}

    def stop_pane(self, pane_id: str) -> bool:
        """個別ペイン停止"""
        if pane_id not in self.running_processes:
            return False

        process = self.running_processes[pane_id]
        if process.poll() is None:  # 動作中
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                time.sleep(1)
                if process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)

                print(f"✅ {pane_id} stopped")
                return True
            except Exception as e:
                print(f"❌ Error stopping {pane_id}: {e}")
                return False

        return True


def main():
    """メイン実行"""
    launcher = ClaudeCode4PaneLauncher()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            # ステータス確認
            status = launcher.get_pane_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif command == "stop":
            # 全ペイン停止
            launcher._cleanup_processes()
            print("✅ All panes stopped")

        elif command.startswith("stop-"):
            # 個別ペイン停止
            pane_id = command.replace("stop-", "")
            if launcher.stop_pane(pane_id):
                print(f"✅ {pane_id} stopped")
            else:
                print(f"❌ Failed to stop {pane_id}")

        else:
            print(
                "Usage: python3 claude_code_4pane_launcher.py [status|stop|stop-pane_1|stop-pane_2|stop-pane_3|stop-pane_4]"
            )

    else:
        # 4ペインシステム起動
        launcher.launch_4pane_system()


if __name__ == "__main__":
    main()
