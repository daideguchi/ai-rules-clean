# 🏗️ プロジェクト構造・ファイル配置ルール

## 📊 最終構造（Gemini + o3 統合版）

```
ai-memory-inheritance-system/
├── pyproject.toml              # プロジェクト設定・依存関係
├── README.md                   # プロジェクト概要・セットアップ
├── .pre-commit-config.yaml     # コード品質チェック
├── .gitignore                  # Git除外設定
├── LICENSE                     # ライセンス
├── Makefile                    # 自動化コマンド
│
├── src/                        # 🎯 インポート可能なPythonパッケージ
│   ├── project_paths.py        # パス設定（テンプレート化対応）
│   └── ai_memory_system/       # メインパッケージ
│       ├── __init__.py         # パッケージ初期化
│       ├── data/               # データローダー・前処理
│       ├── models/             # モデル定義・学習ループ
│       ├── pipelines/          # エンドツーエンドワークフロー
│       └── utils/              # 汎用ヘルパー
│
├── agents/                     # 🤖 AIエージェントシステム
│   ├── executive/              # プレジデント・ボス
│   ├── workers/                # ワーカーエージェント
│   ├── coordination/           # エージェント連携
│   ├── memory-bridge/          # メモリブリッジ
│   └── integrations/           # 外部統合（MCP, Gemini）
│
├── memory/                     # 🧠 メモリ継承システム
│   ├── inheritance/            # セッション間継承
│   ├── persistence/            # 永続化メモリ
│   ├── recovery/               # 復旧システム
│   └── apis/                   # メモリアクセスAPI
│
├── config/                     # ⚙️ 設定管理
│   ├── agents/                 # エージェント設定
│   ├── system/                 # システム設定
│   └── deployment/             # デプロイメント設定
│
├── scripts/                    # 🔧 実行可能スクリプト
│   ├── automation/             # 自動化スクリプト
│   ├── validation/             # 検証スクリプト
│   ├── ai-management/          # AI管理
│   └── utilities/              # ユーティリティ
│
├── operations/                 # 🚀 運用・インフラ
│   ├── infrastructure/         # インフラ設定
│   ├── runtime-logs/           # 実行時ログ
│   ├── backup/                 # バックアップ
│   └── monitoring/             # モニタリング
│
├── docs/                       # 📚 ドキュメント
│   ├── optimization/           # 最適化関連
│   ├── recovery/               # 復旧関連
│   └── analysis/               # 分析結果
│
├── reports/                    # 📊 レポート・分析結果
├── requests/                   # 📤 外部リクエスト
├── env/                        # 🌍 環境設定テンプレート
├── runtime/                    # ⚡ 実行時データ（.gitignore対象）
└── tests/                      # 🧪 テスト

```

## 🎯 ファイル配置ルール（自動チェック対応）

### 1. **Python ファイル**
```
✅ src/           - インポート可能なモジュール
✅ scripts/       - 実行可能スクリプト  
✅ tests/         - テストファイル
❌ data/          - Pythonファイル禁止
❌ docs/          - 実行ファイル禁止（除く examples/）
```

### 2. **設定ファイル**
```
✅ config/        - YAML/JSON設定
✅ ルート          - pyproject.toml, .pre-commit-config.yaml のみ
❌ ルート散乱      - その他の設定ファイル禁止
```

### 3. **データファイル**
```
✅ data/raw/      - オリジナル不変データ
✅ data/processed/ - 前処理済みデータ
❌ ルート          - データファイル禁止
❌ src/           - データファイル禁止
```

## 🚀 命名規則（強制）

### ファイル命名
- **Pythonモジュール**: `snake_case.py`
- **設定ファイル**: `kebab-case.yaml`
- **データファイル**: `snake_case_2025-07-06.parquet`
- **ノートブック**: `01-exploration.ipynb`

### ディレクトリ命名
- **パッケージ**: `snake_case/`
- **機能別**: `kebab-case/`
- **複数語**: `multi-word-function/`

## 🛡️ テンプレート化対応

### 絶対パス禁止
```python
# ❌ 禁止
path = "./project"

# ✅ 推奨
from src.project_paths import PROJECT_ROOT
path = PROJECT_ROOT / "relative/path"
```

### 環境変数対応
```python
# デフォルト値付き環境変数
DATA_DIR = Path(os.getenv("AI_PROJECT_DATA", PROJECT_ROOT / "data"))
```

### 相対インポート
```python
# ✅ 推奨
from src.ai_memory_system.models import XGBRegressor

# ❌ 禁止
sys.path.append("/absolute/path")
```

## 🔍 自動チェック機能

### Pre-commit Hooks
1. **絶対パスチェック**: `scripts/validation/check-absolute-paths.sh`
2. **ファイル配置チェック**: `scripts/validation/check-file-placement.sh`
3. **コード品質**: black, flake8, mypy

### CI/CD 検証
- ファイル配置ルール違反検出
- 絶対パス使用検出
- インポートパス検証
- テストカバレッジ閾値（80%）

## 📏 発見可能性（find不要設計）

### 浅い階層維持
- インポート深度 ≤ 3レベル
- ディレクトリ内ファイル数 ≤ 8個

### 明確な再エクスポート
```python
# src/ai_memory_system/__init__.py
from .models import XGBRegressor, TransformerClassifier
from .pipelines import TrainingPipeline

__all__ = ["XGBRegressor", "TransformerClassifier", "TrainingPipeline"]
```

### レジストリパターン
```python
@register_model(name="xgb")
class XGBRegressor:
    pass

# 使用時
model = ModelRegistry.get("xgb")
```

## ✅ 実装チェックリスト

- [x] pyproject.toml作成（パッケージ化）
- [x] src/project_paths.py（パス管理）
- [x] .pre-commit-config.yaml（品質チェック）
- [x] 絶対パス修正完了
- [x] ファイル配置最適化
- [x] 自動検証スクリプト作成
- [x] ドキュメント整備

**この構造により、プロジェクトは高い保守性・発見可能性・テンプレート化対応を実現します。**