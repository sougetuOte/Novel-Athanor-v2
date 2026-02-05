"""StyleGuideRepository and StyleProfileRepository.

Repositories for style guide and style profile YAML files.
"""

from pathlib import Path

import yaml

from src.core.models.style import StyleGuide, StyleProfile
from src.core.repositories.base import BaseRepository


class StyleGuideRepository(BaseRepository[StyleGuide]):
    """Style guide repository.

    Style guides are stored as YAML files.
    Path: {vault_root}/_style_guides/{work}.yaml
    """

    def _get_path(self, identifier: str) -> Path:
        """Get style guide file path.

        Args:
            identifier: Work name

        Returns:
            Path to style guide YAML file
        """
        return self.vault_root / "_style_guides" / f"{identifier}.yaml"

    def _model_class(self) -> type[StyleGuide]:
        """Return StyleGuide class."""
        return StyleGuide

    def _get_identifier(self, entity: StyleGuide) -> str:
        """Get work name as identifier."""
        return entity.work

    def _read(self, path: Path) -> StyleGuide:
        """Read style guide from YAML file.

        Args:
            path: File path

        Returns:
            StyleGuide model

        Note:
            Overrides BaseRepository._read() since StyleGuide uses pure YAML
            format instead of Markdown+frontmatter.
        """
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return StyleGuide(**data)

    def _write(self, path: Path, entity: StyleGuide) -> None:
        """Write style guide to YAML file.

        Args:
            path: File path
            entity: StyleGuide to write

        Note:
            Overrides BaseRepository._write() since StyleGuide uses pure YAML
            format instead of Markdown+frontmatter.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = entity.model_dump(mode="json")
        yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        path.write_text(yaml_content, encoding="utf-8")


class StyleProfileRepository(BaseRepository[StyleProfile]):
    """Style profile repository.

    Style profiles are stored as YAML files.
    Path: {vault_root}/_style_profiles/{work}.yaml
    """

    def _get_path(self, identifier: str) -> Path:
        """Get style profile file path.

        Args:
            identifier: Work name

        Returns:
            Path to style profile YAML file
        """
        return self.vault_root / "_style_profiles" / f"{identifier}.yaml"

    def _model_class(self) -> type[StyleProfile]:
        """Return StyleProfile class."""
        return StyleProfile

    def _get_identifier(self, entity: StyleProfile) -> str:
        """Get work name as identifier."""
        return entity.work

    def _read(self, path: Path) -> StyleProfile:
        """Read style profile from YAML file.

        Args:
            path: File path

        Returns:
            StyleProfile model

        Note:
            Overrides BaseRepository._read() since StyleProfile uses pure YAML
            format instead of Markdown+frontmatter.
        """
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return StyleProfile(**data)

    def _write(self, path: Path, entity: StyleProfile) -> None:
        """Write style profile to YAML file.

        Args:
            path: File path
            entity: StyleProfile to write

        Note:
            Overrides BaseRepository._write() since StyleProfile uses pure YAML
            format instead of Markdown+frontmatter.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = entity.model_dump(mode="json")
        yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        path.write_text(yaml_content, encoding="utf-8")
