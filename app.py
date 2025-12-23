import streamlit as st
from agent import StockAgent, SECTOR_MAP
import datetime
import os
import json

# App Configuration
st.set_page_config(page_title="StockAgent AI", layout="wide")

st.title("📈 StockAgent: AI Stock Picker")
st.write(f"Logged in as: **Dr. Alex V. Patel** | Date: {datetime.date.today()}")

# Sidebar Inputs
st.sidebar.header("User Configurations")
base_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=0, value=10000)
selected_sectors = st.sidebar.multiselect("Select Sectors (Optional)", list(SECTOR_MAP.keys()))
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

# Initialization
config = {
    "base_amount": base_amount,
    "sectors": selected_sectors,
    "frequency": frequency.lower()
}
agent = StockAgent(config)

# Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Run Agent")
    if st.button("Execute Investment Cycle"):
        with st.spinner("Fetching market data..."):
            prices = agent.perceive()
            if not prices:
                st.error("No data found. Please check internet connection.")
            else:
                suggestion = agent.decide(prices)
                results = agent.act(prices, suggestion)
                
                st.success("Investment Cycle Complete!")
                st.table(results)

with col2:
    st.subheader("📊 Portfolio Summary")
    if st.button("Show Current Holdings"):
        if not agent.portfolio:
            st.info("Portfolio is currently empty.")
        else:
            total_invested = 0
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    history = json.load(f)
                    total_invested = sum(item['amount'] for item in history)
            
            st.metric("Total Invested", f"₹{total_invested:,.2f}")
            st.write("**Current Holdings (Shares):**")
            st.json(agent.portfolio)

# Footer
st.divider()
st.caption("Note: Files (portfolio.json) are stored temporarily on Streamlit Cloud and may reset on app reboot.")
