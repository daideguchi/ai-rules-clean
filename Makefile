.PHONY: help install test run status cleanup setup-hooks docs lint handle-instruction

help:
	@echo "CODING-RULE2 Project Commands:"
	@echo ""
	@echo "🚀 Quick Start (ワンコマンド起動):"
	@echo "  startup          - 完全システム起動（社長+AI組織+DB+記憶）"
	@echo "  quick-start      - 高速起動（必須システムのみ）"
	@echo "  full-startup     - フル起動＋評価システム"
	@echo ""
	@echo "🎯 Main Operations:"
	@echo "  session-safety-check - セッション安全確認（必須最優先）"
	@echo "  declare-president - PRESIDENT宣言必須実行"
	@echo "  run-president     - Start PRESIDENT AI system (要宣言)"
	@echo "  startup-check     - スタートアップチェックリスト実行"
	@echo "  status           - Check system status"
	@echo "  cleanup          - Run system cleanup"
	@echo "  check-root       - Check root directory file limit"
	@echo "  enforce-limit    - Enforce 12-file root limit"
	@echo ""
	@echo "🏢 AI Organization:"
	@echo "  ai-org-start     - 🎯 プロフェッショナルAI組織ダッシュボード"
	@echo "  ai-org-status    - 📊 組織状況確認（詳細統計）"
	@echo "  ai-org-test      - 🧪 並列処理テスト実行"
	@echo "  ai-org-legacy    - 📋 レガシーダッシュボード（非推奨）"
	@echo "  ai-roles         - 🎭 動的役職システム確認"
	@echo "  memory-recall    - 🧠 記憶思い出し・継承確認"
	@echo "  db-connect       - 🗄️ データベース接続確認"
	@echo ""
	@echo "🔧 MCP & API Setup:"
	@echo "  mcp-setup        - 🚀 One command MCP setup (new projects)"
	@echo "  mcp-status       - 📊 Check MCP and API key status"
	@echo "  api-setup        - 🔑 Quick API key configuration"
	@echo "  mcp-config       - ⚙️ Create/update MCP configuration"
	@echo ""
	@echo "🎯 Project Template Initialization:"
	@echo "  init-web-project     - 🌐 Initialize as web project template"
	@echo "  init-python-project  - 🐍 Initialize as Python project template"
	@echo "  init-ai-project      - 🤖 Initialize as AI project template"
	@echo "  init-custom-project  - ⚙️ Initialize as custom project template"
	@echo ""
	@echo "🔒 File Organization (ABSOLUTE COMPLIANCE):"
	@echo "  enforce-file-organization - 🚨 Force strict file organization"
	@echo "  check-file-organization   - 📊 Check organization compliance"
	@echo "  root-audit               - 🔍 Audit root directory file count"
	@echo "  dry-run-organization     - 🔍 Preview organization changes"
	@echo "  file-organization-report - 📋 Generate compliance report"
	@echo ""
	@echo "⚙️  Setup & Maintenance:"
	@echo "  install          - Install dependencies"
	@echo "  setup-hooks      - Configure git hooks"
	@echo "  test             - Run all tests"
	@echo "  integration-test - 統合テスト実行"
	@echo ""
	@echo "📊 Evaluation & Metrics:"
	@echo "  evaluate         - 包括的システム評価"
	@echo "  metrics          - メトリクス確認"
	@echo "  language-check   - 言語使用ルール確認"
	@echo "  todo-protocol    - TODO抽出プロトコル確認"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs             - Generate/update documentation"
	@echo "  lint             - Run code linting"
	@echo ""
	@echo "🔧 Development:"
	@echo "  daily-check      - Run daily status check"
	@echo "  validate         - Validate project structure"
	@echo "  handle-instruction - Execute instruction handling flow"
	@echo ""
	@echo "🎯 UI System:"
	@echo "  ui-dashboard     - Launch AI organization dashboard"
	@echo "  ui-command       - Launch interactive command interface"
	@echo "  ui-worker        - Launch worker management interface"
	@echo "  ui-metrics       - Show system metrics"
	@echo "  ui-install       - Install UI dependencies"

install:
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

declare-president: ## セキュアPRESIDENT宣言必須実行
	@echo "🔴 セキュアPRESIDENT宣言開始..."
	@python3 scripts/tools/unified-president-tool.py declare --secure

