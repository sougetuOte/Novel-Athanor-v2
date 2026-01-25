# L3-6-1d: 可視性統合テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-6-1d |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-6-1a〜L3-6-1c |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/04_ai-information-control.md` |

## 概要

可視性システム全体の統合テストを実装する。
VisibilityAwareContext → VisibilityFilteringService → HintCollector の
連携動作を検証。

## 受け入れ条件

- [ ] VisibilityFilteringService の統合テスト
- [ ] HintCollector の統合テスト
- [ ] 全コンポーネント連携テスト
- [ ] L2 VisibilityController との連携テスト
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_visibility_integration.py`（新規）

### テストフィクスチャ

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.core.services.visibility_controller import (
    VisibilityController,
    AIVisibilityLevel,
)
from src.core.context.filtered_context import FilteredContext
from src.core.context.visibility_context import (
    VisibilityAwareContext,
    VisibilityHint,
)
from src.core.context.visibility_filtering import VisibilityFilteringService
from src.core.context.hint_collector import HintCollector, HintCollection
from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)


@pytest.fixture
def mock_visibility_controller() -> Mock:
    """可視性コントローラーのモック"""
    controller = Mock(spec=VisibilityController)

    # キャラクター可視性
    char_visibility = {
        "アイラ": AIVisibilityLevel.AWARE,      # 秘密あり
        "主人公": AIVisibilityLevel.USE,        # 全情報可
        "黒幕": AIVisibilityLevel.HIDDEN,       # 完全秘匿
        "師匠": AIVisibilityLevel.KNOW,         # 秘密以外可
    }
    controller.get_character_visibility.side_effect = (
        lambda name: char_visibility.get(name, AIVisibilityLevel.KNOW)
    )

    # 世界観可視性
    world_visibility = {
        "古代王国": AIVisibilityLevel.AWARE,
        "魔法体系": AIVisibilityLevel.USE,
        "禁忌の力": AIVisibilityLevel.HIDDEN,
    }
    controller.get_setting_visibility.side_effect = (
        lambda name: world_visibility.get(name, AIVisibilityLevel.KNOW)
    )

    return controller


@pytest.fixture
def sample_context() -> FilteredContext:
    """サンプルコンテキスト"""
    return FilteredContext(
        scene_id="ep010",
        current_phase="arc_1",
        plot_l1="復讐と赦しの物語",
        plot_l2="主人公の決意",
        plot_l3="対決前夜",
        summary_l1="これまでの物語",
        characters={
            "アイラ": """## 基本情報
謎の少女。

## 秘密
実は王族の血を引いている。
""",
            "主人公": """## 基本情報
復讐を誓う戦士。

## 詳細
師匠の仇を追っている。
""",
            "黒幕": """## 基本情報
物語の敵役。

## 秘密
実は主人公の兄。
""",
            "師匠": """## 基本情報
主人公の師。

## 秘密
禁忌の魔法を知っている。
""",
        },
        world_settings={
            "古代王国": """## 基本情報
かつて栄えた王国。

## 秘密
滅亡の真因は内部の裏切り。
""",
            "魔法体系": """## 基本情報
この世界の魔法。

## 詳細
元素を操る力。
""",
            "禁忌の力": """## 基本情報
使ってはならない力。

## 秘密
世界を滅ぼす可能性がある。
""",
        },
    )


@pytest.fixture
def sample_instructions() -> ForeshadowInstructions:
    """サンプル伏線指示書"""
    instructions = ForeshadowInstructions()
    instructions.add_instruction(ForeshadowInstruction(
        foreshadowing_id="FS-001",
        action=InstructionAction.PLANT,
        forbidden_expressions=["王族", "血筋"],
        note="王族の血筋を匂わせる",
        subtlety_target=4,
    ))
    instructions.add_instruction(ForeshadowInstruction(
        foreshadowing_id="FS-002",
        action=InstructionAction.HINT,
        note="禁忌の魔法の存在を示唆",
        subtlety_target=8,
    ))
    return instructions
```

### テストケース一覧

#### VisibilityFilteringService 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | filter_context() 完全フロー | 全カテゴリフィルタ |
| 2 | filter_characters() HIDDEN除外 | 黒幕が除外される |
| 3 | filter_characters() AWARE処理 | アイラは基本情報のみ |
| 4 | filter_characters() KNOW処理 | 師匠は秘密除去 |
| 5 | filter_characters() USE処理 | 主人公は全情報 |
| 6 | filter_world_settings() | 世界観も同様に |
| 7 | ヒント生成 | AWARE時にヒント |

#### HintCollector 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 8 | collect_all() 統合 | 可視性+伏線 |
| 9 | priority ソート | 優先度順 |
| 10 | format_for_prompt() | プロンプト形式 |

