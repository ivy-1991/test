from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatOut(BaseModel):
    id: int
    telegram_id: int
    title: str
    type: str
    favorite: bool
    model_config = {"from_attributes": True}


class FileOut(BaseModel):
    id: int
    message_id: int
    file_id: str
    filename: str
    size: int
    status: str
    downloaded_bytes: int
    path: str | None
    updated_at: datetime
    model_config = {"from_attributes": True}


class StatusOut(BaseModel):
    online: bool
    chats: int
    files: int
    queued: int
    downloading: int
    completed: int
    storage_free_bytes: int
