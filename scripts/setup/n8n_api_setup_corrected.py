#!/usr/bin/env python3
"""
n8n API セットアップ - 公式ドキュメント準拠版
o3からの最新情報とJWTトークンを使用した確実なセットアップ
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

import requests


class N8nApiSetupCorrected:
    """n8n API セットアップ（修正版）"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")

        # .envファイルから設定読み込み
        self._load_env_vars()

        # APIエンドポイント（公式ドキュメント準拠）
        self.base_url = self.n8n_api_url.rstrip("/")

        # セッション設定
        self.session = requests.Session()

        # 認証設定 - JWTトークンを使用
        if self.n8n_api_key:
            # JWTトークンの場合
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.n8n_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "n8n-autonomous-growth-setup/1.0",
                }
            )

        # ログ設定
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("n8n_setup")

        # ワークフローファイル
        self.workflow_files = [
            "config/n8n/workflows/ai_performance_tracker.json",
            "config/n8n/workflows/autonomous_prompt_evolution.json",
        ]

    def _load_env_vars(self):
        """環境変数読み込み"""
        env_file = self.project_root / ".env"

        # デフォルト値
        self.n8n_api_key = None
        self.n8n_api_url = "https://n8n.cloud"

        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        if key == "N8N_API_KEY":
                            self.n8n_api_key = value
                        elif key == "N8N_API_URL":
                            self.n8n_api_url = value

        # 環境変数でオーバーライド
        self.n8n_api_key = os.getenv("N8N_API_KEY", self.n8n_api_key)
        self.n8n_api_url = os.getenv("N8N_API_URL", self.n8n_api_url)

    def test_api_connection(self) -> bool:
        """API接続テスト"""
        print("🔍 n8n API接続テスト中...")

        if not self.n8n_api_key:
            print("❌ N8N_API_KEY が設定されていません")
            return False

        # 複数のエンドポイントを試行
        test_endpoints = ["/api/v1/workflows", "/api/workflows", "/rest/workflows"]

        for endpoint in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=10)

                print(f"   テスト: {endpoint} -> {response.status_code}")

                if response.status_code == 200:
                    print(f"✅ API接続成功: {endpoint}")
                    self.api_endpoint = endpoint
                    return True
                elif response.status_code == 401:
                    print(f"   認証エラー: {endpoint}")
                elif response.status_code == 403:
                    print(f"   アクセス拒否: {endpoint}")
                else:
                    print(f"   その他エラー: {endpoint}")

            except requests.exceptions.RequestException as e:
                print(f"   接続エラー: {endpoint} - {e}")

        print("❌ 全てのエンドポイントで接続失敗")
        return False

    def import_workflow_safe(self, workflow_file: str) -> Optional[str]:
        """安全なワークフローインポート"""
        file_path = self.project_root / workflow_file

        if not file_path.exists():
            print(f"❌ ファイルが見つかりません: {workflow_file}")
            return None

        try:
            # ワークフローJSON読み込み
            with open(file_path, encoding="utf-8") as f:
                workflow_data = json.load(f)

            # IDフィールドを削除（衝突防止）
            if "id" in workflow_data:
                del workflow_data["id"]

            # ワークフロー名取得
            workflow_name = workflow_data.get("name", "Unknown Workflow")
            print(f"📥 インポート中: {workflow_name}")

            # インポート実行
            url = f"{self.base_url}{self.api_endpoint}"
            response = self.session.post(url, json=workflow_data, timeout=30)

            if response.status_code in [200, 201]:
                result = response.json()
                workflow_id = result.get("id")

                print(f"✅ インポート成功: {workflow_name} (ID: {workflow_id})")

                # ワークフロー有効化
                if workflow_id:
                    self._activate_workflow(workflow_id, workflow_name)

                return workflow_id

            else:
                print(f"❌ インポート失敗: {workflow_name}")
                print(f"   ステータス: {response.status_code}")
                print(f"   レスポンス: {response.text[:200]}...")
                return None

        except Exception as e:
            print(f"❌ ワークフロー処理エラー: {workflow_file} - {e}")
            return None

    def _activate_workflow(self, workflow_id: str, workflow_name: str):
        """ワークフロー有効化"""
        try:
            # 有効化エンドポイント
            activate_endpoints = [
                f"{self.api_endpoint}/{workflow_id}/activate",
                f"{self.api_endpoint}/{workflow_id}",
            ]

            for endpoint in activate_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"

                    # 最初のエンドポイントはPOST、2番目はPATCH
                    if "activate" in endpoint:
                        response = self.session.post(url, timeout=10)
                    else:
                        response = self.session.patch(
                            url, json={"active": True}, timeout=10
                        )

                    if response.status_code in [200, 204]:
                        print(f"✅ ワークフロー有効化成功: {workflow_name}")
                        return

                except Exception:
                    continue

            print(f"⚠️ ワークフロー有効化スキップ: {workflow_name}")

        except Exception as e:
            print(f"❌ 有効化エラー: {workflow_name} - {e}")

    def extract_webhook_url(self, workflow_id: str) -> Optional[str]:
        """Webhook URL抽出"""
        try:
            url = f"{self.base_url}{self.api_endpoint}/{workflow_id}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                workflow_data = response.json()

                # Webhook node検索
                for node in workflow_data.get("nodes", []):
                    if node.get("type") == "n8n-nodes-base.webhook":
                        # Webhook URL構築
                        webhook_path = node.get("webhookId") or node.get(
                            "parameters", {}
                        ).get("path", "")
                        if webhook_path:
                            webhook_url = f"{self.base_url}/webhook/{webhook_path}"
                            return webhook_url

        except Exception as e:
            print(f"❌ Webhook URL抽出エラー: {e}")

        return None

    def run_setup(self) -> bool:
        """メインセットアップ実行"""
        print("🚀 n8n API セットアップ開始")
        print("=" * 50)

        # API接続テスト
        if not self.test_api_connection():
            print("\n💡 代替案:")
            print("1. Web UI経由でのマニュアルインポート")
            print("2. python3 scripts/setup/simple_n8n_setup.py")
            return False

        # ワークフローインポート
        workflow_results = {}
        webhook_urls = {}

        for workflow_file in self.workflow_files:
            workflow_id = self.import_workflow_safe(workflow_file)
            if workflow_id:
                workflow_name = Path(workflow_file).stem
                workflow_results[workflow_name] = workflow_id

                # Webhook URL抽出
                webhook_url = self.extract_webhook_url(workflow_id)
                if webhook_url:
                    webhook_urls[workflow_name] = webhook_url

        if not workflow_results:
            print("❌ ワークフローインポートに失敗しました")
            return False

        # 環境変数設定
        self._update_environment_variables(webhook_urls)

        # 完了レポート
        self._generate_completion_report(workflow_results, webhook_urls)

        return True

    def _update_environment_variables(self, webhook_urls: Dict[str, str]):
        """環境変数更新"""
        print("\n🌍 環境変数更新中...")

        env_file = self.project_root / ".env"

        # 現在の.env読み込み
        env_vars = {}
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value

        # Webhook URL設定
        for name, url in webhook_urls.items():
            if "performance_tracker" in name.lower():
                env_vars["N8N_WEBHOOK_URL"] = url

        # その他設定
        env_vars.update(
            {"AUTONOMOUS_GROWTH_ENABLED": "true", "N8N_SETUP_COMPLETED": "true"}
        )

        # 書き込み
        with open(env_file, "w") as f:
            f.write("# n8n Autonomous Growth System - API Setup\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        print(f"✅ 環境変数更新完了: {env_file}")

    def _generate_completion_report(self, workflow_results: Dict, webhook_urls: Dict):
        """完了レポート"""
        print("\n" + "=" * 60)
        print("🎉 n8n API セットアップ完了")
        print("=" * 60)

        print("\n📊 インポート結果:")
        for name, workflow_id in workflow_results.items():
            print(f"   ✅ {name}: {workflow_id}")

        print("\n🔗 Webhook URLs:")
        for name, url in webhook_urls.items():
            print(f"   📍 {name}: {url}")

        print("\n🚀 次のステップ:")
        print("   1. python3 scripts/hooks/autonomous_growth_hook.py test")
        print("   2. python3 src/ai/autonomous_growth_engine.py")
        print("   3. Claude Code使用でAI自律成長開始!")


def main():
    """メイン実行"""
    setup = N8nApiSetupCorrected()

    if not setup.n8n_api_key:
        print("❌ N8N_API_KEY が設定されていません")
        print("   .env ファイルまたは環境変数で設定してください")
        return False

    return setup.run_setup()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
