"""Tests for src/agents/tools/style_tool.py."""

from __future__ import annotations

from pathlib import Path

from src.agents.tools.style_tool import (
    collect_episode_texts,
    load_existing_guide,
    run_analyze_style,
    run_save_style,
)


def test_collect_episode_texts_reads_episodes(tmp_path: Path) -> None:
    """エピソードファイルを読み込み、本文を返す."""
    vault_root = tmp_path / "vault"
    work_dir = vault_root / "test_work" / "episodes"
    work_dir.mkdir(parents=True)

    # エピソードファイル作成（frontmatter + 本文）
    ep1 = work_dir / "ep_001.md"
    ep1.write_text(
        "---\ntitle: エピソード1\n---\n\n本文1の内容です。",
        encoding="utf-8",
    )
    ep2 = work_dir / "ep_002.md"
    ep2.write_text(
        "---\ntitle: エピソード2\n---\n\n本文2の内容です。",
        encoding="utf-8",
    )

    texts = collect_episode_texts(vault_root, "test_work", episode_ids=None)

    assert len(texts) == 2
    assert "本文1の内容です。" in texts[0]
    assert "本文2の内容です。" in texts[1]
    # frontmatter は除外されている
    assert "title: エピソード1" not in texts[0]
    assert "title: エピソード2" not in texts[1]


def test_collect_episode_texts_filters_by_episode_ids(tmp_path: Path) -> None:
    """指定したエピソード ID のみ収集する."""
    vault_root = tmp_path / "vault"
    work_dir = vault_root / "test_work" / "episodes"
    work_dir.mkdir(parents=True)

    # 3つのエピソード作成
    for i in [1, 2, 3]:
        ep = work_dir / f"ep_{i:03d}.md"
        ep.write_text(
            f"---\ntitle: エピソード{i}\n---\n\n本文{i}の内容です。",
            encoding="utf-8",
        )

    texts = collect_episode_texts(vault_root, "test_work", episode_ids=[1, 3])

    assert len(texts) == 2
    assert "本文1の内容です。" in texts[0]
    assert "本文3の内容です。" in texts[1]
    assert not any("本文2" in t for t in texts)


def test_collect_episode_texts_returns_empty_if_no_episodes(tmp_path: Path) -> None:
    """エピソードがない場合は空リストを返す."""
    vault_root = tmp_path / "vault"
    work_dir = vault_root / "test_work" / "episodes"
    work_dir.mkdir(parents=True)

    texts = collect_episode_texts(vault_root, "test_work", episode_ids=None)

    assert texts == []


def test_load_existing_guide_returns_guide_if_exists(tmp_path: Path) -> None:
    """ファイルが存在する場合に StyleGuide を返す."""
    vault_root = tmp_path / "vault"
    style_dir = vault_root / "test_work" / "_style_guides"
    style_dir.mkdir(parents=True)

    guide_file = style_dir / "test_work.yaml"
    guide_file.write_text(
        """work: test_work
pov: third_person
tense: past
style_characteristics:
  - カジュアルな口調
avoid_expressions:
  - 「〜である」
""",
        encoding="utf-8",
    )

    guide = load_existing_guide(vault_root, "test_work")

    assert guide is not None
    assert guide.work == "test_work"
    assert len(guide.style_characteristics) == 1
    assert len(guide.avoid_expressions) == 1


def test_load_existing_guide_returns_none_if_not_exists(tmp_path: Path) -> None:
    """ファイルがない場合は None を返す."""
    vault_root = tmp_path / "vault"

    guide = load_existing_guide(vault_root, "test_work")

    assert guide is None


def test_run_analyze_style_returns_prompt_text(tmp_path: Path) -> None:
    """プロンプトテキストを返す."""
    vault_root = tmp_path / "vault"
    work_dir = vault_root / "test_work" / "episodes"
    work_dir.mkdir(parents=True)

    # エピソードファイル作成
    ep1 = work_dir / "ep_001.md"
    ep1.write_text(
        "---\ntitle: エピソード1\n---\n\n本文1の内容です。",
        encoding="utf-8",
    )

    prompt = run_analyze_style(vault_root, "test_work", episode_ids=None)

    # プロンプトにエピソードテキストが含まれる
    assert "本文1の内容です。" in prompt
    # formatter の出力構造を確認（E-1 で定義される形式）
    assert "## 分析対象テキスト" in prompt or "分析対象" in prompt


def test_run_save_style_saves_style_guide(tmp_path: Path) -> None:
    """StyleGuide を vault に保存する."""
    vault_root = tmp_path / "vault"

    # 入力ファイル作成（LLM出力）— YAML コードブロック形式
    input_file = tmp_path / "guide_output.txt"
    input_file.write_text(
        """```yaml
work: test_work
pov: third_person
tense: past
style_characteristics:
  - カジュアルな口調
avoid_expressions:
  - 「〜である」
```""",
        encoding="utf-8",
    )

    run_save_style(vault_root, "test_work", style_type="guide", input_path=input_file)

    # 保存されたファイルを確認
    saved_file = vault_root / "test_work" / "_style_guides" / "test_work.yaml"
    assert saved_file.exists()

    # パース確認
    import yaml

    with saved_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["work"] == "test_work"
    assert len(data["style_characteristics"]) == 1


def test_run_save_style_saves_style_profile(tmp_path: Path) -> None:
    """StyleProfile を vault に保存する."""
    vault_root = tmp_path / "vault"

    # 入力ファイル作成（LLM出力）— YAML コードブロック形式
    input_file = tmp_path / "profile_output.txt"
    input_file.write_text(
        """```yaml
work: test_work
avg_sentence_length: 25.5
dialogue_ratio: 0.35
ttr: 0.68
frequent_words:
  - 彼
  - 彼女
```""",
        encoding="utf-8",
    )

    run_save_style(vault_root, "test_work", style_type="profile", input_path=input_file)

    # 保存されたファイルを確認
    saved_file = vault_root / "test_work" / "_style_profiles" / "test_work.yaml"
    assert saved_file.exists()

    # パース確認
    import yaml

    with saved_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["work"] == "test_work"
    assert data["avg_sentence_length"] == 25.5
