"""Utilidades."""

from enum import Enum
from typing import Self


class StrEnum(Enum):
    @classmethod
    def from_value(cls, value: str) -> Self:
        try:
            return cls[value]
        except:
            return next(k for k in cls if k.value == value)
