from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_settings
from .downloader import ALLOWED_TYPES, DownloadOptions, run_download


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teldwon",
        description="Download Telegram group or channel files with your own account.",
    )
    parser.add_argument(
        "--chat",
        required=True,
        help="Telegram chat username, invite link, or numeric ID.",
    )
    parser.add_argument(
        "--output",
        default="downloads",
        help="Output directory for downloaded files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of messages to inspect.",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Only download files whose names contain this text.",
    )
    parser.add_argument(
        "--types",
        nargs="*",
        choices=sorted(ALLOWED_TYPES),
        default=None,
        help="Restrict downloads to specific media types.",
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help="Optional path to a custom .env file.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = load_settings(Path(args.env_file) if args.env_file else None)
    options = DownloadOptions(
        chat=args.chat,
        output_dir=Path(args.output),
        limit=args.limit,
        query=args.query,
        media_types=set(args.types) if args.types else None,
    )

    downloaded = run_download(settings, options)
    print(f"Downloaded {downloaded} file(s) to {options.output_dir}")


if __name__ == "__main__":
    main()
