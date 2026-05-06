import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class LivePrice(BaseModel):
    conditions: list[str] | None
    price: Decimal
    symbol: str
    timestamp: datetime.datetime
    volume: Decimal

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(v / 1000, tz=datetime.timezone.utc)
