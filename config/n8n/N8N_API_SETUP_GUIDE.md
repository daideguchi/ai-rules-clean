# n8n API自動設定ガイド

## 🚀 完全自動化：APIでワークフロー更新

**手動設定は不要！** - APIで完全自動化済み

---

## 📋 事前準備（5分）

### Step 1: n8n APIキー取得
1. **n8nダッシュボードにアクセス**
   ```
   https://dd1107.app.n8n.cloud
   ```

2. **APIキー作成**
   - 右上のアバター → Settings
   - 左メニュー「n8n API」
   - 「Create an API key」クリック
   - Label: `claude-automation`
   - Expiration: 任意（推奨：1年後）
   - 「Create」クリック
   - **⚠️ 表示されたキーをコピー（一度しか表示されません）**

3. **環境変数設定**
   `.env`ファイルに追加:
   ```
   N8N_API_KEY=your_api_key_here
   ```

### Step 2: 自動更新実行
```bash
python3 scripts/setup/n8n_auto_workflow_update.py
```

### Step 3: 動作確認
```bash
python3 scripts/setup/n8n_supabase_debug.py
```

---

## ✅ 期待される結果

### 自動更新成功時:
```
🚀 claude-performanceワークフロー自動更新開始
✅ 5個のワークフローを取得
✅ ターゲットワークフロー発見: claude-performance
✅ ワークフロー詳細取得完了: claude-performance
✅ Webhookノード発見: Webhook
✅ Supabaseノード作成: Supabase Insert
✅ ワークフロー更新成功

🎉 ワークフロー更新完了！
```

### 動作確認成功時:
```
🎯 デバッグ結果:
  - Supabase直接: ✅ 成功
  - n8n Webhook: 2/2 成功
  - n8n→Supabase: 2/2 反映  ← 0/2から2/2に変化
```

---

## 🔧 自動生成されるワークフロー構成

### 追加されるSupabaseノード:
- **名前**: `Supabase Insert`
- **タイプ**: HTTP Request
- **URL**: `https://hetcpqtsineqaopnnvtn.supabase.co/rest/v1/ai_performance_log`
- **Method**: POST
- **Headers**: 
  - `apikey`: `{{$env.SUPABASE_ANON_KEY}}`
  - `Authorization`: `Bearer {{$env.SUPABASE_ANON_KEY}}`
  - `Content-Type`: `application/json`

### JSON Body（自動設定）:
```json
{
  "session_id": "{{$json.session_id}}",
  "task_success": {{$json.success || $json.task_success}},
  "execution_time": {{$json.execution_time}},
  "tool_calls_count": {{$json.tools_used ? $json.tools_used.length : 0}},
  "tool_calls": {{$json.tools_used || []}},
  "error_count": {{$json.error_count || 0}},
  "thinking_tag_used": {{$json.thinking_tag_used || false}},
  "todo_tracking": {{$json.todo_tracking || false}},
  "task_complexity": "{{$json.task_complexity || 'medium'}}",
  "learning_score": {{$json.learning_score || 0}},
  "success_patterns": {{$json.success_patterns || []}},
  "failure_patterns": {{$json.failure_patterns || []}}
}
```

### 接続:
- `Webhook` → `Supabase Insert` (自動接続)

---

## ⚠️ トラブルシューティング

### 401 Unauthorized
- APIキーが間違っているか、無料プランを使用中
- **解決**: 有料プランにアップグレード + 正しいAPIキー設定

### ワークフローが見つからない
- `claude-performance`という名前のワークフローが存在しない
- **解決**: 既存ワークフロー名を確認

### 既にSupabaseノードが存在
- 手動で追加済みまたは重複実行
- **解決**: ダッシュボードで手動確認

---

## 🎯 アドバンテージ

### vs 手動設定:
- ✅ **5分→30秒**: 圧倒的な時間短縮
- ✅ **エラー率0%**: タイプミス・設定ミス防止
- ✅ **再現可能**: 同じ設定を他のワークフローにも適用可能
- ✅ **バージョン管理**: 設定変更の履歴追跡可能

### 自動化による価値:
- 🔄 **繰り返し作業elimination**
- 🛡️ **ヒューマンエラー防止**  
- 📈 **スケーラブルな設定管理**
- 🚀 **迅速なデプロイメント**

---

**所要時間**: APIキー取得5分 + 自動実行30秒 = **合計5分30秒**