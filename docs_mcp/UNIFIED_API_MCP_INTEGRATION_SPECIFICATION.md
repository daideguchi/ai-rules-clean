# asagami AI × Cursor Rules 統合システム設計仕様書

## 🎯 プロジェクト概要

### システムの目的
asagami AIの学習データを分析し、個人・チームの弱点に基づいてCursor Rulesを自動生成する「適応型開発環境」を構築します。これにより、学習→実践→フィードバック→改善の継続的なサイクルを実現し、開発者の能力向上と開発品質の向上を同時に達成します。

### 核心的価値提案
- **個人適応型支援**: 学習データから個人の弱点を特定し、専用のCursor Rulesを生成
- **継続的改善**: 実際の開発ログをフィードバックして学習コンテンツを最適化
- **チーム品質向上**: 組織全体のスキルレベル均一化とベストプラクティス共有

## 🏗️ システムアーキテクチャ

### 全体構成図
```
┌─────────────────────┐    ┌────────────────────┐    ┌─────────────────────┐
│    asagami AI       │    │    MCP Server      │    │     Cursor IDE      │
│    (Django)         │◄──►│    (Python)        │◄──►│   (Claude Code)     │
├─────────────────────┤    ├────────────────────┤    ├─────────────────────┤
│• 学習ノート管理     │    │• 学習データ分析    │    │• 開発支援           │
│• 問題自動生成       │    │• AI弱点検出        │    │• エラーログ収集     │
│• 解答結果分析       │    │• Cursor Rules生成  │    │• 適応型アシスタント │
│• 組織・ユーザー管理 │    │• フィードバック処理│    │• 実践データ送信     │
│• 統計・レポート     │    │• 継続的学習改善    │    │• ルール適用         │
└─────────────────────┘    └────────────────────┘    └─────────────────────┘
```

### データフロー詳細
```
1. 学習フェーズ
   asagami AI: ノート作成 → 問題生成 → 解答 → 結果記録

2. 分析フェーズ  
   MCP Server: 学習データ取得 → AI分析 → 弱点検出 → パターン抽出

3. ルール生成フェーズ
   MCP Server: 個人プロファイル作成 → Cursor Rules生成 → 配信

4. 実践フェーズ
   Cursor: 開発支援 → エラー/成功ログ記録 → フィードバック送信

5. 改善フェーズ
   MCP Server: ログ分析 → 新たな弱点検出 → 学習コンテンツ更新提案
```

## 🔧 技術仕様

### バックエンド技術スタック
- **Django 4.2+**: 既存asagami AIシステムの拡張
- **PostgreSQL 14+**: 学習データ・分析結果の永続化
- **Redis 7+**: キャッシュ・セッション管理・リアルタイム通信
- **Celery 5+**: 重い分析処理の非同期実行
- **OpenAI API (GPT-4)**: 学習データ分析・ルール生成AI

### MCP Server技術スタック
- **Python 3.9+**: メインプログラミング言語
- **mcp (Model Context Protocol)**: Claude Codeとの標準連携
- **FastAPI 0.104+**: 高性能API層
- **asyncio**: 非同期処理によるパフォーマンス最適化

### フロントエンド（拡張）
- **React 18.2+**: 既存UIの拡張
- **WebSocket**: リアルタイム通知・更新
- **Chart.js**: 学習進捗・分析結果の可視化

## 🗄️ データ設計

### 新規データベースモデル

#### CursorRuleProfile（Cursor Rules管理）
```python
class CursorRuleProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rule_version = models.CharField(max_length=50)  # ルールバージョン管理
    generated_at = models.DateTimeField(auto_now_add=True)
    rule_config = models.JSONField()  # 生成されたルール内容
    skill_focus_areas = models.JSONField()  # 重点スキル領域
    effectiveness_score = models.FloatField(default=0.0)  # ルール効果測定
    is_active = models.BooleanField(default=True)
```

#### PracticeLog（実践ログ）
```python
class PracticeLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # 開発セッション詳細
    files_modified = models.IntegerField(default=0)
    lines_of_code = models.IntegerField(default=0)
    commits_made = models.IntegerField(default=0)
    
    # エラー・完了データ
    error_data = models.JSONField(default=list)  # エラー詳細
    completion_data = models.JSONField(default=list)  # コード補完データ
    rule_trigger_data = models.JSONField(default=list)  # ルール発火データ
    
    # メトリクス
    productivity_score = models.FloatField(default=0.0)
    satisfaction_rating = models.IntegerField(null=True, blank=True)  # 1-5評価
```

#### LearningAnalysis（学習分析結果）
```python
class LearningAnalysis(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    analysis_date = models.DateField(auto_now_add=True)
    analysis_period_days = models.IntegerField(default=30)
    
    # 分析結果
    weak_points = models.JSONField()  # 弱点詳細リスト
    strong_points = models.JSONField()  # 強み詳細リスト
    skill_level = models.CharField(max_length=20)  # beginner/intermediate/advanced
    improvement_suggestions = models.JSONField()  # 改善提案リスト
    
    # 信頼度・精度指標
    confidence_score = models.FloatField()  # 分析信頼度（0.0-1.0）
    data_sufficiency = models.BooleanField()  # 分析十分性フラグ
```

### データ構造例

#### 学習分析データ構造
```json
{
  "user_id": 123,
  "analysis_date": "2025-07-13",
  "analysis_period": 30,
  "summary": {
    "total_notes": 45,
    "total_questions": 180,
    "average_score": 78.5,
    "study_hours": 67.2,
    "skill_level": "intermediate"
  },
  "weak_points": [
    {
      "topic": "データベース設計",
      "subject_id": 5,
      "average_score": 62,
      "question_count": 15,
      "error_frequency": 8,
      "error_patterns": [
        "正規化理論の理解不足",
        "インデックス設計の判断ミス",
        "外部キー制約の実装エラー"
      ],
      "improvement_priority": "high",
      "estimated_study_time": "8-12時間",
      "recommended_actions": [
        "正規化理論の基礎復習（第1-3正規形）",
        "実際のDBでインデックス効果を測定",
        "外部キー制約のベストプラクティス学習"
      ]
    }
  ],
  "strong_points": [
    {
      "topic": "REST API設計",
      "subject_id": 3,
      "average_score": 94,
      "mastery_level": "advanced",
      "expertise_areas": ["RESTful設計原則", "HTTP ステータスコード", "認証実装"]
    }
  ],
  "learning_patterns": {
    "preferred_study_time": "09:00-11:00",
    "average_session_duration": 45,
    "retention_rate": 0.82,
    "difficulty_preference": "intermediate_to_advanced",
    "most_effective_question_types": ["scenario_based", "hands_on_coding"]
  }
}
```

#### Cursor Rules生成結果
```json
{
  "rule_id": "cr_123_20250713_v1",
  "generated_at": "2025-07-13T10:30:00Z",
  "user_profile": {
    "user_id": 123,
    "skill_level": "intermediate",
    "specializations": ["web_development", "database_design"],
    "learning_goals": ["improve_db_design", "enhance_security_awareness"]
  },
  "cursor_rules": {
    "database": {
      "normalization": {
        "enabled": true,
        "severity": "error",
        "message": "データベース正規化チェック: {table_name}の設計を確認してください。第3正規形まで適用されていますか？",
        "trigger_patterns": ["CREATE TABLE", "ALTER TABLE"],
        "auto_suggestions": true,
        "reference_links": [
          "https://asagami.ai/notes/normalization-guide",
          "https://asagami.ai/practice/db-design-checker"
        ]
      },
      "index_optimization": {
        "enabled": true,
        "severity": "warning", 
        "message": "インデックス最適化: このクエリにインデックスが必要かもしれません。EXPLAIN PLANで確認してください。",
        "trigger_patterns": ["SELECT .* WHERE", "JOIN"],
        "code_templates": ["templates/index_example.sql"]
      }
    },
    "security": {
      "sql_injection": {
        "enabled": true,
        "severity": "error",
        "message": "SQLインジェクション対策: プリペアドステートメントまたはORMを使用してください",
        "trigger_patterns": ["SELECT.*\\+", "INSERT.*\\+", "UPDATE.*\\+"],
        "auto_fix": true,
        "fix_template": "prepared_statement_template.py"
      }
    },
    "performance": {
      "n_plus_one": {
        "enabled": true,
        "severity": "warning",
        "message": "N+1クエリ問題の可能性: バッチロード処理を検討してください",
        "trigger_patterns": ["for.*in.*:", "while.*:"],
        "optimization_suggestions": ["eager_loading", "bulk_operations"]
      }
    }
  },
  "code_templates": [
    {
      "name": "secure_database_connection",
      "file_path": "templates/secure_db_conn.py",
      "description": "セキュアなデータベース接続テンプレート（接続プール、エラーハンドリング含む）",
      "usage_context": ["database_connection", "orm_setup"]
    },
    {
      "name": "index_performance_check",
      "file_path": "templates/index_check.sql", 
      "description": "インデックス効果測定用SQLテンプレート",
      "usage_context": ["performance_tuning", "query_optimization"]
    }
  ],
  "personalized_suggestions": [
    "データベース設計の実践的課題に取り組むことをお勧めします",
    "正規化理論の確認テストを週1回実施してみてください",
    "実際のプロジェクトでEXPLAIN PLANを使った最適化を試してみてください"
  ],
  "effectiveness_tracking": {
    "previous_error_count": 12,
    "target_error_reduction": 0.5,
    "measurement_period": 30,
    "success_metrics": ["error_reduction", "code_quality_score", "development_velocity"]
  }
}
```

## 🌐 API仕様

### RESTful API エンドポイント

#### 1. 学習データ分析API

**個人学習データ取得**
```
GET /api/cursor-integration/learning-data/{user_id}
Parameters:
  - user_id (required): ユーザーID
  - period (optional): 分析期間（日数、デフォルト30）
  - include_team_context (optional): チーム比較データを含むか
  - detail_level (optional): 詳細レベル（summary/detailed/comprehensive）

Response: 上記の学習分析データ構造
```

**チーム学習分析**
```
GET /api/cursor-integration/team-analytics/{department_id}
Parameters:
  - department_id (required): 部門ID
  - comparison_period (optional): 比較期間設定
  - skill_breakdown (optional): スキル別詳細分析

Response:
{
  "department_id": 10,
  "team_size": 12,
  "analysis_date": "2025-07-13",
  "skill_distribution": {
    "database_design": {"beginner": 3, "intermediate": 7, "advanced": 2},
    "security": {"beginner": 5, "intermediate": 5, "advanced": 2},
    "api_development": {"beginner": 2, "intermediate": 8, "advanced": 2}
  },
  "common_weak_points": [
    {
      "topic": "セキュリティ実装",
      "affected_members": 8,
      "average_score": 65,
      "priority": "high",
      "team_impact": "プロジェクト全体のセキュリティリスク"
    }
  ],
  "improvement_roadmap": [
    {
      "phase": "immediate",
      "actions": ["セキュリティ基礎のチーム勉強会"],
      "timeline": "2週間",
      "expected_improvement": 15
    }
  ]
}
```

#### 2. Cursor Rules生成API

**個人用ルール生成**
```
POST /api/cursor-integration/generate-rules

Request Body:
{
  "user_id": 123,
  "analysis_data": { /* 学習分析結果 */ },
  "rule_config": {
    "strictness_level": "intermediate",  // strict/intermediate/lenient
    "focus_areas": ["security", "performance", "maintainability"],
    "include_templates": true,
    "auto_suggestions": true,
    "development_context": "web_application"  // context for better rules
  },
  "integration_preferences": {
    "notification_level": "moderate",  // high/moderate/low
    "auto_fix_enabled": true,
    "learning_mode": true  // より詳細な説明とリンクを提供
  }
}

Response: 上記のCursor Rules生成結果構造
```

**チーム標準ルール生成**
```
POST /api/cursor-integration/generate-team-rules

Request Body:
{
  "department_id": 10,
  "team_analytics": { /* チーム分析結果 */ },
  "organizational_standards": {
    "compliance_requirements": ["GDPR", "PCI_DSS", "SOX"],
    "coding_standards": "google_style_guide",
    "security_level": "enterprise",
    "performance_requirements": "high_traffic"
  },
  "customization_level": "organization"  // organization/team/individual
}
```

#### 3. 実践ログ収集API

**開発セッションログ送信**
```
POST /api/cursor-integration/practice-logs

Request Body:
{
  "user_id": 123,
  "session_id": "sess_20250713_001",
  "session_metadata": {
    "start_time": "2025-07-13T09:00:00Z",
    "end_time": "2025-07-13T10:30:00Z",
    "project_type": "web_application",
    "development_environment": "local",
    "cursor_version": "0.42.0"
  },
  "development_activity": {
    "files_modified": [
      {
        "file_path": "src/auth/login.py",
        "language": "python",
        "modification_type": "enhancement",
        "lines_added": 23,
        "lines_deleted": 5
      }
    ],
    "commits": [
      {
        "commit_hash": "a1b2c3d",
        "message": "Add secure login validation",
        "timestamp": "2025-07-13T10:15:00Z"
      }
    ]
  },
  "error_events": [
    {
      "error_type": "runtime_error",
      "error_category": "authentication",
      "error_message": "Invalid token format",
      "file_path": "src/auth/token_validator.py",
      "line_number": 45,
      "resolution_time_seconds": 180,
      "resolution_method": "cursor_suggestion",
      "user_satisfaction": 4,  // 1-5 scale
      "learning_value": "high"  // high/medium/low
    }
  ],
  "rule_interactions": [
    {
      "rule_id": "security.sql_injection",
      "triggered_at": "2025-07-13T09:45:00Z",
      "trigger_context": "UPDATE users SET password = ? WHERE id = ?",
      "user_action": "accepted",  // accepted/dismissed/modified
      "effectiveness_rating": 5,
      "user_feedback": "Very helpful reminder"
    }
  ],
  "productivity_metrics": {
    "code_completion_usage": 67,  // percentage
    "auto_fix_acceptance_rate": 0.78,
    "average_time_to_resolve_error": 156,  // seconds
    "focus_time_percentage": 0.85,
    "context_switch_count": 3
  }
}

Response:
{
  "log_id": "log_123_20250713_001",
  "processing_status": "accepted",
  "analysis_scheduled": true,
  "immediate_insights": [
    "authentication 関連のエラーが多く発生しています",
    "セキュリティルールの効果が確認されました"
  ],
  "next_analysis_eta": "2025-07-13T11:00:00Z"
}
```

#### 4. フィードバック分析API

**継続的改善レポート**
```
GET /api/cursor-integration/improvement-report/{user_id}

Parameters:
  - report_period: 期間（weekly/monthly/quarterly）
  - include_projections: 将来予測を含むか
  - detail_level: 詳細レベル

Response:
{
  "user_id": 123,
  "report_period": "2025-06-13 to 2025-07-13",
  "overall_progress": {
    "skill_score_change": "+12.5",
    "skill_level_progression": "intermediate → upper-intermediate",
    "confidence_improvement": 0.23,
    "error_reduction_percentage": 0.45
  },
  "learning_effectiveness": {
    "asagami_study_contribution": 0.65,
    "cursor_practice_contribution": 0.72,
    "synergy_effect": 0.89,  // 単体使用時と比較した相乗効果
    "optimal_study_practice_ratio": "40:60"
  },
  "skill_improvements": [
    {
      "skill": "database_design",
      "before_score": 62,
      "current_score": 78,
      "improvement_velocity": "+2.1 points/week",
      "plateau_risk": "low",
      "next_milestone": "advanced_level"
    }
  ],
  "cursor_rules_effectiveness": [
    {
      "rule_category": "security",
      "error_prevention_count": 15,
      "false_positive_rate": 0.12,
      "user_satisfaction": 4.3,
      "adjustment_recommendation": "increase_strictness"
    }
  ],
  "future_projections": {
    "expected_skill_level": "advanced",
    "eta_to_next_level": "6-8 weeks",
    "recommended_focus_areas": ["microservices", "cloud_architecture"],
    "optimal_learning_path": [
      "完了: データベース設計基礎",
      "進行中: セキュリティ実装",
      "次期: パフォーマンス最適化",
      "将来: アーキテクチャ設計"
    ]
  }
}
```

## 🤖 MCP (Model Context Protocol) 実装

### MCPサーバー仕様

**サーバー基本情報**
- サーバー名: `asagami-mcp-server`
- バージョン: `1.0.0`
- プロトコル: MCP v1.0
- ポート: 8001

### 提供ツール詳細

#### 1. analyze_learning_data
```python
@mcp_server.tool()
async def analyze_learning_data(
    user_id: int, 
    analysis_period: int = 30,
    analysis_type: str = "comprehensive"
) -> dict:
    """
    学習データを総合的に分析し、個人の学習パターンと弱点を特定
    
    Args:
        user_id: ユーザーID
        analysis_period: 分析期間（日数）
        analysis_type: 分析タイプ（comprehensive/focused/quick）
    
    Returns:
        詳細な学習分析結果（弱点、強み、学習パターン、改善提案）
    """
    # Django APIからユーザーの学習データを取得
    learning_data = await fetch_user_learning_data(user_id, analysis_period)
    
    # OpenAI GPT-4による詳細分析
    analysis_prompt = create_analysis_prompt(learning_data, analysis_type)
    ai_analysis = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": analysis_prompt}],
        response_format={"type": "json_object"}
    )
    
    # 分析結果の後処理と検証
    processed_result = validate_and_enhance_analysis(ai_analysis)
    
    return processed_result
```

