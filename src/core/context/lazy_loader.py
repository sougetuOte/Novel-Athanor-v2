"""Lazy loading protocol for L3 context building.

This module defines the LazyLoader protocol and related classes for
implementing lazy loading with caching and graceful degradation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Generic, Protocol, TypeVar

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


class ContentType(Enum):
    """Content type classification for lazy loading.

    Attributes:
        PLOT: Plot-related content (L1/L2/L3).
        SUMMARY: Summary content (L1/L2/L3).
        CHARACTER: Character settings and states.
        WORLD_SETTING: World setting and lore.
        STYLE_GUIDE: Writing style guidelines.
        FORESHADOWING: Foreshadowing registry and timeline.
        REFERENCE: Reference materials and notes.
    """

    PLOT = "plot"
    SUMMARY = "summary"
    CHARACTER = "character"
    WORLD_SETTING = "world_setting"
    STYLE_GUIDE = "style_guide"
    FORESHADOWING = "foreshadowing"
    REFERENCE = "reference"


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
    data: T | None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def ok(cls, data: T, warnings: list[str] | None = None) -> "LazyLoadResult[T]":
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


@dataclass
class LazyLoadedContent(Generic[T]):
    """Lazy loaded content with metadata.

    This class represents content that has been lazily loaded, including
    metadata about the source, type, priority, and cache status.

    Attributes:
        content: The actual content data.
        source_path: Path to the source file.
        content_type: Type of the content.
        priority: Load priority (REQUIRED or OPTIONAL).
        loaded_at: Timestamp when the content was loaded.
        cache_key: Optional cache key for identification.

    Examples:
        >>> content = LazyLoadedContent(
        ...     content="Character data",
        ...     source_path=Path("/vault/characters/hero.md"),
        ...     content_type=ContentType.CHARACTER,
        ...     priority=LoadPriority.REQUIRED
        ... )
        >>> content.is_stale(max_age_seconds=300)
        False
        >>> content.get_identifier()
        '/vault/characters/hero.md'
    """

    content: T
    source_path: Path
    content_type: ContentType
    priority: LoadPriority
    loaded_at: datetime = field(default_factory=datetime.now)
    cache_key: str | None = None

    def is_stale(self, max_age_seconds: float = 300.0) -> bool:
        """Check if cached content is stale.

        Args:
            max_age_seconds: Maximum cache age in seconds (default: 300).

        Returns:
            True if the content is older than max_age_seconds.
        """
        age = (datetime.now() - self.loaded_at).total_seconds()
        return age > max_age_seconds

    def get_identifier(self) -> str:
        """Get unique identifier for this content.

        Returns:
            Cache key if available, otherwise source path as string.
        """
        return self.cache_key or str(self.source_path)


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


@dataclass
class CacheEntry(Generic[T]):
    """Cache entry for lazy loaded content.

    This class represents a single cache entry with expiration tracking.

    Attributes:
        data: The cached data.
        loaded_at: Timestamp when the data was loaded.
        source: Path to the source file.

    Example:
        >>> entry = CacheEntry(
        ...     data="content",
        ...     loaded_at=datetime.now(),
        ...     source=Path("test.md")
        ... )
        >>> entry.is_expired(300.0)
        False
    """

    data: T
    loaded_at: datetime
    source: Path

    def is_expired(self, ttl_seconds: float) -> bool:
        """Check if cache entry has expired.

        Args:
            ttl_seconds: Time-to-live in seconds.

        Returns:
            True if the entry is older than ttl_seconds, False otherwise.
        """
        age = (datetime.now() - self.loaded_at).total_seconds()
        return age > ttl_seconds


class FileLazyLoader:
    """File-based lazy loader with caching.

    Implements the LazyLoader protocol for file system access with
    built-in caching and TTL support.

    Attributes:
        vault_root: Root directory for vault data.
        cache_ttl_seconds: Cache time-to-live in seconds.

    Example:
        >>> loader = FileLazyLoader(Path("/vault"), cache_ttl_seconds=300.0)
        >>> result = loader.load("test.md", LoadPriority.REQUIRED)
        >>> if result.success:
        ...     print(result.data)
    """

    def __init__(self, vault_root: Path, cache_ttl_seconds: float = 300.0):
        """Initialize FileLazyLoader.

        Args:
            vault_root: Root directory for vault data.
            cache_ttl_seconds: Cache TTL in seconds (default: 300).
        """
        self.vault_root = vault_root
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, CacheEntry[str]] = {}

    def load(self, identifier: str, priority: LoadPriority) -> LazyLoadResult[str]:
        """Load file content.

        Args:
            identifier: File path relative to vault_root.
            priority: Load priority (REQUIRED or OPTIONAL).

        Returns:
            LazyLoadResult containing the loaded data or error information.
        """
        # Check cache
        if self.is_cached(identifier):
            entry = self._cache[identifier]
            if not entry.is_expired(self.cache_ttl_seconds):
                return LazyLoadResult.ok(entry.data)

        # Load from file
        file_path = self.vault_root / identifier
        try:
            content = file_path.read_text(encoding="utf-8")
            self._cache[identifier] = CacheEntry(
                data=content,
                loaded_at=datetime.now(),
                source=file_path,
            )
            return LazyLoadResult.ok(content)
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            if priority == LoadPriority.REQUIRED:
                return LazyLoadResult.fail(error_msg)
            return LazyLoadResult(success=True, data=None, warnings=[error_msg])
        except Exception as e:
            return LazyLoadResult.fail(str(e))

    def is_cached(self, identifier: str) -> bool:
        """Check if data is already cached.

        Args:
            identifier: The identifier to check.

        Returns:
            True if the data is cached, False otherwise.
        """
        return identifier in self._cache

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with 'total' and 'expired' counts.
        """
        total = len(self._cache)
        expired = sum(
            1 for e in self._cache.values() if e.is_expired(self.cache_ttl_seconds)
        )
        return {"total": total, "expired": expired}

    def evict_expired(self) -> int:
        """Evict expired cache entries.

        Returns:
            Number of entries evicted.
        """
        expired_keys = [
            k for k, v in self._cache.items() if v.is_expired(self.cache_ttl_seconds)
        ]
        for k in expired_keys:
            del self._cache[k]
        return len(expired_keys)
