"""Configurações gerais dos scrapers."""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str = "sqlite:////local.db"
    notification_queue: str = "notification.router.queue"
    broker_url: str = "amqp://guest:guest@localhost:5672/?heartbeat=30"


CONFIG = Config()
