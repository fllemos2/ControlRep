"""
Configurações da aplicação
"""
from pydantic_settings import BaseSettings
import os, sys


def _env_file() -> str:
    if getattr(sys, "frozen", False):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(appdata, "CattleControl", ".env")
    return ".env"


class Settings(BaseSettings):
    # Database (sobrescrito por session.py — aqui só para referência)
    DATABASE_URL: str = "sqlite:///./cattle_control.db"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cattle Control"
    PROJECT_VERSION: str = "0.1.0"

    # CORS (usado apenas em desenvolvimento)
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Anthropic IA
    ANTHROPIC_API_KEY: str = ""

    # Sync com nuvem
    SYNC_SECRET: str = ""       # chave compartilhada local ↔ nuvem
    CLOUD_SYNC_URL: str = ""    # ex: https://cattle-control.up.railway.app

    DEBUG: bool = False

    class Config:
        env_file = _env_file()
        case_sensitive = True


settings = Settings()
