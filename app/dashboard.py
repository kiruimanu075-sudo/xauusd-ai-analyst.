import streamlit as st
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from zoneinfo import ZoneInfo

from app.market_data import get_market_data
from app.strategy import analyse_market


st.set_page_config(
    page_title="XAUUSD AI Analyst",
    page_icon="chart_with_upwards_trend",
    layout="wide"
)

st_autorefresh(
    interval=60000,
    key="market_refresh"
)

st.title("XAUUSD AI MARKET ANALYST")

kenya_time = datetime.now(ZoneInfo("Africa/Nairobi"))

st.caption(
    f"Kenya time: {kenya_time.strftime('%Y-%m-%d %H:%M:%S')} EAT"
)

@st.cache_data(ttl=50, show_spinner=False)
def load_data():
    return get_market_data()


with st.spinner("Loading Gold market data..."):
    data = load_data()

analysis = analyse_market(data)

if analysis["status"] != "Connected":
    st.error(
        "Market data unavailable or insufficient. "
        "Check your internet connection and data provider."
    )
    st.stop()

symbol = data.attrs.get("symbol", "Unknown source")

st.caption(
    f"Data source: Yahoo Finance | Symbol: {symbol} "
    "| Refresh interval: 60 seconds"
)

# Main market metrics
c1, c2, c3, c4 = st.columns(4)

c1.metric("Gold Price", f"{analysis['price']:.2f}")
c2.metric("Market Bias", analysis["bias"])
c3.metric(
    "RSI",
    f"{analysis['rsi']:.2f}"
    if analysis["rsi"] is not None else "N/A"
)
c4.metric("Momentum", analysis["momentum"])

st.divider()

# Market structure
st.subheader("Market Structure")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Liquidity")

    st.write(
        "Bullish sweep detected"
        if analysis["bullish_sweep"]
        else "No bullish sweep detected"
    )

    st.write(
        "Bearish sweep detected"
        if analysis["bearish_sweep"]
        else "No bearish sweep detected"
    )

    st.markdown("### Break of Structure")

    st.write(
        "Bullish BOS detected"
        if analysis["bullish_bos"]
        else "No bullish BOS detected"
    )

    st.write(
        "Bearish BOS detected"
        if analysis["bearish_bos"]
        else "No bearish BOS detected"
    )

with col2:
    st.markdown("### Fair Value Gaps")

    st.write(
        "Potential bullish FVG detected"
        if analysis["bullish_fvg"]
        else "No bullish FVG detected"
    )

    st.write(
        "Potential bearish FVG detected"
        if analysis["bearish_fvg"]
        else "No bearish FVG detected"
    )

    st.markdown("### Reference Levels")

    st.write(f"Previous high: {analysis['previous_high']:.2f}")
    st.write(f"Previous low: {analysis['previous_low']:.2f}")

st.divider()

# Candlestick chart
st.subheader("XAUUSD Candlestick Chart")

df = analysis["candles"].tail(150)

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Gold"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA20"],
        name="EMA 20"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA50"],
        name="EMA 50"
    )
)

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Market assessment
st.subheader("Current Market Assessment")

if analysis["bias"] == "BULLISH":
    st.success(
        "Short-term bullish trend according to the EMA rules. "
        "Wait for confirmation before considering a long setup."
    )

elif analysis["bias"] == "BEARISH":
    st.warning(
        "Short-term bearish trend according to the EMA rules. "
        "Wait for confirmation before considering a short setup."
    )

else:
    st.info(
        "No clear directional trend according to the EMA rules."
    )

if analysis["atr"] is not None:
    st.write(f"14-period ATR: {analysis['atr']:.3f}")

st.caption(
    "Educational analysis only. Signals are not guaranteed. "
    "This application does not execute trades."
)
