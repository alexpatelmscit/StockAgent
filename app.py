import streamlit as st
import pandas as pd
from agent import StockAgent
import os, json, datetime

st.set_page_config(page_title="StockAgent AI", layout="wide")

# --- 1. LOGIN SYSTEM ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        # Change 'admin123' to whatever password you want
        if st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("Enter Password to Access Portfolio", type="password", 
                     on_change=password_entered, key="password")
        st.info("Incognito mode detected: Please authenticate to view data.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input("Enter Password to Access Portfolio", type="password", 
                     on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

# --- 2. MAIN APP LOGIC ---
if check_password():
    # Only initialize agent if logged in
    if 'agent' not in st.session_state:
        st.session_state.agent = StockAgent({"base_amount": 10000})

    agent = st.session_state.agent

    # Header with Dynamic Name
    st.title("📈 StockAgent: AI Stock Picker")
    col_h1, col_h2 = st.columns([3,1])
    with col_h1:
        st.write(f"Logged in: **Dr. Alex V. Patel** | Today: {datetime.date.today()}")
    with col_h2:
        if st.button("Logout"):
            st.session_state["password_correct"] = False
            st.rerun()

    # Sidebar
    st.sidebar.header("Investment Settings")
    base_amount = st.sidebar.number_input("Amount (₹)", min_value=0, value=10000)
    available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
    selected_sectors = st.sidebar.multiselect("Select Sectors (Optional)", available_sectors)
    frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

    # Top 10 Reference Table
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
        st.info(f"**Target:** {'Custom' if selected_sectors else 'Top 10'} ({len(active_stocks)} stocks)")

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
        if st.button("Refresh My Holdings"):
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
                st.metric("Total Cumulative Invested", f"₹{total_invested:,.2f}")
                df_p = pd.DataFrame([{"Stock": k, "Shares": f"{v:.4f}"} for k, v in agent.portfolio.items()])
                df_p.index += 1
                st.dataframe(df_p, use_container_width=True)

    st.caption("Dr. Alex V. Patel | Multi-Sector Dynamic Agent (V4.5)")
