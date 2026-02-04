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


class TestBuildContextSimple:
    """Tests for build_context_simple() method."""

    def test_build_context_simple_returns_filtered(self, builder, scene):
        """T10: build_context_simple() returns FilteredContext directly."""
        result = builder.build_context_simple(scene)
        assert isinstance(result, FilteredContext)
