"""Tests for ForbiddenKeywordCollector."""

from pathlib import Path

import pytest

from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from src.core.context.lazy_loader import FileLazyLoader
from src.core.context.scene_identifier import SceneIdentifier


@pytest.fixture
def tmp_vault(tmp_path: Path) -> Path:
    """Create a temporary vault structure."""
    vault = tmp_path / "vault" / "test_work"
    (vault / "_ai_control").mkdir(parents=True)
    return vault


@pytest.fixture
def vault_with_files(tmp_vault: Path) -> Path:
    """Create vault with visibility and forbidden files."""
    # visibility.yaml
    (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
        """global_forbidden_keywords:
  - 真の名前
  - 最終兵器
""",
        encoding="utf-8",
    )

    # forbidden_keywords.txt
    (tmp_vault / "_ai_control" / "forbidden_keywords.txt").write_text(
        """# グローバル禁止キーワード
世界の終末
神の名
""",
        encoding="utf-8",
    )

    return tmp_vault


@pytest.fixture
def scene() -> SceneIdentifier:
    """Test scene."""
    return SceneIdentifier(episode_id="010")


@pytest.fixture
def sample_instructions() -> ForeshadowInstructions:
    """Sample foreshadow instructions."""
    instructions = ForeshadowInstructions()
    instructions.add_instruction(
        ForeshadowInstruction(
            foreshadowing_id="FS-010-secret",
            action=InstructionAction.PLANT,
            forbidden_expressions=["王族", "血筋"],
            allowed_expressions=["気高い雰囲気"],
            note="伏線の初回設置",
            subtlety_target=4,
        )
    )
    instructions.add_instruction(
        ForeshadowInstruction(
            foreshadowing_id="FS-005-magic",
            action=InstructionAction.REINFORCE,
            forbidden_expressions=["禁忌の魔法"],
            allowed_expressions=["古の技法"],
            note="伏線の強化",
            subtlety_target=6,
        )
    )
    return instructions


class TestForbiddenKeywordCollectorImport:
    """Test imports."""

    def test_import(self):
        """ForbiddenKeywordCollector can be imported."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
            ForbiddenKeywordResult,
        )

        assert ForbiddenKeywordCollector is not None
        assert ForbiddenKeywordResult is not None


class TestForbiddenKeywordResult:
    """Tests for ForbiddenKeywordResult."""

    def test_add_from_source(self):
        """Add keywords from source."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordResult

        result = ForbiddenKeywordResult()
        result.add_from_source("foreshadowing", ["王族", "血筋"])
        result.add_from_source("global", ["世界の終末"])

        assert "foreshadowing" in result.sources
        assert "global" in result.sources
        assert result.sources["foreshadowing"] == ["王族", "血筋"]

    def test_finalize_deduplicates(self):
        """Finalize deduplicates keywords."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordResult

        result = ForbiddenKeywordResult()
        result.add_from_source("source1", ["王族", "血筋"])
        result.add_from_source("source2", ["王族", "禁忌"])  # 王族 is duplicate
        result.finalize()

        assert len(result.keywords) == 3
        assert "王族" in result.keywords
        assert "血筋" in result.keywords
        assert "禁忌" in result.keywords

    def test_finalize_sorts(self):
        """Finalize sorts keywords."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordResult

        result = ForbiddenKeywordResult()
        result.add_from_source("source", ["禁忌", "王族", "血筋"])
        result.finalize()

        # Should be sorted
        assert result.keywords == sorted(result.keywords)


class TestForbiddenKeywordCollectorFromForeshadowing:
    """Tests for collecting from foreshadowing instructions."""

    def test_collect_from_instructions(
        self, tmp_vault: Path, scene: SceneIdentifier, sample_instructions: ForeshadowInstructions
    ):
        """Collect forbidden keywords from foreshadow instructions."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene, sample_instructions)

        assert "王族" in result.keywords
        assert "血筋" in result.keywords
        assert "禁忌の魔法" in result.keywords
        assert "foreshadowing" in result.sources


class TestForbiddenKeywordCollectorFromVisibility:
    """Tests for collecting from visibility.yaml."""

    def test_collect_from_visibility(self, vault_with_files: Path, scene: SceneIdentifier):
        """Collect from visibility.yaml."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        result = collector.collect(scene)

        assert "真の名前" in result.keywords
        assert "最終兵器" in result.keywords
        assert "visibility" in result.sources


class TestForbiddenKeywordCollectorFromGlobal:
    """Tests for collecting from forbidden_keywords.txt."""

    def test_collect_from_global(self, vault_with_files: Path, scene: SceneIdentifier):
        """Collect from forbidden_keywords.txt."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        result = collector.collect(scene)

        assert "世界の終末" in result.keywords
        assert "神の名" in result.keywords
        assert "global" in result.sources


class TestForbiddenKeywordCollectorAllSources:
    """Tests for collecting from all sources."""

    def test_collect_all_sources(
        self,
        vault_with_files: Path,
        scene: SceneIdentifier,
        sample_instructions: ForeshadowInstructions,
    ):
        """Collect from all sources and merge."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        result = collector.collect(scene, sample_instructions)

        # From foreshadowing
        assert "王族" in result.keywords
        assert "血筋" in result.keywords
        assert "禁忌の魔法" in result.keywords

        # From visibility.yaml
        assert "真の名前" in result.keywords
        assert "最終兵器" in result.keywords

        # From forbidden_keywords.txt
        assert "世界の終末" in result.keywords
        assert "神の名" in result.keywords

        # All sources recorded
        assert "foreshadowing" in result.sources
        assert "visibility" in result.sources
        assert "global" in result.sources

    def test_collect_as_list(
        self,
        vault_with_files: Path,
        scene: SceneIdentifier,
        sample_instructions: ForeshadowInstructions,
    ):
        """Collect as simple list."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        keywords = collector.collect_as_list(scene, sample_instructions)

        assert isinstance(keywords, list)
        assert "王族" in keywords


class TestForbiddenKeywordCollectorEmptyVault:
    """Tests for empty vault scenarios."""

    def test_empty_vault_no_error(self, tmp_vault: Path, scene: SceneIdentifier):
        """Empty vault returns empty result without error."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        assert result.keywords == []

    def test_no_instructions_no_error(self, vault_with_files: Path, scene: SceneIdentifier):
        """No foreshadow instructions still works."""
        from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        result = collector.collect(scene, None)

        # Should still have visibility and global keywords
        assert "真の名前" in result.keywords
        assert "世界の終末" in result.keywords
