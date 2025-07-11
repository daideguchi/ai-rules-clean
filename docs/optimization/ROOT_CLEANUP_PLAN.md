# 🧹 ルートディレクトリ最終整理計画

## 📊 現状分析（整理前）

### ルートレベルファイル数
- **隠しファイル**: 9個（過多）
- **通常ファイル**: 9個（過多）
- **隠しディレクトリ**: 7個
- **通常ディレクトリ**: 8個

## 🎯 整理目標

o3とGemini推奨のベストプラクティスに基づき、ルートを最小限に保つ。

## 📋 最終整理計画

### ✅ ルートに残すファイル（必須）
```
/coding-rule2/
├── .git/                    # Git管理（必須）
├── .gitignore              # Git除外設定（必須）
├── .github/                # GitHub設定（必須）
├── .forbidden-move         # 重要：移動禁止リスト（必須）
├── .claude-project         # Claude Code設定（必須）
├── .cursorignore          # Cursor IDE設定（必須）
├── .cursorindexignore     # Cursor IDE設定（必須）
├── .env                    # 環境変数（.gitignore済み）
├── LICENSE                 # ライセンス（必須）
├── README.md              # プロジェクト説明（必須）
└── Makefile               # ビルド・自動化（必須）
```

### 📁 移動計画

#### 1. ドキュメント整理
```bash
docs/
├── optimization/     # 最適化関連
│   └── DIRECTORY_OPTIMIZATION_PLAN.md
├── recovery/        # 復旧関連
│   ├── MISSING_MISTAKES_68-78_DISCOVERY.md
│   └── recovery-consultation.md
└── analysis/        # 分析関連
    └── comprehensive-directory-analysis.md
```

#### 2. レポート整理
```bash
reports/
└── OPTIMIZATION_SUCCESS_REPORT.md
```

#### 3. リクエスト整理
```bash
requests/
└── gemini_recovery_request.json
```

#### 4. 環境設定整理
```bash
env/
└── .env.example
```

#### 5. ツール設定整理（.gitignore推奨）
```bash
.tools/
├── cursor/          # .cursor-new-backup移動
├── vscode/          # .vscode設定
├── specstory/       # .specstory設定
└── shell/           # .shell_integration.zsh
```

## 🚀 実行結果

### Before: ルート18ファイル
### After: ルート11ファイル（必須のみ）

### 削減効果
- **可読性向上**: 39%ファイル削減
- **メンテナンス性**: 必須ファイルのみで明確
- **開発効率**: 新規開発者の理解時間短縮

## 🛡️ 安全対策

1. **.forbidden-move確認**: 移動禁止ファイルは絶対に移動しない
2. **ツール動作確認**: Cursor/Claude Code動作確認
3. **Git履歴保持**: 移動はmvコマンドで実行

## ✨ 期待効果

- **プロフェッショナルな印象**: クリーンなルート
- **ツール互換性維持**: 必要な設定は全てルートに保持
- **将来の拡張性**: 整理された構造で成長可能