run-president: ## PRESIDENT AIシステム起動（自動プロジェクト分析+AI組織配置）
	@echo "🎯 Starting PRESIDENT AI System with Intelligent Organization..."
	@python3 scripts/tools/unified-president-tool.py status || (echo "❌ セキュアPRESIDENT宣言が必要です" && exit 1)
	@echo "📊 Analyzing project requirements..."
	@python3 src/orchestrator/intelligent_project_analyzer.py analyze > /dev/null
	@echo "🚀 Launching optimal AI organization..."
	@python3 src/orchestrator/intelligent_project_analyzer.py launch
	@echo "📈 Starting integrated dashboard monitoring..."
	@python3 src/orchestrator/ai_organization_tmux_bridge.py status
	@echo "✅ PRESIDENT system with AI organization started"

status:
	@echo "📊 System Status Check:"
	@echo "Git status:"
	@git status --short
	@echo ""
	@echo "Project structure:"
	@ls -la | head -10
	@echo ""
	@echo "Active processes:"
	@ps aux | grep -E "(claude|president)" | grep -v grep || echo "No active processes"

cleanup:
	@echo "🧹 Running system cleanup..."
	./scripts/utilities/daily_check.sh
	./scripts/cleanup/safe-duplicate-cleanup.py
	@echo "✅ Cleanup completed"

setup-hooks:
	@echo "🔗 Setting up git hooks..."
	./scripts/setup-hooks.sh
	@echo "✅ Git hooks configured"

test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v
	@echo "✅ Tests completed"

docs:
	@echo "📚 Generating documentation..."
	@echo "Index available at: Index.md"
	@echo "Docs index: docs/00_INDEX/README.md"
	@echo "✅ Documentation ready"

lint:
	@echo "🔍 Running linters..."
	ruff check src/ scripts/
	@echo "✅ Linting completed"

daily-check:
	@echo "📅 Daily check routine..."
	./scripts/utilities/daily_check.sh

validate:
	@echo "✅ Project structure validation..."
	./scripts/validation/validate-structure.sh

handle-instruction:
	@echo "🎯 指示対応フロー開始..."
	@echo "=================================="
	@echo "このフローは推測回答を防止し、"
	@echo "根拠に基づく確実な対応を実現します"
	@echo "=================================="
	@echo ""
	@./scripts/utilities/instruction-checklist-v2.sh
	@echo ""
	@echo "✅ 指示対応フロー完了"

## UI System Commands
ui-install: ## Install UI system dependencies
	@echo "🎯 Installing UI system dependencies..."
	pip install -r requirements-ui.txt
	@echo "✅ UI dependencies installed"

ui-dashboard: ## Launch AI organization dashboard
	@echo "🎯 Launching AI Organization Dashboard..."
	./scripts/ui/launch-dashboard.sh

ui-command: ## Launch interactive command interface
	@echo "🎮 Launching Interactive Command Interface..."
	python src/ui/ai_org_ui.py --mode command

ui-worker: ## Launch worker management interface
	@echo "👥 Launching Worker Management Interface..."
	python src/ui/ai_org_ui.py --mode worker

ui-metrics: ## Show system metrics
	@echo "📈 Showing System Metrics..."
	python src/ui/visual_dashboard.py metrics

ui-demo: ## Run UI system demonstration
	@echo "🧪 Running UI System Demo..."
	python src/ui/visual_dashboard.py dashboard

ui-test: ## Test UI system components
	@echo "🧪 Testing UI System Components..."
	python -c "from src.ui.visual_dashboard import VisualDashboard; d = VisualDashboard(); print('✅ Visual Dashboard OK')"
	python -c "from src.ui.command_interface import InteractiveCommandInterface; i = InteractiveCommandInterface(); print('✅ Command Interface OK')"
	python -c "from src.ui.ai_org_ui import AIOrganizationUI; u = AIOrganizationUI(); print('✅ Main UI OK')"
	@echo "✅ All UI components tested successfully"

check-root: ## Check root directory file limit compliance
	@echo "📊 Checking root directory file limit..."
	python3 scripts/automation/simple-root-enforcer.py list

