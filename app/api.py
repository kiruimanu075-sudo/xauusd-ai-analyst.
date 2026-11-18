import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.market_data import get_market_data
from app.strategy import analyse_market

POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
EAT = ZoneInfo("Africa/Nairobi")
log = logging.getLogger("xauusd_api")
logging.basicConfig(level=logging.INFO)

latest = {
    "status": "Starting",
    "message": "Waiting for the first market-data update",
    "updated_at": None,
}
worker_task = None


def make_json_safe(result):
    output = {}
    for key, value in result.items():
        if key == "candles":
            continue
        if hasattr(value, "item"):
            value = value.item()
        if value is None or isinstance(value, (str, int, float, bool)):
            output[key] = value
        else:
            output[key] = str(value)
    output["updated_at"] = datetime.now(timezone.utc).isoformat()
    output["updated_at_eat"] = datetime.now(EAT).isoformat()
    return output


async def market_loop():
    global latest
    while True:
        try:
            data = await asyncio.to_thread(get_market_data)
            if data is None or data.empty:
                latest = {
                    "status": "No market data",
                    "message": "The market-data provider returned no candles.",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                log.warning("No market data returned")
            else:
                result = await asyncio.to_thread(analyse_market, data)
                latest = make_json_safe(result)
                log.info(
                    "Updated XAUUSD analysis: price=%s bias=%s",
                    latest.get("price"), latest.get("bias")
                )
        except Exception as exc:
            log.exception("Market update failed")
            latest = {
                "status": "Error",
                "message": str(exc),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        await asyncio.sleep(POLL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_task
    worker_task = asyncio.create_task(market_loop())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="XAUUSD AI Analyst API",
    version="1.0.0",
    lifespan=lifespan,
)

# Dashboard is public static content; restrict this to your Netlify domain
# after deployment by setting NETLIFY_ORIGIN in the backend environment.
origin = os.getenv("NETLIFY_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin] if origin != "*" else ["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "XAUUSD AI Analyst API",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "online",
        "poll_seconds": POLL_SECONDS,
        "updated_at": latest.get("updated_at"),
    }


@app.get("/api/latest")
def latest_analysis():
    return latest
