"""SummaryRepository.

Summary エンティティの CRUD 操作を行うリポジトリ。
3階層のサマリ（L1/L2/L3）を統一的に扱う。
"""

from pathlib import Path
from typing import Literal

from src.core.models.summary import SummaryL1, SummaryL2, SummaryL3
from src.core.repositories.base import BaseRepository
from src.core.vault.path_resolver import VaultPathResolver

Summary = SummaryL1 | SummaryL2 | SummaryL3


class SummaryRepository(BaseRepository[Summary]):
    """Summary リポジトリ.

    Note:
        L3 summaries の場合、chapter_name が SummaryL3 モデルに含まれていないため、
        ファイルパスから推測するか、create 時に別途指定する必要がある。
        現在の実装では、L3 ディレクトリ名から chapter_name を抽出している。
    """

    def __init__(self, vault_root: Path) -> None:
        """初期化."""
        super().__init__(vault_root)
        self._path_resolver = VaultPathResolver(vault_root)

    def _get_path(self, identifier: str) -> Path:
        """識別子からファイルパスを取得.

        Args:
            identifier:
                - "L1"
                - "L2-{chapter_number}-{chapter_name}"
                - "L3-{chapter_number}-{chapter_name}-{sequence_number}"

        Returns:
            ファイルパス
        """
        parts = identifier.split("-", maxsplit=3)
        level = parts[0]

        if level == "L1":
            return self._path_resolver.resolve_summary("L1")
        elif level == "L2":
            chapter_number = int(parts[1])
            chapter_name = parts[2]
            return self._path_resolver.resolve_summary(
                "L2", chapter_number=chapter_number, chapter_name=chapter_name
            )
        else:  # L3
            chapter_number = int(parts[1])
            chapter_name = parts[2]
            sequence_number = int(parts[3])
            return self._path_resolver.resolve_summary(
                "L3",
                chapter_number=chapter_number,
                chapter_name=chapter_name,
                sequence_number=sequence_number,
            )

    def _model_class(self) -> type[Summary]:
        """Summary クラスを返す.

        Note:
            実際には Union 型だが、_read() で適切な型を返す。
        """
        return SummaryL1

    def _get_identifier(self, entity: Summary) -> str:
        """サマリから識別子を生成.

        Note:
            L3 の場合、chapter_name が必要だが SummaryL3 モデルには含まれていない。
            create() や update() で L3 を扱う場合、ディレクトリから chapter_name を
            自動推測する。
        """
        if entity.level == "L1":
            return "L1"
        elif entity.level == "L2":
            return f"L2-{entity.chapter_number}-{entity.chapter_name}"
        else:  # L3
            # L3 の場合、chapter_name を取得
            chapter_name = self._get_chapter_name_for_l3(entity.chapter_number)
            return f"L3-{entity.chapter_number}-{chapter_name}-{entity.sequence_number}"

    def _read(self, path: Path) -> Summary:
        """ファイルからモデルを読み込み.

        適切な Summary サブクラス (L1/L2/L3) を返す。
        content フィールドは frontmatter から除去し、body を使用する。
        """
        file_content = path.read_text(encoding="utf-8")
        from src.core.parsers.frontmatter import parse_frontmatter

        fm, body = parse_frontmatter(file_content)

        # content が frontmatter に残っている場合は除去し、body を優先
        fm.pop("content", None)
        level = fm.get("level", "L1")

        if level == "L1":
            return SummaryL1(**fm, content=body)
        elif level == "L2":
            return SummaryL2(**fm, content=body)
        else:
            return SummaryL3(**fm, content=body)

    def get_by_level(self, level: Literal["L1", "L2", "L3"]) -> list[Summary]:
        """指定レベルのサマリを取得.

        Args:
            level: サマリレベル

        Returns:
            指定レベルのサマリのリスト
        """
        summaries = self.list_all()
        return [s for s in summaries if s.level == level]

    def read(self, identifier: str) -> Summary:
        """エンティティを読み込み.

        L3 の場合は特別な処理が必要。
        """
        return super().read(identifier)

    def _get_chapter_name_for_l3(self, chapter_number: int) -> str:
        """L3 用に chapter_name を取得.

        L2 から chapter_name を検索するか、ディレクトリから推測する。
        """
        # まず L2 から探す
        l2_dir = self.vault_root / "_summary" / "L2_chapters"
        if l2_dir.exists():
            for path in l2_dir.glob(f"{chapter_number:02d}_*.md"):
                # ファイル名から chapter_name を抽出
                # Format: "01_Chapter Name.md"
                name_part = path.stem.split("_", 1)[1]
                return name_part

        # L2 がない場合、L3 ディレクトリから推測
        l3_dir = self.vault_root / "_summary" / "L3_sequences"
        if l3_dir.exists():
            for chapter_dir in l3_dir.iterdir():
                if chapter_dir.is_dir() and chapter_dir.name.startswith(
                    f"{chapter_number:02d}_"
                ):
                    return chapter_dir.name.split("_", 1)[1]

        # 見つからない場合はデフォルト
        return "Chapter"

    def _serialize(self, entity: Summary) -> str:
        """Summary を Markdown 形式にシリアライズ.

        content フィールドを body として扱う。
        """
        data = entity.model_dump(mode="json")
        body = data.pop("content", "")
        data.pop("body", "")

        import yaml

        yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        return f"---\n{yaml_content}---\n\n{body}"

    def list_all(self) -> list[Summary]:
        """全サマリを取得.

        Returns:
            サマリのリスト（L1, L2, L3 すべて）
        """
        summaries: list[Summary] = []

        summary_dir = self.vault_root / "_summary"
        if not summary_dir.exists():
            return []

        # L1: _summary/L1_overall.md
        l1_path = summary_dir / "L1_overall.md"
        if l1_path.exists():
            summaries.append(self._read(l1_path))

        # L2: _summary/L2_chapters/*.md
        l2_dir = summary_dir / "L2_chapters"
        if l2_dir.exists():
            for path in l2_dir.glob("*.md"):
                summaries.append(self._read(path))

        # L3: _summary/L3_sequences/*/*.md
        l3_dir = summary_dir / "L3_sequences"
        if l3_dir.exists():
            for chapter_dir in l3_dir.iterdir():
                if chapter_dir.is_dir():
                    for path in chapter_dir.glob("*.md"):
                        summaries.append(self._read(path))

        return summaries
