# =========================
# SIMPLE BACKTEST ENGINE
# =========================

from app.engine.trade_engine import trade_engine


def backtest(symbol, df, *, risk_ratio=2):
    """
    Backtest sederhana berbasis trade_engine
    """

    trades = []
    in_position = False
    current_trade = None

    for i in range(50, len(df)):
        window_df = df.iloc[: i + 1]

        # =========================
        # ENTRY CHECK
        # =========================
        if not in_position:
            result = trade_engine(symbol, window_df, risk_ratio=risk_ratio)

            if result["status"] == "CONFIRMED":
                in_position = True
                entry_price = result["entry"]
                stop_loss = result["stop_loss"]

                current_trade = {
                    "entry_index": i,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "exit_price": None,
                    "exit_index": None,
                    "reason": None,
                }

        # =========================
        # EXIT CHECK
        # =========================
        else:
            exit_result = trade_engine(symbol, window_df, risk_ratio=risk_ratio)

            if exit_result["exit_action"] == "SELL":
                exit_price = window_df["Close"].iloc[-1]

                current_trade["exit_price"] = exit_price
                current_trade["exit_index"] = i
                current_trade["reason"] = exit_result["exit_reason"]

                trades.append(current_trade)

                in_position = False
                current_trade = None

    return trades


def summarize(trades):
    """
    Ringkasan hasil backtest
    """
    if not trades:
        return {}

    wins = 0
    losses = 0
    total_rr = 0

    for t in trades:
        entry = t["entry_price"]
        exit_price = t["exit_price"]
        stop = t["stop_loss"]

        risk = entry - stop
        reward = exit_price - entry

        rr = reward / risk if risk > 0 else 0
        total_rr += rr

        if reward > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    return {
        "total_trades": total,
        "winrate": round(wins / total * 100, 2),
        "avg_rr": round(total_rr / total, 2),
        "wins": wins,
        "losses": losses,
    }
