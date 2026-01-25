# L3-1-1e: シーン→ファイル特定テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-1-1e |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-1-1c, L3-1-1d |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.5 |

## 概要

SceneResolver の統合テストを実装する。
L3-1-1b/c/d で実装した機能が連携して正しく動作することを確認する。

## 受け入れ条件

- [ ] SceneResolver 全メソッドのユニットテスト
- [ ] 統合テスト（フィクスチャ vault を使用）
- [ ] エッジケース（存在しないファイル、空のディレクトリ等）
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_scene_resolver.py`

### テストフィクスチャ

```python
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def mock_vault(tmp_path: Path) -> Path:
    """テスト用 vault 構造を作成"""
    vault = tmp_path / "test_vault"

    # ディレクトリ構造
    (vault / "episodes").mkdir(parents=True)
    (vault / "characters").mkdir()
    (vault / "world" / "地理").mkdir(parents=True)
    (vault / "_plot").mkdir()
    (vault / "_summary").mkdir()
    (vault / "_style_guides").mkdir()

    # ファイル作成
    (vault / "episodes" / "ep010.md").write_text(
        "---\ncharacters:\n  - アイラ\n  - ボブ\n---\n本文"
    )
    (vault / "characters" / "アイラ.md").write_text("# アイラ\n設定...")
    (vault / "characters" / "ボブ.md").write_text("# ボブ\n設定...")
    (vault / "world" / "魔法体系.md").write_text("# 魔法体系\n...")
    (vault / "world" / "地理" / "王都.md").write_text("# 王都\n...")
    (vault / "_plot" / "l1_theme.md").write_text("# テーマ\n...")
    (vault / "_plot" / "l2_chapter01.md").write_text("# 章目標\n...")
    (vault / "_plot" / "l3_ep010.md").write_text("# シーン構成\n...")
    (vault / "_summary" / "l1_overall.md").write_text("# 全体サマリ\n...")
    (vault / "_style_guides" / "default.md").write_text("# スタイル\n...")

    return vault
```

### テストケース一覧

#### 基本解決テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | resolve_episode_path() 正常 | エピソードファイル存在 |
| 2 | resolve_episode_path() 不在 | ファイルなし |
| 3 | resolve_plot_paths() 全存在 | L1/L2/L3 全て |
| 4 | resolve_plot_paths() 部分 | L3 のみ存在 |
| 5 | resolve_summary_paths() 全存在 | L1/L2/L3 全て |
| 6 | resolve_style_guide_path() | デフォルトスタイル |

#### キャラクター特定テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 7 | identify_characters() frontmatter | YAML形式 |
| 8 | identify_characters() wikilink | `[[characters/名前]]` |
| 9 | identify_characters() 存在しないキャラ | 警告付きでスキップ |
| 10 | list_all_characters() | 全キャラ列挙 |

#### 世界観特定テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 11 | identify_world_settings() | 通常パターン |
| 12 | identify_world_settings() サブディレクトリ | 階層対応 |
| 13 | list_all_world_settings() | 再帰列挙 |

#### 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 14 | resolve_all() 完全 | 全パス解決 |
| 15 | resolve_all() 部分 | 一部不在 |
| 16 | 複合シナリオ | キャラ+世界観+プロット |

#### エッジケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 17 | 空の vault | ディレクトリのみ |
| 18 | 存在しない vault | エラーハンドリング |
| 19 | 不正なエピソードID | ValueError |
| 20 | 特殊文字を含む名前 | 日本語、スペース等 |

### テスト実装例

```python
class TestSceneResolverIntegration:
    """SceneResolver 統合テスト"""

    def test_resolve_all_complete(self, mock_vault: Path):
        """全パスが解決されるケース"""
        resolver = SceneResolver(mock_vault)
        scene = SceneIdentifier(
            episode_id="ep010",
            chapter_id="chapter01",
            current_phase="arc_1"
        )

        result = resolver.resolve_all(scene)

        assert result.episode is not None
        assert result.episode.name == "ep010.md"
        assert result.plot_l1 is not None
        assert result.plot_l2 is not None
        assert result.plot_l3 is not None
        assert result.style_guide is not None

    def test_identify_characters_from_frontmatter(self, mock_vault: Path):
        """frontmatter からキャラクター特定"""
        resolver = SceneResolver(mock_vault)
        scene = SceneIdentifier(episode_id="ep010")

        characters = resolver.identify_characters(scene)

        assert len(characters) == 2
        assert any(p.name == "アイラ.md" for p in characters)
        assert any(p.name == "ボブ.md" for p in characters)
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
