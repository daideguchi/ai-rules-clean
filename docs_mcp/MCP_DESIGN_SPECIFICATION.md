# asagami AI × Cursor Rules MCP設計仕様書

## 概要
asagami AIの学習データを分析し、個人・チームの弱点に基づいてCursor Rulesを自動生成するModel Context Protocol（MCP）サーバーの設計仕様書です。

## 1. システム概要

### 1.1 目的
- 学習データから適応型開発環境を構築
- 個人の苦手分野に特化したCursor Rulesの自動生成
- 実践ログとの継続的フィードバックループの実現

### 1.2 基本構成
```
asagami AI (Django) ←→ MCP Server ←→ Cursor (Claude Code)
                         ↕
                   AI Analysis Engine
```

## 2. MCP サーバー仕様

### 2.1 サーバー情報
- **名前**: `asagami-mcp-server`
- **バージョン**: `1.0.0`
- **プロトコル**: MCP v1.0
- **ポート**: 8001

### 2.2 提供ツール

#### 2.2.1 学習データ分析ツール
```json
{
  "name": "analyze_learning_data",
  "description": "学習データを分析して弱点と強みを特定",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "integer", "description": "ユーザーID"},
      "department_id": {"type": "integer", "description": "部門ID（オプション）"},
      "analysis_period": {"type": "string", "description": "分析期間（日数）", "default": "30"},
      "analysis_type": {"type": "string", "enum": ["individual", "team", "department"], "default": "individual"}
    },
    "required": ["user_id"]
  }
}
```

#### 2.2.2 Cursor Rules生成ツール
```json
{
  "name": "generate_cursor_rules",
  "description": "分析結果からCursor Rulesを生成",
  "inputSchema": {
    "type": "object",
    "properties": {
      "analysis_data": {"type": "object", "description": "分析結果データ"},
      "rule_template": {"type": "string", "description": "ルールテンプレート種別"},
      "target_skills": {"type": "array", "items": {"type": "string"}, "description": "対象スキル領域"},
      "severity_level": {"type": "string", "enum": ["basic", "intermediate", "advanced"], "default": "intermediate"}
    },
    "required": ["analysis_data"]
  }
}
```

#### 2.2.3 実践ログ収集ツール
```json
{
  "name": "collect_practice_logs",
  "description": "Cursorでの実践ログを収集・分析",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "integer", "description": "ユーザーID"},
      "session_id": {"type": "string", "description": "セッションID"},
      "error_logs": {"type": "array", "description": "エラーログ"},
      "completion_data": {"type": "object", "description": "コード補完データ"},
      "time_metrics": {"type": "object", "description": "時間指標"}
    },
    "required": ["user_id", "session_id"]
  }
}
```

#### 2.2.4 フィードバック処理ツール
```json
{
  "name": "process_feedback",
  "description": "実践ログからフィードバックを処理し、学習コンテンツを更新",
  "inputSchema": {
    "type": "object",
    "properties": {
      "practice_data": {"type": "object", "description": "実践データ"},
      "feedback_type": {"type": "string", "enum": ["error_pattern", "skill_gap", "improvement"]},
      "auto_generate_content": {"type": "boolean", "default": true}
    },
    "required": ["practice_data", "feedback_type"]
  }
}
```

## 3. データ構造

### 3.1 学習分析データ
```json
{
  "user_id": 123,
  "analysis_date": "2025-07-13",
  "weak_points": [
    {
      "topic": "データ暗号化",
      "score": 65,
      "problem_areas": ["鍵管理", "暗号化アルゴリズム選択"],
      "frequency": 8,
      "improvement_suggestions": ["基礎理論の復習", "実装パターンの練習"]
    }
  ],
  "strong_points": [
    {
      "topic": "API設計",
      "score": 92,
      "mastery_level": "advanced"
    }
  ],
  "learning_patterns": {
    "preferred_time": "morning",
    "avg_session_duration": 45,
    "retention_rate": 0.78
  }
}
```

### 3.2 Cursor Rules構造
```json
{
  "version": "1.0",
  "generated_at": "2025-07-13T10:30:00Z",
  "user_profile": {
    "user_id": 123,
    "skill_level": "intermediate",
    "focus_areas": ["security", "database"]
  },
  "rules": {
    "security": {
      "encryption": {
        "reminder": "暗号化実装時は鍵管理の要件を必ず確認してください",
        "auto_suggestions": true,
        "code_templates": ["aes_encryption.py", "key_management.py"]
      }
    },
    "code_quality": {
      "warnings": ["hardcoded_secrets", "sql_injection_risk"],
      "auto_fix": true
    }
  }
}
```

## 4. API連携

### 4.1 asagami AI連携エンドポイント
- `GET /api/mcp/learning-data/{user_id}` - 学習データ取得
- `GET /api/mcp/question-results/{user_id}` - 問題解答結果取得
- `GET /api/mcp/team-analytics/{department_id}` - チーム分析データ取得
- `POST /api/mcp/feedback` - フィードバックデータ送信

### 4.2 Cursor連携エンドポイント
- `POST /mcp/cursor-rules` - Cursor Rules生成
- `POST /mcp/practice-logs` - 実践ログ送信
- `GET /mcp/personalized-rules/{user_id}` - 個人用ルール取得

## 5. AI分析エンジン

### 5.1 弱点検出アルゴリズム
```python
def detect_weak_points(user_data):
    """
    学習データから弱点を検出
    - 問題解答の正答率分析
    - 回答時間の統計分析
    - 間違いパターンの分類
    - トピック間の関連性分析
    """
    pass
```

### 5.2 ルール生成ロジック
```python
def generate_adaptive_rules(weak_points, user_profile):
    """
    個人に特化したCursor Rulesを生成
    - 弱点に対する具体的なアドバイス
    - コードテンプレートの提案
    - エラー防止のためのチェック
    - 学習リソースへのリンク
    """
    pass
```

## 6. セキュリティ

### 6.1 認証・認可
- JWT トークンベース認証
- ユーザー別データアクセス制御
- 組織レベルの権限管理

### 6.2 データ保護
- 個人学習データの暗号化
- GDPR準拠のデータ処理
- 監査ログの記録

## 7. 拡張性

### 7.1 プラグインアーキテクチャ
- カスタム分析エンジンの追加
- 外部学習プラットフォーム連携
- サードパーティーIDE対応

### 7.2 スケーラビリティ
- 水平スケーリング対応
- キャッシュ戦略
- 非同期処理

## 8. モニタリング

### 8.1 メトリクス
- MCP サーバーのパフォーマンス
- ルール生成の成功率
- ユーザーの学習改善率

### 8.2 ログ
- API呼び出しログ
- エラーログ
- ユーザー行動ログ

## 9. 実装ロードマップ

### Phase 1: 基本MCP サーバー
- 学習データ分析機能
- 基本的なCursor Rules生成

### Phase 2: 高度な分析
- AI による詳細分析
- パーソナライズされたルール生成

### Phase 3: フィードバックループ
- 実践ログ収集
- 継続的改善システム

---

**作成日**: 2025-07-13  
**バージョン**: 1.0  
**作成者**: asagami AI開発チーム