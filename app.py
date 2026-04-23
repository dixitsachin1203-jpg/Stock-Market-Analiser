import streamlit as st
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.title("📊 Manual Stock Investment Analyzer")

st.markdown("Enter stock fundamentals to get investment advice (BUY / HOLD / SELL)")

# ---------------------------
# USER INPUTS
# ---------------------------
st.subheader("📌 Stock Details")

price = st.number_input("Current Market Price", min_value=1.0)

pe_ratio = st.number_input("P/E Ratio", min_value=0.0)
pb_ratio = st.number_input("P/B Ratio", min_value=0.0)
roe = st.number_input("ROE (%)", min_value=0.0)
debt = st.number_input("Debt Ratio", min_value=0.0)
growth = st.number_input("Expected Growth (%)", min_value=0.0)

st.subheader("⏳ Investment Preference")

horizon = st.radio("Holding Type", ["Short Term (1-6 months)", "Long Term (1-5 years)"])

risk = st.selectbox("Risk Appetite", ["Low", "Medium", "High"])

# ---------------------------
# SCORE ENGINE
# ---------------------------
score = 0

# Valuation logic
if pe_ratio < 15:
    score += 3
elif pe_ratio < 25:
    score += 1
else:
    score -= 2

if pb_ratio < 3:
    score += 2
else:
    score -= 1

# Profitability
if roe > 20:
    score += 3
elif roe > 10:
    score += 1
else:
    score -= 2

# Debt risk
if debt < 0.5:
    score += 2
elif debt < 1:
    score += 1
else:
    score -= 2

# Growth
if growth > 15:
    score += 3
elif growth > 8:
    score += 1
else:
    score -= 1

# Risk adjustment
if risk == "High":
    score += 1
elif risk == "Low":
    score -= 1

# Horizon adjustment
if "Long" in horizon:
    score += 2
else:
    score -= 1

# ---------------------------
# FINAL DECISION
# ---------------------------
if score >= 8:
    decision = "🟢 STRONG BUY"
elif score >= 4:
    decision = "🟡 HOLD / ACCUMULATE"
else:
    decision = "🔴 SELL / AVOID"

# ---------------------------
# UI OUTPUT
# ---------------------------
st.divider()

st.subheader("📊 Result")

col1, col2 = st.columns(2)

col1.metric("Investment Score", score)
col2.metric("Decision", decision)

# ---------------------------
# GAUGE CHART
# ---------------------------
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    title={'text': "Investment Strength"},
    gauge={
        'axis': {'range': [-5, 12]},
        'bar': {'color': "green"},
        'steps': [
            {'range': [-5, 0], 'color': "red"},
            {'range': [0, 4], 'color': "orange"},
            {'range': [4, 12], 'color': "lightgreen"}
        ]
    }
))

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# EXPLANATION ENGINE
# ---------------------------
st.subheader("🧠 Analysis Explanation")

explanation = []

if pe_ratio < 15:
    explanation.append("✔ Low P/E suggests undervaluation")
else:
    explanation.append("⚠ High P/E indicates expensive valuation")

if roe > 20:
    explanation.append("✔ Strong ROE indicates good profitability")
else:
    explanation.append("⚠ Weak ROE indicates lower efficiency")

if debt < 0.5:
    explanation.append("✔ Low debt is financially safe")
else:
    explanation.append("⚠ High debt increases risk")

if growth > 15:
    explanation.append("✔ High growth potential")
else:
    explanation.append("⚠ Low growth expectations")

for line in explanation:
    st.write(line)

# ---------------------------
# FINAL INSIGHT
# ---------------------------
st.divider()

if decision.startswith("🟢"):
    st.success("Strong investment opportunity detected based on fundamentals.")
elif decision.startswith("🟡"):
    st.warning("Moderate opportunity. Consider holding and monitoring.")
else:
    st.error("High risk or overvalued stock. Avoid investment.")
