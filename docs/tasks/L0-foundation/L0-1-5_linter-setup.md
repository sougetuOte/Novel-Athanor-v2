# L0-1-5: リンター設定

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L0-1-5 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-1 |
| 参照仕様 | `docs/internal/03_QUALITY_STANDARDS.md` |

## 概要

ruff によるコードリンティング・フォーマット環境をセットアップする。

## 受け入れ条件

- [ ] `pyproject.toml` に ruff 設定が存在する
- [ ] `ruff check src` が正常に実行できる
- [ ] `ruff format src` が正常に実行できる
- [ ] リンティングエラーがない状態でパスする

## 技術的詳細

### pyproject.toml への追記

```toml
[tool.ruff]
target-version = "py310"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (black handles this)
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # assert is fine in tests

[tool.ruff.isort]
known-first-party = ["src"]
```

### リンティング方針

- `ruff` を使用（flake8 + isort + black の統合）
- 行長は 88 文字（black デフォルト）
- import ソートは isort 互換

## 実装メモ

- 2026-01-24: pyproject.toml に ruff 設定追加
- E, W, F, I, B, C4, UP ルールを有効化
- isort 互換設定、known-first-party = ["src"]
- `ruff check src` / `ruff format src --check` 終了コード 0 で成功

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
