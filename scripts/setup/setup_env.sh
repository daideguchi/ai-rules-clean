#!/bin/bash
# 仮想環境自動セットアップ

if [ -d "venv" ]; then
    echo "既存のvenvを使用"
    source venv/bin/activate
else
    echo "新規venv作成"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
fi

# 依存関係インストール
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # 基本依存関係インストール
    pip install rich textual psycopg2-binary openai scikit-learn
    pip freeze > requirements.txt
fi

echo "✅ 環境セットアップ完了"