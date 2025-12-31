# =========================
# ENTRY QUALITY ENGINE
# =========================

from app.indicators.price_action import price_action_score
from app.indicators.volume import volume_score
from app.indicators.momentum import momentum_score
from app.indicators.trend import trend_score
from app.indicators.fundamental import fundamental_score


def entry_quality_score(symbol, df):
    """
    Final Entry Decision Engine
    Return dict lengkap untuk UI & Screener
    """

    pa = price_action_score(df)
    vol = volume_score(df)
    mom = momentum_score(df)
    tr = trend_score(df)
    fund = fundamental_score(symbol)

    total_score = (
        pa["score"]
        + vol["score"]
        + mom["score"]
        + tr["score"]
        + fund["score"]
    )

    # -------------------------
    # HARD FILTER (WAJIB)
    # -------------------------
    if pa["status"] == "FAIL":
        decision = "SKIP"
        reason = "Struktur harga belum aman"

    elif fund["status"] == "FAIL":
        decision = "SKIP"
        reason = "Fundamental bermasalah"

    # -------------------------
    # DECISION LAYER
    # -------------------------
    else:
        if total_score >= 18:
            decision = "BUY"
            reason = "Semua pilar selaras"

        elif total_score >= 14:
            decision = "WATCH"
            reason = "Potensi ada, tunggu konfirmasi"

        else:
            decision = "WAIT"
            reason = "Belum cukup kuat untuk swing"

    return {
        "symbol": symbol,
        "decision": decision,
        "total_score": total_score,
        "reason": reason,
        "pilar": {
            "price_action": pa,
            "volume": vol,
            "momentum": mom,
            "trend": tr,
            "fundamental": fund,
        },
    }
