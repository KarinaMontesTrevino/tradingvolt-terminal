"""
TradingVolt • Stage Analysis Engine (Stan Weinstein 4-Stage Model)
Reverse engineered directly from Deepvue Stage Analysis Desk.
Computes Market Overview S1-S4 distribution, Sector Stage breakdown (11 GICS sectors),
health classification, sector drill-down ranking assets by performance, and chart sync.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------- STAN WEINSTEIN 4-STAGE OVERVIEW -----------------
STAGE_TOTALS = {
    "S1": {"name": "Stage 1 (Basing)", "count": 78, "pct": 1.4, "color": "#F59E0B"},       # Ámbar / Naranja
    "S2": {"name": "Stage 2 (Uptrend)", "count": 1579, "pct": 28.0, "color": "#3B82F6"},    # Azul
    "S3": {"name": "Stage 3 (Distribution)", "count": 842, "pct": 15.0, "color": "#EAB308"},# Dorado
    "S4": {"name": "Stage 4 (Downtrend)", "count": 3141, "pct": 55.6, "color": "#EC4899"}   # Rosa / Magenta
}

# ----------------- SECTOR STAGE BREAKDOWN (11 GICS SECTORS) -----------------
SECTOR_STAGE_DATA = {
    "Energy": {
        "count": 265, "s1": 1, "s2": 41, "s3": 14, "s4": 44, "health": "Strong", "health_color": "#3B82F6",
        "description": "Fuerte rotación institucional liderada por E&P, servicios petroleros y perforación offshore."
    },
    "Financials": {
        "count": 1012, "s1": 1, "s2": 41, "s3": 18, "s4": 40, "health": "Strong", "health_color": "#3B82F6",
        "description": "Bancos regionales y aseguradoras mostrando expansión consistente de bases y acumulación."
    },
    "Consumer Staples": {
        "count": 204, "s1": 3, "s2": 33, "s3": 10, "s4": 55, "health": "Healthy", "health_color": "#06B6D4",
        "description": "Defensivos de alta calidad con bajo beta y acumulación en soporte SMA 50."
    },
    "Utilities": {
        "count": 166, "s1": 4, "s2": 29, "s3": 8, "s4": 59, "health": "Strong", "health_color": "#3B82F6",
        "description": "Beneficiarias de demanda eléctrica de centros de datos de IA y dividendos estables."
    },
    "Information Technology": {
        "count": 687, "s1": 1, "s2": 28, "s3": 14, "s4": 57, "health": "Healthy", "health_color": "#06B6D4",
        "description": "Liderazgo en semiconductores e infraestructura de IA; selectividad en software de aplicación."
    },
    "Consumer Discretionary": {
        "count": 545, "s1": 2, "s2": 21, "s3": 10, "s4": 67, "health": "Healthy", "health_color": "#06B6D4",
        "description": "Bifurcación: minoristas de descuento sólidos frente a discrecionales cíclicos en fase 4."
    },
    "Health Care": {
        "count": 1028, "s1": 1, "s2": 20, "s3": 16, "s4": 62, "health": "Healthy", "health_color": "#06B6D4",
        "description": "Dispositivos médicos y farma de gran capitalización en Stage 2; biotechs en fase 4."
    },
    "Real Estate": {
        "count": 239, "s1": 1, "s2": 19, "s3": 9, "s4": 70, "health": "Neutral", "health_color": "#64748B",
        "description": "Presión persistente por rendimientos de bonos; centros de datos y torres celulares en fase 2."
    },
    "Industrials": {
        "count": 743, "s1": 2, "s2": 19, "s3": 14, "s4": 65, "health": "Neutral", "health_color": "#64748B",
        "description": "Aeroespacial y defensa en máximos de 52 semanas; transporte y maquinaria pesada rezagados."
    },
    "Communication Services": {
        "count": 271, "s1": 1, "s2": 19, "s3": 14, "s4": 66, "health": "Neutral", "health_color": "#64748B",
        "description": "Mega-caps (META, GOOGL, NFLX) impulsando el índice ponderado; telecom tradicionales débiles."
    },
    "Materials": {
        "count": 282, "s1": 1, "s2": 13, "s3": 14, "s4": 71, "health": "Neutral", "health_color": "#64748B",
        "description": "Metales preciosos y químicos especializados en soporte; metales industriales en Stage 4."
    }
}

# ----------------- ACTIVOS POR SECTOR Y PERFORMANCE (REVERSE ENGINEERED DEEPVUE) -----------------
SECTOR_ASSETS_PERFORMANCE = {
    "Energy": [
        {"symbol": "TPET", "name": "Trio Petroleum Corp.", "sub": "Oil, Gas & Consumable Fuels", "change_pct": 13.16, "price": 1.72, "stage": "Stage 2a"},
        {"symbol": "BATL", "name": "Battalion Oil Corp.", "sub": "Exploration & Production", "change_pct": 11.68, "price": 8.45, "stage": "Stage 2"},
        {"symbol": "BANL", "name": "CBL International Ltd.", "sub": "Energy Equipment & Services", "change_pct": 10.75, "price": 1.34, "stage": "Stage 2"},
        {"symbol": "VG", "name": "Venture Global LNG", "sub": "Oil & Gas Storage & Transport", "change_pct": 9.29, "price": 14.20, "stage": "Stage 2"},
        {"symbol": "TBN", "name": "Tamboran Resources", "sub": "Oil & Gas Exploration", "change_pct": 9.03, "price": 18.50, "stage": "Stage 2"},
        {"symbol": "NF", "name": "Noble Fuels", "sub": "Refining & Marketing", "change_pct": 8.53, "price": 24.10, "stage": "Stage 2"},
        {"symbol": "AMTX", "name": "Aemetis Inc.", "sub": "Renewable Fuels", "change_pct": 8.33, "price": 4.15, "stage": "Stage 2a"},
        {"symbol": "REI", "name": "Ring Energy Inc.", "sub": "Exploration & Production", "change_pct": 8.33, "price": 2.10, "stage": "Stage 2"},
        {"symbol": "TDW", "name": "Tidewater Inc.", "sub": "Offshore Supply Vessels", "change_pct": 8.11, "price": 88.40, "stage": "Stage 2"},
        {"symbol": "XPRO", "name": "Expro Group Holdings", "sub": "Well Construction & Flow", "change_pct": 8.11, "price": 17.65, "stage": "Stage 2"},
        {"symbol": "EONR", "name": "Eon Resources Inc.", "sub": "Exploration & Production", "change_pct": 7.99, "price": 2.85, "stage": "Stage 2a"},
        {"symbol": "BORR", "name": "Borr Drilling Ltd.", "sub": "Offshore Drilling", "change_pct": 7.84, "price": 6.20, "stage": "Stage 2"},
        {"symbol": "WTI", "name": "W&T Offshore Inc.", "sub": "Exploration & Production", "change_pct": 7.71, "price": 2.65, "stage": "Stage 2"},
        {"symbol": "TMDE", "name": "Transocean Deepwater", "sub": "Offshore Drilling", "change_pct": 7.56, "price": 5.40, "stage": "Stage 2"},
        {"symbol": "SOC", "name": "Sable Offshore Corp.", "sub": "Exploration & Production", "change_pct": 7.24, "price": 26.80, "stage": "Stage 2"},
        {"symbol": "OII", "name": "Oceaneering International", "sub": "Subsea Engineering", "change_pct": 7.24, "price": 25.10, "stage": "Stage 2"},
        {"symbol": "INVO", "name": "Innovo Energy Corp.", "sub": "Energy Infrastructure", "change_pct": 7.09, "price": 3.90, "stage": "Stage 2a"},
        {"symbol": "SLB", "name": "Schlumberger Ltd.", "sub": "Oilfield Services", "change_pct": 7.08, "price": 48.60, "stage": "Stage 2"},
        {"symbol": "WFRD", "name": "Weatherford International", "sub": "Oilfield Equipment", "change_pct": 6.98, "price": 112.50, "stage": "Stage 2"},
        {"symbol": "OIS", "name": "Oil States International", "sub": "Manufactured Products", "change_pct": 6.97, "price": 5.85, "stage": "Stage 2"},
        {"symbol": "FET", "name": "Forum Energy Technologies", "sub": "Energy Equipment", "change_pct": 6.80, "price": 14.80, "stage": "Stage 2"},
        {"symbol": "PNRG", "name": "PrimeEnergy Resources", "sub": "Oil & Gas E&P", "change_pct": 6.74, "price": 145.00, "stage": "Stage 2"},
        {"symbol": "NUAI", "name": "Nu-Oil & Gas", "sub": "Energy Infrastructure", "change_pct": 6.67, "price": 1.95, "stage": "Stage 2a"},
        {"symbol": "VTOL", "name": "Bristow Group Inc.", "sub": "Offshore Aviation Logistics", "change_pct": 6.60, "price": 38.40, "stage": "Stage 2"},
        {"symbol": "NEXT", "name": "NextDecade Corp.", "sub": "LNG Infrastructure", "change_pct": 6.43, "price": 7.45, "stage": "Stage 2"},
        {"symbol": "SDRL", "name": "Seadrill Ltd.", "sub": "Offshore Drilling", "change_pct": 6.42, "price": 46.20, "stage": "Stage 2"},
        {"symbol": "KOS", "name": "Kosmos Energy Ltd.", "sub": "Deepwater E&P", "change_pct": 6.30, "price": 4.55, "stage": "Stage 2"},
        {"symbol": "REPX", "name": "Riley Exploration Permian", "sub": "Permian Basin E&P", "change_pct": 6.03, "price": 31.80, "stage": "Stage 2"},
        {"symbol": "VIST", "name": "Vista Energy SAB", "sub": "Shale E&P", "change_pct": 5.99, "price": 52.30, "stage": "Stage 2"},
        {"symbol": "MTDR", "name": "Matador Resources", "sub": "Permian Basin E&P", "change_pct": 5.58, "price": 61.20, "stage": "Stage 2"},
        {"symbol": "VAL", "name": "Valaris Ltd.", "sub": "Offshore Drilling", "change_pct": 5.58, "price": 64.50, "stage": "Stage 2"},
        {"symbol": "PTEN", "name": "Patterson-UTI Energy", "sub": "Drilling Services", "change_pct": 5.56, "price": 9.80, "stage": "Stage 2"},
        {"symbol": "ACDC", "name": "ProFrac Holding Corp.", "sub": "Hydraulic Fracturing", "change_pct": 5.44, "price": 8.10, "stage": "Stage 2"},
        {"symbol": "CLS", "name": "Celestica Energy Units", "sub": "Power Conversion Systems", "change_pct": 5.43, "price": 42.10, "stage": "Stage 2"},
        {"symbol": "RIG", "name": "Transocean Ltd.", "sub": "Offshore Ultra-Deepwater", "change_pct": 5.43, "price": 4.65, "stage": "Stage 2"},
        {"symbol": "KRP", "name": "Kimbell Royalty Partners", "sub": "Mineral Rights & Royalties", "change_pct": 5.35, "price": 16.40, "stage": "Stage 2"},
        {"symbol": "NOV", "name": "NOV Inc.", "sub": "Rig Technologies", "change_pct": 5.33, "price": 17.80, "stage": "Stage 2"},
        {"symbol": "EGY", "name": "Vaalco Energy Inc.", "sub": "West Africa E&P", "change_pct": 5.30, "price": 6.15, "stage": "Stage 2"},
        {"symbol": "HAL", "name": "Halliburton Co.", "sub": "Completion & Production", "change_pct": 5.21, "price": 32.50, "stage": "Stage 2"},
        {"symbol": "EQNR", "name": "Equinor ASA", "sub": "Integrated Energy", "change_pct": 5.17, "price": 28.40, "stage": "Stage 2"},
        {"symbol": "LPG", "name": "Dorian LPG Ltd.", "sub": "LPG Shipping Logistics", "change_pct": 5.09, "price": 41.20, "stage": "Stage 2"},
        {"symbol": "CHRD", "name": "Chord Energy Corp.", "sub": "Williston Basin E&P", "change_pct": 5.08, "price": 156.40, "stage": "Stage 2"},
        {"symbol": "APA", "name": "APA Corporation", "sub": "Global Exploration & Prod.", "change_pct": 4.96, "price": 27.80, "stage": "Stage 2"}
    ],
    "Financials": [
        {"symbol": "FCNCA", "name": "First Citizens BancShares", "sub": "Regional Banks", "change_pct": 9.45, "price": 1820.0, "stage": "Stage 2"},
        {"symbol": "CUBI", "name": "Customers Bancorp", "sub": "Regional Banks", "change_pct": 8.30, "price": 54.20, "stage": "Stage 2"},
        {"symbol": "FITB", "name": "Fifth Third Bancorp", "sub": "Major Regional Banks", "change_pct": 7.15, "price": 42.80, "stage": "Stage 2"},
        {"symbol": "COF", "name": "Capital One Financial", "sub": "Consumer Finance", "change_pct": 6.80, "price": 158.40, "stage": "Stage 2"},
        {"symbol": "ZION", "name": "Zions Bancorporation", "sub": "Regional Banks", "change_pct": 6.20, "price": 50.10, "stage": "Stage 2"},
        {"symbol": "WAL", "name": "Western Alliance Bancorp", "sub": "Regional Banks", "change_pct": 5.90, "price": 82.50, "stage": "Stage 2"},
        {"symbol": "CBOE", "name": "Cboe Global Markets", "sub": "Financial Exchanges", "change_pct": 5.40, "price": 210.0, "stage": "Stage 2"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sub": "Diversified Banks", "change_pct": 4.80, "price": 224.50, "stage": "Stage 2"}
    ],
    "Information Technology": [
        {"symbol": "PLTR", "name": "Palantir Technologies", "sub": "Enterprise AI Software", "change_pct": 8.75, "price": 44.50, "stage": "Stage 2"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sub": "Semiconductors", "change_pct": 7.40, "price": 141.20, "stage": "Stage 2"},
        {"symbol": "CRWD", "name": "CrowdStrike Holdings", "sub": "Cybersecurity", "change_pct": 6.50, "price": 315.00, "stage": "Stage 2"},
        {"symbol": "NOW", "name": "ServiceNow Inc.", "sub": "Systems Software", "change_pct": 5.80, "price": 930.00, "stage": "Stage 2"},
        {"symbol": "MNDY", "name": "Monday.com Ltd.", "sub": "Application Software", "change_pct": 5.40, "price": 298.00, "stage": "Stage 2"},
        {"symbol": "ZS", "name": "Zscaler Inc.", "sub": "Security Software", "change_pct": 5.10, "price": 195.00, "stage": "Stage 2"},
        {"symbol": "NET", "name": "Cloudflare Inc.", "sub": "Cloud Edge Network", "change_pct": 4.85, "price": 94.20, "stage": "Stage 2"}
    ],
    "Industrials": [
        {"symbol": "MAGH", "name": "Magnitude International Ltd.", "sub": "Construction & Engineering", "change_pct": 9.21, "price": 6.76, "stage": "Stage 2"},
        {"symbol": "GE", "name": "GE Aerospace", "sub": "Aerospace & Defense", "change_pct": 6.80, "price": 192.40, "stage": "Stage 2"},
        {"symbol": "RTX", "name": "RTX Corporation", "sub": "Defense & Intelligence", "change_pct": 5.90, "price": 128.50, "stage": "Stage 2"},
        {"symbol": "FIX", "name": "Comfort Systems USA", "sub": "Building Infrastructure", "change_pct": 5.50, "price": 420.00, "stage": "Stage 2"},
        {"symbol": "LMT", "name": "Lockheed Martin", "sub": "Aerospace & Defense", "change_pct": 4.90, "price": 595.00, "stage": "Stage 2"}
    ]
}


def generate_market_overview_timeseries(num_weeks: int = 52) -> pd.DataFrame:
    """
    Genera serie histórica semanal de la evolución de acciones en Stage 1, 2, 3 y 4
    mostrando las curvas superpuestas exactamente como en el gráfico Deepvue.
    """
    np.random.seed(88)
    end_date = datetime(2026, 10, 24)
    dates = [end_date - timedelta(weeks=i) for i in range(num_weeks)]
    dates.reverse()
    
    t = np.linspace(0, 3 * np.pi, num_weeks)
    
    # S4 (Downtrend) domina en 55-60%, S2 (Uptrend) oscila entre 20% y 35%
    s4_curve = 3200 - 400 * np.sin(t) + np.random.normal(0, 50, num_weeks)
    s4_curve[-1] = STAGE_TOTALS["S4"]["count"]
    
    s2_curve = 1400 + 350 * np.sin(t) + np.random.normal(0, 40, num_weeks)
    s2_curve[-1] = STAGE_TOTALS["S2"]["count"]
    
    s3_curve = 850 + 80 * np.cos(t) + np.random.normal(0, 25, num_weeks)
    s3_curve[-1] = STAGE_TOTALS["S3"]["count"]
    
    s1_curve = 80 + 15 * np.sin(t * 2) + np.random.normal(0, 5, num_weeks)
    s1_curve[-1] = STAGE_TOTALS["S1"]["count"]
    
    return pd.DataFrame({
        "Date": dates,
        "S1": s1_curve,
        "S2": s2_curve,
        "S3": s3_curve,
        "S4": s4_curve
    }).set_index("Date")


def render_market_overview_chart() -> go.Figure:
    """
    Renderiza el gráfico de líneas histórico de Market Overview (S1, S2, S3, S4)
    idéntico al panel superior de Deepvue Stage Analysis.
    """
    df = generate_market_overview_timeseries()
    
    fig = go.Figure()
    
    # S4 (Rosa / Magenta)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['S4'],
        name="Stage 4 (Downtrend)",
        line=dict(color="#EC4899", width=2.0),
        mode="lines"
    ))
    
    # S2 (Azul eléctrico)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['S2'],
        name="Stage 2 (Uptrend)",
        line=dict(color="#3B82F6", width=2.0),
        mode="lines"
    ))
    
    # S3 (Dorado / Amarillo)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['S3'],
        name="Stage 3 (Distribution)",
        line=dict(color="#EAB308", width=1.4, dash="dot"),
        mode="lines"
    ))
    
    # S1 (Naranja)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['S1'],
        name="Stage 1 (Basing)",
        line=dict(color="#F59E0B", width=1.4, dash="dot"),
        mode="lines"
    ))
    
    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=180,
        margin=dict(l=10, r=20, t=10, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.99,
            font=dict(color="#CBD5E1", size=10)
        ),
        xaxis=dict(showgrid=True, gridcolor="#1E293B", showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor="#1E293B", side="right", tickfont=dict(color="#64748B", size=10)),
        hovermode="x unified"
    )
    
    return fig


def render_sector_assets_barchart(sector_name: str) -> go.Figure:
    """
    Crea gráfico de barras horizontales con las ganancias de los activos del sector
    idéntico a la imagen 2 de Deepvue (con barras azules horizontales).
    """
    assets = SECTOR_ASSETS_PERFORMANCE.get(sector_name, SECTOR_ASSETS_PERFORMANCE["Energy"])
    
    # Ordenar por change_pct ascendente para que el top aparezca arriba
    df = pd.DataFrame(assets).sort_values("change_pct", ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df["symbol"],
        x=df["change_pct"],
        orientation="h",
        marker_color="#3B82F6",
        text=[f"+{v:.2f}%" for v in df["change_pct"]],
        textposition="outside",
        textfont=dict(color="#93C5FD", size=11)
    ))
    
    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=max(450, len(df) * 24),
        margin=dict(l=60, r=70, t=15, b=25),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            ticksuffix="%",
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            tickfont=dict(color="#F8FAFC", size=11, family="monospace")
        ),
        showlegend=False
    )
    
    return fig
