# L1-1-1: YAML frontmatter パーサー実装

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-1-1 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 5 |

## 概要

Markdown ファイルの YAML frontmatter を解析し、構造化データとして抽出するパーサーを実装する。

## 受け入れ条件

- [ ] `parse_frontmatter(content: str) -> tuple[dict, str]` 関数が存在する
- [ ] 正常な frontmatter を辞書として返す
- [ ] frontmatter がない場合は空辞書を返す
- [ ] 不正な YAML の場合は `ParseError` を発生させる
- [ ] ユニットテストが存在する

## 技術的詳細

### 入力例

```markdown
---
type: episode
title: "エピソード1"
episode_number: 1
---

# 本文
```

### 出力例

```python
frontmatter = {
    "type": "episode",
    "title": "エピソード1",
    "episode_number": 1
}
body = "\n# 本文\n"
```

### 実装方針

- `python-frontmatter` ライブラリを使用
- カスタム例外 `ParseError` を定義

### ファイル配置

- `src/core/parsers/frontmatter.py`
- `tests/core/parsers/test_frontmatter.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
