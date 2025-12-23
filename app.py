import streamlit as st
import pandas as pd
from agent import StockAgent
import os, json, datetime

st.set_page_config(page_title="StockAgent AI", layout="wide")

def reset_all():
    for f in ["portfolio.json", "history.json"]:
        if os.path.exists(f): os.remove(f)
    st.session_state.clear()
    st.rerun()

if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

st.title("📈 StockAgent: AI Stock Picker")
st.write(f"Logged in: **Dr. Alex V. Patel** | Today: {datetime.date.today()}")

# Sidebar
st.sidebar.header("Investment Settings")
base_amount = st.sidebar.number_input("Amount (₹)", min_value=0, value=10000)
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Select Sectors (Optional)", available_sectors)
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

if st.sidebar.button("🗑️ Clear All Data"):
    reset_all()

# --- NEW: TOP 10 LISTING TABLE ---
st.subheader("🏆 Top 10 Market Leaders (Nifty 50)")
top_10_data = [
    {"Rank": 1, "Symbol": "RELIANCE.NS", "Company": "Reliance Industries", "Sector": "Energy"},
    {"Rank": 2, "Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Sector": "Financial Services"},
    {"Rank": 3, "Symbol": "BHARTIARTL.NS", "Company": "Bharti Airtel", "Sector": "Telecom"},
    {"Rank": 4, "Symbol": "TCS.NS", "Company": "TCS", "Sector": "IT Services"},
    {"Rank": 5, "Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Sector": "Financial Services"},
    {"Rank": 6, "Symbol": "SBIN.NS", "Company": "State Bank of India", "Sector": "Financial Services"},
    {"Rank": 7, "Symbol": "INFY.NS", "Company": "Infosys", "Sector": "IT Services"},
    {"Rank": 8, "Symbol": "BAJFINANCE.NS", "Company": "Bajaj Finance", "Sector": "Financial Services"},
    {"Rank": 9, "Symbol": "LT.NS", "Company": "Larsen & Toubro", "Sector": "Construction"},
    {"Rank": 10, "Symbol": "HINDUNILVR.NS", "Company": "Hindustan Unilever", "Sector": "FMCG"}
]
st.table(pd.DataFrame(top_10_data).set_index("Rank"))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    active_stocks = agent.get_stocks_from_sectors(selected_sectors) if selected_sectors else agent.fetch_top_buys()
    target_info = "Custom Sectors" if selected_sectors else "Top 10 Default"
    st.info(f"**Target:** {target_info} ({len(active_stocks)} stocks)")

    if st.button("Run Cycle"):
        agent.stocks = active_stocks
        with st.spinner("Fetching live prices..."):
            prices = agent.perceive()
            if prices:
                results = agent.act(prices, base_amount)
                st.success(f"Success! {frequency} investment logged.")
                df = pd.DataFrame(results)
                df.index = df.index + 1
                st.table(df)

with col2:
    st.subheader("📊 Portfolio Status")
    if st.button("Update Valuation"):
        if not agent.portfolio:
            st.info("No holdings yet.")
        else:
            total_invested = 0
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    history = json.load(f)
                    total_invested = sum(item.get('amount', 0) for item in history)
            st.metric("Total Cumulative Invested", f"₹{total_invested:,.2f}")
            df_p = pd.DataFrame([{"Stock": k, "Shares": f"{v:.4f}"} for k, v in agent.portfolio.items()])
            df_p.index = df_p.index + 1
            st.dataframe(df_p, use_container_width=True)

st.caption("Dr. Alex V. Patel | Multi-Sector Dynamic Agent (V4)")
