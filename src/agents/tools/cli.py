"""L4 Agent CLI entry point.

Claude Code agents が Python ツールを呼び出すための CLI。
使用例: python -m src.agents.tools.cli build-context --vault-root vault/作品名 --episode 010
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .context_tool import format_context_as_markdown, run_build_context
from .review_tool import run_algorithmic_review
from .style_tool import run_analyze_style, run_save_style


def create_parser() -> argparse.ArgumentParser:
    """CLI パーサーを構築する."""
    parser = argparse.ArgumentParser(
        prog="novel-agent-tools",
        description="L4 Agent CLI ツール",
    )
    subparsers = parser.add_subparsers(dest="command", help="サブコマンド")

    # build-context
    build_parser = subparsers.add_parser("build-context", help="コンテキスト構築")
    build_parser.add_argument("--vault-root", required=True, help="Vault ルートパス")
    build_parser.add_argument("--episode", required=True, help="エピソード ID")
    build_parser.add_argument("--sequence", default=None, help="シーケンス ID")
    build_parser.add_argument("--chapter", default=None, help="チャプター ID")
    build_parser.add_argument("--phase", default=None, help="フェーズ")

    # format-context
    format_parser = subparsers.add_parser(
        "format-context", help="コンテキスト → Markdown 変換"
    )
    format_parser.add_argument(
        "--input", default="-", help="入力JSONファイル（'-' で stdin）"
    )

    # check-review
    review_parser = subparsers.add_parser(
        "check-review", help="アルゴリズミックレビュー（禁止キーワードチェック）"
    )
    review_parser.add_argument(
        "--draft", required=True, help="ドラフトテキストファイルパス（'-' で stdin）"
    )
    review_parser.add_argument(
        "--keywords", required=True, help="禁止キーワード（カンマ区切り）"
    )

    # analyze-style
    analyze_style_parser = subparsers.add_parser(
        "analyze-style", help="文体分析（エピソードテキスト → StyleGuide/Profile 生成用プロンプト）"
    )
    analyze_style_parser.add_argument(
        "--vault", required=True, help="Vault ルートパス"
    )
    analyze_style_parser.add_argument(
        "--work", required=True, help="作品名"
    )
    analyze_style_parser.add_argument(
        "--episodes", default=None, help="エピソード ID（カンマ区切り、省略時は全エピソード）"
    )

    # save-style
    save_style_parser = subparsers.add_parser(
        "save-style", help="LLM出力を StyleGuide/Profile として保存"
    )
    save_style_parser.add_argument(
        "--vault", required=True, help="Vault ルートパス"
    )
    save_style_parser.add_argument(
        "--work", required=True, help="作品名"
    )
    save_style_parser.add_argument(
        "--type", required=True, choices=["guide", "profile"], help="保存タイプ（guide or profile）"
    )
    save_style_parser.add_argument(
        "--input", required=True, help="LLM出力ファイルパス"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI メインエントリポイント.

    Args:
        argv: コマンドライン引数（None の場合 sys.argv[1:] を使用）

    Returns:
        終了コード (0: 成功, 1: エラー)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "build-context":
            result = run_build_context(
                vault_root=args.vault_root,
                episode=args.episode,
                sequence=args.sequence,
                chapter=args.chapter,
                phase=args.phase,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        elif args.command == "format-context":
            if args.input == "-":
                data = json.load(sys.stdin)
            else:
                with open(args.input, encoding="utf-8") as f:
                    data = json.load(f)
            markdown = format_context_as_markdown(data)
            print(markdown)
            return 0

        elif args.command == "check-review":
            if args.draft == "-":
                draft_text = sys.stdin.read()
            else:
                with open(args.draft, encoding="utf-8") as f:
                    draft_text = f.read()
            keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
            review_result = run_algorithmic_review(draft_text, keywords)
            print(review_result.model_dump_json(indent=2))
            return 0

        elif args.command == "analyze-style":
            vault_root = Path(args.vault)
            episode_ids = None
            if args.episodes:
                episode_ids = [int(e.strip()) for e in args.episodes.split(",") if e.strip()]
            prompt = run_analyze_style(vault_root, args.work, episode_ids)
            print(prompt)
            return 0

        elif args.command == "save-style":
            vault_root = Path(args.vault)
            input_path = Path(args.input)
            run_save_style(vault_root, args.work, args.type, input_path)
            print(f"Saved {args.type} to {vault_root / args.work}")
            return 0

        else:
            parser.print_help()
            return 1

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
