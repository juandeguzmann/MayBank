"""
Incremental backfill from Trading 212.

On startup, checks the latest record in each table and only fetches
data newer than that. If a table is empty, fetches everything.

Usage:
    uv run python -m backend.core.t212.backfill
"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from backend.core.t212.client import TradingAppClient
from backend.db.models.postgres import Dividend, Order
from backend.db.postgres import close_engine, create_tables, get_session_factory

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


async def get_latest(column) -> datetime | None:
    async with get_session_factory()() as session:
        result = await session.execute(select(func.max(column)))
        return result.scalar()


async def backfill_orders(client: TradingAppClient) -> int:
    since = await get_latest(Order.created_at)
    if since:
        log.info(f"Orders: backfilling from {since}")
    else:
        log.info("Orders: table empty, backfilling everything")

    cursor = None
    total = 0

    while True:
        response = await client.get_orders(cursor=cursor, limit=50)
        items = response.get("items", [])

        if not items:
            break

        new_items = []
        done = False
        for o in items:
            created_at = parse_dt(o["order"].get("createdAt"))
            if since and created_at and created_at <= since:
                done = True
                break
            new_items.append(o)

        if new_items:
            rows = [
                {
                    "id": str(o["order"]["id"]),
                    "ticker": o["order"].get("ticker"),
                    "isin": o["order"].get("instrument", {}).get("isin"),
                    "name": o["order"].get("instrument", {}).get("name"),
                    "instrument_currency": o["order"].get("instrument", {}).get("currency"),
                    "type": o["order"].get("type"),
                    "side": o["order"].get("side"),
                    "strategy": o["order"].get("strategy"),
                    "status": o["order"].get("status"),
                    "initiated_from": o["order"].get("initiatedFrom"),
                    "created_at": parse_dt(o["order"].get("createdAt")),
                    "fill_id": str(o["fill"]["id"]) if o.get("fill") else None,
                    "trading_method": o.get("fill", {}).get("tradingMethod"),
                    "price_of_stock": o.get("fill", {}).get("price"), # actual price in currency of stock
                    "quantity": o.get("fill", {}).get("quantity"), # quantity of stock purchased
                    "cost_in_pounds": o.get("fill", {}).get("walletImpact", {}).get("netValue"), # cost in £
                    "executed_currency": o.get("fill", {}).get("walletImpact", {}).get("currency"), # currency conversion
                    "fx_rate": o.get("fill", {}).get("walletImpact", {}).get("fxRate"),
                    "filled_at": parse_dt(o.get("fill", {}).get("filledAt")),
                }
                for o in new_items
            ]
            async with get_session_factory()() as session:
                stmt = insert(Order).values(rows).on_conflict_do_nothing(index_elements=["id"])
                await session.execute(stmt)
                await session.commit()

            total += len(new_items)
            log.info(f"Orders: inserted {total} so far...")

        if done:
            log.info("Orders: reached existing data, stopping")
            break

        cursor = response.get("nextPagePath")
        if not cursor:
            break

        await asyncio.sleep(10)

    return total


async def backfill_dividends(client: TradingAppClient) -> int:
    since = await get_latest(Dividend.paid_at)
    if since:
        log.info(f"Dividends: backfilling from {since}")
    else:
        log.info("Dividends: table empty, backfilling everything")

    cursor = None
    total = 0

    while True:
        response = await client.get_dividends(cursor=cursor, limit=50)
        items = response.get("items", [])

        if not items:
            break

        new_items = []
        done = False
        for d in items:
            paid_at = parse_dt(d.get("paidOn"))
            if since and paid_at and paid_at <= since:
                done = True
                break
            new_items.append(d)

        if new_items:
            rows = [
                {
                    "id": d["reference"],
                    "ticker": d.get("ticker"),
                    "name": d.get("instrument", {}).get("name"),
                    "quantity": d.get("quantity"),
                    "amount": d.get("amount"),
                    "amount_in_euro": d.get("amountInEuro"),
                    "tax_withheld": 0,
                    "paid_at": parse_dt(d.get("paidOn")),
                    "currency": d.get("currency"),
                }
                for d in new_items
            ]
            async with get_session_factory()() as session:
                stmt = insert(Dividend).values(rows).on_conflict_do_nothing(index_elements=["id"])
                await session.execute(stmt)
                await session.commit()

            total += len(new_items)
            log.info(f"Dividends: inserted {total} so far...")

        if done:
            log.info("Dividends: reached existing data, stopping")
            break

        cursor = response.get("nextPagePath")
        if not cursor:
            break

        await asyncio.sleep(10)

    return total


async def run_backfill() -> None:
    log.info("Creating tables if not exist...")
    await create_tables()

    async with TradingAppClient() as client:
        log.info("Starting incremental backfill...")

        orders = await backfill_orders(client)
        dividends = await backfill_dividends(client)
        log.info(
            f"Backfill complete. Orders: {orders}, Dividends: {dividends}"
        )

    await close_engine()


if __name__ == "__main__":
    asyncio.run(run_backfill())
