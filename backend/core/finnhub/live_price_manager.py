import websocket
import logging
import json

from backend.config import FINNHUB_API_KEY
from backend.models.finnhub import LivePrice

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logging.getLogger("websocket").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "trade":
        latest = max(data["data"], key=lambda t: t["t"])
        logger.info(LivePrice(
            conditions=latest["c"],
            price=latest["p"],
            symbol=latest["s"],
            timestamp=latest["t"],
            volume=latest["v"],
        ))


def on_error(ws, error):
    logger.error(error)


def on_close(ws, close_status_code, close_msg):
    pass


def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')


def run():
    ws = websocket.WebSocketApp(
        f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever(reconnect=5)
