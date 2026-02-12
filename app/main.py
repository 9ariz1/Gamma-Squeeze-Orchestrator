import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Gamma Squeeze Orchestrator", layout="wide")

st.title("📈 Gamma Squeeze Orchestrator")
st.write("Analyze gamma pressure using option volume and open interest")

# =========================
# STOCK SELECTION
# =========================
stock = st.selectbox(
    "Select Stock",
    ["TSLA", "NVDA", "AAPL", "MSFT"]
)

# =========================
# PRICE DATA
# =========================
price_data = yf.download(stock, period="1mo")
if isinstance(price_data.columns, pd.MultiIndex):
    price_data.columns = price_data.columns.get_level_values(0)

current_price = price_data['Close'].iloc[-1]

st.metric("Current Price", round(current_price, 2))

# =========================
# OPTION DATA
# =========================
ticker = yf.Ticker(stock)
expiry = ticker.options[0]
option_chain = ticker.option_chain(expiry)
calls = option_chain.calls
calls['volume'] = calls['volume'].fillna(0)

# =========================
# ATM FILTER
# =========================
atm_calls = calls[
    (calls['strike'] >= current_price - 50) &
    (calls['strike'] <= current_price + 50)
].copy()

# =========================
# GAMMA SCORE
# =========================
atm_calls['gamma_score'] = atm_calls['volume'] * (atm_calls['openInterest'] + 1)

def classify(score):
    if score > 50000:
        return "HIGH"
    elif score > 20000:
        return "MEDIUM"
    else:
        return "LOW"

atm_calls['signal'] = atm_calls['gamma_score'].apply(classify)

top_gamma = atm_calls.sort_values(
    by='gamma_score', ascending=False
).head(10)

# =========================
# TABLE VIEW
# =========================
st.subheader("🔍 Top Gamma Pressure Strikes")
st.dataframe(top_gamma[['strike', 'gamma_score', 'signal']])

# =========================
# PRICE CHART
# =========================
st.subheader("📉 Stock Price Trend")
st.line_chart(price_data['Close'])

# =========================
# GAMMA BAR CHART
# =========================
st.subheader("📊 Gamma Pressure Chart")

fig, ax = plt.subplots()
ax.bar(top_gamma['strike'].astype(str), top_gamma['gamma_score'])
ax.set_xlabel("Strike")
ax.set_ylabel("Gamma Score")
ax.set_title("Top Gamma Pressure Zones")
plt.xticks(rotation=45)

st.pyplot(fig)
