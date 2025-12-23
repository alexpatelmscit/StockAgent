import datetime
import yfinance as yf
import json
import os
import pandas as pd
import requests

class StockAgent:
    def __init__(self, config, portfolio_file="portfolio.json", history_file="history.json"):
        self.base_amount = config.get("base_amount", 0)
        self.sectors_input = config.get("sectors", [])
        self.portfolio_file = portfolio_file
        self.history_file = history_file
        
        # Discover all 13 Nifty sectors
        self.SECTOR_MAP = self.discover_sectors()
        self.portfolio = self.load_portfolio()

        # Fix: Ensure stocks are set correctly for "Top 10" default
        if not self.sectors_input:
            self.stocks = self.fetch_top_buys()
        else:
            self.stocks = self.get_stocks_from_sectors(self.sectors_input)

    def discover_sectors(self):
        """Fetches Nifty 50 list or uses a full 13-sector fallback."""
        try:
            url = "https://raw.githubusercontent.com/anirudha-shinde/Indian-Stock-Market-Data/main/Nifty_50_Stocks.csv"
            df = pd.read_csv(url)
            df.columns = [c.strip().lower() for c in df.columns]
            symbol_col = 'symbol' if 'symbol' in df.columns else df.columns[0]
            sector_col = 'industry' if 'industry' in df.columns else 'sector'
            dynamic_map = df.groupby(sector_col)[symbol_col].apply(list).to_dict()
            return {k.lower(): [f"{t}.NS" for t in v] for k, v in dynamic_map.items()}
        except Exception:
            # Full Fallback with all 13 Nifty sectors
            return {
                "financial services": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS"],
                "it": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
                "oil & gas": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
                "fmcg": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
                "automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "EICHERMOT.NS"],
                "healthcare": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS"],
                "construction": ["LT.NS"],
                "metals & mining": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS"],
                "consumer durables": ["TITAN.NS", "ASIANPAINT.NS"],
                "telecommunication": ["BHARTIARTL.NS"],
                "power": ["NTPC.NS", "POWERGRID.NS"],
                "cement": ["ULTRACEMCO.NS", "GRASIM.NS"],
                "services": ["ADANIPORTS.NS"]
            }

    def fetch_top_buys(self):
        """Top 10 High Volume/Market Cap Stocks as of Dec 23, 2025"""
        return ["RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "TCS.NS", "ICICIBANK.NS", 
                "SBIN.NS", "INFY.NS", "BAJFINANCE.NS", "LT.NS", "LICI.NS"]

    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, "r") as f: return json.load(f)
            except: return {}
        return {}

    def save_portfolio(self):
        with open(self.portfolio_file, "w") as f: json.dump(self.portfolio, f, indent=4)

    def log_transaction(self, stock, allocation, price, shares):
        entry = {"date": str(datetime.date.today()), "stock": stock, "amount": round(allocation, 2), "price": round(price, 2), "shares": round(shares, 4)}
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try: history = json.load(f)
                except: pass
        history.append(entry)
        with open(self.history_file, "w") as f: json.dump(history, f, indent=4)

    def get_stocks_from_sectors(self, sectors):
        tickers = []
        for s in sectors: tickers.extend(self.SECTOR_MAP.get(s.lower(), []))
        return list(set(tickers))

    def perceive(self):
        prices = {}
        for ticker in self.stocks:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty: prices[ticker] = hist["Close"].iloc[-1]
            except: continue
        return prices

    def decide(self, prices):
        return {"amount": self.base_amount}

    def act(self, prices, suggestion):
        report = []
        if not prices: return report
        allocation = suggestion["amount"] / len(prices)
        for stock, price in prices.items():
            shares = allocation / price
            self.portfolio[stock] = self.portfolio.get(stock, 0) + shares
            self.log_transaction(stock, allocation, price, shares)
            report.append({"Stock": stock, "Price": round(price, 2), "Shares": round(shares, 4), "Alloc": round(allocation, 2)})
        self.save_portfolio()
        return report
