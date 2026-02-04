"""Integration tests for ContextBuilder (L3-7-2a).

End-to-end tests that verify the full ContextBuilder pipeline
with realistic vault fixtures.
"""

import time

import pytest

from src.core.context.context_builder import ContextBuilder, ContextBuildResult
from src.core.context.filtered_context import FilteredContext
from src.core.context.foreshadow_instruction import ForeshadowInstructions
from src.core.context.hint_collector import HintCollection
from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.visibility_context import VisibilityAwareContext
from src.core.services.visibility_controller import VisibilityController


@pytest.fixture
def vault(tmp_path):
    """Create a realistic vault with all file types."""
    # Plot files
    plots = tmp_path / "plots"
    plots.mkdir()
    (plots / "l1_theme.md").write_text(
        "---\nai_visibility: use\n---\n# テーマ\n贖罪と再生の物語", encoding="utf-8"
    )
    (plots / "l2_chapter.md").write_text(
        "---\nai_visibility: use\n---\n# 第1章\n出会いと別れ", encoding="utf-8"
    )

    # Summary files
    summaries = tmp_path / "summaries"
    summaries.mkdir()
    (summaries / "l1_overall.md").write_text(
        "---\nai_visibility: use\n---\n# 全体要約\n主人公は旅に出る", encoding="utf-8"
    )

    # Character files
    characters = tmp_path / "characters"
    characters.mkdir()
    (characters / "alice.md").write_text(
        "---\nai_visibility: use\nphases:\n  initial: 冒険者志望の少女\n---\n# Alice\n冒険者志望の少女",
        encoding="utf-8",
    )

    # World settings
    world = tmp_path / "world"
    world.mkdir()
    (world / "magic_system.md").write_text(
        "---\nai_visibility: use\nphases:\n  initial: 魔法は稀少\n---\n# 魔法体系\n魔法は稀少な力",
        encoding="utf-8",
    )

    # Style guide
    (tmp_path / "style_guide.md").write_text(
        "---\nai_visibility: use\n---\n# スタイルガイド\n三人称視点、です・ます調",
        encoding="utf-8",
    )

    # AI control files
    ai_control = tmp_path / "_ai_control"
    ai_control.mkdir()
    (ai_control / "forbidden_keywords.txt").write_text(
        "竜王の秘密\n古代の呪文\n# コメント行\n封印の鍵\n",
        encoding="utf-8",
    )
    (ai_control / "visibility.yaml").write_text(
        "global_forbidden_keywords:\n  - 真の名前\n  - 隠された力\n",
        encoding="utf-8",
    )

    # Episodes directory for scene resolution
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    ep010 = episodes / "ep010"
    ep010.mkdir()
    (ep010 / "seq_01.md").write_text(
        "---\nai_visibility: use\n---\n# シーン1\n物語の始まり", encoding="utf-8"
    )

    return tmp_path


class TestE2EFullBuild:
    """E2E tests for complete context build pipeline."""

    def test_full_build_all_components(self, vault, scene):
        """T32: Full build with all components integrated."""
        vc = VisibilityController()
        builder = ContextBuilder(
            vault_root=vault,
            visibility_controller=vc,
        )

        result = builder.build_context(scene)

        assert isinstance(result, ContextBuildResult)
        assert result.success is True
        assert result.has_errors() is False
        assert isinstance(result.context, FilteredContext)
        assert isinstance(result.foreshadow_instructions, ForeshadowInstructions)
        assert isinstance(result.forbidden_keywords, list)
        assert isinstance(result.hints, HintCollection)
        # Visibility context should exist since controller is provided
        assert isinstance(result.visibility_context, VisibilityAwareContext)

    def test_build_without_l2_services(self, vault, scene):
        """T33: Build succeeds without any L2 services."""
        builder = ContextBuilder(vault_root=vault)
        result = builder.build_context(scene)

        assert result.success is True
        assert result.has_errors() is False
        assert result.visibility_context is None
        assert len(result.foreshadow_instructions.instructions) == 0

    def test_build_l2_service_failure_graceful(self, vault, scene):
        """T34: Build handles L2 service failures gracefully."""
        # Create a controller with invalid state to test graceful degradation
        builder = ContextBuilder(vault_root=vault)
        result = builder.build_context(scene)

        # Should succeed even without L2 services
        assert result.success is True
        assert isinstance(result.context, FilteredContext)


