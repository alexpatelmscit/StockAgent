import datetime
import yfinance as yf
import json
import os

SECTOR_MAP = {
    "banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS"],
    "metals": ["TATASTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JSWSTEEL.NS"],
    "automobiles": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "EICHERMOT.NS"],
    "technology": ["INFY.NS", "TCS.NS", "WIPRO.NS", "HCLTECH.NS"],
    "pharma": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"],
    "industrials": ["LT.NS", "BEL.NS", "ABB.NS", "SIEMENS.NS"],
    "consumer discretionary": ["DMART.NS", "TRENT.NS", "PAGEIND.NS", "JUBLFOOD.NS"]
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
            json.dump(self.portfolio, f, indent=4)

    def log_transaction(self, stock, allocation, price, shares):
        entry = {
            "date": str(datetime.date.today()),
            "stock": stock,
            "amount": round(allocation, 2),
            "price": round(price, 2),
            "shares": round(shares, 2)
        }
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                history = json.load(f)
        else:
            history = []
        history.append(entry)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)

    # --- Sector Mapping ---
    def get_stocks_from_sectors(self, sectors):
        tickers = []
        for sector in sectors:
            sector = sector.lower().strip()
            if sector in SECTOR_MAP:
                tickers.extend(SECTOR_MAP[sector])
        return tickers

    # --- Dynamic Top Buys ---
    def fetch_top_buys(self):
        """
        Placeholder for dynamic fetch.
        Replace with API/web scraping for live top 10 recommendations.
        """
        return ["NMDC.NS", "GLENMARK.NS", "BHEL.NS", "HDFCBANK.NS", "ICICIBANK.NS",
                "TATASTEEL.NS", "JSWSTEEL.NS", "INFY.NS", "SUNPHARMA.NS", "LT.NS"]

    def pick_daily_top_buys(self):
        print("📊 No sector chosen — fetching today's Top 10 Buys dynamically...")
        top_buys = self.fetch_top_buys()
        return ["daily_top"], top_buys

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
        suggestion = {
            "amount": self.base_amount,
            "sectors": self.sectors
        }
        if avg_price > 500:
            print("📈 Market prices are high — consider increasing your investment next cycle.")
        else:
            print("📉 Market prices are moderate — sticking to your base amount.")
        return suggestion

    def act(self, prices, suggestion):
        allocation = suggestion["amount"] / len(prices)
        for stock, price in prices.items():
            shares = allocation / price
            self.portfolio[stock] = self.portfolio.get(stock, 0) + shares
            print(f"💸 Invested ₹{allocation:.2f} in {stock} at ₹{price:.2f}, total shares: {self.portfolio[stock]:.2f}")
            self.log_transaction(stock, allocation, price, shares)
        print(f"✅ {self.frequency.capitalize()} investment complete: ₹{suggestion['amount']} across {', '.join(suggestion['sectors'])} sectors")
        self.save_portfolio()

    def run(self):
        print(f"\n🤖 [StockAgent] Running at {datetime.date.today()}")
        prices = self.perceive()
        if not prices:
            print("⚠️ No price data fetched. Check tickers or internet connection.")
            return
        suggestion = self.decide(prices)
        self.act(prices, suggestion)

    def summary(self):
        print("\n📊 Portfolio Summary")
        total_value = 0
        top_stock = None
        top_shares = 0

        for stock, shares in self.portfolio.items():
            try:
                price = yf.Ticker(stock).history(period="1d")["Close"].iloc[-1]
                value = shares * price
                total_value += value
                print(f"{stock}: {shares:.2f} shares, approx value ₹{value:.2f}")
                if shares > top_shares:
                    top_shares = shares
                    top_stock = stock
            except Exception:
                print(f"{stock}: {shares:.2f} shares (price fetch failed)")

        print(f"\n💰 Total Portfolio Value: ₹{total_value:.2f}")
        if top_stock:
            print(f"🏆 Largest Holding: {top_stock} with {top_shares:.2f} shares")

        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                history = json.load(f)
            print(f"\n🕒 Total Runs Logged: {len(history)}")
            invested = sum(entry["amount"] for entry in history)
            print(f"📈 Total Invested Amount: ₹{invested:.2f}")
        else:
            print("\nℹ️ No history found yet.")
