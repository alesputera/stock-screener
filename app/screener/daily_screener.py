# =========================
# DAILY STOCK SCREENER
# =========================

from app.services.data_fetcher import fetch_daily
from app.engine.trade_engine import trade_engine
from app.universe.loader import load_universe


def run_daily_screener(universe: str, risk_ratio=2, debug=False):
    results = []
    symbols = load_universe(universe)

    for symbol in symbols:
        try:
            df = fetch_daily(symbol)
            result = trade_engine(symbol, df, risk_ratio=risk_ratio)

            row = {
                "symbol": symbol,
                "status": result.get("status"),
                "decision": result.get("decision"),
                "score": result.get("confidence_score"),
                "reason": result.get("reason"),
                "pilar": result.get("pilar") or {},
            }

            if debug:
                results.append(row)
            else:
                if row["status"] in ["CONFIRMED", "WAIT_CONFIRMATION"]:
                    results.append(row)

        except Exception as e:
            results.append({
                "symbol": symbol,
                "status": "ERROR",
                "decision": "-",
                "score": 0,
                "reason": str(e),
            })

    return results


if __name__ == "__main__":
    screened = run_daily_screener(
        universe="LQ45",
        risk_ratio=2,
        debug=True
    )

    print("\n📊 HASIL SCREENING HARI INI\n")

    if not screened:
        print("Tidak ada saham yang lolos hari ini.")
    else:
        for s in screened:
            print(
                f"{s['symbol']} | {s['status']} | "
                f"Score: {s['score']} | {s['reason']}"
            )
