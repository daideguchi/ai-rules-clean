# 間違い防止トラッカー

**目的**: 同じ失敗を二度と繰り返さない確実な仕組み

## 📊 失敗履歴

### 2025-07-07: Gemini API エラー
**失敗内容**:
1. CLI引数 `-c` を設定ファイルと誤解
2. 存在しないモデル名 `gemini-2.0-flash-latest` 使用
3. クオータ制限でエラー

**実装した対策**:
- [x] `docs/03_processes/ai-api-error-prevention.md` 作成
- [x] `scripts/utilities/ai-api-check.sh` 実装
- [x] エラーログシステム構築

**検証**:
- [ ] 次回API使用時にチェックスクリプト実行
- [ ] 1週間後に対策有効性確認

## 🔄 対策の実効性確認

### 物理的強制メカニズム
1. **API実行前チェック必須**
   ```bash
   # 今後のAPI実行時は必ずこれを先に実行
   ./scripts/utilities/ai-api-check.sh
   ```

2. **エラー自動記録**
   ```bash
   # エラー発生時の自動ログ
   source runtime/ai_api_logs/error_logger.sh
   log_api_error "エラー内容" "コマンド"
   ```

3. **週次レビュー強制**
   ```bash
   # 毎週の失敗パターン確認
   ./scripts/utilities/weekly-mistake-review.sh
   ```

## 📋 次に追加すべき対策

### 未実装の重要対策
1. **ホックシステム統合**
   - AI API実行時に自動チェック起動

2. **失敗パターンDB**
   - 過去の全失敗を検索可能に

3. **自動警告システム**
   - 危険なコマンドパターンの検出

### 実装予定
- [ ] pre-commit hookにAPI チェック統合
- [ ] 失敗パターンの自動検索機能
- [ ] 月次での対策効果測定

---

**重要**: このトラッカーが更新されていない = 対策が機能していない証拠
