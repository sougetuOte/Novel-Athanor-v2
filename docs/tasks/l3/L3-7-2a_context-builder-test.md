# L3-7-2a: ContextBuilder 統合テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-7-2a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-7-1b〜L3-7-1d |
| フェーズ | Phase G（統合テスト） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 3 |

## 概要

ContextBuilder 全体の統合テストを実装する。
全コンポーネントを連携させた E2E テスト。

## 受け入れ条件

- [ ] build_context() の E2E テスト
- [ ] get_foreshadow_instructions() の E2E テスト
- [ ] get_forbidden_keywords() の E2E テスト
- [ ] 全機能連携テスト
- [ ] パフォーマンステスト
- [ ] エラーリカバリテスト
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_context_builder_integration.py`（新規）

### テストフィクスチャ

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.core.services.visibility_controller import (
    VisibilityController,
    AIVisibilityLevel,
)
from src.core.services.foreshadowing_manager import ForeshadowingManager
from src.core.services.expression_filter import ExpressionFilter

from src.core.context.context_builder import (
    ContextBuilder,
    ContextBuilderConfig,
    BuildResult,
)
from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.foreshadow_instruction import InstructionAction


@pytest.fixture
def complete_vault(tmp_path: Path) -> Path:
    """完全なテスト vault 構造"""
    vault = tmp_path / "test_vault"

    # ディレクトリ構造
    (vault / "episodes" / "chapter01").mkdir(parents=True)
    (vault / "characters").mkdir()
    (vault / "world").mkdir()
    (vault / "_plot").mkdir()
    (vault / "_summary").mkdir()
    (vault / "_style_guides").mkdir()
    (vault / "_ai_control").mkdir()
    (vault / "_foreshadowing").mkdir()

    # エピソードファイル
    (vault / "episodes" / "chapter01" / "ep010.md").write_text("""---
title: 対決前夜
characters:
  - アイラ
  - 主人公
world_settings:
  - 古代王国
  - 魔法体系
---

# 対決前夜

明日、全てが決まる。
""")

    # プロットファイル
    (vault / "_plot" / "l1_theme.md").write_text("# テーマ\n復讐と赦しの物語")
    (vault / "_plot" / "l2_chapter01.md").write_text("# 章目標\n主人公の決意")
    (vault / "_plot" / "l3_ep010.md").write_text("# シーン構成\n対決前夜の緊張感")

    # サマリファイル
    (vault / "_summary" / "l1_overall.md").write_text("# 全体\nこれまでの物語")
    (vault / "_summary" / "l2_chapter01.md").write_text("# 章\n第1章の要約")
    (vault / "_summary" / "l3_ep009.md").write_text("# 直前\n前回のあらすじ")

    # キャラクターファイル
    (vault / "characters" / "アイラ.md").write_text("""---
name: アイラ
visibility:
  ai_level: AWARE
phase_visibility:
  initial: public
  arc_1: public
  finale: full
---

## 基本情報
謎の少女。不思議な力を持つ。

## 秘密
実は王族の血を引いている。
""")

    (vault / "characters" / "主人公.md").write_text("""---
name: 主人公
visibility:
  ai_level: USE
phase_visibility:
  initial: full
  arc_1: full
  finale: full
---

## 基本情報
復讐を誓う戦士。師匠の仇を追っている。

## 詳細
幼少期に師匠と出会い、剣術を学んだ。
""")

    # 世界観ファイル
    (vault / "world" / "古代王国.md").write_text("""---
name: 古代王国
visibility:
  ai_level: AWARE
---

## 基本情報
かつて栄えた王国。

## 秘密
滅亡の真因は内部の裏切り。
""")

    (vault / "world" / "魔法体系.md").write_text("""---
name: 魔法体系
visibility:
  ai_level: USE
---

## 基本情報
この世界の魔法システム。

## 詳細
元素を操る力として知られている。
""")

    # スタイルガイド
    (vault / "_style_guides" / "default.md").write_text("""# スタイルガイド

## 視点
三人称視点

## 文体
やや硬め、叙情的
""")

    # AI制御ファイル
    (vault / "_ai_control" / "visibility.yaml").write_text("""
global_forbidden_keywords:
  - 真の名前
  - 最終兵器
""")

    (vault / "_ai_control" / "forbidden_keywords.txt").write_text("""
# グローバル禁止キーワード
世界の終末
神の力
""")

    # 伏線定義
    (vault / "_foreshadowing" / "FS-001.yaml").write_text("""
id: FS-001
name: アイラの王族の血筋
status: registered
plant_scene: ep010
reinforce_scenes: []
reveal_scene: ep030
allowed_expressions:
  - 気高い雰囲気
  - 見覚えのある光
forbidden_keywords:
  - 王族
  - 血筋
importance: critical
""")

    return vault


@pytest.fixture
def mock_l2_services() -> tuple[Mock, Mock, Mock]:
    """L2 サービスのモック"""
    # VisibilityController
    visibility = Mock(spec=VisibilityController)
    visibility.get_character_visibility.side_effect = lambda name: {
        "アイラ": AIVisibilityLevel.AWARE,
        "主人公": AIVisibilityLevel.USE,
    }.get(name, AIVisibilityLevel.KNOW)

    visibility.get_setting_visibility.side_effect = lambda name: {
        "古代王国": AIVisibilityLevel.AWARE,
        "魔法体系": AIVisibilityLevel.USE,
    }.get(name, AIVisibilityLevel.KNOW)

    # ForeshadowingManager
    foreshadowing = Mock(spec=ForeshadowingManager)
    fs1 = Mock()
    fs1.id = "FS-001"
    fs1.status = "registered"
    fs1.plant_scene = "ep010"
    fs1.reinforce_scenes = []
    fs1.allowed_expressions = ["気高い雰囲気", "見覚えのある光"]
    fs1.forbidden_keywords = ["王族", "血筋"]
    fs1.plant_hint = "王族の血筋を匂わせる"
    fs1.importance = "critical"

    foreshadowing.list_all.return_value = [fs1]
    foreshadowing.get.return_value = fs1

    # ExpressionFilter
    expression = Mock(spec=ExpressionFilter)
    expression.get_forbidden_keywords.return_value = ["禁じられた言葉"]

    return visibility, foreshadowing, expression


@pytest.fixture
def scene() -> SceneIdentifier:
    """テスト用シーン"""
    return SceneIdentifier(
        episode_id="ep010",
        chapter_id="chapter01",
        current_phase="arc_1",
    )
```

