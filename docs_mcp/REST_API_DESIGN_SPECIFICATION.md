# asagami AI × Cursor Rules REST API設計仕様書

## 概要
asagami AIとCursor Rulesの連携を実現するREST API設計仕様書です。学習データの分析からCursor Rulesの生成、実践ログの収集まで、継続的な学習改善サイクルを支援します。

## 1. API概要

### 1.1 目的
- 学習データの分析と集計
- 個人・チーム別の弱点検出
- Cursor Rulesの自動生成と配信
- 実践ログの収集とフィードバック処理

### 1.2 基本情報
- **ベースURL**: `https://api.asagami.ai/v1`
- **認証**: JWT Bearer Token
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8

## 2. 認証・認可

### 2.1 認証方式
```http
Authorization: Bearer <JWT_TOKEN>
```

### 2.2 スコープ
- `read:learning_data` - 学習データ読み取り
- `write:feedback` - フィードバック書き込み
- `generate:rules` - Cursor Rules生成
- `admin:analytics` - 管理者分析機能

## 3. 学習データ分析API

### 3.1 個人学習データ取得
```
GET /api/cursor-integration/learning-data/{user_id}
```

**パラメータ:**
- `user_id` (required): ユーザーID
- `period` (optional): 分析期間（日数、デフォルト30）
- `subject_filter` (optional): 科目フィルター

**レスポンス例:**
```json
{
  "user_id": 123,
  "analysis_period": 30,
  "summary": {
    "total_notes": 45,
    "total_questions": 180,
    "average_score": 78.5,
    "study_hours": 67.2
  },
  "weak_points": [
    {
      "topic": "データベース設計",
      "subject_id": 5,
      "score": 62,
      "question_count": 15,
      "error_patterns": ["正規化の理解不足", "インデックス設計の誤り"],
      "recommended_actions": ["正規化理論の復習", "パフォーマンステストの実践"]
    }
  ],
  "strong_points": [
    {
      "topic": "API設計",
      "subject_id": 3,
      "score": 94,
      "mastery_level": "advanced"
    }
  ],
  "learning_patterns": {
    "preferred_study_time": "09:00-11:00",
    "avg_session_duration": 45,
    "retention_rate": 0.82,
    "difficulty_preference": "intermediate"
  }
}
```

### 3.2 チーム学習分析
```
GET /api/cursor-integration/team-analytics/{department_id}
```

**レスポンス例:**
```json
{
  "department_id": 10,
  "team_size": 12,
  "analysis_date": "2025-07-13",
  "common_weak_points": [
    {
      "topic": "セキュリティ実装",
      "affected_members": 8,
      "average_score": 65,
      "priority": "high"
    }
  ],
  "skill_distribution": {
    "beginner": 3,
    "intermediate": 7,
    "advanced": 2
  },
  "improvement_suggestions": [
    "セキュリティ基礎のチーム勉強会",
    "コードレビューでのセキュリティチェック強化"
  ]
}
```

## 4. Cursor Rules生成API

### 4.1 個人用ルール生成
```
POST /api/cursor-integration/generate-rules
```

**リクエスト例:**
```json
{
  "user_id": 123,
  "analysis_data": {
    "weak_points": [...],
    "strong_points": [...],
    "learning_patterns": {...}
  },
  "rule_config": {
    "strictness_level": "intermediate",
    "focus_areas": ["security", "performance"],
    "include_templates": true,
    "auto_suggestions": true
  }
}
```

**レスポンス例:**
```json
{
  "rule_id": "rule_123_20250713",
  "generated_at": "2025-07-13T10:30:00Z",
  "user_profile": {
    "user_id": 123,
    "skill_level": "intermediate",
    "specializations": ["web_development", "database"]
  },
  "cursor_rules": {
    "security": {
      "sql_injection": {
        "enabled": true,
        "severity": "error",
        "message": "SQLインジェクション対策：プリペアドステートメントを使用してください",
        "examples": ["examples/prepared_statement.py"],
        "auto_fix": true
      },
      "password_handling": {
        "enabled": true,
        "severity": "warning",
        "message": "パスワードの平文保存は禁止です。ハッシュ化を実装してください"
      }
    },
    "performance": {
      "database_queries": {
        "enabled": true,
        "message": "N+1クエリ問題に注意：バッチロード処理を検討してください"
      }
    },
    "code_templates": [
      {
        "name": "secure_database_connection",
        "file_path": "templates/db_connection.py",
        "description": "セキュアなデータベース接続テンプレート"
      }
    ]
  },
  "personalized_suggestions": [
    "データベース設計の復習をお勧めします",
    "セキュリティ実装のベストプラクティスを確認してください"
  ]
}
```

### 4.2 チーム用ルール生成
```
POST /api/cursor-integration/generate-team-rules
```

**リクエスト例:**
```json
{
  "department_id": 10,
  "team_analytics": {...},
  "rule_config": {
    "shared_standards": true,
    "compliance_rules": ["GDPR", "PCI_DSS"],
    "team_best_practices": true
  }
}
```

## 5. 実践ログ収集API

### 5.1 開発セッションログ送信
```
POST /api/cursor-integration/practice-logs
```

