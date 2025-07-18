#!/usr/bin/env python3
"""
n8n画像作成ツールワークフロー作成
"""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


def create_image_creation_tool():
    """画像作成ツールワークフロー作成"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    timestamp = int(datetime.now().timestamp())
    workflow_name = f"Image Creation Tool v{timestamp}"

    print("🎨 画像作成ツールワークフロー作成")
    print("=" * 50)
    print(f"名前: {workflow_name}")

    # 他のワークフローからの実行トリガー
    execute_trigger = {
        "parameters": {},
        "id": "execute_trigger",
        "name": "When executed by workflow",
        "type": "n8n-nodes-base.executeWorkflowTrigger",
        "typeVersion": 1,
        "position": [240, 300],
    }

    # Image Prompt Agent (OpenAI)
    image_prompt_agent = {
        "parameters": {
            "model": "gpt-4",
            "messages": {
                "values": [
                    {
                        "content": """あなたは画像生成プロンプトの専門家です。ユーザーからのテキストを、画像生成モデル用の非常に記述的で詳細なプロンプトに変換してください。

プロンプトには以下を含めてください：
- 主要な主題の詳細な説明
- 背景とシーン設定
- アートスタイル（写真的、イラスト、3D等）
- 照明と色彩
- 構図と視点
- 追加の視覚的詳細

