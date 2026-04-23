import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from textblob import TextBlob

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")
st.title("📊 AI Stock Market Analyzer (Tech + News)")

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("Stock Settings")
symbol = st.sidebar.text_input("Enter Stock Symbol", "RELIANCE.NS")
period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"])

# -------------------------------
# Fetch Stock Data
# -------------------------------
data = yf.download(symbol, period=period, interval="1d")

if data.empty:
    st.error("No data found. Try another symbol.")
    st.stop()

# -------------------------------
# Technical Indicators
# -------------------------------

# RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data["RSI"] = compute_rsi(data["Close"])

# EMA
data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()

# -------------------------------
# Support & Resistance (Simple)
# -------------------------------
support = data["Low"].rolling(window=10).min().iloc[-1]
resistance = data["High"].rolling(window=10).max().iloc[-1]

# -------------------------------
# Buy/Sell Logic
# -------------------------------
latest = data.iloc[-1]

signal = "HOLD"

if latest["RSI"] < 30 and latest["EMA20"] > latest["EMA50"] and latest["Close"] > support:
    signal = "BUY 🟢"
elif latest["RSI"] > 70 and latest["Close"] < resistance:
    signal = "SELL 🔴"

# Stoploss & Target
stoploss = support
target = resistance

# -------------------------------
# Metrics UI
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Stock", symbol)
col2.metric("Price", f"{latest['Close']:.2f}")
col3.metric("Signal", signal)
col4.metric("RSI", f"{latest['RSI']:.2f}")

st.divider()

# -------------------------------
# Candlestick Chart
# -------------------------------
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Price"
))

# Support / Resistance lines
fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Support")
fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Resistance")

fig.update_layout(template="plotly_dark", title="Stock Chart with Support & Resistance")

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Stoploss & Target
# -------------------------------
st.subheader("🎯 Trade Levels")

col5, col6 = st.columns(2)
col5.metric("Stoploss", f"{stoploss:.2f}")
col6.metric("Target", f"{target:.2f}")

# -------------------------------
# News Section (Free API alternative via RSS-like scraping)
# -------------------------------
st.subheader("📰 Latest Business News")

def get_news():
    url = f"https://newsapi.org/v2/everything?q=stock OR market OR economy&sortBy=publishedAt&language=en&apiKey=YOUR_API_KEY"
    return None

st.info("To enable real news, add NewsAPI key (free at newsapi.org)")

# Demo static news (fallback)
news = [
    "Oil prices rise due to global tensions",
    "FIIs continue selling in Indian markets",
    "RBI maintains repo rate unchanged",
    "Tech stocks show strong earnings growth"
]

for n in news:
    sentiment = TextBlob(n).sentiment.polarity
    if sentiment > 0:
        tag = "🟢 Positive"
    elif sentiment < 0:
        tag = "🔴 Negative"
    else:
        tag = "🟡 Neutral"

    st.write(f"• {n}  —  {tag}")

# -------------------------------
# Final Insight
# -------------------------------
st.subheader("🧠 AI Insight (Rule-based)")

if signal.startswith("BUY"):
    st.success("Market shows bullish setup. Consider BUY with risk management.")
elif signal.startswith("SELL"):
    st.error("Market shows bearish signals. Avoid long positions.")
else:
    st.warning("No strong trend detected. Wait for confirmation.")