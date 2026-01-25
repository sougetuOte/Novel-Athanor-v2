# L3-4-3a: ContextIntegrator 統合テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-3a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-4-2a〜L3-4-2e |
| フェーズ | Phase G（統合テスト） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 3 |

## 概要

ContextIntegrator と各コレクター（Plot/Summary/Character/WorldSetting/StyleGuide）
の統合テストを実装する。

## 受け入れ条件

- [ ] 全コレクターの統合動作テスト
- [ ] FilteredContext への正しい統合
- [ ] 警告の伝搬確認
- [ ] パフォーマンステスト（許容時間内）
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_context_integrator.py`

### テストフィクスチャ

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.filtered_context import FilteredContext
from src.core.context.context_integrator import ContextIntegratorImpl
from src.core.context.collectors.plot_collector import PlotCollector
from src.core.context.collectors.summary_collector import SummaryCollector
from src.core.context.collectors.character_collector import CharacterCollector
from src.core.context.collectors.world_setting_collector import WorldSettingCollector
from src.core.context.collectors.style_guide_collector import StyleGuideCollector

@pytest.fixture
def mock_vault(tmp_path: Path) -> Path:
    """完全なテスト vault 構造"""
    vault = tmp_path / "test_vault"

    # ディレクトリ構造
    (vault / "episodes").mkdir(parents=True)
    (vault / "characters").mkdir()
    (vault / "world").mkdir()
    (vault / "_plot").mkdir()
    (vault / "_summary").mkdir()
    (vault / "_style_guides").mkdir()

    # プロット
    (vault / "_plot" / "l1_theme.md").write_text("# テーマ\n復讐と赦し")
    (vault / "_plot" / "l2_chapter01.md").write_text("# 章目標\n主人公の決意")
    (vault / "_plot" / "l3_ep010.md").write_text("# シーン構成\n対決前夜")

    # サマリ
    (vault / "_summary" / "l1_overall.md").write_text("# 全体\nこれまでの物語")
    (vault / "_summary" / "l2_chapter01.md").write_text("# 章\n第1章の要約")
    (vault / "_summary" / "l3_ep009.md").write_text("# 直前\n前回のあらすじ")

    # キャラクター
    (vault / "characters" / "主人公.md").write_text("""---
name: 主人公
---
復讐を誓う戦士
""")

    # 世界観
    (vault / "world" / "王国.md").write_text("""---
name: 王国
---
物語の舞台となる王国
""")

    # スタイルガイド
    (vault / "_style_guides" / "default.md").write_text("# スタイル\n三人称視点")

    return vault

@pytest.fixture
def scene() -> SceneIdentifier:
    """テスト用シーン識別子"""
    return SceneIdentifier(
        episode_id="ep010",
        chapter_id="chapter01",
        current_phase="arc_1",
    )
```

### テストケース一覧

#### 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | integrate() 全コレクター | 全て正常動作 |
| 2 | integrate() 一部のみ | Plot + Character のみ |
| 3 | integrate() コレクターなし | 空の FilteredContext |
| 4 | integrate_with_warnings() | 警告伝搬確認 |

#### FilteredContext 生成テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 5 | plot_l1/l2/l3 設定 | プロット情報 |
| 6 | summary_l1/l2/l3 設定 | サマリ情報 |
| 7 | characters 設定 | キャラクター辞書 |
| 8 | world_settings 設定 | 世界観辞書 |
| 9 | style_guide 設定 | スタイルガイド |
| 10 | scene_id 設定 | シーンID |
| 11 | current_phase 設定 | フェーズ |
| 12 | warnings 設定 | 警告リスト |

#### エラーハンドリングテスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 13 | コレクター例外 | 例外発生時の挙動 |
| 14 | 部分失敗 | 一部コレクター失敗 |
| 15 | 全失敗 | 全コレクター失敗 |

#### パフォーマンステスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 16 | 許容時間内 | 1秒以内に完了 |
| 17 | 大量キャラ | 20キャラクター |
| 18 | 大量設定 | 30設定ファイル |

### テスト実装例

```python
class TestContextIntegratorIntegration:
    """ContextIntegrator 統合テスト"""

    def test_integrate_all_collectors(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
    ):
        """全コレクターで統合"""
        # セットアップ
        loader = FileLazyLoader(mock_vault)
        resolver = SceneResolver(mock_vault)
        phase_filter = CharacterPhaseFilter(["initial", "arc_1", "finale"])

        integrator = ContextIntegratorImpl(
            vault_root=mock_vault,
            loader=loader,
            resolver=resolver,
        )

        # 実行
        result = integrator.integrate(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
            summary_collector=SummaryCollector(mock_vault, loader),
            style_collector=StyleGuideCollector(mock_vault, loader),
        )

        # 検証
        assert result.plot_l1 is not None
        assert result.plot_l2 is not None
        assert result.plot_l3 is not None
        assert result.summary_l1 is not None
        assert result.style_guide is not None
        assert result.scene_id == "ep010"
        assert result.current_phase == "arc_1"

    def test_integrate_with_warnings_propagates(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
    ):
        """警告が伝搬される"""
        # 存在しないファイルを参照するシーン
        scene_missing = SceneIdentifier(
            episode_id="ep999",  # 存在しない
            chapter_id="chapter99",
            current_phase="arc_1",
        )

        loader = FileLazyLoader(mock_vault)
        integrator = ContextIntegratorImpl(
            vault_root=mock_vault,
            loader=loader,
        )

        # 実行
        result, warnings = integrator.integrate_with_warnings(
            scene_missing,
            plot_collector=PlotCollector(mock_vault, loader),
        )

        # 検証
        assert len(warnings) > 0  # 警告が発生


class TestContextIntegratorPerformance:
    """パフォーマンステスト"""

    def test_completes_within_timeout(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
    ):
        """1秒以内に完了"""
        import time

        loader = FileLazyLoader(mock_vault)
        integrator = ContextIntegratorImpl(
            vault_root=mock_vault,
            loader=loader,
        )

        start = time.time()
        result = integrator.integrate(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
            summary_collector=SummaryCollector(mock_vault, loader),
            style_collector=StyleGuideCollector(mock_vault, loader),
        )
        elapsed = time.time() - start

        assert elapsed < 1.0
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