英語で応答し、プロンプトのみを出力してください。""",
                        "role": "system",
                    },
                    {"content": "={{$json.image_prompt}}", "role": "user"},
                ]
            },
            "options": {"temperature": 0.8},
        },
        "id": "image_prompt_agent",
        "name": "Image Prompt Agent",
        "type": "@n8n/n8n-nodes-langchain.openAi",
        "typeVersion": 1,
        "position": [440, 300],
    }

    # OpenAI画像生成HTTP Request
    openai_image_request = {
        "parameters": {
            "url": "https://api.openai.com/v1/images/generations",
            "requestMethod": "POST",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization", "value": f"Bearer {openai_api_key}"},
                    {"name": "Content-Type", "value": "application/json"},
                ]
            },
            "sendBody": True,
            "bodyContentType": "json",
            "jsonParameters": True,
            "bodyParameters": {
                "parameters": [
                    {"name": "model", "value": "dall-e-3"},
                    {
                        "name": "prompt",
                        "value": "={{$json.choices[0].message.content}}",
                    },
                    {"name": "n", "value": 1},
                    {"name": "size", "value": "1024x1024"},
                    {"name": "response_format", "value": "b64_json"},
                ]
            },
        },
        "id": "openai_image_gen",
        "name": "OpenAI Image Generation",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.1,
        "position": [640, 300],
    }

    # Convert to File (Base64からバイナリデータへ変換)
    convert_to_file = {
        "parameters": {
            "options": {
                "fileName": "={{$('When executed by workflow').first().$json.image_title}}.png"
            },
            "dataPropertyName": "data.data[0].b64_json",
            "encoding": "base64",
        },
        "id": "convert_to_file",
        "name": "Convert to File",
        "type": "n8n-nodes-base.convertToFile",
        "typeVersion": 1,
        "position": [840, 300],
    }

    # ファイル情報設定
    set_file_info = {
        "parameters": {
            "keepOnlySet": False,
            "values": {
                "string": [
                    {
                        "name": "image_title",
                        "value": "={{$('When executed by workflow').first().$json.image_title}}",
                    },
                    {
                        "name": "image_prompt",
                        "value": "={{$('When executed by workflow').first().$json.image_prompt}}",
                    },
                    {
                        "name": "telegram_chat_id",
                        "value": "={{$('When executed by workflow').first().$json.telegram_chat_id}}",
                    },
                    {
                        "name": "generated_prompt",
                        "value": "={{$('Image Prompt Agent').first().$json.choices[0].message.content}}",
                    },
                    {"name": "file_name", "value": "={{$json.fileName}}"},
                    {
                        "name": "creation_timestamp",
                        "value": "={{new Date().toISOString()}}",
                    },
                ],
                "object": [{"name": "file_data", "value": "={{$json.data}}"}],
            },
        },
        "id": "set_file_info",
        "name": "Set File Info",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.2,
        "position": [1040, 300],
    }

    # Telegram送信ノード（モックアップ）
    telegram_mock = {
        "parameters": {
            "keepOnlySet": False,
            "values": {
                "string": [
                    {"name": "telegram_status", "value": "success_mock"},
                    {
                        "name": "message",
                        "value": "画像をTelegramに送信しました（モック）: ={{$json.file_name}}",
                    },
                ]
            },
        },
        "id": "telegram_mock",
        "name": "Telegram Send (Mock)",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.2,
        "position": [1240, 200],
    }

    # ログ記録ノード（Supabase代替）
    log_creation = {
        "parameters": {
            "url": f"{os.getenv('SUPABASE_URL')}/rest/v1/marketing_image_log",
            "requestMethod": "POST",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "apikey", "value": os.getenv("SUPABASE_ANON_KEY")},
                    {
                        "name": "Authorization",
                        "value": f"Bearer {os.getenv('SUPABASE_ANON_KEY')}",
                    },
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"},
                ]
            },
            "sendBody": True,
            "bodyContentType": "json",
            "jsonParameters": True,
            "bodyParameters": {
                "parameters": [
                    {"name": "title", "value": "={{$json.image_title}}"},
                    {"name": "type", "value": "image"},
                    {"name": "request", "value": "={{$json.image_prompt}}"},
                    {
                        "name": "generated_prompt",
                        "value": "={{$json.generated_prompt}}",
                    },
                    {"name": "file_name", "value": "={{$json.file_name}}"},
                    {
                        "name": "creation_timestamp",
                        "value": "={{$json.creation_timestamp}}",
                    },
                    {
                        "name": "telegram_chat_id",
                        "value": "={{$json.telegram_chat_id}}",
                    },
                ]
            },
        },
        "id": "log_creation",
        "name": "Log to Database",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.1,
        "position": [1240, 400],
    }

    # 成功応答
    success_response = {
        "parameters": {
            "keepOnlySet": False,
            "values": {
                "string": [
                    {"name": "status", "value": "success"},
                    {
                        "name": "message",
                        "value": "画像「={{$('Set File Info').first().$json.image_title}}」を正常に作成しました",
                    },
                    {
                        "name": "file_name",
                        "value": "={{$('Set File Info').first().$json.file_name}}",
                    },
                ]
            },
        },
        "id": "success_response",
        "name": "Success Response",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.2,
        "position": [1440, 300],
    }

    # ワークフロー定義
    workflow_data = {
        "name": workflow_name,
        "nodes": [
            execute_trigger,
            image_prompt_agent,
            openai_image_request,
            convert_to_file,
            set_file_info,
            telegram_mock,
            log_creation,
            success_response,
        ],
        "connections": {
            "When executed by workflow": {
                "main": [[{"node": "Image Prompt Agent", "type": "main", "index": 0}]]
            },
            "Image Prompt Agent": {
                "main": [
                    [{"node": "OpenAI Image Generation", "type": "main", "index": 0}]
                ]
            },
            "OpenAI Image Generation": {
                "main": [[{"node": "Convert to File", "type": "main", "index": 0}]]
            },
            "Convert to File": {
                "main": [[{"node": "Set File Info", "type": "main", "index": 0}]]
            },
            "Set File Info": {
                "main": [
                    [
                        {"node": "Telegram Send (Mock)", "type": "main", "index": 0},
                        {"node": "Log to Database", "type": "main", "index": 0},
                    ]
                ]
            },
            "Telegram Send (Mock)": {
                "main": [[{"node": "Success Response", "type": "main", "index": 0}]]
            },
            "Log to Database": {
                "main": [[{"node": "Success Response", "type": "main", "index": 0}]]
            },
        },
        "settings": {"timezone": "Asia/Tokyo"},
    }

    # ワークフロー作成
    response = requests.post(
        f"{base_url}/api/v1/workflows", headers=headers, json=workflow_data
    )

    if response.status_code in [200, 201]:
        result = response.json()
        workflow_id = result["id"]

        print(f"✅ 画像作成ツール作成成功: {workflow_id}")

        # アクティブ化
        activate_response = requests.post(
            f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers
        )
        print(f"⚡ アクティブ化試行: {activate_response.status_code}")

        print("🎨 画像作成ツール準備完了")

        return True, workflow_id, workflow_name
    else:
        print(f"❌ 作成失敗: {response.status_code} - {response.text}")
        return False, None, None


if __name__ == "__main__":
    success, workflow_id, name = create_image_creation_tool()

    if success:
        print("\n🎊 **画像作成ツール作成成功** 🎊")
        print(f"🆔 ID: {workflow_id}")
        print(f"📝 名前: {name}")
        print("\n機能:")
        print("✅ OpenAI DALL-E 3画像生成")
        print("✅ プロンプト最適化エージェント")
        print("✅ ファイル変換")
        print("✅ データベースログ記録")
        print("⚠️ Telegramはモック実装")
        print("⚠️ Google Driveはスキップ")
    else:
        print("\n❌ **画像作成ツール作成失敗**")
