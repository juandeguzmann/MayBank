-- Orders: every buy/sell executed on T212 ISA
CREATE TABLE IF NOT EXISTS orders (
    id                  TEXT PRIMARY KEY,
    ticker              TEXT NOT NULL,
    name                TEXT,
    type                TEXT NOT NULL,          -- BUY / SELL
    quantity            NUMERIC NOT NULL,
    filled_quantity     NUMERIC,
    limit_price         NUMERIC,
    fill_price          NUMERIC,
    fill_cost           NUMERIC,                -- total cost of fill
    status              TEXT NOT NULL,          -- FILLED, CANCELLED, etc.
    created_at          TIMESTAMPTZ NOT NULL,
    filled_at           TIMESTAMPTZ,
    currency            TEXT DEFAULT 'GBP'
);

-- Dividends: all dividend payments received
CREATE TABLE IF NOT EXISTS dividends (
    id                  TEXT PRIMARY KEY,
    ticker              TEXT NOT NULL,
    name                TEXT,
    quantity            NUMERIC NOT NULL,
    amount              NUMERIC NOT NULL,       -- gross dividend amount
    amount_in_gbp       NUMERIC,
    tax_withheld        NUMERIC DEFAULT 0,
    paid_at             TIMESTAMPTZ NOT NULL,
    currency            TEXT DEFAULT 'GBP'
);

-- Transactions: deposits, withdrawals, interest
CREATE TABLE IF NOT EXISTS transactions (
    id                  TEXT PRIMARY KEY,
    type                TEXT NOT NULL,          -- DEPOSIT, WITHDRAWAL, INTEREST
    amount              NUMERIC NOT NULL,
    currency            TEXT DEFAULT 'GBP',
    created_at          TIMESTAMPTZ NOT NULL,
    reference           TEXT
);

-- Portfolio snapshots: daily total value of the ISA
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id                  SERIAL PRIMARY KEY,
    snapshot_date       DATE NOT NULL UNIQUE,
    total_value         NUMERIC NOT NULL,       -- total portfolio value in GBP
    invested_value      NUMERIC NOT NULL,       -- total amount invested
    cash                NUMERIC NOT NULL,
    pnl                 NUMERIC NOT NULL,       -- unrealised + realised
    pnl_pct             NUMERIC NOT NULL
);

-- SP500 daily closes for benchmark comparison
CREATE TABLE IF NOT EXISTS sp500_history (
    price_date          DATE NOT NULL PRIMARY KEY,
    close_price         NUMERIC NOT NULL,
    indexed_value       NUMERIC                 -- pre-computed index to 100 from portfolio start
);

-- Tracks last cursor position for incremental T212 API syncs
CREATE TABLE IF NOT EXISTS sync_cursors (
    endpoint            TEXT PRIMARY KEY,       -- 'orders', 'dividends', 'transactions'
    last_cursor         TEXT,
    last_synced_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
