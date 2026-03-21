from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tps_image_name: str = "tps-base"
    tps_container_name: str = "tps-instance"
    tps_host: str = "0.0.0.0"
    tps_port: int = 8080
    packs_dir: Path = Path("packs")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
