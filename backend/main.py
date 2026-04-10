from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI

from backend.core.t212.backfill import run_backfill
from backend.db.postgres import close_engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("App startup: running backfill...")
    run_backfill()
    yield
    close_engine()


app = FastAPI(title="MayBank", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


def start():
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
