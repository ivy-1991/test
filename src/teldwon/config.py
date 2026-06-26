from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    api_id: int
    api_hash: str
    session_name: str


def load_settings(dotenv_path: Path | None = None) -> Settings:
    load_dotenv(dotenv_path=dotenv_path)

    api_id_raw = os.getenv("TG_API_ID", "").strip()
    api_hash = os.getenv("TG_API_HASH", "").strip()
    session_name = os.getenv("TG_SESSION_NAME", "teldwon").strip()

    if not api_id_raw:
        raise ValueError("Missing TG_API_ID in environment or .env")
    if not api_hash:
        raise ValueError("Missing TG_API_HASH in environment or .env")

    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise ValueError("TG_API_ID must be an integer") from exc

    return Settings(api_id=api_id, api_hash=api_hash, session_name=session_name)
