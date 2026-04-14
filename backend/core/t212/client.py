import time
import httpx
from typing import Any
import backend.config as config


class TradingAppClient:
    """HTTP client for the Trading 212 REST API (ISA account)."""

    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=config.T212_BASE_URL,
            headers={"Authorization": config.T212_API_KEY},
            timeout=30.0,
        )

    def close(self) -> None:
        self._client.close()

    def _get(self, path: str, params: dict | None = None) -> Any:
        while True:
            response = self._client.get(path, params=params)
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 60))
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()

    # --- Account ---

    def get_account_info(self) -> dict:
        return self._get("/api/v0/equity/account/info")

    def get_cash(self) -> dict:
        return self._get("/api/v0/equity/account/cash")

    def get_account_summary(self) -> dict:
        return self._get("/api/v0/equity/account/summary")

    # --- Portfolio ---

    def get_portfolio(self) -> list[dict]:
        return self._get("/api/v0/equity/portfolio")

    # --- Historical events ---

    def get_orders(self, cursor: str | None = None, limit: int = 50) -> dict:
        """Returns filled orders. Supports cursor-based pagination."""
        if cursor and cursor.startswith("/"):
            return self._get(cursor)
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._get("/api/v0/equity/history/orders", params=params)

    def get_dividends(self, cursor: str | None = None, limit: int = 50) -> dict:
        """Returns dividend payments received."""
        if cursor and cursor.startswith("/"):
            return self._get(cursor)
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._get("/api/v0/equity/history/dividends", params=params)

    def get_transactions(self, cursor: str | None = None, limit: int = 50, time: str | None = None) -> dict:
        """Returns cash transactions (deposits, withdrawals)."""
        if cursor and cursor.startswith("/"):
            return self._get(cursor)
        params: dict = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if time:
            params["time"] = time
        return self._get("/api/v0/equity/history/transactions", params=params)

    def __enter__(self) -> "TradingAppClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
