# =========================
# TRADE ENGINE
# ENTRY + CONFIRMATION + EXIT
# =========================

from app.engine.entry import entry_quality_score
from app.engine.exit import exit_decision
from app.services.telegram_notifier import send_telegram_alert

def determine_trade_state(pilar):
    pa = pilar.get("PRICE_ACTION", {})
    vol = pilar.get("VOLUME", {})
    mom = pilar.get("MOMENTUM", {})
    trend = pilar.get("TREND", {})

    pa_status = pa.get("status")
    pa_details = pa.get("details", {})

    break_kecil = pa_details.get("break_kecil") is True

    volume_ok = vol.get("status") in ["STRONG", "ACCUMULATION"]
    momentum_ok = mom.get("status") in ["STRONG", "READY"]
    trend_ok = trend.get("status") in ["STRONG", "TRENDING"]

    if pa_status == "FAIL":
        return "NO_TRADE"

    if pa_status in ["TRANSITION", "STRONG"]:
        if not break_kecil:
            return "SETUP"

        if break_kecil and (volume_ok or momentum_ok or trend_ok):
            return "CONFIRMED"

        return "TRIGGERED"

    return "NO_TRADE"


def is_entry_confirmed(df, signal_index):
    """
    Entry confirmation logic:
    - Close candle setelah sinyal
      harus > High candle sinyal
    """
    if signal_index + 1 >= len(df):
        return False

    signal_candle = df.iloc[signal_index]
    confirm_candle = df.iloc[signal_index + 1]

    return confirm_candle["Close"] > signal_candle["High"]


def trade_engine(symbol, df, *, risk_ratio=2):
    """
    Trade Engine Terpadu
    ENTRY → CONFIRMATION → EXIT
    """

    # =========================
    # ENTRY ENGINE
    # =========================
    entry_result = entry_quality_score(symbol, df)

    decision = entry_result["decision"]
    total_score = entry_result["total_score"]
    reason = entry_result["reason"]

    trade = {
        "symbol": symbol,
        "decision": decision,
        "reason": reason,
        "confidence_score": total_score,
        "entry": None,
        "stop_loss": None,
        "take_profit_1": None,
        "take_profit_2": None,
        "exit_action": None,
        "exit_reason": None,
        "status": "NO_TRADE",  # default
        "pilar": entry_result["pilar"],
    }

    # =========================
    # JIKA BUKAN BUY → STOP
    # =========================
    if decision != "BUY":
        trade["status"] = "NO_TRADE"
        return trade

    # =========================
    # ENTRY CONFIRMATION
    # =========================
    signal_index = len(df) - 2  # candle sinyal
    confirmed = is_entry_confirmed(df, signal_index)

    if not confirmed:
        trade["status"] = determine_trade_state(trade["pilar"])
        trade["decision"] = "WAIT"
        trade["reason"] = "Struktur terbentuk, menunggu trigger / konfirmasi"
        return trade


    # =========================
    # ENTRY PRICE (CONFIRMED)
    # =========================
    entry_price = float(df["Close"].iloc[-1])
    trade["entry"] = round(entry_price, 2)
    trade["status"] = "CONFIRMED"
    
    # =========================
    # TELEGRAM ALERT (CONFIRMED)
    # =========================
    message = f"""
    🟢 *CONFIRMED ENTRY*
    {symbol}
    
    Entry : {trade['entry']}
    SL    : {trade['stop_loss']}
    RR    : {risk_ratio}
    """
    
    send_telegram_alert(message)


    # =========================
    # EXIT ENGINE
    # =========================
    exit_result = exit_decision(
        df,
        entry_price=entry_price,
        risk_ratio=risk_ratio,
    )

    trade["exit_action"] = exit_result["action"]
    trade["exit_reason"] = exit_result["reason"]

    levels = exit_result.get("levels", {})
    trade["stop_loss"] = levels.get("stop_loss")
    trade["take_profit_1"] = levels.get("take_profit_1")
    trade["take_profit_2"] = levels.get("take_profit_2")

    return trade
