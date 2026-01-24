# L0-1-4: 型チェック設定

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L0-1-4 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L0-1-1 |
| 参照仕様 | `docs/internal/03_QUALITY_STANDARDS.md` |

## 概要

mypy または pyright による静的型チェック環境をセットアップする。

## 受け入れ条件

- [ ] `pyproject.toml` に mypy 設定が存在する
- [ ] `mypy src` が正常に実行できる
- [ ] 型エラーがない状態でパスする

## 技術的詳細

### pyproject.toml への追記

```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### 型チェック方針

- `strict` モードを採用
- 新規コードは必ず型アノテーションを付ける
- 外部ライブラリの型スタブがない場合は `ignore_missing_imports`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
