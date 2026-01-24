# レビュー依頼

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-24_004 |
| 日時 | 2026-01-24 |
| 依頼元 | claude-code |
| 種別 | code_review |
| Status | open |

## 対象範囲 (Scope)

**対象**:
- `docs/tasks/L0-foundation/` (3タスク)
- `docs/tasks/L1-data/` (16タスク)
- `src/core/` (実装コード)
- `tests/core/` (テストコード)

**背景・コンテキスト**:
L0-foundation と L1-data の P0 タスク（計19件）を TDD で実装完了しました。
個々のタスク完了時にはテストを通していますが、全体を統制した包括的なレビューが必要です。

## 依頼内容 (Request)

### レビュー観点（全て同等の優先度）

1. **タスク定義と実装の整合性**
   - 各タスクファイルの「受け入れ条件」が実装で満たされているか
   - 「技術的詳細」のクラス定義・メソッドが仕様通りか

2. **コード品質**
   - 命名規則の一貫性
   - エラーハンドリングの適切さ
   - 型ヒントの網羅性

3. **設計整合性**
   - DRY 原則の遵守
   - 責務の分離
   - 依存関係の方向

4. **テストカバレッジ**
   - 境界値・エラーケースの網羅
   - テストの可読性

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

### 参照すべきタスクファイル

**L0-foundation**:
- `L0-1-1_python-project-setup.md`
- `L0-1-2_directory-structure.md`
- `L0-1-3_testing-setup.md`

**L1-data**:
- `L1-1-1_yaml-parser.md` - `L1-1-4_parser-unit-tests.md`
- `L1-2-1_episode-model.md` - `L1-2-10_model-integration-tests.md`
- `L1-3-2_vault-path-resolver.md`
- `L1-4-1_base-repository.md` - `L1-4-5_repository-integration-tests.md`

## 添付・参考情報 (Attachments)

### 現在の品質指標

| 項目 | 結果 |
|------|------|
| テスト | 101件 全PASS |
| カバレッジ | 98% |
| mypy | エラーなし |
| ruff | エラーなし |

### 実装ファイル一覧

```
src/core/
├── models/
│   ├── episode.py
│   ├── character.py
│   ├── world_setting.py
│   ├── plot.py
│   └── summary.py
├── parsers/
│   ├── frontmatter.py
│   └── markdown.py
├── repositories/
│   ├── base.py
│   ├── episode.py
│   ├── character.py
│   └── world_setting.py
└── vault/
    └── path_resolver.py
```

### 参照仕様書

- `docs/specs/novel-generator-v2/03_data-model.md`

---

<!-- 回答は以下に追記してください -->
