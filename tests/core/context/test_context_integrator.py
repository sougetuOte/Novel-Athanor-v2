"""Tests for context integrator protocol."""

from typing import Optional

import pytest

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.filtered_context import FilteredContext
from src.core.context.context_integrator import ContextCollector, ContextIntegrator


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
