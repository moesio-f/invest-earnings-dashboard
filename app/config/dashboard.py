"""Configurações do dashboard."""

from pydantic_settings import BaseSettings


class DashboardConfig(BaseSettings):
    ST_DATE_FORMAT: str = "DD/MM/YYYY"
    PAGE_TITLE: str = "Dashboard"
    PAGE_LAYOUT: str = "wide"
    CLEAR_STATE_ON_PAGE_CHANGE: bool = True


DASHBOARD_CONFIG = DashboardConfig()
