import os
import shutil
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.core.security import ALGORITHM, create_access_token, verify_admin
from app.models.entities import ArchiveFile, Chat
from app.schemas.dto import ChatOut, FileOut, LoginRequest, StatusOut, Token
from app.services.archive import status_summary

router = APIRouter()
bearer = HTTPBearer()


def require_auth(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    try:
        payload = jwt.decode(creds.credentials, settings.app_secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    return str(payload["sub"])


@router.post("/auth/login", response_model=Token)
def login(body: LoginRequest) -> Token:
    if not verify_admin(body.username, body.password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return Token(access_token=create_access_token(body.username))


@router.get("/system/status", response_model=StatusOut)
def system_status(db: Session = Depends(get_db), _: str = Depends(require_auth)) -> StatusOut:
    summary = status_summary(db)
    usage = shutil.disk_usage(settings.download_root if os.path.exists(settings.download_root) else ".")
    return StatusOut(online=True, chats=summary.get("chats", 0), files=summary.get("files", 0), queued=summary.get("queued", 0), downloading=summary.get("downloading", 0), completed=summary.get("completed", 0), storage_free_bytes=usage.free)


@router.get("/chats", response_model=list[ChatOut])
def chats(q: str | None = None, db: Session = Depends(get_db), _: str = Depends(require_auth)) -> list[Chat]:
    query = db.query(Chat)
    if q:
        query = query.filter(Chat.title.ilike(f"%{q}%"))
    return query.order_by(Chat.title).all()


@router.post("/chats/{chat_id}/favorite", response_model=ChatOut)
def favorite(chat_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)) -> Chat:
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="chat not found")
    chat.favorite = not chat.favorite
    db.commit()
    db.refresh(chat)
    return chat


@router.get("/files", response_model=list[FileOut])
def files(q: str | None = None, status: str | None = None, db: Session = Depends(get_db), _: str = Depends(require_auth)) -> list[ArchiveFile]:
    query = db.query(ArchiveFile)
    if q:
        query = query.filter(ArchiveFile.filename.ilike(f"%{q}%"))
    if status:
        query = query.filter(ArchiveFile.status == status)
    return query.order_by(ArchiveFile.updated_at.desc()).limit(500).all()


@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)) -> dict[str, bool]:
    item = db.get(ArchiveFile, file_id)
    if not item:
        raise HTTPException(status_code=404, detail="file not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
