import streamlit as st
import datetime
import yfinance as yf
import json
import os

# --- Sector Map (example, extend as needed) ---
SECTOR_MAP = {
    "pharma": ["SUNPHARMA.NS", "DRREDDY.NS"],
    "metals": ["TATASTEEL.NS", "HINDALCO.NS"],
    "it": ["INFY.NS", "TCS.NS"],
    "banking": ["HDFCBANK.NS", "ICICIBANK.NS"]
}

class StockAgent:
    def __init__(self, config, portfolio_file="portfolio.json", history_file="history.json"):
        self.base_amount = config.get("base_amount", 0)
        self.sectors = config.get("sectors", [])
        self.frequency = config.get("frequency", "monthly")
        self.portfolio_file = portfolio_file
        self.history_file = history_file
        self.portfolio = self.load_portfolio()

        if not self.sectors:
            self.sectors, self.stocks = self.pick_daily_top_buys()
        else:
            self.stocks = self.get_stocks_from_sectors(self.sectors)

    # --- Persistence ---
    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, "r") as f:
                return json.load(f)
        return {}

    def save_portfolio(self):
        with open(self.portfolio_file, "w") as f:
            json.dump(self.portfolio, f, indent=2)

    def log_transaction(self, stock, allocation, price, shares):
        record = {
            "date": str(datetime.date.today()),
            "stock": stock,
            "allocation": allocation,
            "price": price,
            "shares": shares
        }
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                history = json.load(f)
        history.append(record)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

    # --- Sector Mapping ---
    def get_stocks_from_sectors(self, sectors):
        tickers = []
        for sector in sectors:
            sector = sector.lower().strip()
            if sector in SECTOR_MAP:
                tickers.extend(SECTOR_MAP[sector])
            else:
                st.warning(f"Sector '{sector}' not found in SECTOR_MAP.")
        return tickers

    # --- Dynamic Top Buys (placeholder logic) ---
    def fetch_top_buys(self):
        # Example: return IT sector by default
        return ["INFY.NS", "TCS.NS"]

    def pick_daily_top_buys(self):
        stocks = self.fetch_top_buys()
        return ["it"], stocks

    # --- Agent Cycle ---
    def perceive(self):
        prices = {}
        for ticker in self.stocks:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if not hist.empty:
                prices[ticker] = hist["Close"].iloc[-1]
        return prices

    def decide(self, prices):
        avg_price = sum(prices.values()) / len(prices)
        suggestion = {"amount": self.base_amount, "sectors": self.sectors}
        if avg_price > 500:
            st.info("📈 Market prices are high — consider increasing your investment next cycle.")
        else:
            st.info("📉 Market prices are moderate — sticking to your base amount.")
        return suggestion

    def act(self, prices, suggestion):
        allocation = suggestion["amount"] / len(prices)
        for stock, price in prices.items():
            shares = allocation / price
            self.portfolio[stock] = self.portfolio.get(stock, 0) + shares
            st.write(f"💸 Invested ₹{allocation:.2f} in {stock} at ₹{price:.2f}, total shares: {self.portfolio[stock]:.2f}")
            self.log_transaction(stock, allocation, price, shares)
        st.success(f"{self.frequency.capitalize()} investment complete: ₹{suggestion['amount']} across {', '.join(suggestion['sectors'])} sectors")
        self.save_portfolio()

    def run(self):
        st.write(f"\n🤖 [StockAgent] Running at {datetime.date.today()}")
        prices = self.perceive()
        if not prices:
            st.error("⚠️ No price data fetched. Check tickers or internet connection.")
            return
        suggestion = self.decide(prices)
        self.act(prices, suggestion)

    def summary(self):
        st.subheader("📊 Portfolio Summary")
        if not self.portfolio:
            st.write("Portfolio is empty.")
        else:
            for stock, shares in self.portfolio.items():
                st.write(f"{stock}: {shares:.2f} shares")

# --- Streamlit UI ---
st.title("🤖 StockAgent Web App")

base_amount = st.number_input("Enter investment amount (₹)", value=10000)
sectors = st.text_input("Enter sectors separated by commas (e.g., metals, pharma)")
frequency = st.selectbox("Choose investment frequency", ["monthly", "quarterly", "half_yearly", "yearly"])

config = {
    "base_amount": base_amount,
    "sectors": [s.strip() for s in sectors.split(",")] if sectors else [],
    "frequency": frequency
}

if st.button("Run Agent"):
    agent = StockAgent(config)
    agent.run()

if st.button("Show Summary"):
    agent = StockAgent({"base_amount": 0, "sectors": []})
    agent.summary()
