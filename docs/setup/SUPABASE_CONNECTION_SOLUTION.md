# Supabase PostgreSQL接続問題解決ガイド

## 🚨 問題: Service Role Key ≠ Database Password

**現在のエラー原因**: 
- n8nにService Role Keyを使用している
- PostgreSQL接続にはDatabase Passwordが必要

## 🔧 解決手順

### 1️⃣ Database Password確認
**Supabase Dashboard**:
```
https://app.supabase.com/project/hetcpqtsineqaopnnvtn/settings/database
```

**Database password**セクションで：
- 現在のパスワード確認 または
- **Reset database password**で新しいパスワード設定

### 2️⃣ 正しい接続設定

**n8n PostgreSQL Credential設定**:
```
Type: PostgreSQL
Host: hetcpqtsineqaopnnvtn.supabase.co
Database: postgres
User: postgres
Password: [Database Password] ← Service Role Keyではない！
Port: 5432
SSL Mode: require
```

### 3️⃣ 代替解決法: Supabase Client使用

**Supabase Client**なら**Service Role Key**が使用可能：
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://hetcpqtsineqaopnnvtn.supabase.co',
  'sb_secret_Duj9K4FLWZDIIjNbef5RLA_p0Wbj4Xa' // Service Role Key
)
```

## 🎯 推奨解決策

**Option A**: Database Password取得してPostgreSQL接続
**Option B**: HTTP Request + Supabase REST API使用

## 🔗 必要なアクション

1. **Supabase Dashboard** → **Settings** → **Database**
2. Database password確認/リセット
3. n8n Credential更新
4. ワークフロー再テスト