"""Base declarativa do SQLAlchemy
representando os bancos da aplicação.
"""

from sqlalchemy.orm import DeclarativeBase


class WalletBase(DeclarativeBase):
    pass


class AnalyticBase(DeclarativeBase):
    pass


class LoggingBase(DeclarativeBase):
    pass
