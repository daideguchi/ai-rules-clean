#!/bin/bash
# tmux Perfect Setup Script - 完璧な設定を一発で適用
# 二度と忘れないように独立スクリプト化

echo "🎯 tmux完璧設定開始..."

# 既存セッション削除
tmux kill-session -t multiagent 2>/dev/null

# 4分割ペイン作成
tmux new-session -d -s multiagent
tmux split-window -t multiagent -h
tmux split-window -t multiagent:0.0 -v
tmux split-window -t multiagent:0.2 -v

# ペインタイトル設定（上部・文字部分のみ薄いグレー背景）
tmux set-option -t multiagent pane-border-status top
tmux set-option -t multiagent pane-border-format "#[bg=colour240,fg=white] #T #[default]"

# ステータスバー設定（下部・薄いグレー背景）
tmux set-option -t multiagent status-position bottom
tmux set-option -t multiagent status-bg colour240
tmux set-option -t multiagent status-left "#[bg=colour240,fg=white,bold] 🤖 AI組織システム #[default]"
tmux set-option -t multiagent status-right "#[bg=colour240,fg=white]%Y-%m-%d %H:%M:%S"

# ワーカータイトル設定（絵文字+役職名+タスク形式）
tmux select-pane -t multiagent:0.0 -T "👔 部長: 待機中"
tmux select-pane -t multiagent:0.1 -T "💻 作業員1: 待機中"
tmux select-pane -t multiagent:0.2 -T "🔧 作業員2: 待機中"
tmux select-pane -t multiagent:0.3 -T "🎨 作業員3: 待機中"

# 自動リネーム無効
tmux set-option -t multiagent automatic-rename off

echo "✅ tmux完璧設定完了！"
echo "📋 設定内容:"
echo "  - 4分割ペイン構成"
echo "  - ペインタイトル上部（文字部分のみ薄いグレー背景）"
echo "  - ステータスバー下部（薄いグレー背景）"
echo "  - 白色テキスト統一"
echo "  - 役職フォーマット: 👔 部長: 待機中"