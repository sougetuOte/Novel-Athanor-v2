"""Tests for VisibilityFilteringService."""


from src.core.context.filtered_context import FilteredContext
from src.core.context.visibility_context import VisibilityAwareContext
from src.core.services.visibility_controller import VisibilityController


class TestVisibilityFilteringServiceImport:
    """Test imports."""

    def test_import(self):
        """VisibilityFilteringService can be imported."""
        from src.core.context.visibility_filtering import (
            FilteringResult,
            VisibilityFilteringService,
        )

        assert VisibilityFilteringService is not None
        assert FilteringResult is not None


class TestFilteringResult:
    """Tests for FilteringResult dataclass."""

    def test_create(self):
        """Create FilteringResult."""
        from src.core.context.visibility_filtering import FilteringResult

        result = FilteringResult(
            filtered_data={"key": "value"},
            removed_count=2,
        )

        assert result.filtered_data == {"key": "value"}
        assert result.removed_count == 2
        assert result.hints == []


class TestVisibilityFilteringServiceBasic:
    """Basic tests for VisibilityFilteringService."""

    def test_filter_context_returns_visibility_aware_context(self):
        """filter_context returns VisibilityAwareContext."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        base_context = FilteredContext(
            plot_l1="Theme: Adventure",
            characters={"Alice": "A brave hero"},
        )

        result = service.filter_context(base_context)

        assert isinstance(result, VisibilityAwareContext)
        assert result.base_context == base_context


class TestVisibilityFilteringServiceCharacters:
    """Tests for character filtering."""

    def test_filter_characters_no_visibility_comments(self):
        """Characters without visibility comments pass through."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        characters = {
            "Alice": "A brave hero.\nShe fights for justice.",
            "Bob": "A mysterious stranger.",
        }

        result = service.filter_characters(characters)

        assert "Alice" in result.filtered_data
        assert "Bob" in result.filtered_data
        assert result.removed_count == 0

    def test_filter_characters_with_hidden_section(self):
        """Characters with HIDDEN sections have those sections removed."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        # ai_visibility: 0 = HIDDEN
        characters = {
            "Alice": """# Alice
## Basic Info
A brave hero.

## Secret
<!-- ai_visibility: 0 -->
She is actually a princess.
""",
        }

        result = service.filter_characters(characters)

        assert "Alice" in result.filtered_data
        # The HIDDEN section should be excluded
        assert "princess" not in result.filtered_data["Alice"]

    def test_filter_characters_with_aware_section_generates_hint(self):
        """Characters with AWARE sections generate hints."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        # ai_visibility: 1 = AWARE
        characters = {
            "Alice": """# Alice
## Basic Info
A brave hero.

## Mystery
<!-- ai_visibility: 1 -->
There's something hidden about her past.
""",
        }

        result = service.filter_characters(characters)

        assert "Alice" in result.filtered_data
        # AWARE section content should be replaced with hints
        assert "hidden about her past" not in result.filtered_data["Alice"]
        # Should have a hint
        assert len(result.hints) > 0


class TestVisibilityFilteringServiceWorldSettings:
    """Tests for world setting filtering."""

    def test_filter_world_settings_no_visibility_comments(self):
        """World settings without visibility comments pass through."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        world_settings = {
            "Magic System": "Magic is powered by emotions.",
            "Geography": "The land is divided into five kingdoms.",
        }

        result = service.filter_world_settings(world_settings)

        assert "Magic System" in result.filtered_data
        assert "Geography" in result.filtered_data
        assert result.removed_count == 0

    def test_filter_world_settings_with_hidden_section(self):
        """World settings with HIDDEN sections have those sections removed."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        # ai_visibility: 0 = HIDDEN
        world_settings = {
            "Magic System": """# Magic System
## Overview
Magic is powered by emotions.

## Forbidden Knowledge
<!-- ai_visibility: 0 -->
The true source of magic is dark.
""",
        }

        result = service.filter_world_settings(world_settings)

        assert "Magic System" in result.filtered_data
        # HIDDEN section should be excluded
        assert "dark" not in result.filtered_data["Magic System"]


