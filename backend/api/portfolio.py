from fastapi import APIRouter

from backend.core.t212.client import TradingAppClient
from backend.models.portfolio import (
    PortfolioSummaryResponse,
    PortfolioSummary,
)

router = APIRouter(prefix="/api/portfolio")


@router.get("/summary", response_model=PortfolioSummaryResponse)
def get_summary():
    with TradingAppClient() as client:
        data = client.get_account_summary()

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
            currency=data.get("currency", "GBP"),
        )
    )
