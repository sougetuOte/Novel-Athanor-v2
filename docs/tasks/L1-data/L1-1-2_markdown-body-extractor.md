# L1-1-2: Markdown 本文抽出機能

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-1-2 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

Markdown ファイルから本文（frontmatter 以降）を抽出し、セクション単位で分割する機能を実装する。

## 受け入れ条件

- [ ] `extract_body(content: str) -> str` 関数が存在する
- [ ] `extract_sections(body: str) -> list[Section]` 関数が存在する
- [ ] 見出し（#, ##, ###）でセクション分割できる
- [ ] 各セクションに `title`, `level`, `content` が含まれる
- [ ] ユニットテストが存在する

## 技術的詳細

### Section 構造

```python
@dataclass
class Section:
    title: str
    level: int  # 1-6
    content: str
    start_line: int
    end_line: int
```

### 入力例

```markdown
# メインタイトル

導入文

## セクション1

セクション1の内容

## セクション2

セクション2の内容
```

### 出力例

```python
[
    Section(title="メインタイトル", level=1, content="導入文\n", ...),
    Section(title="セクション1", level=2, content="セクション1の内容\n", ...),
    Section(title="セクション2", level=2, content="セクション2の内容\n", ...),
]
```

### ファイル配置

- `src/core/parsers/markdown.py`
- `tests/core/parsers/test_markdown.py`

## 実装メモ

- 2026-01-24: TDD で実装
- Section dataclass を定義
- 正規表現で見出しを検出しセクション分割
- テスト9件全て PASS

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
