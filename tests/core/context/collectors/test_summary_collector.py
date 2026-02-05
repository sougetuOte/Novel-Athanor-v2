"""Tests for summary context collector (L3-4-2b)."""

from pathlib import Path

from src.core.context.collectors.summary_collector import (
    SummaryCollector,
    SummaryContext,
)
from src.core.context.lazy_loader import FileLazyLoader
from src.core.context.scene_identifier import SceneIdentifier


class TestSummaryContext:
    """Test SummaryContext data class."""

    def test_create_empty(self):
        """Test creating an empty SummaryContext."""
        context = SummaryContext()
        assert context.l1_overall is None
        assert context.l2_chapter is None
        assert context.l3_recent is None

    def test_create_with_all_fields(self):
        """Test creating SummaryContext with all fields."""
        context = SummaryContext(
            l1_overall="Overall summary",
            l2_chapter="Chapter summary",
            l3_recent="Recent scene summary",
        )
        assert context.l1_overall == "Overall summary"
        assert context.l2_chapter == "Chapter summary"
        assert context.l3_recent == "Recent scene summary"

    def test_to_dict(self):
        """Test converting SummaryContext to dictionary."""
        context = SummaryContext(
            l1_overall="Overall summary",
            l2_chapter="Chapter summary",
            l3_recent="Recent scene summary",
        )
        result = context.to_dict()
        assert result == {
            "summary_l1": "Overall summary",
            "summary_l2": "Chapter summary",
            "summary_l3": "Recent scene summary",
        }

    def test_to_dict_with_none_values(self):
        """Test to_dict with None values."""
        context = SummaryContext(l1_overall="Overall")
        result = context.to_dict()
        assert result == {
            "summary_l1": "Overall",
            "summary_l2": None,
            "summary_l3": None,
        }


class TestSummaryCollectorCollect:
    """Test SummaryCollector.collect() method."""

    def test_collect_all_present(self, tmp_path: Path):
        """Test collect() when L1/L2/L3 all exist."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        # Create summary files
        (summary_dir / "l1_overall.md").write_text("L1 overall summary")
        (summary_dir / "l2_chapter01.md").write_text("L2 chapter summary")
        (summary_dir / "l3_ep009.md").write_text("L3 recent summary")

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.l1_overall == "L1 overall summary"
        assert result.l2_chapter == "L2 chapter summary"
        assert result.l3_recent == "L3 recent summary"

    def test_collect_l1_only(self, tmp_path: Path):
        """Test collect() when only L1 exists (L2/L3 missing)."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        (summary_dir / "l1_overall.md").write_text("L1 overall summary")

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.l1_overall == "L1 overall summary"
        assert result.l2_chapter is None
        assert result.l3_recent is None

    def test_collect_all_missing(self, tmp_path: Path):
        """Test collect() when all summaries are missing."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.l1_overall is None
        assert result.l2_chapter is None
        assert result.l3_recent is None


class TestSummaryCollectorL2:
    """Test SummaryCollector._collect_l2() method."""

    def test_collect_l2_no_chapter_id(self, tmp_path: Path):
        """Test _collect_l2() when chapter_id is None."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010")

        # Act
        result = collector._collect_l2(scene)

        # Assert
        assert result is None

    def test_collect_l2_with_chapter_id(self, tmp_path: Path):
        """Test _collect_l2() with chapter_id."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        (summary_dir / "l2_chapter01.md").write_text("Chapter 01 summary")

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector._collect_l2(scene)

        # Assert
        assert result == "Chapter 01 summary"


class TestSummaryCollectorL3:
    """Test SummaryCollector._collect_l3() method."""

    def test_collect_l3_with_previous_episode(self, tmp_path: Path):
        """Test _collect_l3() when previous episode summary exists."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        (summary_dir / "l3_ep009.md").write_text("Previous episode summary")

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010")

        # Act
        result = collector._collect_l3(scene)

        # Assert
        assert result == "Previous episode summary"

    def test_collect_l3_first_episode(self, tmp_path: Path):
        """Test _collect_l3() when it's the first episode (no previous)."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep001")

        # Act
        result = collector._collect_l3(scene)

        # Assert
        assert result is None


class TestGetPreviousEpisodeId:
    """Test SummaryCollector._get_previous_episode_id() method."""

    def test_get_previous_episode_id_standard(self, tmp_path: Path):
        """Test _get_previous_episode_id() with standard format (ep010 -> ep009)."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)

        # Act
        result = collector._get_previous_episode_id("ep010")

        # Assert
        assert result == "ep009"

    def test_get_previous_episode_id_first_episode(self, tmp_path: Path):
        """Test _get_previous_episode_id() with ep001 returns None."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)

        # Act
        result = collector._get_previous_episode_id("ep001")

        # Assert
        assert result is None

    def test_get_previous_episode_id_numeric_only(self, tmp_path: Path):
        """Test _get_previous_episode_id() with numeric format (010 -> 009)."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)

        # Act
        result = collector._get_previous_episode_id("010")

        # Assert
        assert result == "009"

    def test_get_previous_episode_id_episode_prefix(self, tmp_path: Path):
        """Test _get_previous_episode_id() with 'episode' prefix."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)

        # Act
        result = collector._get_previous_episode_id("episode010")

        # Assert
        assert result == "episode009"

    def test_get_previous_episode_id_invalid_format(self, tmp_path: Path):
        """Test _get_previous_episode_id() with invalid format returns None."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)

        # Act
        result = collector._get_previous_episode_id("invalid")

        # Assert
        assert result is None


class TestSummaryCollectorAsString:
    """Test SummaryCollector.collect_as_string() method."""

    def test_collect_as_string_all_present(self, tmp_path: Path):
        """Test collect_as_string() with all summaries."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        (summary_dir / "l1_overall.md").write_text("L1 overall")
        (summary_dir / "l2_chapter01.md").write_text("L2 chapter")
        (summary_dir / "l3_ep009.md").write_text("L3 recent")

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is not None
        assert "## 全体要約（L1）" in result
        assert "L1 overall" in result
        assert "## 章要約（L2）" in result
        assert "L2 chapter" in result
        assert "## 直近シーン要約（L3）" in result
        assert "L3 recent" in result

    def test_collect_as_string_l1_only(self, tmp_path: Path):
        """Test collect_as_string() with L1 only."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        (summary_dir / "l1_overall.md").write_text("L1 overall")

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is not None
        assert "## 全体要約（L1）" in result
        assert "L1 overall" in result
        assert "## 章要約（L2）" not in result
        assert "## 直近シーン要約（L3）" not in result

    def test_collect_as_string_all_missing(self, tmp_path: Path):
        """Test collect_as_string() when all summaries are missing."""
        # Arrange
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        summary_dir = vault_root / "_summary"
        summary_dir.mkdir()

        loader = FileLazyLoader(vault_root)
        collector = SummaryCollector(vault_root, loader)
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is None