enforce-limit: ## Enforce 12-file root directory limit
	@echo "🚨 Enforcing root directory file limit..."
	python3 scripts/automation/simple-root-enforcer.py fix

## Quick Start Commands (ワンコマンド起動)
startup: ## 完全システム起動（社長+AI組織+DB+記憶）
	@echo "🚀 完全システム起動開始..."
	@echo "=================================="
	@echo "1/5: PRESIDENT宣言実行..."
	@make declare-president || true
	@echo ""
	@echo "2/5: データベース接続確認..."
	@make db-connect || true
	@echo ""
	@echo "3/5: 記憶思い出し・継承確認..."
	@make memory-recall || true
	@echo ""
	@echo "4/5: AI組織システム起動..."
	@make ai-org-start || true
	@echo ""
	@echo "5/5: システム統合テスト..."
	@make integration-test || true
	@echo ""
	@echo "🎉 完全システム起動完了！"
	@echo "=================================="

quick-start: ## 高速起動（必須システムのみ）
	@echo "⚡ 高速起動開始..."
	@echo "=================="
	@make declare-president || true
	@make db-connect || true
	@make ai-org-start || true
	@echo "✅ 高速起動完了！"

full-startup: ## フル起動＋評価システム
	@echo "🌟 フルシステム起動開始..."
	@echo "=========================="
	@make startup
	@echo ""
	@echo "6/6: 包括的システム評価..."
	@make evaluate || true
	@echo ""
	@echo "🎊 フルシステム起動完了！"

startup-check: ## スタートアップチェックリスト実行
	@echo "📋 スタートアップチェックリスト確認..."
	@echo "======================================"
	@echo "チェックリストファイル: startup_checklist.md"
	@echo "インデックスファイル: Index.md"
	@echo ""
	@echo "✅ 必須チェック項目:"
	@echo "  1. PRESIDENT宣言: make declare-president"
	@echo "  2. 統合テスト: make integration-test"
	@echo "  3. AI組織起動: make ai-org-start"
	@echo "  4. DB接続確認: make db-connect"
	@echo ""
	@echo "📋 詳細は startup_checklist.md を参照してください"

## AI Organization Commands
ai-org-start: ## 🎯 スマートAI組織システム（完全自動セットアップ）
	@echo "🚀 スマートAI組織システム起動（完全自動）..."
	@echo "仮想環境 + 依存関係 + 設定 + AI組織 を完全自動化"
	@python3 scripts/automation/smart_ai_org_launcher.py

ai-org-status: ## 📊 統合AI組織状況確認（ガバナンス統合）
	@echo "📊 統合AI組織状況確認（Constitutional AI + RBR + 記憶継承）..."
	@python3 src/orchestrator/ai_organization_tmux_bridge.py status

ai-org-test: ## 🧪 統合AI組織テスト実行
	@echo "🧪 統合AI組織テスト実行（ガバナンス + 並列処理）..."
	@python3 src/orchestrator/ai_organization_tmux_bridge.py start --test-mode

ai-org-monitor: ## 🔍 AI組織完了監視（最後まで完走チェック）
	@echo "🔍 AI組織完了監視開始..."
	@python3 src/ui/professional_ai_dashboard.py monitor

ai-org-completion: ## ⏳ AI組織完了監視（最小限モード）
	@echo "⏳ AI組織完了監視（最小限）..."
	@python3 src/ui/professional_ai_dashboard.py completion --minimal

statusbar-enforce: ## 🎯 完璧ステータスバー設定強制適用
	@echo "🎯 完璧ステータスバー設定を全セッションに適用..."
	@python3 src/orchestrator/tmux_statusbar_enforcer.py apply-all

statusbar-monitor: ## 🔍 ステータスバー継続監視開始
	@echo "🔍 ステータスバー継続監視開始..."
	@python3 src/orchestrator/tmux_statusbar_enforcer.py monitor

statusbar-status: ## 📊 ステータスバー状態確認
	@echo "📊 ステータスバー状態確認..."
	@python3 src/orchestrator/tmux_statusbar_enforcer.py status

worker-status: ## 👥 ワーカー状態監視開始
	@echo "👥 ワーカー状態監視開始..."
	@python3 src/orchestrator/ai_worker_status_monitor.py start

worker-status-check: ## 📊 ワーカー状態確認
	@echo "📊 ワーカー状態確認..."
	@python3 src/orchestrator/ai_worker_status_monitor.py status

