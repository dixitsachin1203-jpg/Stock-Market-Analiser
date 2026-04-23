import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG (UI UPGRADE)
# ---------------------------
st.set_page_config(page_title="Advanced Stock Intelligence", layout="wide")

st.markdown("""
    <style>
    .main {background-color:#0e1117;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Advanced Stock Intelligence Dashboard")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_excel("stock_data1.xlsx", engine="openpyxl")

df = load_data()

# ---------------------------
# STOCK SELECTION
# ---------------------------
stocks = df["Stock"].unique()

col1, col2 = st.columns([1,2])

with col1:
    selected_stock = st.selectbox("Select Stock", stocks)

data = df[df["Stock"] == selected_stock].copy()

if data.empty:
    st.error("No data found")
    st.stop()

# ---------------------------
# TECHNICAL INDICATORS
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
# LATEST VALUES
# ---------------------------
latest = data.iloc[-1]

def safe(x):
    return float(x) if pd.notna(x) else 0

close = safe(latest["Close"])
rsi_val = safe(latest["RSI"], 50)
pe = safe(latest["PE"])
pb = safe(latest["PB"])
roe = safe(latest["ROE"])
debt = safe(latest["Debt"])

# ---------------------------
# SUPPORT / RESISTANCE
# ---------------------------
support = float(data["Low"].min())
resistance = float(data["High"].max())

# ---------------------------
# SCORE SYSTEM (VERY IMPORTANT UPGRADE)
# ---------------------------
score = 0

# Technical scoring
if rsi_val < 30:
    score += 2
elif rsi_val > 70:
    score -= 2

if latest["EMA5"] > latest["EMA10"]:
    score += 2
else:
    score -= 1

# Fundamental scoring (ratios)
if pe < 20:
    score += 2
elif pe > 35:
    score -= 2

if pb < 3:
    score += 1

if roe > 20:
    score += 1

if debt < 1:
    score += 1

# ---------------------------
# SIGNAL ENGINE (SHORT + LONG TERM)
# ---------------------------
if score >= 5:
    short_signal = "BUY 🟢"
    long_signal = "STRONG BUY 📈"
elif score >= 2:
    short_signal = "HOLD 🟡"
    long_signal = "ACCUMULATE 📊"
else:
    short_signal = "SELL 🔴"
    long_signal = "EXIT ⚠️"

# ---------------------------
# UI DASHBOARD CARDS
# ---------------------------
st.subheader("📌 Stock Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Price", close)
c2.metric("RSI", rsi_val)
c3.metric("Score", score)
c4.metric("Signal", short_signal)

st.divider()

# ---------------------------
# CHART 1 - PRICE + EMA
# ---------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(y=data["Close"], name="Price"))
fig.add_trace(go.Scatter(y=data["EMA5"], name="EMA 5"))
fig.add_trace(go.Scatter(y=data["EMA10"], name="EMA 10"))

fig.add_hline(y=support, line_color="green", annotation_text="Support")
fig.add_hline(y=resistance, line_color="red", annotation_text="Resistance")

fig.update_layout(template="plotly_dark", height=500)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# CHART 2 - FUNDAMENTAL RATIOS
# ---------------------------
st.subheader("📊 Fundamental Ratios")

ratio_data = pd.DataFrame({
    "Ratio": ["PE", "PB", "ROE", "Debt"],
    "Value": [pe, pb, roe, debt]
})

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=ratio_data["Ratio"],
    y=ratio_data["Value"],
    marker_color=["blue", "orange", "green", "red"]
))

fig2.update_layout(template="plotly_dark", height=400)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# FINAL INSIGHT PANEL
# ---------------------------
st.subheader("🧠 AI Style Analysis Engine")

colA, colB = st.columns(2)

with colA:
    st.success(f"Short-Term Signal: {short_signal}")

with colB:
    st.info(f"Long-Term Signal: {long_signal}")

# ---------------------------
# SCORE BREAKDOWN
# ---------------------------
with st.expander("📊 Score Breakdown"):
    st.write({
        "PE": pe,
        "PB": pb,
        "ROE": roe,
        "Debt": debt,
        "RSI": rsi_val,
        "Total Score": score
    })
