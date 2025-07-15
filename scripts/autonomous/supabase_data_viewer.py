#!/usr/bin/env python3
"""
Supabase データ確認・自律成長データアクセス
"""

import requests
import json
from datetime import datetime

class SupabaseDataViewer:
    def __init__(self):
        self.supabase_url = "https://hetcpqtsineqaopnnvtn.supabase.co"
        self.anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhldGNwcXRzaW5lcWFvcG5udnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDEzNDEsImV4cCI6MjA2Nzk3NzM0MX0.WAgCVM-XZY0JqYzap7fCXxu6PeX9vES-zitAhoySIbg"
        
        self.headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json"
        }
    
    def get_all_performance_data(self):
        """全パフォーマンスデータ取得"""
        try:
            url = f"{self.supabase_url}/rest/v1/ai_performance_log"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Supabaseデータ取得成功: {len(data)}件")
                return data
            else:
                print(f"❌ データ取得失敗: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return []
    
    def get_recent_data(self, limit=10):
        """最新データ取得"""
        try:
            url = f"{self.supabase_url}/rest/v1/ai_performance_log?order=timestamp.desc&limit={limit}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 最新{limit}件のデータ:")
                for item in data:
                    print(f"  - {item.get('timestamp', 'N/A')}: {item.get('session_id', 'N/A')} (Success: {item.get('task_success', 'N/A')})")
                return data
            else:
                print(f"❌ データ取得失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return []
    
    def analyze_patterns(self):
        """パターン分析・自律成長データ抽出"""
        data = self.get_all_performance_data()
        
        if not data:
            print("❌ 分析データなし")
            return
            
        success_count = sum(1 for item in data if item.get('task_success'))
        total_count = len(data)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n🤖 AI自律成長分析:")
        print(f"  - 総セッション数: {total_count}")
        print(f"  - 成功セッション: {success_count}")
        print(f"  - 成功率: {success_rate:.1f}%")
        
        # パターン分析
        success_patterns = {}
        failure_patterns = {}
        
        for item in data:
            patterns = item.get('success_patterns', []) + item.get('failure_patterns', [])
            for pattern in patterns:
                if item.get('task_success'):
                    success_patterns[pattern] = success_patterns.get(pattern, 0) + 1
                else:
                    failure_patterns[pattern] = failure_patterns.get(pattern, 0) + 1
        
        print(f"\n✅ 成功パターン:")
        for pattern, count in sorted(success_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {pattern}: {count}回")
            
        print(f"\n❌ 失敗パターン:")
        for pattern, count in sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {pattern}: {count}回")
    
    def test_connection(self):
        """接続テスト"""
        try:
            url = f"{self.supabase_url}/rest/v1/"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                print("✅ Supabase接続成功")
                return True
            else:
                print(f"❌ Supabase接続失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return False

def main():
    viewer = SupabaseDataViewer()
    
    print("🔍 Supabaseデータ確認開始")
    print("=" * 50)
    
    # 接続テスト
    if not viewer.test_connection():
        return
    
    # 最新データ確認
    viewer.get_recent_data(5)
    
    # パターン分析
    viewer.analyze_patterns()

if __name__ == "__main__":
    main()