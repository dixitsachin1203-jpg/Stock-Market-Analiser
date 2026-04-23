import streamlit as st
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG + UI STYLE
# ---------------------------
st.set_page_config(page_title="Robo Stock Analyst", layout="wide")

st.markdown("""
    <style>
    .main {background-color:#0e1117;}
    .block-container {padding-top:2rem;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Robo Stock Analyst Dashboard")

st.markdown("### Enter stock fundamentals for deep valuation analysis")

# ---------------------------
# INPUT SECTION (MORE SPECIFIC)
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    price = st.number_input("📌 Current Market Price", min_value=1.0)
    pe = st.number_input("📊 P/E Ratio", min_value=0.1)
    pb = st.number_input("📊 P/B Ratio", min_value=0.1)

with col2:
    roe = st.number_input("📈 ROE (%)", min_value=0.1)
    debt = st.number_input("⚠ Debt-to-Equity Ratio", min_value=0.0)
    margin = st.number_input("💰 Profit Margin (%)", min_value=0.0)

risk = st.selectbox("🎯 Risk Profile", ["Low", "Medium", "High"])

st.divider()

# ---------------------------
# EPS ESTIMATION
# ---------------------------
eps = price / pe if pe > 0 else 0

# ---------------------------
# INTRINSIC VALUE MODEL
# ---------------------------
discount_factor = 10  # simplified constant

intrinsic_value = (eps * (8.5 + 2 * roe)) / discount_factor

# ---------------------------
# VALUE GAP
# ---------------------------
gap = intrinsic_value - price

if gap > 0:
    verdict = "🟢 UNDERVALUED (BUY ZONE)"
elif gap < 0:
    verdict = "🔴 OVERVALUED (RISKY)"
else:
    verdict = "🟡 FAIRLY VALUED"

# ---------------------------
# SCORE SYSTEM
# ---------------------------
score = 0

if pe < 20:
    score += 2
else:
    score -= 1

if roe > 20:
    score += 3
elif roe > 10:
    score += 1
else:
    score -= 2

if pb < 3:
    score += 2
else:
    score -= 1

if debt < 1:
    score += 2
else:
    score -= 2

if margin > 15:
    score += 2
else:
    score -= 1

if risk == "High":
    score += 1
elif risk == "Low":
    score -= 1

# ---------------------------
# FINAL SIGNAL
# ---------------------------
if score >= 7:
    signal = "🟢 STRONG BUY"
elif score >= 3:
    signal = "🟡 HOLD"
else:
    signal = "🔴 SELL"

# ---------------------------
# DASHBOARD UI
# ---------------------------
st.subheader("📊 Stock Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Market Price", price)
c2.metric("Intrinsic Value", round(intrinsic_value, 2))
c3.metric("Score", score)

st.divider()

# ---------------------------
# COMPARISON CHART (PRICE VS VALUE)
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
# SCORE BREAKDOWN CHART
# ---------------------------
fig2 = go.Figure()

categories = ["PE", "ROE", "PB", "Debt", "Margin"]
values = [
    2 if pe < 20 else -1,
    3 if roe > 20 else 1,
    2 if pb < 3 else -1,
    2 if debt < 1 else -2,
    2 if margin > 15 else -1
]

fig2.add_trace(go.Bar(
    x=categories,
    y=values,
    marker_color="skyblue"
))

fig2.update_layout(template="plotly_dark", title="Fundamental Score Breakdown")

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# GAUGE STYLE SCORE
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
            {'range': [0, 3], 'color': "orange"},
            {'range': [3, 10], 'color': "green"}
        ]
    }
))

st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# FINAL INSIGHTS PANEL
# ---------------------------
st.subheader("🧠 AI Investment Analysis")

colA, colB = st.columns(2)

with colA:
    st.success(f"Signal: {signal}")

with colB:
    st.info(f"Valuation Verdict: {verdict}")

st.markdown("### 📌 Explanation")

st.write(f"""
- EPS (Estimated): {round(eps,2)}
- Intrinsic Value: {round(intrinsic_value,2)}
- Market Price: {price}
- Value Gap: {round(gap,2)}

👉 The stock is considered **{verdict}** based on intrinsic value model and financial ratios.
""")

# ---------------------------
# FINAL RECOMMENDATION
# ---------------------------
st.divider()

if signal == "🟢 STRONG BUY":
    st.success("Recommendation: Strong accumulation opportunity based on fundamentals.")
elif signal == "🟡 HOLD":
    st.warning("Recommendation: Hold and monitor performance.")
else:
    st.error("Recommendation: Avoid or exit position due to weak fundamentals.")
