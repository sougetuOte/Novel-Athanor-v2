"""SettingsRepository.

Repository for work-level settings (settings.yaml).
"""

from pathlib import Path

import yaml

from src.core.models.settings import Settings
from src.core.repositories.base import (
    BaseRepository,
)


class SettingsRepository(BaseRepository[Settings]):
    """Settings repository.

    Settings are stored as YAML files (not Markdown+frontmatter).
    Path: {vault_root}/settings.yaml
    """

    def _get_path(self, identifier: str) -> Path:
        """Get settings file path.

        Args:
            identifier: Work ID (used as identifier)

        Returns:
            Path to settings.yaml
        """
        return self.vault_root / "settings.yaml"

    def _model_class(self) -> type[Settings]:
        """Return Settings class."""
        return Settings

    def _get_identifier(self, entity: Settings) -> str:
        """Get work_id as identifier."""
        return entity.work_id

    def _read(self, path: Path) -> Settings:
        """Read settings from YAML file.

        Args:
            path: File path

        Returns:
            Settings model

        Note:
            Overrides BaseRepository._read() since Settings uses pure YAML
            format instead of Markdown+frontmatter.
        """
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return Settings(**data)

    def _write(self, path: Path, entity: Settings) -> None:
        """Write settings to YAML file.

        Args:
            path: File path
            entity: Settings to write

        Note:
            Overrides BaseRepository._write() since Settings uses pure YAML
            format instead of Markdown+frontmatter.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = entity.model_dump(mode="json")
        yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        path.write_text(yaml_content, encoding="utf-8")
