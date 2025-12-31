# =========================
# DAILY STOCK SCREENER
# =========================

from app.services.data_fetcher import fetch_daily
from app.engine.trade_engine import trade_engine


# =========================
# SAHAM YANG DISCREENING
# =========================
UNIVERSE = [
    "BBRI.JK",
    "BBCA.JK",
    "BMRI.JK",
    "BBNI.JK",
    "BRIS.JK",

    "TLKM.JK",
    "EXCL.JK",
    "ISAT.JK",
    "GOTO.JK",
    "ARTO.JK",

    "ADRO.JK",
    "ANTM.JK",
    "MDKA.JK",
    "INCO.JK",
    "TINS.JK",
    "PTBA.JK",
    "ITMG.JK",
    "HRUM.JK",
    "BRMS.JK",
    "BUMI.JK",

    "PGAS.JK",
    "AKRA.JK",
    "RAJA.JK",
    "MEDC.JK",
    "ELSA.JK",

    "ICBP.JK",
    "INDF.JK",
    "UNVR.JK",
    "MYOR.JK",
    "KLBF.JK",

    "CTRA.JK",
    "BSDE.JK",
    "PWON.JK",
    "SMRA.JK",
    "ADHI.JK",

    "ASII.JK",
    "UNTR.JK",
    "MAPI.JK",
    "TBIG.JK",
    "TOWR.JK",

    "SCMA.JK",
    "CPIN.JK",
    "JPFA.JK",
    "SMGR.JK",
    "INKP.JK"
]


def run_daily_screener(risk_ratio=2, debug=False):
    results = []

    for symbol in UNIVERSE:
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


# =========================
# JALANKAN LANGSUNG
# =========================
if __name__ == "__main__":
    screened = run_daily_screener()

    print("\n📊 HASIL SCREENING HARI INI\n")

    if not screened:
        print("Tidak ada saham yang lolos hari ini.")
    else:
        for s in screened:
            print(
                f"{s['symbol']} | {s['status']} | "
                f"Score: {s['score']} | {s['reason']}"
            )