#### 2. generate_cursor_rules
```python
@mcp_server.tool()
async def generate_cursor_rules(
    analysis_data: dict,
    customization_level: str = "personalized",
    rule_strictness: str = "intermediate"
) -> dict:
    """
    学習分析結果から個人に最適化されたCursor Rulesを生成
    
    Args:
        analysis_data: analyze_learning_dataの出力結果
        customization_level: カスタマイズレベル（basic/personalized/expert）
        rule_strictness: ルールの厳格度（lenient/intermediate/strict）
    
    Returns:
        完全にカスタマイズされたCursor Rules設定
    """
    # ユーザープロファイルの構築
    user_profile = build_user_profile(analysis_data)
    
    # 弱点に基づくルール生成戦略の決定
    rule_strategy = determine_rule_strategy(
        user_profile.weak_points,
        user_profile.skill_level,
        rule_strictness
    )
    
    # ルールテンプレートのロードとカスタマイズ
    base_rules = load_rule_templates(user_profile.focus_areas)
    customized_rules = customize_rules_for_user(
        base_rules, 
        user_profile, 
        rule_strategy
    )
    
    # コードテンプレートとサンプルの生成
    code_templates = generate_code_templates(user_profile.weak_points)
    
    # 最終ルール構造の構築
    final_rules = {
        "metadata": {
            "generated_for": user_profile.user_id,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "customization_level": customization_level,
            "expected_effectiveness": calculate_expected_effectiveness(user_profile)
        },
        "rules": customized_rules,
        "templates": code_templates,
        "learning_resources": generate_learning_links(user_profile.weak_points)
    }
    
    return final_rules
```

#### 3. process_practice_feedback
```python
@mcp_server.tool()
async def process_practice_feedback(
    practice_logs: list,
    feedback_type: str = "comprehensive"
) -> dict:
    """
    実践ログを分析してフィードバックを生成し、学習計画を更新
    
    Args:
        practice_logs: 実践セッションのログデータ
        feedback_type: フィードバックタイプ（quick/comprehensive/predictive）
    
    Returns:
        フィードバック分析結果と改善提案
    """
    # ログデータの前処理と統合
    consolidated_logs = consolidate_practice_logs(practice_logs)
    
    # エラーパターンの機械学習分析
    error_patterns = analyze_error_patterns(consolidated_logs.errors)
    skill_gaps = detect_skill_gaps(consolidated_logs, error_patterns)
    
    # ルール効果の測定
    rule_effectiveness = measure_rule_effectiveness(
        consolidated_logs.rule_interactions
    )
    
    # 新しい学習目標の提案
    learning_recommendations = generate_learning_recommendations(
        skill_gaps, 
        error_patterns,
        rule_effectiveness
    )
    
    # asagami AIへの学習コンテンツ更新提案
    content_updates = propose_content_updates(learning_recommendations)
    
    return {
        "analysis_summary": {
            "total_sessions": len(practice_logs),
            "error_trend": calculate_error_trend(error_patterns),
            "skill_improvement_rate": calculate_improvement_rate(consolidated_logs),
            "rule_adoption_rate": calculate_rule_adoption(rule_effectiveness)
        },
        "detected_patterns": error_patterns,
        "skill_gap_analysis": skill_gaps,
        "rule_effectiveness": rule_effectiveness,
        "learning_recommendations": learning_recommendations,
        "content_update_proposals": content_updates
    }
```

### MCPサーバー実装例

```python
# mcp_server/main.py
import asyncio
from mcp import McpServer
from mcp.types import Tool, TextContent
import openai
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional

class AsagamiMcpServer(McpServer):
    def __init__(self, django_api_base: str, openai_api_key: str):
        super().__init__("asagami-mcp-server", "1.0.0")
        self.django_api = django_api_base
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.setup_tools()
    
    async def fetch_user_learning_data(self, user_id: int, period: int) -> Dict:
        """Django APIから学習データを取得"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.django_api}/api/cursor-integration/learning-data/{user_id}"
            params = {"period": period, "detail_level": "comprehensive"}
            async with session.get(url, params=params) as response:
                return await response.json()
    
    def create_analysis_prompt(self, learning_data: Dict, analysis_type: str) -> str:
        """AI分析用のプロンプトを生成"""
        base_prompt = f"""
        以下の学習データを詳細に分析し、ユーザーの学習パターンと改善点を特定してください：

        学習統計:
        - 総学習時間: {learning_data.get('summary', {}).get('study_hours', 0)}時間
        - 総問題数: {learning_data.get('summary', {}).get('total_questions', 0)}
        - 平均正答率: {learning_data.get('summary', {}).get('average_score', 0)}%

        科目別成績:
        {json.dumps(learning_data.get('subject_scores', {}), indent=2)}

        最近のエラーパターン:
        {json.dumps(learning_data.get('recent_errors', []), indent=2)}

        分析要求レベル: {analysis_type}

        以下のJSONフォーマットで回答してください：
        {{
            "weak_points": [
                {{
                    "topic": "具体的なトピック名",
                    "severity": "high/medium/low",
                    "evidence": ["具体的な根拠1", "具体的な根拠2"],
                    "improvement_priority": 1-10,
                    "estimated_improvement_time": "時間の見積もり",
                    "specific_actions": ["具体的な行動1", "具体的な行動2"]
                }}
            ],
            "strong_points": [
                {{
                    "topic": "得意分野",
                    "mastery_level": "advanced/expert",
                    "can_mentor_others": true/false
                }}
            ],
            "learning_patterns": {{
                "optimal_study_time": "推奨学習時間帯",
                "effective_question_types": ["効果的な問題タイプ"],
                "learning_velocity": "学習速度の特徴",
                "retention_characteristics": "記憶保持の特徴"
            }},
            "personalized_strategies": [
                "個人に特化した学習戦略1",
                "個人に特化した学習戦略2"
            ]
        }}
        """
        return base_prompt
    
    async def run_server(self):
        """MCPサーバーを起動"""
        await self.serve()

if __name__ == "__main__":
    server = AsagamiMcpServer(
        django_api_base="http://localhost:8000",
        openai_api_key="your-openai-api-key"
    )
    asyncio.run(server.run_server())
```

## 🚀 実装ロードマップ

### Phase 1: 基盤構築 (4週間)
**目標**: MVPの完成と基本的な学習→ルール生成フローの確立

#### Week 1-2: Django拡張

**Step 1: 新規アプリケーションの作成**
```bash
# プロジェクトディレクトリで実行
cd /path/to/asagami-project
python manage.py startapp cursor_integration
```

**Step 2: settings.pyの更新**
```python
# mysite/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'app',
    'cursor_integration',  # 新しく追加
]

# Cursor統合用の設定
CURSOR_INTEGRATION = {
    'MCP_SERVER_URL': 'http://localhost:8001',
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
    'ANALYSIS_CACHE_TIMEOUT': 3600,  # 1時間
    'RULE_GENERATION_TIMEOUT': 300,  # 5分
}

# Celery設定（非同期処理用）
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
```

**Step 3: データベースモデルの実装**
```python
# cursor_integration/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class LearningAnalysis(models.Model):
    """学習データ分析結果を保存"""
    
    ANALYSIS_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_analyses')
    analysis_date = models.DateTimeField(auto_now_add=True)
    analysis_period_days = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, default='pending')
    
    # 分析結果データ
    weak_points = models.JSONField(default=list, blank=True)
    strong_points = models.JSONField(default=list, blank=True)
    skill_level = models.CharField(max_length=20, blank=True)
    learning_patterns = models.JSONField(default=dict, blank=True)
    improvement_suggestions = models.JSONField(default=list, blank=True)
    
    # 分析メタデータ
    confidence_score = models.FloatField(null=True, blank=True)
    data_sufficiency = models.BooleanField(default=False)
    analysis_version = models.CharField(max_length=10, default='1.0')
    
    # 処理時間追跡
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-analysis_date']
        indexes = [
            models.Index(fields=['user', '-analysis_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Analysis for {self.user.username} on {self.analysis_date.date()}"
    
    @property
    def processing_duration(self):
        if self.processing_started_at and self.processing_completed_at:
            return (self.processing_completed_at - self.processing_started_at).total_seconds()
        return None

class CursorRuleProfile(models.Model):
    """生成されたCursor Rulesプロファイル"""
    
    STRICTNESS_CHOICES = [
        ('lenient', 'Lenient'),
        ('intermediate', 'Intermediate'),
        ('strict', 'Strict'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cursor_profiles')
    analysis = models.ForeignKey(LearningAnalysis, on_delete=models.CASCADE, related_name='rule_profiles')
    
    # ルール設定
    rule_version = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    rule_config = models.JSONField()
    code_templates = models.JSONField(default=list)
    learning_resources = models.JSONField(default=list)
    
    # カスタマイズ設定
    strictness_level = models.CharField(max_length=20, choices=STRICTNESS_CHOICES, default='intermediate')
    focus_areas = models.JSONField(default=list)
    auto_suggestions_enabled = models.BooleanField(default=True)
    notification_level = models.CharField(max_length=20, default='moderate')
    
    # 効果測定
    effectiveness_score = models.FloatField(default=0.0)
    user_satisfaction_rating = models.IntegerField(null=True, blank=True)  # 1-5
    usage_count = models.IntegerField(default=0)
    
    # 状態管理
    is_active = models.BooleanField(default=True)
    deployed_at = models.DateTimeField(null=True, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', '-generated_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Rules v{self.rule_version} for {self.user.username}"

class PracticeLog(models.Model):
    """Cursorでの開発実践ログ"""
    
    SESSION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('interrupted', 'Interrupted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_logs')
    cursor_profile = models.ForeignKey(CursorRuleProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    # セッション基本情報
    session_id = models.CharField(max_length=100, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='active')
    
    # プロジェクト情報
    project_name = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(max_length=100, blank=True)
    development_environment = models.CharField(max_length=100, blank=True)
    cursor_version = models.CharField(max_length=50, blank=True)
    
    # 開発活動データ
    files_modified = models.JSONField(default=list)
    lines_added = models.IntegerField(default=0)
    lines_deleted = models.IntegerField(default=0)
    commits_made = models.IntegerField(default=0)
    
    # エラー・完了データ
    error_events = models.JSONField(default=list)
    completion_events = models.JSONField(default=list)
    rule_interactions = models.JSONField(default=list)
    
    # パフォーマンスメトリクス
    code_completion_usage = models.IntegerField(default=0)  # percentage
    auto_fix_acceptance_rate = models.FloatField(default=0.0)
    average_error_resolution_time = models.IntegerField(default=0)  # seconds
    focus_time_percentage = models.FloatField(default=0.0)
    context_switch_count = models.IntegerField(default=0)
    
    # ユーザーフィードバック
    session_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5
    rule_helpfulness = models.IntegerField(null=True, blank=True)  # 1-5
    feedback_comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['session_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} for {self.user.username}"
    
    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return None

class FeedbackAnalysis(models.Model):
    """フィードバック分析結果"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_analyses')
    practice_logs = models.ManyToManyField(PracticeLog, related_name='feedback_analyses')
    
    analysis_date = models.DateTimeField(auto_now_add=True)
    analysis_period_days = models.IntegerField(default=7)
    
    # 分析結果
    new_weak_points = models.JSONField(default=list)
    improved_areas = models.JSONField(default=list)
    error_pattern_analysis = models.JSONField(default=dict)
    rule_effectiveness_metrics = models.JSONField(default=dict)
    
    # 改善提案
    learning_recommendations = models.JSONField(default=list)
    content_update_proposals = models.JSONField(default=list)
    rule_adjustment_suggestions = models.JSONField(default=list)
    
    # メタデータ
    confidence_score = models.FloatField(default=0.0)
    processed_log_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f"Feedback Analysis for {self.user.username} on {self.analysis_date.date()}"
```

**Step 4: データベースマイグレーション**
```bash
# マイグレーションファイルを作成
python manage.py makemigrations cursor_integration

# マイグレーションを実行
python manage.py migrate

# 管理画面での確認用
python manage.py createsuperuser
```

**Step 5: 管理画面設定**
```python
# cursor_integration/admin.py
from django.contrib import admin
from .models import LearningAnalysis, CursorRuleProfile, PracticeLog, FeedbackAnalysis

@admin.register(LearningAnalysis)
class LearningAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'analysis_date', 'status', 'confidence_score', 'data_sufficiency']
    list_filter = ['status', 'analysis_date', 'data_sufficiency']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['id', 'analysis_date', 'processing_duration']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'analysis_period_days', 'status')
        }),
        ('分析結果', {
            'fields': ('weak_points', 'strong_points', 'skill_level', 'learning_patterns'),
            'classes': ('collapse',)
        }),
        ('メタデータ', {
            'fields': ('confidence_score', 'data_sufficiency', 'analysis_version'),
        }),
        ('処理時間', {
            'fields': ('processing_started_at', 'processing_completed_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(CursorRuleProfile)
class CursorRuleProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rule_version', 'generated_at', 'is_active', 'effectiveness_score']
    list_filter = ['is_active', 'strictness_level', 'generated_at']
    search_fields = ['user__username', 'rule_version']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'analysis', 'rule_version', 'is_active')
        }),
        ('ルール設定', {
            'fields': ('rule_config', 'strictness_level', 'focus_areas'),
            'classes': ('collapse',)
        }),
        ('効果測定', {
            'fields': ('effectiveness_score', 'user_satisfaction_rating', 'usage_count')
        })
    )

@admin.register(PracticeLog)
class PracticeLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'start_time', 'status', 'duration_minutes']
    list_filter = ['status', 'start_time', 'project_type']
    search_fields = ['user__username', 'session_id', 'project_name']
    readonly_fields = ['duration_minutes']

@admin.register(FeedbackAnalysis)
class FeedbackAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'analysis_date', 'confidence_score', 'processed_log_count']
    list_filter = ['analysis_date']
    search_fields = ['user__username']
```

#### Week 3-4: MCP サーバー基盤

**Step 1: MCP サーバーディレクトリ構成**
```bash
mkdir mcp_server
cd mcp_server

# ディレクトリ構造を作成
mkdir -p {src,tests,config,templates,logs}
touch {src/__init__.py,tests/__init__.py,main.py,requirements.txt}
```

**Step 2: 依存関係の設定**
```txt
# mcp_server/requirements.txt
mcp>=0.1.0
fastapi>=0.104.0
uvicorn>=0.24.0
openai>=1.0.0
aiohttp>=3.9.0
pydantic>=2.0.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
structlog>=23.0.0
prometheus-client>=0.18.0
```

**Step 3: 環境設定ファイル**
```bash
# mcp_server/.env
OPENAI_API_KEY=your_openai_api_key_here
DJANGO_API_BASE_URL=http://localhost:8000
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
LOG_LEVEL=INFO
PROMETHEUS_PORT=9090

# Redis設定
REDIS_URL=redis://localhost:6379

# 分析設定
DEFAULT_ANALYSIS_PERIOD=30
MAX_ANALYSIS_PERIOD=90
ANALYSIS_CACHE_TTL=3600
```

