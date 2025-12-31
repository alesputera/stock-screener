# =========================
# VOLUME RULES (PILAR 2)
# =========================

def volume_naik_saat_stagnan(df):
    if len(df) < 20:
        return False

    avg5 = df['Volume'].tail(5).mean()
    avg20 = df['Volume'].tail(20).mean()

    return avg5 > avg20


def volume_hijau_besar(df):
    if len(df) < 20:
        return False

    last = df.iloc[-1]
    avg20 = df['Volume'].tail(20).mean()

    return last['Close'] > last['Open'] and last['Volume'] > avg20


def volume_kecil_saat_merah(df):
    if len(df) < 20:
        return False

    last = df.iloc[-1]
    avg20 = df['Volume'].tail(20).mean()

    return last['Close'] < last['Open'] and last['Volume'] < avg20


def tren_volume_naik(df):
    if len(df) < 30:
        return False

    avg10 = df['Volume'].tail(10).mean()
    avg30 = df['Volume'].tail(30).mean()

    return avg10 > avg30


# =========================
# VOLUME SCORE
# =========================

def volume_score(df):
    """
    Pilar 2 - Volume Score
    Return dict: {score, status, details}
    """

    score = 0
    details = {}

    v1 = bool(volume_naik_saat_stagnan(df))
    details["volume_naik_saat_stagnan"] = v1
    if v1:
        score += 2

    v2 = bool(volume_hijau_besar(df))
    details["volume_hijau_besar"] = v2
    if v2:
        score += 1

    v3 = bool(volume_kecil_saat_merah(df))
    details["volume_kecil_saat_merah"] = v3
    if v3:
        score += 1

    v4 = bool(tren_volume_naik(df))
    details["tren_volume_naik"] = v4
    if v4:
        score += 1

    if score >= 4:
        status = "STRONG"
    elif score >= 3:
        status = "ACCUMULATION"
    elif score >= 2:
        status = "WEAK"
    else:
        status = "FAIL"

    return {
        "score": score,
        "status": status,
        "details": details
    }
