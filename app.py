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

# Initialize Agent
if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

st.title("📈 StockAgent: AI Stock Picker")
st.write(f"Logged in: **Dr. Alex V. Patel** | Date: {datetime.date.today()}")

# Sidebar Restored
st.sidebar.header("Strategy Settings")
base_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=0, value=10000)
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Select Sectors (Empty = Top 10)", available_sectors)

# Frequency Selector Restored
frequency = st.sidebar.selectbox("Investment Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

if st.sidebar.button("🗑️ Clear All Data"):
    reset_all()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    
    # Logic to show Top 10 Stocks as default
    active_stocks = agent.get_stocks_from_sectors(selected_sectors) if selected_sectors else agent.fetch_top_buys()
    target_label = "Custom Sectors" if selected_sectors else "Top 10 Daily Stocks (Default)"
    
    st.info(f"**Targeting:** {target_label}  \n**Stocks:** {', '.join(active_stocks[:5])}...")

    if st.button("Run Investment Cycle"):
        agent.stocks = active_stocks # Update agent with current UI choice
        with st.spinner("Analyzing market..."):
            prices = agent.perceive()
            if prices:
                results = agent.act(prices, base_amount)
                st.success(f"Successfully processed {frequency} investment!")
                
                # Table Index starting at 1
                df = pd.DataFrame(results)
                df.index = df.index + 1
                st.table(df)
            else:
                st.error("Could not fetch market prices. Please try again.")

with col2:
    st.subheader("📊 Portfolio Summary")
    if st.button("Refresh My Portfolio"):
        if not agent.portfolio:
            st.info("No active holdings.")
        else:
            total_invested = 0
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    try:
                        history = json.load(f)
                        total_invested = sum(item.get('amount', 0) for item in history)
                    except: pass
            
            st.metric("Total Cumulative Investment", f"₹{total_invested:,.2f}")
            
            # Formatted portfolio table with Index starting at 1
            port_data = [{"Stock": k, "Total Shares": f"{v:.4f}"} for k, v in agent.portfolio.items()]
            df_p = pd.DataFrame(port_data)
            df_p.index = df_p.index + 1
            st.dataframe(df_p, use_container_width=True)

st.divider()
st.caption("Developed by Dr. Alex V. Patel | Sector data & Top 10 stocks updated for Dec 2025")
