import streamlit as st
import pandas as pd
from agent import StockAgent
import datetime
import os
import json

st.set_page_config(page_title="StockAgent AI", layout="wide")

# Helper to Reset Data
def clear_app_data():
    files_to_delete = ["portfolio.json", "history.json"]
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)
    st.session_state.clear()
    st.rerun()

# Initialize Agent
if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

st.title("📈 StockAgent: AI Stock Picker")
st.write(f"Logged in: **Dr. Alex V. Patel** | Today's Date: {datetime.date.today()}")

# Sidebar
st.sidebar.header("Settings")
base_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=0, value=10000)
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Select Specific Sectors (Dynamic)", available_sectors)
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

st.sidebar.divider()
if st.sidebar.button("🗑️ Clear All Data & History"):
    clear_app_data()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    # Show what stocks are being targeted
    current_targets = selected_sectors if selected_sectors else ["Top 10 Daily Stocks (Default)"]
    st.info(f"Targeting: {', '.join(current_targets)}")
    
    if st.button("Run Investment Cycle"):
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
                
                # Format table to start index at 1
                df_results = pd.DataFrame(results)
                df_results.index = df_results.index + 1
                st.table(df_results)

with col2:
    st.subheader("📊 Portfolio Status")
    if st.button("Refresh Valuation"):
        if not agent.portfolio:
            st.info("No active holdings found.")
        else:
            with st.spinner("Fetching live prices..."):
                current_prices = agent.perceive()
                total_invested = 0
                current_value = 0
                portfolio_details = []

                if os.path.exists("history.json"):
                    with open("history.json", "r") as f:
                        try:
                            history = json.load(f)
                            total_invested = sum(item.get('amount', 0) for item in history)
                        except: total_invested = 0

                for stock, shares in agent.portfolio.items():
                    # Attempt to get fresh price for valuation
                    price = current_prices.get(stock)
                    if not price: # Fetch individual if not in current batch
                        price = yf.Ticker(stock).history(period="1d")["Close"].iloc[-1]
                    
                    val = shares * price
                    current_value += val
                    portfolio_details.append({
                        "Stock": stock,
                        "Shares": round(shares, 4),
                        "Last Price": f"₹{price:.2f}",
                        "Current Value": f"₹{val:.2f}"
                    })

                # Accurate Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Invested", f"₹{total_invested:,.2f}")
                m2.metric("Current Value", f"₹{current_value:,.2f}")
                
                pnl = current_value - total_invested
                pnl_pct = (pnl / total_invested * 100) if total_invested > 0 else 0
                m3.metric("Net P&L", f"₹{pnl:,.2f}", delta=f"{pnl_pct:.2f}%")

                # Simplified Portfolio Table
                df_port = pd.DataFrame(portfolio_details)
                df_port.index = df_port.index + 1
                st.dataframe(df_port, use_container_width=True)

st.divider()
st.caption("Developed by Dr. Alex V. Patel | Sector data fetched dynamically from Nifty 50 Index")
