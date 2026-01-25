# L3-1-1a: SceneIdentifier データクラス定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-1-1a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | なし |
| 並列実行 | Phase A グループ（他データクラスと並列可） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 3.4 |

## 概要

シーンを一意に特定するための不変データクラスを定義する。
このクラスは L3 全体で「どのシーンのコンテキストを構築するか」を指定する際に使用される。

## 受け入れ条件

- [ ] `SceneIdentifier` が frozen dataclass である
- [ ] `episode_id` が必須フィールドである
- [ ] `sequence_id`, `chapter_id`, `current_phase` がオプショナルである
- [ ] `episode_id` が空の場合に `ValueError` を送出する
- [ ] ユニットテストが存在する（5件以上）

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/scene_identifier.py`
- テスト: `tests/core/context/test_scene_identifier.py`

### クラス定義

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SceneIdentifier:
    """シーンを一意に特定する識別子

    Attributes:
        episode_id: エピソード番号（必須）例: "010", "ep010"
        sequence_id: シーケンス番号（オプション）例: "seq_01"
        chapter_id: 章番号（オプション）例: "ch_03"
        current_phase: 現在のフェーズ（オプション）例: "arc_1_reveal"
    """

    episode_id: str
    sequence_id: Optional[str] = None
    chapter_id: Optional[str] = None
    current_phase: Optional[str] = None

    def __post_init__(self):
        if not self.episode_id:
            raise ValueError("episode_id is required")

    def __str__(self) -> str:
        parts = [f"ep:{self.episode_id}"]
        if self.sequence_id:
            parts.append(f"seq:{self.sequence_id}")
        if self.chapter_id:
            parts.append(f"ch:{self.chapter_id}")
        return "/".join(parts)
```

### テストケース

| No. | テストケース | 入力 | 期待結果 |
|-----|-------------|------|---------|
| 1 | episode_id のみ | `SceneIdentifier("010")` | 正常生成 |
| 2 | 全フィールド指定 | `SceneIdentifier("010", "seq_01", "ch_03", "arc_1")` | 正常生成 |
| 3 | episode_id が空文字 | `SceneIdentifier("")` | ValueError |
| 4 | episode_id が None | `SceneIdentifier(None)` | TypeError or ValueError |
| 5 | frozen確認 | `scene.episode_id = "020"` | FrozenInstanceError |
| 6 | __str__ 確認 | `str(SceneIdentifier("010", "seq_01"))` | "ep:010/seq:seq_01" |
| 7 | equality | 同値の2インスタンス | 等価 |

## 実装手順

1. `src/core/context/` ディレクトリ作成
2. `__init__.py` 作成
3. テストファイル作成（Red）
4. `scene_identifier.py` 実装（Green）
5. リファクタリング

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