**Step 4: MCPサーバーメイン実装**
```python
# mcp_server/main.py
import asyncio
import os
import json
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import aiohttp
import openai
from mcp import McpServer
from mcp.types import Tool, TextContent
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ログ設定
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@dataclass
class AnalysisConfig:
    """分析設定"""
    period_days: int = 30
    detail_level: str = "comprehensive"
    include_team_context: bool = False
    confidence_threshold: float = 0.7

@dataclass
class RuleGenerationConfig:
    """ルール生成設定"""
    strictness_level: str = "intermediate"
    customization_level: str = "personalized"
    include_templates: bool = True
    auto_suggestions: bool = True
    focus_areas: List[str] = None

class AsagamiMcpServer(McpServer):
    """asagami AI MCP サーバー"""
    
    def __init__(self):
        super().__init__(
            name="asagami-mcp-server",
            version="1.0.0"
        )
        
        # 設定の初期化
        self.django_api_base = os.getenv("DJANGO_API_BASE_URL", "http://localhost:8000")
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # HTTPクライアント
        self.http_session = None
        
        # キャッシュ（本番環境ではRedisを使用）
        self.analysis_cache = {}
        
        logger.info("MCP Server initialized", 
                   server_name=self.name, 
                   version=self.version)
        
        # ツールの設定
        self.setup_tools()
    
    async def __aenter__(self):
        """非同期コンテキストマネージャー開始"""
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー終了"""
        if self.http_session:
            await self.http_session.close()
    
    def setup_tools(self):
        """MCPツールの設定"""
        
        @self.tool()
        async def analyze_learning_data(
            user_id: int,
            period_days: int = 30,
            detail_level: str = "comprehensive",
            include_team_context: bool = False
        ) -> str:
            """
            学習データを分析してユーザーの弱点と強みを特定
            
            Args:
                user_id: ユーザーID
                period_days: 分析期間（日数）
                detail_level: 詳細レベル（summary/detailed/comprehensive）
                include_team_context: チーム比較を含むか
            
            Returns:
                JSON形式の分析結果
            """
            try:
                logger.info("Starting learning data analysis",
                           user_id=user_id, 
                           period_days=period_days,
                           detail_level=detail_level)
                
                config = AnalysisConfig(
                    period_days=period_days,
                    detail_level=detail_level,
                    include_team_context=include_team_context
                )
                
                # Django APIから学習データを取得
                learning_data = await self.fetch_learning_data(user_id, config)
                
                # AI分析の実行
                analysis_result = await self.perform_ai_analysis(learning_data, config)
                
                # 結果の検証と後処理
                validated_result = self.validate_analysis_result(analysis_result)
                
                # キャッシュに保存
                cache_key = f"analysis_{user_id}_{period_days}_{detail_level}"
                self.analysis_cache[cache_key] = {
                    "result": validated_result,
                    "timestamp": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(hours=1)
                }
                
                logger.info("Learning data analysis completed",
                           user_id=user_id,
                           confidence_score=validated_result.get("confidence_score", 0),
                           weak_points_count=len(validated_result.get("weak_points", [])))
                
                return json.dumps(validated_result, ensure_ascii=False, indent=2)
                
            except Exception as e:
                logger.error("Learning data analysis failed",
                           user_id=user_id,
                           error=str(e),
                           exc_info=True)
                return json.dumps({
                    "error": "分析に失敗しました",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        @self.tool()
        async def generate_cursor_rules(
            analysis_data: str,
            strictness_level: str = "intermediate",
            focus_areas: str = "",
            customization_level: str = "personalized"
        ) -> str:
            """
            学習分析結果からCursor Rulesを生成
            
            Args:
                analysis_data: analyze_learning_dataの出力結果（JSON文字列）
                strictness_level: ルールの厳格度（lenient/intermediate/strict）
                focus_areas: 重点エリア（カンマ区切り）
                customization_level: カスタマイズレベル（basic/personalized/expert）
            
            Returns:
                JSON形式のCursor Rules設定
            """
            try:
                logger.info("Starting Cursor Rules generation",
                           strictness_level=strictness_level,
                           customization_level=customization_level)
                
                # 入力データの解析
                analysis_result = json.loads(analysis_data)
                focus_list = [area.strip() for area in focus_areas.split(",") if area.strip()]
                
                config = RuleGenerationConfig(
                    strictness_level=strictness_level,
                    customization_level=customization_level,
                    focus_areas=focus_list
                )
                
                # ユーザープロファイルの構築
                user_profile = self.build_user_profile(analysis_result)
                
                # ルール生成戦略の決定
                rule_strategy = self.determine_rule_strategy(user_profile, config)
                
                # 基本ルールのロードとカスタマイズ
                cursor_rules = await self.generate_personalized_rules(
                    user_profile, rule_strategy, config
                )
                
                # コードテンプレートの生成
                code_templates = await self.generate_code_templates(user_profile)
                
                # 最終ルール構造の構築
                final_rules = {
                    "metadata": {
                        "generated_at": datetime.utcnow().isoformat(),
                        "user_profile": user_profile,
                        "customization_level": customization_level,
                        "strictness_level": strictness_level,
                        "focus_areas": focus_list,
                        "rule_version": "1.0"
                    },
                    "cursor_rules": cursor_rules,
                    "code_templates": code_templates,
                    "learning_resources": self.generate_learning_resources(user_profile),
                    "effectiveness_tracking": {
                        "metrics_to_track": ["error_reduction", "code_quality", "productivity"],
                        "measurement_period": 30,
                        "success_thresholds": {
                            "error_reduction": 0.3,
                            "code_quality_improvement": 0.2,
                            "productivity_increase": 0.15
                        }
                    }
                }
                
                logger.info("Cursor Rules generation completed",
                           rule_count=len(cursor_rules),
                           template_count=len(code_templates))
                
                return json.dumps(final_rules, ensure_ascii=False, indent=2)
                
            except json.JSONDecodeError as e:
                logger.error("Invalid analysis data format", error=str(e))
                return json.dumps({
                    "error": "分析データの形式が不正です",
                    "details": str(e)
                })
            except Exception as e:
                logger.error("Cursor Rules generation failed", error=str(e), exc_info=True)
                return json.dumps({
                    "error": "ルール生成に失敗しました",
                    "details": str(e)
                })
        
        @self.tool()
        async def process_practice_feedback(
            practice_logs_json: str,
            analysis_type: str = "comprehensive"
        ) -> str:
            """
            実践ログを分析してフィードバックを生成
            
            Args:
                practice_logs_json: 実践ログのJSON配列
                analysis_type: 分析タイプ（quick/comprehensive/predictive）
            
            Returns:
                JSON形式のフィードバック分析結果
            """
            try:
                logger.info("Starting practice feedback processing",
                           analysis_type=analysis_type)
                
                practice_logs = json.loads(practice_logs_json)
                
                # ログデータの統合と前処理
                consolidated_data = self.consolidate_practice_logs(practice_logs)
                
                # エラーパターンの分析
                error_patterns = await self.analyze_error_patterns(consolidated_data)
                
                # スキルギャップの検出
                skill_gaps = self.detect_skill_gaps(consolidated_data, error_patterns)
                
                # ルール効果の測定
                rule_effectiveness = self.measure_rule_effectiveness(consolidated_data)
                
                # 学習改善提案の生成
                learning_recommendations = await self.generate_learning_recommendations(
                    skill_gaps, error_patterns
                )
                
                feedback_result = {
                    "analysis_summary": {
                        "total_sessions": len(practice_logs),
                        "analysis_period": self.calculate_analysis_period(practice_logs),
                        "overall_trend": self.calculate_overall_trend(consolidated_data),
                        "key_insights": error_patterns.get("key_insights", [])
                    },
                    "error_pattern_analysis": error_patterns,
                    "skill_gap_analysis": skill_gaps,
                    "rule_effectiveness": rule_effectiveness,
                    "learning_recommendations": learning_recommendations,
                    "next_actions": self.generate_next_actions(skill_gaps, learning_recommendations)
                }
                
                logger.info("Practice feedback processing completed",
                           sessions_analyzed=len(practice_logs),
                           new_skill_gaps=len(skill_gaps))
                
                return json.dumps(feedback_result, ensure_ascii=False, indent=2)
                
            except Exception as e:
                logger.error("Practice feedback processing failed", error=str(e), exc_info=True)
                return json.dumps({
                    "error": "フィードバック処理に失敗しました",
                    "details": str(e)
                })
    
    async def fetch_learning_data(self, user_id: int, config: AnalysisConfig) -> Dict:
        """Django APIから学習データを取得"""
        
        url = f"{self.django_api_base}/api/cursor-integration/learning-data/{user_id}"
        params = {
            "period": config.period_days,
            "detail_level": config.detail_level,
            "include_team_context": config.include_team_context
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        async with self.http_session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"API request failed: {response.status} - {error_text}")
    
    async def perform_ai_analysis(self, learning_data: Dict, config: AnalysisConfig) -> Dict:
        """OpenAI APIを使用した学習データ分析"""
        
        analysis_prompt = self.create_detailed_analysis_prompt(learning_data, config)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self.get_analysis_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=4000
            )
            
            result = json.loads(response.choices[0].message.content)
            result["ai_model_used"] = "gpt-4"
            result["analysis_timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            raise Exception(f"AI分析に失敗しました: {str(e)}")
    
    def get_analysis_system_prompt(self) -> str:
        """AI分析用のシステムプロンプト"""
        return """
        あなたは学習データ分析の専門家です。プログラミング学習者の学習パターンを分析し、
        具体的で実行可能な改善提案を提供してください。
        
        分析の観点：
        1. 学習効率の評価
        2. 知識のギャップ特定
        3. エラーパターンの分類
        4. 学習スタイルの特定
        5. 改善の優先順位付け
        
        回答は必ずJSON形式で、以下の構造に従ってください：
        - weak_points: 弱点の詳細分析
        - strong_points: 強みの特定
        - learning_patterns: 学習パターンの分析
        - improvement_suggestions: 具体的な改善提案
        - confidence_score: 分析の信頼度（0.0-1.0）
        """
    
    def create_detailed_analysis_prompt(self, learning_data: Dict, config: AnalysisConfig) -> str:
        """詳細な分析プロンプトを作成"""
        
        summary = learning_data.get('summary', {})
        
        prompt = f"""
        以下の学習データを分析してください：

        【基本統計】
        - 学習期間: {config.period_days}日間
        - 総学習時間: {summary.get('study_hours', 0)}時間
        - 作成ノート数: {summary.get('total_notes', 0)}
        - 解答問題数: {summary.get('total_questions', 0)}
        - 平均正答率: {summary.get('average_score', 0)}%
        - 現在のスキルレベル: {summary.get('skill_level', 'unknown')}

        【科目別成績】
        {json.dumps(learning_data.get('subject_scores', {}), ensure_ascii=False, indent=2)}

        【最近のエラーパターン】
        {json.dumps(learning_data.get('recent_errors', []), ensure_ascii=False, indent=2)}

        【学習セッション情報】
        {json.dumps(learning_data.get('session_patterns', {}), ensure_ascii=False, indent=2)}

        【詳細レベル】: {config.detail_level}
        
        この分析結果から、以下の形式でJSONを生成してください：
        
        {{
            "weak_points": [
                {{
                    "topic": "具体的なトピック名",
                    "severity": "high/medium/low",
                    "current_score": 数値,
                    "evidence": ["具体的な根拠1", "具体的な根拠2"],
                    "error_frequency": 数値,
                    "improvement_priority": 1-10,
                    "estimated_improvement_time": "時間の見積もり",
                    "specific_actions": ["具体的な行動1", "具体的な行動2"],
                    "blocking_factors": ["阻害要因1", "阻害要因2"]
                }}
            ],
            "strong_points": [
                {{
                    "topic": "得意分野",
                    "mastery_level": "intermediate/advanced/expert",
                    "score": 数値,
                    "expertise_areas": ["専門領域1", "専門領域2"],
                    "can_mentor_others": true/false,
                    "application_opportunities": ["活用機会1", "活用機会2"]
                }}
            ],
            "learning_patterns": {{
                "optimal_study_time": "推奨学習時間帯",
                "effective_session_duration": 数値（分）,
                "preferred_difficulty": "beginner/intermediate/advanced",
                "effective_question_types": ["効果的な問題タイプ"],
                "learning_velocity": "fast/normal/slow",
                "retention_characteristics": "理解度保持の特徴",
                "motivation_patterns": "モチベーションパターン"
            }},
            "improvement_strategies": [
                {{
                    "strategy": "戦略名",
                    "target_skills": ["対象スキル"],
                    "implementation_steps": ["ステップ1", "ステップ2"],
                    "timeline": "期間",
                    "success_metrics": ["成功指標"]
                }}
            ],
            "confidence_score": 0.0-1.0の数値,
            "analysis_reliability": {{
                "data_sufficiency": true/false,
                "pattern_consistency": true/false,
                "recommendation_confidence": 0.0-1.0
            }}
        }}
        """
        
        return prompt
    
    def validate_analysis_result(self, result: Dict) -> Dict:
        """分析結果の検証と品質保証"""
        
        # 必須フィールドの検証
        required_fields = ["weak_points", "strong_points", "learning_patterns", "confidence_score"]
        for field in required_fields:
            if field not in result:
                result[field] = []
        
        # 信頼度スコアの検証
        confidence = result.get("confidence_score", 0.0)
        if not 0.0 <= confidence <= 1.0:
            result["confidence_score"] = 0.5
        
        # 弱点データの検証と補完
        validated_weak_points = []
        for weak_point in result.get("weak_points", []):
            if "topic" in weak_point and "severity" in weak_point:
                # デフォルト値の設定
                weak_point.setdefault("improvement_priority", 5)
                weak_point.setdefault("estimated_improvement_time", "要評価")
                weak_point.setdefault("specific_actions", [])
                validated_weak_points.append(weak_point)
        
        result["weak_points"] = validated_weak_points
        
        # 検証メタデータの追加
        result["validation_info"] = {
            "validated_at": datetime.utcnow().isoformat(),
            "validation_version": "1.0",
            "data_quality_score": self.calculate_data_quality_score(result)
        }
        
        return result
    
    def calculate_data_quality_score(self, result: Dict) -> float:
        """データ品質スコアの計算"""
        
        score = 0.0
        max_score = 10.0
        
        # 弱点データの品質
        weak_points = result.get("weak_points", [])
        if weak_points:
            score += 3.0
            if all("evidence" in wp for wp in weak_points):
                score += 1.0
            if all("specific_actions" in wp for wp in weak_points):
                score += 1.0
        
        # 強みデータの品質
        strong_points = result.get("strong_points", [])
        if strong_points:
            score += 2.0
        
        # 学習パターンの品質
        learning_patterns = result.get("learning_patterns", {})
        if learning_patterns:
            score += 2.0
        
        # 信頼度スコア
        confidence = result.get("confidence_score", 0.0)
        if confidence >= 0.7:
            score += 1.0
        
        return min(score / max_score, 1.0)

    # その他のヘルパーメソッドの実装...
    # (build_user_profile, determine_rule_strategy, generate_personalized_rules など)

async def main():
    """メインエントリーポイント"""
    
    # ログの初期化
    logger.info("Starting asagami MCP Server")
    
    async with AsagamiMcpServer() as server:
        # ヘルスチェックエンドポイント
        @server.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        
        # MCPサーバーの起動
        host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_SERVER_PORT", 8001))
        
        logger.info("MCP Server starting", host=host, port=port)
        
        await server.serve(host=host, port=port)

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 5: サーバー起動スクリプト**
```bash
#!/bin/bash
# mcp_server/start_server.sh

# 仮想環境の作成（初回のみ）
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の確認
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create it with required configurations."
    exit 1
fi

# サーバーの起動
echo "Starting asagami MCP Server..."
python main.py
```

**Step 6: Django API実装（学習データ分析）**
```python
# cursor_integration/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import json
from datetime import datetime, timedelta
from .models import LearningAnalysis, CursorRuleProfile, PracticeLog
from app.models import Note, CustomUser  # 既存モデルのインポート