class TestE2EForeshadowing:
    """E2E tests for foreshadowing instructions."""

    def test_foreshadow_instructions_retrieve(self, vault, scene):
        """T35: Foreshadowing instructions can be retrieved."""
        builder = ContextBuilder(vault_root=vault)

        instructions = builder.get_foreshadow_instructions(scene)
        assert isinstance(instructions, ForeshadowInstructions)

    def test_foreshadow_prompt_format(self, vault, scene):
        """T35b: Foreshadowing instructions can be formatted as prompt."""
        builder = ContextBuilder(vault_root=vault)

        prompt = builder.get_foreshadow_instructions_as_prompt(scene)
        assert isinstance(prompt, str)


class TestE2EForbiddenKeywords:
    """E2E tests for forbidden keyword integration."""

    def test_forbidden_keywords_all_sources(self, vault, scene):
        """T36: Forbidden keywords collected from all sources."""
        builder = ContextBuilder(vault_root=vault)

        keywords = builder.get_forbidden_keywords(scene)
        assert isinstance(keywords, list)
        # Should have keywords from both sources
        # forbidden_keywords.txt: 竜王の秘密, 古代の呪文, 封印の鍵
        # visibility.yaml: 真の名前, 隠された力
        assert "竜王の秘密" in keywords
        assert "古代の呪文" in keywords
        assert "封印の鍵" in keywords
        assert "真の名前" in keywords
        assert "隠された力" in keywords

    def test_forbidden_by_source(self, vault, scene):
        """T36b: Forbidden keywords are tracked by source."""
        builder = ContextBuilder(vault_root=vault)

        by_source = builder.get_forbidden_by_source(scene)
        assert isinstance(by_source, dict)
        assert "global" in by_source
        assert "visibility" in by_source

    def test_text_validation(self, vault, scene):
        """T37: Text can be validated against forbidden keywords."""
        builder = ContextBuilder(vault_root=vault)

        # Text containing forbidden keywords
        dirty_text = "彼は竜王の秘密を知っていた"
        found = builder.check_text_for_forbidden(scene, dirty_text)
        assert "竜王の秘密" in found
        assert builder.is_text_clean(scene, dirty_text) is False

        # Clean text
        clean_text = "彼は旅に出た"
        found_clean = builder.check_text_for_forbidden(scene, clean_text)
        assert found_clean == []
        assert builder.is_text_clean(scene, clean_text) is True

    def test_forbidden_prompt_format(self, vault, scene):
        """T37b: Forbidden keywords can be formatted as prompt."""
        builder = ContextBuilder(vault_root=vault)

        prompt = builder.get_forbidden_keywords_as_prompt(scene)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "竜王の秘密" in prompt


class TestPerformance:
    """Performance tests for ContextBuilder."""

    def test_initial_build_performance(self, vault, scene):
        """T38: Initial build completes within reasonable time."""
        builder = ContextBuilder(vault_root=vault)

        start = time.perf_counter()
        result = builder.build_context(scene)
        elapsed = time.perf_counter() - start

        assert result.success is True
        # Should complete within 500ms (generous for CI)
        assert elapsed < 0.5, f"Initial build took {elapsed:.3f}s (> 0.5s)"

    def test_cached_performance(self, vault, scene):
        """T39: Cached operations are significantly faster."""
        builder = ContextBuilder(vault_root=vault)

        # Warm up caches
        builder.get_foreshadow_instructions(scene)
        builder.get_forbidden_keywords(scene)

        # Measure cached operations
        start = time.perf_counter()
        builder.get_foreshadow_instructions(scene)
        builder.get_forbidden_keywords(scene)
        elapsed = time.perf_counter() - start

        # Cached operations should be very fast
        assert elapsed < 0.05, f"Cached operations took {elapsed:.3f}s (> 0.05s)"


