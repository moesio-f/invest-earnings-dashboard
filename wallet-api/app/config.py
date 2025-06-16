"""Configurações da API."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    db_backup_path: Optional[Path] = None
    db_bootstrap_data_path: Optional[Path] = None
    db_url: str = "sqlite:////local.db"


DB_CONFIG = DatabaseConfig()
