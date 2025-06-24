"""Configurações da API."""

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    db_url: str = "sqlite:////local.db"


class DispatcherConfig(BaseSettings):
    notification_queue: str = "notification.router.queue"
    broker_url: str = "amqp://guest:guest@localhost:5672/?heartbeat=30"


DB_CONFIG = DatabaseConfig()
DISPATCHER_CONFIG = DispatcherConfig()
