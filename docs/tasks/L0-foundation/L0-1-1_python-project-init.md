# L0-1-1: Python プロジェクト初期化

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L0-1-1 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | なし |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 5.1 |

## 概要

Pythonプロジェクトの基盤となる `pyproject.toml` を作成し、依存関係管理とビルド設定を行う。

## 受け入れ条件

- [ ] `pyproject.toml` がプロジェクトルートに存在する
- [ ] プロジェクト名: `novel-athanor-v2`
- [ ] Python バージョン: `>=3.10`
- [ ] 以下の依存関係が定義されている:
  - `pydantic>=2.0` (データモデル)
  - `pyyaml>=6.0` (YAML パーサー)
  - `python-frontmatter>=1.0` (frontmatter パーサー)
- [ ] 以下の開発依存関係が定義されている:
  - `pytest>=7.0`
  - `pytest-cov`
  - `mypy` または `pyright`
  - `ruff`
- [ ] `pip install -e .` が成功する

## 技術的詳細

### pyproject.toml 構成

```toml
[project]
name = "novel-athanor-v2"
version = "0.1.0"
description = "半自動小説生成システム"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "python-frontmatter>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "mypy",
    "ruff",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

## 実装メモ

- 2026-01-24: L0-1-2と統合して実装（pip install には src/ 構造が必要なため）
- pyproject.toml に pytest, mypy, ruff の設定も追加
- `pip install -e ".[dev]"` で開発依存関係も含めてインストール完了

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
