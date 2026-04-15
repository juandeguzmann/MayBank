from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.api.dividends import router as dividends_router
from backend.api.portfolio import router as portfolio_router
from backend.core.t212.backfill import run_backfill
from backend.db.postgres import close_engine

log = logging.getLogger(__name__)

templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("App startup: running backfill...")
    run_backfill()
    yield
    close_engine()


app = FastAPI(title="MayBank", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.include_router(dividends_router)
app.include_router(portfolio_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def index():
    return RedirectResponse(url="/home")


@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/dividends")
async def dividends(request: Request):
    return templates.TemplateResponse("dividends.html", {"request": request})


def start():
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
