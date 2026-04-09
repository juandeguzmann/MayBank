import httpx
from typing import Any
from backend.config import settings


class T212Client:
    """Async HTTP client for the Trading 212 REST API (ISA account)."""

    BASE_URL = settings.t212_base_url

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": settings.t212_api_key},
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> Any:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    # --- Account ---

    async def get_account_info(self) -> dict:
        return await self._get("/api/v0/equity/account/info")

    async def get_cash(self) -> dict:
        return await self._get("/api/v0/equity/account/cash")

    # --- Portfolio ---

    async def get_portfolio(self) -> list[dict]:
        return await self._get("/api/v0/equity/portfolio")

    # --- Historical events ---

    async def get_orders(self, cursor: str | None = None, limit: int = 50) -> dict:
        """Returns filled orders. Supports cursor-based pagination."""
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get("/api/v0/equity/history/orders", params=params)

    async def get_dividends(self, cursor: str | None = None, limit: int = 50) -> dict:
        """Returns dividend payments received."""
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get("/api/v0/equity/history/dividends", params=params)

    async def get_transactions(self, cursor: str | None = None, limit: int = 50) -> dict:
        """Returns cash transactions (deposits, withdrawals)."""
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get("/api/v0/equity/history/transactions", params=params)

    async def __aenter__(self) -> "T212Client":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
