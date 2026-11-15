import yfinance as yf


class MarketDataProvider:
    
    def fetch_history(self, symbol, period="5d"):
        ticker = yf.Ticker(symbol)
        frame = ticker.history(period=period, interval="1d", auto_adjust=False)

        if frame.empty:
            return []

        results = []
        for index, row in frame.iterrows():
            close = row.get("Close")
            if close is None:
                continue
            results.append((index.date().isoformat(), float(close)))

        return results
