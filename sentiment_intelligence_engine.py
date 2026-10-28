"""
TradingVolt • Sentiment Intelligence Desk (NAAIM & AAII)
Reverse engineered from Deepvue Sentiment Intelligence Terminal.
Tracks NAAIM Active Manager Exposure Index overlay with SPY/QQQ benchmarks
and AAII Retail Investor Sentiment Surveys with historical spreads and Trader Read.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------- BENCHMARK DATA: NAAIM & AAII -----------------
NAAIM_DATA = {
    "current_index": 87.7,
    "stance": "Neutral",
    "last_report": "Oct 21, 2026",
    "percentile": "75%",
    "z_score": 0.72,
    "change_4w": -0.4,
    "historical_range": "13 - 108",
    "interpretation": "Exposure is not near a historical extreme, so the contrarian signal is neutral."
}

AAII_DATA = {
    "last_update": "Oct 19, 2026",
    "bullish": 38.7,
    "bullish_1w_chg": -1.8,
    "bearish": 41.6,
    "bearish_1w_chg": +2.8,
    "neutral": 19.7,
    "spread": -2.9,
    "spread_4w_chg": +21.6,
    "surveys": [
        {"date": "Oct 16", "bullish": 38.7, "neutral": 19.7, "bearish": 41.6, "spread": -2.9},
        {"date": "Oct 9", "bullish": 40.5, "neutral": 20.8, "bearish": 38.7, "spread": +1.8},
        {"date": "Oct 2", "bullish": 35.2, "neutral": 17.7, "bearish": 47.1, "spread": -11.9},
        {"date": "Sep 25", "bullish": 32.8, "neutral": 19.0, "bearish": 48.2, "spread": -15.4}
    ],
    "trader_read": (
        "Sentiment is broadly balanced. Neither optimism nor pessimism is unusually crowded. "
        "Week-over-week direction may be more useful than the absolute reading. "
        "Use AAII as context, not a standalone signal. Confirm extremes with price, breadth, and your risk process."
    )
}


def generate_naaim_timeseries(num_weeks: int = 156) -> pd.DataFrame:
    """
    Genera serie histórica del NAAIM Exposure Index comparada con SPY y QQQ
    a lo largo de los últimos 3 años (156 semanas).
    """
    np.random.seed(101)
    end_date = datetime(2026, 10, 21)
    dates = [end_date - timedelta(weeks=i) for i in range(num_weeks)]
    dates.reverse()
    
    # Simulación realista de SPY y QQQ en tendencia alcista secular
    t = np.linspace(0, 10, num_weeks)
    trend = 380 + 20 * t + 15 * np.sin(t)
    spy_prices = trend + np.random.normal(0, 4, num_weeks)
    qqq_prices = trend * 1.15 + np.random.normal(0, 6, num_weeks)
    
    # NAAIM Exposure oscilando entre 15 y 105
    naaim_base = 75 + 25 * np.sin(t * 1.5) + np.random.normal(0, 8, num_weeks)
    naaim = np.clip(naaim_base, 13.0, 108.0)
    naaim[-1] = 87.7
    
    df = pd.DataFrame({
        "Date": dates,
        "NAAIM": naaim,
        "SPY": spy_prices,
        "QQQ": qqq_prices
    }).set_index("Date")
    
    return df


def render_naaim_chart() -> go.Figure:
    """
    Genera el gráfico interactivo de la línea de exposición NAAIM
    superpuesta con los índices de referencia SPY y QQQ.
    """
    df = generate_naaim_timeseries()
    
    fig = go.Figure()
    
    # 1. NAAIM Exposure Line (Azul brillante)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['NAAIM'],
        name="NAAIM Exposure",
        line=dict(color="#38BDF8", width=2.0),
        yaxis="y1"
    ))
    
    # 2. SPY Benchmark (Naranja / Ámbar)
    # Normalizado para escala visual armónica
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SPY'],
        name="SPY (S&P 500)",
        line=dict(color="#FB923C", width=1.4),
        yaxis="y2"
    ))
    
    # 3. QQQ Benchmark (Azul cielo / Cian)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['QQQ'],
        name="QQQ (Nasdaq 100)",
        line=dict(color="#818CF8", width=1.2, dash="dot"),
        yaxis="y2"
    ))
    
    # Zonas de referencia de exposición
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(239, 68, 68, 0.4)", line_width=1, annotation_text="Overleveraged (>100)", annotation_position="top left")
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(34, 197, 94, 0.4)", line_width=1, annotation_text="Capitulation (<20)", annotation_position="bottom left")
    
    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=480,
        margin=dict(l=40, r=50, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            font=dict(color="#CBD5E1", size=12)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="Índice de Exposición NAAIM (%)", font=dict(color="#38BDF8", size=12)),
            tickfont=dict(color="#38BDF8"),
            showgrid=True,
            gridcolor="#1E293B",
            range=[0, 120]
        ),
        yaxis2=dict(
            title=dict(text="Precio Benchmarks (SPY / QQQ)", font=dict(color="#FB923C", size=12)),
            tickfont=dict(color="#FB923C"),
            overlaying="y",
            side="right",
            showgrid=False
        ),
        hovermode="x unified"
    )
    
    return fig


def render_aaii_horizontal_bars() -> go.Figure:
    """
    Genera el gráfico de barras horizontales apiladas de las últimas 4 encuestas AAII:
    Bullish (Verde), Neutral (Gris/Pizarra), Bearish (Rojo).
    """
    surveys = AAII_DATA["surveys"]
    dates = [s["date"] for s in surveys]
    bullish_vals = [s["bullish"] for s in surveys]
    neutral_vals = [s["neutral"] for s in surveys]
    bearish_vals = [s["bearish"] for s in surveys]
    spreads = [s["spread"] for s in surveys]
    
    fig = go.Figure()
    
    # 1. Bullish (Verde)
    fig.add_trace(go.Bar(
        y=dates,
        x=bullish_vals,
        name="Bullish",
        orientation='h',
        marker_color="#22C55E",
        text=[f"{v:.1f}%" for v in bullish_vals],
        textposition="inside",
        insidetextanchor="middle"
    ))
    
    # 2. Neutral (Pizarra)
    fig.add_trace(go.Bar(
        y=dates,
        x=neutral_vals,
        name="Neutral",
        orientation='h',
        marker_color="#64748B",
        text=[f"{v:.1f}%" for v in neutral_vals],
        textposition="inside",
        insidetextanchor="middle"
    ))
    
    # 3. Bearish (Rojo)
    fig.add_trace(go.Bar(
        y=dates,
        x=bearish_vals,
        name="Bearish",
        orientation='h',
        marker_color="#EF4444",
        text=[f"{v:.1f}%" for v in bearish_vals],
        textposition="inside",
        insidetextanchor="middle"
    ))
    
    # Anotaciones con el spread neto a la derecha
    for i, (d, sp) in enumerate(zip(dates, spreads)):
        sp_sign = "+" if sp > 0 else ""
        sp_color = "#22C55E" if sp > 0 else "#EF4444"
        fig.add_annotation(
            y=d,
            x=103,
            text=f"<span style='color:{sp_color}; font-weight:bold;'>{sp_sign}{sp:.1f}</span>",
            showarrow=False,
            font=dict(size=13)
        )
        
    fig.update_layout(
        barmode='stack',
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=260,
        margin=dict(l=60, r=50, t=25, b=25),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="left",
            x=0.01,
            font=dict(color="#CBD5E1", size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            range=[0, 110],
            ticksuffix="%"
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#E2E8F0", size=12)
        )
    )
    
    return fig
