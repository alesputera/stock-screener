from app.services.data_fetcher import fetch_daily
from app.backtest.backtest import backtest, summarize

symbol = "ESSA.JK"
df = fetch_daily(symbol)

trades = backtest(symbol, df)
summary = summarize(trades)

print(summary)
