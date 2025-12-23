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

    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, "r") as f:
                    return json.load(f)
            except: return {}
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
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try: history = json.load(f)
                except: history = []
        history.append(entry)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)

    def get_stocks_from_sectors(self, sectors):
        tickers = []
        for sector in sectors:
            sector = sector.lower().strip()
            if sector in SECTOR_MAP:
                tickers.extend(SECTOR_MAP[sector])
        return tickers

    def fetch_top_buys(self):
        return ["NMDC.NS", "GLENMARK.NS", "BHEL.NS", "HDFCBANK.NS", "ICICIBANK.NS",
                "TATASTEEL.NS", "JSWSTEEL.NS", "INFY.NS", "SUNPHARMA.NS", "LT.NS"]

    def pick_daily_top_buys(self):
        return ["daily_top"], self.fetch_top_buys()

    def perceive(self):
        prices = {}
        for ticker in self.stocks:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if not hist.empty:
                prices[ticker] = hist["Close"].iloc[-1]
        return prices

    def decide(self, prices):
        return {"amount": self.base_amount, "sectors": self.sectors}

    def act(self, prices, suggestion):
        # This returns a list of results for the UI to display
        report = []
        allocation = suggestion["amount"] / len(prices)
        for stock, price in prices.items():
            shares = allocation / price
            self.portfolio[stock] = self.portfolio.get(stock, 0) + shares
            self.log_transaction(stock, allocation, price, shares)
            report.append({"Stock": stock, "Price": price, "Shares": shares, "Alloc": allocation})
        self.save_portfolio()
        return report
