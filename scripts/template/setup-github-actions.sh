#!/bin/bash
# GitHub Actions Template Setup Script
# テンプレートプロジェクトでのGitHub Actions設定自動化

echo "🤖 Claude Code GitHub Actions Template Setup"
echo "============================================="

# プロジェクトルート確認
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ Error: CLAUDE.md not found. Run from project root."
    exit 1
fi

# .github ディレクトリ作成
echo "📁 Creating .github directories..."
mkdir -p .github/workflows
mkdir -p .github/scripts

# ワークフローファイルをコピー（存在しない場合のみ）
if [ ! -f ".github/workflows/claude-code.yml" ]; then
    echo "📋 Setting up claude-code.yml workflow..."
    cat > .github/workflows/claude-code.yml << 'EOF'
name: Claude Code AI Assistant

on:
  issues:
    types: [opened, edited]
  issue_comment:
    types: [created, edited]
  pull_request:
    types: [opened, edited, synchronize]
  pull_request_review_comment:
    types: [created, edited]

jobs:
  claude-code:
    runs-on: ubuntu-latest
    if: contains(github.event.comment.body, '@claude') || contains(github.event.issue.body, '@claude') || contains(github.event.pull_request.body, '@claude')
    
    permissions:
      contents: write
      pull-requests: write
      issues: write
      
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install anthropic requests
          
      - name: Claude Code AI Processing
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/scripts/claude-handler.py \
            --event-type "${{ github.event_name }}" \
            --repository "${{ github.repository }}" \
            --issue-number "${{ github.event.issue.number || github.event.pull_request.number }}" \
            --comment-body "${{ github.event.comment.body || github.event.issue.body || github.event.pull_request.body }}"
EOF
    echo "✅ claude-code.yml workflow created"
else
    echo "ℹ️ claude-code.yml already exists, skipping"
fi

# PR レビューワークフロー
if [ ! -f ".github/workflows/claude-pr-review.yml" ]; then
    echo "📋 Setting up claude-pr-review.yml workflow..."
    cat > .github/workflows/claude-pr-review.yml << 'EOF'
name: Claude Code PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
  pull_request_review:
    types: [submitted]

jobs:
  claude-review:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.body, '@claude-review') || contains(github.event.review.body, '@claude-review')
    
    permissions:
      contents: read
      pull-requests: write
      
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install anthropic requests
          
      - name: Claude Code PR Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/scripts/claude-pr-reviewer.py \
            --pr-number "${{ github.event.pull_request.number }}" \
            --repository "${{ github.repository }}" \
            --base-sha "${{ github.event.pull_request.base.sha }}" \
            --head-sha "${{ github.event.pull_request.head.sha }}"
EOF
    echo "✅ claude-pr-review.yml workflow created"
else
    echo "ℹ️ claude-pr-review.yml already exists, skipping"
fi

# スクリプトの実行権限設定
echo "🔧 Setting script permissions..."
chmod +x .github/scripts/*.py 2>/dev/null || true

# セットアップガイド作成
if [ ! -f ".github/CLAUDE_GITHUB_SETUP.md" ]; then
    echo "📚 Creating setup documentation..."
    # Setup guide will be created by the main implementation
    echo "ℹ️ Setup guide will be available after template completion"
fi

# テンプレート設定確認
echo ""
echo "🎯 Template Setup Status:"
echo "========================="

# CLAUDE.md チェック
if grep -q "AI安全ガバナンス" CLAUDE.md 2>/dev/null; then
    echo "✅ AI Safety Governance template detected"
    template_type="ai-safety"
else
    echo "ℹ️ Generic template detected"
    template_type="generic"
fi

# 必須ファイル確認
check_files=(
    ".github/workflows/claude-code.yml"
    ".github/workflows/claude-pr-review.yml"
    ".github/scripts/claude-handler.py"
    ".github/scripts/claude-pr-reviewer.py"
)

all_present=true
for file in "${check_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        all_present=false
    fi
done

echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. 🔑 Set ANTHROPIC_API_KEY in GitHub Secrets"
echo "   Repository → Settings → Secrets and variables → Actions"
echo "   Name: ANTHROPIC_API_KEY"
echo "   Value: your_anthropic_api_key"
echo ""
echo "2. 🤖 Test the integration:"
echo "   - Create an issue with '@claude help me implement X'"
echo "   - Create a PR with '@claude-review' in description"
echo ""
echo "3. 📖 Read the setup guide:"
echo "   - .github/CLAUDE_GITHUB_SETUP.md"
echo ""

if [ "$all_present" = true ]; then
    echo "✅ GitHub Actions setup completed successfully!"
    echo "🎉 Template ready for use"
else
    echo "⚠️ Some files are missing. Please run the full template setup."
fi

echo ""
echo "🔗 Useful links:"
echo "- GitHub App: https://github.com/apps/claude"
echo "- Documentation: https://docs.anthropic.com/ja/docs/claude-code/github-actions"
echo "- Template repo: Current repository"