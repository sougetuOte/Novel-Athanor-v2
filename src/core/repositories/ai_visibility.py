"""AIVisibilityRepository.

Repository for AI visibility configuration (visibility.yaml).
"""

from pathlib import Path

import yaml

from src.core.models.ai_visibility import VisibilityConfig
from src.core.repositories.base import BaseRepository


class AIVisibilityRepository(BaseRepository[VisibilityConfig]):
    """AI visibility repository.

    Visibility configs are stored as YAML files.
    Path: {vault_root}/_ai_control/visibility.yaml

    Note:
        This repository manages a single visibility config file per vault.
        The identifier is always "visibility" (the filename without extension).
    """

    def _get_path(self, identifier: str = "visibility") -> Path:
        """Get visibility config file path.

        Args:
            identifier: Always "visibility" (ignored, included for compatibility)

        Returns:
            Path to visibility.yaml
        """
        return self.vault_root / "_ai_control" / "visibility.yaml"

    def _model_class(self) -> type[VisibilityConfig]:
        """Return VisibilityConfig class."""
        return VisibilityConfig

    def _get_identifier(self, entity: VisibilityConfig) -> str:
        """Get identifier (always 'visibility')."""
        return "visibility"

    def _read(self, path: Path) -> VisibilityConfig:
        """Read visibility config from YAML file.

        Args:
            path: File path

        Returns:
            VisibilityConfig model

        Note:
            Overrides BaseRepository._read() since VisibilityConfig uses pure YAML
            format instead of Markdown+frontmatter.
        """
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return VisibilityConfig(**data)

    def _write(self, path: Path, entity: VisibilityConfig) -> None:
        """Write visibility config to YAML file.

        Args:
            path: File path
            entity: VisibilityConfig to write

        Note:
            Overrides BaseRepository._write() since VisibilityConfig uses pure YAML
            format instead of Markdown+frontmatter.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = entity.model_dump(mode="json")
        yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        path.write_text(yaml_content, encoding="utf-8")

    # Convenience methods for singleton-like access

    def read(self, identifier: str = "visibility") -> VisibilityConfig:
        """Read visibility config.

        Args:
            identifier: Ignored (always reads visibility.yaml)

        Returns:
            VisibilityConfig

        Raises:
            EntityNotFoundError: If visibility.yaml does not exist
        """
        return super().read(identifier)

    def delete(self, identifier: str = "visibility") -> None:
        """Delete visibility config.

        Args:
            identifier: Ignored (always deletes visibility.yaml)

        Raises:
            EntityNotFoundError: If visibility.yaml does not exist
        """
        return super().delete(identifier)

    def exists(self, identifier: str = "visibility") -> bool:
        """Check if visibility config exists.

        Args:
            identifier: Ignored (always checks visibility.yaml)

        Returns:
            True if visibility.yaml exists
        """
        return super().exists(identifier)
