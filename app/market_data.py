import yfinance as yf
import pandas as pd

SYMBOLS = ["XAUUSD=X", "GC=F"]


def get_market_data(period="5d", interval="5m"):
    """
    Fetch Gold price candles.
    XAUUSD=X is attempted first.
    GC=F is used as a fallback.
    This is not a direct TradingView feed.
    """

    for symbol in SYMBOLS:
        try:
            data = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False
            )

            if data.empty:
                continue

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            required = ["Open", "High", "Low", "Close"]

            if not all(col in data.columns for col in required):
                continue

            data = data.dropna(subset=required)

            if len(data) < 50:
                continue

            data.attrs["symbol"] = symbol
            return data

        except Exception as error:
            print(f"Error fetching {symbol}: {error}")

    return None
