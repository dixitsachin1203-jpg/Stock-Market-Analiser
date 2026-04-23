import streamlit as st
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Robo Stock Analyst Pro", layout="wide")

st.title("📊 Robo Stock Analyst Pro Dashboard")
st.markdown("### Select stock → auto-filled fundamentals → deep analysis")

# ---------------------------
# PREDEFINED STOCK DATABASE (AUTO-FILL SYSTEM)
# ---------------------------
stock_db = {
    "Reliance": {
        "price": 1380,
        "pe": 22.4,
        "pb": 1.75,
        "roe": 8.4,
        "debt": 0.36,
        "margin": 10.5,
        "dividend_yield": 0.9,
        "current_ratio": 1.1
    },
    "TCS": {
        "price": 3800,
        "pe": 28.2,
        "pb": 12.5,
        "roe": 45,
        "debt": 0.05,
        "margin": 25,
        "dividend_yield": 1.2,
        "current_ratio": 2.0
    },
    "Infosys": {
        "price": 1500,
        "pe": 24,
        "pb": 7.8,
        "roe": 32,
        "debt": 0.1,
        "margin": 21,
        "dividend_yield": 2.1,
        "current_ratio": 2.2
    },
    "HDFC Bank": {
        "price": 1600,
        "pe": 18,
        "pb": 2.3,
        "roe": 18,
        "debt": 0.0,
        "margin": 15,
        "dividend_yield": 1.0,
        "current_ratio": 1.5
    }
}

# ---------------------------
# STOCK SELECTION (AUTO-FILL)
# ---------------------------
stock = st.selectbox("📌 Select Stock", list(stock_db.keys()))

data = stock_db[stock]

# AUTO-FILLED VALUES
price = data["price"]
pe = data["pe"]
pb = data["pb"]
roe = data["roe"]
debt = data["debt"]
margin = data["margin"]
dividend = data["dividend_yield"]
current_ratio = data["current_ratio"]

# ---------------------------
# EPS + INTRINSIC VALUE
# ---------------------------
eps = price / pe
intrinsic_value = (eps * (8.5 + 2 * roe)) / 10
gap = intrinsic_value - price

# ---------------------------
# IMPROVED SCORING SYSTEM
# ---------------------------
score = 0

# valuation
if pe < 20:
    score += 2
elif pe < 30:
    score += 1
else:
    score -= 2

# profitability
if roe > 25:
    score += 3
elif roe > 15:
    score += 2
else:
    score -= 2

# leverage
if debt < 0.5:
    score += 2
else:
    score -= 2

# margins
if margin > 20:
    score += 2
elif margin > 10:
    score += 1
else:
    score -= 1

# liquidity
if current_ratio > 1.5:
    score += 1

# dividend
if dividend > 1:
    score += 1

# ---------------------------
# FINAL SIGNAL
# ---------------------------
if score >= 7:
    signal = "🟢 STRONG BUY"
elif score >= 4:
    signal = "🟡 HOLD"
else:
    signal = "🔴 SELL"

# ---------------------------
# UI DASHBOARD
# ---------------------------
st.subheader(f"📊 Analysis for {stock}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Price", price)
col2.metric("Intrinsic Value", round(intrinsic_value, 2))
col3.metric("Score", score)
col4.metric("Signal", signal)

st.divider()

# ---------------------------
# CHART 1: PRICE vs VALUE
# ---------------------------
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=["Market Price", "Intrinsic Value"],
    y=[price, intrinsic_value],
    marker_color=["red", "green"]
))
fig1.update_layout(template="plotly_dark", title="Price vs Intrinsic Value")
st.plotly_chart(fig1, use_container_width=True)

# ---------------------------
# CHART 2: RATIO HEALTH (DONUT STYLE)
# ---------------------------
labels = ["ROE", "Margins", "Debt Safety", "Liquidity", "Valuation"]
values = [
    roe,
    margin,
    max(0, 100 - debt * 50),
    current_ratio * 50,
    max(0, 100 - pe * 2)
]

fig2 = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hole=0.5
)])

fig2.update_layout(template="plotly_dark", title="Financial Health Breakdown")
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# CHART 3: SCORE VISUAL
# ---------------------------
fig3 = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    title={'text': "Investment Strength Score"},
    gauge={
        'axis': {'range': [-5, 10]},
        'bar': {'color': "blue"},
        'steps': [
            {'range': [-5, 0], 'color': "red"},
            {'range': [0, 4], 'color': "orange"},
            {'range': [4, 10], 'color': "green"}
        ]
    }
))

st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# FINAL INSIGHT PANEL
# ---------------------------
st.subheader("🧠 AI Analysis Summary")

st.write(f"""
### 📌 Key Metrics
- EPS: {round(eps,2)}
- ROE: {roe}%
- Margin: {margin}%
- Debt: {debt}
- Current Ratio: {current_ratio}

### 💰 Valuation
- Intrinsic Value: {round(intrinsic_value,2)}
- Market Price: {price}
- Gap: {round(gap,2)}

### 📊 Verdict
**{signal}**

👉 {'Stock is undervalued based on fundamentals.' if gap > 0 else 'Stock is overvalued or fairly priced.'}
""")

# ---------------------------
# FINAL RECOMMENDATION
# ---------------------------
st.divider()

if signal == "🟢 STRONG BUY":
    st.success("Strong long-term accumulation opportunity.")
elif signal == "🟡 HOLD":
    st.warning("Hold and monitor quarterly results.")
else:
    st.error("Avoid or reduce exposure due to weak fundamentals.")
