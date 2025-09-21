"""Configurações gerais dos scrapers."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Config(BaseSettings):
    db_url: str = "sqlite:////local.db"
    wallet_api: str = "http://localhost:8083"
    notification_queue: str = "notification.router.queue"
    broker_url: str = "amqp://guest:guest@localhost:5672/?heartbeat=30"
    timeout: float = 5.0
    market_price_previous_days: int = 30
    market_price_config_path: Path = Path("asset_config.json")


CONFIG = Config()
