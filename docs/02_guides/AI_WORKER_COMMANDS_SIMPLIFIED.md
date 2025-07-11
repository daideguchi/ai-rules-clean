# 🎯 AI Worker Commands - Simplified Version

## 超シンプル：必要なコマンドは3つだけ

### 1. ワーカー確認
```bash
# 全ワーカーの状況を一覧表示
aiw ps

# 出力例:
# NAME        STATUS   UPTIME   CPU%   MEM%   TASK
# president   ACTIVE   2h15m    45%    2.1GB  Strategic Leadership
# coordinator IDLE     2h15m    12%    1.8GB  Waiting for tasks
# analyst     ACTIVE   2h15m    38%    2.3GB  Requirements Analysis
```

### 2. ワーカーログ確認
```bash
# 特定ワーカーのログを表示
aiw logs president

# リアルタイムログ監視
aiw logs president -f

# 最新10行のみ表示
aiw logs president -n 10
```

### 3. ワーカー再起動
```bash
# 特定ワーカー再起動
aiw restart president

# 全ワーカー再起動
aiw restart --all
```

## 実際のコマンド実装

### 現在の実装
```bash
# 1. ワーカー確認
python3 src/ui/quick_demo.py

# 2. 詳細ログ確認
python3 src/ui/ai_org_ui.py --mode command
# then type: workers --detailed

# 3. ワーカー管理
python3 src/ui/ai_org_ui.py --mode worker
```

### 推奨エイリアス設定
```bash
# ~/.bashrc または ~/.zshrc に追加
alias aiw-ps='python3 src/ui/quick_demo.py'
alias aiw-logs='python3 src/ui/ai_org_ui.py --mode command'
alias aiw-restart='python3 src/ui/ai_org_ui.py --mode worker'
```

## 最もシンプルな使用方法

### 日常使用
```bash
# 1. ワーカー状況確認
aiw-ps

# 2. 問題がある場合のログ確認
aiw-logs

# 3. 必要に応じて再起動
aiw-restart
```

**これで十分です。他のコマンドは不要です。**