# =========================
# TRADE ENGINE
# ENTRY + CONFIRMATION + EXIT
# =========================

from app.engine.entry import entry_quality_score
from app.engine.exit import exit_decision


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
        "status": None,
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
        trade["status"] = "WAIT_CONFIRMATION"
        trade["decision"] = "WAIT"
        trade["reason"] = "Menunggu candle konfirmasi"
        return trade

    # =========================
    # ENTRY PRICE (CONFIRMED)
    # =========================
    entry_price = float(df["Close"].iloc[-1])
    trade["entry"] = round(entry_price, 2)
    trade["status"] = "CONFIRMED"

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
