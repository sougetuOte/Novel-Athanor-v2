"""Tests for ContextBuilder forbidden keyword methods (L3-7-1d)."""

import pytest

from src.core.context.context_builder import ContextBuilder
from src.core.context.forbidden_keyword_collector import ForbiddenKeywordResult


@pytest.fixture
def builder_with_forbidden(tmp_path):
    """Builder with forbidden keywords file in vault."""
    # Create forbidden_keywords.txt
    ai_control = tmp_path / "_ai_control"
    ai_control.mkdir()
    (ai_control / "forbidden_keywords.txt").write_text(
        "秘密の力\n王家の血\n# comment\n真の名前\n"
    )
    return ContextBuilder(vault_root=tmp_path)


class TestGetForbiddenKeywords:
    """Tests for get_forbidden_keywords()."""

    def test_returns_list(self, builder, scene):
        """T22: Returns a list of strings."""
        result = builder.get_forbidden_keywords(scene)
        assert isinstance(result, list)

    def test_cache_works(self, builder, scene):
        """T23: Second call uses cache."""
        result1 = builder.get_forbidden_keywords(scene)
        result2 = builder.get_forbidden_keywords(scene)
        assert result1 is result2

    def test_cache_bypass(self, builder, scene):
        """T23b: use_cache=False bypasses cache."""
        result1 = builder.get_forbidden_keywords(scene)
        result2 = builder.get_forbidden_keywords(scene, use_cache=False)
        assert result1 is not result2

    def test_empty_without_sources(self, builder, scene):
        """T24: Returns empty list when no forbidden sources exist."""
        result = builder.get_forbidden_keywords(scene)
        assert result == []

    def test_collects_from_file(self, builder_with_forbidden, scene):
        """T22b: Collects keywords from forbidden_keywords.txt."""
        result = builder_with_forbidden.get_forbidden_keywords(scene)
        assert "秘密の力" in result
        assert "王家の血" in result
        assert "真の名前" in result
        # Comments should be excluded
        assert "# comment" not in result


class TestGetForbiddenKeywordsWithSources:
    """Tests for get_forbidden_keywords_with_sources()."""

    def test_returns_result(self, builder, scene):
        """T25: Returns ForbiddenKeywordResult."""
        result = builder.get_forbidden_keywords_with_sources(scene)
        assert isinstance(result, ForbiddenKeywordResult)

    def test_has_source_info(self, builder_with_forbidden, scene):
        """T25b: Result contains source information."""
        result = builder_with_forbidden.get_forbidden_keywords_with_sources(scene)
        assert isinstance(result.sources, dict)
        if result.keywords:
            assert len(result.sources) > 0


class TestGetForbiddenKeywordsAsPrompt:
    """Tests for get_forbidden_keywords_as_prompt()."""

    def test_returns_string(self, builder, scene):
        """T26: Returns formatted string."""
        result = builder.get_forbidden_keywords_as_prompt(scene)
        assert isinstance(result, str)

    def test_empty_when_no_keywords(self, builder, scene):
        """T26b: Returns empty string when no keywords."""
        result = builder.get_forbidden_keywords_as_prompt(scene)
        assert result == ""

    def test_format_with_keywords(self, builder_with_forbidden, scene):
        """T26c: Formats keywords for prompt."""
        result = builder_with_forbidden.get_forbidden_keywords_as_prompt(scene)
        assert len(result) > 0
        assert "秘密の力" in result


class TestGetForbiddenBySource:
    """Tests for get_forbidden_by_source()."""

    def test_returns_dict(self, builder, scene):
        """T27: Returns dict mapping source to keywords."""
        result = builder.get_forbidden_by_source(scene)
        assert isinstance(result, dict)


class TestCheckTextForForbidden:
    """Tests for check_text_for_forbidden()."""

    def test_detect_forbidden(self, builder_with_forbidden, scene):
        """T28: Detects forbidden keywords in text."""
        result = builder_with_forbidden.check_text_for_forbidden(
            scene, "彼女は秘密の力を持っている"
        )
        assert len(result) > 0
        assert "秘密の力" in result

    def test_no_forbidden(self, builder_with_forbidden, scene):
        """T29: Returns empty when no forbidden keywords found."""
        result = builder_with_forbidden.check_text_for_forbidden(scene, "普通の日常の風景")
        assert result == []


class TestIsTextClean:
    """Tests for is_text_clean()."""

    def test_clean_text(self, builder_with_forbidden, scene):
        """T30: Returns True for clean text."""
        assert (
            builder_with_forbidden.is_text_clean(scene, "普通の日常の風景") is True
        )

    def test_dirty_text(self, builder_with_forbidden, scene):
        """T30b: Returns False for text with forbidden keywords."""
        assert (
            builder_with_forbidden.is_text_clean(scene, "王家の血を引く者") is False
        )


class TestClearForbiddenCache:
    """Tests for clear_forbidden_cache() and clear_all_caches()."""

    def test_clear_forbidden_cache(self, builder, scene):
        """T31: Clearing forbidden cache works."""
        result1 = builder.get_forbidden_keywords(scene)
        builder.clear_forbidden_cache()
        result2 = builder.get_forbidden_keywords(scene)
        assert result1 is not result2

    def test_clear_all_caches(self, builder, scene):
        """T31b: clear_all_caches clears forbidden cache."""
        result1 = builder.get_forbidden_keywords(scene)
        builder.clear_all_caches()
        result2 = builder.get_forbidden_keywords(scene)
        assert result1 is not result2
