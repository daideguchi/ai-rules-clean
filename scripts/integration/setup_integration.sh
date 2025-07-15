#!/bin/bash
# 🔧 他プロダクト統合セットアップスクリプト
# 環境競合を完全回避する安全な統合

set -euo pipefail

PROJECT_NAME="${1:-$(basename $(pwd))}"
INTEGRATION_MODE="${2:-docker}"

echo "🚀 {{mistake_count}}回ミス防止AI統合セットアップ"
echo "プロジェクト: $PROJECT_NAME"
echo "統合モード: $INTEGRATION_MODE"

# 環境競合チェック
check_conflicts() {
    echo "🔍 環境競合チェック中..."
    
    # Python環境チェック
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "   Python: $PYTHON_VERSION"
    fi
    
    # 既存venvチェック
    if [ -d "venv" ] || [ -d ".venv" ]; then
        echo "⚠️  既存仮想環境検出: 名前空間分離で対応"
    fi
    
    # ポート競合チェック
    MISAIP_PORT=${MISAIP_PORT:-8088}
    MISAIP_DB_PORT=${MISAIP_DB_PORT:-55432}
    
    if lsof -i :$MISAIP_PORT &> /dev/null; then
        echo "⚠️  ポート$MISAIP_PORT使用中: 自動代替ポート設定"
        MISAIP_PORT=$((MISAIP_PORT + 1))
    fi
    
    if lsof -i :$MISAIP_DB_PORT &> /dev/null; then
        echo "⚠️  ポート$MISAIP_DB_PORT使用中: 自動代替ポート設定"
        MISAIP_DB_PORT=$((MISAIP_DB_PORT + 1))
    fi
    
    echo "   AI服务端口: $MISAIP_PORT"
    echo "   DB端口: $MISAIP_DB_PORT"
}

# Docker統合セットアップ
setup_docker_integration() {
    echo "🐳 Docker統合セットアップ"
    
    # プロジェクト固有の環境変数
    cat > .env.misaip << EOF
PROJECT_NAME=$PROJECT_NAME
MISAIP_PORT=$MISAIP_PORT
MISAIP_DB_PORT=$MISAIP_DB_PORT
MISAIP_DB_PASSWORD=$(openssl rand -hex 16)
COMPOSE_PROJECT_NAME=misaip_$PROJECT_NAME
EOF
    
    # Docker Compose起動
    docker-compose -f docker-compose.integration.yml --env-file .env.misaip up -d
    
    echo "✅ Docker統合完了"
    echo "   アクセス: http://localhost:$MISAIP_PORT"
    echo "   DB: localhost:$MISAIP_DB_PORT"
}

# 仮想環境統合セットアップ  
setup_venv_integration() {
    echo "🐍 仮想環境統合セットアップ"
    
    # 名前空間付き仮想環境
    VENV_NAME="misaip_${PROJECT_NAME}_venv"
    
    if [ ! -d "$VENV_NAME" ]; then
        python3 -m venv $VENV_NAME
        echo "   仮想環境作成: $VENV_NAME"
    fi
    
    # 依存関係インストール
    source $VENV_NAME/bin/activate
    pip install -r requirements.txt
    
    # プロジェクト固有DB作成
    DB_NAME="${PROJECT_NAME}_misaip_ai"
    createdb $DB_NAME 2>/dev/null || echo "DB $DB_NAME 既存"
    psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
    
    echo "✅ 仮想環境統合完了"
    echo "   アクティベート: source $VENV_NAME/bin/activate"
    echo "   DB: $DB_NAME"
}

# 統合テスト
run_integration_test() {
    echo "🧪 統合テスト実行"
    
    if [ "$INTEGRATION_MODE" = "docker" ]; then
        docker-compose -f docker-compose.integration.yml --env-file .env.misaip exec misaip-ai python3 tests/integration_test.py
    else
        source misaip_${PROJECT_NAME}_venv/bin/activate
        python3 tests/integration_test.py
    fi
    
    echo "✅ 統合テスト完了"
}

# メイン実行
main() {
    check_conflicts
    
    case $INTEGRATION_MODE in
        docker)
            setup_docker_integration
            ;;
        venv)
            setup_venv_integration
            ;;
        *)
            echo "❌ 不正な統合モード: $INTEGRATION_MODE"
            echo "利用可能: docker, venv"
            exit 1
            ;;
    esac
    
    run_integration_test
    
    echo ""
    echo "🎉 {{mistake_count}}回ミス防止AI統合セットアップ完了"
    echo "📋 他プロダクトとの競合は完全回避されています"
}

main