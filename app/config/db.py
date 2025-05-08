"""Configurações do banco
de dados.
"""

from enum import Enum

import pydantic
from pydantic_settings import BaseSettings


class SupportedDatabases(Enum):
    SQLITE = "sqlite"


class DatabaseConfig(BaseSettings):
    db_backend: SupportedDatabases = SupportedDatabases.SQLITE
    connection_string: str = "sqlite:////local.db"

    @pydantic.model_validator(mode="after")
    def validate(self):
        prefix = f"{self.db_backend.value}:///"
        if not self.connection_string.startswith(prefix):
            raise ValueError("Incompatible connection string for databaset backend.")

        return self


DB_CONFIG = DatabaseConfig()
