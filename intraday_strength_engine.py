"""
================================================================================
TRADINGVOLT • INTRADAY STRENGTH WATCH & BUBBLE MAP ENGINE (v2.0 VECTORIZED)
================================================================================
Motor Cuantitativo de Fuerza Intradía & Bubble Map conectado en tiempo real
a los Filtros Cuantitativos Actualizados (y no a universos estáticos):
  - Arrastra automáticamente las listas actualizadas de los 43 Filtros Oficiales,
    el Radar Activo Compartido y las ejecuciones en vivo de la sesión.
  - Procesamiento matricial vectorizado vía quant_data_pipeline (L1 RAM + L2
    Disco Cache) con telemetría de latencia en milisegundos.
================================================================================
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import quant_data_pipeline as qdp

# ----------------- BASE BENCHMARK DE RESPALDO OFFLINE -----------------
INTRADAY_BASE_STOCKS = [
    {"symbol": "RHI", "name": "Robert Half Inc.", "industry": "Staffing & Employment", "sector": "Industrials", "price": 68.40, "chg_today": 21.50, "chg_from_open": 8.70, "chg_from_high": -1.10, "chg_from_low": 12.40, "rvol_20d": 4.20, "run_rate_20d": 420.0, "pre_mkt_gap": 11.75, "post_mkt_chg": 0.45, "pct_from_vwap": 5.8, "rs_1m": 96, "rs_3m": 92, "dollar_vol_m": 185.0},
    {"symbol": "CART", "name": "Maplebear (Instacart)", "industry": "Internet Retail", "sector": "Consumer Discretionary", "price": 42.80, "chg_today": 9.20, "chg_from_open": 9.40, "chg_from_high": -0.60, "chg_from_low": 9.90, "rvol_20d": 3.80, "run_rate_20d": 380.0, "pre_mkt_gap": -0.18, "post_mkt_chg": 0.25, "pct_from_vwap": 4.9, "rs_1m": 94, "rs_3m": 95, "dollar_vol_m": 240.0},
    {"symbol": "PBF", "name": "PBF Energy Inc.", "industry": "Oil Refining", "sector": "Energy", "price": 81.50, "chg_today": 7.00, "chg_from_open": 7.44, "chg_from_high": -0.45, "chg_from_low": 7.90, "rvol_20d": 2.45, "run_rate_20d": 245.0, "pre_mkt_gap": -0.41, "post_mkt_chg": 0.15, "pct_from_vwap": 3.8, "rs_1m": 93, "rs_3m": 91, "dollar_vol_m": 165.0},
    {"symbol": "CRWD", "name": "CrowdStrike Holdings", "industry": "Cybersecurity Software", "sector": "Information Technology", "price": 315.00, "chg_today": 8.20, "chg_from_open": 7.10, "chg_from_high": -0.80, "chg_from_low": 8.50, "rvol_20d": 2.10, "run_rate_20d": 210.0, "pre_mkt_gap": 1.02, "post_mkt_chg": 0.32, "pct_from_vwap": 3.5, "rs_1m": 95, "rs_3m": 94, "dollar_vol_m": 420.0},
    {"symbol": "MPC", "name": "Marathon Petroleum", "industry": "Oil Refining & Marketing", "sector": "Energy", "price": 472.38, "chg_today": 3.32, "chg_from_open": 3.27, "chg_from_high": -0.35, "chg_from_low": 3.80, "rvol_20d": 1.85, "run_rate_20d": 185.0, "pre_mkt_gap": 0.05, "post_mkt_chg": 0.10, "pct_from_vwap": 1.9, "rs_1m": 91, "rs_3m": 94, "dollar_vol_m": 310.0},
    {"symbol": "FIGS", "name": "FIGS Inc.", "industry": "Healthcare Apparel", "sector": "Consumer Discretionary", "price": 20.54, "chg_today": 1.68, "chg_from_open": 1.53, "chg_from_high": -0.50, "chg_from_low": 2.20, "rvol_20d": 1.65, "run_rate_20d": 165.0, "pre_mkt_gap": 0.15, "post_mkt_chg": 0.05, "pct_from_vwap": 1.1, "rs_1m": 97, "rs_3m": 96, "dollar_vol_m": 48.0},
    {"symbol": "ZS", "name": "Zscaler Inc.", "industry": "Cybersecurity Software", "sector": "Information Technology", "price": 195.00, "chg_today": 7.31, "chg_from_open": 15.48, "chg_from_high": -0.90, "chg_from_low": 16.20, "rvol_20d": 2.65, "run_rate_20d": 265.0, "pre_mkt_gap": -7.11, "post_mkt_chg": 0.82, "pct_from_vwap": 4.2, "rs_1m": 90, "rs_3m": 88, "dollar_vol_m": 310.0},
    {"symbol": "TNGX", "name": "Tango Therapeutics", "industry": "Targeted Oncology", "sector": "Health Care", "price": 4.25, "chg_today": -16.80, "chg_from_open": -8.50, "chg_from_high": -17.20, "chg_from_low": 1.10, "rvol_20d": 3.80, "run_rate_20d": 380.0, "pre_mkt_gap": -9.07, "post_mkt_chg": -0.80, "pct_from_vwap": -6.2, "rs_1m": 35, "rs_3m": 42, "dollar_vol_m": 45.0}
]

METRIC_LABELS = {
    "chg_today": "Price % Change Today",
    "chg_from_open": "Price % Change from Open",
    "chg_from_high": "Price % Change from High",
    "chg_from_low": "Price % Change from Low",
    "pct_from_vwap": "% From Daily VWAP",
    "pre_mkt_gap": "Pre Market Gap %",
    "post_mkt_chg": "Post Market % Change",
    "rvol_20d": "Relative Volume - 20 Day (Adj)",
    "run_rate_20d": "Run Rate 20d (%)",
    "rs_1m": "Relative Strength - 1 Month",
    "rs_3m": "Relative Strength - 3 Month",
    "dollar_vol_m": "Volume in Dollars ($M)"
}


def get_available_filters_dict(session_state: Optional[Any] = None) -> Dict[str, Dict[str, Any]]:
    """
    Retorna el catálogo en vivo de Filtros Cuantitativos con sus listas actualizadas.
    """
    return qdp.get_updated_filters_catalog(session_state=session_state)


# Mantener alias de compatibilidad por si algún módulo externo lo referencia
TRADINGVOLT_UNIVERSES = {
    k: v["tickers"] for k, v in qdp.get_updated_filters_catalog().items()
}


def get_intraday_dataframe(
    universe_name: str = "",
    sector_filter: str = "All",
    search_query: str = "",
    sort_by: str = "chg_today",
    ascending: bool = False,
    custom_tickers: Optional[List[str]] = None,
    session_state: Optional[Any] = None,
    force_refresh: bool = False,
    max_tickers: int = 100
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Obtiene y calcula de forma vectorizada los datos intradía reales de la lista
    actualizada del filtro seleccionado.
    Retorna (df, telemetry_dict).
    """
    catalog = qdp.get_updated_filters_catalog(session_state=session_state)

    if custom_tickers and len(custom_tickers) > 0:
        selected_tickers = custom_tickers
        filter_meta = {
            "name": "✏️ Filtro / Lista Personalizada",
            "short_name": "Personalizado",
            "category": "Custom",
            "updated_at": datetime.now().strftime("%H:%M:%S")
        }
    elif universe_name in catalog:
        filter_meta = catalog[universe_name]
        selected_tickers = filter_meta["tickers"]
    else:
        # Buscar coincidencia parcial por nombre corto
        matched_key = next((k for k in catalog.keys() if universe_name in k or k in universe_name), None)
        if matched_key:
            filter_meta = catalog[matched_key]
            selected_tickers = filter_meta["tickers"]
        else:
            first_k = next(iter(catalog.keys()))
            filter_meta = catalog[first_k]
            selected_tickers = filter_meta["tickers"]

    df, telemetry = qdp.compute_vectorized_intraday_df(
        tickers=selected_tickers,
        force_refresh=force_refresh,
        max_tickers=max_tickers
    )

    if df.empty:
        # Fallback offline si no hay red
        df = pd.DataFrame(INTRADAY_BASE_STOCKS)
        telemetry = {
            "latency_ms": 0.5,
            "downloaded": 0,
            "cached": len(df),
            "total_tickers": len(df),
            "cache_timestamp": "Fallback"
        }

    telemetry["filter_name"] = filter_meta.get("short_name", universe_name)
    telemetry["filter_category"] = filter_meta.get("category", "Filtro")
    telemetry["filter_updated_at"] = filter_meta.get("updated_at", "Hoy")
    telemetry["filter_total_pool"] = len(selected_tickers)

    if sector_filter and sector_filter != "All":
        df = df[df["sector"] == sector_filter]

    if search_query and search_query.strip():
        q = search_query.upper().strip()
        df = df[
            df["symbol"].str.contains(q, na=False)
            | df["name"].str.upper().str.contains(q, na=False)
            | df["industry"].str.upper().str.contains(q, na=False)
        ]

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    return df.reset_index(drop=True), telemetry


