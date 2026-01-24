# ADR-0004: データ形式とObsidian統合

## メタ情報
| 項目 | 内容 |
|------|------|
| ステータス | Accepted |
| 日付 | 2026-01-24 |
| 意思決定者 | プロジェクトオーナー |
| 関連ADR | [ADR-0001](./0001-three-project-integration.md) |

## コンテキスト

### 背景
小説執筆支援システムでは、設定資料、キャラクター情報、プロット、本文など多様なデータを管理する必要がある。データ形式の選択は、システム全体の使いやすさと拡張性に大きく影響する。

Novel-Athanor（ユーザー作）では既に Obsidian との統合が行われており、この資産を活かしたい。

### 制約条件
- Claude Code (CLI) での処理が容易であること
- 人間が直接編集可能であること
- バージョン管理（Git）と相性が良いこと
- 既存の Obsidian ワークフローを活かしたい

### 要求事項
- 構造化データと自然文の両方を扱える
- メタデータとコンテンツを分離
- 相互リンク機能
- 検索性

## 検討した選択肢

### Option A: JSON / YAML のみ
**概要**: 全データを構造化ファイルで管理

**メリット**:
- 機械処理が容易
- スキーマ検証が可能

**デメリット**:
- 人間の編集が困難
- 長文コンテンツに不向き

### Option B: Markdown のみ
**概要**: 全データを Markdown で管理

**メリット**:
- 人間に読みやすい
- 既存エディタで編集可能

**デメリット**:
- 構造化データの表現が困難
- メタデータの一貫性が保てない

### Option C: Markdown + YAML Frontmatter
**概要**: メタデータは YAML frontmatter、コンテンツは Markdown

```markdown
---
type: character
name: 主人公
visibility: 3
tags: [protagonist, hero]
---

# 主人公

## プロフィール
...
```

**メリット**:
- 構造化データと自然文の両立
- Obsidian 完全互換
- Git diff が見やすい

**デメリット**:
- パース処理が必要

### Option D: データベース（SQLite）
**概要**: リレーショナルDBでデータ管理

**メリット**:
- 複雑なクエリが可能
- データ整合性

**デメリット**:
- Git との相性が悪い
- 人間の直接編集が困難
- Obsidian 統合が困難

## 3 Agents Analysis

### [Affirmative] 推進者の視点
> 最高の結果はどうなるか？どうすれば実現できるか？

- Markdown + YAML は「両方の良いとこ取り」
- Obsidian のグラフビュー、バックリンクが活用できる
- ユーザーは既に Obsidian を使っている可能性が高い
- Git での差分管理が容易で、変更履歴が追いやすい
- 将来的に別ツールへの移行も容易（ロックインなし）

### [Critical] 批判者の視点
> 最悪の場合どうなるか？何が壊れるか？

- frontmatter のスキーマが崩れるリスク
- パース処理の実装コスト
- 大量ファイル時のパフォーマンス
- Obsidian に依存しすぎると、非 Obsidian ユーザーが困る

### [Mediator] 調停者の視点
> 今、我々が取るべき最善のバランスは何か？

- Option C（Markdown + YAML frontmatter）を採用
- スキーマは厳格すぎず、必須フィールドのみ検証
- Obsidian は「推奨」だが「必須」ではない設計
- パフォーマンス対策は必要に応じて後から追加

## 決定

**採用**: Option C（Markdown + YAML Frontmatter）

### 決定理由
- Novel-Athanor の既存資産を最大限活用
- 人間と機械の両方にフレンドリー
- Obsidian エコシステムの恩恵を受けられる
- ベンダーロックインなし

### 却下理由
- **Option A**: 長文コンテンツに不向き
- **Option B**: メタデータ管理が困難
- **Option D**: Git・Obsidian との相性が悪い

## 影響

### ポジティブな影響
- 既存 Obsidian ユーザーの参入障壁が低い
- バージョン管理が容易
- 将来の拡張性が高い

### ネガティブな影響
- frontmatter パーサーの実装が必要（緩和策: 既存ライブラリを活用）

### 影響を受けるコンポーネント
- `docs/specs/novel-generator-v2/03_data-model.md`: 仕様定義済み
- `src/core/data/`: パーサー実装予定
- 全データファイル: この形式に統一

## 実装計画

### フェーズ1: パーサー実装
- [ ] YAML frontmatter パーサー
- [ ] スキーマ検証（必須フィールドのみ）
- [ ] Markdown 処理

### フェーズ2: データ操作
- [ ] CRUD 操作
- [ ] インデックス生成
- [ ] 検索機能

### フェーズ3: Obsidian 連携
- [ ] リンク解析
- [ ] グラフデータ生成

## 検証方法
- 既存 Obsidian vault との互換性テスト
- 1000 ファイル以上でのパフォーマンステスト
- Git diff の可読性確認

## 参考資料
- `docs/specs/novel-generator-v2/03_data-model.md`: データモデル仕様
- Obsidian: https://obsidian.md/
- YAML frontmatter: https://jekyllrb.com/docs/front-matter/
