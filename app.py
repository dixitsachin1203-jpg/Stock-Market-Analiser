import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📊 Excel-Based Stock Analyzer (Streamlit)")

# ---------------------------
# LOAD EXCEL FILE
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("stock_data.xlsx", engine="openpyxl")
    return df

df = load_data()

# ---------------------------
# STOCK SELECTION
# ---------------------------
stocks = df["Stock"].unique()
selected_stock = st.selectbox("Select Stock", stocks)

data = df[df["Stock"] == selected_stock].copy().reset_index(drop=True)

if data.empty:
    st.error("No data found for selected stock")
    st.stop()

# ---------------------------
# INDICATORS
# ---------------------------

data["EMA5"] = data["Close"].ewm(span=5).mean()
data["EMA10"] = data["Close"].ewm(span=10).mean()

def rsi(series, period=5):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data["RSI"] = rsi(data["Close"])

# ---------------------------
# CLEAN LAST ROW SAFELY
# ---------------------------
latest = data.iloc[-1]

def safe(val, default=0.0):
    return float(val) if pd.notna(val) else default

close = safe(latest["Close"])
rsi_val = safe(latest["RSI"], 50)
ema5 = safe(latest["EMA5"])
ema10 = safe(latest["EMA10"])

# ---------------------------
# SUPPORT / RESISTANCE
# ---------------------------
support = float(data["Low"].min())
resistance = float(data["High"].max())

# ---------------------------
# SIGNAL ENGINE
# ---------------------------
signal = "HOLD 🟡"

if rsi_val < 30 and ema5 > ema10:
    signal = "BUY 🟢"
elif rsi_val > 70 and ema5 < ema10:
    signal = "SELL 🔴"

# ---------------------------
# DASHBOARD METRICS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Stock", selected_stock)
col2.metric("Close Price", close)
col3.metric("Signal", signal)
col4.metric("RSI", round(rsi_val, 2))

st.divider()

# ---------------------------
# CHART
# ---------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(y=data["Close"], name="Close Price"))
fig.add_trace(go.Scatter(y=data["EMA5"], name="EMA5"))
fig.add_trace(go.Scatter(y=data["EMA10"], name="EMA10"))

fig.add_hline(y=support, line_color="green", annotation_text="Support")
fig.add_hline(y=resistance, line_color="red", annotation_text="Resistance")

fig.update_layout(template="plotly_dark", height=600)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# TRADE LEVELS
# ---------------------------
st.subheader("🎯 Trade Levels")

c1, c2 = st.columns(2)
c1.metric("Stoploss (Support)", support)
c2.metric("Target (Resistance)", resistance)

# ---------------------------
# INSIGHT
# ---------------------------
st.subheader("🧠 Analysis Result")

if signal == "BUY 🟢":
    st.success("Bullish setup detected: Momentum + trend alignment")
elif signal == "SELL 🔴":
    st.error("Bearish setup detected: Weak momentum")
else:
    st.warning("No strong trend detected. Market is neutral")
