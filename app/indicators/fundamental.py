# =========================
# FUNDAMENTAL & NEWS
# PILAR 5
# =========================

import yfinance as yf


# -------------------------
# FUNDAMENTAL HELPERS
# -------------------------
def get_fundamental(symbol):
    """
    Ambil data fundamental dasar dari yfinance
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return info


# -------------------------
# RULE F1: VALUASI MASUK AKAL
# -------------------------
def valuasi_aman(info):
    pe = info.get("trailingPE")
    pbv = info.get("priceToBook")

    if pe is None and pbv is None:
        return False

    if pe is not None and pe < 25:
        return True

    if pbv is not None and pbv <= 3:
        return True

    return False


# -------------------------
# RULE F2: LABA TIDAK NEGATIF
# -------------------------
def laba_tidak_rugi(info):
    eps = info.get("trailingEps")
    return eps is not None and eps > 0


# -------------------------
# RULE F3: CASHFLOW / OPERASI SEHAT
# -------------------------
def cashflow_sehat(info):
    op_cash = info.get("operatingCashflow")
    return op_cash is not None and op_cash > 0


# -------------------------
# RULE F4: LEVERAGE AMAN
# -------------------------
def utang_aman(info):
    debt = info.get("totalDebt")
    equity = info.get("totalStockholderEquity")

    if debt is None or equity is None or equity <= 0:
        return False

    der = debt / equity
    return der <= 2


# -------------------------
# RULE F5: PROFITABILITY MINIMAL
# -------------------------
def profitabilitas(info):
    roe = info.get("returnOnEquity")
    return roe is not None and roe > 0.08


# =========================
# FUNDAMENTAL SCORE
# =========================
def fundamental_score(symbol):
    """
    Pilar 5 - Fundamental Score
    Return dict: {score, status, details}
    """

    info = get_fundamental(symbol)

    score = 0
    details = {}

    f1 = bool(valuasi_aman(info))
    details["valuasi_aman"] = f1
    if f1:
        score += 1

    f2 = bool(laba_tidak_rugi(info))
    details["laba_tidak_rugi"] = f2
    if f2:
        score += 1

    f3 = bool(cashflow_sehat(info))
    details["cashflow_sehat"] = f3
    if f3:
        score += 1

    f4 = bool(utang_aman(info))
    details["utang_aman"] = f4
    if f4:
        score += 1

    f5 = bool(profitabilitas(info))
    details["profitabilitas"] = f5
    if f5:
        score += 1

    if score >= 4:
        status = "STRONG"
    elif score >= 3:
        status = "SAFE"
    elif score >= 2:
        status = "RISKY"
    else:
        status = "FAIL"

    return {
        "score": score,
        "status": status,
        "details": details
    }
