import streamlit as st
import pandas as pd
from agent import StockAgent
import os, json, datetime

st.set_page_config(page_title="StockAgent Pro", layout="wide")

if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"

if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

# --- SIDEBAR ---
st.sidebar.header("User & Strategy")
name_input = st.sidebar.text_input("Name (Current: Guest)", value="")
if name_input:
    st.session_state.user_name = name_input

st.sidebar.divider()
base_amount = st.sidebar.number_input("Budget (₹)", min_value=1000, value=10000)
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Filter Sectors", available_sectors)

if st.sidebar.button("🗑️ Clear All Data"):
    for f in ["portfolio.json", "history.json"]:
        if os.path.exists(f): os.remove(f)
    st.session_state.clear()
    st.rerun()

# --- MAIN PAGE ---
st.title("📈 StockAgent AI Dashboard")
st.write(f"Logged in as: **{st.session_state.user_name}** | Date: {datetime.date.today()}")

# Reference Table
st.subheader("🏆 Market Leaders Reference (Nifty 10)")
top_10_list = [
    {"Symbol": "RELIANCE.NS", "Company": "Reliance Industries", "Sector": "Energy"},
    {"Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Sector": "Finance"},
    {"Symbol": "BHARTIARTL.NS", "Company": "Bharti Airtel", "Sector": "Telecom"},
    {"Symbol": "TCS.NS", "Company": "TCS", "Sector": "IT"},
    {"Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Sector": "Finance"},
    {"Symbol": "SBIN.NS", "Company": "SBI", "Sector": "Finance"},
    {"Symbol": "INFY.NS", "Company": "Infosys", "Sector": "IT"},
    {"Symbol": "BAJFINANCE.NS", "Company": "Bajaj Finance", "Sector": "Finance"},
    {"Symbol": "LT.NS", "Company": "Larsen & Toubro", "Sector": "Construction"},
    {"Symbol": "HINDUNILVR.NS", "Company": "HUL", "Sector": "FMCG"}
]
df_top = pd.DataFrame(top_10_list)
df_top.index += 1
st.table(df_top)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    active_stocks = agent.get_stocks_from_sectors(selected_sectors) if selected_sectors else agent.fetch_top_buys()
    st.info(f"Targeting: {'Selected Sectors' if selected_sectors else 'Top 10 Default'}")
    
    if st.button("Run Investment Cycle"):
        agent.stocks = active_stocks
        with st.spinner("Analyzing market..."):
            prices = agent.perceive()
            if prices:
                results = agent.act(prices, base_amount)
                st.success(f"{frequency} cycle completed!")
                df_res = pd.DataFrame(results)
                df_res.index += 1
                st.table(df_res)

with col2:
    st.subheader("📊 Portfolio Status")
    if st.button("Refresh Holdings"):
        if not agent.portfolio:
            st.info("Portfolio is empty.")
        else:
            total_invested = 0
            history_data = []
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    try:
                        history_data = json.load(f)
                        total_invested = sum(item.get('amount', 0) for item in history_data)
                    except: pass
            
            st.metric("Total Cumulative Invested", f"₹{total_invested:,.2f}")
            
            # --- SECTOR CHART LOGIC ---
            if history_data:
                st.write("**Sector Allocation:**")
                chart_df = pd.DataFrame(history_data)
                sector_dist = chart_df.groupby("sector")["amount"].sum().reset_index()
                # Visual Pie Chart using Streamlit's native charting
                st.bar_chart(data=sector_dist, x="sector", y="amount")
            
            # Portfolio Table
            df_p = pd.DataFrame([{"Stock": k, "Total Shares": f"{v:.4f}"} for k, v in agent.portfolio.items()])
            df_p.index += 1
            st.dataframe(df_p, use_container_width=True)

st.caption(f"StockAgent Engine V6 | Identity: {st.session_state.user_name}")