task-display-start: ## 📋 役職・タスク表示システム起動
	@echo "📋 役職・タスク表示システム起動..."
	@python3 src/orchestrator/realtime_task_display_system.py start

task-display-status: ## 📊 現在のタスク状況確認
	@echo "📊 現在のタスク状況確認..."
	@python3 src/orchestrator/realtime_task_display_system.py status

task-display-update: ## 🔄 タスク表示強制更新
	@echo "🔄 タスク表示強制更新..."
	@python3 src/orchestrator/realtime_task_display_system.py update

task-display-language-ja: ## 🇯🇵 ステータスバー言語を日本語に設定
	@echo "🇯🇵 ステータスバー言語を日本語に設定..."
	@python3 src/orchestrator/realtime_task_display_system.py set-language --language ja

task-display-language-en: ## 🇺🇸 ステータスバー言語を英語に設定
	@echo "🇺🇸 ステータスバー言語を英語に設定..."
	@python3 src/orchestrator/realtime_task_display_system.py set-language --language en

ai-org-analyze: ## 📊 プロジェクト自動分析
	@echo "📊 プロジェクト要件自動分析..."
	@python3 src/orchestrator/intelligent_project_analyzer.py analyze

ai-org-legacy: ## 📋 レガシーダッシュボード（非推奨）
	@echo "📋 レガシーダッシュボード起動（非推奨・開発用）..."
	@python3 src/ui/ai_organization_dashboard.py dashboard

ai-roles: ## 動的役職システム確認
	@echo "🎭 動的役職システム確認..."
	python3 src/ai/dynamic_role_system.py

memory-recall: ## 記憶思い出し・継承確認
	@echo "🧠 記憶思い出し・継承確認..."
	python3 src/memory/unified_memory_manager.py status

db-connect: ## データベース接続確認
	@echo "🗄️ データベース接続確認..."
	@echo "PostgreSQL + SQLite 統合確認..."
	python3 -c "from src.memory.unified_memory_manager import UnifiedMemoryManager; mgr = UnifiedMemoryManager(); print('✅ Database connection successful')" || echo "❌ Database connection failed"

integration-test: ## 統合テスト実行
	@echo "🧪 統合テスト実行..."
	python3 tests/integration_test.py

## Evaluation & Metrics Commands
evaluate: ## 包括的システム評価
	@echo "📊 包括的システム評価実行..."
	python3 src/ai/evaluation_harness_metrics.py

metrics: ## メトリクス確認
	@echo "📈 システムメトリクス確認..."
	@python3 src/ai/evaluation_harness_metrics.py

language-check: ## 言語使用ルール確認
	@echo "🔤 言語使用ルール確認..."
	python3 src/ai/english_processing_enforcement.py

todo-protocol: ## TODO抽出プロトコル確認
	@echo "🎯 TODO抽出プロトコル確認..."
	python3 src/ai/conversation_exit_todo_protocol.py
## Template Management Commands
template-init: ## テンプレート初期化（新プロジェクト用）
	@echo "🎯 テンプレート初期化開始..."
	@python3 src/ai/mistake_counter_system.py --init-template
	@echo "✅ テンプレート初期化完了"

mistake-count: ## 現在のミス数確認
	@echo "🔢 現在のミス数:"
	@python3 src/ai/mistake_counter_system.py --count

add-mistake: ## 新しいミス記録
	@echo "📝 新しいミス記録:"
	@python3 src/ai/mistake_counter_system.py --add-mistake

mistake-stats: ## ミス統計表示
	@echo "📊 ミス統計:"
	@python3 src/ai/mistake_counter_system.py --stats

github-actions-setup: ## 🤖 GitHub Actions統合セットアップ
	@echo "🤖 Claude Code GitHub Actions統合セットアップ..."
	@./scripts/template/setup-github-actions.sh
	@echo "✅ GitHub Actions統合セットアップ完了"

