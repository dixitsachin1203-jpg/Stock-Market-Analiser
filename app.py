import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from textblob import TextBlob

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📊 Stock Fundamental + Technical Analyzer")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("Stock Selection")

stock_options = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS"
}

selected = st.sidebar.selectbox("Choose Stock", list(stock_options.keys()))
symbol = stock_options[selected]

period = st.sidebar.selectbox("Select Period", ["6mo", "1y", "2y"])

# ---------------------------
# DATA FETCH (SAFE)
# ---------------------------
@st.cache_data
def load_data(symbol, period):
    try:
        data = yf.download(symbol, period=period, interval="1d", progress=False)
        return data
    except:
        return pd.DataFrame()

data = load_data(symbol, period)

# ---------------------------
# VALIDATION FIX
# ---------------------------
if data is None or data.empty:
    st.error("❌ No data found. Try another stock.")
    st.stop()

# Clean data (IMPORTANT FIX)
data = data.replace([np.inf, -np.inf], np.nan).dropna()

# ---------------------------
# TECHNICAL INDICATORS
# ---------------------------

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data["RSI"] = rsi(data["Close"])
data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()

# ---------------------------
# SAFE LAST ROW
# ---------------------------
latest = data.iloc[-1]

def safe(val, default=0.0):
    return float(val) if pd.notna(val) else default

rsi_val = safe(latest["RSI"], 50)
ema20 = safe(latest["EMA20"])
ema50 = safe(latest["EMA50"])
close = safe(latest["Close"])

# ---------------------------
# SUPPORT / RESISTANCE
# ---------------------------
support = float(data["Low"].rolling(10).min().iloc[-1])
resistance = float(data["High"].rolling(10).max().iloc[-1])

# ---------------------------
# SIGNAL ENGINE (FIXED)
# ---------------------------
signal = "HOLD 🟡"

if rsi_val < 30 and ema20 > ema50:
    signal = "BUY 🟢"
elif rsi_val > 70 and ema20 < ema50:
    signal = "SELL 🔴"

# ---------------------------
# UI METRICS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Stock", selected)
col2.metric("Price", f"{close:.2f}")
col3.metric("Signal", signal)
col4.metric("RSI", f"{rsi_val:.2f}")

st.divider()

# ---------------------------
# CANDLESTICK CHART
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

fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], name="EMA20"))
fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], name="EMA50"))

fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Support")
fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Resistance")

fig.update_layout(template="plotly_dark", height=600)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# TRADE LEVELS
# ---------------------------
st.subheader("🎯 Trade Levels")

c1, c2 = st.columns(2)
c1.metric("Stoploss", f"{support:.2f}")
c2.metric("Target", f"{resistance:.2f}")

# ---------------------------
# NEWS (STATIC SAFE VERSION)
# ---------------------------
st.subheader("📰 News Sentiment")

news_list = [
    "Company reports strong earnings this quarter",
    "Market reacts to global economic slowdown",
    "Analysts upgrade stock outlook"
]

for n in news_list:
    polarity = TextBlob(n).sentiment.polarity

    if polarity > 0:
        tag = "🟢 Positive"
    elif polarity < 0:
        tag = "🔴 Negative"
    else:
        tag = "🟡 Neutral"

    st.write(f"• {n} — {tag}")

# ---------------------------
# INSIGHT ENGINE
# ---------------------------
st.subheader("🧠 Insight")

if signal == "BUY 🟢":
    st.success("Strong bullish setup detected (trend + momentum).")
elif signal == "SELL 🔴":
    st.error("Bearish conditions detected. Weak momentum.")
else:
    st.warning("No strong trend. Wait for confirmation.")
