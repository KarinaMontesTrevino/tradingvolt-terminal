"""
================================================================================
TRADINGVOLT • RELATIVE ROTATION GRAPHS (RRG ENGINE v2.0 MULTI-TIMEFRAME)
================================================================================
Motor Institucional Multi-Temporalidad de Rotación Relativa (Modelo Julius de
Kempenaer / StockCharts RRG):
  - Soporta múltiples temporalidades:
      1. 📅 3 Meses · Datos Diarios (Cola de 10 días de trading) - Corto Plazo
      2. 📆 1 Año · Datos Semanales (Cola de 10 semanas) - Medio/Largo Plazo
      3. ⚡ 1 Mes · Datos Horarios 1H (Cola de 10 horas) - Intradía Táctico
      4. 📊 6 Meses · Datos Diarios (Cola de 12 días) - Swing Intermedio
      5. 🏛️ 3 Años · Datos Mensuales (Cola de 6 meses) - Macro Secular
  - Alimentación directa desde cualquiera de los 43 Filtros Cuantitativos
    Actualizados, MTM WL de la Semana, Sectores GICS o ETFs Temáticos.
  - Mini-Gráfico Acompañante del Benchmark ($SPX / SPY / QQQ) con franja
    sombreada azul marcando exactamente la ventana de la cola (Tail Length).
  - Doble Tema Visual: Dark Neon Institutional y Classic StockCharts (Club).
================================================================================
"""

import os
import json
import math
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import quant_data_pipeline as qdp

# ----------------- UNIVERSOS DE ACTIVOS BASE -----------------

SPY_SECTORS = {
    "XLK": {"name": "Tecnología", "sector": "Information Technology", "color": "#00E8AA"},
    "XLC": {"name": "Servicios Comunicación", "sector": "Communication Services", "color": "#6366F1"},
    "XLY": {"name": "Consumo Discrecional", "sector": "Consumer Discretionary", "color": "#EC4899"},
    "XLF": {"name": "Finanzas", "sector": "Financials", "color": "#3B82F6"},
    "XLI": {"name": "Industriales", "sector": "Industrials", "color": "#10B981"},
    "XLE": {"name": "Energía", "sector": "Energy", "color": "#F59E0B"},
    "XLV": {"name": "Salud", "sector": "Health Care", "color": "#14B8A6"},
    "XLP": {"name": "Consumo Básico", "sector": "Consumer Staples", "color": "#8B5CF6"},
    "XLU": {"name": "Utilities", "sector": "Utilities", "color": "#EAB308"},
    "XLRE": {"name": "Inmobiliario", "sector": "Real Estate", "color": "#F97316"},
    "XLB": {"name": "Materiales Básicos", "sector": "Materials", "color": "#84CC16"}
}

THEMATIC_ETFS = {
    "SMH": {"name": "Semiconductores", "theme": "Semiconductors & Hardware", "color": "#22D3EE"},
    "IGV": {"name": "Software & SaaS", "theme": "Expanded Cloud & Enterprise Software", "color": "#38BDF8"},
    "XBI": {"name": "Biotecnología", "theme": "S&P Biotech High-Beta", "color": "#A855F7"},
    "XHB": {"name": "Constructoras", "theme": "Homebuilders & Housing", "color": "#F43F5E"},
    "KRE": {"name": "Banca Regional", "theme": "Regional Banking (Mid/Small)", "color": "#06B6D4"},
    "XRT": {"name": "Retail & Consumo", "theme": "Equal-Weight Retail", "color": "#F97316"},
    "ARKK": {"name": "Innovación Disruptiva", "theme": "Speculative Tech & Growth", "color": "#D946EF"},
    "TAN": {"name": "Energía Solar", "theme": "Clean & Renewable Energy", "color": "#EAB308"},
    "IWM": {"name": "Russell 2000", "theme": "Small Cap Growth/Value", "color": "#3B82F6"},
    "DIA": {"name": "Dow Jones Industrials", "theme": "Mega-Cap Blue Chips", "color": "#60A5FA"},
    "TLT": {"name": "Bonos Soberanos 20Y+", "theme": "Long Duration US Treasuries", "color": "#10B981"},
    "GLD": {"name": "Oro Físico", "theme": "Precious Metals & Real Assets", "color": "#FBBF24"},
    "USO": {"name": "Petróleo WTI", "theme": "Crude Oil Futures", "color": "#FB923C"},
    "IBIT": {"name": "Bitcoin Spot", "theme": "Crypto Assets", "color": "#F59E0B"}
}

