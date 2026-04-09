"""
One-time historical backfill from Trading 212.

Fetches all orders, dividends, and transactions using cursor-based
pagination and persists them to PostgreSQL.

Usage:
    uv run python -m backend.core.t212.backfill
"""
import asyncio
import asyncpg
from backend.core.t212.client import T212Client
from backend.db.postgres import get_pool
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def backfill_orders(client: T212Client, pool: asyncpg.Pool) -> int:
    cursor = None
    total = 0

    while True:
        response = await client.get_orders(cursor=cursor, limit=50)
        items = response.get("items", [])

        if not items:
            break

        await pool.executemany(
            """
            INSERT INTO orders (
                id, ticker, name, type, quantity, filled_quantity,
                limit_price, fill_price, fill_cost, status, created_at, filled_at, currency
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
            ON CONFLICT (id) DO NOTHING
            """,
            [
                (
                    o["id"],
                    o.get("ticker"),
                    o.get("name"),
                    o.get("type"),
                    o.get("quantity"),
                    o.get("filledQuantity"),
                    o.get("limitPrice"),
                    o.get("fillPrice"),
                    o.get("fillCost"),
                    o.get("status"),
                    o.get("creationTime"),
                    o.get("dateExecuted"),
                    o.get("currencyCode", "GBP"),
                )
                for o in items
            ],
        )
        total += len(items)
        log.info(f"Orders: inserted {total} so far...")

        cursor = response.get("nextPagePath")
        if not cursor:
            break

    return total


async def backfill_dividends(client: T212Client, pool: asyncpg.Pool) -> int:
    cursor = None
    total = 0

    while True:
        response = await client.get_dividends(cursor=cursor, limit=50)
        items = response.get("items", [])

        if not items:
            break

        await pool.executemany(
            """
            INSERT INTO dividends (
                id, ticker, name, quantity, amount, amount_in_gbp, tax_withheld, paid_at, currency
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            ON CONFLICT (id) DO NOTHING
            """,
            [
                (
                    d["id"],
                    d.get("ticker"),
                    d.get("name"),
                    d.get("quantity"),
                    d.get("amount"),
                    d.get("amountInEuro"),  # T212 may return in account currency
                    d.get("withheldTax", 0),
                    d.get("paidOn"),
                    d.get("currencyCode", "GBP"),
                )
                for d in items
            ],
        )
        total += len(items)
        log.info(f"Dividends: inserted {total} so far...")

        cursor = response.get("nextPagePath")
        if not cursor:
            break

    return total


async def backfill_transactions(client: T212Client, pool: asyncpg.Pool) -> int:
    cursor = None
    total = 0

    while True:
        response = await client.get_transactions(cursor=cursor, limit=50)
        items = response.get("items", [])

        if not items:
            break

        await pool.executemany(
            """
            INSERT INTO transactions (id, type, amount, currency, created_at, reference)
            VALUES ($1,$2,$3,$4,$5,$6)
            ON CONFLICT (id) DO NOTHING
            """,
            [
                (
                    t["id"],
                    t.get("type"),
                    t.get("amount"),
                    t.get("currencyCode", "GBP"),
                    t.get("dateTime"),
                    t.get("reference"),
                )
                for t in items
            ],
        )
        total += len(items)
        log.info(f"Transactions: inserted {total} so far...")

        cursor = response.get("nextPagePath")
        if not cursor:
            break

    return total


async def run_backfill() -> None:
    pool = await get_pool()
    async with T212Client() as client:
        log.info("Starting T212 historical backfill...")

        orders = await backfill_orders(client, pool)
        dividends = await backfill_dividends(client, pool)
        transactions = await backfill_transactions(client, pool)

        log.info(
            f"Backfill complete. Orders: {orders}, Dividends: {dividends}, Transactions: {transactions}"
        )


if __name__ == "__main__":
    asyncio.run(run_backfill())
