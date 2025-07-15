# 🤖 AI指示書ナビゲーション

**o3+Gemini統合提案による最適構造 - 定型業務最重要ファイル群**

## 📋 AI指示書アーキテクチャ

```
ai-instructions/
├── roles/              # AIの役割定義（不変のコア）
│   ├── president.md    # 🏛️ 組織管理・方向性決定・最終判断
│   ├── boss.md        # 👔 チームリーダー・タスク分配・進捗管理
│   └── worker.md      # 💻 実装・開発・技術作業
├── policies/           # 遵守すべき不変のルール
├── procedures/         # 特定タスクの標準手順書（頻繁に追加・更新）
└── templates/          # 定型出力のテンプレート
```

## 🔗 クイックアクセス

### 役割指示書（毎日使用）
- **プレジデント**: [`ai-instructions/roles/president.md`](ai-instructions/roles/president.md)
- **ボス**: [`ai-instructions/roles/boss.md`](ai-instructions/roles/boss.md)  
- **ワーカー**: [`ai-instructions/roles/worker.md`](ai-instructions/roles/worker.md)

## 🚨 アクセス性の重要性

**定型業務で毎回必要なファイル**は、検索不要でアクセスできるべきです：

❌ **以前の問題**: `src/ai/agents/president.md` （深い階層、検索必須）  
✅ **改善後**: `./PRESIDENT.md` （ルートレベル、直接アクセス）

## 📁 ファイル配置ルール

### 重要度に応じた配置
- **最重要（定型業務）**: ルートレベル
- **重要（参照頻度高）**: `docs/` 直下
- **中程度**: 適切なサブディレクトリ
- **低頻度**: 深い階層OK

### アクセス性の原則
1. **毎日使う** → ルート配置
2. **週次使用** → docs/ 配置  
3. **月次参照** → サブディレクトリ
4. **アーカイブ** → 深い階層

## 🔄 今後の運用

この改善により：
- プレジデント業務開始時に `./PRESIDENT.md` で即座アクセス
- ボス指示は `./BOSS.md` で確認
- ワーカー作業は `./WORKER.md` で参照

**検索不要、迷わない、効率的なAI運用を実現**