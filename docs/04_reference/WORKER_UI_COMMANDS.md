# 🎯 AI組織ワーカー視覚化コマンド完全ガイド

## 🚀 クイックスタート

### 基本起動コマンド
```bash
# メインダッシュボード起動（8ワーカーパネル表示）
make ui-dashboard
# または
python src/ui/ai_org_ui.py --mode dashboard

# インタラクティブコマンド起動
make ui-command
# または  
python src/ui/command_interface.py

# ワーカー管理専用UI
make ui-worker
# または
python src/ui/visual_dashboard.py
```

## 📊 ワーカーペイン確認コマンド

### 1. 全ワーカー状況確認
```bash
# 基本表示
workers

# 詳細ステータス
workers --detailed

# リアルタイム監視（1秒更新）
workers --live

# 特定ワーカーフィルター
workers --role president
workers --status active
```

### 2. 個別ワーカー詳細
```bash
# ワーカー詳細表示
worker <worker_id>

# 例：PRESIDENT詳細
worker president

# ワーカーログ表示
worker president --logs

# ワーカータスク履歴
worker president --history
```

### 3. ステータスバー確認
```bash
# システム全体ステータス
status

# パフォーマンスメトリクス
metrics

# ヘルスチェック
health

# システムリソース使用状況
resources
```

## 🎮 インタラクティブコマンド

### ワーカー管理コマンド
```bash
# タスク割り当て
assign <worker_id> <task_description>

# ワーカー開始/停止
start <worker_id>
stop <worker_id>
restart <worker_id>

# ワーカー設定変更
configure <worker_id> --priority high
configure <worker_id> --resources 2GB
```

### 表示制御コマンド
```bash
# レイアウト変更
layout grid       # 2x4グリッド（デフォルト）
layout list       # リスト表示
layout compact    # コンパクト表示

# 更新間隔設定
refresh 1s        # 1秒間隔
refresh 5s        # 5秒間隔
refresh manual    # 手動更新のみ
```

## 🎨 カラーコード

### ワーカーステータス
- 🟢 **Active**: ワーカー稼働中、タスク実行
- 🟡 **Idle**: ワーカー待機中、タスク待ち
- 🔵 **Processing**: ワーカー処理中、高負荷状態
- 🔴 **Error**: ワーカーエラー状態、要対応
- ⚫ **Offline**: ワーカー停止状態

### パフォーマンス指標
- 🟢 **Normal**: 0-70% リソース使用
- 🟡 **Warning**: 70-90% リソース使用
- 🔴 **Critical**: 90%+ リソース使用

## 🖥️ UI特化コマンド

### パネル操作
```bash
# パネルサイズ調整
panel resize <worker_id> --width 40 --height 20

# パネル位置変更
panel move <worker_id> --position top-left

# パネル表示/非表示
panel show <worker_id>
panel hide <worker_id>
```

### フィルタリング・検索
```bash
# ワーカー検索
search <keyword>

# タスクフィルター
filter --task-type analysis
filter --priority high
filter --status active

# 時間範囲フィルター
filter --since 1h        # 過去1時間
filter --since today     # 今日
filter --since yesterday # 昨日
```

## 🔧 トラブルシューティング

### よくある問題と解決
```bash
# UI起動失敗
pip install -r requirements-ui.txt
python src/ui/ai_org_ui.py --debug

# ワーカー応答なし
worker restart all
system reset

# パフォーマンス低下
metrics --detailed
resources --cleanup
```

### デバッグコマンド
```bash
# デバッグモード起動
python src/ui/ai_org_ui.py --debug --verbose

# ログレベル変更
loglevel debug
loglevel info
loglevel warning

# システム診断
diagnose
diagnose --full
```

## 📱 ショートカットキー

### クイックアクセス
- `w` → workers（ワーカー一覧）
- `s` → status（システム状況）
- `m` → metrics（メトリクス）
- `h` → help（ヘルプ）
- `q` → quit（終了）
- `r` → refresh（手動更新）

### ワーカー選択
- `1-8` → 対応するワーカー詳細
- `ctrl+r` → 全ワーカー再起動
- `ctrl+s` → 設定保存
- `ctrl+l` → ログクリア

## 🎯 実用例

### 日常的な監視
```bash
# 朝の状況確認
make ui-dashboard
workers --live

# タスク進捗確認
metrics --tasks
status --detailed

# 問題発生時の対応
worker <error_worker_id> --logs
diagnose --full
restart <error_worker_id>
```

### パフォーマンス最適化
```bash
# リソース使用状況確認
resources --detailed

# 負荷分散調整
assign coordinator "Load balancing optimization"
configure data_engineer --priority medium

# システム最適化
system optimize
refresh 2s
```

## 💡 ベストプラクティス

1. **定期的監視**: `workers --live`で継続監視
2. **エラー対応**: 🔴ステータス発見時は即座に`worker <id> --logs`確認
3. **パフォーマンス**: `metrics`を定期的にチェック
4. **リソース管理**: `resources`でメモリ・CPU監視
5. **プロアクティブ**: `health`コマンドで予防的チェック

---

**🎉 Professional UI/UX System - Complete Command Reference**

このコマンドガイドで8役職AI組織の効率的な管理と監視が可能です。