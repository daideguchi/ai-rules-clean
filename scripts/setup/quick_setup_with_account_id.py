#!/usr/bin/env python3
"""
Account ID確認後の高速セットアップ
URLから取得したAccount IDで即座にZero Trust設定
"""

import re

def main():
    """Account ID確認と高速セットアップ"""
    
    print("🚀 Account ID確認 & 高速セットアップ")
    print("="*45)
    
    print("📍 **現在のブラウザURLを確認してください**")
    print("例: https://one.dash.cloudflare.com/abc123.../zero-trust")
    
    # URLまたはAccount ID入力
    user_input = input("\n🔗 URLまたはAccount IDを入力してください: ").strip()
    
    # Account ID抽出
    account_id = extract_account_id(user_input)
    
    if account_id:
        print(f"✅ Account ID確認: {account_id}")
        
        # 新しいAPI Token入力
        print("\n🔑 **新しいAPI Token作成が必要です**")
        print("権限設定:")
        print("  ✅ Account | Access: Service Tokens | Edit")
        print("  ✅ Account | Access: Apps and Policies | Edit")
        print("  ✅ Account | Cloudflare Tunnel | Edit")
        
        new_token = input("\n新しいAPI Token: ").strip()
        
        if new_token:
            # 環境変数設定スクリプト生成
            generate_setup_script(account_id, new_token)
        else:
            print("❌ API Tokenが入力されていません")
    else:
        print("❌ Account IDが見つかりませんでした")
        print("💡 URLの例: https://one.dash.cloudflare.com/abc123def456/zero-trust")

def extract_account_id(user_input):
    """URLまたは文字列からAccount ID抽出"""
    
    # 32文字の英数字パターン
    account_id_pattern = r'[a-f0-9]{32}'
    
    # パターンマッチング
    matches = re.findall(account_id_pattern, user_input.lower())
    
    if matches:
        return matches[0]
    
    # 直接32文字のIDが入力された場合
    if len(user_input) == 32 and all(c in '0123456789abcdef' for c in user_input.lower()):
        return user_input.lower()
    
    return None

def generate_setup_script(account_id, api_token):
    """セットアップスクリプト生成"""
    
    script_content = f"""#!/bin/bash
# Cloudflare Zero Trust自動セットアップ

echo "🚀 Cloudflare Zero Trust セットアップ開始"
echo "Account ID: {account_id}"

# 環境変数設定
export CLOUDFLARE_API_TOKEN="{api_token}"
export CLOUDFLARE_ACCOUNT_ID="{account_id}"

# 既存の環境変数読み込み
source .env
export N8N_API_KEY="$N8N_API_KEY"
export N8N_API_URL="$N8N_API_URL"

echo "✅ 環境変数設定完了"

# Zero Trust セットアップ実行
echo "🛡️ Zero Trust セットアップ実行中..."
python3 scripts/setup/cloudflare_zero_trust_setup.py

if [ $? -eq 0 ]; then
    echo "🎉 Zero Trust セットアップ成功!"
    
    # .env更新
    cat >> .env << EOF

# Cloudflare Zero Trust ($(date))
CLOUDFLARE_API_TOKEN={api_token}
CLOUDFLARE_ACCOUNT_ID={account_id}
ZERO_TRUST_SETUP_COMPLETED=true
EOF
    
    echo "📝 設定を.envに保存完了"
    echo "🧬 自律AI成長システム準備完了!"
    
    # テスト実行
    echo "🧪 動作テスト実行..."
    python3 scripts/hooks/autonomous_growth_hook.py test
    
else
    echo "❌ Zero Trust セットアップ失敗"
    echo "💡 代替案: bash scripts/setup/webhook_url_setup.sh"
fi
"""
    
    script_path = "scripts/setup/execute_zero_trust_setup.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    import os
    os.chmod(script_path, 0o755)
    
    print(f"\n✅ セットアップスクリプト生成: {script_path}")
    print("\n🚀 **実行手順:**")
    print(f"   bash {script_path}")
    
    print("\n📊 **期待される結果:**")
    print("   ✅ Service Token作成")
    print("   ✅ Access Policy設定")
    print("   ✅ n8n API制限突破")
    print("   ✅ ワークフロー自動インポート")
    print("   🎉 自律AI成長システム稼働!")

if __name__ == "__main__":
    main()