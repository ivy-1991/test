from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from telethon import TelegramClient
from telethon.tl.custom.message import Message

from .config import Settings


ALLOWED_TYPES = {"document", "photo", "video", "audio", "voice"}


@dataclass(slots=True)
class DownloadOptions:
    chat: str
    output_dir: Path
    limit: int | None = None
    query: str | None = None
    media_types: set[str] | None = None


def _message_matches(message: Message, options: DownloadOptions) -> bool:
    if not message.file:
        return False

    if options.query:
        file_name = (message.file.name or "").lower()
        if options.query.lower() not in file_name:
            return False

    if not options.media_types:
        return True

    if message.voice and "voice" in options.media_types:
        return True
    if message.video and "video" in options.media_types:
        return True
    if message.photo and "photo" in options.media_types:
        return True
    if message.audio and not message.voice and "audio" in options.media_types:
        return True
    if message.document and "document" in options.media_types:
        return True
    return False


def _state_file(output_dir: Path) -> Path:
    return output_dir / ".teldwon-state.json"


def _load_seen_ids(output_dir: Path) -> set[int]:
    state_path = _state_file(output_dir)
    if not state_path.exists():
        return set()

    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()

    raw_ids = payload.get("downloaded_message_ids", [])
    return {int(item) for item in raw_ids}


def _save_seen_ids(output_dir: Path, seen_ids: Iterable[int]) -> None:
    state_path = _state_file(output_dir)
    payload = {"downloaded_message_ids": sorted(set(seen_ids))}
    state_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


async def download_files(settings: Settings, options: DownloadOptions) -> int:
    options.output_dir.mkdir(parents=True, exist_ok=True)
    seen_ids = _load_seen_ids(options.output_dir)
    downloaded = 0

    async with TelegramClient(
        settings.session_name,
        settings.api_id,
        settings.api_hash,
    ) as client:
        entity = await client.get_entity(options.chat)

        async for message in client.iter_messages(entity, limit=options.limit):
            if message.id in seen_ids:
                continue

            if not _message_matches(message, options):
                continue

            await message.download_media(file=options.output_dir)
            seen_ids.add(message.id)
            downloaded += 1

    _save_seen_ids(options.output_dir, seen_ids)
    return downloaded


def run_download(settings: Settings, options: DownloadOptions) -> int:
    return asyncio.run(download_files(settings, options))
