from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.entities import ArchiveFile, Chat

RETRY_MINUTES = [1, 5, 15, 30, 60]


def classify(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext in {"mp4", "mkv", "avi", "mov"}:
        return "video"
    if ext in {"jpg", "png", "gif", "webp"}:
        return "image"
    if ext in {"zip", "rar", "7z", "iso"}:
        return "archive"
    if ext in {"pdf", "epub", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx"}:
        return "document"
    if ext in {"apk", "exe"}:
        return "software"
    return "other"


def target_path(chat_title: str, created: datetime, filename: str) -> Path:
    safe_chat = "".join(c if c.isalnum() or c in " ._-" else "_" for c in chat_title).strip()
    return Path(settings.download_root) / safe_chat / str(created.year) / f"{created.month:02d}" / classify(filename) / filename


def register_file(db: Session, chat: Chat, message_id: int, file_id: str, filename: str, size: int) -> ArchiveFile:
    existing = db.query(ArchiveFile).filter_by(chat_id=chat.id, message_id=message_id, file_id=file_id).first()
    if existing:
        return existing
    item = ArchiveFile(chat_id=chat.id, message_id=message_id, file_id=file_id, filename=filename, size=size)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def mark_retry(db: Session, item: ArchiveFile) -> ArchiveFile:
    item.retries += 1
    delay = RETRY_MINUTES[min(item.retries - 1, len(RETRY_MINUTES) - 1)]
    item.status = "retrying"
    item.next_retry_at = datetime.utcnow() + timedelta(minutes=delay)
    db.commit()
    db.refresh(item)
    return item


def status_summary(db: Session) -> dict[str, int]:
    total_chats = db.query(func.count(Chat.id)).scalar() or 0
    total_files = db.query(func.count(ArchiveFile.id)).scalar() or 0
    by_status = dict(db.query(ArchiveFile.status, func.count(ArchiveFile.id)).group_by(ArchiveFile.status).all())
    return {"chats": total_chats, "files": total_files, **by_status}
