"""
AskBull.org — PSX AI Trading Signals
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz
import time

from bot_engine import (
    run_daily_scan, get_top_picks, market_is_open,
    last_scan_time, PSX_UNIVERSE, compute_rsi, compute_macd, compute_bollinger
)

PST = pytz.timezone("Asia/Karachi")

# ─── Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskBull — PSX Trading Signals",
    page_icon="🐂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --green:  #00e676;
    --red:    #ff1744;
    --gold:   #ffd600;
    --blue:   #2979ff;
    --bg:     #0a0e1a;
    --card:   #111827;
    --border: #1f2937;
    --text:   #e5e7eb;
    --muted:  #6b7280;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }

/* ── Header ── */
.ab-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1rem 0 0.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.ab-logo {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffd600, #ff6d00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}
.ab-tagline {
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.05em;
}
.ab-live-dot {
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    display: inline-block;
    animation: pulse 1.5s infinite;
    margin-right: 5px;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.5; transform:scale(1.4); }
}

/* ── Signal Cards ── */
.signal-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color .2s;
}
.signal-card:hover { border-color: #374151; }

.signal-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
}
.badge-strong-buy  { background:#003d1f; color:#00e676; border:1px solid #00e676; }
.badge-buy         { background:#001a0d; color:#69f0ae; border:1px solid #69f0ae; }
.badge-sell        { background:#3d0010; color:#ff5252; border:1px solid #ff5252; }
.badge-strong-sell { background:#1a0005; color:#ff1744; border:1px solid #ff1744; }
.badge-hold        { background:#1a1500; color:#ffd600; border:1px solid #ffd600; }

.conviction-high   { color: var(--green); font-size:.75rem; font-weight:600; }
.conviction-medium { color: var(--gold);  font-size:.75rem; font-weight:600; }
.conviction-low    { color: var(--muted); font-size:.75rem; font-weight:600; }

/* ── Metric boxes ── */
.metric-row { display:flex; gap:10px; flex-wrap:wrap; margin: 0.6rem 0; }
.metric-box {
    background: #0d1525;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
}
.metric-label { color: var(--muted); font-size:.68rem; margin-bottom:2px; }
.metric-val   { color: var(--text);  font-weight:600; }
.metric-green { color: var(--green) !important; }
.metric-red   { color: var(--red)   !important; }

/* ── Ticker header ── */
.ticker-name  { font-weight:700; font-size:1.05rem; margin-bottom:4px; }
.ticker-price {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text);
}

/* ── Section headers ── */
.section-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Scrolling ticker tape ── */
.ticker-tape {
    background: #0d1117;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 6px 0;
    overflow: hidden;
    white-space: nowrap;
    margin-bottom: 1rem;
}
.ticker-tape-inner {
    display: inline-block;
    animation: scroll 30s linear infinite;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}
@keyframes scroll {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* ── Market status ── */
.market-open   { color: var(--green); font-size:.8rem; font-weight:600; }
.market-closed { color: var(--red);   font-size:.8rem; font-weight:600; }

/* ── Premium blur ── */
.blurred { filter: blur(5px); pointer-events: none; user-select: none; }

/* ── Buttons ── */
.stButton>button {
    background: linear-gradient(135deg, #ffd600, #ff6d00);
    color: #000;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    font-family: 'Space Grotesk', sans-serif;
}
.stButton>button:hover { opacity: .9; }

/* ── Reasons list ── */
.reason-item {
    font-size: 0.78rem;
    color: var(--muted);
    padding: 2px 0;
}
.reason-item::before { content: "↳ "; color: var(--gold); }
</style>
""", unsafe_allow_html=True)


# ─── Session State ─────────────────────────────────────────────────────────
if "scan_results" not in st.session_state:
    st.session_state.scan_results  = []
if "last_scan"    not in st.session_state:
    st.session_state.last_scan     = None
if "is_premium"   not in st.session_state:
    st.session_state.is_premium    = False  # Will be True for paying users later


# ─── Helper: Signal Badge ──────────────────────────────────────────────────
def signal_html(signal: str) -> str:
    cls = {
        "STRONG BUY":  "badge-strong-buy",
        "BUY":         "badge-buy",
        "HOLD":        "badge-hold",
        "SELL":        "badge-sell",
        "STRONG SELL": "badge-strong-sell",
    }.get(signal, "badge-hold")
    return f'<span class="signal-badge {cls}">{signal}</span>'


def conviction_html(conviction: str) -> str:
    cls = f"conviction-{conviction.lower()}"
    return f'<span class="{cls}">⬤ {conviction} CONVICTION</span>'


