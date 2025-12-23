import datetime
import yfinance as yf
import json
import os
import pandas as pd

class StockAgent:
    def __init__(self, config, portfolio_file="portfolio.json", history_file="history.json"):
        self.base_amount = config.get("base_amount", 0)
        self.sectors_input = config.get("sectors", [])
        self.frequency = config.get("frequency", "Monthly")
        self.portfolio_file = portfolio_file
        self.history_file = history_file
        
        # Comprehensive 13-sector fallback for 2025
        self.SECTOR_MAP = self.discover_sectors()
        self.portfolio = self.load_portfolio()

        # Always initialize stocks list
        self.stocks = self.get_stocks_from_sectors(self.sectors_input) if self.sectors_input else self.fetch_top_buys()

    def discover_sectors(self):
        """Fetches Nifty 50 list with a detailed 13-sector fallback."""
        try:
            url = "https://raw.githubusercontent.com/anirudha-shinde/Indian-Stock-Market-Data/main/Nifty_50_Stocks.csv"
            df = pd.read_csv(url)
            df.columns = [c.strip().lower() for c in df.columns]
            symbol_col = 'symbol' if 'symbol' in df.columns else df.columns[0]
            sector_col = 'industry' if 'industry' in df.columns else 'sector'
            dynamic_map = df.groupby(sector_col)[symbol_col].apply(list).to_dict()
            return {k.lower(): [f"{t}.NS" for t in v] for k, v in dynamic_map.items()}
        except:
            # Full 2025 Sector Fallback
            return {
                "financial services": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
                "it": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
                "oil, gas & consumable fuels": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
                "fmcg": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS"],
                "automobile & auto components": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS"],
                "healthcare": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS"],
                "construction": ["LT.NS"],
                "metals & mining": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS"],
                "consumer durables": ["TITAN.NS", "ASIANPAINT.NS"],
                "telecommunication": ["BHARTIARTL.NS"],
                "power": ["NTPC.NS", "POWERGRID.NS"],
                "cement & cement products": ["ULTRACEMCO.NS", "GRASIM.NS"],
                "services": ["ADANIPORTS.NS"]
            }

    def fetch_top_buys(self):
        """Top 10 High-Impact Nifty Stocks"""
        return ["RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "TCS.NS", "ICICIBANK.NS", 
                "SBIN.NS", "INFY.NS", "BAJFINANCE.NS", "LT.NS", "LICI.NS"]

    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, "r") as f:
                try: return json.load(f)
                except: return {}
        return {}

    def save_portfolio(self):
        with open(self.portfolio_file, "w") as f:
            json.dump(self.portfolio, f, indent=4)

    def log_transaction(self, stock, allocation, price, shares):
        entry = {"date": str(datetime.date.today()), "stock": stock, "amount": round(allocation, 2), "price": round(price, 2), "shares": round(shares, 4)}
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try: history = json.load(f)
                except: pass
        history.append(entry)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)

    def get_stocks_from_sectors(self, sectors):
        tickers = []
        for s in sectors:
            tickers.extend(self.SECTOR_MAP.get(s.lower(), []))
        return list(set(tickers))

    def perceive(self):
        prices = {}
        for ticker in self.stocks:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    prices[ticker] = hist["Close"].iloc[-1]
            except: continue
        return prices

    def act(self, prices, amount):
        report = []
        if not prices: return report
        allocation = amount / len(prices)
        for stock, price in prices.items():
            shares = allocation / price
            self.portfolio[stock] = self.portfolio.get(stock, 0) + shares
            self.log_transaction(stock, allocation, price, shares)
            report.append({"Stock": stock, "Price": round(price, 2), "Shares": round(shares, 4), "Alloc": round(allocation, 2)})
        self.save_portfolio()
        return report
