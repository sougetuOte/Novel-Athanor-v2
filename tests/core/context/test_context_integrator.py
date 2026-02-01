"""Tests for context integrator protocol and implementation."""

import time
from pathlib import Path
from typing import Optional

import pytest

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.filtered_context import FilteredContext
from src.core.context.context_integrator import (
    ContextCollector,
    ContextIntegrator,
    ContextIntegratorImpl,
)
from src.core.context.lazy_loader import FileLazyLoader
from src.core.context.collectors.plot_collector import PlotCollector
from src.core.context.collectors.summary_collector import SummaryCollector
from src.core.context.collectors.style_guide_collector import StyleGuideCollector


# ContextCollector のテスト
class TestContextCollectorProtocol:
    """Test ContextCollector protocol compliance."""

    def test_mock_implements_protocol(self):
        """Mock が ContextCollector プロトコルを満たす"""

        class MockCollector:
            def collect(self, scene: SceneIdentifier) -> Optional[str]:
                return "collected content"

        collector: ContextCollector = MockCollector()
        scene = SceneIdentifier(episode_id="010")
        assert collector.collect(scene) == "collected content"

    def test_collect_returns_none(self):
        """collect() が None を返せる"""

        class MockCollector:
            def collect(self, scene: SceneIdentifier) -> Optional[str]:
                return None

        collector: ContextCollector = MockCollector()
        scene = SceneIdentifier(episode_id="010")
        assert collector.collect(scene) is None


# ContextIntegrator のテスト
class TestContextIntegratorProtocol:
    """Test ContextIntegrator protocol compliance."""

    def test_mock_implements_protocol(self):
        """Mock が ContextIntegrator プロトコルを満たす"""

        class MockIntegrator:
            def integrate(
                self,
                scene: SceneIdentifier,
                *,
                plot_collector: Optional[ContextCollector] = None,
                summary_collector: Optional[ContextCollector] = None,
                character_collector: Optional[ContextCollector] = None,
                world_collector: Optional[ContextCollector] = None,
                style_collector: Optional[ContextCollector] = None,
            ) -> FilteredContext:
                return FilteredContext(scene_id=str(scene))

            def integrate_with_warnings(
                self,
                scene: SceneIdentifier,
                **collectors,
            ) -> tuple[FilteredContext, list[str]]:
                return FilteredContext(scene_id=str(scene)), []

        integrator: ContextIntegrator = MockIntegrator()
        scene = SceneIdentifier(episode_id="010")
        result = integrator.integrate(scene)
        assert isinstance(result, FilteredContext)

    def test_integrate_with_all_collectors(self):
        """全コレクター指定で統合"""

        class MockCollector:
            def __init__(self, content: str):
                self.content = content

            def collect(self, scene: SceneIdentifier) -> Optional[str]:
                return self.content

        class MockIntegrator:
            def integrate(
                self,
                scene: SceneIdentifier,
                *,
                plot_collector: Optional[ContextCollector] = None,
                summary_collector: Optional[ContextCollector] = None,
                character_collector: Optional[ContextCollector] = None,
                world_collector: Optional[ContextCollector] = None,
                style_collector: Optional[ContextCollector] = None,
            ) -> FilteredContext:
                ctx = FilteredContext(scene_id=str(scene))
                if plot_collector:
                    ctx.plot_l1 = plot_collector.collect(scene)
                if summary_collector:
                    ctx.summary_l1 = summary_collector.collect(scene)
                return ctx

            def integrate_with_warnings(
                self,
                scene: SceneIdentifier,
                **collectors,
            ) -> tuple[FilteredContext, list[str]]:
                return FilteredContext(scene_id=str(scene)), []

        integrator: ContextIntegrator = MockIntegrator()
        scene = SceneIdentifier(episode_id="010")

        plot_col = MockCollector("plot content")
        summary_col = MockCollector("summary content")

        result = integrator.integrate(
            scene, plot_collector=plot_col, summary_collector=summary_col
        )

        assert result.plot_l1 == "plot content"
        assert result.summary_l1 == "summary content"

    def test_integrate_with_partial_collectors(self):
        """一部コレクターのみで統合"""

        class MockCollector:
            def __init__(self, content: str):
                self.content = content

            def collect(self, scene: SceneIdentifier) -> Optional[str]:
                return self.content

        class MockIntegrator:
            def integrate(
                self,
                scene: SceneIdentifier,
                *,
                plot_collector: Optional[ContextCollector] = None,
                summary_collector: Optional[ContextCollector] = None,
                character_collector: Optional[ContextCollector] = None,
                world_collector: Optional[ContextCollector] = None,
                style_collector: Optional[ContextCollector] = None,
            ) -> FilteredContext:
                ctx = FilteredContext(scene_id=str(scene))
                if plot_collector:
                    ctx.plot_l1 = plot_collector.collect(scene)
                return ctx

            def integrate_with_warnings(
                self,
                scene: SceneIdentifier,
                **collectors,
            ) -> tuple[FilteredContext, list[str]]:
                return FilteredContext(scene_id=str(scene)), []

        integrator: ContextIntegrator = MockIntegrator()
        scene = SceneIdentifier(episode_id="010")

        plot_col = MockCollector("plot only")

        result = integrator.integrate(scene, plot_collector=plot_col)

        assert result.plot_l1 == "plot only"
        assert result.summary_l1 is None

    def test_integrate_with_no_collectors(self):
        """コレクターなしで空のFilteredContext"""

        class MockIntegrator:
            def integrate(
                self,
                scene: SceneIdentifier,
                *,
                plot_collector: Optional[ContextCollector] = None,
                summary_collector: Optional[ContextCollector] = None,
                character_collector: Optional[ContextCollector] = None,
                world_collector: Optional[ContextCollector] = None,
                style_collector: Optional[ContextCollector] = None,
            ) -> FilteredContext:
                return FilteredContext(scene_id=str(scene))

            def integrate_with_warnings(
                self,
                scene: SceneIdentifier,
                **collectors,
            ) -> tuple[FilteredContext, list[str]]:
                return FilteredContext(scene_id=str(scene)), []

        integrator: ContextIntegrator = MockIntegrator()
        scene = SceneIdentifier(episode_id="010")

        result = integrator.integrate(scene)

        assert result.scene_id == "ep:010"
        assert result.plot_l1 is None
        assert result.summary_l1 is None

    def test_integrate_with_warnings(self):
        """警告付き統合"""

        class MockIntegrator:
            def integrate(
                self,
                scene: SceneIdentifier,
                *,
                plot_collector: Optional[ContextCollector] = None,
                summary_collector: Optional[ContextCollector] = None,
                character_collector: Optional[ContextCollector] = None,
                world_collector: Optional[ContextCollector] = None,
                style_collector: Optional[ContextCollector] = None,
            ) -> FilteredContext:
                return FilteredContext(scene_id=str(scene))

            def integrate_with_warnings(
                self,
                scene: SceneIdentifier,
                **collectors,
            ) -> tuple[FilteredContext, list[str]]:
                warnings = ["Warning: some collector failed"]
                return FilteredContext(scene_id=str(scene)), warnings

        integrator: ContextIntegrator = MockIntegrator()
        scene = SceneIdentifier(episode_id="010")

        ctx, warnings = integrator.integrate_with_warnings(scene)

        assert isinstance(ctx, FilteredContext)
        assert len(warnings) == 1
        assert "some collector failed" in warnings[0]


