#!/usr/bin/env python3
"""
n8nマーケティングチームメインエージェントワークフロー作成
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_main_agent_workflow():
    """メインマーケティングエージェントワークフロー作成"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    timestamp = int(datetime.now().timestamp())
    workflow_name = f"Marketing Team Agent v{timestamp}"
    webhook_path = f"marketing-agent-{timestamp}"
    
    print("🎯 マーケティングチームメインエージェント作成")
    print("="*60)
    print(f"名前: {workflow_name}")
    print(f"Path: {webhook_path}")
    
    # Webhookトリガーノード (Telegram入力受信)
    webhook_node = {
        "parameters": {
            "httpMethod": "POST",
            "path": webhook_path,
            "responseMode": "onReceived"
        },
        "id": "marketing_webhook",
        "name": "Marketing Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [240, 300]
    }
    
    # メインマーケティングエージェント（OpenAI）
    main_agent_node = {
        "parameters": {
            "model": "gpt-4",
            "messages": {
                "values": [
                    {
                        "content": """概要：あなたはマーケティングチームのAIエージェントです。あなたの仕事は、ユーザーが要求に基づいて画像を「作成」したり「編集」したり、コンテンツを「作成」したりするのを助けることです。

利用可能なツール：
- create_image: 画像作成に使用
- edit_image: 画像編集に使用（ユーザーが「make」と言った場合も編集と判断）
- image_database: 画像データベースの検索に使用
- blog_post: ブログ投稿の作成に使用
- linkedin_post: LinkedIn投稿の作成に使用
- video: 動画作成に使用

追加指示：
- ユーザーが「その画像を編集してほしい」または「それを何か作ってほしい」と要求した場合、データベース内の最新の画像を編集したいことを示します
- ブログ投稿またはLinkedIn投稿を要求された場合、「リクエストされた投稿はこちらです。お楽しみください。」と出力します

応答形式は以下のJSONで回答してください：
{
  "tool": "使用するツール名",
  "parameters": {
    "image_title": "画像タイトル（最大4語）",
    "image_prompt": "画像の説明",
    "blog_topic": "ブログトピック",
    "target_audience": "ターゲットオーディエンス",
    "topic_of_video": "動画のトピック",
    "request": "編集内容の要求",
    "image_title_search": "検索する画像のタイトル",
    "intent": "get_image または edit_image"
  },
  "telegram_chat_id": "={{$json.chat_id}}",
  "response": "ユーザーへの応答メッセージ"
}""",
                        "role": "system"
                    },
                    {
                        "content": "={{$json.text}}",
                        "role": "user"
                    }
                ]
            },
            "options": {
                "temperature": 0.7
            }
        },
        "id": "main_agent",
        "name": "Marketing Team Agent",
        "type": "@n8n/n8n-nodes-langchain.openAi",
        "typeVersion": 1,
        "position": [440, 300]
    }
    
    # JSON Parser（エージェント応答解析）
    json_parser_node = {
        "parameters": {
            "keepOnlySet": False,
            "values": {
                "string": [
                    {
                        "name": "tool",
                        "value": "={{JSON.parse($json.choices[0].message.content).tool}}"
                    },
                    {
                        "name": "response",
                        "value": "={{JSON.parse($json.choices[0].message.content).response}}"
                    },
                    {
                        "name": "telegram_chat_id", 
                        "value": "={{JSON.parse($json.choices[0].message.content).telegram_chat_id}}"
                    }
                ],
                "object": [
                    {
                        "name": "parameters",
                        "value": "={{JSON.parse($json.choices[0].message.content).parameters}}"
                    }
                ]
            }
        },
        "id": "json_parser",
        "name": "Parse Agent Response",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.2,
        "position": [640, 300]
    }
    
    # Switch（ツール選択分岐）
    switch_node = {
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{$json.tool}}",
                                    "value2": "create_image"
                                }
                            ]
                        },
                        "renameOutput": True,
                        "outputKey": "create_image"
                    },
                    {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{$json.tool}}",
                                    "value2": "edit_image"
                                }
                            ]
                        },
                        "renameOutput": True,
                        "outputKey": "edit_image"
                    },
                    {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{$json.tool}}",
                                    "value2": "image_database"
                                }
                            ]
                        },
                        "renameOutput": True,
                        "outputKey": "image_database"
                    },
                    {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{$json.tool}}",
                                    "value2": "blog_post"
                                }
                            ]
                        },
                        "renameOutput": True,
                        "outputKey": "blog_post"
                    },
                    {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{$json.tool}}",
                                    "value2": "linkedin_post"
                                }
                            ]
                        },
                        "renameOutput": True,
                        "outputKey": "linkedin_post"
                    },
                    {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{$json.tool}}",
                                    "value2": "video"
                                }
                            ]
                        },
                        "renameOutput": True,
                        "outputKey": "video"
                    }
                ]
            },
            "fallbackOutput": "NoMatch"
        },
        "id": "tool_switch",
        "name": "Tool Switch",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 1,
        "position": [840, 300]
    }
    
    # サブワークフロー呼び出しノード（画像作成）
    create_image_subflow = {
        "parameters": {
            "workflowId": "{{ $('HTTP Request').first() }}",
            "fieldsToSend": "specifyInNode",
            "fields": {
                "values": [
                    {
                        "name": "image_title",
                        "stringValue": "={{$json.parameters.image_title}}"
                    },
                    {
                        "name": "image_prompt", 
                        "stringValue": "={{$json.parameters.image_prompt}}"
                    },
                    {
                        "name": "telegram_chat_id",
                        "stringValue": "={{$json.telegram_chat_id}}"
                    }
                ]
            }
        },
        "id": "create_image_subflow",
        "name": "Create Image Tool",
        "type": "n8n-nodes-base.executeWorkflow",
        "typeVersion": 1,
        "position": [1040, 200]
    }
    
    # エラーハンドリング用のNo Match応答
    no_match_response = {
        "parameters": {
            "keepOnlySet": False,
            "values": {
                "string": [
                    {
                        "name": "response",
                        "value": "申し訳ありませんが、その要求を理解できませんでした。画像作成、編集、ブログ投稿、LinkedIn投稿、または動画作成についてお手伝いできます。"
                    }
                ]
            }
        },
        "id": "no_match_response",
        "name": "No Match Response",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.2,
        "position": [1040, 400]
    }
    
    # ワークフロー定義
    workflow_data = {
        "name": workflow_name,
        "nodes": [
            webhook_node,
            main_agent_node,
            json_parser_node,
            switch_node,
            create_image_subflow,
            no_match_response
        ],
        "connections": {
            "Marketing Webhook": {
                "main": [[{"node": "Marketing Team Agent", "type": "main", "index": 0}]]
            },
            "Marketing Team Agent": {
                "main": [[{"node": "Parse Agent Response", "type": "main", "index": 0}]]
            },
            "Parse Agent Response": {
                "main": [[{"node": "Tool Switch", "type": "main", "index": 0}]]
            },
            "Tool Switch": {
                "create_image": [[{"node": "Create Image Tool", "type": "main", "index": 0}]],
                "NoMatch": [[{"node": "No Match Response", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "timezone": "Asia/Tokyo"
        }
    }
    
    # ワークフロー作成
    response = requests.post(f"{base_url}/api/v1/workflows", headers=headers, json=workflow_data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        workflow_id = result['id']
        
        print(f"✅ メインエージェントワークフロー作成成功: {workflow_id}")
        
        # アクティブ化
        activate_response = requests.post(f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers)
        print(f"⚡ アクティブ化試行: {activate_response.status_code}")
        
        webhook_url = f"{base_url}/webhook/{webhook_path}"
        
        print(f"📡 Webhook URL: {webhook_url}")
        print(f"🎯 メインエージェント準備完了")
        
        return True, webhook_url, workflow_id, workflow_name
    else:
        print(f"❌ 作成失敗: {response.status_code} - {response.text}")
        return False, None, None, None

if __name__ == "__main__":
    success, url, workflow_id, name = create_main_agent_workflow()
    
    if success:
        print(f"\n🎊 **メインエージェント作成成功** 🎊")
        print(f"📡 URL: {url}")
        print(f"🆔 ID: {workflow_id}")
        print(f"📝 名前: {name}")
        print(f"\n次のステップ:")
        print(f"1. サブワークフロー（画像作成等）の作成")
        print(f"2. 必要なAPIキーの追加設定")
        print(f"3. 統合テスト実行")
    else:
        print(f"\n❌ **メインエージェント作成失敗**")