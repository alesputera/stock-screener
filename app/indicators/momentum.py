# =========================
# MOMENTUM INDICATORS (PILAR 3)
# =========================

import pandas as pd


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# -------------------------
# RULE M1: RSI KELUAR OVERSOLD
# -------------------------
def rsi_keluar_oversold(df):
    if len(df) < 20:
        return False

    r = rsi(df["Close"])
    return r.iloc[-2] < 30 and r.iloc[-1] > r.iloc[-2]


# -------------------------
# RULE M2: RSI BULLISH DIVERGENCE
# -------------------------
def rsi_bullish_divergence(df):
    if len(df) < 30:
        return False

    r = rsi(df["Close"])

    price_low_recent = df["Low"].iloc[-5]
    price_low_prev = df["Low"].iloc[-15]

    rsi_low_recent = r.iloc[-5]
    rsi_low_prev = r.iloc[-15]

    return price_low_recent < price_low_prev and rsi_low_recent > rsi_low_prev


# -------------------------
# RULE M3: RSI RECLAIM 40
# -------------------------
def rsi_reclaim_40(df):
    if len(df) < 20:
        return False

    r = rsi(df["Close"])
    return r.iloc[-2] < 40 and r.iloc[-1] >= 40


# -------------------------
# MACD & RULE M4
# -------------------------
def macd_histogram(df, fast=12, slow=26, signal=9):
    exp1 = df["Close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["Close"].ewm(span=slow, adjust=False).mean()

    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line

    return hist


def macd_histogram_membaik(df):
    if len(df) < 30:
        return False

    hist = macd_histogram(df)
    return hist.iloc[-1] > hist.iloc[-2]


# =========================
# MOMENTUM SCORE
# =========================
def momentum_score(df):
    score = 0
    details = {}

    m1 = bool(rsi_keluar_oversold(df))
    details["rsi_keluar_oversold"] = m1
    if m1:
        score += 2

    m2 = bool(rsi_bullish_divergence(df))
    details["rsi_bullish_divergence"] = m2
    if m2:
        score += 2

    m3 = bool(rsi_reclaim_40(df))
    details["rsi_reclaim_40"] = m3
    if m3:
        score += 1

    m4 = bool(macd_histogram_membaik(df))
    details["macd_histogram_membaik"] = m4
    if m4:
        score += 1

    if score >= 4:
        status = "STRONG"
    elif score >= 3:
        status = "READY"
    elif score >= 2:
        status = "WEAK"
    else:
        status = "FAIL"

    return {
        "score": score,
        "status": status,
        "details": details
    }
