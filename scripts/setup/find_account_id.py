#!/usr/bin/env python3
"""
Cloudflare Account ID確実取得方法
複数の方法でAccount IDを見つける
"""

import webbrowser
import time

def main():
    """Account ID確実取得ガイド"""
    
    print("🔍 Cloudflare Account ID 確実取得方法")
    print("="*50)
    
    print("🌐 **方法1: URLから取得 (最確実)**")
    print("1. 現在のブラウザのURLバーを確認してください")
    print("2. URLの形式:")
    print("   https://one.dash.cloudflare.com/[ACCOUNT_ID]/...")
    print("   または")  
    print("   https://dash.cloudflare.com/[ACCOUNT_ID]/...")
    print("3. [ACCOUNT_ID]の部分が32文字の英数字です")
    print("   例: 1d8df0d5c5764d1796fdec60652d4694")
    
    print("\n📍 **方法2: メインダッシュボードに移動**")
    print("1. 左上の 'Cloudflare' ロゴをクリック")
    print("2. またはこのURLにアクセス:")
    print("   https://dash.cloudflare.com/")
    print("3. 右サイドバーに 'Account ID' が表示されます")
    
    print("\n⚙️ **方法3: Billing ページ経由**")
    print("1. 右上のアカウントメニュー → 'Billing'")
    print("2. Account IDが表示されます")
    
    print("\n🔑 **方法4: API経由で取得**")
    print("1. 現在のTokenでも取得可能です:")
    
    # API経由でAccount ID取得を試行
    try:
        import requests
        
        # 現在のTokenでアカウント情報取得を試行
        token = "iDhAvNEpin4bY1H1WD0KYgshOVNcSDiSOC96aLd2"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # ユーザー情報からAccount情報を取得
        response = requests.get(
            'https://api.cloudflare.com/client/v4/user',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('success'):
                print("   ✅ API経由取得成功:")
                
                # Membership情報取得を試行
                membership_response = requests.get(
                    'https://api.cloudflare.com/client/v4/memberships',
                    headers=headers,
                    timeout=10
                )
                
                if membership_response.status_code == 200:
                    membership_data = membership_response.json()
                    if membership_data.get('success') and membership_data.get('result'):
                        for membership in membership_data['result']:
                            account = membership.get('account', {})
                            account_id = account.get('id')
                            account_name = account.get('name')
                            if account_id:
                                print(f"   📍 Account ID: {account_id}")
                                print(f"   📝 Account Name: {account_name}")
                                
                                # 環境変数設定スクリプト生成
                                generate_env_script(account_id)
                                return account_id
                                
        print("   ⚠️ API経由での取得に失敗")
        
    except Exception as e:
        print(f"   ❌ API取得エラー: {e}")
    
    print("\n💡 **推奨: URL確認方法**")
    print("現在のブラウザのURLを確認して、32文字のIDを探してください")
    
    # ブラウザでメインダッシュボードを開く
    try:
        print("\n🌐 メインダッシュボードを開いています...")
        webbrowser.open('https://dash.cloudflare.com/')
        time.sleep(2)
    except:
        print("手動で https://dash.cloudflare.com/ を開いてください")
    
    print("\n📋 **取得後の手順:**")
    print("1. Account IDを確認")
    print("2. 正しい権限でAPI Token再作成")
    print("3. bash scripts/setup/run_zero_trust_setup.sh")
    
    return None

def generate_env_script(account_id):
    """環境変数設定スクリプト生成"""
    script_content = f"""#!/bin/bash
# Cloudflare Account ID自動設定

echo "🆔 Account ID確認: {account_id}"
echo "🔑 新しいAPI Token (正しい権限) を入力してください:"
read -p "API Token: " NEW_API_TOKEN

# 環境変数設定
export CLOUDFLARE_API_TOKEN="$NEW_API_TOKEN"
export CLOUDFLARE_ACCOUNT_ID="{account_id}"

echo "✅ 環境変数設定完了"
echo "🚀 Zero Trust セットアップ実行中..."

# Zero Trust セットアップ実行
python3 scripts/setup/cloudflare_zero_trust_setup.py
"""
    
    script_path = "scripts/setup/auto_zero_trust_setup.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    import os
    os.chmod(script_path, 0o755)
    
    print(f"\n✅ 自動セットアップスクリプト生成: {script_path}")

if __name__ == "__main__":
    main()