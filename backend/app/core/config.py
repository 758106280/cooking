from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite:///./data/cooking.db"
    admin_username: str = "admin"
    admin_password: str = "change-me"
    secret_key: str = "change-this-secret-key"
    upload_dir: str = "./data/uploads"
    cors_origins: str = "http://localhost:5173,http://localhost:8080,https://localhost,capacitor://localhost"
    session_same_site: str = "lax"
    session_https_only: bool = False
    access_token_max_age: int = 60 * 60 * 24 * 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