class LearningDataAPIView(APIView):
    """学習データ取得API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        """
        指定ユーザーの学習データを取得
        """
        try:
            # リクエストユーザーの権限チェック
            if request.user.id != user_id and not request.user.is_staff:
                return Response({'error': 'Permission denied'}, status=403)
            
            # パラメータの取得
            period_days = int(request.GET.get('period', 30))
            detail_level = request.GET.get('detail_level', 'comprehensive')
            include_team_context = request.GET.get('include_team_context', 'false').lower() == 'true'
            
            # ユーザーの存在確認
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
            
            # 学習データの収集期間を設定
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # ノートデータの取得
            notes = Note.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).order_by('-created_at')
            
            # 問題解答データの取得（既存のasagami AIデータから）
            question_results = self.get_question_results(user, start_date, end_date)
            
            # 科目別スコアの計算
            subject_scores = self.calculate_subject_scores(user, start_date, end_date)
            
            # エラーパターンの分析
            recent_errors = self.analyze_recent_errors(user, start_date, end_date)
            
            # 学習セッションパターンの分析
            session_patterns = self.analyze_session_patterns(user, start_date, end_date)
            
            # レスポンスデータの構築
            response_data = {
                'user_id': user_id,
                'analysis_period': period_days,
                'data_collection_date': datetime.now().isoformat(),
                'summary': {
                    'total_notes': notes.count(),
                    'total_questions': question_results.get('total_count', 0),
                    'average_score': question_results.get('average_score', 0),
                    'study_hours': self.calculate_study_hours(user, start_date, end_date),
                    'skill_level': self.determine_skill_level(user),
                    'learning_streak': self.calculate_learning_streak(user)
                },
                'subject_scores': subject_scores,
                'recent_errors': recent_errors,
                'session_patterns': session_patterns,
                'note_analytics': self.analyze_note_content(notes),
                'improvement_trends': self.calculate_improvement_trends(user, period_days)
            }
            
            # チーム比較データの追加
            if include_team_context and user.department_id:
                team_data = self.get_team_comparison_data(user, start_date, end_date)
                response_data['team_context'] = team_data
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'error': 'データ取得に失敗しました',
                'details': str(e)
            }, status=500)
    
    def get_question_results(self, user, start_date, end_date):
        """問題解答結果の取得と分析"""
        # 既存のasagami AIの問題解答データから取得
        # ここでは例として基本構造を示す
        return {
            'total_count': 150,
            'average_score': 78.5,
            'correct_answers': 118,
            'incorrect_answers': 32,
            'completion_rate': 0.89,
            'topics_covered': ['データベース', 'セキュリティ', 'API設計']
        }
    
    def calculate_subject_scores(self, user, start_date, end_date):
        """科目別スコアの計算"""
        # 既存のSubjectモデルとの連携
        return {
            'データベース設計': {'score': 65, 'question_count': 20, 'improvement': -5},
            'セキュリティ': {'score': 72, 'question_count': 15, 'improvement': +8},
            'API開発': {'score': 88, 'question_count': 25, 'improvement': +12},
            'フロントエンド': {'score': 81, 'question_count': 18, 'improvement': +3}
        }
    
    def analyze_recent_errors(self, user, start_date, end_date):
        """最近のエラーパターンの分析"""
        return [
            {
                'error_type': 'concept_misunderstanding',
                'topic': 'データベース正規化',
                'frequency': 8,
                'last_occurrence': '2025-07-10',
                'pattern': '第3正規形の理解が不十分'
            },
            {
                'error_type': 'implementation_error',
                'topic': 'SQL文法',
                'frequency': 5,
                'last_occurrence': '2025-07-12',
                'pattern': 'JOIN句の記述ミス'
            }
        ]
    
    def analyze_session_patterns(self, user, start_date, end_date):
        """学習セッションパターンの分析"""
        return {
            'preferred_time_slots': ['09:00-11:00', '14:00-16:00'],
            'average_session_duration': 45,  # 分
            'weekly_frequency': 4.2,
            'productivity_peaks': ['火曜日午前', '木曜日午後'],
            'attention_span': {
                'average': 35,  # 分
                'declining_after': 40
            }
        }

class CursorRulesGenerationAPIView(APIView):
    """Cursor Rules生成API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        学習分析結果からCursor Rulesを生成
        """
        try:
            data = json.loads(request.body)
            
            # 入力データの検証
            required_fields = ['user_id', 'analysis_data']
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'{field} is required'}, status=400)
            
            user_id = data['user_id']
            analysis_data = data['analysis_data']
            
            # 権限チェック
            if request.user.id != user_id and not request.user.is_staff:
                return Response({'error': 'Permission denied'}, status=403)
            
            # ルール生成設定の取得
            rule_config = data.get('rule_config', {})
            strictness_level = rule_config.get('strictness_level', 'intermediate')
            focus_areas = rule_config.get('focus_areas', [])
            include_templates = rule_config.get('include_templates', True)
            
            # MCP サーバーとの連携でルール生成
            mcp_client = self.get_mcp_client()
            rules_result = await mcp_client.generate_cursor_rules(
                analysis_data=json.dumps(analysis_data),
                strictness_level=strictness_level,
                focus_areas=','.join(focus_areas),
                customization_level='personalized'
            )
            
            rules_data = json.loads(rules_result)
            
            # データベースに保存
            cursor_profile = CursorRuleProfile.objects.create(
                user_id=user_id,
                rule_version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                rule_config=rules_data['cursor_rules'],
                code_templates=rules_data.get('code_templates', []),
                learning_resources=rules_data.get('learning_resources', []),
                strictness_level=strictness_level,
                focus_areas=focus_areas,
                auto_suggestions_enabled=rule_config.get('auto_suggestions', True)
            )
            
            response_data = {
                'rule_id': str(cursor_profile.id),
                'generated_at': cursor_profile.generated_at.isoformat(),
                'cursor_rules': rules_data,
                'deployment_instructions': self.generate_deployment_instructions(rules_data),
                'expected_impact': self.calculate_expected_impact(analysis_data),
                'monitoring_setup': self.generate_monitoring_setup(user_id)
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'error': 'ルール生成に失敗しました',
                'details': str(e)
            }, status=500)
    
    def generate_deployment_instructions(self, rules_data):
        """Cursorへのデプロイ手順を生成"""
        return {
            'step_1': {
                'action': 'Create .cursor directory',
                'command': 'mkdir -p .cursor',
                'description': 'プロジェクトルートに.cursorディレクトリを作成'
            },
            'step_2': {
                'action': 'Create rules.json',
                'command': 'Create .cursor/rules.json with generated rules',
                'content': rules_data['cursor_rules'],
                'description': '生成されたルールを.cursor/rules.jsonに保存'
            },
            'step_3': {
                'action': 'Restart Cursor',
                'command': 'Restart your Cursor IDE',
                'description': 'ルールを適用するためCursorを再起動'
            },
            'verification': {
                'action': 'Test rules',
                'description': 'サンプルコードでルールが適用されることを確認'
            }
        }

@csrf_exempt
@login_required
def practice_logs_api(request):
    """実践ログ収集API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # ログデータの検証と保存
            practice_log = PracticeLog.objects.create(
                user=request.user,
                session_id=data['session_id'],
                start_time=datetime.fromisoformat(data['session_metadata']['start_time'].replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(data['session_metadata']['end_time'].replace('Z', '+00:00')),
                project_name=data['session_metadata'].get('project_name', ''),
                project_type=data['session_metadata'].get('project_type', ''),
                development_environment=data['session_metadata'].get('development_environment', ''),
                cursor_version=data['session_metadata'].get('cursor_version', ''),
                files_modified=data['development_activity'].get('files_modified', []),
                lines_added=sum(f.get('lines_added', 0) for f in data['development_activity'].get('files_modified', [])),
                lines_deleted=sum(f.get('lines_deleted', 0) for f in data['development_activity'].get('files_modified', [])),
                commits_made=len(data['development_activity'].get('commits', [])),
                error_events=data.get('error_events', []),
                completion_events=data.get('completion_events', []),
                rule_interactions=data.get('rule_interactions', []),
                code_completion_usage=data['productivity_metrics'].get('code_completion_usage', 0),
                auto_fix_acceptance_rate=data['productivity_metrics'].get('auto_fix_acceptance_rate', 0.0),
                average_error_resolution_time=data['productivity_metrics'].get('average_time_to_resolve_error', 0),
                focus_time_percentage=data['productivity_metrics'].get('focus_time_percentage', 0.0),
                context_switch_count=data['productivity_metrics'].get('context_switch_count', 0)
            )
            
            # 非同期でフィードバック分析をスケジュール
            from .tasks import analyze_practice_feedback
            analyze_practice_feedback.delay(practice_log.id)
            
            return JsonResponse({
                'status': 'success',
                'log_id': str(practice_log.id),
                'processing_scheduled': True,
                'next_analysis_eta': (datetime.now() + timedelta(minutes=5)).isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

**Step 7: Celeryタスクの実装**
```python
# cursor_integration/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import PracticeLog, FeedbackAnalysis, LearningAnalysis
import json
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def analyze_practice_feedback(self, practice_log_id):
    """
    実践ログのフィードバック分析タスク
    """
    try:
        practice_log = PracticeLog.objects.get(id=practice_log_id)
        
        logger.info(f"Starting feedback analysis for log {practice_log_id}")
        
        # エラーパターンの分析
        error_analysis = analyze_error_patterns(practice_log.error_events)
        
        # ルール効果の測定
        rule_effectiveness = measure_rule_effectiveness(practice_log.rule_interactions)
        
        # スキルギャップの検出
        skill_gaps = detect_skill_gaps_from_errors(practice_log.error_events)
        
        # フィードバック分析レコードの作成
        feedback_analysis = FeedbackAnalysis.objects.create(
            user=practice_log.user,
            analysis_period_days=7,
            error_pattern_analysis=error_analysis,
            rule_effectiveness_metrics=rule_effectiveness,
            new_weak_points=skill_gaps,
            confidence_score=calculate_analysis_confidence(error_analysis, rule_effectiveness),
            processed_log_count=1
        )
        
        feedback_analysis.practice_logs.add(practice_log)
        
        # 新しい学習コンテンツの提案があれば通知
        if skill_gaps:
            generate_learning_content_suggestions.delay(practice_log.user.id, skill_gaps)
        
        logger.info(f"Feedback analysis completed for log {practice_log_id}")
        
        return {
            'analysis_id': str(feedback_analysis.id),
            'new_weak_points_count': len(skill_gaps),
            'rule_effectiveness_score': rule_effectiveness.get('overall_score', 0)
        }
        
    except PracticeLog.DoesNotExist:
        logger.error(f"Practice log {practice_log_id} not found")
        raise
    except Exception as e:
        logger.error(f"Feedback analysis failed for log {practice_log_id}: {str(e)}")
        raise

@shared_task
def generate_learning_content_suggestions(user_id, skill_gaps):
    """
    新しい学習コンテンツの提案生成
    """
    try:
        # asagami AIの既存システムとの連携
        # 新しい問題やノートの生成提案
        pass
    except Exception as e:
        logger.error(f"Learning content suggestion failed for user {user_id}: {str(e)}")

def analyze_error_patterns(error_events):
    """エラーパターンの分析"""
    patterns = {}
    
    for error in error_events:
        category = error.get('error_category', 'unknown')
        if category not in patterns:
            patterns[category] = {
                'frequency': 0,
                'avg_resolution_time': 0,
                'common_triggers': []
            }
        
        patterns[category]['frequency'] += 1
        patterns[category]['avg_resolution_time'] += error.get('resolution_time_seconds', 0)
    
    # 平均値の計算
    for category, data in patterns.items():
        if data['frequency'] > 0:
            data['avg_resolution_time'] /= data['frequency']
    
    return patterns

def measure_rule_effectiveness(rule_interactions):
    """ルール効果の測定"""
    if not rule_interactions:
        return {'overall_score': 0, 'interactions': 0}
    
    total_interactions = len(rule_interactions)
    accepted_count = sum(1 for r in rule_interactions if r.get('user_action') == 'accepted')
    avg_effectiveness = sum(r.get('effectiveness_rating', 0) for r in rule_interactions) / total_interactions
    
    return {
        'overall_score': avg_effectiveness,
        'interactions': total_interactions,
        'acceptance_rate': accepted_count / total_interactions if total_interactions > 0 else 0,
        'most_effective_rules': get_most_effective_rules(rule_interactions)
    }

def get_most_effective_rules(rule_interactions):
    """最も効果的なルールの特定"""
    rule_scores = {}
    
    for interaction in rule_interactions:
        rule_id = interaction.get('rule_id')
        if rule_id:
            if rule_id not in rule_scores:
                rule_scores[rule_id] = []
            rule_scores[rule_id].append(interaction.get('effectiveness_rating', 0))
    
    # 平均スコアの計算と上位3つを返す
    avg_scores = {rule_id: sum(scores)/len(scores) for rule_id, scores in rule_scores.items()}
    return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:3]
```

**Step 8: URLパターンの設定**
```python
# cursor_integration/urls.py
from django.urls import path
from . import views

app_name = 'cursor_integration'

urlpatterns = [
    # 学習データ分析API
    path('learning-data/<int:user_id>/', views.LearningDataAPIView.as_view(), name='learning_data'),
    
    # Cursor Rules生成API
    path('generate-rules/', views.CursorRulesGenerationAPIView.as_view(), name='generate_rules'),
    
    # 実践ログ収集API
    path('practice-logs/', views.practice_logs_api, name='practice_logs'),
    
    # フィードバック分析API
    path('feedback-analysis/<int:user_id>/', views.FeedbackAnalysisAPIView.as_view(), name='feedback_analysis'),
    
    # 統計・レポートAPI
    path('analytics/improvement-report/<int:user_id>/', views.ImprovementReportAPIView.as_view(), name='improvement_report'),
    path('analytics/team-stats/<int:department_id>/', views.TeamStatsAPIView.as_view(), name='team_stats'),
    
    # ルール管理API
    path('rules/<uuid:rule_id>/', views.RuleManagementAPIView.as_view(), name='rule_management'),
    path('rules/<uuid:rule_id>/effectiveness/', views.RuleEffectivenessAPIView.as_view(), name='rule_effectiveness'),
]
```

**Step 9: メインプロジェクトURLの更新**
```python
# mysite/urls.py に追加
path('api/cursor-integration/', include('cursor_integration.urls')),
```

### Phase 2: AI分析エンジン強化 (3週間)
**目標**: 高精度な学習分析とパーソナライズされたルール生成

#### Week 5-6: 分析精度向上

**Step 1: 機械学習モデルの実装**
```python
# mcp_server/ml_models.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import json

class WeakPointDetector:
    """機械学習による弱点検出モデル"""
    
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, learning_data):
        """学習データから特徴量を準備"""
        features = []
        
        # 基本統計特徴量
        summary = learning_data.get('summary', {})
        features.extend([
            summary.get('study_hours', 0),
            summary.get('total_questions', 0),
            summary.get('average_score', 0),
            summary.get('learning_streak', 0)
        ])
        
        # 科目別スコア特徴量
        subject_scores = learning_data.get('subject_scores', {})
        for subject, data in subject_scores.items():
            features.extend([
                data.get('score', 0),
                data.get('question_count', 0),
                data.get('improvement', 0)
            ])
        
        # セッションパターン特徴量
        session_patterns = learning_data.get('session_patterns', {})
        features.extend([
            session_patterns.get('average_session_duration', 0),
            session_patterns.get('weekly_frequency', 0),
            session_patterns.get('attention_span', {}).get('average', 0)
        ])
        
        # エラーパターン特徴量
        recent_errors = learning_data.get('recent_errors', [])
        error_features = self.extract_error_features(recent_errors)
        features.extend(error_features)
        
        return np.array(features).reshape(1, -1)
    
    def extract_error_features(self, errors):
        """エラーデータから特徴量を抽出"""
        if not errors:
            return [0] * 10  # デフォルト特徴量
        
        # エラー頻度、タイプ別集計など
        total_errors = len(errors)
        concept_errors = sum(1 for e in errors if e.get('error_type') == 'concept_misunderstanding')
        implementation_errors = sum(1 for e in errors if e.get('error_type') == 'implementation_error')
        
        avg_frequency = sum(e.get('frequency', 0) for e in errors) / total_errors
        
        return [
            total_errors,
            concept_errors,
            implementation_errors,
            avg_frequency,
            concept_errors / total_errors if total_errors > 0 else 0,
            implementation_errors / total_errors if total_errors > 0 else 0,
            0, 0, 0, 0  # 追加特徴量用
        ]
    
    def predict_weak_points(self, learning_data):
        """弱点を予測"""
        if not self.is_trained:
            # 初期モデルまたはプリトレーニングモデルを使用
            return self.fallback_weak_point_detection(learning_data)
        
        features = self.prepare_features(learning_data)
        features_scaled = self.scaler.transform(features)
        
        # 弱点の予測
        weak_point_probs = self.classifier.predict_proba(features_scaled)
        
        return self.format_predictions(weak_point_probs)
    
    def fallback_weak_point_detection(self, learning_data):
        """ルールベースのフォールバック弱点検出"""
        weak_points = []
        
        # スコアベースの弱点検出
        subject_scores = learning_data.get('subject_scores', {})
        for subject, data in subject_scores.items():
            score = data.get('score', 0)
            if score < 70:  # 閾値
                severity = 'high' if score < 50 else 'medium'
                weak_points.append({
                    'topic': subject,
                    'severity': severity,
                    'current_score': score,
                    'improvement_priority': 10 - (score // 10),
                    'detection_method': 'score_based'
                })
        
        # エラーパターンベースの検出
        recent_errors = learning_data.get('recent_errors', [])
        for error in recent_errors:
            if error.get('frequency', 0) >= 5:
                weak_points.append({
                    'topic': error.get('topic', 'Unknown'),
                    'severity': 'high',
                    'error_frequency': error.get('frequency'),
                    'improvement_priority': 8,
                    'detection_method': 'error_pattern_based'
                })
        
        return weak_points

class LearningEffectivenessPredictor:
    """学習効果予測モデル"""
    
    def __init__(self):
        self.regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
    
    def predict_learning_outcome(self, user_profile, study_plan):
        """学習計画の効果を予測"""
        # 特徴量の準備
        features = self.prepare_prediction_features(user_profile, study_plan)
        
        # 予測実行
        predicted_improvement = self.regressor.predict(features)
        
        return {
            'expected_score_improvement': float(predicted_improvement[0]),
            'confidence_interval': self.calculate_confidence_interval(features),
            'timeline_estimate': self.estimate_timeline(user_profile, predicted_improvement[0]),
            'success_probability': self.calculate_success_probability(features)
        }

class UserClusteringEngine:
    """ユーザークラスタリングエンジン"""
    
    def __init__(self):
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
    
    def cluster_users(self, users_data):
        """ユーザーをスキルパターンでクラスタリング"""
        features_matrix = []
        
        for user_data in users_data:
            features = self.extract_user_features(user_data)
            features_matrix.append(features)
        
        features_scaled = self.scaler.fit_transform(features_matrix)
        clusters = self.kmeans.fit_predict(features_scaled)
        
        return {
            'cluster_assignments': clusters.tolist(),
            'cluster_centers': self.kmeans.cluster_centers_.tolist(),
            'cluster_characteristics': self.analyze_clusters(features_scaled, clusters)
        }

# 使用例
def enhanced_analysis_with_ml(learning_data):
    """機械学習を使用した高度な分析"""
    
    # 弱点検出
    detector = WeakPointDetector()
    ml_weak_points = detector.predict_weak_points(learning_data)
    
    # 学習効果予測
    predictor = LearningEffectivenessPredictor()
    # effectiveness_prediction = predictor.predict_learning_outcome(user_profile, study_plan)
    
    return {
        'ml_weak_points': ml_weak_points,
        'confidence_score': 0.85,  # ML モデルの信頼度
        'analysis_method': 'machine_learning_enhanced'
    }
```

**Step 2: A/Bテストフレームワーク**
```python
# mcp_server/ab_testing.py
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ABTestFramework:
    """A/Bテスト実行フレームワーク"""
    
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
    
    def create_test(self, test_config: Dict) -> str:
        """
        新しいA/Bテストを作成
        
        Args:
            test_config: テスト設定
            {
                'name': 'rule_strictness_test',
                'description': 'ルール厳格度の効果測定',
                'variants': [
                    {'name': 'lenient', 'config': {'strictness': 'lenient'}},
                    {'name': 'strict', 'config': {'strictness': 'strict'}}
                ],
                'traffic_allocation': [0.5, 0.5],
                'duration_days': 14,
                'success_metrics': ['error_reduction', 'user_satisfaction'],
                'minimum_sample_size': 100
            }
        
        Returns:
            test_id: テストID
        """
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_tests[test_id] = {
            **test_config,
            'test_id': test_id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=test_config['duration_days']),
            'participants': {},
            'status': 'active'
        }
        
        return test_id
    
    def assign_user_to_variant(self, test_id: str, user_id: int) -> Optional[Dict]:
        """ユーザーをテストバリアントに割り当て"""
        
        if test_id not in self.active_tests:
            return None
        
        test = self.active_tests[test_id]
        
        # 既に割り当て済みの場合は既存のバリアントを返す
        if user_id in test['participants']:
            return test['participants'][user_id]
        
        # ランダム割り当て
        variants = test['variants']
        allocation = test['traffic_allocation']
        
        random_value = random.random()
        cumulative_prob = 0
        
        for i, prob in enumerate(allocation):
            cumulative_prob += prob
            if random_value <= cumulative_prob:
                selected_variant = variants[i]
                break
        else:
            selected_variant = variants[-1]  # フォールバック
        
        # 参加者情報を記録
        participant_info = {
            'variant': selected_variant,
            'assigned_at': datetime.now(),
            'user_id': user_id
        }
        
        test['participants'][user_id] = participant_info
        
        return participant_info
    
    def record_metric(self, test_id: str, user_id: int, metric_name: str, value: float):
        """メトリクス値を記録"""
        
        if test_id not in self.active_tests:
            return False
        
        test = self.active_tests[test_id]
        
        if user_id not in test['participants']:
            return False
        
        participant = test['participants'][user_id]
        
        if 'metrics' not in participant:
            participant['metrics'] = {}
        
        if metric_name not in participant['metrics']:
            participant['metrics'][metric_name] = []
        
        participant['metrics'][metric_name].append({
            'value': value,
            'timestamp': datetime.now()
        })
        
        return True
    
    def analyze_test_results(self, test_id: str) -> Dict:
        """テスト結果の統計分析"""
        
        if test_id not in self.active_tests:
            return {'error': 'Test not found'}
        
        test = self.active_tests[test_id]
        participants = test['participants']
        
        # バリアント別の結果集計
        variant_results = {}
        
        for user_id, participant in participants.items():
            variant_name = participant['variant']['name']
            
            if variant_name not in variant_results:
                variant_results[variant_name] = {
                    'participants': 0,
                    'metrics': {}
                }
            
            variant_results[variant_name]['participants'] += 1
            
            # メトリクスの集計
            for metric_name, values in participant.get('metrics', {}).items():
                if metric_name not in variant_results[variant_name]['metrics']:
                    variant_results[variant_name]['metrics'][metric_name] = []
                
                # 最新値を使用
                if values:
                    latest_value = values[-1]['value']
                    variant_results[variant_name]['metrics'][metric_name].append(latest_value)
        
        # 統計的有意性の検定
        statistical_results = self.perform_statistical_tests(variant_results)
        
        return {
            'test_id': test_id,
            'test_name': test['name'],
            'status': test['status'],
            'duration': (datetime.now() - test['start_date']).days,
            'variant_results': variant_results,
            'statistical_analysis': statistical_results,
            'recommendations': self.generate_recommendations(variant_results, statistical_results)
        }
    
    def perform_statistical_tests(self, variant_results: Dict) -> Dict:
        """統計的有意性の検定"""
        # 簡易版の実装（本格的にはscipy.statsを使用）
        
        results = {}
        variants = list(variant_results.keys())
        
        if len(variants) != 2:
            return {'error': 'Only supports two-variant tests currently'}
        
        variant_a, variant_b = variants
        
        for metric_name in variant_results[variant_a].get('metrics', {}):
            if metric_name in variant_results[variant_b].get('metrics', {}):
                
                values_a = variant_results[variant_a]['metrics'][metric_name]
                values_b = variant_results[variant_b]['metrics'][metric_name]
                
                if len(values_a) >= 10 and len(values_b) >= 10:  # 最小サンプルサイズ
                    
                    mean_a = sum(values_a) / len(values_a)
                    mean_b = sum(values_b) / len(values_b)
                    
                    improvement = ((mean_b - mean_a) / mean_a * 100) if mean_a != 0 else 0
                    
                    results[metric_name] = {
                        'variant_a_mean': mean_a,
                        'variant_b_mean': mean_b,
                        'improvement_percentage': improvement,
                        'sample_size_a': len(values_a),
                        'sample_size_b': len(values_b),
                        'statistical_significance': abs(improvement) > 5  # 簡易判定
                    }
        
        return results

# A/Bテストの使用例
def setup_rule_effectiveness_test():
    """ルール効果のA/Bテスト設定"""
    
    ab_framework = ABTestFramework()
    
    test_config = {
        'name': 'cursor_rule_strictness_test',
        'description': 'Cursor Rulesの厳格度による効果の違いを測定',
        'variants': [
            {
                'name': 'lenient_rules',
                'config': {
                    'strictness_level': 'lenient',
                    'auto_suggestions': True,
                    'notification_level': 'low'
                }
            },
            {
                'name': 'strict_rules',
                'config': {
                    'strictness_level': 'strict',
                    'auto_suggestions': True,
                    'notification_level': 'high'
                }
            }
        ],
        'traffic_allocation': [0.5, 0.5],
        'duration_days': 21,
        'success_metrics': [
            'error_reduction_rate',
            'code_quality_score',
            'user_satisfaction',
            'learning_velocity'
        ],
        'minimum_sample_size': 50
    }
    
    test_id = ab_framework.create_test(test_config)
    return test_id, ab_framework
```

#### Week 7: ルール生成の高度化

**Step 1: 動的ルール調整機能**
```python
# mcp_server/dynamic_rules.py
from typing import Dict, List
import json
from datetime import datetime, timedelta

class DynamicRuleAdjuster:
    """動的ルール調整エンジン"""
    
    def __init__(self):
        self.adjustment_strategies = {
            'performance_based': self.performance_based_adjustment,
            'error_pattern_based': self.error_pattern_adjustment,
            'user_feedback_based': self.feedback_based_adjustment,
            'learning_progress_based': self.progress_based_adjustment
        }
    
    def adjust_rules(self, user_id: int, current_rules: Dict, 
                    performance_data: Dict, adjustment_strategy: str = 'performance_based') -> Dict:
        """
        パフォーマンスデータに基づいてルールを動的調整
        
        Args:
            user_id: ユーザーID
            current_rules: 現在のルール設定
            performance_data: パフォーマンスデータ
            adjustment_strategy: 調整戦略
        
        Returns:
            調整されたルール設定
        """
        
        if adjustment_strategy in self.adjustment_strategies:
            adjuster = self.adjustment_strategies[adjustment_strategy]
            adjusted_rules = adjuster(current_rules, performance_data)
        else:
            adjusted_rules = current_rules
        
        # 調整履歴の記録
        adjustment_log = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'strategy': adjustment_strategy,
            'original_rules': current_rules,
            'adjusted_rules': adjusted_rules,
            'performance_trigger': performance_data
        }
        
        self.log_adjustment(adjustment_log)
        
        return adjusted_rules
    
    def performance_based_adjustment(self, rules: Dict, performance_data: Dict) -> Dict:
        """パフォーマンスベースの調整"""
        
        adjusted_rules = rules.copy()
        
        # エラー率が高い場合はルールを厳格化
        error_rate = performance_data.get('error_rate', 0)
        if error_rate > 0.3:  # 30%以上のエラー率
            adjusted_rules = self.increase_rule_strictness(adjusted_rules)
        
        # エラー率が低い場合は段階的に緩和
        elif error_rate < 0.1:  # 10%未満のエラー率
            adjusted_rules = self.decrease_rule_strictness(adjusted_rules)
        
        # 特定のエラータイプが多い場合の特別対応
        frequent_errors = performance_data.get('frequent_error_types', [])
        for error_type in frequent_errors:
            adjusted_rules = self.strengthen_rules_for_error_type(adjusted_rules, error_type)
        
        return adjusted_rules
    
    def error_pattern_adjustment(self, rules: Dict, performance_data: Dict) -> Dict:
        """エラーパターンベースの調整"""
        
        adjusted_rules = rules.copy()
        error_patterns = performance_data.get('error_patterns', {})
        
        for pattern, frequency in error_patterns.items():
            if frequency > 5:  # 頻繁に発生するパターン
                # 該当するルールを強化
                adjusted_rules = self.add_specific_rule_for_pattern(adjusted_rules, pattern)
        
        return adjusted_rules
    
    def feedback_based_adjustment(self, rules: Dict, performance_data: Dict) -> Dict:
        """ユーザーフィードバックベースの調整"""
        
        adjusted_rules = rules.copy()
        user_feedback = performance_data.get('user_feedback', {})
        
        # 満足度が低いルールを調整
        low_satisfaction_rules = user_feedback.get('low_satisfaction_rules', [])
        for rule_id in low_satisfaction_rules:
            adjusted_rules = self.adjust_specific_rule(adjusted_rules, rule_id, 'reduce_severity')
        
        # 高評価のルールを維持・強化
        high_satisfaction_rules = user_feedback.get('high_satisfaction_rules', [])
        for rule_id in high_satisfaction_rules:
            adjusted_rules = self.adjust_specific_rule(adjusted_rules, rule_id, 'maintain_or_enhance')
        
        return adjusted_rules
    
    def increase_rule_strictness(self, rules: Dict) -> Dict:
        """ルールの厳格度を上げる"""
        
        adjusted = rules.copy()
        
        for category, category_rules in adjusted.items():
            if isinstance(category_rules, dict):
                for rule_name, rule_config in category_rules.items():
                    if isinstance(rule_config, dict):
                        # severity を上げる
                        if rule_config.get('severity') == 'warning':
                            rule_config['severity'] = 'error'
                        elif rule_config.get('severity') == 'info':
                            rule_config['severity'] = 'warning'
                        
                        # auto_fix を有効化
                        rule_config['auto_fix'] = True
        
        return adjusted
    
    def add_specific_rule_for_pattern(self, rules: Dict, error_pattern: str) -> Dict:
        """特定のエラーパターンに対するルールを追加"""
        
        adjusted = rules.copy()
        
        # エラーパターンに応じたルール生成
        pattern_rules = {
            'sql_injection': {
                'enabled': True,
                'severity': 'error',
                'message': 'SQLインジェクション対策: プリペアドステートメントを使用してください',
                'auto_fix': True,
                'trigger_patterns': ['SELECT.*\\+', 'INSERT.*\\+', 'UPDATE.*\\+']
            },
            'xss_vulnerability': {
                'enabled': True,
                'severity': 'error',
                'message': 'XSS対策: 入力値をエスケープしてください',
                'auto_fix': True,
                'trigger_patterns': ['innerHTML.*\\+', 'document.write']
            },
            'memory_leak': {
                'enabled': True,
                'severity': 'warning',
                'message': 'メモリリーク対策: リソースの適切な解放を確認してください',
                'auto_fix': False,
                'trigger_patterns': ['addEventListener', 'setInterval']
            }
        }
        
        if error_pattern in pattern_rules:
            if 'security' not in adjusted:
                adjusted['security'] = {}
            
            adjusted['security'][error_pattern] = pattern_rules[error_pattern]
        
        return adjusted

class ContextAwareRuleGenerator:
    """コンテキスト依存ルール生成器"""
    
    def __init__(self):
        self.context_templates = self.load_context_templates()
    
    def generate_context_rules(self, user_profile: Dict, project_context: Dict) -> Dict:
        """
        プロジェクトコンテキストに応じたルール生成
        
        Args:
            user_profile: ユーザープロファイル
            project_context: プロジェクトコンテキスト
            {
                'project_type': 'web_application',
                'frameworks': ['django', 'react'],
                'languages': ['python', 'javascript'],
                'team_size': 5,
                'compliance_requirements': ['GDPR', 'PCI_DSS'],
                'performance_requirements': 'high',
                'security_level': 'enterprise'
            }
        
        Returns:
            コンテキスト特化ルール
        """
        
        context_rules = {}
        
        # プロジェクトタイプ特化ルール
        project_type = project_context.get('project_type')
        if project_type in self.context_templates:
            context_rules.update(self.context_templates[project_type])
        
        # フレームワーク特化ルール
        frameworks = project_context.get('frameworks', [])
        for framework in frameworks:
            if framework in self.context_templates.get('frameworks', {}):
                framework_rules = self.context_templates['frameworks'][framework]
                context_rules = self.merge_rules(context_rules, framework_rules)
        
        # コンプライアンス要件ルール
        compliance_reqs = project_context.get('compliance_requirements', [])
        for req in compliance_reqs:
            if req in self.context_templates.get('compliance', {}):
                compliance_rules = self.context_templates['compliance'][req]
                context_rules = self.merge_rules(context_rules, compliance_rules)
        
        # パフォーマンス要件ルール
        perf_req = project_context.get('performance_requirements')
        if perf_req == 'high':
            perf_rules = self.context_templates.get('performance', {}).get('high', {})
            context_rules = self.merge_rules(context_rules, perf_rules)
        
        # ユーザーのスキルレベルに応じた調整
        skill_level = user_profile.get('skill_level', 'intermediate')
        context_rules = self.adjust_for_skill_level(context_rules, skill_level)
        
        return context_rules
    
    def load_context_templates(self) -> Dict:
        """コンテキストテンプレートを読み込み"""
        
        return {
            'web_application': {
                'security': {
                    'csrf_protection': {
                        'enabled': True,
                        'severity': 'error',
                        'message': 'CSRF保護を実装してください'
                    },
                    'https_enforcement': {
                        'enabled': True,
                        'severity': 'warning',
                        'message': 'HTTPS通信を使用してください'
                    }
                },
                'performance': {
                    'image_optimization': {
                        'enabled': True,
                        'severity': 'info',
                        'message': '画像の最適化を検討してください'
                    }
                }
            },
            'frameworks': {
                'django': {
                    'django_security': {
                        'sql_injection_protection': {
                            'enabled': True,
                            'severity': 'error',
                            'message': 'Django ORMを使用してSQLインジェクションを防いでください'
                        },
                        'template_escaping': {
                            'enabled': True,
                            'severity': 'error',
                            'message': 'テンプレートでの自動エスケープを確認してください'
                        }
                    }
                },
                'react': {
                    'react_security': {
                        'jsx_xss_prevention': {
                            'enabled': True,
                            'severity': 'error',
                            'message': 'dangerouslySetInnerHTMLの使用は避けてください'
                        }
                    },
                    'react_performance': {
                        'unnecessary_renders': {
                            'enabled': True,
                            'severity': 'warning',
                            'message': '不要な再レンダリングを避けるためメモ化を検討してください'
                        }
                    }
                }
            },
            'compliance': {
                'GDPR': {
                    'data_protection': {
                        'consent_management': {
                            'enabled': True,
                            'severity': 'error',
                            'message': 'GDPR準拠: ユーザー同意の管理を実装してください'
                        },
                        'data_minimization': {
                            'enabled': True,
                            'severity': 'warning',
                            'message': 'GDPR準拠: 必要最小限のデータ収集を心がけてください'
                        }
                    }
                },
                'PCI_DSS': {
                    'payment_security': {
                        'card_data_encryption': {
                            'enabled': True,
                            'severity': 'error',
                            'message': 'PCI DSS準拠: カード情報の暗号化が必要です'
                        }
                    }
                }
            },
            'performance': {
                'high': {
                    'optimization': {
                        'database_queries': {
                            'enabled': True,
                            'severity': 'warning',
                            'message': 'N+1クエリ問題に注意してください'
                        },
                        'caching_strategy': {
                            'enabled': True,
                            'severity': 'info',
                            'message': 'キャッシュ戦略を検討してください'
                        }
                    }
                }
            }
        }
```

### Phase 3: フィードバックループ完成 (3週間)
**目標**: 継続的改善サイクルの自動化

#### Week 8-9: 実践ログ統合

**Step 1: Cursor側ログ収集スクリプト**
```typescript
// cursor_log_collector.ts - Cursorエクステンション内で実行
import * as vscode from 'vscode';
import axios from 'axios';

interface CursorLogData {
    session_id: string;
    user_id: number;
    session_metadata: SessionMetadata;
    development_activity: DevelopmentActivity;
    error_events: ErrorEvent[];
    completion_events: CompletionEvent[];
    rule_interactions: RuleInteraction[];
    productivity_metrics: ProductivityMetrics;
}

class CursorLogCollector {
    private sessionId: string;
    private userId: number;
    private sessionStartTime: Date;
    private errorEvents: ErrorEvent[] = [];
    private completionEvents: CompletionEvent[] = [];
    private ruleInteractions: RuleInteraction[] = [];
    private filesModified: Set<string> = new Set();
    private linesAdded: number = 0;
    private linesDeleted: number = 0;
    private codeCompletionUsage: number = 0;
    private contextSwitchCount: number = 0;
    
    constructor(userId: number) {
        this.userId = userId;
        this.sessionId = `cursor_${Date.now()}_${userId}`;
        this.sessionStartTime = new Date();
        this.setupEventListeners();
    }
    
    private setupEventListeners() {
        // エラーイベントの監視
        vscode.languages.onDidChangeDiagnostics((e) => {
            this.handleDiagnosticsChange(e);
        });
        
        // ファイル編集の監視
        vscode.workspace.onDidChangeTextDocument((e) => {
            this.handleTextDocumentChange(e);
        });
        
        // コード補完の監視
        vscode.languages.registerCompletionItemProvider('*', {
            provideCompletionItems: (document, position) => {
                this.recordCompletionUsage();
                return [];
            }
        });
        
        // Cursor Rules発火の監視
        this.setupRuleInteractionListeners();
    }
    
    private handleDiagnosticsChange(e: vscode.DiagnosticChangeEvent) {
        e.uris.forEach(uri => {
            const diagnostics = vscode.languages.getDiagnostics(uri);
            diagnostics.forEach(diagnostic => {
                if (diagnostic.severity === vscode.DiagnosticSeverity.Error) {
                    this.recordErrorEvent({
                        error_type: this.categorizeError(diagnostic.message),
                        error_category: this.getErrorCategory(diagnostic.source),
                        error_message: diagnostic.message,
                        file_path: uri.fsPath,
                        line_number: diagnostic.range.start.line + 1,
                        timestamp: new Date(),
                        resolution_time_seconds: 0, // 後で更新
                        resolution_method: 'unknown',
                        user_satisfaction: null,
                        learning_value: 'medium'
                    });
                }
            });
        });
    }
    
    private handleTextDocumentChange(e: vscode.TextDocumentChangeEvent) {
        this.filesModified.add(e.document.fileName);
        
        e.contentChanges.forEach(change => {
            const changedLines = change.text.split('\n').length - 1;
            const deletedLines = change.rangeLength > 0 ? 
                e.document.getText(change.range).split('\n').length - 1 : 0;
            
            this.linesAdded += Math.max(0, changedLines - deletedLines);
            this.linesDeleted += Math.max(0, deletedLines - changedLines);
        });
    }
    
    private recordErrorEvent(errorEvent: ErrorEvent) {
        this.errorEvents.push(errorEvent);
    }
    
    private recordCompletionUsage() {
        this.codeCompletionUsage++;
    }
    
    private recordRuleInteraction(ruleId: string, triggered: boolean, userAction: string) {
        this.ruleInteractions.push({
            rule_id: ruleId,
            triggered_at: new Date(),
            trigger_context: this.getCurrentContext(),
            user_action: userAction,
            effectiveness_rating: this.getUserEffectivenessRating(),
            user_feedback: null
        });
    }
    
    private categorizeError(message: string): string {
        // エラーメッセージからタイプを分類
        if (message.includes('TypeError')) return 'type_error';
        if (message.includes('SyntaxError')) return 'syntax_error';
        if (message.includes('ReferenceError')) return 'reference_error';
        if (message.includes('SecurityError')) return 'security_error';
        return 'unknown_error';
    }
    
    private getErrorCategory(source: string | undefined): string {
        // エラーソースからカテゴリを決定
        if (!source) return 'unknown';
        if (source.includes('typescript')) return 'language_server';
        if (source.includes('eslint')) return 'linting';
        if (source.includes('cursor')) return 'cursor_rules';
        return 'other';
    }
    
    private getCurrentContext(): string {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) return '';
        
        const position = activeEditor.selection.active;
        const line = activeEditor.document.lineAt(position.line);
        return line.text.trim();
    }
    
    private getUserEffectivenessRating(): number {
        // 簡易的な効果評価（実際にはユーザー入力を求める）
        return Math.floor(Math.random() * 5) + 1; // 1-5の範囲
    }
    
    public async endSession() {
        const sessionEndTime = new Date();
        const sessionDuration = sessionEndTime.getTime() - this.sessionStartTime.getTime();
        
        const logData: CursorLogData = {
            session_id: this.sessionId,
            user_id: this.userId,
            session_metadata: {
                start_time: this.sessionStartTime.toISOString(),
                end_time: sessionEndTime.toISOString(),
                project_name: this.getProjectName(),
                project_type: this.detectProjectType(),
                development_environment: 'cursor',
                cursor_version: this.getCursorVersion()
            },
            development_activity: {
                files_modified: Array.from(this.filesModified).map(path => ({
                    file_path: path,
                    language: this.detectLanguage(path),
                    modification_type: 'unknown',
                    lines_added: 0, // ファイル別の詳細は省略
                    lines_deleted: 0
                })),
                commits: [], // Git統合で取得
                total_lines_added: this.linesAdded,
                total_lines_deleted: this.linesDeleted
            },
            error_events: this.errorEvents,
            completion_events: this.completionEvents,
            rule_interactions: this.ruleInteractions,
            productivity_metrics: {
                code_completion_usage: this.codeCompletionUsage,
                auto_fix_acceptance_rate: this.calculateAutoFixAcceptanceRate(),
                average_time_to_resolve_error: this.calculateAvgErrorResolutionTime(),
                focus_time_percentage: this.calculateFocusTime(sessionDuration),
                context_switch_count: this.contextSwitchCount
            }
        };
        
        // asagami AI APIにデータを送信
        await this.sendLogData(logData);
    }
    
    private async sendLogData(logData: CursorLogData) {
        try {
            const response = await axios.post(
                'http://localhost:8000/api/cursor-integration/practice-logs/',
                logData,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.getAuthToken()}`
                    }
                }
            );
            
            console.log('Log data sent successfully:', response.data);
        } catch (error) {
            console.error('Failed to send log data:', error);
            // ローカルストレージに保存してリトライ
            this.saveLogDataLocally(logData);
        }
    }
    
    private getAuthToken(): string {
        // ユーザーの認証トークンを取得
        return vscode.workspace.getConfiguration('asagami').get('authToken', '');
    }
    
    private saveLogDataLocally(logData: CursorLogData) {
        // 後でリトライするためのローカル保存
        const savedLogs = vscode.workspace.getConfiguration('asagami').get('pendingLogs', []);
        savedLogs.push(logData);
        vscode.workspace.getConfiguration('asagami').update('pendingLogs', savedLogs);
    }
}

