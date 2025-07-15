# n8n→Supabase統合修正手順

## 現在の問題
- Webhook受信: ✅ 成功
- Supabaseデータ反映: ❌ 失敗（ワークフロー途中停止）

## 修正手順

### 1. n8nワークフロー確認
URL: https://dd1107.app.n8n.cloud

**Current Webhook URL**: 
```
POST https://dd1107.app.n8n.cloud/webhook/claude-performance
```

### 2. ワークフロー構成修正

**Step 1: Webhook設定**
- Path: `claude-performance`
- HTTP Method: `POST`
- Authentication: `None`
- Respond: `Immediately`

**Step 2: Supabase Node追加**
```javascript
// Supabase HTTP Request設定
URL: https://hetcpqtsineqaopnnvtn.supabase.co/rest/v1/ai_performance_log
Method: POST
Headers:
  apikey: {{SUPABASE_ANON_KEY}}
  Authorization: Bearer {{SUPABASE_ANON_KEY}}
  Content-Type: application/json

Body (JSON):
{
  "session_id": "{{$json.session_id}}",
  "task_success": {{$json.success}},
  "execution_time": {{$json.execution_time}},
  "tool_calls_count": {{$json.tools_used ? $json.tools_used.length : 0}},
  "tool_calls": {{$json.tools_used}},
  "error_count": {{$json.error_count}},
  "thinking_tag_used": {{$json.thinking_tag_used}},
  "todo_tracking": {{$json.todo_tracking}},
  "task_complexity": "{{$json.task_complexity}}",
  "user_feedback": "{{$json.user_feedback}}",
  "learning_score": {{$json.learning_score || 0}},
  "success_patterns": [],
  "failure_patterns": []
}
```

### 3. 環境変数設定
n8nで以下の環境変数を設定:
```
SUPABASE_ANON_KEY={{process.env.SUPABASE_ANON_KEY}}
```

### 4. テスト用データ形式
```json
{
  "session_id": "test_session_123",
  "success": true,
  "execution_time": 45.2,
  "tools_used": ["Read", "Write", "Bash"],
  "error_count": 0,
  "thinking_tag_used": true,
  "todo_tracking": true,
  "task_complexity": "medium",
  "user_feedback": "Test successful",
  "learning_score": 4,
  "timestamp": "2025-07-14T16:52:00.000Z"
}
```

### 5. 動作確認
修正後、以下のテストで確認:
```bash
python3 scripts/autonomous/test_supabase_final.py
```

期待結果:
```
3️⃣ n8n→Supabase統合テスト...
  ✅ n8n Webhook送信成功
  ✅ n8n→Supabase統合成功確認
```