import streamlit as st
import pandas as pd
from auth import login

if not login():
    st.stop()

from app.screener.daily_screener import run_daily_screener


# =====================================================
# RULE EXPLANATION (WAJIB LENGKAP DI SINI)
# =====================================================
RULE_EXPLANATION = {

    # ======================
    # PRICE ACTION
    # ======================
    "stop_lower_low": "Harga tidak membentuk lower low baru → tekanan jual melemah",
    "higher_low": "Low terakhir lebih tinggi dari sebelumnya → struktur bullish",
    "rejection_bawah": "Ekor bawah panjang → buyer menahan penurunan",
    "base_sideways": "Harga bergerak sideways → fase akumulasi",
    "break_kecil": "Breakout kecil dari konsolidasi → awal pergerakan",

    # ======================
    # TREND
    # ======================
    "reclaim_ma20": "Harga kembali menembus MA20 → trend jangka pendek membaik",
    "ma20_naik": "MA20 mengarah ke atas → trend naik aktif",
    "hold_above_ma20": "Harga bertahan di atas MA20 → buyer masih dominan",
    "ma20_above_ma50": "MA20 di atas MA50 → struktur uptrend terkonfirmasi",
    "near_ma200": "Harga dekat MA200 → area krusial (reversal / rejection)",

    # ======================
    # MOMENTUM
    # ======================
    "rsi_keluar_oversold": "RSI naik dari area oversold (<30) → indikasi reversal",
    "rsi_bullish_divergence": "Harga lower low namun RSI higher low → momentum jual melemah",
    "rsi_reclaim_40": "RSI kembali di atas 40 → momentum bullish mulai terbentuk",
    "macd_histogram_membaik": "Histogram MACD membaik → tekanan bearish melemah",

    # ======================
    # VOLUME
    # ======================
    "volume_naik_saat_stagnan": "Volume meningkat saat harga sideways → indikasi akumulasi",
    "volume_hijau_besar": "Candle hijau dengan volume besar → buyer agresif",
    "volume_kecil_saat_merah": "Volume kecil saat candle merah → tidak ada distribusi",
    "tren_volume_naik": "Rata-rata volume meningkat → minat pasar naik",

    # ======================
    # FUNDAMENTAL
    # ======================
    "valuasi_aman": "Valuasi relatif wajar dibanding historis / sektornya",
    "laba_tidak_rugi": "Perusahaan mencatat laba bersih (tidak rugi)",
    "cashflow_sehat": "Arus kas operasional positif & stabil",
    "utang_aman": "Rasio utang masih dalam batas aman",
    "profitabilitas": "ROE / ROA menunjukkan bisnis yang efisien",
}


# =====================================================
# PIPELINE UI
# =====================================================
def render_pipeline(item):
    status = item.get("status")
    pilar = item.get("pilar", {})

    st.markdown("### 📍 Trading Pipeline")

    if status == "NO_TRADE":
        st.write("❌ Filter Awal — Gagal")
        return
    else:
        st.write("✅ Filter Awal — Lolos")

    for i in range(1, 6):
        key = f"pilar_{i}"
        label = f"Pilar {i}"

        if key not in pilar:
            st.write(f"⏸ {label} — Belum dihitung")
            continue

        p_status = pilar[key].get("status")

        if p_status in ["FAIL", "WEAK"]:
            st.write(f"❌ {label} — {p_status}")
            break
        else:
            st.write(f"✅ {label} — {p_status}")

def render_confirmation_abc(item):
    """
    Menampilkan Konfirmasi Entry A / B / C
    """

    pilar = item.get("pilar", {})

    # 🔥 FIX: key sesuai data asli
    pa = pilar.get("PRICE_ACTION", {})
    vol = pilar.get("VOLUME", {})
    mom = pilar.get("MOMENTUM", {})
    trend = pilar.get("TREND", {})

    pa_details = pa.get("details", {})
    vol_status = vol.get("status")
    mom_status = mom.get("status")
    trend_status = trend.get("status")

    # =========================
    # A — STRUKTUR ENTRY
    # =========================
    a_ok = pa.get("status") in ["STRONG", "TRANSITION"]

    # =========================
    # B — TRIGGER HARGA
    # =========================
    b_ok = pa_details.get("break_kecil") is True

    # =========================
    # C — VALIDATOR TAMBAHAN
    # =========================
    c_ok = (
        vol_status in ["STRONG", "ACCUMULATION"] or
        mom_status in ["STRONG", "READY"] or
        trend_status in ["STRONG", "TRENDING"]
    )

    st.markdown("### 🧭 Konfirmasi Entry")

    # --- A ---
    if a_ok:
        st.success("🟢 A — Struktur Entry: VALID")
    else:
        st.error("🔴 A — Struktur Entry: BELUM VALID")

    # --- B ---
    if b_ok:
        st.success("🟢 B — Trigger Harga (Break Kecil): VALID")
    else:
        st.warning("🟡 B — Trigger Harga (Break Kecil): MENUNGGU")
        st.caption("⏳ Menunggu: close > high 5 hari terakhir")

    # --- C ---
    if c_ok:
        st.info("🟢 C — Validator Tambahan: MENDUKUNG")
    else:
        st.info("🟡 C — Validator Tambahan: OPSIONAL")

    # =========================
    # STATUS FINAL
    # =========================
    state = item.get("status")

    if state == "CONFIRMED":
        st.success("🟢 STATUS: CONFIRMED — SIAP ENTRY")
    elif state == "TRIGGERED":
        st.warning("🟠 STATUS: TRIGGERED — Tunggu Validasi")
    elif state == "SETUP":
        st.info("🟡 STATUS: SETUP — Struktur Kuat, Belum Break")
    else:
        st.error("🔴 STATUS: NO TRADE")



