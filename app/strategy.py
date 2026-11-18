import pandas as pd
import numpy as np


def analyse_market(data):

    if data is None or len(data) < 50:
        return {"status": "Insufficient market data"}

    df = data.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    # Exponential moving averages
    df["EMA20"] = close.ewm(span=20, adjust=False).mean()
    df["EMA50"] = close.ewm(span=50, adjust=False).mean()

    # RSI
    change = close.diff()
    gain = change.clip(lower=0)
    loss = -change.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ATR
    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs()
        ],
        axis=1
    ).max(axis=1)

    df["ATR"] = true_range.rolling(14).mean()

    latest = df.iloc[-1]

    # Directional bias
    if latest["EMA20"] > latest["EMA50"]:
        bias = "BULLISH"
    elif latest["EMA20"] < latest["EMA50"]:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    # Previous 20-candle liquidity levels
    previous_high = high.iloc[-21:-1].max()
    previous_low = low.iloc[-21:-1].min()

    # Potential liquidity sweeps
    bullish_sweep = (
        latest["Low"] < previous_low
        and latest["Close"] > previous_low
    )

    bearish_sweep = (
        latest["High"] > previous_high
        and latest["Close"] < previous_high
    )

    # Basic break of structure
    bullish_bos = latest["Close"] > previous_high
    bearish_bos = latest["Close"] < previous_low

    # Three-candle FVG approximation
    bullish_fvg = low.iloc[-1] > high.iloc[-3]
    bearish_fvg = high.iloc[-1] < low.iloc[-3]

    # RSI interpretation
    rsi = latest["RSI"]

    if pd.isna(rsi):
        momentum = "Unavailable"
    elif rsi >= 70:
        momentum = "Overbought"
    elif rsi <= 30:
        momentum = "Oversold"
    else:
        momentum = "Neutral"

    return {
        "status": "Connected",
        "price": float(latest["Close"]),
        "ema20": float(latest["EMA20"]),
        "ema50": float(latest["EMA50"]),
        "rsi": float(rsi) if pd.notna(rsi) else None,
        "atr": float(latest["ATR"]) if pd.notna(latest["ATR"]) else None,
        "bias": bias,
        "momentum": momentum,
        "bullish_sweep": bool(bullish_sweep),
        "bearish_sweep": bool(bearish_sweep),
        "bullish_bos": bool(bullish_bos),
        "bearish_bos": bool(bearish_bos),
        "bullish_fvg": bool(bullish_fvg),
        "bearish_fvg": bool(bearish_fvg),
        "previous_high": float(previous_high),
        "previous_low": float(previous_low),
        "candles": df
    }
