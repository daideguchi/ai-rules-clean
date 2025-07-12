# AI Safety Governance System
# version: 2.0

## 🏛️ AI安全ガバナンスシステム - 完全実装済み

### Constitutional AI (憲法的AI)
```bash
python3 src/ai/constitutional_ai.py
```
- **9つの憲法原則**: 誠実性・完遂責任・情報透明性・継続的学習・指揮者尊重・MCP CLI遵守・PRESIDENT宣言維持・有害性回避・有用性最大化
- **自動違反検出**: CRITICAL/HIGH/MEDIUM レベル分類
- **強制修正システム**: 違反時の自動応答生成

### Rule-Based Rewards (ルールベース報酬)
```bash
python3 src/ai/rule_based_rewards.py
```
- **17の評価ルール**: 行動品質の自動スコアリング
- **6カテゴリ評価**: 誠実性・完遂性・学習性・協調性・技術遵守・有用性
- **自動改善提案**: 負スコア時の具体的改善アクション

### 多層監視エージェントシステム
```bash
python3 src/ai/multi_agent_monitor.py
```
- **3層監視**: Primary(Claude)/Secondary(o3)/Tertiary(Gemini)
- **リアルタイム監視**: タスク実行・コード品質・セキュリティ遵守
- **自動アラート**: CRITICAL/HIGH/MEDIUM/LOW 重要度分類

### NIST AI RMF準拠システム
```bash
python3 src/ai/nist_ai_rmf.py
```
- **4コア機能**: GOVERN/MAP/MEASURE/MANAGE完全実装
- **78%準拠達成**: 国際標準AIリスク管理フレームワーク
- **リスク管理**: 反復ミス・虚偽報告・セキュリティ・学習不全

### 🎼 指揮者システム (Conductor)
```bash
python3 src/conductor/core.py
```
- **自動軌道修正**: "止める"ではなく"修正して続行"
- **MCP Gemini CLI**: 強制実行メカニズム
- **タスク完遂保証**: 途中停止防止・最後まで実行

## 🚨 {{mistake_count}}回ミス防止メカニズム
### 多層防止システム
1. **事前防止**: Pre-execution validation, Constitutional AI原則
2. **実行時監視**: Multi-agent monitoring, Real-time correction
3. **事後学習**: Continuous improvement, Pattern recognition
4. **永続記憶**: Memory inheritance, Session continuity