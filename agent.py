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
        self.frequency = config.get("frequency", "monthly")
        self.portfolio_file = portfolio_file
        self.history_file = history_file
        
        # 1. Dynamically discover sectors
        self.SECTOR_MAP = self.discover_sectors()
        self.portfolio = self.load_portfolio()

        if not self.sectors_input:
            self.sectors, self.stocks = self.pick_daily_top_buys()
        else:
            self.stocks = self.get_stocks_from_sectors(self.sectors_input)

    def discover_sectors(self):
        """Fetches the Nifty 50 list and groups tickers by Industry."""
        try:
            # Using a reliable public mirror for Nifty 50 data
            url = "https://raw.githubusercontent.com/anirudha-shinde/Indian-Stock-Market-Data/main/Nifty_50_Stocks.csv"
            df = pd.read_csv(url)
            
            # Clean column names (handles spaces/case)
            df.columns = [c.strip().lower() for c in df.columns]
            
            # Find the right columns (Symbol and Industry/Sector)
            symbol_col = 'symbol' if 'symbol' in df.columns else df.columns[0]
            sector_col = 'industry' if 'industry' in df.columns else 'sector'
            
            # Grouping
            dynamic_map = df.groupby(sector_col)[symbol_col].apply(list).to_dict()
            
            # Add .NS suffix for Yahoo Finance
            formatted_map = {}
            for sector, tickers in dynamic_map.items():
                formatted_map[sector.lower()] = [f"{t}.NS" for t in tickers]
            
            return formatted_map
        except Exception as e:
            # Fallback static map if network fails
            return {
                "banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
                "it": ["TCS.NS", "INFY.NS", "WIPRO.NS"],
                "oil & gas": ["RELIANCE.NS", "ONGC.NS"]
            }

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
            "shares": round(shares, 4)
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
        for s in sectors:
            tickers.extend(self.SECTOR_MAP.get(s.lower(), []))
        return tickers

    def fetch_top_buys(self):
        """Top 10 High Volume Stocks for today"""
        return ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TCS.NS", "INFY.NS", 
                "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LICI.NS", "AXISBANK.NS"]

    def pick_daily_top_buys(self):
        return ["Daily Top 10"], self.fetch_top_buys()

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

    def decide(self, prices):
        return {"amount": self.base_amount, "sectors": self.sectors_input}

    def act(self, prices, suggestion):
        report = []
        if not prices: return report
        allocation = suggestion["amount"] / len(prices)
        for stock, price in prices.items():
            shares = allocation / price
            self.portfolio[stock] = self.portfolio.get(stock, 0) + shares
            self.log_transaction(stock, allocation, price, shares)
            report.append({"Stock": stock, "Price": price, "Shares": shares, "Alloc": allocation})
        self.save_portfolio()
        return report
