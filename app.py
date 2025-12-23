import streamlit as st
from agent import StockAgent
import datetime
import os
import json

st.set_page_config(page_title="StockAgent AI", layout="wide")

# Initialize Agent once to get dynamic sectors
if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

st.title("📈 StockAgent: AI Stock Picker")
st.write(f"Logged in: **Dr. Alex V. Patel** | Today's Date: {datetime.date.today()}")

# Sidebar
st.sidebar.header("Settings")
base_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=0, value=10000)
# Pulling the dynamic sectors from the Agent
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Select Specific Sectors (Dynamic)", available_sectors)
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    if st.button("Run Investment Cycle"):
        # Update agent config before run
        agent.base_amount = base_amount
        agent.sectors_input = selected_sectors
        agent.stocks = agent.get_stocks_from_sectors(selected_sectors) if selected_sectors else agent.fetch_top_buys()
        
        with st.spinner("Analyzing market data..."):
            prices = agent.perceive()
            if not prices:
                st.error("No data found. Check your connection.")
            else:
                suggestion = agent.decide(prices)
                results = agent.act(prices, suggestion)
                st.success("Cycle Complete!")
                st.table(results)

with col2:
    st.subheader("📊 Portfolio Summary")
    if st.button("Refresh Portfolio Status"):
        if not agent.portfolio:
            st.info("No active holdings found.")
        else:
            total_invested = 0
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    try:
                        history = json.load(f)
                        # FIXED: Using .get() to prevent KeyError if 'amount' is missing
                        total_invested = sum(item.get('amount', 0) for item in history)
                    except:
                        total_invested = 0
            
            st.metric("Total Invested (Cumulative)", f"₹{total_invested:,.2f}")
            st.write("**Current Assets:**")
            st.json({k: f"{v:.4f} shares" for k, v in agent.portfolio.items()})

st.divider()
st.caption("Developed by Dr. Alex V. Patel | Sector data fetched dynamically from Nifty 50 Index")
