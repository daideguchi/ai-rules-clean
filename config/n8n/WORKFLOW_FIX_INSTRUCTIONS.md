
# n8nワークフロー修正手順

## 問題: Webhookは受信するがSupabaseに送信されていない

### 修正手順:

1. **n8nワークフローエディタにアクセス**
   https://dd1107.app.n8n.cloud

2. **claude-performanceワークフローを開く**

3. **HTTP Requestノードを追加**
   - Webhook受信後のノードとして追加
   - Method: POST
   - URL: https://hetcpqtsineqaopnnvtn.supabase.co/rest/v1/ai_performance_log

4. **Headers設定**
   ```
   apikey: {{$env.SUPABASE_ANON_KEY}}
   Authorization: Bearer {{$env.SUPABASE_ANON_KEY}}
   Content-Type: application/json
   ```

5. **Body設定 (JSON)**
   ```json
   {
     "session_id": "{{$json.session_id}}",
     "task_success": {{$json.success || $json.task_success}},
     "execution_time": {{$json.execution_time}},
     "tool_calls_count": {{$json.tools_used ? $json.tools_used.length : $json.tool_calls_count}},
     "tool_calls": {{$json.tools_used || $json.tool_calls}},
     "error_count": {{$json.error_count || 0}},
     "thinking_tag_used": {{$json.thinking_tag_used || false}},
     "todo_tracking": {{$json.todo_tracking || false}},
     "task_complexity": "{{$json.task_complexity || 'medium'}}",
     "learning_score": {{$json.learning_score || 0}},
     "success_patterns": {{$json.success_patterns || []}},
     "failure_patterns": {{$json.failure_patterns || []}}
   }
   ```

6. **環境変数設定**
   n8n設定で環境変数を追加:
   ```
   SUPABASE_ANON_KEY=[Your Supabase Anon Key]
   ```

7. **テスト実行**
   ```bash
   python3 scripts/setup/n8n_supabase_debug.py
   ```
