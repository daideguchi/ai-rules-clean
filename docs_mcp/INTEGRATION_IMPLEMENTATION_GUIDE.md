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