"""Lazy loading protocol for L3 context building.

This module defines the LazyLoader protocol and related classes for
implementing lazy loading with caching and graceful degradation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Optional, Protocol, TypeVar

T = TypeVar("T")


class LoadPriority(Enum):
    """Priority level for lazy loading.

    Used for graceful degradation: REQUIRED data must be loaded successfully,
    while OPTIONAL data can fail with a warning.

    Attributes:
        REQUIRED: Data is mandatory. Loading failure results in an error.
        OPTIONAL: Data is supplementary. Loading failure results in a warning.
    """

    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass
class LazyLoadResult(Generic[T]):
    """Result of a lazy load operation.

    This generic class wraps the result of a lazy load attempt, including
    success status, data, errors, and warnings.

    Attributes:
        success: Whether the load operation succeeded.
        data: The loaded data (None if failed).
        error: Error message if the load failed.
        warnings: List of warning messages.

    Examples:
        >>> result = LazyLoadResult.ok("loaded data")
        >>> result = LazyLoadResult.fail("File not found")
        >>> result = LazyLoadResult.ok("data", warnings=["file was stale"])
    """

    success: bool
    data: Optional[T]
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def ok(cls, data: T, warnings: Optional[list[str]] = None) -> "LazyLoadResult[T]":
        """Create a successful result.

        Args:
            data: The successfully loaded data.
            warnings: Optional list of warning messages.

        Returns:
            A LazyLoadResult indicating success.
        """
        return cls(success=True, data=data, warnings=warnings or [])

    @classmethod
    def fail(cls, error: str) -> "LazyLoadResult[T]":
        """Create a failed result.

        Args:
            error: The error message describing why the load failed.

        Returns:
            A LazyLoadResult indicating failure.
        """
        return cls(success=False, data=None, error=error)


class LazyLoader(Protocol[T]):
    """Protocol for lazy loading with caching.

    Implementations of this protocol provide lazy loading functionality
    with built-in caching and support for graceful degradation based on
    load priority.

    Methods:
        load: Load data by identifier with specified priority.
        is_cached: Check if data is already cached.
        clear_cache: Clear all cached data.

    Example implementation:
        class FileLoader:
            def __init__(self):
                self._cache = {}

            def load(self, identifier: str, priority: LoadPriority) -> LazyLoadResult[str]:
                if identifier in self._cache:
                    return LazyLoadResult.ok(self._cache[identifier])
                try:
                    data = read_file(identifier)
                    self._cache[identifier] = data
                    return LazyLoadResult.ok(data)
                except FileNotFoundError:
                    if priority == LoadPriority.REQUIRED:
                        return LazyLoadResult.fail(f"Required file not found: {identifier}")
                    return LazyLoadResult.ok("", warnings=[f"Optional file not found: {identifier}"])

            def is_cached(self, identifier: str) -> bool:
                return identifier in self._cache

            def clear_cache(self) -> None:
                self._cache.clear()
    """

    def load(self, identifier: str, priority: LoadPriority) -> LazyLoadResult[T]:
        """Load data by identifier.

        Args:
            identifier: The identifier for the data to load.
            priority: The load priority (REQUIRED or OPTIONAL).

        Returns:
            LazyLoadResult containing the loaded data or error information.
        """
        ...

    def is_cached(self, identifier: str) -> bool:
        """Check if data is already cached.

        Args:
            identifier: The identifier to check.

        Returns:
            True if the data is cached, False otherwise.
        """
        ...

    def clear_cache(self) -> None:
        """Clear all cached data."""
        ...
