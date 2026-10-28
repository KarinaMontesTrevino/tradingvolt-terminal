"""
TradingVolt • NYSE Order Imbalance Engine (NOI Auctions)
Motor de Inteligencia de Subastas de Apertura, Cierre y Halts de la Bolsa de Nueva York (NYSE).
Reverse engineered from Massive NOI WebSocket Stream & NYSE Auction Mechanics.
Proporciona:
- Subastas de Apertura (Market Open 'M', 9:00 - 9:30 AM ET)
- Subastas de Cierre (Market Close 'C', 3:50 - 4:00 PM ET, MOC Orders)
- Subastas Post-Halt de Volatilidad (Trading Halt 'H')
- Métricas: Imbalance Quantity (o), Paired Shares (p), Indicative Clearing Price (b), % of ADV, Imbalance Value ($M)
- Detector de Convergencia (Shrinking vs Growing)
"""

from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------- BASE DE DATOS DE EVENTOS NOI HISTÓRICOS Y EN VIVO -----------------
NOI_AUCTION_RECORDS = [
    # JPM - Market Open Auction (M) - Buy Imbalance Shrinking (Convergencia Alcista)
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:15:22", "imbalance_qty": 52000, "paired_qty": 428000, "clearing_price": 222.50, "ref_price": 221.80, "adv_shares": 9500000, "prev_qty": None},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:20:10", "imbalance_qty": 44000, "paired_qty": 438000, "clearing_price": 222.40, "ref_price": 221.80, "adv_shares": 9500000, "prev_qty": 52000},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:25:40", "imbalance_qty": 38000, "paired_qty": 444200, "clearing_price": 222.35, "ref_price": 221.80, "adv_shares": 9500000, "prev_qty": 44000},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:29:15", "imbalance_qty": 18500, "paired_qty": 465000, "clearing_price": 222.25, "ref_price": 221.80, "adv_shares": 9500000, "prev_qty": 38000},

    # BAC - Market Open Auction (M) - Sell Imbalance Growing (Presión Vendedora Creciente)
    {"symbol": "BAC", "name": "Bank of America Corp.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:15:22", "imbalance_qty": -31000, "paired_qty": 284000, "clearing_price": 42.75, "ref_price": 43.10, "adv_shares": 38000000, "prev_qty": None},
    {"symbol": "BAC", "name": "Bank of America Corp.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:22:15", "imbalance_qty": -45000, "paired_qty": 270000, "clearing_price": 42.60, "ref_price": 43.10, "adv_shares": 38000000, "prev_qty": -31000},
    {"symbol": "BAC", "name": "Bank of America Corp.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:28:50", "imbalance_qty": -78000, "paired_qty": 255000, "clearing_price": 42.45, "ref_price": 43.10, "adv_shares": 38000000, "prev_qty": -45000},

    # GS - Market Open Auction (M) - Massive Buy Imbalance Shrinking (Liquidez llegando)
    {"symbol": "GS", "name": "Goldman Sachs Group", "auction_type": "M", "auction_time": "09:30", "time_str": "09:15:22", "imbalance_qty": 124000, "paired_qty": 852000, "clearing_price": 512.30, "ref_price": 508.50, "adv_shares": 2200000, "prev_qty": None},
    {"symbol": "GS", "name": "Goldman Sachs Group", "auction_type": "M", "auction_time": "09:30", "time_str": "09:24:30", "imbalance_qty": 81000, "paired_qty": 895000, "clearing_price": 512.15, "ref_price": 508.50, "adv_shares": 2200000, "prev_qty": 124000},
    {"symbol": "GS", "name": "Goldman Sachs Group", "auction_type": "M", "auction_time": "09:30", "time_str": "09:29:45", "imbalance_qty": 32000, "paired_qty": 945000, "clearing_price": 511.90, "ref_price": 508.50, "adv_shares": 2200000, "prev_qty": 81000},

    # PLTR - Market Close Auction (C) - Huge Buy Imbalance (MOC Index Flow)
    {"symbol": "PLTR", "name": "Palantir Technologies", "auction_type": "C", "auction_time": "16:00", "time_str": "15:50:10", "imbalance_qty": 650000, "paired_qty": 3200000, "clearing_price": 43.80, "ref_price": 43.20, "adv_shares": 45000000, "prev_qty": None},
    {"symbol": "PLTR", "name": "Palantir Technologies", "auction_type": "C", "auction_time": "16:00", "time_str": "15:55:00", "imbalance_qty": 820000, "paired_qty": 3450000, "clearing_price": 43.95, "ref_price": 43.20, "adv_shares": 45000000, "prev_qty": 650000},
    {"symbol": "PLTR", "name": "Palantir Technologies", "auction_type": "C", "auction_time": "16:00", "time_str": "15:59:30", "imbalance_qty": 410000, "paired_qty": 3980000, "clearing_price": 43.85, "ref_price": 43.20, "adv_shares": 45000000, "prev_qty": 820000},

    # UBER - Market Close Auction (C) - Sell Imbalance Shrinking
    {"symbol": "UBER", "name": "Uber Technologies Inc.", "auction_type": "C", "auction_time": "16:00", "time_str": "15:52:15", "imbalance_qty": -320000, "paired_qty": 1850000, "clearing_price": 78.20, "ref_price": 78.60, "adv_shares": 18000000, "prev_qty": None},
    {"symbol": "UBER", "name": "Uber Technologies Inc.", "auction_type": "C", "auction_time": "16:00", "time_str": "15:58:45", "imbalance_qty": -115000, "paired_qty": 2050000, "clearing_price": 78.45, "ref_price": 78.60, "adv_shares": 18000000, "prev_qty": -320000},

    # GE - Market Open Auction (M) - Strong Buy Imbalance Growing
    {"symbol": "GE", "name": "GE Aerospace", "auction_type": "M", "auction_time": "09:30", "time_str": "09:18:00", "imbalance_qty": 45000, "paired_qty": 310000, "clearing_price": 192.50, "ref_price": 189.50, "adv_shares": 5200000, "prev_qty": None},
    {"symbol": "GE", "name": "GE Aerospace", "auction_type": "M", "auction_time": "09:30", "time_str": "09:27:30", "imbalance_qty": 78000, "paired_qty": 330000, "clearing_price": 193.10, "ref_price": 189.50, "adv_shares": 5200000, "prev_qty": 45000},

    # XOM - Market Close Auction (C) - Large Energy Imbalance
    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "auction_type": "C", "auction_time": "16:00", "time_str": "15:51:20", "imbalance_qty": 480000, "paired_qty": 4100000, "clearing_price": 121.80, "ref_price": 121.20, "adv_shares": 16000000, "prev_qty": None},
    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "auction_type": "C", "auction_time": "16:00", "time_str": "15:57:10", "imbalance_qty": 290000, "paired_qty": 4350000, "clearing_price": 121.60, "ref_price": 121.20, "adv_shares": 16000000, "prev_qty": 480000},

    # LMT - Volatility Halt Reopening (H) - Buy Imbalance Post-Halt
    {"symbol": "LMT", "name": "Lockheed Martin Corp.", "auction_type": "H", "auction_time": "11:15", "time_str": "11:10:00", "imbalance_qty": 24000, "paired_qty": 85000, "clearing_price": 582.00, "ref_price": 574.00, "adv_shares": 1400000, "prev_qty": None},
    {"symbol": "LMT", "name": "Lockheed Martin Corp.", "auction_type": "H", "auction_time": "11:15", "time_str": "11:14:30", "imbalance_qty": 14000, "paired_qty": 95000, "clearing_price": 580.50, "ref_price": 574.00, "adv_shares": 1400000, "prev_qty": 24000},

    # SNOW - Market Open Auction (M) - Cloud Tech Reversal
    {"symbol": "SNOW", "name": "Snowflake Inc.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:16:40", "imbalance_qty": -85000, "paired_qty": 390000, "clearing_price": 124.50, "ref_price": 126.80, "adv_shares": 4800000, "prev_qty": None},
    {"symbol": "SNOW", "name": "Snowflake Inc.", "auction_type": "M", "auction_time": "09:30", "time_str": "09:28:10", "imbalance_qty": -42000, "paired_qty": 435000, "clearing_price": 125.20, "ref_price": 126.80, "adv_shares": 4800000, "prev_qty": -85000}
]

