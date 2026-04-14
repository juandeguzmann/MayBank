"""
Incremental backfill from Trading 212.

On startup, checks the latest record in each table and only fetches
data newer than that. If a table is empty, fetches everything.

Usage:
    uv run python -m backend.core.t212.backfill
"""
import logging
import time
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from urllib.parse import parse_qs

from backend.core.t212.client import TradingAppClient
from backend.db.models.postgres import Dividend, Order, Transactions
from backend.db.postgres import create_tables, session_factory

log = logging.getLogger(__name__)

PAGE_SIZE = 50
RATE_LIMIT_DELAY = 10  # seconds between pages


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_latest(column) -> datetime | None:
    with session_factory() as session:
        result = session.execute(select(func.max(column)))
        return result.scalar()


def backfill_orders(client: TradingAppClient) -> int:
    since = get_latest(Order.created_at)
    log.info(f"Orders: backfilling from {since}" if since else "Orders: table empty, backfilling everything")

    cursor = None
    total = 0

    while True:
        response = client.get_orders(cursor=cursor, limit=PAGE_SIZE)
        items = response.get("items", [])

        if not items:
            break

        new_items, done = [], False
        for o in items:
            if since and (ts := parse_dt(o["order"].get("createdAt"))) and ts <= since:
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
                    "price_of_stock": o.get("fill", {}).get("price"),
                    "quantity": o.get("fill", {}).get("quantity"),
                    "cost_in_pounds": o.get("fill", {}).get("walletImpact", {}).get("netValue"),
                    "executed_currency": o.get("fill", {}).get("walletImpact", {}).get("currency"),
                    "fx_rate": o.get("fill", {}).get("walletImpact", {}).get("fxRate"),
                    "filled_at": parse_dt(o.get("fill", {}).get("filledAt")),
                }
                for o in new_items
            ]
            with session_factory() as session:
                stmt = insert(Order).values(rows).on_conflict_do_nothing(index_elements=["id"])
                session.execute(stmt)
                session.commit()

            total += len(new_items)
            log.info(f"Orders: {total} inserted so far...")

        if done:
            log.info("Orders: reached existing data, stopping")
            break

        cursor = response.get("nextPagePath")
        if not cursor:
            break

        time.sleep(RATE_LIMIT_DELAY)

    return total


def backfill_dividends(client: TradingAppClient) -> int:
    since = get_latest(Dividend.paid_at)
    log.info(f"Dividends: backfilling from {since}" if since else "Dividends: table empty, backfilling everything")

    cursor = None
    total = 0

    while True:
        response = client.get_dividends(cursor=cursor, limit=PAGE_SIZE)
        items = response.get("items", [])

        if not items:
            break

        new_items, done = [], False
        for d in items:
            if since and (ts := parse_dt(d.get("paidOn"))) and ts <= since:
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
            with session_factory() as session:
                stmt = insert(Dividend).values(rows).on_conflict_do_nothing(index_elements=["id"])
                session.execute(stmt)
                session.commit()

            total += len(new_items)
            log.info(f"Dividends: {total} inserted so far...")

        if done:
            log.info("Dividends: reached existing data, stopping")
            break

        cursor = response.get("nextPagePath")
        if not cursor:
            break

        time.sleep(RATE_LIMIT_DELAY)

    return total


def backfill_transactions(client: TradingAppClient) -> int:
    since = get_latest(Transactions.date_time)
    log.info(f"Transactions: backfilling from {since}" if since else "Transactions: table empty, backfilling everything")

    cursor = None
    next_time = None
    total = 0

    while True:
        response = client.get_transactions(cursor=cursor, limit=PAGE_SIZE, time=next_time)
        items = response.get("items", [])

        if not items:
            break

        new_items, done = [], False
        for d in items:
            if since and (ts := parse_dt(d.get("dateTime"))) and ts <= since:
                done = True
                break
            new_items.append(d)

        if new_items:
            rows = [
                {
                    "type": d["type"],
                    "amount": d.get("amount"),
                    "currency": d.get("currency"),
                    "reference": d.get("reference"),
                    "date_time": d.get("dateTime"),
                }
                for d in new_items
            ]
            with session_factory() as session:
                stmt = insert(Transactions).values(rows).on_conflict_do_nothing(index_elements=["reference"])
                session.execute(stmt)
                session.commit()

            total += len(new_items)
            log.info(f"Transactions: {total} inserted so far...")

        if done:
            log.info("Transactions: reached existing data, stopping")
            break

        next_page = response.get("nextPagePath")
        if not next_page:
            break

        parsed = parse_qs(next_page)
        cursor = parsed.get("cursor", [None])[0]
        next_time = parsed.get("time", [None])[0]

        time.sleep(RATE_LIMIT_DELAY)

    return total


def run_backfill() -> None:
    log.info("Creating tables if not exist...")
    create_tables()

    with TradingAppClient() as client:
        log.info("Starting incremental backfill...")
        orders = backfill_orders(client)
        dividends = backfill_dividends(client)
        dividends = backfill_transactions(client)
        log.info(f"Backfill complete. Orders: {orders}, Dividends: {dividends}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_backfill()
