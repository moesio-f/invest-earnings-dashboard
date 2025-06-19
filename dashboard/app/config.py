"""Configurações do streamlit."""

from pydantic import AmqpDsn, AnyUrl
from pydantic_settings import BaseSettings


class StreamlitConfig(BaseSettings):
    DATE_FORMAT: str = "%d/%m/%Y"
    ST_DATE_FORMAT: str = "DD/MM/YYYY"
    PAGE_TITLE: str = "Dashboard de Proventos"
    PAGE_LAYOUT: str = "wide"


class DashboardConfig(BaseSettings):
    BROKER_URL: AmqpDsn
    NOTIFICATION_QUEUE: str
    ANALYTIC_DB_URL: AnyUrl


ST_CONFIG = StreamlitConfig()
