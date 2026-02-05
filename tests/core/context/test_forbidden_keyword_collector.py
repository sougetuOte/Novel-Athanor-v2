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
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

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
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

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
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

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
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

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
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        keywords = collector.collect_as_list(scene, sample_instructions)

        assert isinstance(keywords, list)
        assert "王族" in keywords


class TestForbiddenKeywordCollectorFromEntityVisibility:
    """Tests for collecting from entity-specific visibility.yaml (Source 4)."""

    def test_collect_from_entity_visibility_basic(self, tmp_vault: Path, scene: SceneIdentifier):
        """Collect entity-specific forbidden keywords from visibility.yaml."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        # Create visibility.yaml with entity-specific forbidden keywords
        (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
            """global_forbidden_keywords:
  - 秘密
  - 真実

entities:
  - entity_name: "Alice"
    default_level: 0
    sections:
      - name: "秘密の出自"
        level: 0
        forbidden_keywords:
          - "王族"
          - "王女"
      - name: "表の顔"
        level: 3
  - entity_name: "Magic System"
    default_level: 3
    sections:
      - name: "禁忌の魔法"
        level: 0
        forbidden_keywords:
          - "闇の魔法"
""",
            encoding="utf-8",
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        # Entity-specific keywords should be collected
        assert "王族" in result.keywords
        assert "王女" in result.keywords
        assert "闇の魔法" in result.keywords
        assert "entity_visibility" in result.sources

    def test_collect_from_entity_visibility_no_entities(self, tmp_vault: Path, scene: SceneIdentifier):
        """No entities key in visibility.yaml."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
            """global_forbidden_keywords:
  - 秘密
""",
            encoding="utf-8",
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        # Should not have entity_visibility source
        assert "entity_visibility" not in result.sources
        # Global keywords should still work
        assert "秘密" in result.keywords

    def test_collect_from_entity_visibility_no_forbidden(self, tmp_vault: Path, scene: SceneIdentifier):
        """Sections without forbidden_keywords."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
            """entities:
  - entity_name: "Alice"
    sections:
      - name: "基本情報"
        level: 3
""",
            encoding="utf-8",
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        # Should not crash, should have no entity keywords
        assert "entity_visibility" not in result.sources or result.sources["entity_visibility"] == []

    def test_collect_from_entity_visibility_multiple_entities(self, tmp_vault: Path, scene: SceneIdentifier):
        """Multiple entities with forbidden keywords."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
            """entities:
  - entity_name: "Alice"
    sections:
      - name: "秘密1"
        forbidden_keywords:
          - "王族"
  - entity_name: "Bob"
    sections:
      - name: "秘密2"
        forbidden_keywords:
          - "暗殺者"
  - entity_name: "World"
    sections:
      - name: "秘密3"
        forbidden_keywords:
          - "世界の真実"
""",
            encoding="utf-8",
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        assert "王族" in result.keywords
        assert "暗殺者" in result.keywords
        assert "世界の真実" in result.keywords

    def test_collect_integrates_all_four_sources(
        self,
        tmp_vault: Path,
        scene: SceneIdentifier,
        sample_instructions: ForeshadowInstructions,
    ):
        """All four sources are integrated."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        # Setup all sources
        (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
            """global_forbidden_keywords:
  - グローバル1

entities:
  - entity_name: "Alice"
    sections:
      - name: "秘密"
        forbidden_keywords:
          - "エンティティ1"
""",
            encoding="utf-8",
        )
        (tmp_vault / "_ai_control" / "forbidden_keywords.txt").write_text(
            "グローバルファイル1",
            encoding="utf-8",
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene, sample_instructions)

        # Source 1: foreshadowing
        assert "王族" in result.keywords
        # Source 2: visibility global
        assert "グローバル1" in result.keywords
        # Source 3: forbidden_keywords.txt
        assert "グローバルファイル1" in result.keywords
        # Source 4: entity visibility
        assert "エンティティ1" in result.keywords

        # All 4 sources present
        assert "foreshadowing" in result.sources
        assert "visibility" in result.sources
        assert "global" in result.sources
        assert "entity_visibility" in result.sources

    def test_collect_deduplication_across_sources(self, tmp_vault: Path, scene: SceneIdentifier):
        """Keywords duplicated across sources are deduplicated."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        (tmp_vault / "_ai_control" / "visibility.yaml").write_text(
            """global_forbidden_keywords:
  - 共通キーワード

entities:
  - entity_name: "Alice"
    sections:
      - name: "秘密"
        forbidden_keywords:
          - "共通キーワード"
          - "独自キーワード"
""",
            encoding="utf-8",
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        # Should only appear once in final keywords
        assert result.keywords.count("共通キーワード") == 1
        assert "独自キーワード" in result.keywords


class TestForbiddenKeywordCollectorEmptyVault:
    """Tests for empty vault scenarios."""

    def test_empty_vault_no_error(self, tmp_vault: Path, scene: SceneIdentifier):
        """Empty vault returns empty result without error."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        loader = FileLazyLoader(tmp_vault)
        collector = ForbiddenKeywordCollector(tmp_vault, loader)

        result = collector.collect(scene)

        assert result.keywords == []

    def test_no_instructions_no_error(self, vault_with_files: Path, scene: SceneIdentifier):
        """No foreshadow instructions still works."""
        from src.core.context.forbidden_keyword_collector import (
            ForbiddenKeywordCollector,
        )

        loader = FileLazyLoader(vault_with_files)
        collector = ForbiddenKeywordCollector(vault_with_files, loader)

        result = collector.collect(scene, None)

        # Should still have visibility and global keywords
        assert "真の名前" in result.keywords
        assert "世界の終末" in result.keywords
