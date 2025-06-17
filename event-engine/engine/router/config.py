"""Configurações do roteador."""

from pydantic_settings import BaseSettings


class RouterConfig(BaseSettings):
    notification_queue: str = "notification.router.queue"
    yoc_queue: str = "processor.yoc.queue"
    connection_url: str = "amqp://guest:guest@localhost:5672/?heartbeat=30"
