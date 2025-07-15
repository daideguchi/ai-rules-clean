#!/usr/bin/env python3
"""
実行データの完全ダンプ
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def dump_execution_data():
    """最新実行の完全データダンプ"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 最新の実行ID: 42
    exec_id = "42"
    
    print(f"🔍 実行ID {exec_id} の完全データダンプ")
    print("="*60)
    
    # 詳細データ取得
    response = requests.get(f"{base_url}/api/v1/executions/{exec_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # 完全なJSONを整形して表示
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return True
    else:
        print(f"❌ データ取得失敗: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    dump_execution_data()