class TestVisibilityFilteringServiceFull:
    """Tests for full context filtering."""

    def test_filter_context_combines_all_filters(self):
        """filter_context filters all categories."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        # ai_visibility: 0 = HIDDEN
        base_context = FilteredContext(
            plot_l1="Theme: Mystery",
            plot_l2="Chapter goal: Reveal the truth",
            characters={
                "Alice": """# Alice
## Basic Info
A detective.

## Secret
<!-- ai_visibility: 0 -->
She knows the culprit.
""",
            },
            world_settings={
                "City": "A dark and mysterious city.",
            },
        )

        result = service.filter_context(base_context)

        # Should be VisibilityAwareContext
        assert isinstance(result, VisibilityAwareContext)

        # Characters should be filtered
        assert "Alice" in result.filtered_characters
        assert "culprit" not in result.filtered_characters.get("Alice", "")

        # World settings should pass through
        assert "City" in result.filtered_world_settings

        # Base context preserved
        assert result.base_context.plot_l1 == "Theme: Mystery"


class TestVisibilityFilteringServiceWithForbiddenKeywords:
    """Tests for forbidden keyword handling."""

    def test_forbidden_keywords_collected(self):
        """Forbidden keywords from controller are collected."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController(
            forbidden_keywords=["secret", "hidden"]
        )
        service = VisibilityFilteringService(controller)

        base_context = FilteredContext(
            characters={"Alice": "A brave hero."},
        )

        result = service.filter_context(base_context)

        # Forbidden keywords should be in the result
        assert "secret" in result.forbidden_keywords
        assert "hidden" in result.forbidden_keywords


class TestVisibilityFilteringServiceEmptyContext:
    """Tests for empty context scenarios."""

    def test_empty_context(self):
        """Empty context returns empty VisibilityAwareContext."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        base_context = FilteredContext()

        result = service.filter_context(base_context)

        assert isinstance(result, VisibilityAwareContext)
        assert result.filtered_characters == {}
        assert result.filtered_world_settings == {}

    def test_none_characters(self):
        """Context with no characters works."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        base_context = FilteredContext(
            plot_l1="Theme",
            characters={},
        )

        result = service.filter_context(base_context)

        assert result.filtered_characters == {}


class TestVisibilityFilteringServiceTypeImports:
    """Tests for type imports (W2B-3)."""

    def test_l2_filtered_context_not_confused_with_l3(self):
        """L2 VisibilityFilteredContent import is distinct from L3 FilteredContext."""
        from src.core.context.filtered_context import (
            FilteredContext as L3FilteredContext,
        )
        from src.core.context.visibility_filtering import VisibilityFilteringService
        from src.core.services.visibility_controller import (
            VisibilityFilteredContent as L2VisibilityFilteredContent,
        )

        # L2 and L3 should be different types (name collision resolved)
        assert L2VisibilityFilteredContent is not L3FilteredContext

        # Service should work with L3 FilteredContext
        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        l3_context = L3FilteredContext(
            characters={"Alice": "Hero"},
        )
        result = service.filter_context(l3_context)
        assert isinstance(result, VisibilityAwareContext)

    def test_filtering_returns_l2_visibility_filtered_content(self):
        """filter() method returns L2 VisibilityFilteredContent type."""
        from src.core.context.visibility_filtering import VisibilityFilteringService

        controller = VisibilityController()
        service = VisibilityFilteringService(controller)

        characters = {"Alice": "A brave hero."}
        service.filter_characters(characters)

        # The result should reference L2's VisibilityFilteredContent type in the controller
        # Verify that filter_result from controller has correct attributes
        content = "## Secret\n<!-- ai_visibility: 0 -->\nSecret info"
        filter_result = controller.filter(content)

        # L2 VisibilityFilteredContent has these attributes
        assert hasattr(filter_result, "content")
        assert hasattr(filter_result, "hints")
        assert hasattr(filter_result, "forbidden_keywords")
        assert hasattr(filter_result, "excluded_sections")
