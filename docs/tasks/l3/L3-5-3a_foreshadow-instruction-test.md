# L3-5-3a: 伏線指示書統合テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-3a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-5-2a〜L3-5-2c |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

伏線指示書生成の統合テストを実装する。
ForeshadowingIdentifier → InstructionGenerator → ForbiddenKeywordCollector の
連携動作を検証。

## 受け入れ条件

- [ ] ForeshadowingIdentifier の統合テスト
- [ ] InstructionGeneratorImpl の統合テスト
- [ ] ForbiddenKeywordCollector の統合テスト
- [ ] 全コンポーネント連携テスト
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_foreshadow_integration.py`（新規）

### テストフィクスチャ

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from src.core.context.foreshadowing_identifier import (
    ForeshadowingIdentifier,
    IdentifiedForeshadowing,
)
from src.core.context.instruction_generator import InstructionGeneratorImpl
from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector
from src.core.context.lazy_loader import FileLazyLoader


@pytest.fixture
def mock_foreshadowing_manager() -> Mock:
    """伏線マネージャーのモック"""
    manager = Mock()

    # サンプル伏線データ
    fs1 = Mock()
    fs1.id = "FS-001"
    fs1.status = "registered"
    fs1.plant_scene = "ep010"
    fs1.reinforce_scenes = []
    fs1.allowed_expressions = ["気高い雰囲気", "見覚えのある光"]
    fs1.forbidden_keywords = ["王族", "血筋"]
    fs1.plant_hint = "自然に描写してください"
    fs1.importance = "critical"

    fs2 = Mock()
    fs2.id = "FS-002"
    fs2.status = "planted"
    fs2.plant_scene = "ep005"
    fs2.reinforce_scenes = ["ep010", "ep015"]
    fs2.allowed_expressions = ["禁じられた技法"]
    fs2.forbidden_keywords = ["禁忌の魔法"]
    fs2.reinforce_hint = "控えめに想起させてください"
    fs2.importance = "normal"

    manager.list_all.return_value = [fs1, fs2]
    manager.get.side_effect = lambda id: fs1 if id == "FS-001" else fs2

    return manager


@pytest.fixture
def mock_vault(tmp_path: Path) -> Path:
    """テスト用 vault"""
    vault = tmp_path / "test_vault"
    (vault / "_ai_control").mkdir(parents=True)

    # visibility.yaml
    (vault / "_ai_control" / "visibility.yaml").write_text("""
global_forbidden_keywords:
  - 真の名前
  - 最終兵器
""")

    # forbidden_keywords.txt
    (vault / "_ai_control" / "forbidden_keywords.txt").write_text("""
# グローバル禁止キーワード
世界の終末
神の名
""")

    return vault


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

#### ForeshadowingIdentifier 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | identify() PLANT + REINFORCE | 同一シーンで両方検出 |
| 2 | identify() 複数伏線 | 複数の伏線が返る |
| 3 | identify() L2連携 | ForeshadowingManager連携 |

#### InstructionGeneratorImpl 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 4 | generate() 完全フロー | 特定→指示生成 |
| 5 | generate() subtlety計算 | 重要度反映 |
| 6 | generate() 指示内容 | note, expressions |

#### ForbiddenKeywordCollector 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 7 | collect() 全ソース統合 | 伏線+可視性+グローバル |
| 8 | collect() 重複排除 | 同じキーワード |
| 9 | collect() ソース記録 | デバッグ情報 |

#### 全体統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 10 | 完全フロー | シーン→指示書→禁止キーワード |
| 11 | 空シーン | 伏線なしシーン |
| 12 | パフォーマンス | 100ms以内 |

### テスト実装例

```python
class TestForeshadowIntegration:
    """伏線指示書統合テスト"""

    def test_complete_flow(
        self,
        mock_foreshadowing_manager: Mock,
        mock_vault: Path,
        scene: SceneIdentifier,
    ):
        """シーン → 伏線特定 → 指示生成 → 禁止キーワード収集"""
        # セットアップ
        identifier = ForeshadowingIdentifier(mock_foreshadowing_manager)
        generator = InstructionGeneratorImpl(
            mock_foreshadowing_manager,
            identifier,
        )
        loader = FileLazyLoader(mock_vault)
        collector = ForbiddenKeywordCollector(mock_vault, loader)

        # 1. 指示書生成
        instructions = generator.generate(scene)

        # 2. 禁止キーワード収集
        forbidden = collector.collect(scene, instructions)

        # 検証
        # PLANT（FS-001）と REINFORCE（FS-002）の2つ
        assert len(instructions.instructions) == 2

        # PLANT 指示確認
        plant_inst = instructions.get_for_foreshadowing("FS-001")
        assert plant_inst is not None
        assert plant_inst.action == InstructionAction.PLANT
        assert "王族" in plant_inst.forbidden_expressions

        # REINFORCE 指示確認
        reinforce_inst = instructions.get_for_foreshadowing("FS-002")
        assert reinforce_inst is not None
        assert reinforce_inst.action == InstructionAction.REINFORCE

        # 禁止キーワード統合確認
        assert "王族" in forbidden.keywords
        assert "血筋" in forbidden.keywords
        assert "禁忌の魔法" in forbidden.keywords
        assert "真の名前" in forbidden.keywords  # visibility.yaml から
        assert "世界の終末" in forbidden.keywords  # forbidden_keywords.txt から

    def test_subtlety_reflects_importance(
        self,
        mock_foreshadowing_manager: Mock,
        scene: SceneIdentifier,
    ):
        """重要度が subtlety に反映される"""
        identifier = ForeshadowingIdentifier(mock_foreshadowing_manager)
        generator = InstructionGeneratorImpl(
            mock_foreshadowing_manager,
            identifier,
        )

        instructions = generator.generate(scene)

        # FS-001 は critical なので subtlety が低い（より明確）
        critical_inst = instructions.get_for_foreshadowing("FS-001")
        assert critical_inst.subtlety_target <= 4

        # FS-002 は normal なので標準的な subtlety
        normal_inst = instructions.get_for_foreshadowing("FS-002")
        assert normal_inst.subtlety_target >= 5

    def test_empty_scene_returns_empty_instructions(
        self,
        mock_foreshadowing_manager: Mock,
    ):
        """伏線なしシーンでは空の指示書"""
        # 無関係なシーン
        unrelated_scene = SceneIdentifier(
            episode_id="ep999",
            chapter_id="chapter99",
            current_phase="finale",
        )

        identifier = ForeshadowingIdentifier(mock_foreshadowing_manager)
        generator = InstructionGeneratorImpl(
            mock_foreshadowing_manager,
            identifier,
        )

        instructions = generator.generate(unrelated_scene)

        assert len(instructions.instructions) == 0

    def test_performance_within_limit(
        self,
        mock_foreshadowing_manager: Mock,
        mock_vault: Path,
        scene: SceneIdentifier,
    ):
        """100ms以内に完了"""
        import time

        identifier = ForeshadowingIdentifier(mock_foreshadowing_manager)
        generator = InstructionGeneratorImpl(
            mock_foreshadowing_manager,
            identifier,
        )
        loader = FileLazyLoader(mock_vault)
        collector = ForbiddenKeywordCollector(mock_vault, loader)

        start = time.time()
        instructions = generator.generate(scene)
        _ = collector.collect(scene, instructions)
        elapsed = time.time() - start

        assert elapsed < 0.1  # 100ms
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
