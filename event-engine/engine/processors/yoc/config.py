"""Configurações do processador de YoC."""

from pydantic_settings import BaseSettings


class YoCProcessorConfig(BaseSettings):
    yoc_queue: str = "processor.yoc.queue"
    broker_url: str = "amqp://guest:guest@localhost:5672/?heartbeat=30"
    wallet_db_url: str = "sqlite:///wallet.db"
    analytic_db_url: str = "sqlite:///analytic.db"
