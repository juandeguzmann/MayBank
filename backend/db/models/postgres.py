from datetime import date, datetime
from typing import Any, Optional
from sqlalchemy import DateTime, JSON
from sqlmodel import Column, Field, SQLModel


def _dt(nullable: bool = False, server_default: str | None = None):
    kwargs = {"sa_type": DateTime(timezone=True)}
    if server_default:
        kwargs["sa_column_kwargs"] = {"server_default": server_default}
    if nullable:
        return Field(default=None, **kwargs)
    return Field(**kwargs)


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    # Order fields
    id: str = Field(primary_key=True)
    ticker: Optional[str] = None
    isin: Optional[str] = None
    name: Optional[str] = None
    instrument_currency: Optional[str] = None   # currency the stock trades in (e.g. GBX, USD)
    type: Optional[str] = None                  # MARKET, LIMIT, STOP
    side: Optional[str] = None                  # BUY, SELL
    strategy: Optional[str] = None              # QUANTITY, VALUE
    status: Optional[str] = None
    initiated_from: Optional[str] = None        # API, AUTOINVEST, etc.
    created_at: datetime = _dt()

    # Fill fields
    fill_id: Optional[str] = None
    trading_method: Optional[str] = None        # OTC, TOTV
    price_of_stock: Optional[float] = None      # actual price in instrument_currency
    quantity: Optional[float] = None            # quantity of stock purchased
    cost_in_pounds: Optional[float] = None      # walletImpact.netValue — cost in GBP
    executed_currency: Optional[str] = None     # walletImpact.currency
    fx_rate: Optional[float] = None             # conversion rate to GBP
    filled_at: Optional[datetime] = _dt(nullable=True)

    saved_at: Optional[datetime] = _dt(nullable=True, server_default="NOW()")


class Dividend(SQLModel, table=True):
    __tablename__ = "dividends"

    id: str = Field(primary_key=True)
    ticker: str
    name: Optional[str] = None
    quantity: float
    amount: float
    amount_in_euro: Optional[float] = None
    tax_withheld: float = 0
    paid_at: datetime = _dt()
    currency: str
    saved_at: Optional[datetime] = _dt(nullable=True, server_default="NOW()")


class Transactions(SQLModel, table=True):
    __tablename__ = "transactions"

    type: str
    amount: float
    currency: str
    reference: str = Field(primary_key=True)
    date_time: datetime = _dt()
    saved_at: Optional[datetime] = _dt(nullable=True, server_default="NOW()")
