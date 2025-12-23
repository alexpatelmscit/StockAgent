import datetime
import yfinance as yf
import json
import os
import pandas as pd

class StockAgent:
    def __init__(self, config, portfolio_file="portfolio.json", history_file="history.json"):
        self.base_amount = config.get("base_amount", 10000)
        self.sectors_input = config.get("sectors", [])
        self.frequency = config.get("frequency", "Monthly")
        self.portfolio_file = portfolio_file
        self.history_file = history_file
        
        self.SECTOR_MAP = self.discover_sectors()
        # Inverse map to find sector by ticker
        self.TICKER_TO_SECTOR = {ticker: sector for sector, tickers in self.SECTOR_MAP.items() for ticker in tickers}
        
        self.portfolio = self.load_portfolio()
        self.stocks = self.get_stocks_from_sectors(self.sectors_input) if self.sectors_input else self.fetch_top_buys()

    def discover_sectors(self):
        return {
            "financial services": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
            "it": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
            "oil & gas": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
            "fmcg": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
            "automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS"],
            "healthcare": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS"],
            "metals & mining": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS"],
            "power": ["NTPC.NS", "POWERGRID.NS"],
            "construction": ["LT.NS"],
            "consumer durables": ["TITAN.NS", "ASIANPAINT.NS"],
            "telecommunication": ["BHARTIARTL.NS"],
            "cement": ["ULTRACEMCO.NS", "GRASIM.NS"],
            "services": ["ADANIPORTS.NS"]
        }

    def fetch_top_buys(self):
        return ["RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "TCS.NS", "ICICIBANK.NS", 
                "SBIN.NS", "INFY.NS", "BAJFINANCE.NS", "LT.NS", "HINDUNILVR.NS"]

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
        sector = self.TICKER_TO_SECTOR.get(stock, "Other")
        entry = {
            "date": str(datetime.date.today()), 
            "stock": stock, 
            "sector": sector,
            "amount": round(allocation, 2), 
            "price": round(price, 2), 
            "shares": round(shares, 4)
        }
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
                if not hist.empty: prices[ticker] = hist["Close"].iloc[-1]
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