# --- Integration Tests with Real Collectors ---


@pytest.fixture
def mock_vault(tmp_path: Path) -> Path:
    """Create a complete test vault structure."""
    vault = tmp_path / "test_vault"

    # Directory structure
    (vault / "episodes").mkdir(parents=True)
    (vault / "characters").mkdir()
    (vault / "world").mkdir()
    (vault / "_plot").mkdir()
    (vault / "_summary").mkdir()
    (vault / "_style_guides").mkdir()

    # Plot files
    (vault / "_plot" / "l1_theme.md").write_text(
        "# テーマ\n復讐と赦しの物語", encoding="utf-8"
    )
    (vault / "_plot" / "l2_chapter01.md").write_text(
        "# 章目標\n主人公の決意を描く", encoding="utf-8"
    )
    (vault / "_plot" / "l3_ep010.md").write_text(
        "# シーン構成\n対決前夜の緊張感", encoding="utf-8"
    )

    # Summary files
    (vault / "_summary" / "l1_overall.md").write_text(
        "# 全体要約\nこれまでの物語の概要", encoding="utf-8"
    )
    (vault / "_summary" / "l2_chapter01.md").write_text(
        "# 章要約\n第1章で起きたこと", encoding="utf-8"
    )
    (vault / "_summary" / "l3_ep009.md").write_text(
        "# 直前要約\n前回のシーンのあらすじ", encoding="utf-8"
    )

    # Style guide
    (vault / "_style_guides" / "default.md").write_text(
        "# スタイルガイド\n三人称視点で記述", encoding="utf-8"
    )

    return vault