def render_intraday_bubble_map(
    df: pd.DataFrame,
    x_metric: str = "chg_from_open",
    y_metric: str = "chg_today",
    size_metric: str = "rvol_20d",
    universe_label: str = "Filtro Activo",
    active_ticker: Optional[str] = None
) -> go.Figure:
    """
    Renderiza el Bubble Map Cuantitativo 4-Cuadrantes con colores institucionales
    según el cuadrante de fuerza intradía (Líderes, Reversión, Fading, Debilidad).
    """
    x_label = METRIC_LABELS.get(x_metric, x_metric)
    y_label = METRIC_LABELS.get(y_metric, y_metric)
    size_label = METRIC_LABELS.get(size_metric, size_metric)

    fig = go.Figure()

    if df.empty:
        fig.update_layout(
            paper_bgcolor="#080C14",
            plot_bgcolor="#080C14",
            height=640,
            annotations=[dict(text="Sin activos para los criterios seleccionados", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(color="#94A3B8", size=14))]
        )
        return fig

    raw_sizes = df[size_metric].fillna(1.0).values
    min_s, max_s = float(raw_sizes.min()), float(raw_sizes.max())
    if max_s > min_s:
        scaled_sizes = 14.0 + 36.0 * (raw_sizes - min_s) / (max_s - min_s)
    else:
        scaled_sizes = np.full_like(raw_sizes, 22.0, dtype=float)

    # Colores por cuadrante intradía:
    # Q1 (x>=0, y>=0): Líderes de Expansión -> Verde Esmeralda / Cian (#10B981)
    # Q2 (x<0, y>=0) o (x>=0, y<0 con x>=0 empuje desde open):
    #   Si x (vs open) >= 0 y y (chg today) < 0 -> Reversión Alcista desde Gap Down (#38BDF8)
    #   Si x (vs open) < 0 y y (chg today) >= 0 -> Fading Gapper (#F59E0B)
    #   Si x < 0 y y < 0 -> Presión Bajista (#F43F5E)
    bubble_colors = []
    border_colors = []
    quad_labels = []

    for _, row in df.iterrows():
        xv = float(row.get(x_metric, 0.0))
        yv = float(row.get(y_metric, 0.0))
        is_sel = (active_ticker and row["symbol"] == active_ticker)

        if xv >= 0 and yv >= 0:
            bubble_colors.append("rgba(16, 185, 129, 0.82)" if not is_sel else "rgba(0, 255, 135, 0.95)")
            border_colors.append("#FFFFFF" if is_sel else "#34D399")
            quad_labels.append("🟢 Líder de Expansión Intradía")
        elif xv >= 0 and yv < 0:
            bubble_colors.append("rgba(56, 189, 248, 0.82)")
            border_colors.append("#FFFFFF" if is_sel else "#7DD3FC")
            quad_labels.append("🔵 Reversión Alcista (Compras desde Open)")
        elif xv < 0 and yv >= 0:
            bubble_colors.append("rgba(245, 158, 11, 0.80)")
            border_colors.append("#FFFFFF" if is_sel else "#FBBF24")
            quad_labels.append("🟡 Gap Up Cediendo (Fading Gapper)")
        else:
            bubble_colors.append("rgba(244, 63, 94, 0.78)")
            border_colors.append("#FFFFFF" if is_sel else "#FB7185")
            quad_labels.append("🔴 Presión Vendedora Intradía")

    fig.add_trace(go.Scatter(
        x=df[x_metric],
        y=df[y_metric],
        mode="markers+text",
        marker=dict(
            size=scaled_sizes,
            color=bubble_colors,
            line=dict(color=border_colors, width=1.6),
            sizemode="diameter"
        ),
        text=df["symbol"],
        textposition="middle center",
        textfont=dict(size=10, color="#FFFFFF", family="JetBrains Mono, Arial Black, sans-serif"),
        customdata=np.stack((
            df["industry"],
            df["price"],
            df[size_metric],
            df["sector"],
            df["rvol_20d"],
            df["pre_mkt_gap"],
            quad_labels
        ), axis=-1),
        hovertemplate=(
            "<b>%{text}</b> • %{customdata[0]}<br>"
            "<span style='color:#94A3B8'>Sector: %{customdata[3]}</span><br>"
            "<b>%{customdata[6]}</b><br>"
            "────────────────────────<br>"
            f"{x_label}: <b>%{{x:+.2f}}%</b><br>"
            f"{y_label}: <b>%{{y:+.2f}}%</b><br>"
            "Pre-Market Gap: <b>%{customdata[5]:+.2f}%</b><br>"
            "RVOL (20d Adj): <b>%{customdata[4]:.2f}x</b><br>"
            f"{size_label}: <b>%{{customdata[2]:.2f}}</b><br>"
            "Precio Actual: <b>$%{customdata[1]:.2f}</b><extra></extra>"
        )
    ))

    # Líneas divisorias de cuadrantes (0, 0)
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(148, 163, 184, 0.45)", line_width=1.4)
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(148, 163, 184, 0.45)", line_width=1.4)

    # Etiquetas de los 4 cuadrantes
    fig.add_annotation(xref="paper", yref="paper", x=0.98, y=0.98,
                       text="<b>🟢 LÍDERES DE EXPANSIÓN</b><br><span style='font-size:10px'>Sobre Apertura & En Verde Hoy</span>",
                       showarrow=False, font=dict(color="#34D399", size=11, family="JetBrains Mono"), align="right")
    fig.add_annotation(xref="paper", yref="paper", x=0.02, y=0.98,
                       text="<b>🟡 FADING GAPPERS</b><br><span style='font-size:10px'>Gap Alcista pero Bajo Apertura</span>",
                       showarrow=False, font=dict(color="#FBBF24", size=11, family="JetBrains Mono"), align="left")
    fig.add_annotation(xref="paper", yref="paper", x=0.02, y=0.02,
                       text="<b>🔴 PRESIÓN BAJISTA</b><br><span style='font-size:10px'>En Rojo Hoy & Bajo Apertura</span>",
                       showarrow=False, font=dict(color="#FB7185", size=11, family="JetBrains Mono"), align="left")
    fig.add_annotation(xref="paper", yref="paper", x=0.98, y=0.02,
                       text="<b>🔵 REVERSIÓN ALCISTA</b><br><span style='font-size:10px'>Gap Bajista pero Empujando desde Open</span>",
                       showarrow=False, font=dict(color="#38BDF8", size=11, family="JetBrains Mono"), align="right")

    fig.update_layout(
        paper_bgcolor="#080C14",
        plot_bgcolor="#0B111E",
        height=640,
        margin=dict(l=45, r=30, t=28, b=45),
        xaxis=dict(
            title=dict(text=f"<b>{x_label}</b>", font=dict(color="#CBD5E1", size=12)),
            showgrid=True,
            gridcolor="rgba(30, 41, 59, 0.7)",
            zeroline=False,
            ticksuffix="%" if "rs_" not in x_metric else "",
            tickfont=dict(color="#94A3B8", family="JetBrains Mono", size=11)
        ),
        yaxis=dict(
            title=dict(text=f"<b>{y_label}</b>", font=dict(color="#CBD5E1", size=12)),
            showgrid=True,
            gridcolor="rgba(30, 41, 59, 0.7)",
            zeroline=False,
            ticksuffix="%" if "rs_" not in y_metric else "",
            tickfont=dict(color="#94A3B8", family="JetBrains Mono", size=11)
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor="#38BDF8",
            font=dict(family="JetBrains Mono", size=11.5, color="#F8FAFC")
        ),
        hovermode="closest",
        showlegend=False
    )

    return fig
