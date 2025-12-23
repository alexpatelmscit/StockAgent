import streamlit as st
import pandas as pd
from agent import StockAgent
import os, json, datetime

st.set_page_config(page_title="StockAgent AI", layout="wide")

# Initialize Session State for User Identity
if "user_identity" not in st.session_state:
    st.session_state.user_identity = "Guest"

if 'agent' not in st.session_state:
    st.session_state.agent = StockAgent({"base_amount": 10000})

agent = st.session_state.agent

# --- SIDEBAR SETTINGS ---
st.sidebar.header("User Profile")
# Typing a name here changes the 'Guest' label to your name
user_name_input = st.sidebar.text_input("Enter your name to personalize", value="")
if user_name_input:
    st.session_state.user_identity = user_name_input

st.sidebar.divider()
st.sidebar.header("Investment Settings")
base_amount = st.sidebar.number_input("Amount (₹)", min_value=0, value=10000)

# Full 13 Sectors & Frequency restored
available_sectors = sorted(list(agent.SECTOR_MAP.keys()))
selected_sectors = st.sidebar.multiselect("Select Sectors (Optional)", available_sectors)
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

if st.sidebar.button("🗑️ Clear My Session Data"):
    st.session_state.clear()
    st.rerun()

# --- MAIN INTERFACE ---
st.title("📈 StockAgent: AI Stock Picker")
st.write(f"Active User: **{st.session_state.user_identity}** | Today: {datetime.date.today()}")

# Top 10 Table (Always visible as a reference)
st.subheader("🏆 Market Leaders (Nifty 10)")
top_10_list = [
    {"Rank": 1, "Symbol": "RELIANCE.NS", "Company": "Reliance Industries", "Sector": "Energy"},
    {"Rank": 2, "Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Sector": "Finance"},
    {"Rank": 3, "Symbol": "BHARTIARTL.NS", "Company": "Bharti Airtel", "Sector": "Telecom"},
    {"Rank": 4, "Symbol": "TCS.NS", "Company": "TCS", "Sector": "IT"},
    {"Rank": 5, "Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Sector": "Finance"},
    {"Rank": 6, "Symbol": "SBIN.NS", "Company": "SBI", "Sector": "Finance"},
    {"Rank": 7, "Symbol": "INFY.NS", "Company": "Infosys", "Sector": "IT"},
    {"Rank": 8, "Symbol": "BAJFINANCE.NS", "Company": "Bajaj Finance", "Sector": "Finance"},
    {"Rank": 9, "Symbol": "LT.NS", "Company": "Larsen & Toubro", "Sector": "Construction"},
    {"Rank": 10, "Symbol": "HINDUNILVR.NS", "Company": "HUL", "Sector": "FMCG"}
]
st.table(pd.DataFrame(top_10_list).set_index("Rank"))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Execute Strategy")
    active_stocks = agent.get_stocks_from_sectors