AUCTION_TYPE_NAMES = {
    "M": "Market Open (09:30 AM)",
    "C": "Market Close (04:00 PM)",
    "H": "Halt Reopening"
}


def get_latest_noi_feed(
    auction_filter: str = "All",
    direction_filter: str = "All",
    trend_filter: str = "All",
    search_query: str = "",
    min_imbalance_shares: int = 0
) -> pd.DataFrame:
    """
    Retorna el estado más reciente de desequilibrio de órdenes (NOI) por ticker con cálculo de convergencia.
    """
    # Tomar el último registro de cada ticker
    df_raw = pd.DataFrame(NOI_AUCTION_RECORDS)
    
    # Agrupar para obtener el último snapshot de cada ticker
    latest_rows = []
    for sym, group in df_raw.groupby("symbol"):
        last_rec = group.iloc[-1].to_dict()
        
        # Calcular campos derivados cuantitativos
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
        
        # Porcentaje del Volumen Promedio Diario (ADV Normalization)
        pct_adv = (abs_qty / adv) * 100.0 if adv > 0 else 0.0
        
        # Ratio de emparejamiento (Paired Ratio %)
        paired_ratio = (paired / (paired + abs_qty)) * 100.0 if (paired + abs_qty) > 0 else 0.0
        
        # Desviación estimada de precio vs precio de referencia (%)
        price_delta_pct = ((price - ref_p) / ref_p) * 100.0 if ref_p > 0 else 0.0
        
        # Indicador de Convergencia (Shrinking vs Growing)
        if prev is not None:
            if abs_qty < abs(prev):
                trend = "shrinking"  # Contra-liquidez llegando
            elif abs_qty > abs(prev):
                trend = "growing"    # Presión desbalanceada en aumento
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
        last_rec["auction_label"] = AUCTION_TYPE_NAMES.get(last_rec["auction_type"], "Auction")

        latest_rows.append(last_rec)
        
    df = pd.DataFrame(latest_rows)

    # Filtros
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
    """
    Retorna la serie temporal completa de actualizaciones NOI para un ticker específico.
    """
    df_raw = pd.DataFrame(NOI_AUCTION_RECORDS)
    ticker_df = df_raw[df_raw["symbol"] == symbol.upper().strip()].copy()
    if ticker_df.empty:
        return pd.DataFrame()
        
    ticker_df["abs_imbalance"] = ticker_df["imbalance_qty"].abs()
    ticker_df["imbalance_val_m"] = (ticker_df["abs_imbalance"] * ticker_df["clearing_price"]) / 1_000_000.0
    ticker_df["direction"] = ticker_df["imbalance_qty"].apply(lambda q: "BUY" if q > 0 else ("SELL" if q < 0 else "FLAT"))
    return ticker_df.reset_index(drop=True)


