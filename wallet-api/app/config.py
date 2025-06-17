"""Configurações da API."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    db_backup_path: Optional[Path] = None
    db_bootstrap_data_path: Optional[Path] = None
    db_url: str = "sqlite:////local.db"


class DispatcherConfig(BaseSettings):
    notification_queue: str = "notification.router.queue"
    connection_url: str = "amqp://guest:guest@localhost:5672/?heartbeat=30"


DB_CONFIG = DatabaseConfig()
DISPATCHER_CONFIG = DispatcherConfig()
