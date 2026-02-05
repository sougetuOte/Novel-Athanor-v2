"""Tests for Foreshadowing repository."""

from pathlib import Path

import pytest

from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingSeed,
    ForeshadowingStatus,
    ForeshadowingType,
)
from src.core.repositories.foreshadowing import ForeshadowingRepository


class TestForeshadowingRepository:
    """ForeshadowingRepository クラスのテスト."""

    @pytest.fixture
    def repo(self, tmp_path: Path) -> ForeshadowingRepository:
        """テスト用リポジトリを作成する."""
        return ForeshadowingRepository(tmp_path, "テスト作品")

    @pytest.fixture
    def sample_foreshadowing(self) -> Foreshadowing:
        """テスト用の伏線を作成する."""
        return Foreshadowing(
            id="FS-03-rocket",
            title="主人公の出生の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=7,
            seed=ForeshadowingSeed(
                content="主人公が古びたロケットを持っている",
            ),
        )

    def test_create_and_read(
        self, repo: ForeshadowingRepository, sample_foreshadowing: Foreshadowing
    ) -> None:
        """伏線を作成して読み込める."""
        repo.create(sample_foreshadowing)

        result = repo.read("FS-03-rocket")
        assert result.id == "FS-03-rocket"
        assert result.title == "主人公の出生の秘密"
        assert result.fs_type == ForeshadowingType.CHARACTER_SECRET
        assert result.status == ForeshadowingStatus.PLANTED

    def test_read_not_found(self, repo: ForeshadowingRepository) -> None:
        """存在しない伏線を読み込むと例外が発生する."""
        from src.core.repositories.base import EntityNotFoundError

        with pytest.raises(EntityNotFoundError):
            repo.read("NOT-EXISTS")

    def test_update(
        self, repo: ForeshadowingRepository, sample_foreshadowing: Foreshadowing
    ) -> None:
        """伏線を更新できる."""
        repo.create(sample_foreshadowing)

        # ステータスを更新
        sample_foreshadowing.status = ForeshadowingStatus.REVEALED
        repo.update(sample_foreshadowing)

        result = repo.read("FS-03-rocket")
        assert result.status == ForeshadowingStatus.REVEALED

    def test_delete(
        self, repo: ForeshadowingRepository, sample_foreshadowing: Foreshadowing
    ) -> None:
        """伏線を削除できる."""
        repo.create(sample_foreshadowing)
        assert repo.exists("FS-03-rocket")

        repo.delete("FS-03-rocket")
        assert not repo.exists("FS-03-rocket")

    def test_list_all(self, repo: ForeshadowingRepository) -> None:
        """すべての伏線をリストできる."""
        fs1 = Foreshadowing(
            id="FS-01-test1",
            title="テスト1",
            fs_type=ForeshadowingType.PLOT_TWIST,
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=5,
        )
        fs2 = Foreshadowing(
            id="FS-02-test2",
            title="テスト2",
            fs_type=ForeshadowingType.WORLD_REVEAL,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=3,
        )

        repo.create(fs1)
        repo.create(fs2)

        all_fs = repo.list_all()
        assert len(all_fs) == 2
        ids = [fs.id for fs in all_fs]
        assert "FS-01-test1" in ids
        assert "FS-02-test2" in ids

    def test_list_by_status(self, repo: ForeshadowingRepository) -> None:
        """ステータスで伏線をフィルタできる."""
        fs1 = Foreshadowing(
            id="FS-01-test1",
            title="テスト1",
            fs_type=ForeshadowingType.PLOT_TWIST,
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=5,
        )
        fs2 = Foreshadowing(
            id="FS-02-test2",
            title="テスト2",
            fs_type=ForeshadowingType.WORLD_REVEAL,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=3,
        )
        fs3 = Foreshadowing(
            id="FS-03-test3",
            title="テスト3",
            fs_type=ForeshadowingType.ITEM_SIGNIFICANCE,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=4,
        )

        repo.create(fs1)
        repo.create(fs2)
        repo.create(fs3)

        planted = repo.list_by_status(ForeshadowingStatus.PLANTED)
        assert len(planted) == 2

        registered = repo.list_by_status(ForeshadowingStatus.REGISTERED)
        assert len(registered) == 1

    def test_exists(
        self, repo: ForeshadowingRepository, sample_foreshadowing: Foreshadowing
    ) -> None:
        """伏線の存在確認ができる."""
        assert not repo.exists("FS-03-rocket")

        repo.create(sample_foreshadowing)
        assert repo.exists("FS-03-rocket")

    def test_registry_file_created(
        self, repo: ForeshadowingRepository, sample_foreshadowing: Foreshadowing
    ) -> None:
        """registry.yaml ファイルが作成される."""
        repo.create(sample_foreshadowing)

        registry_path = repo.vault_root / "テスト作品" / "_foreshadowing" / "registry.yaml"
        assert registry_path.exists()

    def test_create_duplicate_raises_error(
        self, repo: ForeshadowingRepository, sample_foreshadowing: Foreshadowing
    ) -> None:
        """重複する ID の伏線を作成すると例外が発生する."""
        from src.core.repositories.base import EntityExistsError

        repo.create(sample_foreshadowing)

        with pytest.raises(EntityExistsError):
            repo.create(sample_foreshadowing)
