import yfinance as yf

def fetch_daily(symbol, period="6mo"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)

    if df.empty:
        raise ValueError(f"Data kosong untuk {symbol}")

    return df