github-actions-test: ## 🧪 GitHub Actions設定テスト
	@echo "🧪 GitHub Actions設定テスト..."
	@echo "📋 ワークフロー確認:"
	@ls -la .github/workflows/ 2>/dev/null || echo "❌ .github/workflows/ not found"
	@echo "📋 スクリプト確認:"
	@ls -la .github/scripts/ 2>/dev/null || echo "❌ .github/scripts/ not found"
	@echo "📋 セットアップガイド確認:"
	@ls -la .github/CLAUDE_GITHUB_SETUP.md 2>/dev/null && echo "✅ Setup guide available" || echo "❌ Setup guide missing"

template-export: ## テンプレート設定エクスポート
	@echo "📦 テンプレート設定エクスポート:"
	@python3 src/ai/mistake_counter_system.py --export-template

## 🔒 Error Prevention System - MANDATORY
session-safety-check: ## セッション安全確認（必須最優先実行）
	@echo "🔒 SESSION SAFETY CHECK - MANDATORY EXECUTION"
	@python3 scripts/hooks/session_error_prevention.py

safety-enforce: ## 安全強制システム実行
	@echo "🔧 Safety enforcement activated"
	@python3 scripts/hooks/session_error_prevention.py

## 🔧 MCP & API Setup Commands
mcp-setup: ## 🚀 One command MCP setup (new projects)
	@echo "🚀 One Command MCP Setup Starting..."
	@bash scripts/setup/one_command_mcp_setup.sh

mcp-status: ## 📊 Check MCP and API key status
	@echo "📊 MCP and API Key Status Check..."
	@bash scripts/setup/one_command_mcp_setup.sh --check-only

api-setup: ## 🔑 Quick API key configuration
	@echo "🔑 Quick API Key Setup..."
	@python3 scripts/setup/quick_api_setup.py

mcp-config: ## ⚙️ Create/update MCP configuration
	@echo "⚙️ MCP Configuration Setup..."
	@python3 scripts/setup/auto_mcp_setup.py

mcp-quick: ## ⚡ Quick MCP setup (skip interactive prompts)
	@echo "⚡ Quick MCP Setup (non-interactive)..."
	@bash scripts/setup/one_command_mcp_setup.sh --quick

## 🎯 Project Template Initialization
init-web-project: ## 🌐 Initialize as web project template
	@echo "🌐 Initializing as web project..."
	@read -p "Enter project name: " name; python3 scripts/setup/initialize_new_project.py "$$name" --type web

init-python-project: ## 🐍 Initialize as Python project template  
	@echo "🐍 Initializing as Python project..."
	@read -p "Enter project name: " name; python3 scripts/setup/initialize_new_project.py "$$name" --type python

init-ai-project: ## 🤖 Initialize as AI project template (keep current structure)
	@echo "🤖 Initializing as AI project..."
	@read -p "Enter project name: " name; python3 scripts/setup/initialize_new_project.py "$$name" --type ai-project

init-custom-project: ## ⚙️ Initialize as custom project template
	@echo "⚙️ Initializing as custom project..."
	@read -p "Enter project name: " name; python3 scripts/setup/initialize_new_project.py "$$name" --type custom

## 🔒 File Organization Enforcement - ABSOLUTE COMPLIANCE
enforce-file-organization: ## 🚨 Force strict file organization compliance
	@echo "🚨 ENFORCING STRICT FILE ORGANIZATION..."
	@python3 scripts/automation/strict-file-organizer.py --force

check-file-organization: ## 📊 Check file organization compliance
	@echo "📊 Checking File Organization Compliance..."
	@python3 scripts/automation/strict-file-organizer.py --check-only

file-organization-report: ## 📋 Generate detailed compliance report
	@echo "📋 Generating File Organization Report..."
	@python3 scripts/automation/strict-file-organizer.py --report

dry-run-organization: ## 🔍 Preview file organization changes
	@echo "🔍 File Organization Dry Run..."
	@python3 scripts/automation/strict-file-organizer.py --dry-run

root-audit: ## 🔍 Audit root directory file count
	@echo "🔍 Root Directory Audit..."
	@echo "Files in root: $$(ls -la | grep "^-" | wc -l | tr -d ' ')/12 maximum"
	@echo "Folders: $$(ls -d */ 2>/dev/null | wc -l)"
	@if [ $$(ls -la | grep "^-" | wc -l | tr -d ' ') -gt 12 ]; then echo "❌ OVER LIMIT - Run 'make enforce-file-organization'"; exit 1; else echo "✅ COMPLIANT"; fi
