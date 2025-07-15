#!/usr/bin/env python3
"""
Cloudflare Account ID取得スクリプト
Dashboard経由でAccount IDを確認
"""

import webbrowser
import time

def main():
    """Account ID取得ガイド"""
    
    print("🆔 Cloudflare Account ID取得")
    print("="*40)
    
    print("📋 **方法1: Dashboard経由**")
    print("1. https://dash.cloudflare.com/ にアクセス")
    print("2. 右サイドバーの 'Account ID' をコピー")
    print("   (例: 1d8df0d5c5764d1796fdec60652d4694)")
    
    print("\n📋 **方法2: URLから取得**")
    print("1. Cloudflare Dashboard の任意のページのURLを確認")
    print("2. URLの中にAccount IDが含まれています")
    print("   https://dash.cloudflare.com/[ACCOUNT_ID]/...")
    
    # ブラウザを開く
    try:
        print("\n🌐 Cloudflare Dashboard を開いています...")
        webbrowser.open('https://dash.cloudflare.com/')
        time.sleep(2)
    except:
        print("手動でブラウザを開いてください: https://dash.cloudflare.com/")
    
    print("\n⏰ Dashboard確認後、以下を実行してください:")
    print("1. 正しい権限でAPI Token再作成")
    print("2. Account IDをコピー")
    print("3. bash scripts/setup/run_zero_trust_setup.sh")

if __name__ == "__main__":
    main()