#!/usr/bin/env python3
"""
リアルタイム学習システムテスト
実際のClaude Code操作で自動学習を確認
"""

import time
import os

def simulate_claude_code_session():
    """Claude Codeセッション模擬"""
    print("🤖 Claude Codeセッション模擬開始...")
    
    # 複数ツール使用をシミュレート
    tools_used = ["Read", "Write", "Bash", "TodoWrite"]
    
    for i, tool in enumerate(tools_used, 1):
        print(f"   {i}. {tool}ツール使用中...")
        time.sleep(0.5)
    
    print("✅ セッション完了")
    return {
        "tools_count": len(tools_used),
        "success": True,
        "execution_time": 2.3
    }

def main():
    print("🧪 リアルタイム学習システムテスト")
    print("=" * 40)
    
    # セッション実行
    session_result = simulate_claude_code_session()
    
    # パフォーマンス自動送信をトリガー
    print("📡 自動学習データ送信中...")
    
    # 実際の自動送信システムを呼び出し
    os.system("python3 scripts/hooks/performance_auto_sender.py")
    
    print("\n🎉 テスト完了！")
    print("📊 確認事項:")
    print("1. Supabase Dashboard → Table Editor")
    print("2. ai_performance_log テーブルで最新データ確認")
    print("3. session_id: auto_* の新しいエントリが追加されているはず")
    
    return session_result

if __name__ == "__main__":
    main()