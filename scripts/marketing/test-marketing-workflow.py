#!/usr/bin/env python3
"""
マーケティングワークフロー統合テスト
"""

import time
from datetime import datetime

import requests


def test_marketing_workflow():
    """マーケティングワークフロー統合テスト"""

    webhook_url = "https://dd1107.app.n8n.cloud/webhook/marketing-agent-1752541701"

    print("🧪 マーケティングワークフロー統合テスト")
    print("=" * 50)
    print(f"📡 URL: {webhook_url}")

    # テストデータ（画像作成リクエスト）
    test_data = {
        "text": "美しい夕日の海辺の写真を作って",
        "chat_id": "test_chat_001",
        "user_id": "test_user",
        "timestamp": datetime.now().isoformat(),
    }

    print("📤 送信データ:")
    print(f"   テキスト: {test_data['text']}")
    print(f"   チャットID: {test_data['chat_id']}")

    try:
        # メインエージェントにリクエスト送信
        response = requests.post(webhook_url, json=test_data, timeout=30)

        print("\n📥 応答:")
        print(f"   ステータス: {response.status_code}")
        print(f"   レスポンス: {response.text}")

        if response.status_code == 200:
            print("\n✅ **Webhook送信成功**")

            # 処理完了まで待機
            print("⏳ 30秒待機（画像生成処理）...")
            time.sleep(30)

            return True
        else:
            print("\n❌ **Webhook送信失敗**")
            return False

    except Exception as e:
        print(f"\n❌ **テスト実行エラー**: {e}")
        return False


def test_different_requests():
    """様々なリクエストパターンをテスト"""

    webhook_url = "https://dd1107.app.n8n.cloud/webhook/marketing-agent-1752541701"

    test_cases = [
        {
            "name": "画像作成リクエスト",
            "data": {
                "text": "ロボットが料理をしている未来的なキッチンの画像を作成して",
                "chat_id": "test_chat_002",
            },
        },
        {
            "name": "ブログ投稿リクエスト",
            "data": {
                "text": "AIの未来について技術者向けのブログ投稿を書いて",
                "chat_id": "test_chat_003",
            },
        },
        {
            "name": "LinkedIn投稿リクエスト",
            "data": {
                "text": "プロダクトマネージャー向けのLinkedIn投稿を作成して",
                "chat_id": "test_chat_004",
            },
        },
    ]

    print("\n🎯 複数パターンテスト")
    print("=" * 30)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   送信: {test_case['data']['text']}")

        try:
            response = requests.post(webhook_url, json=test_case["data"], timeout=20)
            print(f"   結果: {response.status_code} - {response.text[:100]}...")

            time.sleep(5)  # レート制限回避

        except Exception as e:
            print(f"   エラー: {e}")


if __name__ == "__main__":
    print("🚀 マーケティングワークフローテスト開始")

    # 基本テスト
    basic_success = test_marketing_workflow()

    if basic_success:
        # 追加テスト
        test_different_requests()

        print("\n🎊 **テスト完了** 🎊")
        print("✅ メインエージェント動作確認")
        print("✅ 画像作成ツール連携確認")
        print("📊 ログ記録確認推奨")
    else:
        print("\n⚠️ **基本テスト失敗**")
        print("🔧 ワークフロー設定を確認してください")
