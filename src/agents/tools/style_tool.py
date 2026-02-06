"""Style analysis tool.

Provides CLI tools for analyzing and saving style guides/profiles.
Used by the Style Agent to generate StyleGuide and StyleProfile from episode texts.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.core.models.style import StyleGuide


def collect_episode_texts(
    vault_root: Path,
    work: str,
    episode_ids: list[int] | None = None,
) -> list[str]:
    """Collect episode texts from vault.

    Args:
        vault_root: Vault root directory path.
        work: Work name.
        episode_ids: Episode IDs to collect (None = all episodes).

    Returns:
        List of episode body texts (frontmatter excluded).
    """
    episodes_dir = vault_root / work / "episodes"
    if not episodes_dir.exists():
        return []

    # エピソードファイルを収集
    episode_files = sorted(episodes_dir.glob("ep_*.md"))

    if episode_ids is not None:
        # episode_ids でフィルタ
        episode_set = set(episode_ids)
        filtered = []
        for ep_file in episode_files:
            # ep_001.md → 1
            match = re.match(r"ep_(\d+)\.md", ep_file.name)
            if match:
                ep_num = int(match.group(1))
                if ep_num in episode_set:
                    filtered.append(ep_file)
        episode_files = filtered

    texts = []
    for ep_file in episode_files:
        content = ep_file.read_text(encoding="utf-8")
        # frontmatter (--- ... ---) を除去
        body = _extract_body(content)
        texts.append(body)

    return texts


def _extract_body(content: str) -> str:
    """Extract body text from markdown with frontmatter.

    Args:
        content: Markdown content with frontmatter.

    Returns:
        Body text (frontmatter excluded).
    """
    # frontmatter: --- ... ---
    pattern = r"^---\s*\n.*?\n---\s*\n"
    body = re.sub(pattern, "", content, count=1, flags=re.DOTALL)
    return body.strip()


def load_existing_guide(vault_root: Path, work: str) -> StyleGuide | None:
    """Load existing StyleGuide from vault.

    Args:
        vault_root: Vault root directory path.
        work: Work name.

    Returns:
        StyleGuide if exists, otherwise None.
    """
    guide_file = vault_root / work / "_style_guides" / f"{work}.yaml"
    if not guide_file.exists():
        return None

    import yaml

    with guide_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return StyleGuide(**data)


def run_analyze_style(
    vault_root: Path,
    work: str,
    episode_ids: list[int] | None = None,
) -> str:
    """Run style analysis and return prompt text.

    Args:
        vault_root: Vault root directory path.
        work: Work name.
        episode_ids: Episode IDs to analyze (None = all episodes).

    Returns:
        Prompt text for LLM style analysis.
    """
    # エピソードテキスト収集
    texts = collect_episode_texts(vault_root, work, episode_ids)

    # 既存ガイド読み込み
    existing_guide = load_existing_guide(vault_root, work)

    # E-1 で定義される format_style_analysis_context() を使用
    # 並行作業のため、このタイミングでは存在しない可能性がある
    # その場合は簡易フォーマットで対応
    try:
        from src.agents.prompts.style_agent import format_style_analysis_context

        return format_style_analysis_context(texts, existing_guide)
    except ImportError:
        # E-1 が未完了の場合の fallback
        combined = "\n\n---\n\n".join(texts)
        prompt = f"## 分析対象テキスト\n\n{combined}"
        if existing_guide:
            prompt += f"\n\n## 既存ガイド\n\n作品: {existing_guide.work}"
        return prompt


def run_save_style(
    vault_root: Path,
    work: str,
    style_type: str,
    input_path: Path,
) -> None:
    """Save StyleGuide or StyleProfile to vault.

    Args:
        vault_root: Vault root directory path.
        work: Work name.
        style_type: "guide" or "profile".
        input_path: Path to LLM output text file.
    """
    import yaml

    from src.agents.parsers.style_parser import (
        parse_style_guide_output,
        parse_style_profile_output,
    )
    from src.core.models.style import StyleProfile

    input_text = input_path.read_text(encoding="utf-8")

    model: StyleGuide | StyleProfile
    if style_type == "guide":
        model = parse_style_guide_output(input_text)
        subdir = "_style_guides"
    elif style_type == "profile":
        model = parse_style_profile_output(input_text)
        subdir = "_style_profiles"
    else:
        raise ValueError(f"Invalid style_type: {style_type}")

    save_dir = vault_root / work / subdir
    save_dir.mkdir(parents=True, exist_ok=True)
    save_file = save_dir / f"{work}.yaml"

    with save_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(model.model_dump(mode="json", exclude_none=True), f, allow_unicode=True)