#### 全体統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 11 | 完全フロー | コンテキスト→フィルタ→ヒント |
| 12 | L2連携 | VisibilityController 使用 |
| 13 | パフォーマンス | 100ms以内 |

### テスト実装例

```python
class TestVisibilityIntegration:
    """可視性システム統合テスト"""

    def test_complete_filtering_flow(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
    ):
        """コンテキスト → フィルタリング → ヒント収集"""
        # セットアップ
        filtering_service = VisibilityFilteringService(
            mock_visibility_controller
        )
        hint_collector = HintCollector()

        # 1. コンテキストをフィルタリング
        visibility_context = filtering_service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )

        # 検証: HIDDEN の黒幕が除外されている
        assert "黒幕" not in visibility_context.filtered_characters
        assert "禁忌の力" not in visibility_context.filtered_world_settings

        # 検証: AWARE のアイラは基本情報のみ
        aira_info = visibility_context.filtered_characters.get("アイラ", "")
        assert "基本情報" in aira_info
        assert "秘密" not in aira_info or "王族" not in aira_info

        # 検証: USE の主人公は全情報
        hero_info = visibility_context.filtered_characters.get("主人公", "")
        assert "復讐を誓う戦士" in hero_info
        assert "師匠の仇" in hero_info

        # 2. ヒントを収集
        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
        )

        # 検証: AWARE のキャラ/設定にヒントが生成されている
        aira_hints = [h for h in hints.hints if h.entity_id == "アイラ"]
        assert len(aira_hints) > 0

    def test_with_foreshadowing_instructions(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
        sample_instructions: ForeshadowInstructions,
    ):
        """伏線指示書と可視性の統合"""
        filtering_service = VisibilityFilteringService(
            mock_visibility_controller
        )
        hint_collector = HintCollector()

        # フィルタリング
        visibility_context = filtering_service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )

        # 全ヒント収集
        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=sample_instructions,
        )

        # 検証: 伏線からのヒントも含まれる
        fs_hints = [
            h for h in hints.hints
            if h.source.value == "foreshadowing"
        ]
        assert len(fs_hints) > 0

        # HINT アクションのみがヒントとして収集される
        # （PLANTは指示書として別途扱う）
        fs002_hints = [h for h in fs_hints if "FS-002" in h.entity_id]
        assert len(fs002_hints) == 1

    def test_prompt_format_output(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
        sample_instructions: ForeshadowInstructions,
    ):
        """プロンプト形式出力の検証"""
        filtering_service = VisibilityFilteringService(
            mock_visibility_controller
        )
        hint_collector = HintCollector()

        visibility_context = filtering_service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )

        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=sample_instructions,
        )

        # プロンプト形式に変換
        prompt_text = hint_collector.format_for_prompt(hints)

        # 検証
        assert "執筆時のヒント" in prompt_text
        assert "匂わせてください" in prompt_text

    def test_performance_within_limit(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
        sample_instructions: ForeshadowInstructions,
    ):
        """100ms以内に完了"""
        import time

        filtering_service = VisibilityFilteringService(
            mock_visibility_controller
        )
        hint_collector = HintCollector()

        start = time.time()

        visibility_context = filtering_service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )
        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=sample_instructions,
        )
        _ = hint_collector.format_for_prompt(hints)

        elapsed = time.time() - start

        assert elapsed < 0.1  # 100ms


class TestVisibilityLevelBehavior:
    """可視性レベル別の動作テスト"""

    def test_hidden_completely_excluded(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
    ):
        """HIDDEN は完全に除外"""
        service = VisibilityFilteringService(mock_visibility_controller)

        result = service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )

        # 黒幕と禁忌の力は見えない
        assert "黒幕" not in result.filtered_characters
        assert "禁忌の力" not in result.filtered_world_settings

    def test_aware_generates_hints(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
    ):
        """AWARE はヒントを生成"""
        service = VisibilityFilteringService(mock_visibility_controller)

        result = service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )

        # アイラと古代王国のヒントが生成される
        aira_hints = [h for h in result.hints if h.entity_id == "アイラ"]
        kingdom_hints = [h for h in result.hints if h.entity_id == "古代王国"]

        assert len(aira_hints) > 0
        assert len(kingdom_hints) > 0

    def test_know_removes_secrets(
        self,
        mock_visibility_controller: Mock,
        sample_context: FilteredContext,
    ):
        """KNOW は秘密セクションを除去"""
        service = VisibilityFilteringService(mock_visibility_controller)

        result = service.filter_context(
            sample_context,
            target_level=AIVisibilityLevel.KNOW,
        )

        # 師匠は KNOW なので秘密が除去される
        shishou_info = result.filtered_characters.get("師匠", "")
        assert "基本情報" in shishou_info
        # 秘密セクションの内容が含まれていないことを確認
        assert "禁忌の魔法を知っている" not in shishou_info
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
