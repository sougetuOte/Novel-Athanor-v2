# レビュー依頼

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-25_001 |
| 日時 | 2026-01-25 |
| 依頼元 | claude-code |
| 種別 | code_review / refactor |
| Status | open |
| 前提 | 2026-01-24_004, 2026-01-24_005 完了 |

## 対象範囲 (Scope)

**対象（今回追加分）**:
- `src/core/models/foreshadowing.py` - 伏線管理モデル
- `src/core/models/ai_visibility.py` - AI可視性制御モデル
- `src/core/models/secret.py` - 秘密情報モデル
- `src/core/models/style.py` - スタイルガイド/プロファイルモデル
- `src/core/vault/init.py` - Vault 初期化
- `src/core/parsers/obsidian_link.py` - Obsidian リンクパーサー
- `src/core/repositories/foreshadowing.py` - 伏線リポジトリ
- 対応するテストファイル（`tests/core/` 以下）

**背景・コンテキスト**:
L1-data レイヤーの P0 タスク完了後、残りの P1/P2 タスク（8件）を TDD で実装完了しました。
これにより **L1 レイヤーが全て完了** し、L2（AI情報制御レイヤー）に進む準備が整いました。

今回実装したタスク:
| タスクID | 内容 | 優先度 |
|----------|------|--------|
| L1-1-3 | パースエラーフォールバック | P1 |
| L1-2-6 | Foreshadowing モデル | P1 |
| L1-2-7 | AIVisibility モデル完全版 | P1 |
| L1-2-8 | Secret モデル | P1 |
| L1-2-9 | StyleGuide/StyleProfile モデル | P2 |
| L1-3-1 | Vault 初期化スクリプト | P1 |
| L1-3-3 | Obsidian リンクパーサー | P1 |
| L1-4-4 | Foreshadowing リポジトリ | P1 |

## 依頼内容 (Request)

### 1. 全体レビュー

今回実装したコードについて、以下の観点でレビューをお願いします：

**コード品質**:
- Pythonic なコーディングスタイル（PEP 8, PEP 20）
- 可読性・保守性
- 命名規則の一貫性
- docstring の品質

**設計品質**:
- 既存コード（P0タスク分）との整合性
- Pydantic モデルの設計パターン
- SOLID 原則の遵守
- 将来の拡張性（L2 レイヤーとの接続を見据えて）

**テスト品質**:
- 境界値・エラーケースの網羅性
- テストの可読性・保守性

### 2. リファクタリング提案

以下の既知の問題について、改善案をお願いします：

**mypy エラー（4件）**:
```
src\core\models\ai_visibility.py:51: error: Missing type parameters for generic type "dict"
src\core\repositories\foreshadowing.py:35: error: Missing type parameters for generic type "dict"
src\core\repositories\foreshadowing.py:45: error: Missing type parameters for generic type "dict"
src\core\repositories\foreshadowing.py:54: error: Missing type parameters for generic type "dict"
```

**ruff 警告（1件）**:
```
src\core\models\ai_visibility.py:51: UP007 Use `X | Y` for type annotations
```

### 3. L2 レイヤー準備確認

L2（AI情報制御レイヤー）実装に向けて、L1 の設計で問題になりそうな点があれば指摘してください：

- `AIVisibility` モデルと L2-1（Visibility Controller）の接続
- `Foreshadowing` モデルと L2-3（Foreshadowing Manager）の接続
- `Secret` モデルと L2-2（Expression Filter）の接続

## 添付・参考情報 (Attachments)

### 現在の品質指標

| 項目 | 結果 |
|------|------|
| テスト | 202件 全PASS |
| カバレッジ | 98% |
| mypy | 4 エラー（型パラメータ未指定） |
| ruff | 1 警告（Union → \| 推奨） |

### 実装ファイル一覧（今回追加分）

```
src/core/
├── models/
│   ├── foreshadowing.py   # NEW: 伏線管理（Chekhov's Gun Tracker）
│   ├── ai_visibility.py   # NEW: AI可視性制御（4段階）
│   ├── secret.py          # NEW: エンティティ固有秘密情報
│   └── style.py           # NEW: スタイルガイド/プロファイル
├── parsers/
│   └── obsidian_link.py   # NEW: [[link]] 記法パーサー
├── repositories/
│   └── foreshadowing.py   # NEW: YAML レジストリ形式リポジトリ
└── vault/
    └── init.py            # NEW: Vault 初期化
```

### テストファイル一覧（今回追加分）

```
tests/core/
├── models/
│   ├── test_foreshadowing.py   # 19 tests
│   ├── test_ai_visibility.py   # 16 tests
│   ├── test_secret.py          # 9 tests
│   └── test_style.py           # 12 tests
├── parsers/
│   └── test_obsidian_link.py   # 19 tests
├── repositories/
│   └── test_foreshadowing.py   # 9 tests
└── vault/
    └── test_init.py            # 11 tests
```

### 主要な設計決定

1. **Foreshadowing モデル**: 伏線の状態遷移（registered → planted → growing → ready → harvested/abandoned）を Enum で表現。Subtlety レベル（1-10）で AI への露出度を制御。

2. **AIVisibility モデル**: 4段階可視性（HIDDEN=0, AWARE=1, KNOW=2, USE=3）を IntEnum で定義。セクション単位・エンティティ単位での可視性設定をサポート。

3. **Secret モデル**: 禁止キーワード + 許可表現パターンを保持。重要度（CRITICAL/HIGH/MEDIUM/LOW）に応じた類似度閾値調整機能。

4. **ForeshadowingRepository**: 他のリポジトリ（Markdown ファイル形式）と異なり、YAML レジストリ形式（`_foreshadowing/registry.yaml`）を採用。一元管理による状態追跡の容易さを優先。

### 参照仕様書

- `docs/specs/novel-generator-v2/03_data-model.md`
- `docs/specs/novel-generator-v2/04_ai-information-control.md`
- `docs/tasks/implementation-backlog.md`

### 仮想環境の使用方法

```bash
# プロジェクトディレクトリで実行
cd C:\work5\Novel-Athanor-v2

# 依存関係インストール（dev含む）
uv pip install -e ".[dev]"

# テスト実行
uv run python -m pytest tests/ -v

# 型チェック
uv run python -m mypy src/ --show-error-codes

# リンター
uv run python -m ruff check src/

# カバレッジ付きテスト
uv run python -m pytest tests/ --cov=src --cov-report=term-missing
```

### 期待するアウトプット

1. **問題点のリスト**（Critical/Warning/Info）
2. **リファクタリング提案**（優先度付き、コード例があれば尚良）
3. **L2 実装への推奨事項**
4. **総合評価**（A/B/C/D）

---

<!-- 回答は別ファイル 2026-01-25_001_review-response-antigravity.md に記載してください -->
