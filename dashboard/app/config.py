"""Configurações do streamlit."""

from pydantic_settings import BaseSettings


class StreamlitConfig(BaseSettings):
    DATE_FORMAT: str = "%d/%m/%Y"
    ST_DATE_FORMAT: str = "DD/MM/YYYY"
    PAGE_TITLE: str = "Dashboard de Proventos"
    PAGE_LAYOUT: str = "wide"


ST_CONFIG = StreamlitConfig()
