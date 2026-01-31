"""Tests for LazyLoader protocol and related classes."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Optional

from src.core.context.lazy_loader import (
    ContentType,
    LazyLoadedContent,
    LazyLoader,
    LazyLoadResult,
    LoadPriority,
)


class TestLoadPriority:
    """Test LoadPriority enum."""

    def test_required_exists(self):
        """REQUIRED 優先度が存在する."""
        assert LoadPriority.REQUIRED.value == "required"

    def test_optional_exists(self):
        """OPTIONAL 優先度が存在する."""
        assert LoadPriority.OPTIONAL.value == "optional"

    def test_all_priorities(self):
        """全ての優先度が定義されている."""
        priorities = [p for p in LoadPriority]
        assert len(priorities) == 2


class TestLazyLoadResult:
    """Test LazyLoadResult data class."""

    def test_create_success_result(self):
        """成功結果を生成できる."""
        result = LazyLoadResult(success=True, data="test_data")
        assert result.success is True
        assert result.data == "test_data"
        assert result.error is None
        assert result.warnings == []

    def test_create_failure_result(self):
        """失敗結果を生成できる."""
        result = LazyLoadResult(
            success=False, data=None, error="File not found"
        )
        assert result.success is False
        assert result.data is None
        assert result.error == "File not found"

    def test_ok_factory_method(self):
        """ok() ファクトリメソッドで成功結果を生成."""
        result = LazyLoadResult.ok("test_data")
        assert result.success is True
        assert result.data == "test_data"
        assert result.error is None

    def test_ok_with_warnings(self):
        """ok() で警告付きの成功結果を生成."""
        result = LazyLoadResult.ok("test_data", warnings=["warning1", "warning2"])
        assert result.success is True
        assert result.data == "test_data"
        assert result.warnings == ["warning1", "warning2"]

    def test_fail_factory_method(self):
        """fail() ファクトリメソッドで失敗結果を生成."""
        result: LazyLoadResult[str] = LazyLoadResult.fail("Error occurred")
        assert result.success is False
        assert result.data is None
        assert result.error == "Error occurred"

    def test_generic_type(self):
        """ジェネリック型として動作する."""
        result: LazyLoadResult[int] = LazyLoadResult.ok(42)
        assert result.data == 42

        result_dict: LazyLoadResult[dict] = LazyLoadResult.ok({"key": "value"})
        assert result_dict.data == {"key": "value"}


class TestLazyLoaderProtocol:
    """Test LazyLoader protocol compliance."""

    def test_protocol_compliance(self):
        """Protocol を満たす具象クラスを作成できる."""

        class MockLazyLoader:
            """Mock implementation of LazyLoader protocol."""

            def __init__(self) -> None:
                self._cache: dict[str, str] = {}

            def load(
                self, identifier: str, priority: LoadPriority
            ) -> LazyLoadResult[str]:
                if identifier in self._cache:
                    return LazyLoadResult.ok(self._cache[identifier])
                if priority == LoadPriority.REQUIRED:
                    return LazyLoadResult.fail(f"Not found: {identifier}")
                return LazyLoadResult.ok(
                    "", warnings=[f"Optional data not found: {identifier}"]
                )

            def is_cached(self, identifier: str) -> bool:
                return identifier in self._cache

            def clear_cache(self) -> None:
                self._cache.clear()

        # Protocol 準拠を確認（型チェックで検証）
        loader: LazyLoader[str] = MockLazyLoader()

        # load メソッドが動作する
        result = loader.load("test", LoadPriority.OPTIONAL)
        assert isinstance(result, LazyLoadResult)

        # is_cached メソッドが動作する
        assert loader.is_cached("test") is False

        # clear_cache メソッドが動作する
        loader.clear_cache()

    def test_required_priority_behavior(self):
        """REQUIRED 優先度の挙動テスト."""

        class StrictLoader:
            """Loader that fails on missing required data."""

            def load(
                self, identifier: str, priority: LoadPriority
            ) -> LazyLoadResult[str]:
                # シミュレート: データが見つからない
                if priority == LoadPriority.REQUIRED:
                    return LazyLoadResult.fail("Required data not found")
                return LazyLoadResult.ok("", warnings=["Data not found"])

            def is_cached(self, identifier: str) -> bool:
                return False

            def clear_cache(self) -> None:
                pass

        loader: LazyLoader[str] = StrictLoader()
        result = loader.load("missing", LoadPriority.REQUIRED)
        assert result.success is False
        assert result.error == "Required data not found"

    def test_optional_priority_behavior(self):
        """OPTIONAL 優先度の挙動テスト."""

        class GracefulLoader:
            """Loader that warns on missing optional data."""

            def load(
                self, identifier: str, priority: LoadPriority
            ) -> LazyLoadResult[str]:
                # シミュレート: データが見つからない
                if priority == LoadPriority.OPTIONAL:
                    return LazyLoadResult.ok(
                        "", warnings=[f"Optional data '{identifier}' not found"]
                    )
                return LazyLoadResult.fail("Required data not found")

            def is_cached(self, identifier: str) -> bool:
                return False

            def clear_cache(self) -> None:
                pass

        loader: LazyLoader[str] = GracefulLoader()
        result = loader.load("missing", LoadPriority.OPTIONAL)
        assert result.success is True
        assert len(result.warnings) == 1
        assert "Optional data 'missing' not found" in result.warnings[0]


class TestLazyLoadResultHelpers:
    """Test LazyLoadResult helper methods."""

    def test_result_with_multiple_warnings(self):
        """複数警告を持つ結果."""
        result = LazyLoadResult(
            success=True,
            data="data",
            warnings=["warn1", "warn2", "warn3"],
        )
        assert len(result.warnings) == 3

    def test_empty_warnings_default(self):
        """警告のデフォルトは空リスト."""
        result = LazyLoadResult(success=True, data="data")
        assert result.warnings == []
        assert isinstance(result.warnings, list)


class TestContentType:
    """Test ContentType enum."""

    def test_content_type_values(self):
        """全種別（PLOT, SUMMARY, CHARACTER, WORLD_SETTING, STYLE_GUIDE, FORESHADOWING, REFERENCE）が存在."""
        assert ContentType.PLOT.value == "plot"
        assert ContentType.SUMMARY.value == "summary"
        assert ContentType.CHARACTER.value == "character"
        assert ContentType.WORLD_SETTING.value == "world_setting"
        assert ContentType.STYLE_GUIDE.value == "style_guide"
        assert ContentType.FORESHADOWING.value == "foreshadowing"
        assert ContentType.REFERENCE.value == "reference"

    def test_all_content_types(self):
        """全てのコンテンツタイプが定義されている."""
        content_types = [ct for ct in ContentType]
        assert len(content_types) == 7


class TestLazyLoadedContent:
    """Test LazyLoadedContent data class."""

    def test_lazy_loaded_content_creation(self):
        """基本生成（content, source_path, content_type, priority）."""
        path = Path("/vault/test/characters/hero.md")
        content = LazyLoadedContent(
            content="Test content",
            source_path=path,
            content_type=ContentType.CHARACTER,
            priority=LoadPriority.REQUIRED,
        )
        assert content.content == "Test content"
        assert content.source_path == path
        assert content.content_type == ContentType.CHARACTER
        assert content.priority == LoadPriority.REQUIRED

    def test_lazy_loaded_content_loaded_at_default(self):
        """loaded_at が現在時刻で自動設定される."""
        before = datetime.now()
        content = LazyLoadedContent(
            content="Test",
            source_path=Path("/test.md"),
            content_type=ContentType.PLOT,
            priority=LoadPriority.REQUIRED,
        )
        after = datetime.now()
        assert before <= content.loaded_at <= after

    def test_lazy_loaded_content_is_stale_true(self):
        """古いコンテンツ（max_age_seconds 超過）."""
        old_time = datetime.now() - timedelta(seconds=10)
        content = LazyLoadedContent(
            content="Old content",
            source_path=Path("/test.md"),
            content_type=ContentType.SUMMARY,
            priority=LoadPriority.OPTIONAL,
            loaded_at=old_time,
        )
        # 5秒で古くなると定義
        assert content.is_stale(max_age_seconds=5.0)

    def test_lazy_loaded_content_is_stale_false(self):
        """新しいコンテンツ."""
        content = LazyLoadedContent(
            content="Fresh content",
            source_path=Path("/test.md"),
            content_type=ContentType.CHARACTER,
            priority=LoadPriority.REQUIRED,
        )
        # デフォルト300秒では新しい
        assert not content.is_stale()

    def test_lazy_loaded_content_get_identifier_with_cache_key(self):
        """cache_key がある場合."""
        content = LazyLoadedContent(
            content="Data",
            source_path=Path("/vault/test.md"),
            content_type=ContentType.REFERENCE,
            priority=LoadPriority.OPTIONAL,
            cache_key="custom_key_123",
        )
        assert content.get_identifier() == "custom_key_123"

    def test_lazy_loaded_content_get_identifier_without_cache_key(self):
        """cache_key がない場合は source_path."""
        path = Path("/vault/world/magic.md")
        content = LazyLoadedContent(
            content="Magic system",
            source_path=path,
            content_type=ContentType.WORLD_SETTING,
            priority=LoadPriority.REQUIRED,
        )
        assert content.get_identifier() == str(path)

    def test_lazy_loaded_content_generic_type(self):
        """ジェネリック型として動作する."""
        # str型
        str_content: LazyLoadedContent[str] = LazyLoadedContent(
            content="text",
            source_path=Path("/test.md"),
            content_type=ContentType.PLOT,
            priority=LoadPriority.REQUIRED,
        )
        assert isinstance(str_content.content, str)

        # dict型
        dict_content: LazyLoadedContent[dict] = LazyLoadedContent(
            content={"key": "value"},
            source_path=Path("/test.yaml"),
            content_type=ContentType.FORESHADOWING,
            priority=LoadPriority.OPTIONAL,
        )
        assert isinstance(dict_content.content, dict)


# --- CacheEntry と FileLazyLoader のテスト ---


class TestCacheEntry:
    """Test CacheEntry data class."""

    def test_create_cache_entry(self):
        """CacheEntryを作成."""
        from src.core.context.lazy_loader import CacheEntry

        entry = CacheEntry(
            data="test content",
            loaded_at=datetime.now(),
            source=Path("test.md"),
        )
        assert entry.data == "test content"

    def test_is_expired_false(self):
        """期限切れでない."""
        from src.core.context.lazy_loader import CacheEntry

        entry = CacheEntry(
            data="test",
            loaded_at=datetime.now(),
            source=Path("test.md"),
        )
        assert not entry.is_expired(300.0)

    def test_is_expired_true(self):
        """期限切れ."""
        from src.core.context.lazy_loader import CacheEntry

        old_time = datetime.now() - timedelta(seconds=400)
        entry = CacheEntry(
            data="test",
            loaded_at=old_time,
            source=Path("test.md"),
        )
        assert entry.is_expired(300.0)


class TestFileLazyLoader:
    """Test FileLazyLoader implementation."""

    @pytest.fixture
    def vault_root(self, tmp_path):
        """テスト用vault."""
        (tmp_path / "test.md").write_text("Test content", encoding="utf-8")
        return tmp_path

    @pytest.fixture
    def loader(self, vault_root):
        from src.core.context.lazy_loader import FileLazyLoader

        return FileLazyLoader(vault_root, cache_ttl_seconds=300.0)

    def test_load_success(self, loader):
        """ファイル読み込み成功."""
        result = loader.load("test.md", LoadPriority.REQUIRED)
        assert result.success
        assert result.data == "Test content"

    def test_load_required_not_found(self, loader):
        """REQUIRED ファイルなし = エラー."""
        result = loader.load("not_exists.md", LoadPriority.REQUIRED)
        assert not result.success
        assert "not found" in result.error.lower()

    def test_load_optional_not_found(self, loader):
        """OPTIONAL ファイルなし = 警告のみ."""
        result = loader.load("not_exists.md", LoadPriority.OPTIONAL)
        assert result.success
        assert result.data is None
        assert len(result.warnings) > 0

    def test_is_cached_after_load(self, loader):
        """読み込み後はキャッシュされる."""
        assert not loader.is_cached("test.md")
        loader.load("test.md", LoadPriority.REQUIRED)
        assert loader.is_cached("test.md")

    def test_cache_hit(self, loader):
        """キャッシュヒット."""
        loader.load("test.md", LoadPriority.REQUIRED)
        # 2回目はキャッシュから
        result = loader.load("test.md", LoadPriority.REQUIRED)
        assert result.success

    def test_clear_cache(self, loader):
        """キャッシュクリア."""
        loader.load("test.md", LoadPriority.REQUIRED)
        loader.clear_cache()
        assert not loader.is_cached("test.md")

    def test_get_cache_stats(self, loader):
        """キャッシュ統計."""
        loader.load("test.md", LoadPriority.REQUIRED)
        stats = loader.get_cache_stats()
        assert stats["total"] == 1
        assert stats["expired"] == 0

    def test_evict_expired(self, loader, vault_root):
        """期限切れ削除."""
        loader.load("test.md", LoadPriority.REQUIRED)
        # 手動でキャッシュを古くする
        loader._cache["test.md"].loaded_at = datetime.now() - timedelta(seconds=400)

        evicted = loader.evict_expired()
        assert evicted == 1
        assert not loader.is_cached("test.md")


# --- GracefulLoader テスト ---


class TestGracefulLoadResult:
    """Test GracefulLoadResult data class."""

    def test_create_success_result(self):
        """成功結果を作成."""
        from src.core.context.lazy_loader import GracefulLoadResult

        result = GracefulLoadResult(success=True)
        assert result.success is True
        assert result.data == {}
        assert result.errors == []
        assert result.warnings == []
        assert result.missing_required == []
        assert result.missing_optional == []

    def test_create_with_data(self):
        """データ付き結果を作成."""
        from src.core.context.lazy_loader import GracefulLoadResult

        result = GracefulLoadResult(
            success=True,
            data={"char": "content", "plot": "plot content"},
        )
        assert result.data["char"] == "content"
        assert result.data["plot"] == "plot content"

    def test_create_failure_result(self):
        """失敗結果を作成."""
        from src.core.context.lazy_loader import GracefulLoadResult

        result = GracefulLoadResult(
            success=False,
            errors=["必須コンテキスト取得失敗: char"],
            missing_required=["char"],
        )
        assert result.success is False
        assert len(result.errors) == 1
        assert "char" in result.missing_required


class TestGracefulLoader:
    """Test GracefulLoader implementation."""

    @pytest.fixture
    def vault_root(self, tmp_path):
        """テスト用vault."""
        (tmp_path / "required1.md").write_text("Required 1 content", encoding="utf-8")
        (tmp_path / "required2.md").write_text("Required 2 content", encoding="utf-8")
        (tmp_path / "optional1.md").write_text("Optional 1 content", encoding="utf-8")
        return tmp_path

    @pytest.fixture
    def base_loader(self, vault_root):
        """基本ローダー."""
        from src.core.context.lazy_loader import FileLazyLoader

        return FileLazyLoader(vault_root)

    @pytest.fixture
    def graceful_loader(self, base_loader):
        """GracefulLoader インスタンス."""
        from src.core.context.lazy_loader import GracefulLoader

        return GracefulLoader(base_loader)

    def test_all_success(self, graceful_loader):
        """全件成功: required + optional 全て存在."""
        result = graceful_loader.load_with_graceful_degradation(
            required={"r1": "required1.md", "r2": "required2.md"},
            optional={"o1": "optional1.md"},
        )
        assert result.success is True
        assert "r1" in result.data
        assert "r2" in result.data
        assert "o1" in result.data
        assert result.errors == []
        assert result.warnings == []

    def test_required_failure(self, graceful_loader):
        """required 失敗: 必須が1件不在 → success=False."""
        result = graceful_loader.load_with_graceful_degradation(
            required={"r1": "required1.md", "missing": "not_exists.md"},
            optional={},
        )
        assert result.success is False
        assert "missing" in result.missing_required
        assert len(result.errors) > 0

    def test_optional_failure(self, graceful_loader):
        """optional 失敗: 付加的が不在 → success=True, warnings."""
        result = graceful_loader.load_with_graceful_degradation(
            required={"r1": "required1.md"},
            optional={"missing": "not_exists.md"},
        )
        assert result.success is True
        assert "r1" in result.data
        assert "missing" in result.missing_optional
        assert len(result.warnings) > 0

    def test_mixed_pattern(self, graceful_loader):
        """混合パターン: required成功、optional一部失敗."""
        result = graceful_loader.load_with_graceful_degradation(
            required={"r1": "required1.md", "r2": "required2.md"},
            optional={"o1": "optional1.md", "missing": "not_exists.md"},
        )
        assert result.success is True
        assert "r1" in result.data
        assert "r2" in result.data
        assert "o1" in result.data
        assert "missing" in result.missing_optional
        assert len(result.warnings) > 0
        assert result.errors == []

    def test_all_failure(self, graceful_loader):
        """全件失敗: 全て不在."""
        result = graceful_loader.load_with_graceful_degradation(
            required={"r1": "missing1.md"},
            optional={"o1": "missing2.md"},
        )
        assert result.success is False
        assert "r1" in result.missing_required
        assert "o1" in result.missing_optional

    def test_load_batch(self, graceful_loader):
        """バッチ読み込み."""
        from src.core.context.lazy_loader import LoadPriority

        result = graceful_loader.load_batch([
            ("r1", "required1.md", LoadPriority.REQUIRED),
            ("o1", "optional1.md", LoadPriority.OPTIONAL),
            ("missing", "not_exists.md", LoadPriority.OPTIONAL),
        ])
        assert result.success is True
        assert "r1" in result.data
        assert "o1" in result.data
        assert "missing" in result.missing_optional

    def test_empty_inputs(self, graceful_loader):
        """空入力."""
        result = graceful_loader.load_with_graceful_degradation(
            required={},
            optional={},
        )
        assert result.success is True
        assert result.data == {}
        assert result.errors == []
        assert result.warnings == []
