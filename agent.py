import datetime
import yfinance as yf
import json
import os
import pandas as pd

class StockAgent:
    def __init__(self, config, portfolio_file="portfolio.json", history_file="history.json"):
        self.base_amount = config.get("base_amount", 0)
        self.sectors_input = config.get("sectors", [])
        self.portfolio_file = portfolio_file
        self.history_file = history_file
        self.SECTOR_MAP = self.discover_sectors()
        self.portfolio = self.load_portfolio()

        # Default to Top 10 if no sector selected
        if not self.sectors_input:
            self.stocks = self.fetch_top_buys()
        else:
            self.stocks = self.get_stocks_from_sectors(self.sectors_input)

    def discover_sectors(self):
        try:
            url = "https://raw.githubusercontent.com/anirudha-shinde/Indian-Stock-Market-Data/main/Nifty_50_Stocks.csv"
            df = pd.read_csv(url)
            df.columns = [c.strip().lower() for c in df.columns]
            symbol_col = 'symbol' if 'symbol' in df.columns else df.columns[0]
            sector_col = 'industry' if 'industry' in df.columns else 'sector'
            dynamic_map = df.groupby(sector_col)[symbol_col].apply(list).to_dict()
            return {k.lower(): [f"{t}.NS" for t in v] for k, v in dynamic_map.items()}
        except:
            return {"banking": ["HDFCBANK.NS", "ICICIBANK.NS"], "it": ["TCS.NS", "INFY.NS"]}

    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def fetch_top_buys(self):
        return ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TCS.NS", "INFY.NS", 
                "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LICI.NS", "AXISBANK.NS"]

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
            
            # Log transaction
            entry = {"date": str(datetime.date.today()), "stock": stock, "amount": allocation, "price": price, "shares": shares}
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    try: history = json.load(f)
                    except: pass
            history.append(entry)
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=4)
                
            report.append({"Stock": stock, "Price": round(price, 2), "Shares": round(shares, 4), "Alloc": round(allocation, 2)})
        
        with open(self.portfolio_file, "w") as f:
            json.dump(self.portfolio, f, indent=4)
        return report
