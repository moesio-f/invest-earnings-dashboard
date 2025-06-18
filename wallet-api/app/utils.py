"""Utilidades para a API."""

from datetime import date

import pandas as pd


def to_last_day_of_the_month(v: str | date) -> date:
    return (pd.to_datetime(v) + pd.offsets.MonthEnd(0)).date()
