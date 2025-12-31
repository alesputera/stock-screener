# =========================
# PRICE ACTION INDICATORS
# PILAR 1
# =========================

import pandas as pd


# -------------------------
# RULE 1: STOP LOWER LOW
# -------------------------
def stop_lower_low(df, lookback=20):
    """
    Harga tidak membuat lower low baru
    """
    if len(df) < lookback + 1:
        return False

    recent_lows = df["Low"].tail(lookback)
    prev_lows = df["Low"].iloc[-lookback - 1 : -1]

    return recent_lows.min() >= prev_lows.min()


# -------------------------
# RULE 2: HIGHER LOW
# -------------------------
def higher_low(df):
    """
    Low terakhir lebih tinggi dari low sebelumnya
    """
    if len(df) < 3:
        return False

    return df["Low"].iloc[-1] > df["Low"].iloc[-2]


# -------------------------
# RULE 3: REJECTION BAWAH
# -------------------------
def rejection_bawah(df):
    """
    Ekor bawah panjang (buyer menolak harga rendah)
    """
    if len(df) < 1:
        return False

    candle = df.iloc[-1]
    body = abs(candle["Close"] - candle["Open"])
    lower_wick = min(candle["Open"], candle["Close"]) - candle["Low"]

    return lower_wick > body * 1.2


# -------------------------
# RULE 4: BASE / SIDEWAYS
# -------------------------
def base_sideways(df, days=10, tolerance=0.03):
    """
    Harga bergerak mendatar (konsolidasi)
    """
    if len(df) < days:
        return False

    recent = df["Close"].tail(days)
    high = recent.max()
    low = recent.min()

    return (high - low) / low <= tolerance


# -------------------------
# RULE 5: BREAK KECIL
# -------------------------
def break_kecil(df, days=5):
    """
    Break kecil dari area konsolidasi
    """
    if len(df) < days + 1:
        return False

    recent = df["Close"].iloc[-days - 1 : -1]
    return df["Close"].iloc[-1] > recent.max()


# =========================
# PRICE ACTION SCORE
# =========================
def price_action_score(df):
    """
    Pilar 1 - Price Action Score
    """

    # HARD FILTER
    if not stop_lower_low(df):
        return {
            "score": 0,
            "status": "FAIL",
            "details": {
                "stop_lower_low": False
            }
        }

    score = 0
    details = {
        "stop_lower_low": True
    }

    hl = bool(higher_low(df))
    details["higher_low"] = hl
    if hl:
        score += 2

    rb = bool(rejection_bawah(df))
    details["rejection_bawah"] = rb
    if rb:
        score += 1

    bs = bool(base_sideways(df))
    details["base_sideways"] = bs
    if bs:
        score += 1

    bk = bool(break_kecil(df))
    details["break_kecil"] = bk
    if bk:
        score += 1

    if score >= 4:
        status = "STRONG"
    elif score >= 2:
        status = "TRANSITION"
    else:
        status = "WEAK"

    return {
        "score": score,
        "status": status,
        "details": details
    }