**リクエスト例:**
```json
{
  "user_id": 123,
  "session_id": "sess_20250713_001",
  "session_start": "2025-07-13T09:00:00Z",
  "session_end": "2025-07-13T10:30:00Z",
  "development_data": {
    "errors_encountered": [
      {
        "error_type": "syntax_error",
        "error_message": "Uncaught TypeError: Cannot read property",
        "file_path": "src/auth.js",
        "line_number": 45,
        "resolution_time": 180,
        "resolution_method": "cursor_suggestion"
      }
    ],
    "code_completions": [
      {
        "trigger": "database connection",
        "suggestion_used": true,
        "completion_time": 5,
        "satisfaction_rating": 4
      }
    ],
    "rule_triggers": [
      {
        "rule_id": "security.sql_injection",
        "triggered_at": "2025-07-13T09:45:00Z",
        "user_action": "accepted",
        "effectiveness": "high"
      }
    ],
    "productivity_metrics": {
      "lines_of_code": 156,
      "files_modified": 3,
      "commits_made": 2,
      "test_coverage": 0.78
    }
  }
}
```

### 5.2 エラーパターン分析
```
GET /api/cursor-integration/error-patterns/{user_id}
```

**レスポンス例:**
```json
{
  "user_id": 123,
  "analysis_period": 7,
  "common_errors": [
    {
      "error_category": "database_queries",
      "frequency": 12,
      "avg_resolution_time": 240,
      "improvement_trend": "stable",
      "recommendations": [
        "ORM使用方法の復習",
        "データベース設計パターンの学習"
      ]
    }
  ],
  "skill_improvement": [
    {
      "skill": "error_handling",
      "before_score": 65,
      "current_score": 78,
      "improvement_rate": 0.2
    }
  ]
}
```

## 6. フィードバック処理API

### 6.1 学習コンテンツ更新提案
```
POST /api/cursor-integration/feedback-analysis
```

**リクエスト例:**
```json
{
  "user_id": 123,
  "feedback_data": {
    "error_patterns": [...],
    "skill_gaps": [...],
    "improvement_areas": [...]
  },
  "auto_generate": true
}
```

**レスポンス例:**
```json
{
  "feedback_id": "fb_123_20250713",
  "analysis_results": {
    "new_weak_points_detected": [
      {
        "topic": "非同期処理",
        "confidence": 0.85,
        "evidence": ["Promise未処理エラー3回", "async/await使用ミス2回"]
      }
    ],
    "improvement_confirmed": [
      {
        "topic": "SQL最適化",
        "improvement_score": 15,
        "evidence": ["N+1クエリエラー0回（前週3回）"]
      }
    ]
  },
  "content_suggestions": [
    {
      "type": "new_question",
      "topic": "非同期処理",
      "difficulty": "intermediate",
      "description": "Promise とasync/awaitの適切な使い分け"
    },
    {
      "type": "update_rule",
      "rule_id": "performance.database_queries",
      "change": "strictness_increase",
      "reason": "改善が確認されたため、より高度なパターンを追加"
    }
  ]
}
```

### 6.2 継続的改善レポート
```
GET /api/cursor-integration/improvement-report/{user_id}
```

**レスポンス例:**
```json
{
  "user_id": 123,
  "report_period": "2025-06-13 to 2025-07-13",
  "overall_improvement": {
    "score_change": "+12.5",
    "skill_level_change": "intermediate → upper-intermediate",
    "confidence_index": 0.78
  },
  "learning_effectiveness": {
    "asagami_study_impact": 0.65,
    "cursor_practice_impact": 0.72,
    "combined_effectiveness": 0.89
  },
  "next_focus_areas": [
    "クラウドアーキテクチャ設計",
    "マイクロサービス実装"
  ],
  "recommended_actions": [
    "AWSコースの受講",
    "Docker実践プロジェクトの開始"
  ]
}
```

## 7. 統計・分析API

### 7.1 システム全体統計
```
GET /api/cursor-integration/system-analytics
```

### 7.2 ROI分析
```
GET /api/cursor-integration/roi-analysis/{organization_id}
```

## 8. Webhook統合

### 8.1 リアルタイム通知
```
POST /webhooks/cursor-integration/notifications
```

### 8.2 自動ルール更新
```
POST /webhooks/cursor-integration/rule-updates
```

## 9. エラーハンドリング

### 9.1 エラーレスポンス形式
```json
{
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "学習データの分析に失敗しました",
    "details": "insufficient_data",
    "timestamp": "2025-07-13T10:30:00Z"
  }
}
```

### 9.2 エラーコード一覧
- `INVALID_USER_ID` - 無効なユーザーID
- `INSUFFICIENT_DATA` - 分析に必要なデータが不足
- `RULE_GENERATION_FAILED` - ルール生成に失敗
- `UNAUTHORIZED_ACCESS` - 認証エラー

## 10. レート制限

### 10.1 制限値
- 学習データ取得: 100 requests/hour/user
- ルール生成: 10 requests/hour/user
- ログ送信: 1000 requests/hour/user

## 11. 実装優先度

### Phase 1 (MVP)
- 基本的な学習データ分析API
- シンプルなCursor Rules生成
- 基本的な実践ログ収集

### Phase 2 (拡張機能)
- 高度な分析機能
- チーム機能
- リアルタイム更新

### Phase 3 (AI強化)
- 機械学習による予測分析
- 自動的な学習コンテンツ生成
- パーソナライゼーションの高度化

---

**作成日**: 2025-07-13  
**バージョン**: 1.0  
**作成者**: asagami AI開発チーム