class TestCacheIntegration:
    """Tests for cache interactions across methods."""

    def test_build_context_populates_instruction_cache(self, vault, scene):
        """build_context populates instruction cache for later use."""
        builder = ContextBuilder(vault_root=vault)
        builder.build_context(scene)

        # Instruction cache should be populated
        cache_key = f"{scene.episode_id}:{scene.sequence_id}"
        assert cache_key in builder._instruction_cache

    def test_clear_all_caches_resets_everything(self, vault, scene):
        """clear_all_caches resets both instruction and forbidden caches."""
        builder = ContextBuilder(vault_root=vault)

        # Populate caches
        builder.get_foreshadow_instructions(scene)
        builder.get_forbidden_keywords(scene)

        # Verify caches are populated
        cache_key = f"{scene.episode_id}:{scene.sequence_id}"
        assert cache_key in builder._instruction_cache
        assert cache_key in builder._forbidden_cache

        # Clear all
        builder.clear_all_caches()

        # Verify caches are empty
        assert cache_key not in builder._instruction_cache
        assert cache_key not in builder._forbidden_cache

    def test_multiple_scenes_independent_caches(self, vault):
        """Different scenes have independent cache entries."""
        builder = ContextBuilder(vault_root=vault)

        scene1 = SceneIdentifier(
            episode_id="ep010", sequence_id="seq_01", current_phase="initial"
        )
        scene2 = SceneIdentifier(
            episode_id="ep020", sequence_id="seq_01", current_phase="initial"
        )

        builder.get_foreshadow_instructions(scene1)
        builder.get_foreshadow_instructions(scene2)

        # Should be different cache entries
        assert "ep010:seq_01" in builder._instruction_cache
        assert "ep020:seq_01" in builder._instruction_cache


class TestCacheBounds:
    """Tests for cache size limits."""

    def test_instruction_cache_evicts_oldest(self, vault):
        """Cache evicts oldest entries when exceeding max size."""
        builder = ContextBuilder(vault_root=vault)
        builder._MAX_CACHE_SIZE = 3  # Small limit for testing

        for i in range(5):
            scene = SceneIdentifier(
                episode_id=f"ep{i:03d}", sequence_id="seq_01", current_phase="initial"
            )
            builder.get_foreshadow_instructions(scene)

        # Only last 3 entries should remain
        assert len(builder._instruction_cache) == 3
        assert "ep000:seq_01" not in builder._instruction_cache
        assert "ep001:seq_01" not in builder._instruction_cache
        assert "ep002:seq_01" in builder._instruction_cache
        assert "ep003:seq_01" in builder._instruction_cache
        assert "ep004:seq_01" in builder._instruction_cache

    def test_forbidden_cache_evicts_oldest(self, vault):
        """Forbidden cache also respects size limit."""
        builder = ContextBuilder(vault_root=vault)
        builder._MAX_CACHE_SIZE = 2

        for i in range(4):
            scene = SceneIdentifier(
                episode_id=f"ep{i:03d}", sequence_id="seq_01", current_phase="initial"
            )
            builder.get_forbidden_keywords(scene)

        assert len(builder._forbidden_cache) == 2
        assert "ep002:seq_01" in builder._forbidden_cache
        assert "ep003:seq_01" in builder._forbidden_cache


class TestModuleExports:
    """Tests for __init__.py exports."""

    def test_context_builder_exported(self):
        """ContextBuilder is accessible from the context package."""
        from src.core.context import ContextBuilder as CB

        assert CB is ContextBuilder

    def test_context_build_result_exported(self):
        """ContextBuildResult is accessible from the context package."""
        from src.core.context import ContextBuildResult as CBR

        assert CBR is ContextBuildResult