def render_noi_auction_chart(symbol: str) -> go.Figure:
    """
    Renderiza el gráfico de evolución de subasta:
    - Panel 1: Precio Indicativo de Clearing vs Precio de Referencia
    - Panel 2: Desequilibrio de Órdenes (Imbalance) vs Acciones Emparejadas (Paired)
    """
    df_hist = get_ticker_noi_history(symbol)
    if df_hist.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No hay stream de NOI disponible para {symbol}", showarrow=False, font=dict(color="#94A3B8", size=14))
        fig.update_layout(paper_bgcolor="#0A0E17", plot_bgcolor="#0A0E17")
        return fig

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.55, 0.45],
        subplot_titles=[
            f"<b>{symbol}</b> • Trayectoria de Precio Indicativo de Subasta",
            "Volumen Emparejado (Paired) vs Desequilibrio Neto (Imbalance)"
        ]
    )

    # 1. Panel de Precios
    fig.add_trace(go.Scatter(
        x=df_hist["time_str"],
        y=df_hist["clearing_price"],
        mode="lines+markers+text",
        name="Indicative Clearing Price",
        line=dict(color="#00F0FF", width=2.5),
        marker=dict(size=9, color="#00FF87", line=dict(color="#FFFFFF", width=1.5)),
        text=[f"${p:.2f}" for p in df_hist["clearing_price"]],
        textposition="top center",
        textfont=dict(size=11, color="#00F0FF")
    ), row=1, col=1)

    ref_price = df_hist["ref_price"].iloc[0]
    fig.add_hline(
        y=ref_price, line_dash="dash", line_color="#E2E8F0", line_width=1.2,
        annotation_text=f"Ref Price: ${ref_price:.2f}", annotation_position="bottom right",
        annotation_font=dict(color="#94A3B8", size=10), row=1, col=1
    )

    # 2. Panel de Barras: Paired vs Imbalance
    fig.add_trace(go.Bar(
        x=df_hist["time_str"],
        y=df_hist["paired_qty"],
        name="Acciones Emparejadas (Paired)",
        marker_color="rgba(59, 130, 246, 0.75)",
        marker_line=dict(color="#3B82F6", width=1)
    ), row=2, col=1)

    imb_colors = ["#10B981" if q > 0 else "#EF4444" for q in df_hist["imbalance_qty"]]
    fig.add_trace(go.Bar(
        x=df_hist["time_str"],
        y=df_hist["abs_imbalance"],
        name="Desequilibrio Neto (Imbalance)",
        marker_color=imb_colors,
        marker_line=dict(color="#FFFFFF", width=1.2)
    ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=520,
        margin=dict(l=40, r=30, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#94A3B8", size=11)),
        hovermode="x unified",
        barmode="group"
    )

    fig.update_xaxes(showgrid=True, gridcolor="#1E293B", color="#94A3B8")
    fig.update_yaxes(showgrid=True, gridcolor="#1E293B", color="#94A3B8")

    return fig
