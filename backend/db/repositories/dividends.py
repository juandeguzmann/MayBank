from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db.models.postgres import Dividend


def get_monthly_dividends(session: Session) -> list:
    stmt = (
        select(
            func.date_trunc("month", Dividend.paid_at).label("month"),
            func.sum(Dividend.amount).label("total_amount"),
            func.sum(Dividend.tax_withheld).label("total_tax"),
            Dividend.currency,
        )
        .group_by(func.date_trunc("month", Dividend.paid_at), Dividend.currency)
        .order_by(func.date_trunc("month", Dividend.paid_at))
    )
    return session.execute(stmt).all()


def get_dividends_by_ticker(session: Session) -> list:
    stmt = (
        select(
            Dividend.ticker,
            Dividend.name,
            func.sum(Dividend.amount).label("total_amount"),
            func.count(Dividend.id).label("payments"),
            Dividend.currency,
        )
        .group_by(Dividend.ticker, Dividend.name, Dividend.currency)
        .order_by(func.sum(Dividend.amount).desc())
    )
    return session.execute(stmt).all()
