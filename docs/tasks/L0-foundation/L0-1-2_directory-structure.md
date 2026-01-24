# L0-1-2: ディレクトリ構造作成

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L0-1-2 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-1 |
| 参照仕様 | `docs/internal/00_PROJECT_STRUCTURE.md`, `docs/specs/novel-generator-v2/02_architecture.md` Section 6 |

## 概要

仕様書に基づいたソースコードのディレクトリ構造を作成する。

## 受け入れ条件

- [ ] 以下のディレクトリ構造が存在する:
  ```
  src/
  ├── core/           # コアモジュール
  │   ├── __init__.py
  │   ├── models/     # データモデル
  │   ├── parsers/    # パーサー
  │   └── repositories/  # リポジトリ
  ├── agents/         # エージェント実装
  │   └── __init__.py
  └── cli/            # CLIインターフェース
      └── __init__.py
  ```
- [ ] 以下のテストディレクトリ構造が存在する:
  ```
  tests/
  ├── __init__.py
  ├── core/
  │   ├── __init__.py
  │   ├── models/
  │   ├── parsers/
  │   └── repositories/
  └── agents/
      └── __init__.py
  ```
- [ ] 各 `__init__.py` が適切に配置されている
- [ ] `python -c "import src"` が成功する

## 技術的詳細

### ディレクトリ説明

| ディレクトリ | 責務 |
|-------------|------|
| `src/core/models/` | Pydantic データモデル |
| `src/core/parsers/` | YAML/Markdown パーサー |
| `src/core/repositories/` | データ永続化 |
| `src/agents/` | エージェント実装 |
| `src/cli/` | CLIコマンド |

## 実装メモ

- 2026-01-24: L0-1-1と統合して実装
- src/ 配下: core/models, core/parsers, core/repositories, agents, cli
- tests/ 配下: 同等の構造を作成
- 各ディレクトリに __init__.py を配置
- import テスト成功

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
