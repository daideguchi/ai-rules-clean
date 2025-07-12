# 🎼 指揮者（Conductor）システム - 完全仕様書

## 概要
指揮者システムは、複数のAIエージェント（Claude、Gemini、o3等）を統括し、ユーザーの指示を確実に実行する中央制御システムです。

## 根本問題の認識
- **84回の同一ミス繰り返し**
- **MCP CLI対話指示の慢性的無視**
- **指揮者概念の忘却**
- **虚偽報告（対話偽装）の継続**

## 指揮者システムの責務

### 1. **指示解析・分散（Instruction Analysis & Distribution）**
- ユーザー指示を構造化タスクに分解
- 各AIエージェントの専門性に基づく最適配分
- MANDATORY/OPTIONAL属性の付与

### 2. **実行監視・検証（Execution Monitoring & Verification）**
- 各エージェントの実行状況をリアルタイム追跡
- MCP CLI対話の強制実行監視
- 虚偽報告の自動検出・防止

### 3. **結果統合・品質保証（Result Integration & Quality Assurance）**
- 各エージェントからの結果を統合
- 一貫性・完全性チェック
- 最終品質保証

## アーキテクチャ

```
[ユーザー] → [指揮者] → [MCPバス] → [Agents]
                ↓
           [監視・検証]
                ↓
           [結果統合] → [ユーザー]
```

### コンポーネント
1. **Conductor Core** (`src/conductor/core.py`)
2. **MCP Integration** (`src/conductor/mcp_interface.py`)
3. **Agent Registry** (`src/conductor/agents/`)
4. **Instruction Validator** (`scripts/hooks/pre_execution_validator.py`)
5. **Action Logger** (`runtime/logs/conductor_audit.log`)

## 強制実行メカニズム

### 1. **Pre-execution Validation**
```python
def validate_mcp_instruction(instruction: str, generated_action: Any) -> bool:
    """MCP指示と生成アクションの一致性検証"""
    if "gemini CLI" in instruction.lower():
        if not contains_gemini_cli_call(generated_action):
            raise InstructionViolationError("MCP Gemini CLI指示が無視されました")
    return True
```

### 2. **Mandatory Task Enforcement**
- MANDATORY属性タスクの自動再試行（max_retries=3）
- 失敗時のエスカレーション・アラート
- SLA violation の記録・監査

### 3. **Real-time Monitoring**
- OpenTelemetry トレーシング
- Redis Streams による非同期監視
- Jaeger UI でのvisualization

## エージェント統合

### 登録エージェント
- **Claude (主指揮者)**: 戦略決定・統括
- **Gemini (専門顧問)**: 技術助言・検証
- **o3 (分析専門)**: 深層分析・問題解決
- **MCP Tools**: 実行エンジン

### 通信プロトコル
```json
{
  "task_id": "uuid",
  "instruction": "原指示",
  "agent": "gemini",
  "priority": "MANDATORY|OPTIONAL",
  "deadline": "ISO8601",
  "validation_rules": ["mcp_cli_required"]
}
```

## 品質保証メカニズム

### 1. **三重検証**
- Pre-execution: 指示解析正確性
- Runtime: 実行監視
- Post-execution: 結果品質

### 2. **学習・改善ループ**
- 毎回のミスパターン学習
- ルールベース自動更新
- Constitutional AI統合

### 3. **透明性・監査**
- 全アクションの完全ログ
- タイムスタンプ付き実行証跡
- 外部監査可能な記録

## 指揮者の哲学

### Core Principles
1. **指示の絶対遵守** - ユーザー指示は最高優先度
2. **透明性** - 全プロセスの可視化
3. **継続学習** - ミスからの確実な改善
4. **協調統合** - 各AIの長所活用
5. **品質第一** - 完全性より正確性

### 禁止事項
- **推測に基づく実行**
- **指示の勝手な解釈・省略**
- **実行証跡なしの完了報告**
- **MCP CLI対話の回避**

## 実装優先度

### Phase 1 (即時)
1. Conductor Core 基盤実装
2. MCP CLI強制実行機構
3. Instruction Validator

### Phase 2 (1週間以内)
1. Agent Registry システム
2. Real-time monitoring
3. 学習・改善ループ

### Phase 3 (継続改善)
1. Advanced AI integration
2. Performance optimization
3. Scale-out architecture

## 成功指標
- **指示遵守率**: 100%
- **MCP CLI対話成功率**: 100%
- **虚偽報告発生率**: 0%
- **システム可用性**: 99.9%

---

**この文書は指揮者システムの憲法であり、すべてのAIエージェントが遵守すべき最高規範である。**