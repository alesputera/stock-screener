# =========================
# TREND & MOVING AVERAGE
# PILAR 4
# =========================

import pandas as pd


# -------------------------
# MOVING AVERAGE HELPERS
# -------------------------
def sma(series, period):
    return series.rolling(period).mean()


# -------------------------
# RULE T1: HARGA RECLAIM MA20
# -------------------------
def reclaim_ma20(df):
    if len(df) < 21:
        return False

    ma20 = sma(df["Close"], 20)
    return df["Close"].iloc[-1] > ma20.iloc[-1]


# -------------------------
# RULE T2: MA20 SLOPE NAIK
# -------------------------
def ma20_naik(df):
    if len(df) < 22:
        return False

    ma20 = sma(df["Close"], 20)
    return ma20.iloc[-1] > ma20.iloc[-2]


# -------------------------
# RULE T3: HARGA BERTAHAN DI ATAS MA20
# -------------------------
def hold_above_ma20(df, days=3):
    if len(df) < 20 + days:
        return False

    ma20 = sma(df["Close"], 20)
    recent_close = df["Close"].tail(days)
    recent_ma = ma20.tail(days)

    return all(recent_close > recent_ma)


# -------------------------
# RULE T4: MA20 > MA50 (EARLY TREND)
# -------------------------
def ma20_above_ma50(df):
    if len(df) < 51:
        return False

    ma20 = sma(df["Close"], 20)
    ma50 = sma(df["Close"], 50)

    return ma20.iloc[-1] > ma50.iloc[-1]


# -------------------------
# RULE T5: JARAK SEHAT DARI MA200
# -------------------------
def near_ma200(df, threshold=-0.10):
    """
    threshold = -0.10 artinya harga tidak boleh >10% di bawah MA200
    """
    if len(df) < 201:
        return False

    ma200 = sma(df["Close"], 200)
    close = df["Close"].iloc[-1]

    distance = (close - ma200.iloc[-1]) / ma200.iloc[-1]
    return distance >= threshold


# =========================
# TREND SCORE
# =========================
def trend_score(df):
    """
    Pilar 4 - Trend & MA
    Return dict: {score, status, details}
    """

    score = 0
    details = {}

    t1 = bool(reclaim_ma20(df))
    details["reclaim_ma20"] = t1
    if t1:
        score += 2

    t2 = bool(ma20_naik(df))
    details["ma20_naik"] = t2
    if t2:
        score += 1

    t3 = bool(hold_above_ma20(df))
    details["hold_above_ma20"] = t3
    if t3:
        score += 1

    t4 = bool(ma20_above_ma50(df))
    details["ma20_above_ma50"] = t4
    if t4:
        score += 1

    t5 = bool(near_ma200(df))
    details["near_ma200"] = t5
    if t5:
        score += 1

    if score >= 4:
        status = "STRONG"
    elif score >= 3:
        status = "TRENDING"
    elif score >= 2:
        status = "EARLY"
    else:
        status = "FAIL"

    return {
        "score": score,
        "status": status,
        "details": details
    }
