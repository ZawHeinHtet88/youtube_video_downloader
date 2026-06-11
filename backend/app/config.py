from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    download_dir: Path = Path("downloads")
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    max_concurrent_downloads: int = 3
    file_cleanup_hours: int = 24
    cors_origins: list[str] = ["*"]

    model_config = {"env_prefix": "IDM_"}


settings = Settings()
settings.download_dir.mkdir(parents=True, exist_ok=True)
