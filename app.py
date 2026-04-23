import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Smart Stock Analyzer", layout="wide")

st.title("📊 Smart Stock Market Analyzer")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("Stock Selection")

# Predefined stock list (you can expand this anytime)
stock_options = {
    "Reliance (India)": "RELIANCE.NS",
    "TCS (India)": "TCS.NS",
    "Infosys (India)": "INFY.NS",
    "HDFC Bank (India)": "HDFCBANK.NS",
    "ICICI Bank (India)": "ICICIBANK.NS",
    "SBI (India)": "SBIN.NS",
    "Apple (US)": "AAPL",
    "Tesla (US)": "TSLA",
    "Microsoft (US)": "MSFT",
    "NVIDIA (US)": "NVDA"
}

selected_stock = st.sidebar.selectbox(
    "Choose Stock",
    list(stock_options.keys())
)

symbol = stock_options[selected_stock]

period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"])

# ---------------------------
# DATA FETCH (SAFE)
# ---------------------------
@st.cache_data
def load_data(symbol, period):
    try:
        data = yf.download(symbol, period=period, interval="1d", progress=False)
        return data
    except Exception:
        return pd.DataFrame()

data = load_data(symbol, period)

# ---------------------------
# VALIDATION
# ---------------------------
if data is None or data.empty:
    st.error("❌ No data found. Try another stock.")
    st.stop()

# ---------------------------
# INDICATORS
# ---------------------------
def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data["RSI"] = rsi(data["Close"])
data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()

# ---------------------------
# SUPPORT / RESISTANCE
# ---------------------------
support = data["Low"].rolling(10).min().iloc[-1]
resistance = data["High"].rolling(10).max().iloc[-1]

latest = data.iloc[-1]

# ---------------------------
# SIGNAL LOGIC
# ---------------------------
signal = "HOLD 🟡"

if latest["RSI"] < 30 and latest["EMA20"] > latest["EMA50"]:
    signal = "BUY 🟢"
elif latest["RSI"] > 70 and latest["EMA20"] < latest["EMA50"]:
    signal = "SELL 🔴"

stoploss = support
target = resistance

# ---------------------------
# METRICS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Stock", selected_stock)
col2.metric("Price", f"{latest['Close']:.2f}")
col3.metric("Signal", signal)
col4.metric("RSI", f"{latest['RSI']:.2f}")

st.divider()

# ---------------------------
# CHART
# ---------------------------
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Price"
))

fig.add_hline(y=support, line_color="green", line_dash="dash", annotation_text="Support")
fig.add_hline(y=resistance, line_color="red", line_dash="dash", annotation_text="Resistance")

fig.update_layout(template="plotly_dark", height=600)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# TRADE LEVELS
# ---------------------------
st.subheader("🎯 Trade Levels")

c1, c2 = st.columns(2)
c1.metric("Stoploss", f"{stoploss:.2f}")
c2.metric("Target", f"{target:.2f}")

# ---------------------------
# INSIGHT
# ---------------------------
st.subheader("🧠 Insight Engine")

if signal.startswith("BUY"):
    st.success("Bullish setup: Oversold + trend confirmation.")
elif signal.startswith("SELL"):
    st.error("Bearish setup: Overbought + weakness detected.")
else:
    st.warning("No strong trend detected. Wait for confirmation.")

# ---------------------------
# RAW DATA (OPTIONAL)
# ---------------------------
with st.expander("📊 View Raw Data"):
    st.dataframe(data.tail())