### テストケース一覧

#### build_context() E2E テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | build_context() 完全フロー | 全コンポーネント統合 |
| 2 | build_context() L2連携 | 全L2サービス使用 |
| 3 | build_context() 警告収集 | 警告が伝搬する |
| 4 | build_context() プロット収集 | L1/L2/L3 |
| 5 | build_context() サマリ収集 | L1/L2/L3 |
| 6 | build_context() キャラ収集 | フェーズフィルタ適用 |
| 7 | build_context() 世界観収集 | フェーズフィルタ適用 |
| 8 | build_context() 可視性フィルタ | HIDDEN 除外 |

#### get_foreshadow_instructions() E2E テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 9 | 指示書生成 | PLANT 検出 |
| 10 | プロンプト形式 | 正しいフォーマット |
| 11 | キャッシュ動作 | 再計算しない |
| 12 | アクティブ伏線 | IDリスト取得 |

#### get_forbidden_keywords() E2E テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 13 | キーワード収集 | 全ソース統合 |
| 14 | ソース別取得 | デバッグ情報 |
| 15 | テキストチェック | 禁止検出 |
| 16 | プロンプト形式 | 正しいフォーマット |

#### パフォーマンステスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 17 | 初回ビルド | 500ms以内 |
| 18 | キャッシュ使用 | 50ms以内 |
| 19 | 大量キャラ | 20キャラクターでも1秒以内 |

#### エラーリカバリテスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 20 | L2サービス障害 | Graceful Degradation |
| 21 | ファイル欠損 | 警告のみで継続 |
| 22 | 不正YAML | エラーハンドリング |

### テスト実装例