# ─── Chart Builder ─────────────────────────────────────────────────────────
def build_chart(result: dict) -> go.Figure:
    df = result["df"].tail(60)
    close = df["Close"].squeeze()

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"].squeeze(),
        high=df["High"].squeeze(),
        low=df["Low"].squeeze(),
        close=close,
        name="Price",
        increasing_line_color="#00e676",
        decreasing_line_color="#ff1744",
        increasing_fillcolor="#00e676",
        decreasing_fillcolor="#ff1744",
    ), row=1, col=1)

    # Bollinger Bands
    bb_up, bb_mid, bb_lo = compute_bollinger(close)
    fig.add_trace(go.Scatter(x=df.index, y=bb_up, line=dict(color="#374151", width=1, dash="dot"), name="BB Upper", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb_lo, line=dict(color="#374151", width=1, dash="dot"), name="BB Lower", fill="tonexty", fillcolor="rgba(55,65,81,0.1)", showlegend=False), row=1, col=1)

    # EMAs
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    fig.add_trace(go.Scatter(x=df.index, y=ema20, line=dict(color="#ffd600", width=1.5), name="EMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ema50, line=dict(color="#2979ff", width=1.5), name="EMA50"), row=1, col=1)

    # T1 / T2 / SL lines
    if result["signal"] in ("BUY", "STRONG BUY"):
        fig.add_hline(y=result["t1"],        line=dict(color="#69f0ae", width=1, dash="dash"), annotation_text=f"T1 {result['t1']}", row=1, col=1)
        fig.add_hline(y=result["t2"],        line=dict(color="#00e676", width=1, dash="dash"), annotation_text=f"T2 {result['t2']}", row=1, col=1)
        fig.add_hline(y=result["stop_loss"], line=dict(color="#ff5252", width=1, dash="dash"), annotation_text=f"SL {result['stop_loss']}", row=1, col=1)

    # RSI
    rsi = compute_rsi(close)
    fig.add_trace(go.Scatter(x=df.index, y=rsi, line=dict(color="#a78bfa", width=1.5), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#ff5252", width=0.8, dash="dot"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#69f0ae", width=0.8, dash="dot"), row=2, col=1)

    # MACD
    macd, sig, hist = compute_macd(close)
    colors = ["#00e676" if v >= 0 else "#ff1744" for v in hist]
    fig.add_trace(go.Bar(x=df.index, y=hist, marker_color=colors, name="MACD Hist"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=macd, line=dict(color="#ffd600", width=1.2), name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=sig,  line=dict(color="#ff6d00", width=1.2), name="Signal"), row=3, col=1)

    fig.update_layout(
        height=600,
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0a0e1a",
        font=dict(family="JetBrains Mono", color="#e5e7eb", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.04, bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        margin=dict(l=0, r=0, t=30, b=0),
    )
    for i in range(1, 4):
        fig.update_yaxes(gridcolor="#1f2937", row=i, col=1, zerolinecolor="#1f2937")
        fig.update_xaxes(gridcolor="#1f2937", row=i, col=1)

    fig.update_yaxes(title_text="RSI",  row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)

    return fig


# ─── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐂 AskBull")
    st.markdown("---")

    is_open = market_is_open()
    status_html = '<span class="market-open">● MARKET OPEN</span>' if is_open else '<span class="market-closed">● MARKET CLOSED</span>'
    st.markdown(status_html, unsafe_allow_html=True)

    now_pkt = datetime.now(PST).strftime("%I:%M %p PKT")
    st.caption(f"PSX time: {now_pkt}")

    st.markdown("---")

    # Scan button
    if st.button("🔍 Run Daily Scan", use_container_width=True):
        with st.spinner("Scanning PSX stocks..."):
            results = run_daily_scan(PSX_UNIVERSE)
            st.session_state.scan_results = results
            st.session_state.last_scan    = last_scan_time()
        st.success(f"Scanned {len(results)} stocks")

    if st.session_state.last_scan:
        st.caption(f"Last scan: {st.session_state.last_scan}")

    st.markdown("---")

    # Account status
    st.markdown("**Account**")
    if st.session_state.is_premium:
        st.success("✅ Premium Active")
    else:
        st.warning("🔒 Free Plan")
        st.markdown('<small>Upgrade to see all picks, charts & journal</small>', unsafe_allow_html=True)
        if st.button("⭐ Upgrade to Premium", use_container_width=True):
            st.info("Payment integration coming in Step 2!")

    st.markdown("---")
    st.caption("AskBull.org © 2025\nPSX AI Trading Signals")


# ─── Main Content ──────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="ab-header">
    <div>
        <div class="ab-logo">🐂 AskBull</div>
        <div class="ab-tagline">AI-POWERED PSX TRADING SIGNALS · KARACHI STOCK EXCHANGE</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_picks, tab_all, tab_chart, tab_journal = st.tabs([
    "📊 Today's Picks", "📋 All Stocks", "📈 Charts", "📓 Trade Journal"
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Today's Picks
# ═══════════════════════════════════════════════════════════════════════════
with tab_picks:
    if not st.session_state.scan_results:
        st.markdown("""
        <div style="text-align:center; padding:3rem 0; color:#6b7280;">
            <div style="font-size:3rem; margin-bottom:1rem;">🐂</div>
            <div style="font-size:1.1rem; font-weight:600; color:#e5e7eb;">No scan run yet</div>
            <div style="margin-top:.5rem;">Click <b>Run Daily Scan</b> in the sidebar to get today's picks</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        results = st.session_state.scan_results
        picks   = get_top_picks(results)

        # Summary row
        buy_count  = sum(1 for r in results if r["signal"] in ("BUY","STRONG BUY"))
        sell_count = sum(1 for r in results if r["signal"] in ("SELL","STRONG SELL"))
        hold_count = sum(1 for r in results if r["signal"] == "HOLD")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Stocks Scanned",  len(results))
        col2.metric("Buy Signals",     buy_count,  delta=None)
        col3.metric("Sell Signals",    sell_count, delta=None)
        col4.metric("Market Neutral",  hold_count)

        st.markdown('<div class="section-title">Top Picks Today</div>', unsafe_allow_html=True)

        if not picks:
            st.info("No strong buy signals today. Market may be consolidating.")
        else:
            for i, r in enumerate(picks):
                is_locked = (not st.session_state.is_premium) and (i >= 1)

                with st.container():
                    st.markdown(f"""
                    <div class="signal-card">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                            <div>
                                <div class="ticker-name">
                                    {r['name']} <span style="color:#6b7280; font-weight:400; font-size:.85rem;">({r['ticker'].replace('.KA','')})</span>
                                </div>
                                <div style="margin:4px 0;">
                                    {signal_html(r['signal'])}
                                    &nbsp;{conviction_html(r['conviction'])}
                                </div>
                            </div>
                            <div class="ticker-price {'blurred' if is_locked else ''}">
                                PKR {r['price']:,.2f}
                            </div>
                        </div>

                        <div class="metric-row {'blurred' if is_locked else ''}">
                            <div class="metric-box">
                                <div class="metric-label">Target 1</div>
                                <div class="metric-val metric-green">PKR {r['t1']:,.2f}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Target 2</div>
                                <div class="metric-val metric-green">PKR {r['t2']:,.2f}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Stop Loss</div>
                                <div class="metric-val metric-red">PKR {r['stop_loss']:,.2f}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">RSI</div>
                                <div class="metric-val">{r['rsi']}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Volume</div>
                                <div class="metric-val">{r['vol_ratio']:.1f}x avg</div>
                            </div>
                        </div>

                        <div class="{'blurred' if is_locked else ''}">
                            {''.join(f'<div class="reason-item">{reason}</div>' for reason in r['reasons'][:3])}
                        </div>

                        {'<div style="margin-top:8px;font-size:.78rem;color:#ffd600;">🔒 Upgrade to Premium to see targets & reasons</div>' if is_locked else ''}
                    </div>
                    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — All Stocks
# ═══════════════════════════════════════════════════════════════════════════
with tab_all:
    if not st.session_state.scan_results:
        st.info("Run the scan from the sidebar first.")
    else:
        results = st.session_state.scan_results

        # Filter controls
        col1, col2 = st.columns([1, 3])
        with col1:
            sig_filter = st.multiselect(
                "Filter by signal",
                ["STRONG BUY","BUY","HOLD","SELL","STRONG SELL"],
                default=["STRONG BUY","BUY","HOLD","SELL","STRONG SELL"]
            )

        filtered = [r for r in results if r["signal"] in sig_filter]

        # Build dataframe
        rows = []
        for r in filtered:
            rows.append({
                "Stock":      r["name"],
                "Ticker":     r["ticker"].replace(".KA",""),
                "Price (PKR)":f"{r['price']:,.2f}",
                "Signal":     r["signal"],
                "Score":      r["score"],
                "RSI":        r["rsi"],
                "Vol Ratio":  r["vol_ratio"],
                "T1":         r["t1"],
                "T2":         r["t2"],
                "Stop Loss":  r["stop_loss"],
            })

        df_display = pd.DataFrame(rows)

        def colour_signal(val):
            colours = {
                "STRONG BUY":  "color:#00e676; font-weight:700",
                "BUY":         "color:#69f0ae; font-weight:600",
                "HOLD":        "color:#ffd600",
                "SELL":        "color:#ff5252",
                "STRONG SELL": "color:#ff1744; font-weight:700",
            }
            return colours.get(val, "")

        styled = df_display.style.map(colour_signal, subset=["Signal"])
        st.dataframe(styled, use_container_width=True, height=500)

        # CSV download
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download CSV", csv, "askbull_picks.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Charts
# ═══════════════════════════════════════════════════════════════════════════
with tab_chart:
    if not st.session_state.scan_results:
        st.info("Run the scan first to see charts.")
    else:
        results  = st.session_state.scan_results
        names    = [f"{r['name']} ({r['ticker'].replace('.KA','')}) — {r['signal']}" for r in results]
        selected = st.selectbox("Select stock to chart", names)

        idx    = names.index(selected)
        result = results[idx]

        # Lock charts for free users (only first stock visible)
        if (not st.session_state.is_premium) and idx > 0:
            st.warning("🔒 **Premium required** — Upgrade to view charts for all stocks.")
            st.markdown("Free plan includes chart for the #1 pick only.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Price",     f"PKR {result['price']:,.2f}")
            col2.metric("Signal",    result["signal"])
            col3.metric("T1",        f"PKR {result['t1']:,.2f}")
            col4.metric("Stop Loss", f"PKR {result['stop_loss']:,.2f}")

            st.plotly_chart(build_chart(result), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — Trade Journal
# ═══════════════════════════════════════════════════════════════════════════
with tab_journal:
    if not st.session_state.is_premium:
        st.warning("🔒 **Premium feature** — Trade journal is available for premium subscribers.")
        st.markdown("Track your trades, calculate P&L, and help calibrate the bot's signals.")
    else:
        st.markdown('<div class="section-title">Log a Trade</div>', unsafe_allow_html=True)

        if "journal" not in st.session_state:
            st.session_state.journal = []

        with st.form("trade_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                ticker    = st.text_input("Ticker (e.g. OGDC)")
                direction = st.selectbox("Direction", ["BUY","SELL"])
            with col2:
                buy_price  = st.number_input("Entry Price (PKR)", min_value=0.0, format="%.2f")
                sell_price = st.number_input("Exit Price (PKR)",  min_value=0.0, format="%.2f")
            with col3:
                qty        = st.number_input("Shares", min_value=1, step=1)
                trade_date = st.date_input("Trade Date")

            notes = st.text_area("Notes (optional)", height=60)
            submitted = st.form_submit_button("Add Trade")

            if submitted and ticker and buy_price > 0 and sell_price > 0:
                pnl = (sell_price - buy_price) * qty if direction == "BUY" else (buy_price - sell_price) * qty
                st.session_state.journal.append({
                    "Date":      str(trade_date),
                    "Ticker":    ticker.upper(),
                    "Direction": direction,
                    "Entry":     buy_price,
                    "Exit":      sell_price,
                    "Shares":    qty,
                    "P&L (PKR)": round(pnl, 2),
                    "Notes":     notes,
                })
                st.success(f"Trade logged! P&L: PKR {pnl:,.2f}")

        if st.session_state.journal:
            st.markdown('<div class="section-title">Trade History</div>', unsafe_allow_html=True)
            df_journal = pd.DataFrame(st.session_state.journal)

            total_pnl   = df_journal["P&L (PKR)"].sum()
            win_trades  = (df_journal["P&L (PKR)"] > 0).sum()
            total_trades = len(df_journal)
            win_rate    = win_trades / total_trades * 100 if total_trades else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Trades", total_trades)
            c2.metric("Win Rate",     f"{win_rate:.0f}%")
            c3.metric("Total P&L",    f"PKR {total_pnl:,.0f}", delta=f"{total_pnl:,.0f}")
            c4.metric("Winning Trades", win_trades)

            def colour_pnl(val):
                if isinstance(val, (int, float)):
                    return "color:#00e676" if val > 0 else "color:#ff1744"
                return ""

            st.dataframe(
                df_journal.style.map(colour_pnl, subset=["P&L (PKR)"]),
                use_container_width=True
            )
