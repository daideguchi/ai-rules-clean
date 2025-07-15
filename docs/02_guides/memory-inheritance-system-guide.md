# 記憶継承システム運用ガイド

## システム概要
記憶継承システムは、78回のミス履歴を基に、リアルタイムでミスパターンを検出し、同じ間違いを二度と繰り返さないための統合システムです。

## 主要コンポーネント

### 1. Runtime Advisor（ミドルウェア層）
- **場所**: `src/memory/core/runtime_advisor.py`
- **機能**: 入力/出力のリアルタイム分析とミスパターン検出
- **検出パターン**: 虚偽報告、推測回答、ファイル散乱、絶対パス使用、確認回避

### 2. ミスパターンデータベース
- **場所**: `src/memory/persistent-learning/mistakes-database.json`
- **内容**: 78個の歴史的ミスパターンと防止策
- **更新**: 新しいミスパターンは自動的に追加

### 3. CI自動回帰テスト
- **場所**: `tests/mistake-prevention-ci.py`
- **成功率**: 100%（17/17テスト合格）
- **実行**: プッシュ時に自動実行

### 4. フック統合
- **場所**: `scripts/hooks/memory_inheritance_hook.py`
- **対象ツール**: Edit, Write, MultiEdit, Bash, Task
- **動作**: 危険パターン検出時に警告/ブロック

## 運用方法

### 日常の使用
1. **PRESIDENT宣言**: 作業開始前に必ず実行
2. **自動検出**: ツール使用時に自動でミスパターンを検出
3. **警告対応**: 警告が出た場合は推奨アクションに従う

### ミスパターン追加
1. 新しいミスを発見したら`mistakes-database.json`に追加
2. CIテストを実行して動作確認
3. 必要に応じてRuntime Advisorのパターンマッチングを更新

### モニタリング
- **ログ確認**: `runtime/ai_api_logs/runtime_advisor.log`
- **防止効果**: `python3 src/memory/core/runtime_advisor.py`でサマリー表示
- **フック動作**: `runtime/ai_api_logs/memory_inheritance_hook.log`

## トラブルシューティング

### フックがブロックする場合
1. PRESIDENT宣言を確認
2. 検出されたパターンを確認
3. 推奨アクションに従って修正

### 誤検出の場合
1. パターンマッチング規則を調整
2. 重要度（severity）を調整
3. CIテストで動作確認

## 効果測定
- 初期成功率: 88.24%
- 現在成功率: 100%
- 防止したミス: 累積でカウント中