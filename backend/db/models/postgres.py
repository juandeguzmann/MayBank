from datetime import date, datetime
from typing import Optional
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def _dt(nullable: bool = False, server_default: str | None = None):
    kwargs = {"sa_type": DateTime(timezone=True)}
    if server_default:
        kwargs["sa_column_kwargs"] = {"server_default": server_default}
    if nullable:
        return Field(default=None, **kwargs)
    return Field(**kwargs)


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: str = Field(primary_key=True)
    ticker: str
    name: Optional[str] = None
    type: str
    quantity: Optional[float] = None
    filled_quantity: Optional[float] = None
    limit_price: Optional[float] = None
    fill_price: Optional[float] = None
    fill_cost: Optional[float] = None
    status: str
    created_at: datetime = _dt()
    filled_at: Optional[datetime] = _dt(nullable=True)
    currency: str = "GBP"
    saved_at: Optional[datetime] = _dt(nullable=True, server_default="NOW()")


class Dividend(SQLModel, table=True):
    __tablename__ = "dividends"

    id: str = Field(primary_key=True)
    ticker: str
    name: Optional[str] = None
    quantity: float
    amount: float
    amount_in_gbp: Optional[float] = None
    tax_withheld: float = 0
    paid_at: datetime = _dt()
    currency: str = "GBP"
    saved_at: Optional[datetime] = _dt(nullable=True, server_default="NOW()")
