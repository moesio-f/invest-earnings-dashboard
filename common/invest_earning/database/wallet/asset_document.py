"""Documentos públicos
para ativos.
"""

from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger, Integer

from invest_earning.database.base import WalletBase


class AssetDocument(WalletBase):
    __tablename__ = "asset_document"

    id = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        comment="ID automático de provento.",
    )
    asset_b3_code: Mapped[str] = mapped_column(
        ForeignKey("asset.b3_code", ondelete="CASCADE")
    )

    title: Mapped[str] = mapped_column(
        comment="Títutlo do documento.", nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(comment="URL do documento.", nullable=False)
    publish_date: Mapped[date] = mapped_column(
        comment="Data de publicação do documento.", nullable=False, index=True
    )
