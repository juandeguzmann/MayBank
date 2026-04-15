import datetime

from typing import Optional, List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db.models.postgres import Transactions

def get_transactions(
    session: Session,
    types: List,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    ) -> list:    
    stmt = select(Transactions).order_by(
        Transactions.date_time.desc()
    ).where(Transactions.type.in_(types))
    
    if "WITHDRAW" in types:
        stmt = stmt.where(Transactions.amount < 0)
    
    if "DEPOSIT" in types:
        stmt = stmt.where(Transactions.amount > 0)

    if start_date is not None:
        stmt = stmt.where(Transactions.date_time >= start_date)

    if end_date is not None:
        stmt = stmt.where(Transactions.date_time <= end_date)
    
    return session.execute(stmt).scalars().all()