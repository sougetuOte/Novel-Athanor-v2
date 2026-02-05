"""Tests for parallel execution in ContextIntegrator."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.core.context.collectors.character_collector import CharacterContext
from src.core.context.collectors.plot_collector import PlotContext
from src.core.context.collectors.summary_collector import SummaryContext
from src.core.context.collectors.world_setting_collector import WorldSettingContext
from src.core.context.context_integrator import ContextIntegratorImpl
from src.core.context.filtered_context import FilteredContext
from src.core.context.scene_identifier import SceneIdentifier


@pytest.fixture
def scene() -> SceneIdentifier:
    """Create a test scene identifier."""
    return SceneIdentifier(
        episode_id="ep010",
        chapter_id="chapter01",
        current_phase="arc_1",
    )


@pytest.fixture
def mock_vault(tmp_path: Path) -> Path:
    """Create a minimal test vault structure."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    return vault


class TestContextIntegratorParallelDefault:
    """Test default behavior (parallel=False)."""

    def test_default_is_sequential(self, mock_vault: Path, scene: SceneIdentifier):
        """parallel=False should be the default."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        # Default should be False
        assert integrator._parallel is False

    def test_default_max_workers(self, mock_vault: Path):
        """Default max_workers should be 5."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault)

        assert integrator._max_workers == 5

    def test_sequential_integration_unchanged(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """parallel=False should produce the same result as before."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=False)

        # Create mock collectors
        plot_col = Mock()
        plot_col.collect_as_string.return_value = "plot content"

        summary_col = Mock()
        summary_col.collect_as_string.return_value = "summary content"

        result = integrator.integrate(
            scene, plot_collector=plot_col, summary_collector=summary_col
        )

        # Should work as before
        assert isinstance(result, FilteredContext)
        assert result.scene_id == "ep010"


class TestContextIntegratorParallelEnabled:
    """Test parallel execution (parallel=True)."""

    def test_parallel_initialization(self, mock_vault: Path):
        """parallel=True should be stored correctly."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        assert integrator._parallel is True

    def test_parallel_with_custom_max_workers(self, mock_vault: Path):
        """max_workers should be configurable."""
        integrator = ContextIntegratorImpl(
            vault_root=mock_vault, parallel=True, max_workers=10
        )

        assert integrator._max_workers == 10

    def test_parallel_integration_with_mock_collectors(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """parallel=True should integrate all collectors in parallel."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        # Create mock collectors with collect() returning typed context
        plot_col = Mock()
        plot_context = PlotContext(
            l1_theme="L1 theme",
            l2_chapter="L2 chapter",
            l3_scene="L3 scene",
        )
        plot_col.collect.return_value = plot_context

        summary_col = Mock()
        summary_context = SummaryContext(
            l1_overall="L1 summary",
            l2_chapter="L2 summary",
            l3_recent="L3 summary",
        )
        summary_col.collect.return_value = summary_context

        style_col = Mock()
        style_col.collect_as_string.return_value = "Style guide content"

        result = integrator.integrate(
            scene,
            plot_collector=plot_col,
            summary_collector=summary_col,
            style_collector=style_col,
        )

        # Verify results
        assert isinstance(result, FilteredContext)
        assert result.plot_l1 == "L1 theme"
        assert result.plot_l2 == "L2 chapter"
        assert result.plot_l3 == "L3 scene"
        assert result.summary_l1 == "L1 summary"
        assert result.summary_l2 == "L2 summary"
        assert result.summary_l3 == "L3 summary"
        assert result.style_guide == "Style guide content"

    def test_parallel_integration_empty_collectors(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """parallel=True with no collectors should return empty context."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        result = integrator.integrate(scene)

        assert isinstance(result, FilteredContext)
        assert result.scene_id == "ep010"
        assert result.plot_l1 is None
        assert result.summary_l1 is None

    def test_parallel_integration_partial_collectors(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """parallel=True with only some collectors."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        plot_col = Mock()
        plot_context = PlotContext(
            l1_theme="Theme only",
            l2_chapter=None,
            l3_scene=None,
        )
        plot_col.collect.return_value = plot_context

        result = integrator.integrate(scene, plot_collector=plot_col)

        assert result.plot_l1 == "Theme only"
        assert result.summary_l1 is None


class TestContextIntegratorParallelErrorHandling:
    """Test error handling in parallel execution."""

    def test_parallel_collector_exception_adds_warning(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """Exception in one collector should add warning and continue."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        # Plot collector raises exception
        plot_col = Mock()
        plot_col.collect.side_effect = ValueError("Plot collection failed")

        # Summary collector works fine
        summary_col = Mock()
        summary_context = SummaryContext(
            l1_overall="Summary works",
            l2_chapter=None,
            l3_recent=None,
        )
        summary_col.collect.return_value = summary_context

        result = integrator.integrate(
            scene, plot_collector=plot_col, summary_collector=summary_col
        )

        # Summary should still work
        assert result.summary_l1 == "Summary works"

        # Warning should be added
        assert len(result.warnings) > 0
        assert any("plot" in w.lower() for w in result.warnings)
        assert any("Plot collection failed" in w for w in result.warnings)

    def test_parallel_multiple_collector_exceptions(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """Multiple collectors failing should add multiple warnings."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        plot_col = Mock()
        plot_col.collect.side_effect = ValueError("Plot failed")

        summary_col = Mock()
        summary_col.collect.side_effect = RuntimeError("Summary failed")

        result = integrator.integrate(
            scene, plot_collector=plot_col, summary_collector=summary_col
        )

        # Both should have warnings
        assert len(result.warnings) >= 2
        assert any("plot" in w.lower() for w in result.warnings)
        assert any("summary" in w.lower() for w in result.warnings)


class TestContextIntegratorParallelCharacterAndWorld:
    """Test parallel execution with character and world collectors."""

    def test_parallel_character_collector(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """parallel=True should handle CharacterContext correctly."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        char_col = Mock()
        char_context = CharacterContext(
            characters={"Alice": "Alice data", "Bob": "Bob data"},
            warnings=["Character warning"],
        )
        char_col.collect.return_value = char_context

        result = integrator.integrate(scene, character_collector=char_col)

        assert result.characters["Alice"] == "Alice data"
        assert result.characters["Bob"] == "Bob data"
        assert "Character warning" in result.warnings

    def test_parallel_world_collector(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """parallel=True should handle WorldSettingContext correctly."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        world_col = Mock()
        world_context = WorldSettingContext(
            settings={"Magic": "Magic system", "Tech": "Technology level"},
            warnings=["World warning"],
        )
        world_col.collect.return_value = world_context

        result = integrator.integrate(scene, world_collector=world_col)

        assert result.world_settings["Magic"] == "Magic system"
        assert result.world_settings["Tech"] == "Technology level"
        assert "World warning" in result.warnings


class TestContextIntegratorWithWarningsParallel:
    """Test integrate_with_warnings with parallel execution."""

    def test_integrate_with_warnings_parallel(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """integrate_with_warnings should work with parallel=True."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        plot_col = Mock()
        plot_context = PlotContext(
            l1_theme="Theme",
            l2_chapter="Chapter",
            l3_scene="Scene",
        )
        plot_col.collect.return_value = plot_context

        ctx, warnings = integrator.integrate_with_warnings(
            scene, plot_collector=plot_col
        )

        assert isinstance(ctx, FilteredContext)
        assert isinstance(warnings, list)
        assert ctx.plot_l1 == "Theme"

    def test_integrate_with_warnings_parallel_with_collector_error(
        self, mock_vault: Path, scene: SceneIdentifier
    ):
        """integrate_with_warnings should propagate warnings from parallel execution."""
        integrator = ContextIntegratorImpl(vault_root=mock_vault, parallel=True)

        plot_col = Mock()
        plot_col.collect.side_effect = ValueError("Collection error")

        ctx, warnings = integrator.integrate_with_warnings(
            scene, plot_collector=plot_col
        )

        # Warnings should be propagated
        assert len(warnings) > 0
        assert any("Collection error" in w for w in warnings)