CACHE_FILE = os.path.join(r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener", "rrg_cache.json")


def get_quadrant(rs_ratio: float, rs_mom: float) -> Tuple[str, str, str]:
    """Retorna (nombre_cuadrante, codigo_color, icono)."""
    if rs_ratio >= 100.0 and rs_mom >= 100.0:
        return "Líder", "#00FF87", "🟢"
    elif rs_ratio >= 100.0 and rs_mom < 100.0:
        return "Debilitándose", "#FFB300", "🟡"
    elif rs_ratio < 100.0 and rs_mom < 100.0:
        return "Rezagado", "#FF3366", "🔴"
    else:
        return "Mejorando", "#00D4FF", "🔵"


def calculate_heading_and_velocity(tail: List[List[float]]) -> Tuple[float, float, str]:
    if len(tail) < 2:
        return 0.0, 0.0, "Estable"
    p1 = tail[-2]
    p2 = tail[-1]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    velocity = math.sqrt(dx**2 + dy**2)
    angle_deg = math.degrees(math.atan2(dy, dx)) % 360.0
    if 0 <= angle_deg < 45 or 315 <= angle_deg < 360:
        direction = "Hacia Líder (Este-Noreste) ↗️"
    elif 45 <= angle_deg < 135:
        direction = "Aceleración Fuerte (Norte) ⬆️"
    elif 135 <= angle_deg < 225:
        direction = "Giro a Rezagado (Oeste) ⬅️"
    else:
        direction = "Pérdida de Impulso (Sur) ⬇️"
    return round(angle_deg, 1), round(velocity, 2), direction


def get_rrg_filter_options(session_state: Optional[Any] = None) -> Dict[str, Dict[str, Any]]:
    """
    Construye el catálogo de fuentes para RRG combinando:
      1. 📋 MTM WL de la Semana (Club RRG Leaders - 28 acciones)
      2. 🏢 Sectores S&P 500 (11 GICS)
      3. 🚀 ETFs Temáticos & Sub-Industrias (14 ETFs)
      4. Todos los Filtros Cuantitativos con Listas Actualizadas
    """
    options: Dict[str, Dict[str, Any]] = {
        "📋 MTM WL de la Semana (Club RRG Leaders • 28 activos)": {
            "type": "mtm_weekly",
            "tickers": qdp.MTM_WEEKLY_RRG_LEADERS,
            "custom_meta": None
        },
        "🏢 Sectores S&P 500 (11 GICS)": {
            "type": "sectors",
            "tickers": list(SPY_SECTORS.keys()),
            "custom_meta": SPY_SECTORS
        },
        "🚀 ETFs Temáticos & Sub-Industrias (14 ETFs)": {
            "type": "thematics",
            "tickers": list(THEMATIC_ETFS.keys()),
            "custom_meta": THEMATIC_ETFS
        }
    }

    filter_cat = qdp.get_updated_filters_catalog(session_state=session_state)
    for k, v in filter_cat.items():
        if "MTM WL" in k:
            continue
        options[f"⚡ Filtro: {k}"] = {
            "type": "filter",
            "tickers": v["tickers"],
            "custom_meta": None,
            "filter_info": v
        }

    return options


def fetch_and_compute_rrg(
    universe_type: str = "sectors",
    benchmark: str = "$SPX",
    window: int = 14,
    tail_len: int = 10,
    timeframe_key: str = "3m_1d",
    custom_tickers: Optional[List[str]] = None,
    force_refresh: bool = False,
    max_tickers: int = 40,
    session_state: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Calcula RRG Multi-Temporalidad usando el motor vectorizado quant_data_pipeline.
    Soporta Sectores, ETFs Temáticos, MTM WL de la Semana y cualquiera de los
    43 Filtros Cuantitativos Actualizados.
    """
    custom_meta = None
    if custom_tickers and len(custom_tickers) > 0:
        tickers = custom_tickers[:max_tickers]
    elif universe_type == "sectors":
        tickers = list(SPY_SECTORS.keys())
        custom_meta = SPY_SECTORS
    elif universe_type == "thematics":
        tickers = list(THEMATIC_ETFS.keys())
        custom_meta = THEMATIC_ETFS
    elif universe_type == "mtm_weekly":
        tickers = qdp.MTM_WEEKLY_RRG_LEADERS[:max_tickers]
    elif universe_type == "radar":
        try:
            import active_radar_engine as are
            tickers = are.get_active_radar_tickers(max_items=max_tickers)
        except Exception:
            tickers = qdp.MTM_WEEKLY_RRG_LEADERS[:max_tickers]
    else:
        # Buscar en el catálogo de filtros
        opts = get_rrg_filter_options(session_state=session_state)
        if universe_type in opts:
            tickers = opts[universe_type]["tickers"][:max_tickers]
            custom_meta = opts[universe_type].get("custom_meta")
        else:
            tickers = qdp.MTM_WEEKLY_RRG_LEADERS[:max_tickers]

    rrg_pack = qdp.compute_vectorized_rrg(
        tickers=tickers,
        benchmark=benchmark,
        timeframe_key=timeframe_key,
        tail_len=tail_len,
        force_refresh=force_refresh,
        max_tickers=max_tickers,
        custom_meta=custom_meta
    )

    if not rrg_pack.get("results"):
        return generate_default_rrg_dataset(universe_type, benchmark)

    rrg_pack["universe_type"] = universe_type
    return rrg_pack


def generate_default_rrg_dataset(universe_type: str = "sectors", benchmark: str = "SPY") -> dict:
    """Fallback offline si no hay conexión a red."""
    meta_dict = SPY_SECTORS if universe_type == "sectors" else THEMATIC_ETFS
    base_pts = {
        "XLK": {"r": 103.8, "m": 102.4, "tail": [[100.2, 99.1], [101.0, 100.2], [101.9, 101.0], [102.7, 101.7], [103.3, 102.1], [103.8, 102.4]]},
        "XLF": {"r": 101.5, "m": 103.1, "tail": [[98.8, 100.5], [99.4, 101.2], [100.0, 101.9], [100.6, 102.4], [101.1, 102.8], [101.5, 103.1]]},
        "XLE": {"r": 108.4, "m": 104.8, "tail": [[104.0, 101.5], [105.2, 102.4], [106.3, 103.2], [107.2, 103.9], [107.9, 104.4], [108.4, 104.8]]},
        "XLV": {"r": 104.2, "m": 97.8, "tail": [[106.5, 101.2], [106.0, 100.1], [105.5, 99.2], [105.0, 98.5], [104.6, 98.1], [104.2, 97.8]]},
        "XLI": {"r": 97.4, "m": 102.2, "tail": [[94.5, 98.5], [95.2, 99.4], [95.9, 100.3], [96.5, 101.1], [97.0, 101.7], [97.4, 102.2]]},
        "XLB": {"r": 96.2, "m": 96.8, "tail": [[99.1, 99.5], [98.4, 98.7], [97.7, 98.0], [97.1, 97.4], [96.6, 97.0], [96.2, 96.8]]}
    }
    results = {}
    tail_dates = ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"]
    for sym, item in base_pts.items():
        meta = meta_dict.get(sym, {})
        cur_r, cur_m = item["r"], item["m"]
        tail = item["tail"]
        quad, q_col, q_ico = get_quadrant(cur_r, cur_m)
        heading, vel, dir_label = calculate_heading_and_velocity(tail)
        results[sym] = {
            "symbol": sym,
            "name": meta.get("name", sym),
            "sector": meta.get("sector", "Sector"),
            "color": meta.get("color", q_col),
            "quadrant_color_neon": q_col,
            "quadrant_color_sc": q_col,
            "rs_ratio": cur_r,
            "rs_momentum": cur_m,
            "prev_ratio": tail[-2][0],
            "prev_mom": tail[-2][1],
            "quadrant": quad,
            "quadrant_en": "Leading" if quad == "Líder" else "Weakening",
            "quadrant_icon": q_ico,
            "quadrant_color": q_col,
            "prev_quadrant": quad,
            "quadrant_changed": False,
            "heading_deg": heading,
            "velocity": vel,
            "direction_label": dir_label,
            "perf_vs_bench_1w": 0.85,
            "perf_vs_bench_4w": 2.40,
            "tail": tail,
            "tail_dates": tail_dates
        }
    return {
        "universe_type": universe_type,
        "benchmark": benchmark,
        "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        "tail_len": 6,
        "results": results,
        "tail_dates": tail_dates,
        "bench_series": [5600, 5650, 5710, 5690, 5780, 5840],
        "bench_dates": tail_dates
    }


# ----------------- VISUALIZACIÓN INTERACTIVA PLOTLY (STOCKCHARTS & DARK NEON) -----------------

def build_plotly_rrg_chart(
    rrg_data: dict,
    show_tails: bool = True,
    tail_len: int = 10,
    height: int = 760,
    theme_style: str = "dark_neon",
    color_mode: str = "quadrant"
) -> go.Figure:
    """
    Construye el gráfico RRG interactivo con curvas spline suaves, estelas con nodos
    por sesión/semana y dos temas visuales:
      - 'stockcharts_light': Idéntico al formato institucional de StockCharts / Club
        de Inversionistas (cuadrantes pastel verde/amarillo/rojo/azul y curvas coloreadas
        según su cuadrante actual).
      - 'dark_neon': Estilo oscuro de alto contraste TradingVolt.
    """
    results = rrg_data.get("results", {})
    if not results:
        return go.Figure()

    bench = rrg_data.get("benchmark", "$SPX")
    tf_cfg = rrg_data.get("tf_config", {})
    tf_short = tf_cfg.get("short_label", "Daily")
    tail_unit = tf_cfg.get("tail_unit", "periods")

    all_x = [v["rs_ratio"] for v in results.values()]
    all_y = [v["rs_momentum"] for v in results.values()]
    for v in results.values():
        for pt in v.get("tail", [])[-(tail_len + 1):]:
            all_x.append(pt[0])
            all_y.append(pt[1])

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    pad_x = max(2.2, (max_x - min_x) * 0.10)
    pad_y = max(2.2, (max_y - min_y) * 0.10)
    x_range = [min(96.0, min_x - pad_x), max(104.0, max_x + pad_x)]
    y_range = [min(96.0, min_y - pad_y), max(104.0, max_y + pad_y)]

    is_light = (theme_style == "stockcharts_light")
    fig = go.Figure()

    if is_light:
        # Fondos pastel idénticos a las capturas de StockCharts / Club de Inversionistas
        q1_bg = "rgba(216, 243, 220, 0.55)"   # Leading (Verde pastel)
        q4_bg = "rgba(254, 243, 199, 0.55)"   # Weakening (Amarillo crema pastel)
        q3_bg = "rgba(254, 226, 226, 0.55)"   # Lagging (Rojo rosa pastel)
        q2_bg = "rgba(224, 231, 255, 0.55)"   # Improving (Azul lavanda pastel)
        paper_bg = "#F8FAFC"
        plot_bg = "#FFFFFF"
        axis_line_col = "rgba(71, 85, 105, 0.65)"
        grid_col = "rgba(148, 163, 184, 0.25)"
        tick_col = "#334155"
        label_text_col = "#0F172A"
        q_colors = {
            "Líder": "#15803D",         # Verde institucional fuerte
            "Debilitándose": "#D97706", # Amarillo/Oro oscuro
            "Rezagada": "#DC2626",      # Rojo vivo
            "Rezagado": "#DC2626",
            "Mejorando": "#2563EB"      # Azul intenso
        }
    else:
        q1_bg = "rgba(16, 185, 129, 0.11)"   # Leading (Verde oscuro institucional)
        q4_bg = "rgba(245, 158, 11, 0.10)"   # Weakening (Ámbar oscuro institucional)
        q3_bg = "rgba(244, 63, 94, 0.10)"    # Lagging (Carmesí oscuro institucional)
        q2_bg = "rgba(56, 189, 248, 0.11)"   # Improving (Azul cian oscuro institucional)
        paper_bg = "#0B0F19"
        plot_bg = "#0D1322"
        axis_line_col = "rgba(226, 232, 240, 0.38)"
        grid_col = "rgba(148, 163, 184, 0.10)"
        tick_col = "#94A3B8"
        label_text_col = "#F8FAFC"
        q_colors = {
            "Líder": "#00FF87",
            "Debilitándose": "#FBBF24",
            "Rezagada": "#FB7185",
            "Rezagado": "#FB7185",
            "Mejorando": "#38BDF8"
        }

    # 1. Cuadrantes sombreados
    fig.add_shape(type="rect", x0=100, y0=100, x1=x_range[1], y1=y_range[1], fillcolor=q1_bg, line_width=0, layer="below")
    fig.add_shape(type="rect", x0=100, y0=y_range[0], x1=x_range[1], y1=100, fillcolor=q4_bg, line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_range[0], y0=y_range[0], x1=100, y1=100, fillcolor=q3_bg, line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_range[0], y0=100, x1=100, y1=y_range[1], fillcolor=q2_bg, line_width=0, layer="below")

    # 2. Ejes centrales (100, 100)
    fig.add_shape(type="line", x0=100, y0=y_range[0], x1=100, y1=y_range[1],
                  line=dict(color=axis_line_col, width=1.4), layer="below")
    fig.add_shape(type="line", x0=x_range[0], y0=100, x1=x_range[1], y1=100,
                  line=dict(color=axis_line_col, width=1.4), layer="below")

    # 3. Etiquetas de las 4 esquinas
    fig.add_annotation(xref="paper", yref="paper", x=0.99, y=0.99,
                       text="<b>Leading (Líderes)</b>", showarrow=False,
                       font=dict(color=q_colors["Líder"], size=12, family="Inter, sans-serif"), xanchor="right", yanchor="top")
    fig.add_annotation(xref="paper", yref="paper", x=0.99, y=0.01,
                       text="<b>Weakening (Debilitándose)</b>", showarrow=False,
                       font=dict(color=q_colors["Debilitándose"], size=12, family="Inter, sans-serif"), xanchor="right", yanchor="bottom")
    fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.01,
                       text="<b>Lagging (Rezagadas)</b>", showarrow=False,
                       font=dict(color=q_colors["Rezagada"], size=12, family="Inter, sans-serif"), xanchor="left", yanchor="bottom")
    fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.99,
                       text="<b>Improving (Mejorando)</b>", showarrow=False,
                       font=dict(color=q_colors["Mejorando"], size=12, family="Inter, sans-serif"), xanchor="left", yanchor="top")

    # 4. Trazar cada activo (Curva Spline Suave + Nodos Intermedios + Cabeza con Etiqueta)
    for sym, item in results.items():
        quad = item["quadrant"]
        if color_mode == "quadrant":
            trace_color = q_colors.get(quad, item["color"])
        else:
            trace_color = item["color"]

        tail = item.get("tail", [])[-(tail_len + 1):]
        dates = item.get("tail_dates", [])[-(tail_len + 1):]

        if show_tails and len(tail) >= 2:
            tx = [p[0] for p in tail]
            ty = [p[1] for p in tail]

            # Línea curva orgánica (spline)
            fig.add_trace(go.Scatter(
                x=tx, y=ty,
                mode="lines+markers",
                line=dict(color=trace_color, width=2.6, shape="spline", smoothing=1.25),
                marker=dict(size=4.5, color=trace_color, opacity=0.65),
                hoverinfo="skip",
                showlegend=False,
                opacity=0.88
            ))

        cur_x = item["rs_ratio"]
        cur_y = item["rs_momentum"]

        hover_html = (
            f"<b>{sym} · {item['name']}</b><br>"
            f"Categoría: {item['sector']}<br>"
            f"Temporalidad: <b>{tf_short} (Cola: {tail_len} {tail_unit})</b><br>"
            f"────────────────────────────────<br>"
            f"Cuadrante: <b>{item['quadrant_icon']} {quad}</b><br>"
            f"JdK RS-Ratio: <b>{cur_x:.2f}</b><br>"
            f"JdK RS-Momentum: <b>{cur_y:.2f}</b><br>"
            f"Rumbo: <b>{item['heading_deg']}°</b> ({item['direction_label']})<br>"
            f"Perf vs {bench} (1p): <b>{item['perf_vs_bench_1w']:+.2f}%</b><br>"
            f"Perf vs {bench} (Cola): <b>{item['perf_vs_bench_4w']:+.2f}%</b>"
        )

        fig.add_trace(go.Scatter(
            x=[cur_x], y=[cur_y],
            mode="markers+text",
            marker=dict(
                size=9.5,
                color=trace_color,
                line=dict(width=1.8, color="#0F172A" if is_light else "#FFFFFF")
            ),
            text=[f" {sym}"],
            textposition="middle right",
            textfont=dict(size=10.5, color=label_text_col, family="JetBrains Mono, Arial, sans-serif"),
            name=f"{sym} ({quad})",
            hoverinfo="text",
            hovertext=hover_html,
            showlegend=False
        ))

    fig.update_layout(
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        height=height,
        margin=dict(l=48, r=28, t=24, b=45),
        xaxis=dict(
            title=dict(text=f"<b>JdK RS-Ratio</b> (vs {bench})", font=dict(size=11.5, color=tick_col)),
            range=x_range,
            showgrid=True,
            gridcolor=grid_col,
            zeroline=False,
            tickformat=".2f",
            tickfont=dict(color=tick_col, family="JetBrains Mono", size=10)
        ),
        yaxis=dict(
            title=dict(text="<b>JdK RS-Momentum</b>", font=dict(size=11.5, color=tick_col)),
            range=y_range,
            showgrid=True,
            gridcolor=grid_col,
            zeroline=False,
            tickformat=".2f",
            tickfont=dict(color=tick_col, family="JetBrains Mono", size=10)
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor="#38BDF8",
            font=dict(family="JetBrains Mono", size=11.5, color="#F8FAFC")
        ),
        hovermode="closest"
    )

    return fig


def build_benchmark_companion_chart(
    rrg_data: dict,
    theme_style: str = "dark_neon",
    height: int = 260
) -> go.Figure:
    """
    Construye el Mini-Gráfico lateral del Benchmark ($SPX / SPY / QQQ) idéntico a
    las capturas de StockCharts, sombreando en azul la ventana exacta de la cola
    (Tail Length, ej. 10 trading days o 10 weeks) y marcando el nivel actual.
    """
    bench = rrg_data.get("benchmark", "$SPX")
    vals = rrg_data.get("bench_series", [])
    dts = rrg_data.get("bench_dates", [])
    tail_len = int(rrg_data.get("tail_len", 10))
    is_light = (theme_style == "stockcharts_light")

    fig = go.Figure()
    if not vals or not dts:
        fig.update_layout(height=height, paper_bgcolor="#0A0E1A", plot_bgcolor="#0A0E1A")
        return fig

    paper_bg = "#F8FAFC" if is_light else "#0A0E1A"
    plot_bg = "#F1F5F9" if is_light else "#0F172A"
    line_col = "#1E293B" if is_light else "#E2E8F0"
    tail_line_col = "#2563EB" if is_light else "#38BDF8"
    tick_col = "#475569" if is_light else "#94A3B8"
    grid_col = "rgba(148, 163, 184, 0.3)" if is_light else "rgba(255, 255, 255, 0.07)"

    # Serie completa del periodo (ej. 3 meses o 1 año)
    fig.add_trace(go.Scatter(
        x=dts,
        y=vals,
        mode="lines",
        line=dict(color=line_col, width=1.6),
        fill="tozeroy",
        fillcolor="rgba(148, 163, 184, 0.22)" if is_light else "rgba(56, 189, 248, 0.08)",
        name=bench,
        hovertemplate=f"<b>{bench}</b><br>%{{x}}<br>Nivel: <b>%{{y:,.2f}}</b><extra></extra>"
    ))

    # Tramo final correspondiente a la cola (Tail Length) resaltado en azul
    t_idx = max(0, len(vals) - (tail_len + 1))
    fig.add_trace(go.Scatter(
        x=dts[t_idx:],
        y=vals[t_idx:],
        mode="lines",
        line=dict(color=tail_line_col, width=2.4),
        name=f"Cola ({tail_len})",
        hoverinfo="skip"
    ))

    # Franja vertical azul sombreando la ventana de la cola (Tail Length)
    fig.add_vrect(
        x0=dts[t_idx],
        x1=dts[-1],
        fillcolor="rgba(59, 130, 246, 0.22)" if is_light else "rgba(56, 189, 248, 0.18)",
        line_width=1,
        line_color=tail_line_col
    )

    # Línea horizontal azul del último cierre
    last_val = vals[-1]
    fig.add_hline(
        y=last_val,
        line_color=tail_line_col,
        line_width=1.2,
        annotation_text=f"<b>{last_val:,.2f}</b>",
        annotation_position="right",
        annotation_font=dict(color=tail_line_col, size=10, family="JetBrains Mono")
    )

    min_v, max_v = min(vals), max(vals)
    pad_v = max(1.0, (max_v - min_v) * 0.12)

    fig.update_layout(
        title=dict(text=f"<b>{bench}</b>", x=0.04, y=0.92, font=dict(size=12, color=tick_col, family="JetBrains Mono")),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        height=height,
        margin=dict(l=12, r=52, t=28, b=24),
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_col,
            nticks=5,
            tickfont=dict(size=9.5, color=tick_col, family="JetBrains Mono")
        ),
        yaxis=dict(
            range=[min_v - pad_v, max_v + pad_v],
            side="right",
            showgrid=True,
            gridcolor=grid_col,
            tickfont=dict(size=9.5, color=tick_col, family="JetBrains Mono")
        ),
        showlegend=False
    )

    return fig


def build_transition_matrix_df(rrg_data: dict) -> pd.DataFrame:
    """Genera DataFrame ordenable de análisis táctico por cuadrante y velocidad."""
    results = rrg_data.get("results", {})
    rows = []
    for sym, item in results.items():
        rows.append({
            "Símbolo": sym,
            "Nombre": item["name"],
            "Categoría": item["sector"],
            "Cuadrante": f"{item['quadrant_icon']} {item['quadrant']}",
            "RS-Ratio": item["rs_ratio"],
            "RS-Momentum": item["rs_momentum"],
            "Rumbo (°)": item["heading_deg"],
            "Velocidad": item["velocity"],
            "Dirección": item["direction_label"],
            "Perf vs Bench (1p)": f"{item['perf_vs_bench_1w']:+.2f}%",
            "Perf vs Bench (Cola)": f"{item['perf_vs_bench_4w']:+.2f}%",
            "Giro": "⚡ Cambio de Cuadrante" if item["quadrant_changed"] else "Continuación"
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by=["RS-Ratio", "RS-Momentum"], ascending=[False, False])
    return df


def build_animated_svg_player(rrg_data: dict, height: int = 780) -> str:
    """
    Genera el reproductor interactivo HTML/SVG nativo con Play/Pause (▶),
    slider temporal de pasos de la cola, hover tooltips y estelas trazadas.
    """
    results = rrg_data.get("results", {})
    if not results:
        return "<div>No hay datos RRG</div>"

    bench = rrg_data.get("benchmark", "$SPX")
    dates = rrg_data.get("tail_dates", [])
    if not dates:
        dates = [f"Paso {i+1}" for i in range(10)]

    series_dict = {}
    col_dict = {}
    name_dict = {}
    all_x, all_y = [], []

    for sym, item in results.items():
        col_dict[sym] = item.get("quadrant_color_neon", item["color"])
        name_dict[sym] = item["name"]
        pts = item.get("tail", [])
        series_dict[sym] = pts
        for p in pts:
            all_x.append(p[0])
            all_y.append(p[1])

    min_x, max_x = min(all_x or [90]), max(all_x or [110])
    min_y, max_y = min(all_y or [90]), max(all_y or [110])
    span = max(abs(100.0 - min_x), abs(max_x - 100.0), abs(100.0 - min_y), abs(max_y - 100.0)) + 2.5
    xlo, xhi = round(100.0 - span, 1), round(100.0 + span, 1)
    ylo, yhi = round(100.0 - span, 1), round(100.0 + span, 1)
    svg_max_h = max(500, height - 120)

    json_str = json.dumps({
        "W": 960, "H": 660, "pad": 48,
        "xlo": xlo, "xhi": xhi, "ylo": ylo, "yhi": yhi,
        "tail": len(dates), "labels": dates,
        "series": series_dict, "col": col_dict, "name": name_dict
    })
    num_steps = max(1, len(dates) - 1)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      html, body {{ margin:0; padding:6px 10px; background:#0A0E1A; color:#E2E8F0; font-family:sans-serif; overflow:hidden; }}
      .rrgbox {{ background:#0B101D; border:1px solid #1E293B; border-radius:12px; padding:12px 16px; }}
      .rrgctl {{ display:flex; align-items:center; gap:14px; margin-bottom:10px; }}
      .rrgctl input[type=range] {{ flex:1; accent-color:#00F0FF; cursor:pointer; }}
      .rrgplay {{ font-family:monospace; font-size:13px; font-weight:700; background:rgba(0,240,255,0.12); color:#00F0FF; border:1px solid rgba(0,240,255,0.4); border-radius:6px; padding:5px 16px; cursor:pointer; }}
      #rrgsvg {{ display:block; width:100%; height:auto; max-height:{svg_max_h}px; margin:0 auto; }}
    </style>
    </head>
    <body>
    <div class="rrgbox">
      <div class="rrgctl">
        <button type="button" class="rrgplay" id="rrgplay">▶ Play</button>
        <input type="range" id="rrgweek" min="0" max="{num_steps}" value="{num_steps}" step="1">
        <span id="rrgweeklbl" style="color:#00F0FF;font-family:monospace;font-weight:700;">{dates[-1]}</span>
      </div>
      <svg id="rrgsvg" viewBox="0 0 960 660" preserveAspectRatio="xMidYMid meet">
        <rect x="480" y="48" width="432" height="282" fill="rgba(0,232,170,0.07)"/>
        <rect x="480" y="330" width="432" height="282" fill="rgba(255,179,0,0.06)"/>
        <rect x="48" y="330" width="432" height="282" fill="rgba(255,51,102,0.06)"/>
        <rect x="48" y="48" width="432" height="282" fill="rgba(0,212,255,0.06)"/>
        <line x1="480" y1="48" x2="480" y2="612" stroke="rgba(255,255,255,0.25)" stroke-dasharray="4,4"/>
        <line x1="48" y1="330" x2="912" y2="330" stroke="rgba(255,255,255,0.25)" stroke-dasharray="4,4"/>
        <text x="896" y="72" fill="#00FF87" font-size="13" text-anchor="end" font-weight="800" font-family="monospace">LEADING (LÍDERES) ▲</text>
        <text x="896" y="596" fill="#FFB300" font-size="13" text-anchor="end" font-weight="800" font-family="monospace">WEAKENING (DEBILITÁNDOSE) ▼</text>
        <text x="64" y="596" fill="#FF3366" font-size="13" font-weight="800" font-family="monospace">LAGGING (REZAGADAS) ▼</text>
        <text x="64" y="72" fill="#00D4FF" font-size="13" font-weight="800" font-family="monospace">IMPROVING (MEJORANDO) ▲</text>
        <circle cx="480" cy="330" r="5" fill="#00F0FF" stroke="#FFFFFF" stroke-width="2"/>
        <text x="488" y="324" fill="#00F0FF" font-size="11" font-weight="800" font-family="monospace">{bench}</text>
        <g id="rrgdyn"></g>
      </svg>
    </div>
    <script id="rrgdata" type="application/json">{json_str}</script>
    <script>
    (function() {{
      var D = JSON.parse(document.getElementById('rrgdata').textContent);
      var dyn = document.getElementById('rrgdyn'), slider = document.getElementById('rrgweek'),
          lbl = document.getElementById('rrgweeklbl'), play = document.getElementById('rrgplay');
      function X(v) {{ return D.pad + (v - D.xlo) / (D.xhi - D.xlo) * (D.W - 2 * D.pad); }}
      function Y(v) {{ return D.pad + (D.yhi - v) / (D.yhi - D.ylo) * (D.H - 2 * D.pad); }}
      function draw(idx) {{
        lbl.textContent = D.labels[idx] || ('Paso ' + idx);
        var out = '';
        for (var s in D.series) {{
          var arr = D.series[s], c = D.col[s], pts = [];
          for (var i = 0; i <= idx; i++) {{ if (arr[i]) pts.push(arr[i]); }}
          if (!pts.length) continue;
          var poly = pts.map(function(pp) {{ return X(pp[0]).toFixed(1) + ',' + Y(pp[1]).toFixed(1); }}).join(' ');
          var L = pts[pts.length - 1];
          out += '<g>';
          if (pts.length > 1) {{
            out += '<polyline points="' + poly + '" fill="none" stroke="' + c + '" stroke-width="2.6" opacity="0.8"/>';
            for (var j = 0; j < pts.length - 1; j++) {{
              out += '<circle cx="' + X(pts[j][0]).toFixed(1) + '" cy="' + Y(pts[j][1]).toFixed(1) + '" r="3.5" fill="' + c + '" opacity="0.55"/>';
            }}
          }}
          var lx = X(L[0]), ly = Y(L[1]);
          out += '<circle cx="' + lx.toFixed(1) + '" cy="' + ly.toFixed(1) + '" r="6" fill="' + c + '" stroke="#050811" stroke-width="1.8"/>';
          out += '<text x="' + (lx + 8).toFixed(1) + '" y="' + (ly + 4).toFixed(1) + '" fill="#FFFFFF" font-size="11" font-weight="700" font-family="monospace">' + s + '</text>';
          out += '</g>';
        }}
        dyn.innerHTML = out;
      }}
      slider.addEventListener('input', function() {{ draw(parseInt(this.value, 10)); }});
      draw(parseInt(slider.value, 10));
      var timer = null;
      play.addEventListener('click', function() {{
        if (timer) {{ clearInterval(timer); timer = null; play.textContent = '▶ Play'; }}
        else {{
          play.textContent = '⏸ Pause';
          timer = setInterval(function() {{
            var v = parseInt(slider.value, 10);
            v = (v >= D.labels.length - 1) ? 0 : v + 1;
            slider.value = v; draw(v);
          }}, 650);
        }}
      }});
    }})();
    </script>
    </body>
    </html>
    """
