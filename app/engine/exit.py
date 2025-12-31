# =========================
# EXIT STRATEGY ENGINE
# WITH TRAILING STOP (MA20)
# =========================

from app.indicators.momentum import rsi, macd_histogram
import pandas as pd


# =========================
# HELPER FUNCTIONS
# =========================
def sma(series, period):
    return series.rolling(period).mean()


def last_swing_low(df, lookback=5):
    """
    Ambil swing low terakhir sebagai stop loss awal
    """
    return float(df["Low"].tail(lookback).min())


# =========================
# EXIT DECISION ENGINE
# =========================
def exit_decision(df, *, entry_price, risk_ratio=2):
    """
    Exit decision dengan:
    - Initial SL: swing low
    - TP1: Risk Reward
    - TP2: Trailing Stop MA20
    """

    # =========================
    # ENTRY VALIDATION
    # =========================
    entry_price = float(entry_price)

    if entry_price <= 0:
        return {
            "action": "ERROR",
            "reason": "Entry price tidak valid",
            "levels": {}
        }

    # =========================
    # INITIAL STOP LOSS
    # =========================
    stop_loss = last_swing_low(df)

    if stop_loss >= entry_price:
        return {
            "action": "HOLD",
            "reason": "Stop loss tidak valid (>= entry)",
            "levels": {
                "entry": round(entry_price, 2),
                "stop_loss": round(stop_loss, 2),
            },
        }

    # =========================
    # RISK & TP1
    # =========================
    risk = entry_price - stop_loss
    take_profit_1 = entry_price + (risk * risk_ratio)

    # =========================
    # TRAILING STOP (MA20)
    # =========================
    ma20 = sma(df["Close"], 20)
    last_close = df["Close"].iloc[-1]
    last_ma20 = ma20.iloc[-1]

    # =========================
    # MOMENTUM
    # =========================
    r = rsi(df["Close"])
    hist = macd_histogram(df)

    action = "HOLD"
    reason = "Trend masih sehat (di atas MA20)"

    # =========================
    # EXIT CONDITIONS
    # =========================

    # HARD STOP LOSS
    if last_close < stop_loss:
        action = "SELL"
        reason = "Stop loss awal kena"

    # TRAILING STOP MA20 (EXIT FULL)
    elif last_close < last_ma20:
        action = "SELL"
        reason = "Trailing stop kena (close < MA20)"

    # MOMENTUM MATI
    elif hist.iloc[-1] < hist.iloc[-2] and r.iloc[-1] < 50:
        action = "SELL"
        reason = "Momentum mati"

    # =========================
    # RETURN
    # =========================
    return {
        "action": action,
        "reason": reason,
        "levels": {
            "entry": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit_1": round(take_profit_1, 2),
            "trailing_stop_ma20": round(last_ma20, 2),
        },
    }