```python
class TestContextBuilderE2E:
    """ContextBuilder E2E テスト"""

    def test_complete_build_flow(
        self,
        complete_vault: Path,
        mock_l2_services: tuple,
        scene: SceneIdentifier,
    ):
        """全コンポーネントを使った完全ビルド"""
        visibility, foreshadowing, expression = mock_l2_services

        config = ContextBuilderConfig(
            vault_root=complete_vault,
            enable_visibility_filter=True,
            enable_foreshadowing=True,
        )

        builder = ContextBuilder(
            config=config,
            visibility_controller=visibility,
            foreshadowing_manager=foreshadowing,
            expression_filter=expression,
        )

        # ビルド実行
        result = builder.build_context(scene)

        # コンテキスト検証
        assert result.context is not None
        assert result.context.scene_id == "ep010"
        assert result.context.current_phase == "arc_1"

        # プロット
        assert result.context.plot_l1 is not None
        assert "復讐と赦し" in result.context.plot_l1

        # キャラクター（可視性フィルタ適用後）
        assert "主人公" in result.context.characters
        # アイラは AWARE なので基本情報のみ
        if "アイラ" in result.context.characters:
            assert "秘密" not in result.context.characters["アイラ"] or \
                   "王族" not in result.context.characters["アイラ"]

        # 伏線指示書
        assert result.instructions is not None
        plant_inst = result.instructions.get_for_foreshadowing("FS-001")
        assert plant_inst is not None
        assert plant_inst.action == InstructionAction.PLANT

        # 禁止キーワード
        assert len(result.forbidden_keywords) > 0
        assert "王族" in result.forbidden_keywords
        assert "真の名前" in result.forbidden_keywords

    def test_build_without_l2_services(
        self,
        complete_vault: Path,
        scene: SceneIdentifier,
    ):
        """L2サービスなしでもビルド可能"""
        config = ContextBuilderConfig(
            vault_root=complete_vault,
            enable_visibility_filter=False,
            enable_foreshadowing=False,
        )

        builder = ContextBuilder(config=config)

        result = builder.build_context(scene)

        # 基本コンテキストは取得できる
        assert result.context is not None
        assert result.context.plot_l1 is not None

        # L2関連は空
        assert result.instructions is None or len(result.instructions.instructions) == 0
        assert len(result.forbidden_keywords) == 0

    def test_graceful_degradation_on_l2_failure(
        self,
        complete_vault: Path,
        scene: SceneIdentifier,
    ):
        """L2サービス障害時の Graceful Degradation"""
        # 例外を投げるモック
        failing_visibility = Mock(spec=VisibilityController)
        failing_visibility.get_character_visibility.side_effect = Exception("L2 Error")

        failing_foreshadowing = Mock(spec=ForeshadowingManager)
        failing_foreshadowing.list_all.side_effect = Exception("L2 Error")

        config = ContextBuilderConfig(
            vault_root=complete_vault,
            enable_visibility_filter=True,
            enable_foreshadowing=True,
        )

        builder = ContextBuilder(
            config=config,
            visibility_controller=failing_visibility,
            foreshadowing_manager=failing_foreshadowing,
        )

        # エラーでも継続
        result = builder.build_context(scene)

        # 基本コンテキストは取得できる
        assert result.context is not None

        # 警告が記録されている
        assert len(result.warnings) > 0


class TestContextBuilderPerformance:
    """パフォーマンステスト"""

    def test_initial_build_within_timeout(
        self,
        complete_vault: Path,
        mock_l2_services: tuple,
        scene: SceneIdentifier,
    ):
        """初回ビルドが500ms以内"""
        import time

        visibility, foreshadowing, expression = mock_l2_services

        config = ContextBuilderConfig(vault_root=complete_vault)
        builder = ContextBuilder(
            config=config,
            visibility_controller=visibility,
            foreshadowing_manager=foreshadowing,
            expression_filter=expression,
        )

        start = time.time()
        _ = builder.build_context(scene)
        elapsed = time.time() - start

        assert elapsed < 0.5  # 500ms

    def test_cached_build_faster(
        self,
        complete_vault: Path,
        mock_l2_services: tuple,
        scene: SceneIdentifier,
    ):
        """キャッシュ使用時は50ms以内"""
        import time

        visibility, foreshadowing, expression = mock_l2_services

        config = ContextBuilderConfig(vault_root=complete_vault)
        builder = ContextBuilder(
            config=config,
            visibility_controller=visibility,
            foreshadowing_manager=foreshadowing,
            expression_filter=expression,
        )

        # 初回ビルド（キャッシュ構築）
        _ = builder.build_context(scene)

        # 2回目（キャッシュ使用）
        start = time.time()
        _ = builder.get_foreshadow_instructions(scene)
        _ = builder.get_forbidden_keywords(scene)
        elapsed = time.time() - start

        assert elapsed < 0.05  # 50ms


class TestContextBuilderPromptOutput:
    """プロンプト出力テスト"""

    def test_foreshadow_prompt_format(
        self,
        complete_vault: Path,
        mock_l2_services: tuple,
        scene: SceneIdentifier,
    ):
        """伏線指示のプロンプト形式"""
        visibility, foreshadowing, expression = mock_l2_services

        config = ContextBuilderConfig(vault_root=complete_vault)
        builder = ContextBuilder(
            config=config,
            foreshadowing_manager=foreshadowing,
        )

        prompt = builder.get_foreshadow_instructions_as_prompt(scene)

        assert "## 伏線指示" in prompt
        assert "FS-001" in prompt
        assert "初回設置" in prompt
        assert "気高い雰囲気" in prompt
        assert "王族" in prompt  # 禁止表現として

    def test_forbidden_prompt_format(
        self,
        complete_vault: Path,
        mock_l2_services: tuple,
        scene: SceneIdentifier,
    ):
        """禁止キーワードのプロンプト形式"""
        visibility, foreshadowing, expression = mock_l2_services

        config = ContextBuilderConfig(vault_root=complete_vault)
        builder = ContextBuilder(
            config=config,
            foreshadowing_manager=foreshadowing,
        )

        prompt = builder.get_forbidden_keywords_as_prompt(scene)

        assert "## 禁止キーワード" in prompt
        assert "絶対に使用しないでください" in prompt
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
