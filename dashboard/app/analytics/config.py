"""Configurações do dashboard de analytics."""

from pydantic_settings import BaseSettings


class AnalyticsConfig(BaseSettings):
    BROKER_URL: str
    NOTIFICATION_QUEUE: str
    ANALYTIC_DB_URL: str


ANALYTICS_CONFIG = AnalyticsConfig()
