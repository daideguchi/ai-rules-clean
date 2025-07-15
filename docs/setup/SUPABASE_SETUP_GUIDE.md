# Supabase自律成長システム完全セットアップガイド

## ✅ 完了済み
- Supabase MCP設定追加
- 環境変数設定
- n8nワークフロー作成
- SQLテーブル定義作成

## 🔧 必要な作業

### 1. Supabase Personal Access Token作成
1. [Supabase Dashboard](https://app.supabase.com) → Account → Personal Access Tokens
2. "Create new token"をクリック
3. 名前: `Claude MCP AI Growth`
4. トークンをコピーして.envファイルの`SUPABASE_ACCESS_TOKEN`に設定

### 2. Service Role Key取得（n8n用）
1. Supabase Dashboard → Settings → API
2. **Service Role Key**をコピー（secret keyの方）
3. n8n接続設定で使用

### 3. データベーステーブル作成
```sql
-- 以下を Supabase Dashboard → SQL Editor で実行
-- ファイル: config/supabase/ai_growth_tables.sql を使用
```

### 4. n8n接続設定
1. n8nで新しいCredential作成
2. Type: PostgreSQL
3. 設定値:
   - Host: `hetcpqtsineqaopnnvtn.supabase.co`
   - Database: `postgres` 
   - User: `postgres`
   - Password: `[Service Role Key]`
   - Port: `5432`
   - SSL: `require`

### 5. ワークフローインポート
- ファイル: `config/n8n/workflows/supabase_ai_tracker.json`
- SQLiteエラー一切なし！完全クラウド対応

## 🧬 システム構成
```
Claude Code → Supabase MCP → Supabase DB
     ↓
n8n Webhook → AI分析 → Supabase PostgreSQL
     ↓
自律成長システム → CLAUDE.md進化
```

## 🎯 期待効果
- **100%クラウド**: localhost依存なし
- **完全自律**: AIが自動的に賢くなる
- **データ永続化**: 全パフォーマンスデータをSupabaseに保存
- **リアルタイム学習**: 成功/失敗パターンを即座に分析

## 🔒 セキュリティ
- Row Level Security有効
- Read-only MCP接続
- Personal Access Token利用
- プロジェクト範囲限定

完了後、Claude Code再起動でSupabase MCPサーバーが利用可能になります！