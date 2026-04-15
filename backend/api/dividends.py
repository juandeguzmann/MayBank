from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.deps import get_session
from backend.db.queries.dividends import get_dividends_by_ticker, get_monthly_dividends
from backend.models.dividends import MonthlyDividendsResponse, TickerDividendsResponse

router = APIRouter(prefix="/api/dividends", tags=["dividends"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/monthly", response_model=MonthlyDividendsResponse)
def monthly_dividends(session: SessionDep):
    rows = get_monthly_dividends(session)
    return MonthlyDividendsResponse(
        data=[
            {"month": r.month, "total_amount": r.total_amount, "total_tax": r.total_tax, "currency": r.currency}
            for r in rows
        ]
    )


@router.get("/by-ticker", response_model=TickerDividendsResponse)
def dividends_by_ticker(session: SessionDep):
    rows = get_dividends_by_ticker(session)
    return TickerDividendsResponse(
        data=[
            {"ticker": r.ticker, "name": r.name, "total_amount": r.total_amount, "payments": r.payments, "currency": r.currency}
            for r in rows
        ]
    )
