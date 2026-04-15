from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.t212.client import TradingAppClient
from backend.db.deps import get_session
from backend.db.queries.portfolio import get_transactions
from backend.models.portfolio import (
    PortfolioSummaryResponse,
    PortfolioSummary,
)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/summary", response_model=PortfolioSummaryResponse)
def get_summary(session: SessionDep):
    with TradingAppClient() as client:
        data = client.get_account_summary()
    
    deposit_types = ["DEPOSIT", "TRANSFER"]
    withdraw_types = ["WITHDRAW", "TRANSFER"]

    deposits = get_transactions(session, deposit_types)
    withdraws = get_transactions(session, withdraw_types)

    net_deposits = sum(t.amount for t in deposits)
    net_withdrawals = sum(t.amount for t in withdraws)
    net_cashflow = net_deposits + net_withdrawals

    investments = data.get("investments", {})
    cash = data.get("cash", {})

    total_cost: float = investments.get("totalCost", 0)
    unrealised: float = investments.get("unrealizedProfitLoss", 0)
    realised: float = investments.get("realizedProfitLoss", 0)
    gain_pct: float = (unrealised / total_cost * 100) if total_cost else 0.0

    return PortfolioSummaryResponse(
        data=PortfolioSummary(
            portfolio_value=data.get("totalValue", 0),
            cash=cash.get("availableToTrade", 0),
            invested=total_cost,
            unrealised_gain=unrealised,
            unrealised_gain_pct=gain_pct,
            realised_gain=realised,
            net_deposits=net_deposits,
            net_withdrawals=net_withdrawals,
            net_cashflow=net_cashflow,
            currency=data.get("currency", "GBP"),
        )
    )
