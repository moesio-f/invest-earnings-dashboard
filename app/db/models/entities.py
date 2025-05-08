"""Classe que representa um ativo
que faz distribuição de proventos.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.types import Numeric, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AssetKind(Enum):
    stock = "Ação"
    bdr = "BDR"
    fii = "FII"
    etf = "ETF"

    @classmethod
    def from_value(cls, value: str) -> AssetKind:
        try:
            return cls[value]
        except:
            return next(k for k in cls if k.value == value)


class TransactionKind(Enum):
    buy = "Compra"
    sell = "Venda"

    @classmethod
    def from_value(cls, value: str) -> TransactionKind:
        try:
            return cls[value]
        except:
            return next(k for k in cls if k.value == value)


class EarningKind(Enum):
    dividend = "Dividendo"
    jscp = "Juros sobre Capital Próprio"
    taxable = "Rendimento Tributável"

    @classmethod
    def from_value(cls, value: str) -> EarningKind:
        try:
            return cls[value]
        except:
            return next(k for k in cls if k.value == value)


class Asset(Base):
    __tablename__ = "asset"

    b3_code: Mapped[str] = mapped_column(
        primary_key=True, comment="Código de negociação na B3."
    )
    name: Mapped[str] = mapped_column(index=True, unique=True, comment="Nome do ativo.")
    description: Mapped[str]
    kind: Mapped[AssetKind] = mapped_column(index=True, comment="Tipo do ativo.")
    added: Mapped[date] = mapped_column(
        comment="Data de criação/cadastro do ativo no sistema."
    )

    # Proventos desse ativo
    earnings: Mapped[List[Earning]] = relationship(
        back_populates="asset", cascade="all, delete"
    )

    # Transações desse ativo
    transactions: Mapped[List[Transaction]] = relationship(
        back_populates="asset", cascade="all, delete"
    )

    def __repr__(self):
        return f"Asset({self.b3_code}, {self.name}, {self.kind.value})"


class Earning(Base):
    __tablename__ = "earning"

    id = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        comment="ID automático de provento.",
    )
    asset_b3_code: Mapped[str] = mapped_column(
        ForeignKey("asset.b3_code", ondelete="CASCADE")
    )
    hold_date: Mapped[date] = mapped_column(comment="Data de custódia.")
    payment_date: Mapped[date] = mapped_column(comment="Data de pagamento.")
    value_per_share = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False), comment="Valor por unidade."
    )

    ir_percentage: Mapped[Optional[float]] = mapped_column(
        comment="Taxa (%) de incidência do Imposto de Renda."
    )
    kind: Mapped[EarningKind] = mapped_column(index=True, comment="Tipo do provento.")

    # Ativo sobre o qual esse provento se refere
    asset: Mapped[Asset] = relationship(back_populates="earnings")

    # Transações que possuem direito a esse provento
    right_to_earnings: Mapped[List[Transaction]] = relationship(
        secondary="earnings_rights", back_populates="entitled_to_earnings"
    )

    def __repr__(self):
        return (
            f"Earning({self.asset_b3_code}, {self.hold_date.isoformat()}, "
            f"{self.payment_date.isoformat()}, {self.value_per_share}, "
            f"{self.kind.value})"
        )


class Transaction(Base):
    __tablename__ = "transaction"

    id = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        comment="ID automático da transação.",
    )
    asset_b3_code: Mapped[str] = mapped_column(
        ForeignKey("asset.b3_code", ondelete="CASCADE")
    )
    date: Mapped[date] = mapped_column(comment="Data da transação.")
    kind: Mapped[TransactionKind] = mapped_column(
        index=True, comment="Tipo da transação."
    )
    value_per_share = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False), comment="Valor por unidade."
    )
    shares: Mapped[int] = mapped_column(comment="Unidades movimentadas.")

    # Ativo sobre qual essa transação se refere
    asset: Mapped[Asset] = relationship(back_populates="transactions")

    # Proventos sobre os quais essa transação possui direito
    entitled_to_earnings: Mapped[List[Earning]] = relationship(
        secondary="earnings_rights", back_populates="right_to_earnings"
    )

    def __repr__(self):
        return (
            f"Transaction({self.asset_b3_code}, {self.kind.value}, "
            f"{self.value_per_share * self.shares:.2f})"
        )


class EarningsRights(Base):
    __tablename__ = "earnings_rights"

    earning = mapped_column(ForeignKey("earning.id"), primary_key=True)
    has_right = mapped_column(ForeignKey("transaction.id"), primary_key=True)
