import streamlit as st
import pandas as pd
from agent import StockAgent
import os

st.set_page_config(page_title="StockAgent Pro", layout="wide")

# Helper to clear files
def clear_data():
    for f in ["portfolio.json", "history.json"]:
        if os.path.exists(f): os.remove(f)
    st.session_state.clear()
    st.rerun()

# Initialize Agent
if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

st.title("📈 StockAgent: Intelligent Portfolio Manager")

# Sidebar
st.sidebar.header("Control Panel")
base_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=0, value=10000)
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Sectors (Defaults to Top 10 if empty)", available_sectors)

if st.sidebar.button("🗑️ Clear All Data & History"):
    clear_data()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🚀 Investment Cycle")
    if st.button("Run Investment Cycle"):
        agent.sectors_input = selected_sectors
        agent.stocks = agent.get_stocks_from_sectors(selected_sectors) if selected_sectors else agent.fetch_top_buys()
        
        with st.spinner("Executing trades..."):
            prices = agent.perceive()
            if prices:
                results = agent.act(prices, base_amount)
                st.success("Cycle Complete!")
                # Convert to DataFrame and hide index
                df_res = pd.DataFrame(results)
                st.table(df_res.assign(index='').set_index('index'))
            else:
                st.error("Market data unavailable.")

with col2:
    st.subheader("📊 Live Portfolio Status")
    if st.button("Refresh Valuation"):
        if not agent.portfolio:
            st.info("Portfolio is empty.")
        else:
            with st.spinner("Calculating current value..."):
                current_prices = agent.perceive()
                portfolio_data = []
                total_invested = 0
                current_value = 0
                
                # Calculate Invested Amount from history
                if os.path.exists("history.json"):
                    import json
                    with open("history.json", "r") as f:
                        hist = json.load(f)
                        total_invested = sum(item.get('amount', 0) for item in hist)

                for stock, shares in agent.portfolio.items():
                    price = current_prices.get(stock, 0)
                    value = shares * price
                    current_value += value
                    portfolio_data.append({
                        "Stock": stock,
                        "Holdings": f"{shares:.4f}",
                        "Live Price": f"₹{price:.2f}",
                        "Current Value": f"₹{value:.2f}"
                    })

                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Invested", f"₹{total_invested:,.2f}")
                m2.metric("Current Value", f"₹{current_value:,.2f}")
                pnl = current_value - total_invested
                m3.metric("Net P&L", f"₹{pnl:,.2f}", delta=f"{(pnl/total_invested)*100:.2f}%" if total_invested > 0 else "0%")

                df_port = pd.DataFrame(portfolio_data)
                st.dataframe(df_port.assign(index='').set_index('index'), use_container_width=True)

st.divider()
st.caption("Dr. Alex V. Patel | v2.1 Update: No-index tables & Auto-Top 10 Default")
