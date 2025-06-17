"""Modelos de mensagens."""

from invest_earning.database.utils import StrEnum
from pydantic import BaseModel, ConfigDict, model_validator


class Empty(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalyticTrigger(StrEnum):
    wallet_update = "wallet_update"
    dashboard_query = "dashboard_query"


class WalletEntity(StrEnum):
    asset = "asset"
    earning = "earning"
    transaction = "transaction"
    economic_data = "economic_data"


class DatabaseOperation(StrEnum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"


class QueryKind(StrEnum):
    ASSET = "ASSET"
    GROUP = "GROUP"


class AnalyticTable(StrEnum):
    earning_yield = "earning_yield"
    monthly_yield = "monthly_yield"


class WalletUpdateInformation(BaseModel):
    entity: WalletEntity
    operation: DatabaseOperation
    entity_id: str
    reference: WalletEntity | None = None
    reference_id: str | None = None


class QueryInformation(BaseModel):
    kind: QueryKind
    entity: str
    table: AnalyticTable


class AnalyticEvent(BaseModel):
    trigger: AnalyticTrigger
    update_information: WalletUpdateInformation | Empty
    query_information: QueryInformation | Empty

    @model_validator(mode="after")
    def check_consistencty(self) -> "AnalyticEvent":
        if self.trigger == AnalyticTrigger.wallet_update:
            assert not isinstance(self.update_information, Empty)

        if self.trigger == AnalyticTrigger.dashboard_query:
            assert not isinstance(self.query_information, Empty)

        return self
