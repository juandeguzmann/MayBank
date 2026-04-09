-- Orders: every buy/sell executed on T212 ISA
CREATE TABLE IF NOT EXISTS orders (
    id                  TEXT PRIMARY KEY,
    ticker              TEXT NOT NULL,
    name                TEXT,
    type                TEXT NOT NULL,          -- BUY / SELL
    quantity            NUMERIC,
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