# =====================================================
# TRADE PLAN UI
# =====================================================
def render_trade_plan(item):
    entry = item.get("entry")
    sl = item.get("stop_loss")
    tp1 = item.get("take_profit_1")
    tp2 = item.get("take_profit_2")

    st.markdown("### 🎯 Trade Plan")

    if not entry or not sl:
        st.info("Level Entry / Stop Loss belum tersedia.")
        return

    risk_pct = ((entry - sl) / entry) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Entry", f"{entry:,.0f}")
    col2.metric("Stop Loss", f"{sl:,.0f}", f"-{risk_pct:.2f}%")

    if tp1:
        rr1 = (tp1 - entry) / (entry - sl)
        col3.metric("TP 1", f"{tp1:,.0f}", f"RR {rr1:.2f}")
    else:
        col3.metric("TP 1", "-")

    if tp2:
        rr2 = (tp2 - entry) / (entry - sl)
        col4.metric("TP 2", f"{tp2:,.0f}", f"RR {rr2:.2f}")
    else:
        col4.metric("TP 2", "-")


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Daily Stock Screener",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("📊 Daily Stock Screener")
st.caption("Screening otomatis saham potensial berbasis sistem trading")
st.markdown("### ⚙️ Pengaturan Screening")

col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

with col1:
    universe = st.selectbox(
        "Universe Saham",
        ["LQ45", "IDX30", "Kompas100", "Konglo"],
        index=0
    )

with col2:
    risk_ratio = st.selectbox(
        "Risk Reward",
        [1, 1.5, 2, 3, 4],
        index=2
    )

with col3:
    debug_mode = st.checkbox(
        "Debug",
        value=False
    )

with col4:
    run = st.button(
        "🚀 Jalankan Screening",
        use_container_width=True
    )

st.markdown("---")


# =====================================================
# MAIN
# =====================================================
if run:
    with st.spinner("Menjalankan screening harian..."):        
        results = run_daily_screener(
        universe=universe,
        risk_ratio=risk_ratio,
        debug=debug_mode
)    


    st.subheader("📋 Hasil Screening Hari Ini")

    if not results:
        st.warning("Tidak ada saham yang lolos hari ini.")
        st.stop()

    df = pd.DataFrame(results)

    status_order = {
        "CONFIRMED": 0,
        "TRIGGERED": 1,
        "SETUP": 2,
        "NO_TRADE": 3
    }


    df["status_order"] = df["status"].map(status_order)

    df = df.sort_values(
        ["status_order", "score"],
        ascending=[True, False]
    ).drop(columns=["status_order"])

    st.dataframe(
        df[["symbol", "status", "decision", "score", "reason"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("🔍 Bedah Logika Trading (Per Emiten)")

    results_sorted = sorted(
        results,
        key=lambda x: (
            status_order.get(x.get("status"), 99),
            -x.get("score", 0)
        )
    )

    for item in results_sorted:
        with st.expander(
            f"{item['symbol']} — {item['status']} | Score: {item['score']}",
            expanded=False
        ):
            st.markdown(
                f"""
                **Decision:** `{item['decision']}`  
                **Alasan Utama:** {item['reason']}
                """
            )

            render_pipeline(item)
            render_confirmation_abc(item)
            render_trade_plan(item)


            pilar_data = item.get("pilar", {})

            for pilar_name, pilar in pilar_data.items():
                with st.expander(
                    f"{pilar_name.upper()} — {pilar.get('status')} | Score: {pilar.get('score')}"
                ):
                    details = pilar.get("details", {})

                    if not details:
                        st.info("Tidak ada rule detail.")
                    else:
                        for rule_name, passed in details.items():
                            icon = "✅" if passed else "❌"
                            title = rule_name.replace("_", " ").title()
                            explanation = RULE_EXPLANATION.get(
                                rule_name,
                                "Penjelasan rule belum tersedia."
                            )

                            st.markdown(
                                f"""
                                {icon} **{title}**  
                                <span style="color:gray">{explanation}</span>
                                """,
                                unsafe_allow_html=True
                            )


# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Built for disciplined trading — bukan signal instan.")
