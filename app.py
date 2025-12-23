import streamlit as st
import pandas as pd
from agent import StockAgent
import os, json, datetime

st.set_page_config(page_title="StockAgent AI", layout="wide")

def reset_data():
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
st.sidebar.header("Control Panel")
base_amount = st.sidebar.number_input("Amount (₹)", min_value=0, value=10000)
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Sectors (Empty = Top 10)", available_sectors)

if st.sidebar.button("🗑️ Clear All Data"):
    reset_data()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    # Display logic for current target
    target_msg = "Top 10 Daily Stocks" if not selected_sectors else ", ".join(selected_sectors)
    st.info(f"Targeting: {target_msg}")

    if st.button("Run Investment Cycle"):
        agent.base_amount = base_amount
        agent.sectors_input = selected_sectors
        agent.stocks = agent.get_stocks_from_sectors(selected_sectors) if selected_sectors else agent.fetch_top_buys()
        
        with st.spinner("Processing..."):
            prices = agent.perceive()
            if prices:
                results = agent.act(prices, {"amount": base_amount})
                st.success("Cycle Complete!")
                # Fix: Table index starts at 1
                df = pd.DataFrame(results)
                df.index = df.index + 1
                st.table(df)

with col2:
    st.subheader("📊 Portfolio Status")
    if st.button("Check Valuation"):
        if not agent.portfolio:
            st.info("Portfolio is empty.")
        else:
            total_invested = 0
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    history = json.load(f)
                    total_invested = sum(item.get('amount', 0) for item in history)
            
            # Simple, accurate summary
            st.metric("Total Invested", f"₹{total_invested:,.2f}")
            st.write("**Current Holdings:**")
            df_p = pd.DataFrame([{"Stock": k, "Shares": f"{v:.4f}"} for k, v in agent.portfolio.items()])
            df_p.index = df_p.index + 1
            st.dataframe(df_p, use_container_width=True)

st.divider()
st.caption("Dr. Alex V. Patel | Multi-Sector Dynamic Agent")