// 使用例
export function activate(context: vscode.ExtensionContext) {
    const userId = getUserId(); // ユーザーIDを取得
    const logCollector = new CursorLogCollector(userId);
    
    // セッション終了時の処理
    vscode.window.onDidChangeWindowState((e) => {
        if (!e.focused) {
            logCollector.endSession();
        }
    });
}
```

**Step 2: リアルタイム分析エンジン**
```python
# mcp_server/realtime_analyzer.py
import asyncio
import json
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis
import logging

logger = logging.getLogger(__name__)

class RealtimeAnalysisEngine:
    """リアルタイム分析エンジン"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.analysis_tasks = {}
        self.active_sessions = {}
        
    async def start_session_monitoring(self, user_id: int, session_id: str):
        """セッション監視の開始"""
        
        session_key = f"session:{user_id}:{session_id}"
        self.active_sessions[session_key] = {
            'user_id': user_id,
            'session_id': session_id,
            'start_time': datetime.now(),
            'error_count': 0,
            'completion_count': 0,
            'rule_triggers': 0,
            'last_activity': datetime.now()
        }
        
        # リアルタイム分析タスクを開始
        task = asyncio.create_task(
            self.monitor_session(user_id, session_id)
        )
        self.analysis_tasks[session_key] = task
        
        logger.info(f"Started monitoring session {session_id} for user {user_id}")
    
    async def monitor_session(self, user_id: int, session_id: str):
        """セッションの継続監視"""
        
        session_key = f"session:{user_id}:{session_id}"
        
        while session_key in self.active_sessions:
            try:
                # セッションデータの更新チェック
                await self.check_session_updates(user_id, session_id)
                
                # 異常パターンの検出
                await self.detect_anomalies(user_id, session_id)
                
                # リアルタイム推奨の生成
                await self.generate_realtime_suggestions(user_id, session_id)
                
                # 5秒間隔で監視
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error monitoring session {session_id}: {e}")
                break
    
    async def process_realtime_event(self, event_data: Dict):
        """リアルタイムイベントの処理"""
        
        user_id = event_data.get('user_id')
        session_id = event_data.get('session_id')
        event_type = event_data.get('event_type')
        
        session_key = f"session:{user_id}:{session_id}"
        
        if session_key not in self.active_sessions:
            await self.start_session_monitoring(user_id, session_id)
        
        session = self.active_sessions[session_key]
        session['last_activity'] = datetime.now()
        
        # イベントタイプ別の処理
        if event_type == 'error_occurred':
            await self.handle_error_event(session, event_data)
        elif event_type == 'completion_used':
            await self.handle_completion_event(session, event_data)
        elif event_type == 'rule_triggered':
            await self.handle_rule_event(session, event_data)
        
        # セッションデータをRedisに保存
        await self.save_session_data(session_key, session)
    
    async def handle_error_event(self, session: Dict, event_data: Dict):
        """エラーイベントの処理"""
        
        session['error_count'] += 1
        error_category = event_data.get('error_category', 'unknown')
        
        # エラー頻度が高い場合のアラート
        if session['error_count'] > 10:
            await self.trigger_intervention_alert(
                session['user_id'],
                'high_error_frequency',
                f"短時間で{session['error_count']}個のエラーが発生しています"
            )
        
        # 特定のエラーパターンの検出
        if error_category == 'security_error':
            await self.trigger_security_alert(
                session['user_id'],
                event_data.get('error_message', '')
            )
    
    async def handle_completion_event(self, session: Dict, event_data: Dict):
        """コード補完イベントの処理"""
        
        session['completion_count'] += 1
        completion_type = event_data.get('completion_type', 'unknown')
        
        # 補完使用パターンの分析
        if completion_type == 'security_template':
            await self.record_positive_behavior(
                session['user_id'],
                'security_awareness',
                'セキュリティテンプレートの使用'
            )
    
    async def handle_rule_event(self, session: Dict, event_data: Dict):
        """ルール発火イベントの処理"""
        
        session['rule_triggers'] += 1
        rule_id = event_data.get('rule_id')
        user_action = event_data.get('user_action')
        
        # ルール効果の即座の評価
        if user_action == 'accepted':
            await self.record_rule_effectiveness(
                session['user_id'],
                rule_id,
                'positive'
            )
        elif user_action == 'dismissed':
            await self.record_rule_effectiveness(
                session['user_id'],
                rule_id,
                'negative'
            )
    
    async def detect_anomalies(self, user_id: int, session_id: str):
        """異常パターンの検出"""
        
        session_key = f"session:{user_id}:{session_id}"
        session = self.active_sessions.get(session_key)
        
        if not session:
            return
        
        current_time = datetime.now()
        session_duration = (current_time - session['start_time']).total_seconds() / 60
        
        # 長時間セッションの検出
        if session_duration > 120:  # 2時間以上
            await self.suggest_break(user_id, session_duration)
        
        # 高エラー率の検出
        if session_duration > 30:  # 30分以上のセッション
            error_rate = session['error_count'] / session_duration
            if error_rate > 0.5:  # 1分あたり0.5個以上のエラー
                await self.suggest_learning_content(
                    user_id,
                    'high_error_rate',
                    session['error_count']
                )
    
    async def generate_realtime_suggestions(self, user_id: int, session_id: str):
        """リアルタイム推奨の生成"""
        
        session_key = f"session:{user_id}:{session_id}"
        session = self.active_sessions.get(session_key)
        
        if not session:
            return
        
        # 最近のパフォーマンスデータを分析
        recent_data = await self.get_recent_performance_data(user_id)
        
        if recent_data:
            suggestions = await self.analyze_and_suggest(user_id, recent_data)
            
            if suggestions:
                await self.send_realtime_suggestions(user_id, suggestions)
    
    async def trigger_intervention_alert(self, user_id: int, alert_type: str, message: str):
        """介入アラートの発火"""
        
        alert_data = {
            'user_id': user_id,
            'alert_type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'suggested_actions': self.get_intervention_actions(alert_type)
        }
        
        # WebSocket経由でリアルタイム通知
        await self.send_websocket_notification(user_id, alert_data)
        
        # データベースにログ記録
        await self.log_intervention_alert(alert_data)
    
    def get_intervention_actions(self, alert_type: str) -> List[str]:
        """介入アクションの取得"""
        
        actions = {
            'high_error_frequency': [
                '5分間の休憩を取ることをお勧めします',
                '基本概念の復習をしてみてください',
                'より簡単な問題から始めることを検討してください'
            ],
            'long_session': [
                '休憩を取って集中力を回復してください',
                '明日続きを行うことを検討してください',
                '適度な運動で頭をリフレッシュしてください'
            ],
            'security_concern': [
                'セキュリティベストプラクティスを確認してください',
                'セキュリティ関連の学習コンテンツを推奨します',
                'コードレビューを依頼することを検討してください'
            ]
        }
        
        return actions.get(alert_type, ['専門家に相談することをお勧めします'])

class WebSocketManager:
    """WebSocket接続管理"""
    
    def __init__(self):
        self.connections = {}  # user_id -> websocket
    
    async def register_connection(self, user_id: int, websocket):
        """WebSocket接続の登録"""
        self.connections[user_id] = websocket
        logger.info(f"WebSocket registered for user {user_id}")
    
    async def unregister_connection(self, user_id: int):
        """WebSocket接続の削除"""
        if user_id in self.connections:
            del self.connections[user_id]
            logger.info(f"WebSocket unregistered for user {user_id}")
    
    async def send_notification(self, user_id: int, notification: Dict):
        """リアルタイム通知の送信"""
        
        if user_id in self.connections:
            websocket = self.connections[user_id]
            try:
                await websocket.send(json.dumps(notification))
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")
                await self.unregister_connection(user_id)

# WebSocketサーバーの起動
async def websocket_handler(websocket, path):
    """WebSocketハンドラー"""
    
    try:
        # 認証
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)
        user_id = auth_data.get('user_id')
        
        if not user_id:
            await websocket.close(code=4001, reason="Invalid authentication")
            return
        
        # 接続を登録
        ws_manager = WebSocketManager()
        await ws_manager.register_connection(user_id, websocket)
        
        # 接続維持
        async for message in websocket:
            # リアルタイムイベントの処理
            event_data = json.loads(message)
            await realtime_analyzer.process_realtime_event(event_data)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"WebSocket connection closed for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if 'user_id' in locals():
            await ws_manager.unregister_connection(user_id)

# リアルタイム分析エンジンのインスタンス
realtime_analyzer = RealtimeAnalysisEngine()

# WebSocketサーバーの起動
async def start_websocket_server():
    """WebSocketサーバーの起動"""
    
    logger.info("Starting WebSocket server on port 8765")
    await websockets.serve(websocket_handler, "localhost", 8765)
```

**Step 3: 自動ルール更新システム**
```python
# mcp_server/auto_rule_updater.py
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class AutomaticRuleUpdater:
    """自動ルール更新システム"""
    
    def __init__(self, update_threshold: float = 0.3):
        self.update_threshold = update_threshold  # 更新の閾値
        self.pending_updates = {}
        self.update_history = {}
    
    async def evaluate_rule_updates(self, user_id: int):
        """ルール更新の評価"""
        
        # 最近のパフォーマンスデータを取得
        performance_data = await self.get_recent_performance(user_id)
        current_rules = await self.get_current_rules(user_id)
        
        if not performance_data or not current_rules:
            return
        
        # 更新候補の評価
        update_candidates = await self.identify_update_candidates(
            user_id, performance_data, current_rules
        )
        
        for candidate in update_candidates:
            await self.process_update_candidate(user_id, candidate)
    
    async def identify_update_candidates(self, user_id: int, 
                                       performance_data: Dict, 
                                       current_rules: Dict) -> List[Dict]:
        """更新候補の特定"""
        
        candidates = []
        
        # 1. 効果が低いルールの特定
        ineffective_rules = self.find_ineffective_rules(
            performance_data.get('rule_effectiveness', {})
        )
        
        for rule_id in ineffective_rules:
            candidates.append({
                'type': 'effectiveness_improvement',
                'rule_id': rule_id,
                'current_effectiveness': ineffective_rules[rule_id],
                'suggested_action': 'adjust_or_disable'
            })
        
        # 2. 新しいエラーパターンに対するルール追加
        new_error_patterns = self.detect_new_error_patterns(
            performance_data.get('error_patterns', {})
        )
        
        for pattern in new_error_patterns:
            candidates.append({
                'type': 'new_rule_addition',
                'error_pattern': pattern,
                'frequency': new_error_patterns[pattern],
                'suggested_action': 'add_rule'
            })
        
        # 3. スキル向上に伴うルール調整
        skill_improvements = self.detect_skill_improvements(
            performance_data.get('skill_progress', {})
        )
        
        for skill, improvement in skill_improvements.items():
            if improvement > self.update_threshold:
                candidates.append({
                    'type': 'skill_based_adjustment',
                    'skill': skill,
                    'improvement': improvement,
                    'suggested_action': 'reduce_assistance'
                })
        
        return candidates
    
    def find_ineffective_rules(self, rule_effectiveness: Dict) -> Dict:
        """効果が低いルールを特定"""
        
        ineffective = {}
        
        for rule_id, effectiveness in rule_effectiveness.items():
            avg_score = effectiveness.get('overall_score', 0)
            acceptance_rate = effectiveness.get('acceptance_rate', 0)
            
            # 効果スコアが低い、または受け入れ率が低い
            if avg_score < 2.0 or acceptance_rate < 0.3:
                ineffective[rule_id] = {
                    'score': avg_score,
                    'acceptance_rate': acceptance_rate,
                    'interactions': effectiveness.get('interactions', 0)
                }
        
        return ineffective
    
    def detect_new_error_patterns(self, error_patterns: Dict) -> Dict:
        """新しいエラーパターンを検出"""
        
        new_patterns = {}
        
        for pattern, data in error_patterns.items():
            frequency = data.get('frequency', 0)
            
            # 頻度が高く、まだルールが存在しないパターン
            if frequency >= 5 and not self.rule_exists_for_pattern(pattern):
                new_patterns[pattern] = frequency
        
        return new_patterns
    
    def detect_skill_improvements(self, skill_progress: Dict) -> Dict:
        """スキル向上を検出"""
        
        improvements = {}
        
        for skill, progress in skill_progress.items():
            current_score = progress.get('current_score', 0)
            previous_score = progress.get('previous_score', 0)
            
            if previous_score > 0:
                improvement_rate = (current_score - previous_score) / previous_score
                if improvement_rate > 0.2:  # 20%以上の向上
                    improvements[skill] = improvement_rate
        
        return improvements
    
    async def process_update_candidate(self, user_id: int, candidate: Dict):
        """更新候補の処理"""
        
        candidate_type = candidate['type']
        
        if candidate_type == 'effectiveness_improvement':
            await self.handle_effectiveness_improvement(user_id, candidate)
        elif candidate_type == 'new_rule_addition':
            await self.handle_new_rule_addition(user_id, candidate)
        elif candidate_type == 'skill_based_adjustment':
            await self.handle_skill_based_adjustment(user_id, candidate)
    
    async def handle_effectiveness_improvement(self, user_id: int, candidate: Dict):
        """効果改善の処理"""
        
        rule_id = candidate['rule_id']
        current_effectiveness = candidate['current_effectiveness']
        
        # A/Bテストで改善案をテスト
        improvement_variants = await self.generate_improvement_variants(
            rule_id, current_effectiveness
        )
        
        if improvement_variants:
            await self.schedule_ab_test(
                user_id,
                rule_id,
                improvement_variants,
                'effectiveness_improvement'
            )
    
    async def handle_new_rule_addition(self, user_id: int, candidate: Dict):
        """新規ルール追加の処理"""
        
        error_pattern = candidate['error_pattern']
        frequency = candidate['frequency']
        
        # 新しいルールを生成
        new_rule = await self.generate_rule_for_pattern(error_pattern, frequency)
        
        if new_rule:
            # 段階的導入でテスト
            await self.schedule_gradual_rollout(
                user_id,
                new_rule,
                'new_rule_addition'
            )
    
    async def handle_skill_based_adjustment(self, user_id: int, candidate: Dict):
        """スキルベース調整の処理"""
        
        skill = candidate['skill']
        improvement = candidate['improvement']
        
        # スキル向上に応じたルール調整
        adjusted_rules = await self.adjust_rules_for_skill_improvement(
            user_id, skill, improvement
        )
        
        if adjusted_rules:
            await self.apply_rule_adjustments(user_id, adjusted_rules)
    
    async def generate_improvement_variants(self, rule_id: str, 
                                         current_effectiveness: Dict) -> List[Dict]:
        """改善バリアントの生成"""
        
        variants = []
        
        # 現在の問題を分析
        low_score = current_effectiveness.get('score', 0) < 2.0
        low_acceptance = current_effectiveness.get('acceptance_rate', 0) < 0.3
        
        if low_score:
            # メッセージの改善
            variants.append({
                'type': 'message_improvement',
                'changes': {
                    'message_tone': 'more_helpful',
                    'include_examples': True,
                    'add_learning_links': True
                }
            })
        
        if low_acceptance:
            # 厳格度の調整
            variants.append({
                'type': 'strictness_adjustment',
                'changes': {
                    'severity': 'reduce',
                    'auto_fix': 'enable',
                    'notification_frequency': 'reduce'
                }
            })
        
        return variants
    
    async def generate_rule_for_pattern(self, error_pattern: str, 
                                      frequency: int) -> Optional[Dict]:
        """エラーパターンに対するルール生成"""
        
        # パターン別のルール生成ロジック
        rule_templates = {
            'undefined_variable': {
                'severity': 'error',
                'message': '未定義の変数が使用されています。変数の宣言を確認してください。',
                'auto_fix': True,
                'trigger_patterns': ['ReferenceError.*is not defined']
            },
            'async_await_misuse': {
                'severity': 'warning',
                'message': 'async/awaitの使用方法を確認してください。',
                'auto_fix': False,
                'trigger_patterns': ['await.*non-async', 'async.*without-await']
            },
            'memory_leak_risk': {
                'severity': 'info',
                'message': 'メモリリークの可能性があります。リソースの解放を確認してください。',
                'auto_fix': False,
                'trigger_patterns': ['addEventListener.*without.*removeEventListener']
            }
        }
        
        if error_pattern in rule_templates:
            rule = rule_templates[error_pattern].copy()
            rule['pattern'] = error_pattern
            rule['frequency_based_priority'] = min(frequency / 10, 1.0)
            return rule
        
        return None
    
    async def schedule_ab_test(self, user_id: int, rule_id: str, 
                             variants: List[Dict], test_type: str):
        """A/Bテストのスケジュール"""
        
        test_config = {
            'name': f'{test_type}_{rule_id}_{datetime.now().strftime("%Y%m%d")}',
            'description': f'Rule effectiveness improvement test for {rule_id}',
            'variants': [
                {'name': 'current', 'config': {'rule_id': rule_id, 'changes': {}}},
                *[{'name': f'variant_{i}', 'config': variant} for i, variant in enumerate(variants)]
            ],
            'traffic_allocation': [0.5] + [0.5 / len(variants)] * len(variants),
            'duration_days': 7,
            'success_metrics': ['effectiveness_score', 'acceptance_rate', 'error_reduction'],
            'user_filter': {'user_ids': [user_id]}
        }
        
        from .ab_testing import ABTestFramework
        ab_framework = ABTestFramework()
        test_id = ab_framework.create_test(test_config)
        
        logger.info(f"Scheduled A/B test {test_id} for rule {rule_id}")
        
        return test_id
    
    async def apply_rule_adjustments(self, user_id: int, adjusted_rules: Dict):
        """ルール調整の適用"""
        
        # 現在のルールプロファイルを取得
        current_profile = await self.get_current_rule_profile(user_id)
        
        if not current_profile:
            return
        
        # ルールを更新
        updated_rules = current_profile['rule_config'].copy()
        updated_rules.update(adjusted_rules)
        
        # 新しいバージョンを作成
        new_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}_auto"
        
        await self.create_new_rule_version(
            user_id,
            new_version,
            updated_rules,
            'automatic_adjustment'
        )
        
        # ユーザーに通知
        await self.notify_rule_update(user_id, {
            'type': 'automatic_adjustment',
            'version': new_version,
            'changes_summary': self.summarize_changes(
                current_profile['rule_config'],
                updated_rules
            )
        })
        
        logger.info(f"Applied automatic rule adjustments for user {user_id}")

# 自動更新スケジューラー
class AutoUpdateScheduler:
    """自動更新スケジューラー"""
    
    def __init__(self, update_interval_hours: int = 24):
        self.update_interval = timedelta(hours=update_interval_hours)
        self.updater = AutomaticRuleUpdater()
        self.running = False
    
    async def start(self):
        """スケジューラーの開始"""
        
        self.running = True
        logger.info("Auto update scheduler started")
        
        while self.running:
            try:
                # アクティブなユーザーのリストを取得
                active_users = await self.get_active_users()
                
                # 各ユーザーのルール更新を評価
                for user_id in active_users:
                    await self.updater.evaluate_rule_updates(user_id)
                
                # 次の実行まで待機
                await asyncio.sleep(self.update_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Error in auto update scheduler: {e}")
                await asyncio.sleep(3600)  # エラー時は1時間待機
    
    def stop(self):
        """スケジューラーの停止"""
        self.running = False
        logger.info("Auto update scheduler stopped")
    
    async def get_active_users(self) -> List[int]:
        """アクティブユーザーのリスト取得"""
        # 過去24時間以内にアクティビティがあったユーザーを取得
        # 実装はDjangoのモデルに依存
        return []  # プレースホルダー

# 使用例
async def start_auto_update_system():
    """自動更新システムの開始"""
    
    scheduler = AutoUpdateScheduler(update_interval_hours=24)
    await scheduler.start()
```

#### Week 10: 自動改善システム

**Step 1: 予測的弱点検出**
```python
# mcp_server/predictive_analysis.py
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class PredictiveWeaknessDetector:
    """予測的弱点検出システム"""
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
    
    def prepare_time_series_features(self, user_data: List[Dict]) -> np.ndarray:
        """時系列特徴量の準備"""
        
        features_list = []
        
        for data_point in user_data:
            features = []
            
            # 基本パフォーマンス特徴量
            features.extend([
                data_point.get('score', 0),
                data_point.get('completion_time', 0),
                data_point.get('error_count', 0),
                data_point.get('help_usage', 0)
            ])
            
            # 学習パターン特徴量
            learning_pattern = data_point.get('learning_pattern', {})
            features.extend([
                learning_pattern.get('session_duration', 0),
                learning_pattern.get('focus_level', 0),
                learning_pattern.get('difficulty_preference', 0)
            ])
            
            # 時間的特徴量
            timestamp = datetime.fromisoformat(data_point.get('timestamp'))
            features.extend([
                timestamp.hour,  # 時間帯
                timestamp.weekday(),  # 曜日
                (datetime.now() - timestamp).days  # 経過日数
            ])
            
            # エラーパターン特徴量
            error_patterns = data_point.get('error_patterns', {})
            features.extend([
                error_patterns.get('syntax_errors', 0),
                error_patterns.get('logic_errors', 0),
                error_patterns.get('runtime_errors', 0)
            ])
            
            features_list.append(features)
        
        return np.array(features_list)
    
    def train_anomaly_detector(self, historical_data: List[Dict]):
        """異常検出モデルの訓練"""
        
        if len(historical_data) < 50:  # 最小データ数
            return False
        
        features = self.prepare_time_series_features(historical_data)
        features_scaled = self.scaler.fit_transform(features)
        
        self.anomaly_detector.fit(features_scaled)
        self.is_trained = True
        
        return True
    
    def predict_potential_weaknesses(self, recent_data: List[Dict]) -> Dict:
        """潜在的弱点の予測"""
        
        if not self.is_trained or len(recent_data) < 5:
            return self.fallback_prediction(recent_data)
        
        features = self.prepare_time_series_features(recent_data)
        features_scaled = self.scaler.transform(features)
        
        # 異常スコアの計算
        anomaly_scores = self.anomaly_detector.decision_function(features_scaled)
        
        # トレンド分析
        trend_analysis = self.analyze_trends(recent_data)
        
        # 予測結果の統合
        predictions = self.integrate_predictions(
            recent_data, anomaly_scores, trend_analysis
        )
        
        return predictions
    
    def analyze_trends(self, data: List[Dict]) -> Dict:
        """トレンド分析"""
        
        if len(data) < 3:
            return {}
        
        # スコアトレンド
        scores = [d.get('score', 0) for d in data]
        score_trend = self.calculate_trend(scores)
        
        # エラートレンド
        errors = [d.get('error_count', 0) for d in data]
        error_trend = self.calculate_trend(errors)
        
        # 完了時間トレンド
        completion_times = [d.get('completion_time', 0) for d in data]
        time_trend = self.calculate_trend(completion_times)
        
        return {
            'score_trend': score_trend,
            'error_trend': error_trend,
            'time_trend': time_trend,
            'overall_trend': self.calculate_overall_trend([score_trend, -error_trend, -time_trend])
        }
    
    def calculate_trend(self, values: List[float]) -> float:
        """線形トレンドの計算"""
        
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # 線形回帰の傾き
        slope = np.polyfit(x, y, 1)[0]
        return float(slope)
    
    def integrate_predictions(self, data: List[Dict], 
                            anomaly_scores: np.ndarray, 
                            trend_analysis: Dict) -> Dict:
        """予測結果の統合"""
        
        predictions = {
            'risk_level': 'low',
            'potential_weaknesses': [],
            'early_warning_indicators': [],
            'recommended_interventions': [],
            'confidence_score': 0.0
        }
        
        # 異常スコアから危険度を判定
        avg_anomaly_score = np.mean(anomaly_scores)
        if avg_anomaly_score < -0.3:
            predictions['risk_level'] = 'high'
        elif avg_anomaly_score < -0.1:
            predictions['risk_level'] = 'medium'
        
        # トレンド分析から潜在的弱点を特定
        overall_trend = trend_analysis.get('overall_trend', 0)
        if overall_trend < -0.1:  # 悪化傾向
            predictions['potential_weaknesses'].append({
                'type': 'performance_decline',
                'severity': 'medium' if overall_trend > -0.3 else 'high',
                'evidence': 'パフォーマンスの悪化傾向が検出されました',
                'timeline': '1-2週間以内に影響が顕在化する可能性'
            })
        
        # エラー増加傾向の検出
        error_trend = trend_analysis.get('error_trend', 0)
        if error_trend > 0.2:
            predictions['potential_weaknesses'].append({
                'type': 'error_pattern_emergence',
                'severity': 'medium',
                'evidence': 'エラー発生率の増加傾向',
                'timeline': '数日以内に問題が表面化する可能性'
            })
        
        # 早期警告指標の設定
        if predictions['risk_level'] != 'low':
            predictions['early_warning_indicators'] = self.generate_warning_indicators(
                data, trend_analysis
            )
        
        # 推奨介入の生成
        predictions['recommended_interventions'] = self.generate_interventions(
            predictions['potential_weaknesses'],
            trend_analysis
        )
        
        # 信頼度スコアの計算
        predictions['confidence_score'] = self.calculate_confidence_score(
            len(data), avg_anomaly_score, trend_analysis
        )
        
        return predictions
    
    def generate_warning_indicators(self, data: List[Dict], 
                                  trend_analysis: Dict) -> List[Dict]:
        """早期警告指標の生成"""
        
        indicators = []
        
        # 学習時間の短縮傾向
        if len(data) >= 3:
            recent_durations = [d.get('learning_pattern', {}).get('session_duration', 0) 
                              for d in data[-3:]]
            if all(recent_durations[i] > recent_durations[i+1] for i in range(len(recent_durations)-1)):
                indicators.append({
                    'type': 'decreasing_study_time',
                    'description': '学習時間の継続的な短縮',
                    'risk_level': 'medium'
                })
        
        # 難易度回避傾向
        difficulty_preferences = [d.get('learning_pattern', {}).get('difficulty_preference', 0) 
                                for d in data]
        if len(difficulty_preferences) >= 3:
            recent_prefs = difficulty_preferences[-3:]
            if all(recent_prefs[i] > recent_prefs[i+1] for i in range(len(recent_prefs)-1)):
                indicators.append({
                    'type': 'difficulty_avoidance',
                    'description': '困難な問題を避ける傾向の増加',
                    'risk_level': 'medium'
                })
        
        return indicators
    
    def generate_interventions(self, potential_weaknesses: List[Dict], 
                             trend_analysis: Dict) -> List[Dict]:
        """推奨介入の生成"""
        
        interventions = []
        
        for weakness in potential_weaknesses:
            weakness_type = weakness['type']
            
            if weakness_type == 'performance_decline':
                interventions.append({
                    'type': 'review_fundamentals',
                    'priority': 'high',
                    'description': '基礎概念の復習を強く推奨します',
                    'specific_actions': [
                        '過去の学習内容の振り返り',
                        '理解が曖昧な概念の再学習',
                        '簡単な問題からの段階的な再開'
                    ],
                    'timeline': '今すぐ開始'
                })
            
            elif weakness_type == 'error_pattern_emergence':
                interventions.append({
                    'type': 'error_pattern_analysis',
                    'priority': 'medium',
                    'description': 'エラーパターンの詳細分析と対策',
                    'specific_actions': [
                        'よくあるエラーの原因分析',
                        'デバッグスキルの向上',
                        'コードレビューの活用'
                    ],
                    'timeline': '1週間以内'
                })
        
        # 全般的な介入
        overall_trend = trend_analysis.get('overall_trend', 0)
        if overall_trend < -0.2:
            interventions.append({
                'type': 'comprehensive_support',
                'priority': 'high',
                'description': '包括的な学習支援の提供',
                'specific_actions': [
                    'パーソナライズされた学習計画の再作成',
                    'メンターとの1対1セッション',
                    '学習方法の見直しと最適化'
                ],
                'timeline': '緊急対応'
            })
        
        return interventions

class ProactiveContentGenerator:
    """プロアクティブコンテンツ生成器"""
    
    def __init__(self):
        self.weakness_detector = PredictiveWeaknessDetector()
    
    async def generate_proactive_content(self, user_id: int, 
                                       prediction_results: Dict) -> Dict:
        """プロアクティブな学習コンテンツの生成"""
        
        content_plan = {
            'immediate_actions': [],
            'weekly_plan': [],
            'monthly_goals': [],
            'personalized_resources': []
        }
        
        potential_weaknesses = prediction_results.get('potential_weaknesses', [])
        
        for weakness in potential_weaknesses:
            # 即座の対応コンテンツ
            immediate_content = await self.generate_immediate_content(weakness)
            content_plan['immediate_actions'].extend(immediate_content)
            
            # 週間学習計画
            weekly_content = await self.generate_weekly_content(weakness)
            content_plan['weekly_plan'].extend(weekly_content)
            
            # 月間目標
            monthly_goals = await self.generate_monthly_goals(weakness)
            content_plan['monthly_goals'].extend(monthly_goals)
        
        # パーソナライズされたリソース
        content_plan['personalized_resources'] = await self.generate_personalized_resources(
            user_id, potential_weaknesses
        )
        
        return content_plan
    
    async def generate_immediate_content(self, weakness: Dict) -> List[Dict]:
        """即座の対応コンテンツ生成"""
        
        weakness_type = weakness['type']
        
        if weakness_type == 'performance_decline':
            return [
                {
                    'type': 'diagnostic_quiz',
                    'title': '理解度確認クイズ',
                    'description': '現在の理解レベルを正確に把握します',
                    'estimated_time': 15,
                    'priority': 'high'
                },
                {
                    'type': 'concept_review',
                    'title': '重要概念の振り返り',
                    'description': '基礎概念の確認と補強',
                    'estimated_time': 30,
                    'priority': 'high'
                }
            ]
        
        elif weakness_type == 'error_pattern_emergence':
            return [
                {
                    'type': 'error_analysis_exercise',
                    'title': 'エラー分析演習',
                    'description': 'よくあるエラーの特定と修正方法',
                    'estimated_time': 20,
                    'priority': 'medium'
                }
            ]
        
        return []
    
    async def generate_weekly_content(self, weakness: Dict) -> List[Dict]:
        """週間学習コンテンツ生成"""
        
        return [
            {
                'day': 1,
                'content': '基礎概念の復習',
                'activities': ['読む', '例題を解く', '確認テスト']
            },
            {
                'day': 3,
                'content': '応用問題への挑戦',
                'activities': ['段階的な問題解決', 'ピアレビュー']
            },
            {
                'day': 5,
                'content': 'プロジェクト実践',
                'activities': ['ミニプロジェクト', '成果物の発表']
            },
            {
                'day': 7,
                'content': '週間振り返り',
                'activities': ['進捗確認', '次週の計画立案']
            }
        ]

# 使用例
async def run_predictive_analysis(user_id: int):
    """予測分析の実行"""
    
    # 過去のデータを取得
    historical_data = await get_user_historical_data(user_id, days=90)
    recent_data = await get_user_recent_data(user_id, days=7)
    
    # 予測モデルの訓練
    detector = PredictiveWeaknessDetector()
    if detector.train_anomaly_detector(historical_data):
        
        # 弱点予測の実行
        predictions = detector.predict_potential_weaknesses(recent_data)
        
        # プロアクティブコンテンツの生成
        content_generator = ProactiveContentGenerator()
        content_plan = await content_generator.generate_proactive_content(
            user_id, predictions
        )
        
        # 結果をデータベースに保存
        await save_prediction_results(user_id, predictions, content_plan)
        
        # 必要に応じてユーザーに通知
        if predictions['risk_level'] in ['medium', 'high']:
            await notify_user_of_predictions(user_id, predictions, content_plan)
        
        return {
            'predictions': predictions,
            'content_plan': content_plan,
            'status': 'success'
        }
    
    else:
        return {
            'status': 'insufficient_data',
            'message': '予測に必要なデータが不足しています'
        }
```

#### Week 8-9: 実践ログ統合
- [ ] リアルタイムログ収集システム
- [ ] エラーパターン自動分類
- [ ] ルール効果測定システム
- [ ] 統計ダッシュボード

#### Week 10: 自動改善システム  
- [ ] 自動的な学習コンテンツ更新提案
- [ ] ルールの自動調整機能
- [ ] 予測的な弱点検出
- [ ] 統合テストとユーザビリティテスト

### Phase 4: エンタープライズ機能 (4週間)
**目標**: 組織レベルの機能とスケーラビリティ

#### Week 11-12: チーム機能
- [ ] 部門別統計・分析
- [ ] チーム標準ルール管理
- [ ] ピアレビュー連携
- [ ] スキルマトリックス自動生成

#### Week 13-14: 拡張性とパフォーマンス
- [ ] 水平スケーリング対応
- [ ] キャッシング戦略実装
- [ ] モニタリング・アラート
- [ ] セキュリティ監査とペネトレーションテスト

## 📊 成功指標とKPI

### 技術的指標
- **API応答時間**: 95%ile < 500ms
- **MCP処理時間**: 学習分析 < 3秒、ルール生成 < 2秒
- **システム稼働率**: > 99.9%
- **データ処理精度**: 弱点検出精度 > 85%

### ユーザー体験指標
- **学習効率向上率**: +30% (従来の学習方法と比較)
- **開発エラー削減率**: -50% (Cursor Rules適用前後)
- **ユーザー満足度**: > 4.5/5.0
- **継続利用率**: > 80% (3ヶ月後)

### ビジネス指標
- **スキル向上速度**: 従来比 +40%
- **チーム生産性**: コードレビュー時間 -30%
- **品質指標**: バグ検出率向上 +60%
- **ROI**: 導入コスト回収期間 < 6ヶ月

## 🔒 セキュリティとプライバシー

### データ保護
- **個人学習データ暗号化**: AES-256による暗号化
- **APIトークン管理**: JWT + OAuth 2.0
- **データアクセス制御**: ロールベースアクセス制御（RBAC）
- **監査ログ**: 全データアクセスの記録

### プライバシー保護
- **データ匿名化**: 統計処理時の個人情報除去
- **同意管理**: 明示的なデータ使用同意
- **GDPR準拠**: EU圏ユーザーの権利保護
- **データ保持期間**: 明確な保存期間と自動削除

### セキュリティ対策
```python
# セキュリティミドルウェアの例
class CursorIntegrationSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Rate limiting
        if not self.check_rate_limit(request):
            return HttpResponse("Rate limit exceeded", status=429)
        
        # API token validation
        if not self.validate_api_token(request):
            return HttpResponse("Invalid token", status=401)
        
        # Data access authorization
        if not self.authorize_data_access(request):
            return HttpResponse("Unauthorized", status=403)
        
        response = self.get_response(request)
        
        # Response sanitization
        response = self.sanitize_response(response)
        
        return response
```

## 📈 モニタリングと運用

### システム監視
```python
# メトリクス収集の例
from prometheus_client import Counter, Histogram, Gauge

# API使用量メトリクス
api_requests_total = Counter(
    'cursor_integration_api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

# 処理時間メトリクス
processing_duration = Histogram(
    'cursor_integration_processing_seconds',
    'Processing duration',
    ['operation_type']
)

# アクティブユーザー数
active_users = Gauge(
    'cursor_integration_active_users',
    'Currently active users'
)
```

### ログ管理
```python
# 構造化ログの例
import structlog

logger = structlog.get_logger()

# 学習分析ログ
logger.info("learning_analysis_completed", 
    user_id=user_id,
    analysis_duration=duration,
    weak_points_count=len(weak_points),
    confidence_score=confidence
)

# ルール生成ログ  
logger.info("cursor_rules_generated",
    user_id=user_id,
    rule_count=len(rules),
    customization_level=customization_level,
    generation_duration=duration
)
```

### 異常検知
```python
# 異常検知アラートの例
class AnomalyDetector:
    def check_analysis_accuracy(self, results):
        """分析精度の異常を検知"""
        if results.confidence_score < 0.7:
            self.send_alert("Low analysis confidence detected")
    
    def check_rule_effectiveness(self, effectiveness_metrics):
        """ルール効果の異常を検知"""
        if effectiveness_metrics.error_reduction < 0.2:
            self.send_alert("Rule effectiveness below threshold")
    
    def check_system_performance(self, metrics):
        """システムパフォーマンスの異常を検知"""
        if metrics.avg_response_time > 1000:  # 1秒
            self.send_alert("High response time detected")
```

## 🔄 継続的改善プロセス

### 自動学習システム
```python
class ContinuousLearningEngine:
    def analyze_user_feedback(self, feedback_data):
        """ユーザーフィードバックから改善点を特定"""
        # フィードバック分析
        satisfaction_trends = self.analyze_satisfaction_trends(feedback_data)
        feature_requests = self.extract_feature_requests(feedback_data)
        
        # 改善提案の生成
        improvement_proposals = self.generate_improvement_proposals(
            satisfaction_trends, feature_requests
        )
        
        return improvement_proposals
    
    def update_ai_models(self, practice_logs):
        """実践ログからAI モデルを更新"""
        # 新しい学習データの準備
        training_data = self.prepare_training_data(practice_logs)
        
        # モデルの再訓練
        updated_model = self.retrain_model(training_data)
        
        # A/Bテストでの検証
        self.deploy_model_for_testing(updated_model)
```

### バージョン管理戦略
```python
class RuleVersionManager:
    def create_rule_version(self, user_id, rules):
        """新しいルールバージョンを作成"""
        version = {
            "version_id": self.generate_version_id(),
            "user_id": user_id,
            "rules": rules,
            "created_at": datetime.utcnow(),
            "parent_version": self.get_current_version(user_id),
            "effectiveness_baseline": None  # 後で測定
        }
        return self.save_version(version)
    
    def rollback_rules(self, user_id, target_version):
        """効果が低い場合のロールバック"""
        target = self.get_version(user_id, target_version)
        self.set_active_version(user_id, target)
        
        self.log_rollback(user_id, target_version, "low_effectiveness")
```

---

## 📋 結論

この統合システムにより、asagami AIとCursor Rulesの連携による「適応型開発環境」が実現されます。個人の学習データから生成されたパーソナライズされたCursor Rulesにより、開発者は自分の弱点に特化した支援を受けながらコーディングを行い、その実践結果が再び学習内容の改善に活用される継続的な成長サイクルが確立されます。

### 期待される効果
1. **個人レベル**: スキル向上速度 +40%、開発エラー -50%
2. **チームレベル**: コード品質均一化、ナレッジ共有促進  
3. **組織レベル**: 開発生産性向上、技術負債削減

この包括的な設計仕様書に基づき、段階的な実装を進めることで、革新的な学習支援システムの構築が可能となります。

---

**作成日**: 2025-07-13  
**バージョン**: 1.0  
**作成者**: asagami AI開発チーム  
**承認**: 開発効率化推進チーム

**技術レビュー**: システムアーキテクト、セキュリティエンジニア  
**ビジネスレビュー**: プロダクトマネージャー、品質保証チーム

---

# INTEGRATION IMPLEMENTATION GUIDE

# asagami AI × Cursor Rules 統合実装ガイド

## 概要
このドキュメントは、asagami AIとCursor Rulesの連携による「適応型開発環境」を実現するための包括的な実装ガイドです。

## 1. アーキテクチャ概要

### 1.1 システム構成図
```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   asagami AI    │◄──►│  MCP Server      │◄──►│   Cursor IDE     │
│   (Django)      │    │  (Python)        │    │   (Claude Code)  │
├─────────────────┤    ├──────────────────┤    ├──────────────────┤
│• 学習データ管理 │    │• データ分析      │    │• 開発支援       │
│• 問題生成       │    │• ルール生成      │    │• ログ収集       │
│• 進捗追跡       │    │• AI処理          │    │• 適応型アシスト │
│• ユーザー管理   │    │• 統合処理        │    │• フィードバック │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

### 1.2 データフロー
```
学習 → 分析 → ルール生成 → 開発支援 → フィードバック → 改善
 ↑                                                    ↓
 └────────────── 継続的改善サイクル ──────────────────┘
```

## 2. 実装フェーズ

### Phase 1: 基盤構築 (4週間)
**目標**: MVPの実装と基本的な連携機能の確立

#### 2.1.1 asagami AI側の拡張
```python
# 新規APIエンドポイントの追加
# app/urls.py に追加
path('api/cursor-integration/', include('cursor_integration.urls')),

# cursor_integration/urls.py
urlpatterns = [
    path('learning-data/<int:user_id>/', views.get_learning_data, name='get_learning_data'),
    path('generate-rules/', views.generate_cursor_rules, name='generate_cursor_rules'),
    path('practice-logs/', views.collect_practice_logs, name='collect_practice_logs'),
]
```

#### 2.1.2 新規Djangoアプリの作成
```bash
python manage.py startapp cursor_integration
```

#### 2.1.3 必要なモデル追加
```python
# cursor_integration/models.py
class CursorRuleProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rule_version = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    rule_config = models.JSONField()
    is_active = models.BooleanField(default=True)

class PracticeLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    error_data = models.JSONField()
    completion_data = models.JSONField()
    productivity_metrics = models.JSONField()

class LearningAnalysis(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    analysis_date = models.DateField(auto_now_add=True)
    weak_points = models.JSONField()
    strong_points = models.JSONField()
    improvement_suggestions = models.JSONField()
    confidence_score = models.FloatField()
```

### Phase 2: MCP サーバー構築 (3週間)

#### 2.2.1 MCPサーバーのセットアップ
```python
# mcp_server/server.py
from mcp import McpServer
from mcp.types import Tool, TextContent

class AsagamiMcpServer(McpServer):
    def __init__(self):
        super().__init__("asagami-mcp-server", "1.0.0")
        self.setup_tools()
    
    def setup_tools(self):
        @self.tool()
        async def analyze_learning_data(user_id: int, period: int = 30):
            """学習データを分析して弱点と強みを特定"""
            # Django APIを呼び出してデータを取得
            analysis_result = await self.fetch_learning_data(user_id, period)
            return self.process_analysis(analysis_result)
        
        @self.tool()
        async def generate_cursor_rules(analysis_data: dict):
            """分析結果からCursor Rulesを生成"""
            rules = await self.create_adaptive_rules(analysis_data)
            return self.format_cursor_rules(rules)
```

#### 2.2.2 AI分析エンジンの実装
```python
# mcp_server/ai_engine.py
import openai
from typing import Dict, List

class LearningAnalysisEngine:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    async def analyze_weak_points(self, user_data: Dict) -> List[Dict]:
        """ユーザーの学習データから弱点を分析"""
        prompt = f"""
        学習データを分析して、ユーザーの弱点を特定してください：
        - 問題解答データ: {user_data['question_results']}
        - 学習時間: {user_data['study_time']}
        - エラーパターン: {user_data['error_patterns']}
        
        以下の形式でJSONレスポンスを返してください：
        {{
            "weak_points": [
                {{
                    "topic": "トピック名",
                    "score": 数値スコア,
                    "priority": "high/medium/low",
                    "improvement_suggestions": ["提案1", "提案2"]
                }}
            ]
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

### Phase 3: Cursor Rules生成エンジン (2週間)

#### 2.3.1 ルール生成ロジック
```python
# mcp_server/rule_generator.py
class CursorRuleGenerator:
    def __init__(self):
        self.rule_templates = self.load_rule_templates()
    
    def generate_personalized_rules(self, weak_points: List[Dict], user_profile: Dict) -> Dict:
        """個人に特化したCursor Rulesを生成"""
        rules = {
            "version": "1.0",
            "user_profile": user_profile,
            "rules": {},
            "templates": [],
            "suggestions": []
        }
        
        for weak_point in weak_points:
            topic = weak_point['topic']
            if topic in self.rule_templates:
                personalized_rule = self.customize_rule(
                    self.rule_templates[topic], 
                    weak_point,
                    user_profile
                )
                rules['rules'][topic] = personalized_rule
        
        return rules
    
    def customize_rule(self, template: Dict, weak_point: Dict, profile: Dict) -> Dict:
        """テンプレートをユーザーに合わせてカスタマイズ"""
        rule = template.copy()
        
        # スキルレベルに応じた調整
        skill_level = profile.get('skill_level', 'intermediate')
        if skill_level == 'beginner':
            rule['severity'] = 'error'
            rule['auto_fix'] = True
        elif skill_level == 'advanced':
            rule['severity'] = 'info'
            rule['auto_fix'] = False
        
        # 弱点に応じたメッセージのカスタマイズ
        rule['message'] = rule['message'].format(
            topic=weak_point['topic'],
            suggestions=', '.join(weak_point['improvement_suggestions'])
        )
        
        return rule
```

### Phase 4: フィードバックループ実装 (3週間)

#### 2.4.1 実践ログ収集システム
```python
# cursor_integration/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def collect_practice_logs(request):
    """Cursorからの実践ログを収集"""
    if request.method == 'POST':
        log_data = json.loads(request.body)
        
        # ログデータの保存
        practice_log = PracticeLog.objects.create(
            user_id=log_data['user_id'],
            session_id=log_data['session_id'],
            start_time=log_data['session_start'],
            end_time=log_data['session_end'],
            error_data=log_data['development_data']['errors_encountered'],
            completion_data=log_data['development_data']['code_completions'],
            productivity_metrics=log_data['development_data']['productivity_metrics']
        )
        
        # 非同期でフィードバック分析を実行
        analyze_feedback.delay(practice_log.id)
        
        return JsonResponse({'status': 'success', 'log_id': practice_log.id})
```

#### 2.4.2 フィードバック分析タスク
```python
# cursor_integration/tasks.py
from celery import shared_task
from .ai_engine import LearningAnalysisEngine

@shared_task
def analyze_feedback(practice_log_id):
    """実践ログを分析してフィードバックを生成"""
    practice_log = PracticeLog.objects.get(id=practice_log_id)
    
    # エラーパターンの分析
    error_analysis = analyze_error_patterns(practice_log.error_data)
    
    # 新しい弱点の検出
    new_weak_points = detect_new_weak_points(error_analysis)
    
    # 学習コンテンツの更新提案
    if new_weak_points:
        generate_new_learning_content.delay(
            practice_log.user_id, 
            new_weak_points
        )
    
    # ルールの効果測定
    rule_effectiveness = measure_rule_effectiveness(practice_log)
    
    return {
        'new_weak_points': new_weak_points,
        'rule_effectiveness': rule_effectiveness
    }
```

## 3. 技術スタック

### 3.1 バックエンド
- **Django**: 4.2+ (既存システム)
- **Python**: 3.9+
- **PostgreSQL**: 14+ (既存データベース)
- **Redis**: 7+ (キャッシュ・セッション管理)
- **Celery**: 5+ (非同期タスク処理)

### 3.2 MCP サーバー
- **mcp**: 最新版
- **FastAPI**: 0.104+ (API部分)
- **OpenAI API**: GPT-4 (AI分析)
- **asyncio**: 非同期処理

### 3.3 フロントエンド（拡張）
- **React**: 18.2+ (既存)
- **Axios**: API通信
- **WebSocket**: リアルタイム通信

## 4. 設定とデプロイ

### 4.1 環境変数
```bash
# .env
OPENAI_API_KEY=your_openai_api_key
MCP_SERVER_URL=http://localhost:8001
CURSOR_WEBHOOK_SECRET=your_webhook_secret
REDIS_URL=redis://localhost:6379
```

### 4.2 Dockerコンテナ構成
```yaml
# docker-compose.yml
version: '3.8'
services:
  django:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/asagami
    depends_on:
      - db
      - redis
  
  mcp-server:
    build: ./mcp_server
    ports:
      - "8001:8001"
    environment:
      - DJANGO_API_URL=http://django:8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery:
    build: .
    command: celery -A mysite worker -l info
    depends_on:
      - redis
      - db
```

## 5. セキュリティ考慮事項

### 5.1 データ保護
- 個人学習データの暗号化
- APIアクセストークンの適切な管理
- CORS設定の最適化

### 5.2 認証・認可
```python
# cursor_integration/authentication.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class CursorIntegrationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # 権限チェック
        if not request.user.has_perm('cursor_integration.view_data'):
            return Response({'error': 'Permission denied'}, status=403)
```

## 6. テスト戦略

### 6.1 単体テスト
```python
# tests/test_rule_generator.py
class TestCursorRuleGenerator(TestCase):
    def setUp(self):
        self.generator = CursorRuleGenerator()
        self.sample_weak_points = [
            {
                'topic': 'SQL Injection',
                'score': 65,
                'priority': 'high'
            }
        ]
    
    def test_generate_personalized_rules(self):
        rules = self.generator.generate_personalized_rules(
            self.sample_weak_points,
            {'skill_level': 'intermediate'}
        )
        self.assertIn('SQL Injection', rules['rules'])
```

### 6.2 統合テスト
```python
# tests/test_integration.py
class TestAsagamiCursorIntegration(TestCase):
    def test_end_to_end_workflow(self):
        # 1. 学習データの生成
        user = create_test_user()
        create_learning_data(user)
        
        # 2. MCP分析の実行
        analysis = call_mcp_analysis(user.id)
        
        # 3. Cursor Rules生成
        rules = generate_cursor_rules(analysis)
        
        # 4. ルール配信
        response = deploy_rules_to_cursor(rules)
        
        self.assertEqual(response.status_code, 200)
```

## 7. モニタリングとメトリクス

### 7.1 KPI設定
- 学習改善率: 前月比での問題正答率向上
- 開発エラー減少率: Cursor使用前後のエラー発生率比較
- ユーザー満足度: フィードバックスコア
- システムパフォーマンス: API応答時間、MCP処理時間

### 7.2 ログ設定
```python
# settings/logging.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'cursor_integration': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/cursor_integration.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'cursor_integration': {
            'handlers': ['cursor_integration'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 8. ロードマップ

### 8.1 短期目標 (3ヶ月)
- [ ] MVPの完成とβテスト開始
- [ ] 基本的な学習データ分析機能
- [ ] シンプルなCursor Rules生成
- [ ] フィードバック収集システム

### 8.2 中期目標 (6ヶ月)
- [ ] AI分析精度の向上
- [ ] チーム機能の実装
- [ ] リアルタイム更新システム
- [ ] 外部ツール連携（GitHub、Slack等）

### 8.3 長期目標 (12ヶ月)
- [ ] 機械学習による予測分析
- [ ] 自動的な学習コンテンツ生成
- [ ] 企業向けエンタープライズ機能
- [ ] 他のIDE対応（VS Code、IntelliJ等）

## 9. 成功指標

### 9.1 技術的指標
- API応答時間: < 500ms (95%ile)
- MCP処理時間: < 2秒
- システム稼働率: > 99.9%
- エラー率: < 0.1%

### 9.2 ビジネス指標
- ユーザーの学習効率向上: +30%
- 開発エラー減少: -50%
- ユーザー満足度: > 4.5/5.0
- 継続利用率: > 80%

---

**作成日**: 2025-07-13  
**バージョン**: 1.0  
**作成者**: asagami AI開発チーム  
**レビュー**: 開発効率化推進チーム

---

# MCP DESIGN SPECIFICATION

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

---

# REST API DESIGN SPECIFICATION

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