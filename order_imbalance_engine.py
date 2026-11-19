"""
TradingVolt • Live Order Imbalance & Auction Flow Engine
Calcula el desequilibrio neto de flujo de órdenes (Buy vs Sell Imbalance) en tiempo real
usando barras intradía (5m con pre/post-market) y volumen promedio diario (ADV 20D) vía yfinance.
Soporta cualquier ticker (NYSE, NASDAQ, ETFs) bajo demanda.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

DEFAULT_NOI_UNIVERSE = [
    "JPM", "BAC", "GS", "PLTR", "UBER", "GE", "XOM", "LMT", "SNOW",
    "AMD", "NVDA", "AAPL", "MSFT", "META", "TSLA",
]

AUCTION_TYPE_NAMES = {
    "M": "Market Open (09:30 AM)",
    "C": "Market Close (04:00 PM)",
    "H": "Intraday / Flow",
}

_LIVE_HISTORY_CACHE: dict[str, pd.DataFrame] = {}


def _compute_live_ticker_imbalance(symbol: str) -> pd.DataFrame:
    """Fetch live intraday 5m bars (prepost=True) and compute signed order-flow imbalance."""
    sym = symbol.strip().upper()
    if not sym:
        return pd.DataFrame()

    try:
        t = yf.Ticker(sym)
        intraday = t.history(period="2d", interval="5m", prepost=True, auto_adjust=True)
        daily = t.history(period="1mo", interval="1d", auto_adjust=True)
    except Exception:
        return pd.DataFrame()

    if intraday is None or intraday.empty or len(intraday) < 3:
        return pd.DataFrame()

    # Previous session close as reference price
    if daily is not None and len(daily) >= 2:
        ref_price = float(daily["Close"].iloc[-2])
        adv_shares = float(daily["Volume"].tail(20).mean()) if "Volume" in daily.columns else 1_000_000.0
    else:
        ref_price = float(intraday["Close"].iloc[0])
        adv_shares = float(intraday["Volume"].sum())

    if adv_shares <= 0:
        adv_shares = 1_000_000.0

    # Take last 12 bars (~1 hour of live flow)
    recent = intraday.tail(12).copy()
    hi = recent["High"].astype(float)
    lo = recent["Low"].astype(float)
    cl = recent["Close"].astype(float)
    vol = recent["Volume"].fillna(0).astype(float)

    rng = (hi - lo).replace(0, np.nan)
    # Close Location Value in [-1, +1]: +1 = closed at high (buy pressure), -1 = closed at low (sell pressure)
    clv = (((cl - lo) - (hi - cl)) / rng).fillna(0.0).clip(-1.0, 1.0)
    signed_imb = (vol * clv).round(0).astype(int)
    paired = (vol - signed_imb.abs()).clip(lower=0).round(0).astype(int)

    rows: list[dict[str, Any]] = []
    prev_imb: int | None = None
    for idx, row in recent.iterrows():
        ts = pd.Timestamp(idx)
        hhmm = ts.strftime("%H:%M")
        time_str = ts.strftime("%H:%M:%S")
        if hhmm <= "09:45":
            a_type = "M"
            a_time = "09:30"
        elif hhmm >= "15:45":
            a_type = "C"
            a_time = "16:00"
        else:
            a_type = "H"
            a_time = hhmm

        imb_q = int(signed_imb.loc[idx])
        pair_q = int(paired.loc[idx])
        px = float(cl.loc[idx])

        rows.append(
            {
                "symbol": sym,
                "name": sym,
                "auction_type": a_type,
                "auction_time": a_time,
                "time_str": time_str,
                "imbalance_qty": imb_q,
                "paired_qty": pair_q,
                "clearing_price": px,
                "ref_price": ref_price,
                "adv_shares": adv_shares,
                "prev_qty": prev_imb,
            }
        )
        prev_imb = imb_q

    df_hist = pd.DataFrame(rows)
    _LIVE_HISTORY_CACHE[sym] = df_hist
    return df_hist


def get_latest_noi_feed(
    auction_filter: str = "All",
    direction_filter: str = "All",
    trend_filter: str = "All",
    search_query: str = "",
    min_imbalance_shares: int = 0,
) -> pd.DataFrame:
    """Return live intraday order-imbalance snapshots for the radar + any searched ticker."""
    symbols = list(DEFAULT_NOI_UNIVERSE)
    if search_query:
        for tok in search_query.replace(",", " ").split():
            s = tok.strip().upper()
            if s and s not in symbols:
                symbols.insert(0, s)

    # If user explicitly searched a single ticker, prioritize fetching it immediately
    if search_query and len(search_query.strip().split()) == 1:
        q_sym = search_query.strip().upper()
        target_syms = [q_sym] + [s for s in symbols if s != q_sym]
    else:
        target_syms = symbols

    latest_rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_compute_live_ticker_imbalance, sym): sym for sym in target_syms}
        for fut in as_completed(futures):
            try:
                df_t = fut.result()
            except Exception:
                continue
            if df_t is None or df_t.empty:
                continue

            last_rec = df_t.iloc[-1].to_dict()
            qty = last_rec["imbalance_qty"]
            paired = last_rec["paired_qty"]
            price = last_rec["clearing_price"]
            ref_p = last_rec["ref_price"]
            adv = last_rec["adv_shares"]
            prev = last_rec["prev_qty"]

            dir_label = "BUY" if qty > 0 else ("SELL" if qty < 0 else "FLAT")
            abs_qty = abs(qty)
            imb_val_m = (abs_qty * price) / 1_000_000.0
            paired_val_m = (paired * price) / 1_000_000.0
            total_auction_m = ((abs_qty + paired) * price) / 1_000_000.0
            pct_adv = (abs_qty / adv) * 100.0 if adv > 0 else 0.0
            paired_ratio = (paired / (paired + abs_qty)) * 100.0 if (paired + abs_qty) > 0 else 0.0
            price_delta_pct = ((price - ref_p) / ref_p) * 100.0 if ref_p > 0 else 0.0

            if prev is not None:
                if abs_qty < abs(prev):
                    trend = "shrinking"
                elif abs_qty > abs(prev):
                    trend = "growing"
                else:
                    trend = "flat"
            else:
                trend = "initial"

            last_rec["direction"] = dir_label
            last_rec["abs_imbalance"] = abs_qty
            last_rec["imbalance_val_m"] = imb_val_m
            last_rec["paired_val_m"] = paired_val_m
            last_rec["total_auction_m"] = total_auction_m
            last_rec["pct_adv"] = pct_adv
            last_rec["paired_ratio"] = paired_ratio
            last_rec["price_delta_pct"] = price_delta_pct
            last_rec["trend"] = trend
            last_rec["auction_label"] = AUCTION_TYPE_NAMES.get(last_rec["auction_type"], "Intraday / Flow")
            latest_rows.append(last_rec)

    if not latest_rows:
        return pd.DataFrame()

    df = pd.DataFrame(latest_rows)

    if auction_filter != "All":
        code = "M" if "Open" in auction_filter else ("C" if "Close" in auction_filter else "H")
        df = df[df["auction_type"] == code]

    if direction_filter != "All":
        df = df[df["direction"] == direction_filter]

    if trend_filter != "All":
        df = df[df["trend"] == trend_filter.lower()]

    if search_query:
        q = search_query.upper().strip()
        df = df[df["symbol"].str.contains(q) | df["name"].str.upper().str.contains(q)]

    if min_imbalance_shares > 0:
        df = df[df["abs_imbalance"] >= min_imbalance_shares]

    return df.sort_values("imbalance_val_m", ascending=False).reset_index(drop=True)


def get_ticker_noi_history(symbol: str) -> pd.DataFrame:
    """Return live 5m order-flow history for a specific ticker."""
    sym = symbol.upper().strip()
    df_hist = _LIVE_HISTORY_CACHE.get(sym)
    if df_hist is None or df_hist.empty:
        df_hist = _compute_live_ticker_imbalance(sym)
    if df_hist is None or df_hist.empty:
        return pd.DataFrame()

    ticker_df = df_hist.copy()
    ticker_df["abs_imbalance"] = ticker_df["imbalance_qty"].abs()
    ticker_df["imbalance_val_m"] = (ticker_df["abs_imbalance"] * ticker_df["clearing_price"]) / 1_000_000.0
    ticker_df["direction"] = ticker_df["imbalance_qty"].apply(lambda q: "BUY" if q > 0 else ("SELL" if q < 0 else "FLAT"))
    return ticker_df.reset_index(drop=True)


def render_noi_auction_chart(symbol: str) -> go.Figure:
    """Render live intraday price vs reference and paired vs net imbalance volume."""
    df_hist = get_ticker_noi_history(symbol)
    if df_hist.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No hay datos intradía disponibles para {symbol}", showarrow=False, font=dict(color="#94A3B8", size=14))
        fig.update_layout(paper_bgcolor="#0A0E17", plot_bgcolor="#0A0E17")
        return fig

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.55, 0.45],
        subplot_titles=[
            f"<b>{symbol}</b> • Trayectoria de Precio en Vivo (5m) vs Cierre Previo",
            "Volumen Emparejado vs Desequilibrio Neto (Signed Volume Imbalance)",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=df_hist["time_str"],
            y=df_hist["clearing_price"],
            mode="lines+markers+text",
            name="Precio Live (5m)",
            line=dict(color="#00F0FF", width=2.5),
            marker=dict(size=8, color="#00FF87", line=dict(color="#FFFFFF", width=1.2)),
            text=[f"${p:.2f}" for p in df_hist["clearing_price"]],
            textposition="top center",
            textfont=dict(size=10, color="#00F0FF"),
        ),
        row=1,
        col=1,
    )

    ref_price = df_hist["ref_price"].iloc[0]
    fig.add_hline(
        y=ref_price,
        line_dash="dash",
        line_color="#E2E8F0",
        line_width=1.2,
        annotation_text=f"Ref (Prev Close): ${ref_price:.2f}",
        annotation_position="bottom right",
        annotation_font=dict(color="#94A3B8", size=10),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=df_hist["time_str"],
            y=df_hist["paired_qty"],
            name="Volumen Emparejado",
            marker_color="rgba(59, 130, 246, 0.75)",
            marker_line=dict(color="#3B82F6", width=1),
        ),
        row=2,
        col=1,
    )

    imb_colors = ["#10B981" if q > 0 else "#EF4444" for q in df_hist["imbalance_qty"]]
    fig.add_trace(
        go.Bar(
            x=df_hist["time_str"],
            y=df_hist["abs_imbalance"],
            name="Desequilibrio Neto (Imbalance)",
            marker_color=imb_colors,
            marker_line=dict(color="#FFFFFF", width=1.0),
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=520,
        margin=dict(l=40, r=30, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#94A3B8", size=11)),
        hovermode="x unified",
        barmode="group",
    )

    fig.update_xaxes(showgrid=True, gridcolor="#1E293B", color="#94A3B8")
    fig.update_yaxes(showgrid=True, gridcolor="#1E293B", color="#94A3B8")
    return fig
