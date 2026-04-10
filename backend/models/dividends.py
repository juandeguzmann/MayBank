from datetime import datetime

from pydantic import BaseModel


class MonthlyDividend(BaseModel):
    month: datetime
    total_amount: float
    total_tax: float
    currency: str


class TickerDividend(BaseModel):
    ticker: str
    name: str | None
    total_amount: float
    payments: int
    currency: str


class MonthlyDividendsResponse(BaseModel):
    data: list[MonthlyDividend]


class TickerDividendsResponse(BaseModel):
    data: list[TickerDividend]
