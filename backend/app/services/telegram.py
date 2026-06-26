from dataclasses import dataclass
from telethon import TelegramClient
from telethon.sessions import StringSession
from app.core.config import settings


@dataclass
class LoginQr:
    token: str
    url: str


class TelegramManager:
    def client(self, session: str | None = None) -> TelegramClient:
        return TelegramClient(StringSession(session), int(settings.telegram_api_id or 0), settings.telegram_api_hash)

    async def qr_login_url(self) -> LoginQr:
        if not settings.telegram_api_id or not settings.telegram_api_hash:
            raise RuntimeError("Telegram API credentials are not configured")
        async with self.client() as client:
            qr = await client.qr_login()
            return LoginQr(token=qr.token.hex(), url=qr.url)


telegram_manager = TelegramManager()
