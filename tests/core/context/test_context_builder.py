"""Tests for ContextBuilder facade (L3-7-1a).

Tests the ContextBuilder class definition and ContextBuildResult data class.
"""



from src.core.context.context_builder import ContextBuilder, ContextBuildResult
from src.core.context.filtered_context import FilteredContext
from src.core.context.foreshadow_instruction import ForeshadowInstructions
from src.core.context.hint_collector import HintCollection
from src.core.context.visibility_context import VisibilityAwareContext


class TestContextBuildResult:
    """Tests for ContextBuildResult data class."""

    def test_create_with_all_fields(self):
        """T1: ContextBuildResult can be created with all fields."""
        context = FilteredContext(plot_l1="Theme")
        visibility = VisibilityAwareContext(base_context=context)
        instructions = ForeshadowInstructions()
        hints = HintCollection()

        result = ContextBuildResult(
            context=context,
            visibility_context=visibility,
            foreshadow_instructions=instructions,
            forbidden_keywords=["secret", "royal"],
            hints=hints,
            success=True,
            errors=[],
            warnings=["minor issue"],
        )

        assert result.context is context
        assert result.visibility_context is visibility
        assert result.foreshadow_instructions is instructions
        assert result.forbidden_keywords == ["secret", "royal"]
        assert result.hints is hints
        assert result.success is True
        assert result.errors == []
        assert result.warnings == ["minor issue"]

    def test_create_minimal(self):
        """T1b: ContextBuildResult can be created with minimal fields."""
        context = FilteredContext()
        instructions = ForeshadowInstructions()
        hints = HintCollection()

        result = ContextBuildResult(
            context=context,
            visibility_context=None,
            foreshadow_instructions=instructions,
            forbidden_keywords=[],
            hints=hints,
        )

        assert result.context is context
        assert result.visibility_context is None
        assert result.success is True
        assert result.errors == []
        assert result.warnings == []

    def test_has_errors(self):
        """T2: has_errors() returns True when errors exist."""
        result = ContextBuildResult(
            context=FilteredContext(),
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
            errors=["Something failed"],
        )

        assert result.has_errors() is True

    def test_has_errors_empty(self):
        """T2b: has_errors() returns False when no errors."""
        result = ContextBuildResult(
            context=FilteredContext(),
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        assert result.has_errors() is False

    def test_has_warnings(self):
        """T2c: has_warnings() returns True when warnings exist."""
        result = ContextBuildResult(
            context=FilteredContext(),
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
            warnings=["A warning"],
        )

        assert result.has_warnings() is True

    def test_has_warnings_empty(self):
        """T2d: has_warnings() returns False when no warnings."""
        result = ContextBuildResult(
            context=FilteredContext(),
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        assert result.has_warnings() is False


class TestContextBuilderInit:
    """Tests for ContextBuilder initialization."""

    def test_create_minimal(self, tmp_path):
        """T3: ContextBuilder can be created with vault_root only."""
        builder = ContextBuilder(vault_root=tmp_path)

        assert builder._vault_root == tmp_path

    def test_create_with_all_options(self, tmp_path):
        """T4: ContextBuilder can be created with all optional parameters."""
        from src.core.repositories.foreshadowing import ForeshadowingRepository
        from src.core.services.visibility_controller import VisibilityController

        vc = VisibilityController()
        repo = ForeshadowingRepository(vault_root=tmp_path, work_name="test_work")

        builder = ContextBuilder(
            vault_root=tmp_path,
            work_name="test_work",
            visibility_controller=vc,
            foreshadowing_repository=repo,
        )

        assert builder._vault_root == tmp_path
        assert builder._work_name == "test_work"
        assert builder._visibility_controller is vc
        assert builder._foreshadowing_repository is repo

    def test_internal_components_initialized(self, tmp_path):
        """T5: Internal components are correctly initialized."""
        builder = ContextBuilder(vault_root=tmp_path)

        # Loader should be created
        assert builder._loader is not None

        # Resolver should be created
        assert builder._resolver is not None

        # Integrator should be created
        assert builder._integrator is not None

        # Collectors should be created
        assert builder._plot_collector is not None
        assert builder._summary_collector is not None
        assert builder._character_collector is not None
        assert builder._world_collector is not None
        assert builder._style_collector is not None

        # Hint collector should be created
        assert builder._hint_collector is not None

    def test_foreshadowing_components_without_repo(self, tmp_path):
        """T5b: Without repository, foreshadowing components are None."""
        builder = ContextBuilder(vault_root=tmp_path)

        assert builder._foreshadowing_repository is None
        assert builder._foreshadowing_identifier is None
        assert builder._instruction_generator is None

    def test_foreshadowing_components_with_repo(self, tmp_path):
        """T5c: With repository, foreshadowing components are initialized."""
        from src.core.repositories.foreshadowing import ForeshadowingRepository

        repo = ForeshadowingRepository(vault_root=tmp_path, work_name="test")

        builder = ContextBuilder(
            vault_root=tmp_path,
            work_name="test",
            foreshadowing_repository=repo,
        )

        assert builder._foreshadowing_repository is repo
        assert builder._foreshadowing_identifier is not None
        assert builder._instruction_generator is not None

    def test_visibility_components_without_controller(self, tmp_path):
        """T5d: Without controller, visibility components are None."""
        builder = ContextBuilder(vault_root=tmp_path)

        assert builder._visibility_controller is None
        assert builder._visibility_filtering_service is None

    def test_visibility_components_with_controller(self, tmp_path):
        """T5e: With controller, visibility components are initialized."""
        from src.core.services.visibility_controller import VisibilityController

        vc = VisibilityController()

        builder = ContextBuilder(
            vault_root=tmp_path,
            visibility_controller=vc,
        )

        assert builder._visibility_controller is vc
        assert builder._visibility_filtering_service is not None

    def test_forbidden_keyword_collector_initialized(self, tmp_path):
        """T5f: ForbiddenKeywordCollector is always initialized."""
        builder = ContextBuilder(vault_root=tmp_path)

        assert builder._forbidden_keyword_collector is not None

    def test_stub_methods_exist(self, tmp_path):
        """Verify stub methods exist on the class."""
        builder = ContextBuilder(vault_root=tmp_path)

        assert hasattr(builder, "build_context")
        assert hasattr(builder, "get_foreshadow_instructions")
        assert hasattr(builder, "get_forbidden_keywords")
        assert callable(builder.build_context)
        assert callable(builder.get_foreshadow_instructions)
        assert callable(builder.get_forbidden_keywords)
