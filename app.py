import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from textblob import TextBlob
import requests

# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📊 Stock Fundamental + Technical Analyzer")

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.header("Stock Selection")

symbol = st.sidebar.text_input("Enter Stock Symbol", "AAPL")
period = st.sidebar.selectbox("Select Period", ["6mo", "1y", "2y"])

# ----------------------------
# LOAD DATA
# ----------------------------
data = yf.download(symbol, period=period, interval="1d")

if data.empty:
    st.error("Invalid stock symbol or no data available")
    st.stop()

# ----------------------------
# TECHNICAL INDICATORS
# ----------------------------

data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data["RSI"] = rsi(data["Close"])

latest = data.iloc[-1]

# ----------------------------
# FUNDAMENTAL DATA
# ----------------------------
ticker = yf.Ticker(symbol)
info = ticker.info

pe = info.get("trailingPE", None)
pb = info.get("priceToBook", None)
market_cap = info.get("marketCap", None)
dividend = info.get("dividendYield", None)

# ----------------------------
# SIGNAL ENGINE
# ----------------------------

score = 0

# Technical scoring
if latest["RSI"] < 30:
    score += 2
elif latest["RSI"] > 70:
    score -= 2

if latest["EMA20"] > latest["EMA50"]:
    score += 2
else:
    score -= 2

# Fundamental scoring
if pe and pe < 20:
    score += 2
elif pe and pe > 40:
    score -= 2

if pb and pb < 3:
    score += 1

# Final decision
if score >= 4:
    signal = "BUY 🟢"
elif score <= -2:
    signal = "SELL 🔴"
else:
    signal = "HOLD 🟡"

# ----------------------------
# UI METRICS
# ----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Stock", symbol)
col2.metric("Signal", signal)
col3.metric("Score", score)

st.divider()

# ----------------------------
# CHART
# ----------------------------
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

fig.update_layout(template="plotly_dark", height=600)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# FUNDAMENTAL RATIOS
# ----------------------------
st.subheader("📊 Fundamental Analysis")

col1, col2, col3, col4 = st.columns(4)

col1.metric("P/E Ratio", pe if pe else "N/A")
col2.metric("P/B Ratio", pb if pb else "N/A")
col3.metric("Market Cap", market_cap if market_cap else "N/A")
col4.metric("Dividend Yield", dividend if dividend else "N/A")

# ----------------------------
# NEWS SECTION
# ----------------------------
st.subheader("📰 Company News")

query = symbol + " stock"

url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey=YOUR_API_KEY"

st.info("Add NewsAPI key to enable live news")

demo_news = [
    "Company reports strong quarterly earnings",
    "Market reacts to economic slowdown concerns",
    "Analysts upgrade stock rating"
]

for n in demo_news:
    sentiment = TextBlob(n).sentiment.polarity

    if sentiment > 0:
        tag = "🟢 Positive"
    elif sentiment < 0:
        tag = "🔴 Negative"
    else:
        tag = "🟡 Neutral"

    st.write(f"• {n} — {tag}")

# ----------------------------
# INSIGHT SECTION
# ----------------------------
st.subheader("🧠 AI Insight")

if signal.startswith("BUY"):
    st.success("Strong fundamentals + technical strength detected.")
elif signal.startswith("SELL"):
    st.error("Weak fundamentals or bearish trend detected.")
else:
    st.warning("Mixed signals. Wait for better confirmation.")
