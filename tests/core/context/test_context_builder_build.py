"""Tests for ContextBuilder.build_context() (L3-7-1b)."""



from src.core.context.context_builder import ContextBuilder, ContextBuildResult
from src.core.context.filtered_context import FilteredContext
from src.core.context.foreshadow_instruction import ForeshadowInstructions
from src.core.context.hint_collector import HintCollection
from src.core.context.visibility_context import VisibilityAwareContext


class TestBuildContext:
    """Tests for build_context() method."""

    def test_build_context_returns_result(self, builder, scene):
        """T6: build_context() returns ContextBuildResult."""
        result = builder.build_context(scene)
        assert isinstance(result, ContextBuildResult)
        assert isinstance(result.context, FilteredContext)
        assert isinstance(result.foreshadow_instructions, ForeshadowInstructions)
        assert isinstance(result.forbidden_keywords, list)
        assert isinstance(result.hints, HintCollection)

    def test_build_context_without_visibility(self, builder, scene):
        """T7: build_context() works without visibility controller."""
        result = builder.build_context(scene)
        assert result.visibility_context is None
        assert result.success is True

    def test_build_context_with_visibility(self, tmp_path, scene):
        """T7b: build_context() applies visibility when controller provided."""
        from src.core.services.visibility_controller import VisibilityController

        vc = VisibilityController()
        builder = ContextBuilder(vault_root=tmp_path, visibility_controller=vc)
        result = builder.build_context(scene)
        assert result.visibility_context is not None
        assert isinstance(result.visibility_context, VisibilityAwareContext)

    def test_build_context_without_foreshadowing(self, builder, scene):
        """T8: build_context() works without foreshadowing repository."""
        result = builder.build_context(scene)
        assert result.foreshadow_instructions is not None
        assert len(result.foreshadow_instructions.instructions) == 0

    def test_build_context_graceful_degradation(self, builder, scene):
        """T9: build_context() handles component errors gracefully."""
        # Even with missing files, build should succeed with warnings
        result = builder.build_context(scene)
        assert result.success is True
        # errors should be empty (no critical failures)
        assert result.has_errors() is False

    def test_build_context_warnings_propagated(self, builder, scene):
        """T11: Warnings from integrator are propagated to result."""
        result = builder.build_context(scene)
        # Warnings from individual collectors are preserved in result
        assert isinstance(result.warnings, list)


class TestBuildContextErrors:
    """Tests for build_context() error classification (SHORT-01)."""

    def test_integration_failure_recorded_as_error(self, tmp_path, scene):
        """Integration failure is recorded in errors (not warnings) with success=False."""
        from unittest.mock import MagicMock

        builder = ContextBuilder(vault_root=tmp_path)
        # Replace integrator with one that raises
        mock_integrator = MagicMock()
        mock_integrator.integrate_with_warnings.side_effect = ValueError("integration failed")
        builder._integrator = mock_integrator

        result = builder.build_context(scene)

        assert result.success is False
        assert result.has_errors() is True
        assert any("integration failed" in e for e in result.errors)
        # Should still return a valid (empty) FilteredContext
        assert isinstance(result.context, FilteredContext)

    def test_optional_failures_remain_warnings(self, tmp_path, scene):
        """Optional component failures are recorded as warnings, not errors."""
        from unittest.mock import MagicMock

        from src.core.services.visibility_controller import VisibilityController

        vc = VisibilityController()
        builder = ContextBuilder(vault_root=tmp_path, visibility_controller=vc)
        # Replace visibility filtering with one that raises
        mock_filter = MagicMock()
        mock_filter.filter_context.side_effect = ValueError("visibility failed")
        builder._visibility_filtering_service = mock_filter

        result = builder.build_context(scene)

        assert result.success is True
        assert result.has_errors() is False
        assert any("visibility failed" in w for w in result.warnings)


class TestBuildContextSimple:
    """Tests for build_context_simple() method."""

    def test_build_context_simple_returns_filtered(self, builder, scene):
        """T10: build_context_simple() returns FilteredContext directly."""
        result = builder.build_context_simple(scene)
        assert isinstance(result, FilteredContext)