@pytest.fixture
def scene() -> SceneIdentifier:
    """Create a test scene identifier."""
    return SceneIdentifier(
        episode_id="ep010",
        chapter_id="chapter01",
        current_phase="arc_1",
    )


@pytest.fixture
def loader(mock_vault: Path) -> FileLazyLoader:
    """Create a FileLazyLoader for the mock vault."""
    return FileLazyLoader(mock_vault)


class TestContextIntegratorImpl:
    """Integration tests for ContextIntegratorImpl with real collectors."""

    def test_integrate_all_collectors(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test integration with all collectors."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
            summary_collector=SummaryCollector(mock_vault, loader),
            style_collector=StyleGuideCollector(mock_vault, loader),
        )

        assert isinstance(result, FilteredContext)
        assert result.plot_l1 is not None
        assert "テーマ" in result.plot_l1
        assert result.plot_l2 is not None
        assert result.plot_l3 is not None
        assert result.summary_l1 is not None
        assert result.style_guide is not None
        assert result.scene_id == "ep010"
        assert result.current_phase == "arc_1"

    def test_integrate_partial_collectors(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test integration with only some collectors."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
        )

        assert result.plot_l1 is not None
        assert result.summary_l1 is None
        assert result.style_guide is None

    def test_integrate_no_collectors(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
    ):
        """Test integration with no collectors."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(scene)

        assert isinstance(result, FilteredContext)
        assert result.plot_l1 is None
        assert result.summary_l1 is None
        assert result.style_guide is None
        assert result.scene_id == "ep010"

    def test_integrate_sets_scene_id(
        self,
        mock_vault: Path,
    ):
        """Test that scene_id is correctly set."""
        scene = SceneIdentifier(episode_id="ep020")
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(scene)

        assert result.scene_id == "ep020"

    def test_integrate_sets_current_phase(
        self,
        mock_vault: Path,
    ):
        """Test that current_phase is correctly set."""
        scene = SceneIdentifier(episode_id="ep010", current_phase="finale")
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(scene)

        assert result.current_phase == "finale"


class TestContextIntegratorImplWithWarnings:
    """Tests for integrate_with_warnings method."""

    def test_integrate_with_warnings_returns_tuple(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test that integrate_with_warnings returns a tuple."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result, warnings = integrator.integrate_with_warnings(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
        )

        assert isinstance(result, FilteredContext)
        assert isinstance(warnings, list)

    def test_integrate_with_warnings_missing_files(
        self,
        mock_vault: Path,
        loader: FileLazyLoader,
    ):
        """Test with missing files - plot L3 should be None."""
        scene_missing = SceneIdentifier(
            episode_id="ep999",
            chapter_id="chapter99",
        )

        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result, warnings = integrator.integrate_with_warnings(
            scene_missing,
            plot_collector=PlotCollector(mock_vault, loader),
        )

        # Plot L3 for ep999 doesn't exist
        assert result.plot_l3 is None


class TestFilteredContextIntegration:
    """Tests for FilteredContext field population."""

    def test_plot_fields_populated(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test that plot fields are correctly populated."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
        )

        assert "テーマ" in (result.plot_l1 or "")
        assert "章目標" in (result.plot_l2 or "")
        assert "シーン構成" in (result.plot_l3 or "")

    def test_summary_fields_populated(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test that summary fields are correctly populated."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(
            scene,
            summary_collector=SummaryCollector(mock_vault, loader),
        )

        assert result.summary_l1 is not None
        assert result.summary_l2 is not None
        assert result.summary_l3 is not None

    def test_style_guide_populated(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test that style guide is correctly populated."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        result = integrator.integrate(
            scene,
            style_collector=StyleGuideCollector(mock_vault, loader),
        )

        assert result.style_guide is not None
        assert "スタイルガイド" in result.style_guide


class TestContextIntegratorPerformance:
    """Performance tests for ContextIntegrator."""

    def test_completes_within_timeout(
        self,
        mock_vault: Path,
        scene: SceneIdentifier,
        loader: FileLazyLoader,
    ):
        """Test that integration completes within 1 second."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        start = time.time()
        result = integrator.integrate(
            scene,
            plot_collector=PlotCollector(mock_vault, loader),
            summary_collector=SummaryCollector(mock_vault, loader),
            style_collector=StyleGuideCollector(mock_vault, loader),
        )
        elapsed = time.time() - start

        assert elapsed < 1.0
        assert result is not None
