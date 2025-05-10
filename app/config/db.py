"""Configurações do banco
de dados.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

import pydantic
from pydantic_settings import BaseSettings


class SupportedDatabases(Enum):
    SQLITE = "sqlite"


class DatabaseConfig(BaseSettings):
    db_backend: SupportedDatabases = SupportedDatabases.SQLITE
    db_backup_path: Optional[Path] = None
    connection_string: str = "sqlite:////local.db"

    @pydantic.model_validator(mode="after")
    def validate(self):
        prefix = f"{self.db_backend.value}:///"
        if not self.connection_string.startswith(prefix):
            raise ValueError("Incompatible connection string for databaset backend.")

        return self


DB_CONFIG = DatabaseConfig()
