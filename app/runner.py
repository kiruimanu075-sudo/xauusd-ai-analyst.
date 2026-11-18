"""
Flexible local runner. Starts immediately and continues until Ctrl+C.
No fixed market hours are imposed.
"""
import logging
import time
from pathlib import Path

from app.market_data import get_market_data
from app.strategy import analyse_market

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
DATA_DIR = ROOT / "data"
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "market_runner.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("xauusd_runner")
POLL_SECONDS = 60


def main():
    log.info("XAUUSD analyst running continuously. Press Ctrl+C to stop.")
    while True:
        try:
            data = get_market_data()
            if data is None or data.empty:
                log.warning("No candles received; retrying in %s seconds.", POLL_SECONDS)
            else:
                result = analyse_market(data)
                log.info(
                    "Status=%s | Price=%s | Bias=%s | RSI=%s",
                    result.get("status"),
                    result.get("price"),
                    result.get("bias"),
                    result.get("rsi"),
                )
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log.info("Stopped by user.")
            break
        except Exception:
            log.exception("Update failed; retrying in %s seconds.", POLL_SECONDS)
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
