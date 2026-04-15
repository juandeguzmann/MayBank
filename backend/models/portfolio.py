from pydantic import BaseModel


class PortfolioSummary(BaseModel):
    portfolio_value: float
    cash: float
    invested: float
    unrealised_gain: float
    unrealised_gain_pct: float
    realised_gain: float
    net_deposits: float
    net_withdrawals: float
    net_cashflow: float
    currency: str = "GBP"


class PortfolioSummaryResponse(BaseModel):
    data: PortfolioSummary
