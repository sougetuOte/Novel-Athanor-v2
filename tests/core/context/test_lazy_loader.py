"""Tests for LazyLoader protocol and related classes."""

import pytest
from typing import Optional

from src.core.context.lazy_loader import (
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
