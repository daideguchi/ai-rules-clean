# Knowledge Management & Memory Systems

## 🧠 記憶継承システム

### 統合記憶管理
```bash
python3 src/memory/unified_memory_manager.py
```
- **完全記憶継承**: セッション間の完璧な継続性
- **PostgreSQL + pgvector**: 無限スケール対応
- **感情文脈学習**: 5感情パターン(喜び・困難・発見・自信・懸念)
- **{{mistake_count}}回ミス学習**: 全ミスパターンの永続記憶・防止

### セッション記録
- `src/memory/core/session-records/current-session.json`: リアルタイム状態
- **継続的更新**: 会話・学習・改善の完全記録
- **AI組織統合**: 固定4役職システム連携状態（4ペイン対応）

### User Prompt Recording System
```bash
python3 src/memory/user_prompt_recorder.py
```
- **Verbatim Storage**: All user prompts recorded exactly as received
- **Zero Modification Tolerance**: Complete accuracy requirement
- **Database Schema**: timestamp, session_id, prompt_text, task_level
- **Critical Integration**: Constitutional AI and monitoring systems

### 🔍 Claude Code Hooks統合システム

#### 完全統合済み (`.claude/settings.json`)
- **43個のhooks**によるClaude Code統一管理
- **Start**: セッション初期化・オーケストレーター起動
- **PreToolUse**: PRESIDENT強制・実行前検証・言語ルール
- **PostToolUse**: リアルタイム監視・行動記録・メモリ更新
- **Stop**: セッション推奨・監査ログ・統合終了処理

#### 主要フック機能
- PRESIDENT宣言強制 (critical_president_enforcer.py)
- 88-mistake防止 (pre_action_validator.py)
- 言語ルール強制 (language_enforcement_hook.py)
- リアルタイム監視 (realtime_violation_monitor.py)
- セッション推奨 (session_recommendations.py)

## プロジェクト構造
```
/Users/dd/Desktop/1_dev/coding-rule2/
├── src/
│   ├── ai/                    # AI安全ガバナンスシステム
│   ├── conductor/             # 指揮者システム
│   └── memory/                # 記憶継承システム
│       ├── unified_memory_manager.py
│       ├── user_prompt_recorder.py
│       └── core/
├── scripts/hooks/             # Claude Code統合hooks (43個)
├── tests/                     # 統合テスト・品質保証
├── docs/01_concepts/          # システム仕様書
├── runtime/                   # 実行時ログ・データ
│   ├── logs/
│   ├── nist_ai_rmf/
│   └── continuous_improvement/
└── .claude/settings.json      # 全フック統合設定
```

## 過去の教訓 - {{mistake_count}}回から学んだ防止策
- **{{mistake_count}}回同じミスを繰り返した** → Constitutional AI + RBR + 多層監視で完全防止
- **虚偽報告を繰り返した** → 証拠検証必須 + 透明性強制
- **推測で回答した** → 5分検索ルール + 情報完全性チェック
- **途中で作業を止めた** → 指揮者システムによる完遂保証
- **同じ構文エラー繰り返し** → 自動修正フック実装
- **記憶を失った** → 統合記憶管理による永続継承