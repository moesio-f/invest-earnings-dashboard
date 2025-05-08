"""Define entidades de
resultados de análises
no banco da aplicação.
"""

from datetime import date

import pandera as pa
import pandera.extensions as extensions
from pandera.typing.pandas import Series

from app.db.models import EarningKind

if "is_valid_enum" not in pa.Check.REGISTERED_CUSTOM_CHECKS:

    @extensions.register_check_method(statistics=["enum"])
    def is_valid_enum(pandas_obj, *, enum):
        return (
            pandas_obj.isin([e.name for e in enum]).all()
            or pandas_obj.isin([e.value for e in enum]).all()
        )


class EarningYield(pa.DataFrameModel):
    b3_code: Series[str] = pa.Field(nullable=False)
    hold_date: Series[date] = pa.Field(nullable=False, coerce=False)
    payment_date: Series[date] = pa.Field(nullable=False, coerce=False)
    kind: Series[str] = pa.Field(is_valid_enum={"enum": EarningKind})
    ir: Series[float] = pa.Field(nullable=False)
    value_per_share: Series[float] = pa.Field(nullable=False)
    ir_adjusted_value_per_share: Series[float] = pa.Field(nullable=False)
    avg_price: Series[float] = pa.Field(nullable=False)
    shares: Series[int] = pa.Field(nullable=False)
    yoc: Series[float] = pa.Field(nullable=False)
