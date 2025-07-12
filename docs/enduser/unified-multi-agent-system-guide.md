# 🚀 統合多エージェントシステム使用ガイド

## 📋 概要

このシステムは、Anthropicの多エージェント研究に基づいて設計された統合型のAI組織管理システムです。

### 🎯 主要特徴

- **オーケストレーター・ワーカーパターン**: 単一の調整システムが複数のワーカーを管理
- **WebSocket通信**: 高速でリアルタイムなメッセージング
- **動的タスク分散**: 負荷分散と自動最適化
- **統合監視システム**: 包括的な性能監視と品質管理
- **自動復旧機能**: 障害時の自動復旧とヘルスチェック

## 🏗️ システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                 SYSTEM LAUNCHER                              │
│                 統合起動管理                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                UNIFIED ORCHESTRATOR                          │
│                統合オーケストレーター                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                MESSAGE BUS                               │ │
│  │              メッセージバス                                │ │
│  │           WebSocket (Port 8080)                          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     WORKER AGENTS                            │
│                  ワーカーエージェント                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   WORKER1   │ │   WORKER2   │ │   WORKER3   │ │   WORKER4   │ │
│  │  Automation │ │  Monitoring │ │ Integration │ │   Analysis  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 システム起動

### 1. 基本起動

```bash
# ai-agentsディレクトリに移動
cd ai-agents

# 統合システムランチャーを起動
node scripts/automation/SYSTEM_LAUNCHER.js
```

### 2. 設定ファイルの確認

システムは以下の設定ファイルを使用します：

```json
// configs/unified_system_config.json
{
  "orchestrator": {
    "port": 8080,
    "maxWorkers": 4,
    "monitoringInterval": 30000
  },
  "workers": {
    "specializations": {
      "WORKER1": { "primary": "automation" },
      "WORKER2": { "primary": "monitoring" },
      "WORKER3": { "primary": "integration" },
      "WORKER4": { "primary": "analysis" }
    }
  }
}
```

## 📊 システム監視

### リアルタイム統計

システム起動後、以下の統計情報がコンソールに表示されます：

```
📊 システム統計: オーケストレーター: 稼働, ワーカー: 4/4
📊 性能統計: Workers: 4, Queued: 0, Active: 0, Completed: 0
```

### ヘルスチェック

- **自動監視**: 30秒間隔でヘルスチェック実行
- **障害検出**: 非アクティブワーカーの検出
- **自動復旧**: 障害発生時の自動復旧（最大3回）

## 🎯 タスク実行

### タスクの追加

```javascript
// プログラムからのタスク追加例
const orchestrator = new UnifiedOrchestrator();
await orchestrator.start();

// 分析タスクの追加
const taskId = orchestrator.addTask({
    type: 'analysis',
    data: { input: 'sample data' },
    priority: 'high'
});

// 自動化タスクの追加
const taskId2 = orchestrator.addTask({
    type: 'automation',
    data: { action: 'deploy' },
    priority: 'medium'
});
```

### タスクタイプ

| タイプ | 説明 | 専門ワーカー |
|--------|------|-------------|
| analysis | データ分析・パターン検出 | WORKER4 |
| automation | 自動化・プロセス実行 | WORKER1 |
| monitoring | 監視・メトリクス収集 | WORKER2 |
| integration | システム統合・連携 | WORKER3 |

## 🔧 設定カスタマイズ

### オーケストレーター設定

```json
{
  "orchestrator": {
    "port": 8080,              // WebSocketポート
    "maxWorkers": 4,           // 最大ワーカー数
    "monitoringInterval": 30000, // 監視間隔(ms)
    "qualityThreshold": 0.8,   // 品質閾値
    "taskTimeout": 300000,     // タスクタイムアウト(ms)
    "retryLimit": 3           // 再試行回数
  }
}
```

### ワーカー設定

```json
{
  "workers": {
    "specializations": {
      "WORKER1": {
        "primary": "automation",
        "secondary": ["analysis", "integration"]
      }
    }
  }
}
```

## 🛠️ 開発・拡張

### 新しいタスクタイプの追加

1. **ワーカーエージェントの拡張**:
```javascript
// scripts/core/WORKER_AGENT.js
async processTask(task) {
    switch (task.type) {
        case 'newTaskType':
            return await this.performNewTask(task.data);
        // 既存のケース...
    }
}
```

2. **設定ファイルの更新**:
```json
{
  "workers": {
    "defaultCapabilities": {
      "newTaskType": true
    }
  }
}
```

### カスタムワーカーの作成

```javascript
const WorkerAgent = require('./scripts/core/WORKER_AGENT.js');

class CustomWorker extends WorkerAgent {
    constructor(workerId, orchestratorUrl) {
        super(workerId, orchestratorUrl);
        this.capabilities = {
            ...this.capabilities,
            customCapability: true
        };
    }
    
    async performCustomTask(data) {
        // カスタムロジック
        return { result: 'custom result' };
    }
}
```

## 🔍 トラブルシューティング

### よくある問題

1. **ワーカー接続エラー**
   ```
   ERROR: connect ECONNREFUSED 127.0.0.1:8080
   ```
   - 原因: オーケストレーターが起動していない
   - 対策: システムランチャーを使用して統合起動

2. **タスク処理エラー**
   ```
   ❌ タスク失敗: task_123 - TypeError: Cannot read property
   ```
   - 原因: タスクデータの不正
   - 対策: タスクスキーマの確認

3. **メモリ使用量増加**
   - 原因: 完了タスクの蓄積
   - 対策: 定期的なクリーンアップ実行

### デバッグモード

```bash
# 詳細ログ付きで起動
DEBUG=* node scripts/automation/SYSTEM_LAUNCHER.js
```

## 📈 性能最適化

### 推奨設定

- **高負荷環境**: maxWorkers: 8, monitoringInterval: 15000
- **低負荷環境**: maxWorkers: 2, monitoringInterval: 60000
- **開発環境**: maxWorkers: 2, monitoringInterval: 10000

### 監視メトリクス

- **スループット**: 1分間あたりの完了タスク数
- **レイテンシー**: タスクの平均処理時間
- **成功率**: 成功したタスクの割合
- **ワーカー効率**: 各ワーカーの性能指標

## 🔄 システム停止

### 正常停止

```bash
# Ctrl+C または SIGTERM でグレースフル停止
^C
🛑 SIGINT受信 - システム停止中...
✅ 統合多エージェントシステム停止完了
```

### 緊急停止

```bash
# 強制停止
pkill -f "SYSTEM_LAUNCHER.js"
```

## 🎉 次のステップ

1. **既存システムとの統合**: 現在のTrinity、Autopilot、One-Commandシステムとの統合
2. **AI機能の拡張**: Claude、Gemini、YOLO統合の強化
3. **監視機能の拡張**: より詳細なメトリクスとアラート
4. **スケーラビリティ**: 複数マシンでの分散実行

---

**🔥 このシステムは、Anthropicの研究に基づいた次世代AIエージェントシステムです。継続的な改善と最適化により、最高のパフォーマンスを実現します。**