from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret_key: str = "dev-secret"
    session_secret_key: str = "dev-session-secret"
    admin_username: str = "admin"
    admin_password: str = "admin"
    database_url: str = "sqlite:///./tadp.db"
    redis_url: str = "redis://localhost:6379/0"
    download_root: str = "./Downloads"
    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
