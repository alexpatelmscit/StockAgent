import streamlit as st
from agent import StockAgent
import datetime

st.set_page_config(page_title="StockAgent - AI Picker", layout="wide")

# Sidebar for Inputs
st.sidebar.header("⚙️ Investment Configuration")

base_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=0, value=10000, step=500)
sectors_list = list(StockAgent({}).SECTOR_MAP.keys())
selected_sectors = st.sidebar.multiselect("Select Sectors (Leave empty for Top 10)", sectors_list)

frequency = st.sidebar.selectbox("Investment Frequency", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

# App Layout
st.title("📈 StockAgent: Intelligent Stock Picker")
st.write(f"Today is **{datetime.date.today()}**")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Run Investment Agent"):
        config = {
            "base_amount": base_amount,
            "sectors": selected_sectors,
            "frequency": frequency.lower()
        }
        agent = StockAgent(config)
        
        with st.spinner("Agent is perceiving market data..."):
            # We wrap the run output to capture it for Streamlit
            st.subheader("🤖 Agent Action Log")
            prices = agent.perceive()
            if not prices:
                st.error("Could not fetch prices. Check connection.")
            else:
                suggestion = agent.decide(prices)
                # Display market sentiment
                if sum(prices.values())/len(prices) > 500:
                    st.warning("📈 Market prices are high — consider increasing investment next cycle.")
                else:
                    st.info("📉 Market prices are moderate — sticking to base amount.")
                
                # Execute actions
                allocation = suggestion["amount"] / len(prices)
                results = []
                for stock, price in prices.items():
                    shares = allocation / price
                    results.append({
                        "Stock": stock,
                        "Price": f"₹{price:.2f}",
                        "Shares Bought": f"{shares:.2f}",
                        "Allocation": f"₹{allocation:.2f}"
                    })
                    agent.log_transaction(stock, allocation, price, shares)
                
                st.table(results)
                st.success(f"Investment of ₹{suggestion['amount']} complete!")

with col2:
    if st.button("📊 View Portfolio Summary"):
        agent = StockAgent({"base_amount": 0, "sectors": []})
        st.subheader("Your Portfolio Statistics")
        
        if not agent.portfolio:
            st.info("No portfolio found. Run the agent first!")
        else:
            summary_data = []
            total_val = 0
            for stock, shares in agent.portfolio.items():
                try:
                    price = agent.perceive().get(stock) or 0
                    value = shares * price
                    total_val += value
                    summary_data.append({"Stock": stock, "Shares": round(shares, 2), "Current Value": f"₹{value:.2f}"})
                except:
                    summary_data.append({"Stock": stock, "Shares": round(shares, 2), "Current Value": "Fetch Error"})
            
            st.dataframe(summary_data, use_container_width=True)
            st.metric("Total Portfolio Value", f"₹{total_val:.2f}")
