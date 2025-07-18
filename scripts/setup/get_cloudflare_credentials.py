#!/usr/bin/env python3
"""
Cloudflare認証情報取得ガイド
Zero Trust setup用のAPI Token・Account ID取得
"""

import time
import webbrowser


def main():
    """Cloudflare認証情報取得ガイド"""

    print("🌐 Cloudflare認証情報取得ガイド")
    print("="*50)

    print("🔑 **STEP 1: Cloudflare API Token取得**")
    print("1. Cloudflare Dashboard にログイン")
    print("2. 右上のアカウントアイコン → 'My Profile'")
    print("3. 'API Tokens' タブ")
    print("4. 'Create Token' をクリック")
    print("5. 'Custom token' を選択")

    print("\n⚙️ **Token設定:**")
    print("   Token name: n8n-zero-trust-access")
    print("   Permissions:")
    print("     - Account: Cloudflare Tunnel:Edit")
    print("     - Account: Access: Service Tokens:Edit")
    print("     - Account: Access: Apps and Policies:Edit")
    print("   Account Resources: Include - All accounts")
    print("   Zone Resources: Include - All zones")

    print("\n🆔 **STEP 2: Account ID取得**")
    print("1. Cloudflare Dashboard のホーム画面")
    print("2. 右サイドバーの 'Account ID' をコピー")

    # ブラウザで自動オープン
    try:
        print("\n🌐 Cloudflare Dashboard を開いています...")
        webbrowser.open('https://dash.cloudflare.com/profile/api-tokens')
        time.sleep(2)
        webbrowser.open('https://dash.cloudflare.com/')
    except Exception:
        print("手動でブラウザを開いてください:")
        print("   API Token: https://dash.cloudflare.com/profile/api-tokens")
        print("   Account ID: https://dash.cloudflare.com/")

    print("\n📋 **STEP 3: 環境変数設定**")

    api_token = input("\n🔑 Cloudflare API Token を入力してください: ").strip()
    account_id = input("🆔 Cloudflare Account ID を入力してください: ").strip()

    if api_token and account_id:
        # 環境変数設定スクリプト生成
        env_script = f"""#!/bin/bash
# Cloudflare Zero Trust環境変数設定

# 既存の.envファイル読み込み
source .env

# Cloudflare設定追加
export CLOUDFLARE_API_TOKEN="{api_token}"
export CLOUDFLARE_ACCOUNT_ID="{account_id}"

# .envファイル更新
cat > .env << EOF
# Original API keys
OPENAI_API_KEY=$OPENAI_API_KEY
GEMINI_API_KEY=$GEMINI_API_KEY
N8N_API_KEY=$N8N_API_KEY
N8N_API_URL=$N8N_API_URL
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Cloudflare Zero Trust
CLOUDFLARE_API_TOKEN={api_token}
CLOUDFLARE_ACCOUNT_ID={account_id}

# Autonomous Growth System
AUTONOMOUS_GROWTH_ENABLED=true
N8N_SETUP_COMPLETED=false
EOF

echo "✅ 環境変数設定完了"
echo "🚀 Zero Trust セットアップ実行:"
echo "   python3 scripts/setup/cloudflare_zero_trust_setup.py"
"""

        # スクリプト保存
        script_path = "scripts/setup/set_cloudflare_env.sh"
        with open(script_path, 'w') as f:
            f.write(env_script)

        import os
        os.chmod(script_path, 0o755)

        print(f"✅ 環境変数設定スクリプト生成: {script_path}")

        print("\n🚀 **STEP 4: Zero Trust セットアップ実行**")
        print(f"   bash {script_path}")
        print("   python3 scripts/setup/cloudflare_zero_trust_setup.py")

        print("\n📊 **期待される結果:**")
        print("   ✅ Service Token作成")
        print("   ✅ Access Policy設定")
        print("   ✅ n8n API制限突破")
        print("   ✅ ワークフロー自動インポート")
        print("   🚀 自律AI成長システム稼働開始!")

    else:
        print("❌ API TokenまたはAccount IDが入力されていません")
        return False

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
