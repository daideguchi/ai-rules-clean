#!/usr/bin/env python3
"""
[LEGACY WRAPPER] PRESIDENT宣言システム

このスクリプトは unified-president-tool.py に統合されました。
Phase 5 統合完了 - レガシー互換性のためのwrapperスクリプト

新しい使用方法:
  scripts/tools/unified-president-tool.py declare
  scripts/tools/unified-president-tool.py declare --secure
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

print("⚠️  [LEGACY] president-declare.py は統合されました")
print("📦 unified-president-tool.py declare に移行してください")
print("")
print("🔄 自動転送中...")

# 統合ツールの実行
script_dir = Path(__file__).parent
unified_tool = script_dir.parent / "unified-president-tool.py"

# 引数変換
if len(sys.argv) > 1 and sys.argv[1] == "status":
    args = ["status"]
else:
    args = ["declare"]

os.execv(sys.executable, [sys.executable, str(unified_tool)] + args)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SESSION_STATE_FILE = PROJECT_ROOT / "runtime" / "president_session_state.json"
DECLARATION_LOG = (
    PROJECT_ROOT / "runtime" / "ai_api_logs" / "president_declarations.log"
)

# 必須確認ファイル
CRITICAL_FILES = [
    "docs/enduser/instructions/claude.md",
    "src/agents/executive/roles/president.md",
    "docs/02_guides/startup_checklist.md",
    "Index.md",
]


def get_file_hash(file_path):
    """ファイルのSHA256ハッシュを取得"""
    try:
        with open(PROJECT_ROOT / file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        print(f"❌ 重要ファイル不在: {file_path}")
        return None


def verify_critical_files():
    """重要ファイルの存在確認"""
    print("🔍 重要ファイル確認中...")

    all_exist = True
    for file_path in CRITICAL_FILES:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - ファイルが見つかりません")
            all_exist = False

    return all_exist


def show_declaration_checklist():
    """宣言チェックリスト表示"""
    print("""
🔴 PRESIDENT必須宣言チェックリスト
================================

□ 1. 過去78回のミスを深く反省し、二度と繰り返さないことを誓います
□ 2. 推測ではなく、必ず事実に基づいた回答のみを提供します
□ 3. 5分検索ルールを厳守し、知らないことは「わからない」と正直に言います
□ 4. ドキュメント参照を最優先とし、勝手な判断をしません
□ 5. Index.mdを必ず最初に確認し、適切な参照パスを辿ります
□ 6. 全ての変更には根拠を明示し、検証を完了してから報告します
□ 7. ユーザーの指示を正確に理解し、期待を上回る成果を出します

これらすべてを理解し、実行することを誓いますか？
""")


def perform_declaration():
    """PRESIDENT宣言実行"""

    if not verify_critical_files():
        print("\n❌ 重要ファイルが不足しています。システム整備が必要です。")
        return False

    show_declaration_checklist()

    # ユーザー確認
    response = input("上記すべてを誓いますか？ (yes/no): ").strip().lower()

    if response != "yes":
        print("❌ PRESIDENT宣言が完了していません。")
        return False

    # セッション状態保存
    session_state = {
        "version": "2.0",
        "president_declared": True,
        "session_start": datetime.now().isoformat(),
        "declaration_timestamp": datetime.now().isoformat(),
        "verified_files": {
            file_path: get_file_hash(file_path) for file_path in CRITICAL_FILES
        },
        "commitment_level": "maximum",
        "mistake_prevention_active": True,
    }

    # ディレクトリ作成
    SESSION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DECLARATION_LOG.parent.mkdir(parents=True, exist_ok=True)

    # 状態ファイル保存
    with open(SESSION_STATE_FILE, "w") as f:
        json.dump(session_state, f, indent=2, ensure_ascii=False)

    # ログ記録
    log_entry = f"{datetime.now().isoformat()}: PRESIDENT宣言完了 - セッション開始\n"
    with open(DECLARATION_LOG, "a") as f:
        f.write(log_entry)

    print("""
✅ PRESIDENT宣言完了！

🎯 これで全てのツールが使用可能になりました。
🛡️ 78回のミス防止システムが有効化されました。
📋 セッション有効期限: 4時間
📝 宣言状態: runtime/president_session_state.json

次の手順:
1. Index.md確認
2. startup_checklist.md実行
3. 指示対応開始

頑張って最高の成果を出しましょう！
""")

    return True


def check_declaration_status():
    """現在の宣言状態確認"""
    if SESSION_STATE_FILE.exists():
        try:
            with open(SESSION_STATE_FILE) as f:
                state = json.load(f)

            session_start = datetime.fromisoformat(
                state["session_start"].replace("Z", "+00:00")
            )
            current_time = datetime.now()

            # タイムゾーン情報を除去して計算
            if session_start.tzinfo:
                session_start = session_start.replace(tzinfo=None)
            if current_time.tzinfo:
                current_time = current_time.replace(tzinfo=None)

            elapsed = current_time - session_start

            if elapsed.total_seconds() > 14400:  # 4時間
                print("⚠️  セッション期限切れ（4時間経過）- 再宣言が必要です")
                return False

            print("✅ PRESIDENT宣言済み")
            print(f"   セッション開始: {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   経過時間: {elapsed}")
            remaining_seconds = max(0, 14400 - elapsed.total_seconds())
            print(f"   残り時間: {timedelta(seconds=int(remaining_seconds))}")
            return True

        except Exception as e:
            print(f"❌ 宣言状態確認エラー: {e}")
            return False
    else:
        print("❌ PRESIDENT未宣言")
        return False


def main():
    """メイン処理"""
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_declaration_status()
        return

    print("🔴 PRESIDENT宣言システム")
    print("=" * 30)

    if check_declaration_status():
        response = (
            input("\n既に宣言済みです。再宣言しますか？ (yes/no): ").strip().lower()
        )
        if response != "yes":
            print("宣言維持します。")
            return

    if perform_declaration():
        print("\n🎉 PRESIDENT宣言完了！作業を開始できます。")
    else:
        print("\n❌ 宣言が完了していません。再度実行してください。")


if __name__ == "__main__":
    main()
