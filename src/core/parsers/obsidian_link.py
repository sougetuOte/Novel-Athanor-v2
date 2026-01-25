"""Obsidian link parser.

Obsidian の [[リンク]] 記法を解析するパーサー。
"""

import re
from dataclasses import dataclass

# Obsidian リンクのパターン
# [[target#heading|display]] or [[target#^block-id|display]]
LINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#(\^)?([^\]|]+))?(?:\|([^\]]+))?\]\]")


@dataclass
class ObsidianLink:
    """Obsidian リンクを表すデータクラス."""

    target: str
    display: str | None = None
    heading: str | None = None
    block_id: str | None = None

    @property
    def display_text(self) -> str:
        """表示テキストを取得する.

        display が設定されていればそれを返し、なければ target を返す。
        """
        return self.display if self.display else self.target

    @property
    def filename(self) -> str:
        """ファイル名部分を取得する.

        パスが含まれている場合は最後の部分を返す。
        """
        return self.target.split("/")[-1]

    def to_markdown(self) -> str:
        """Markdown リンク形式に変換する.

        Returns:
            Obsidian リンク形式の文字列
        """
        result = f"[[{self.target}"

        if self.heading:
            result += f"#{self.heading}"
        elif self.block_id:
            result += f"#^{self.block_id}"

        if self.display:
            result += f"|{self.display}"

        result += "]]"
        return result


def parse_link(link_text: str) -> ObsidianLink | None:
    """リンク文字列を解析する.

    Args:
        link_text: 解析するリンク文字列（[[...]] 形式）

    Returns:
        ObsidianLink オブジェクト、または解析できない場合は None
    """
    match = LINK_PATTERN.match(link_text)
    if not match:
        return None

    target = match.group(1).strip()
    if not target:
        return None

    is_block = match.group(2) == "^"
    anchor = match.group(3)
    display = match.group(4)

    return ObsidianLink(
        target=target,
        display=display.strip() if display else None,
        heading=anchor.strip() if anchor and not is_block else None,
        block_id=anchor.strip() if anchor and is_block else None,
    )


def extract_links(text: str) -> list[ObsidianLink]:
    """テキストからすべてのリンクを抽出する.

    Args:
        text: 解析するテキスト

    Returns:
        抽出されたリンクのリスト（出現順）
    """
    links = []
    for match in LINK_PATTERN.finditer(text):
        link = parse_link(match.group(0))
        if link:
            links.append(link)
    return links
