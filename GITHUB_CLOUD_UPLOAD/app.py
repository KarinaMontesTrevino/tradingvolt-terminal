import sys
import subprocess

# Auto-instalador de respaldo para Streamlit Community Cloud si falta requirements.txt en la raíz
for _mod, _pkg in [
    ("plotly", "plotly"),
    ("yfinance", "yfinance"),
    ("scipy", "scipy"),
    ("bs4", "beautifulsoup4"),
    ("lxml", "lxml"),
    ("alpaca", "alpaca-py"),
    ("pytz", "pytz"),
]:
    try:
        __import__(_mod)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", _pkg])

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime
import json
import os
import html
import importlib
from pathlib import Path

import screener_engine as engine
import discord_notifier as discord
import market_dashboard_engine as mde
import key_levels_engine as kle
import expanded_universes as eu
import importlib
try:
    import pure_momentum_universe as _pmu
    importlib.reload(_pmu)
    PURE_MOMENTUM_231_TICKERS = getattr(_pmu, 'PURE_MOMENTUM_231_TICKERS', getattr(_pmu, 'PURE_MOMENTUM_205_TICKERS', []))
    PURE_MOMENTUM_205_TICKERS = getattr(_pmu, 'PURE_MOMENTUM_205_TICKERS', PURE_MOMENTUM_231_TICKERS)
except Exception:
    try:
        from pure_momentum_universe import PURE_MOMENTUM_231_TICKERS, PURE_MOMENTUM_205_TICKERS
    except Exception:
        from pure_momentum_universe import PURE_MOMENTUM_205_TICKERS
        PURE_MOMENTUM_231_TICKERS = PURE_MOMENTUM_205_TICKERS
from leaders_universe import TML_331_TICKERS
try:
    from autonomous_tml_engine import get_autonomous_market_leaders
except ImportError:
    get_autonomous_market_leaders = lambda top_n=260: []
try:
    import quant_options_engine as qoe
    importlib.reload(qoe)
except ImportError:
    qoe = None
try:
    import canslim_terminal_engine as cte
    importlib.reload(cte)
except ImportError:
    cte = None
try:
    import dark_pool_engine as dpe
    importlib.reload(dpe)
except ImportError:
    dpe = None
try:
    import luld_engine as le
    importlib.reload(le)
except ImportError:
    le = None
try:
    import unusual_options_engine as uoe
    importlib.reload(uoe)
except ImportError:
    uoe = None
try:
    import earnings_calendar_engine as ece
    importlib.reload(ece)
except ImportError:
    ece = None
try:
    import new_highs_lows_engine as nhle
    importlib.reload(nhle)
except ImportError:
    nhle = None
try:
    import cot_positioning_engine as cpe
    importlib.reload(cpe)
except ImportError:
    cpe = None
try:
    import sentiment_intelligence_engine as sie
    importlib.reload(sie)
except ImportError:
    sie = None
try:
    import economic_calendar_engine as ecle
    importlib.reload(ecle)
except ImportError:
    ecle = None
try:
    import stage_analysis_engine as sae
    importlib.reload(sae)
except ImportError:
    sae = None
try:
    import industry_ranks_engine as ire
    importlib.reload(ire)
except ImportError:
    ire = None
try:
    import intraday_strength_engine as ise
    importlib.reload(ise)
except ImportError:
    ise = None
try:
    import insider_institutional_engine as iie
    importlib.reload(iie)
except ImportError:
    iie = None
try:
    import order_imbalance_engine as oie
    importlib.reload(oie)
except ImportError:
    oie = None
try:
    import weekend_review_engine as wre
    importlib.reload(wre)
except ImportError:
    wre = None
try:
    import rrg_engine as rrg
    importlib.reload(rrg)
except ImportError:
    rrg = None
try:
    import labor_market_engine as lme
    importlib.reload(lme)
except ImportError:
    lme = None
try:
    import ticker_banner_engine as tbe
    importlib.reload(tbe)
except ImportError:
    tbe = None
try:
    import active_radar_engine as are
    importlib.reload(are)
except ImportError:
    are = None
try:
    import realtime_news_engine as rne
    importlib.reload(rne)
except ImportError:
    rne = None
try:
    import quant_data_pipeline as qdp
    importlib.reload(qdp)
except ImportError:
    qdp = None
try:
    import daily_briefing_engine as dbe
    importlib.reload(dbe)
except ImportError:
    dbe = None
import urllib.parse
import streamlit.components.v1 as components

importlib.reload(engine)
importlib.reload(discord)
importlib.reload(mde)
importlib.reload(kle)
importlib.reload(eu)

# ----------------- CONFIGURACIÓN DE PÁGINA -----------------
st.set_page_config(
    page_title="TradingVolt • Institutional Terminal & Market Desk",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CSS PROFESIONAL NEON-DARK TRADINGVOLT (ALTA LEGIBILIDAD) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    /* Fondo principal y tipografía global de alta legibilidad */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #08090C !important;
        color: #F8FAFC !important;
        font-family: 'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
        letter-spacing: -0.01em !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0C0E14 !important;
        border-right: 1px solid #1A202C !important;
        font-size: 14.5px !important;
    }

    /* Radio buttons en Sidebar más grandes y con mejor espaciado */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        font-size: 14px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        padding: 5px 8px !important;
        margin-bottom: 2px !important;
        border-radius: 6px !important;
        transition: background 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.05) !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Títulos principales y subtítulos con contraste mejorado */
    .brand-title {
        font-size: 30px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #00F0FF 0%, #00FF87 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.5px;
    }

    .brand-sub {
        font-size: 12.5px !important;
        font-weight: 700 !important;
        color: #94A3B8 !important; /* Gris claro de alto contraste */
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: -2px;
        margin-bottom: 14px;
    }

    /* Elementos interactivos de Streamlit (Selectbox, Inputs, Labels) */
    .stSelectbox label, .stTextInput label, .stRadio label, .stSlider label {
        font-size: 14.5px !important;
        font-weight: 600 !important;
        color: #F1F5F9 !important;
        margin-bottom: 4px !important;
    }

    div[data-baseweb="select"] span, div[data-baseweb="select"] input {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #F8FAFC !important;
    }

    div[data-baseweb="select"] li {
        font-size: 14px !important;
        padding: 8px 12px !important;
    }

    .stTextInput input {
        font-size: 14px !important;
        color: #F8FAFC !important;
        padding: 8px 12px !important;
    }

    /* Pestañas (Tabs) ampliadas y nítidas */
    button[data-baseweb="tab"] {
        font-size: 14.5px !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        color: #94A3B8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00F0FF !important;
        font-weight: 700 !important;
    }

    /* Botones primarios y secundarios */
    div.stButton > button {
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        letter-spacing: 0.1px !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00F0FF 0%, #00FF87 100%) !important;
        color: #08090C !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        box-shadow: 0 0 16px rgba(0, 255, 135, 0.3) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #111520 !important;
        color: #00F0FF !important;
        border: 1px solid #1E2638 !important;
        border-radius: 6px !important;
    }

    /* Captions y notas */
    .stCaption, [data-testid="stCaptionContainer"] p {
        font-size: 13.5px !important;
        color: #94A3B8 !important;
        line-height: 1.5 !important;
    }

    /* Tarjetas HUD de Métricas Cuantitativas */
    .hud-card {
        background: #0E121A;
        border: 1px solid #1C2433;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: all 0.2s ease-in-out;
    }
    .hud-card:hover {
        border-color: #00F0FF;
        box-shadow: 0 0 14px rgba(0, 240, 255, 0.12);
    }
    .hud-label {
        font-size: 12.5px !important;
        color: #94A3B8 !important;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.6px;
    }
    .hud-value {
        font-size: 24px !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 4px;
    }

    /* Metric Cards institucionales */
    .metric-card {
        background: #0E121A;
        border: 1px solid #1C2433;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 13.5px !important;
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 24px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800 !important;
    }

    /* Badges de estado con texto más legible */
    .badge-neon-bull {
        display: inline-block;
        background: rgba(0, 255, 135, 0.15);
        color: #00FF87;
        border: 1px solid rgba(0, 255, 135, 0.35);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 12.5px !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }

    .badge-neon-bear {
        display: inline-block;
        background: rgba(255, 46, 99, 0.15);
        color: #FF2E63;
        border: 1px solid rgba(255, 46, 99, 0.35);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 12.5px !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }

    .badge-neon-cyan {
        display: inline-block;
        background: rgba(0, 240, 255, 0.15);
        color: #00F0FF;
        border: 1px solid rgba(0, 240, 255, 0.35);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 12.5px !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }

    /* BREADTH METRIC CARDS & RATIO BARS */
    .breadth-card {
        background: #0E121B;
        border: 1px solid #182030;
        border-radius: 8px;
        padding: 13px 16px 11px 16px;
        margin-bottom: 12px;
    }
    .breadth-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .breadth-title {
        font-size: 13.5px !important;
        font-weight: 700;
        color: #F1F5F9;
    }
    .breadth-ratio-pos {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px !important;
        font-weight: 800;
        color: #00FF87;
        background: rgba(0, 255, 135, 0.1);
        padding: 1px 7px;
        border-radius: 4px;
        border: 1px solid rgba(0, 255, 135, 0.25);
    }
    .breadth-ratio-neg {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px !important;
        font-weight: 800;
        color: #FF2E63;
        background: rgba(255, 46, 99, 0.1);
        padding: 1px 7px;
        border-radius: 4px;
        border: 1px solid rgba(255, 46, 99, 0.25);
    }
    .breadth-track {
        display: flex;
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0;
    }
    .breadth-fill-pos {
        height: 100%;
        background: linear-gradient(90deg, #10B981, #00FF87);
        border-radius: 4px 0 0 4px;
        transition: width 0.3s ease;
    }
    .breadth-fill-neg {
        height: 100%;
        background: linear-gradient(90deg, #FF2E63, #F43F5E);
        border-radius: 0 4px 4px 0;
        transition: width 0.3s ease;
    }
    .breadth-footer {
        display: flex;
        justify-content: space-between;
        font-size: 12px !important;
        font-family: 'JetBrains Mono', monospace;
        color: #94A3B8;
        font-weight: 600;
    }
    .stage-track {
        display: flex;
        width: 100%;
        height: 9px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 5px;
        overflow: hidden;
        margin: 10px 0 8px 0;
    }
    .stage-seg-1 {
        height: 100%;
        background: #64748B;
        transition: width 0.3s ease;
    }
    .stage-seg-2 {
        height: 100%;
        background: linear-gradient(90deg, #2563EB, #38BDF8);
        transition: width 0.3s ease;
    }
    .stage-seg-3 {
        height: 100%;
        background: #EAB308;
        transition: width 0.3s ease;
    }
    .stage-seg-4 {
        height: 100%;
        background: linear-gradient(90deg, #EC4899, #F43F5E);
        transition: width 0.3s ease;
    }

    /* ESCALA AUTOMÁTICA UNIVERSAL PARA TEXTOS DE TABLAS Y FILAS (ELIMINA LETRA PEQUEÑA) */
    *[style*="font-size:9px"], *[style*="font-size: 9px"],
    *[style*="font-size:10px"], *[style*="font-size: 10px"] {
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    *[style*="font-size:11px"], *[style*="font-size: 11px"] {
        font-size: 13.5px !important;
        line-height: 1.45 !important;
    }
    *[style*="font-size:12px"], *[style*="font-size: 12px"] {
        font-size: 14.5px !important;
        line-height: 1.5 !important;
    }
    *[style*="font-size:13px"], *[style*="font-size: 13px"] {
        font-size: 15px !important;
    }

    /* MEJORA DE CONTRASTE: ACLARAR TEXTOS OSCUROS/GRISES */
    *[style*="color:#64748B"], *[style*="color: #64748B"],
    *[style*="color:#718096"], *[style*="color: #718096"],
    *[style*="color:#6B7280"], *[style*="color: #6B7280"] {
        color: #94A3B8 !important; /* Más claro y nítido para no forzar la vista */
    }
    *[style*="color:#8E8EA0"], *[style*="color: #8E8EA0"],
    *[style*="color:#9CA3AF"], *[style*="color: #9CA3AF"] {
        color: #CBD5E1 !important;
    }

    /* Barra de scroll estilizada */
    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }
    ::-webkit-scrollbar-track {
        background: #08090C;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E2638;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #00F0FF;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- CONFIGURACIÓN PERSISTENTE -----------------
CONFIG_FILE = "config.json"
config = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        config = {}

# Soporte automático para Streamlit Community Cloud (st.secrets) en despliegue 24/7
try:
    if hasattr(st, "secrets") and len(st.secrets) > 0:
        for _sk in ("alpaca_api_key", "alpaca_secret_key", "discord_webhook_url", "data_provider"):
            if _sk in st.secrets and not config.get(_sk):
                config[_sk] = str(st.secrets[_sk])
except Exception:
    pass

def save_config(updated_dict):
    config.update(updated_dict)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        st.error(f"Error guardando configuración: {e}")

# ----------------- REUSABLE CANDLESTICK CHART ENGINE -----------------
def render_institutional_chart(ticker, key_suffix="chart"):
    """
    Renderiza el gráfico de velas japonesas profesional continuo con Plotly:
    - Velas sin saltos de fines de semana ni noches (rangebreaks)
    - Medias móviles continuas precalculadas sobre histórico de 2 años (EMA 10, SMA 20, SMA 50, SMA 200)
    - Subplot de volumen con coloreado de velas y media SMA 20
    - Selector de temporalidad independiente
    """
    col_tf1, col_tf2, col_tf3, col_tf4, col_tf5 = st.columns([1.7, 0.55, 0.75, 0.75, 0.95])
    with col_tf1:
        chart_tf = st.radio(
            "Temporalidad del Gráfico:",
            ["📅 1D (Diario)", "⏰ 1H (1 Hora)", "⚡ 15m (15 Min)", "🎯 5m (Intradía)"],
            horizontal=True,
            index=0,
            key=f"rad_tf_{ticker}_{key_suffix}",
            label_visibility="collapsed"
        )
    with col_tf2:
        st.caption(f"Activo: **{ticker}**")
    with col_tf3:
        show_key_levels = st.toggle(
            "🎯 Niveles Clave",
            value=False,
            key=f"tog_kl_{ticker}_{key_suffix}",
            help="Super Indicador de Niveles Clave Institucionales normalizado con volatilidad ATR"
        )
    with col_tf4:
        show_luld = st.toggle(
            "🚨 Bandas LULD",
            value=False,
            key=f"tog_luld_{ticker}_{key_suffix}",
            help="Guardarraíles de volatilidad Limit Up / Limit Down del Plan NMS de la SEC"
        )
    with col_tf5:
        default_piv_tog = bool(st.session_state.get("active_screener_is_pivot", False))
        show_pivot_breakout = st.toggle(
            "📐 Pivot Breakout",
            value=default_piv_tog,
            key=f"tog_piv_{ticker}_{key_suffix}_{int(default_piv_tog)}",
            help="Daily Pivot Breakout Strategy Indicator: Pivotes (5L/5R, Lookback 100), EMA 100 (Slope ≥ 20%), ROC 100d ≥ 30%, RVOL 20d y Momentum Candle Colors"
        )

    if "1D" in chart_tf:
        period, interval = "2y", "1d"
        visible_bars = 250
        is_intraday = False
    elif "1H" in chart_tf:
        period, interval = "3mo", "1h"
        visible_bars = 160
        is_intraday = True
    elif "15m" in chart_tf:
        period, interval = "1mo", "15m"
        visible_bars = 180
        is_intraday = True
    else:
        period, interval = "5d", "5m"
        visible_bars = 160
        is_intraday = True

    with st.spinner(f"Cargando {chart_tf} para {ticker}..."):
        raw_data = yf.download(ticker, period=period, interval=interval, progress=False)

        if raw_data.empty:
            st.warning(f"No se pudieron descargar datos para {ticker}.")
            return

        if isinstance(raw_data.columns, pd.MultiIndex):
            raw_data.columns = raw_data.columns.get_level_values(0)

        # Descartar filas con Close NaN o <= 0 (ej. barras incompletas de after-hours)
        raw_data = raw_data.dropna(subset=['Close'])
        raw_data = raw_data[raw_data['Close'] > 0]

        if raw_data.empty:
            st.warning(f"No hay cotizaciones válidas para {ticker}.")
            return

        if raw_data.index.tz is not None:
            raw_data.index = raw_data.index.tz_convert('America/New_York')

        if not is_intraday:
            raw_data['EMA10'] = raw_data['Close'].ewm(span=10).mean()
            raw_data['SMA20'] = raw_data['Close'].rolling(20).mean()
            raw_data['SMA50'] = raw_data['Close'].rolling(50).mean()
            raw_data['SMA200'] = raw_data['Close'].rolling(200).mean()
            raw_data['VolSMA20'] = raw_data['Volume'].rolling(20).mean()
        else:
            raw_data['EMA9'] = raw_data['Close'].ewm(span=9).mean()
            raw_data['EMA21'] = raw_data['Close'].ewm(span=21).mean()
            raw_data['SMA50'] = raw_data['Close'].rolling(50).mean()
            raw_data['VolSMA20'] = raw_data['Volume'].rolling(20).mean()

        chart_data = raw_data.iloc[-visible_bars:].copy() if len(raw_data) > visible_bars else raw_data.copy()
        x_dates = chart_data.index

        # Header con precio actual y cambio (inmune a NaN)
        last_c = float(chart_data['Close'].iloc[-1])
        if np.isnan(last_c):
            valid_c = chart_data['Close'].dropna()
            last_c = float(valid_c.iloc[-1]) if not valid_c.empty else 0.0
        prev_c = float(chart_data['Close'].iloc[-2]) if len(chart_data) > 1 else last_c
        if np.isnan(prev_c):
            prev_c = last_c
        chg_pct = ((last_c / prev_c) - 1.0) * 100.0 if prev_c > 0 else 0.0
        if np.isnan(chg_pct):
            chg_pct = 0.0
        badge_cls = "badge-neon-bull" if chg_pct >= 0 else "badge-neon-bear"
        sign = "+" if chg_pct >= 0 else ""

        st.markdown(f"""
        <div style="background: #0E121A; border: 1px solid #1C2433; border-radius: 8px 8px 0 0; padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
            <div style="display: flex; align-items: baseline; gap: 12px;">
                <span style="font-size: 22px; font-weight: 800; color: #FFFFFF; font-family: 'JetBrains Mono', monospace;">{ticker}</span>
                <span style="font-size: 19px; font-weight: 700; color: #F8FAFC; font-family: 'JetBrains Mono', monospace;">${last_c:.2f}</span>
                <span class="{badge_cls}">{sign}{chg_pct:.2f}%</span>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <a href="https://www.tradingview.com/chart/?symbol={ticker}" target="_blank" style="color: #00F0FF; font-size: 11px; font-weight: 700; text-decoration: none; padding: 4px 8px; border: 1px solid #00F0FF; border-radius: 4px;">
                    ↗ TV VIEW
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.78, 0.22]
        )

        fig.add_trace(
            go.Candlestick(
                x=x_dates,
                open=chart_data['Open'],
                high=chart_data['High'],
                low=chart_data['Low'],
                close=chart_data['Close'],
                name="Precio",
                increasing_line_color='#00FF87',
                increasing_fillcolor='#00FF87',
                decreasing_line_color='#FF2E63',
                decreasing_fillcolor='#FF2E63'
            ),
            row=1, col=1
        )

        if not is_intraday:
            if 'EMA10' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['EMA10'], line=dict(color='#00F0FF', width=1.5), name="EMA 10", connectgaps=True), row=1, col=1)
            if 'SMA20' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['SMA20'], line=dict(color='#FFD600', width=1.8), name="SMA 20", connectgaps=True), row=1, col=1)
            if 'SMA50' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['SMA50'], line=dict(color='#FF9100', width=2), name="SMA 50", connectgaps=True), row=1, col=1)
            if 'SMA200' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['SMA200'], line=dict(color='#B388FF', width=2), name="SMA 200", connectgaps=True), row=1, col=1)
        else:
            if 'EMA9' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['EMA9'], line=dict(color='#00F0FF', width=1.5), name="EMA 9", connectgaps=True), row=1, col=1)
            if 'EMA21' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['EMA21'], line=dict(color='#FFD600', width=1.8), name="EMA 21", connectgaps=True), row=1, col=1)
            if 'SMA50' in chart_data.columns:
                fig.add_trace(go.Scatter(x=x_dates, y=chart_data['SMA50'], line=dict(color='#FF9100', width=1.8), name="SMA 50", connectgaps=True), row=1, col=1)

        candle_color = [
            '#00FF87' if c >= o else '#FF2E63'
            for c, o in zip(chart_data['Close'], chart_data['Open'])
        ]
        fig.add_trace(
            go.Bar(
                x=x_dates,
                y=chart_data['Volume'],
                marker_color=candle_color,
                name="Volumen",
                opacity=0.85
            ),
            row=2, col=1
        )

        if 'VolSMA20' in chart_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_dates,
                    y=chart_data['VolSMA20'],
                    line=dict(color='#00F0FF', width=1.2, dash='dot'),
                    name="Vol SMA 20",
                    connectgaps=True
                ),
                row=2, col=1
            )

        # ----------------- DIBUJAR NIVELES CLAVE RELEVANTES -----------------
        levels_data = None
        if show_key_levels:
            try:
                levels_data = kle.calculate_key_levels(raw_data)
                if levels_data:
                    fig = kle.add_key_levels_to_chart(fig, levels_data, is_intraday=is_intraday, x_dates=x_dates)
            except Exception as e:
                print(f"Error drawing key levels for {ticker}: {e}")

        # ----------------- DIBUJAR BANDAS LULD (LIMIT UP / LIMIT DOWN) -----------------
        if show_luld and le:
            try:
                luld_guard = le.calculate_luld_guardrails(ticker, spot_price=last_c)
                fig = le.add_luld_bands_to_chart(fig, luld_guard, x_dates=x_dates)
            except Exception as e:
                print(f"Error drawing LULD bands for {ticker}: {e}")

        # ----------------- DIBUJAR DAILY PIVOT BREAKOUT STRATEGY & MOMENTUM CANDLES -----------------
        piv_diag = None
        if show_pivot_breakout:
            try:
                piv_cfg = st.session_state.get("pivot_strategy_params", {
                    "left_strength": 5,
                    "right_strength": 5,
                    "pivot_lookback": 100,
                    "roc_period": 100,
                    "min_roc_pct": 30.0,
                    "rvol_period": 20,
                    "ema_length": 100,
                    "ema_slope_lookback": 100,
                    "ema_smooth_length": 1,
                    "min_ema_slope_pct": 20.0,
                    "enable_momentum_colors": True,
                    "min_rvol": 1.0,
                })
                ema_len_p = int(piv_cfg.get("ema_length", 100))
                smooth_len_p = int(piv_cfg.get("ema_smooth_length", 1))
                roc_p = int(piv_cfg.get("roc_period", 100))
                min_roc_p = float(piv_cfg.get("min_roc_pct", 30.0))
                slope_lb_p = int(piv_cfg.get("ema_slope_lookback", 100))
                min_slope_p = float(piv_cfg.get("min_ema_slope_pct", 20.0))
                rvol_p = int(piv_cfg.get("rvol_period", 20))
                enable_mom_cols = bool(piv_cfg.get("enable_momentum_colors", True))

                # Calcular EMA(100) + Slope(100) + ROC(100) sobre raw_data completo
                ema_full = raw_data['Close'].ewm(span=ema_len_p, adjust=False).mean()
                if smooth_len_p > 1:
                    ema_full = ema_full.ewm(span=smooth_len_p, adjust=False).mean()
                raw_data['EMA_PIV'] = ema_full
                raw_data['EMA_SLOPE_PIV'] = ((raw_data['EMA_PIV'] - raw_data['EMA_PIV'].shift(slope_lb_p)) / (raw_data['EMA_PIV'].shift(slope_lb_p) + 1e-9)) * 100.0
                raw_data['ROC_PIV'] = ((raw_data['Close'] - raw_data['Close'].shift(roc_p)) / (raw_data['Close'].shift(roc_p) + 1e-9)) * 100.0
                raw_data['VOL_REF_PIV'] = raw_data['Volume'].shift(1).rolling(rvol_p).mean()
                raw_data['RVOL_PIV'] = raw_data['Volume'] / (raw_data['VOL_REF_PIV'] + 1e-9)

                chart_piv = raw_data.iloc[-visible_bars:].copy() if len(raw_data) > visible_bars else raw_data.copy()
                piv_diag = engine.evaluate_daily_pivot_breakout(raw_data, params=piv_cfg)

                # 1. Trazar EMA 100 con pendiente en leyenda
                slope_now_val = piv_diag.get("ema_slope_pct", 0.0) if piv_diag and piv_diag.get("valid") else 0.0
                fig.add_trace(
                    go.Scatter(
                        x=chart_piv.index,
                        y=chart_piv['EMA_PIV'],
                        line=dict(color='#00E5FF', width=2.6),
                        name=f"EMA {ema_len_p} (Slope {slope_now_val:+.1f}%)",
                        connectgaps=True
                    ),
                    row=1, col=1
                )

                # 2. Colorear Velas según Momentum (Enable Momentum Candle Colors)
                if enable_mom_cols:
                    # Clasificar cada barra visible en categorías de Momentum para superponer velas coloreadas
                    mask_power = (chart_piv['ROC_PIV'] >= min_roc_p) & (chart_piv['EMA_SLOPE_PIV'] >= min_slope_p) & (chart_piv['Close'] > chart_piv['EMA_PIV'])
                    mask_warm = (~mask_power) & ((chart_piv['ROC_PIV'] >= min_roc_p * 0.5) | (chart_piv['EMA_SLOPE_PIV'] >= min_slope_p * 0.5)) & (chart_piv['Close'] > chart_piv['EMA_PIV'])

                    if mask_power.any():
                        sub_p = chart_piv[mask_power]
                        fig.add_trace(
                            go.Candlestick(
                                x=sub_p.index,
                                open=sub_p['Open'],
                                high=sub_p['High'],
                                low=sub_p['Low'],
                                close=sub_p['Close'],
                                name=f"🔥 Vela Momentum (ROC≥{min_roc_p:.0f}% & Slope≥{min_slope_p:.0f}%)",
                                increasing_line_color='#00F0FF',
                                increasing_fillcolor='#00F0FF',
                                decreasing_line_color='#38BDF8',
                                decreasing_fillcolor='#0284C7',
                                showlegend=True
                            ),
                            row=1, col=1
                        )
                    if mask_warm.any():
                        sub_w = chart_piv[mask_warm]
                        fig.add_trace(
                            go.Candlestick(
                                x=sub_w.index,
                                open=sub_w['Open'],
                                high=sub_w['High'],
                                low=sub_w['Low'],
                                close=sub_w['Close'],
                                name="🟡 Vela Momentum En Construcción",
                                increasing_line_color='#FFD600',
                                increasing_fillcolor='#FFD600',
                                decreasing_line_color='#F59E0B',
                                decreasing_fillcolor='#B45309',
                                showlegend=True
                            ),
                            row=1, col=1
                        )

                # 3. Dibujar Pivot High (─── línea verde), 20% Trailing Stop (••••••• puntos azules) y Entry Signals (by Mike)
                if piv_diag and piv_diag.get("valid"):
                    piv_price = piv_diag["pivot_price"]
                    show_piv_line = bool(piv_cfg.get("show_pivot_high", True))
                    show_trail_line = bool(piv_cfg.get("show_trailing_stop", True))
                    show_entries = bool(piv_cfg.get("show_entry_signals", True))

                    # Serie histórica de Pivot High (─── línea verde escalonada como en el indicador de Mike)
                    piv_series_full = pd.Series(piv_diag.get("pivot_line_series", np.full(len(raw_data), np.nan)), index=raw_data.index)
                    piv_series_vis = piv_series_full.reindex(chart_piv.index)

                    if show_piv_line:
                        fig.add_trace(
                            go.Scatter(
                                x=chart_piv.index,
                                y=piv_series_vis,
                                mode="lines",
                                line=dict(color="#10B981", width=2.2),
                                name=f"─── Pivot High (${piv_price:.2f})",
                                connectgaps=False
                            ),
                            row=1, col=1
                        )

                        conf_pivs = piv_diag.get("confirmed_pivots", [])
                        piv_x = [dt for _, _, dt in conf_pivs if dt in chart_piv.index]
                        piv_y = [val for _, val, dt in conf_pivs if dt in chart_piv.index]
                        if piv_x:
                            fig.add_trace(
                                go.Scatter(
                                    x=piv_x,
                                    y=piv_y,
                                    mode="markers",
                                    marker=dict(symbol="diamond", size=8, color="#10B981", line=dict(color="#FFFFFF", width=1.1)),
                                    name=f"◆ Pivot Confirmado ({piv_cfg.get('left_strength', 5)}L/{piv_cfg.get('right_strength', 5)}R)"
                                ),
                                row=1, col=1
                            )

                        # Línea de referencia del último Pivot High activo
                        fig.add_hline(
                            y=piv_price,
                            line_dash="solid",
                            line_color="#10B981",
                            line_width=1.6,
                            annotation_text=f"Pivot High: ${piv_price:.2f} ({piv_diag['dist_pivot_pct']:+.1f}%)",
                            annotation_position="top left",
                            annotation_font=dict(color="#00FF87", size=11, family="JetBrains Mono"),
                            row=1, col=1
                        )

                    # 4. Dibujar 20% Trailing Stop (••••••• línea punteada azul celeste idéntica al diálogo de Mike)
                    if show_trail_line:
                        trail_series_full = pd.Series(piv_diag.get("trailing_stop_series", np.full(len(raw_data), np.nan)), index=raw_data.index)
                        trail_series_vis = trail_series_full.reindex(chart_piv.index)
                        if trail_series_vis.notna().any():
                            fig.add_trace(
                                go.Scatter(
                                    x=chart_piv.index,
                                    y=trail_series_vis,
                                    mode="lines+markers",
                                    marker=dict(symbol="circle", size=4.5, color="#38BDF8"),
                                    line=dict(color="#38BDF8", width=1.8, dash="dot"),
                                    name=f"••••••• {piv_cfg.get('trailing_stop_pct', 20.0):.0f}% Trailing Stop (${piv_diag['trailing_stop_price']:.2f})",
                                    connectgaps=False
                                ),
                                row=1, col=1
                            )

                    # 5. Dibujar Entry Signals (Breakout) y Salidas por 20% Trailing Stop
                    if show_entries:
                        ent_list = piv_diag.get("entry_signals", [])
                        ent_x = [dt for _, dt, _, _ in ent_list if dt in chart_piv.index]
                        ent_y = [ float(chart_piv.loc[dt, 'Low']) * 0.982 for _, dt, _, _ in ent_list if dt in chart_piv.index ]
                        if ent_x:
                            fig.add_trace(
                                go.Scatter(
                                    x=ent_x,
                                    y=ent_y,
                                    mode="markers+text",
                                    marker=dict(symbol="triangle-up", size=14, color="#00FF87", line=dict(color="#FFFFFF", width=1.5)),
                                    text=["Breakout" for _ in range(len(ent_x))],
                                    textposition="bottom center",
                                    textfont=dict(color="#00FF87", size=11, family="JetBrains Mono"),
                                    name="🚀 Entry Signal (Breakout)"
                                ),
                                row=1, col=1
                            )

                        ext_list = piv_diag.get("exit_signals", [])
                        ext_x = [dt for _, dt, _, _ in ext_list if dt in chart_piv.index]
                        ext_y = [ float(chart_piv.loc[dt, 'High']) * 1.018 for _, dt, _, _ in ext_list if dt in chart_piv.index ]
                        if ext_x:
                            fig.add_trace(
                                go.Scatter(
                                    x=ext_x,
                                    y=ext_y,
                                    mode="markers+text",
                                    marker=dict(symbol="x", size=11, color="#FF2E63", line=dict(color="#FFFFFF", width=1.2)),
                                    text=["Stop 20%" for _ in range(len(ext_x))],
                                    textposition="top center",
                                    textfont=dict(color="#FF2E63", size=10, family="JetBrains Mono"),
                                    name="🛑 20% Trailing Stop Exit"
                                ),
                                row=1, col=1
                            )
            except Exception as e:
                print(f"Error drawing Daily Pivot Breakout overlay for {ticker}: {e}")

        if is_intraday:
            rb_list = [
                dict(bounds=['sat', 'mon']),
                dict(bounds=[16, 9.5], pattern='hour')
            ]
        else:
            rb_list = [dict(bounds=['sat', 'mon'])]

        fig.update_layout(
            template="plotly_dark",
            height=460,
            margin=dict(l=10, r=40, t=10, b=10),
            paper_bgcolor="#0A0D14",
            plot_bgcolor="#0A0D14",
            xaxis_rangeslider_visible=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10, color="#94A3B8")
            ),
            yaxis=dict(
                side="right",
                gridcolor="#151C28",
                zerolinecolor="#151C28",
                tickfont=dict(family="JetBrains Mono", size=10, color="#94A3B8")
            ),
            yaxis2=dict(
                side="right",
                gridcolor="#151C28",
                zerolinecolor="#151C28",
                tickfont=dict(family="JetBrains Mono", size=9, color="#64748B")
            )
        )

        fig.update_xaxes(
            range=[x_dates[0], x_dates[-1]],
            rangebreaks=rb_list,
            gridcolor="#151C28",
            zerolinecolor="#151C28",
            tickfont=dict(family="JetBrains Mono", size=9, color="#64748B")
        )

        st.plotly_chart(fig, width="stretch")

        # ----------------- HUD TÁCTICO DE DAILY PIVOT BREAKOUT STRATEGY (BY MIKE) -----------------
        if show_pivot_breakout and piv_diag and piv_diag.get("valid"):
            p_cfg = st.session_state.get("pivot_strategy_params", {})
            min_r_hud = float(p_cfg.get("min_roc_pct", 30.0))
            min_s_hud = float(p_cfg.get("min_ema_slope_pct", 20.0))
            roc_c = "#00FF87" if piv_diag["cond_momentum"] else "#FF2E63"
            slp_c = "#00FF87" if piv_diag["cond_trend_slope"] else "#FF2E63"
            rvl_c = "#00FF87" if piv_diag["cond_rvol"] else "#FFD600"
            piv_c = "#10B981" if piv_diag["cond_breakout"] else "#00F0FF"
            trl_c = "#38BDF8"

            hp1, hp2, hp3, hp4, hp5, hp6 = st.columns(6)
            with hp1:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid {piv_c};">
                    <div class="hud-label">─── PIVOT HIGH (5L/5R)</div>
                    <div class="hud-value" style="color: {piv_c}; font-size: 19px;">${piv_diag['pivot_price']:.2f}</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Dist: <strong>{piv_diag['dist_pivot_pct']:+.2f}%</strong> ({piv_diag['pivot_date']})</div>
                </div>
                """, unsafe_allow_html=True)
            with hp2:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid {trl_c};">
                    <div class="hud-label">•••• 20% TRAILING STOP</div>
                    <div class="hud-value" style="color: {trl_c}; font-size: 19px;">${piv_diag['trailing_stop_price']:.2f}</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Colchón: <strong>{piv_diag['dist_trailing_stop_pct']:+.1f}%</strong> {'(En Trade)' if piv_diag.get('in_trade') else '(Ref 20%)'}</div>
                </div>
                """, unsafe_allow_html=True)
            with hp3:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid {roc_c};">
                    <div class="hud-label">🚀 ROC (100 DÍAS)</div>
                    <div class="hud-value" style="color: {roc_c}; font-size: 19px;">{piv_diag['roc_val']:+.1f}%</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Mínimo exigido: <strong>+{min_r_hud:.0f}%</strong></div>
                </div>
                """, unsafe_allow_html=True)
            with hp4:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid {slp_c};">
                    <div class="hud-label">📈 EMA 100 SLOPE</div>
                    <div class="hud-value" style="color: {slp_c}; font-size: 19px;">{piv_diag['ema_slope_pct']:+.1f}%</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">EMA 100: <strong>${piv_diag['ema_val']:.2f}</strong> (Mín +{min_s_hud:.0f}%)</div>
                </div>
                """, unsafe_allow_html=True)
            with hp5:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid {rvl_c};">
                    <div class="hud-label">📊 RVOL (20 DÍAS)</div>
                    <div class="hud-value" style="color: {rvl_c}; font-size: 19px;">{piv_diag['rvol_val']:.2f}x</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Requisito: <strong>&gt; 1.00x SMA20</strong></div>
                </div>
                """, unsafe_allow_html=True)
            with hp6:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid {piv_diag['candle_hex']};">
                    <div class="hud-label">🎨 ENTRY & MOMENTUM</div>
                    <div class="hud-value" style="color: {piv_diag['candle_hex']}; font-size: 13.5px; line-height: 1.3;">{piv_diag['candle_state']}</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Últ. Entry: <strong>{piv_diag.get('last_entry_date', '—')}</strong> ({piv_diag.get('gain_since_entry_pct', 0.0):+.1f}%)</div>
                </div>
                """, unsafe_allow_html=True)

        # ----------------- HUD TÁCTICO DE NIVELES CLAVE -----------------
        if show_key_levels and levels_data:
            nearest_res = levels_data['resistances'][0] if levels_data['resistances'] else None
            nearest_sup = levels_data['supports'][0] if levels_data['supports'] else None
            poc_price = levels_data['poc_price']
            poc_dist = ((poc_price / last_c) - 1.0) * 100.0

            col_kl1, col_kl2, col_kl3, col_kl4 = st.columns(4)
            with col_kl1:
                if nearest_res:
                    st.markdown(f"""
                    <div class="hud-card" style="border-left: 3px solid #FF2E63;">
                        <div class="hud-label">🔴 RESISTENCIA {nearest_res.get('Label', 'R1')}</div>
                        <div class="hud-value" style="color: #FF2E63;">${nearest_res['Price']:.2f}</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">
                            {nearest_res['DistPct']:+.1f}% • {nearest_res['Stars']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="hud-card" style="border-left: 3px solid #FF2E63;">
                        <div class="hud-label">🔴 RESISTENCIA</div>
                        <div class="hud-value" style="font-size: 16px; color: #FF2E63;">MÁXIMO HISTÓRICO</div>
                        <div style="font-size: 11px; color: #94A3B8;">Territorio Discovery</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_kl2:
                if nearest_sup:
                    st.markdown(f"""
                    <div class="hud-card" style="border-left: 3px solid #00FF87;">
                        <div class="hud-label">🟢 SOPORTE {nearest_sup.get('Label', 'S1')}</div>
                        <div class="hud-value" style="color: #00FF87;">${nearest_sup['Price']:.2f}</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">
                            {nearest_sup['DistPct']:+.1f}% • {nearest_sup['Stars']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="hud-card" style="border-left: 3px solid #00FF87;">
                        <div class="hud-label">🟢 SOPORTE</div>
                        <div class="hud-value" style="font-size: 16px; color: #00FF87;">SUELO PRINCIPAL</div>
                        <div style="font-size: 11px; color: #94A3B8;">Sin piso cercano</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_kl3:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid #00F0FF;">
                    <div class="hud-label">⚡ POC IMÁN (VOLUMEN)</div>
                    <div class="hud-value" style="color: #00F0FF;">${poc_price:.2f}</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">
                        {poc_dist:+.1f}% • Mayor Liquidez
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_kl4:
                st.markdown(f"""
                <div class="hud-card" style="border-left: 3px solid #FFD600;">
                    <div class="hud-label">📏 ATR VOLATILIDAD (14)</div>
                    <div class="hud-value" style="color: #FFD600;">${levels_data['atr']:.2f}</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">
                        {levels_data['atr']/last_c*100:.1f}% Rango Diario
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander(f"🎯 Matriz de Confluencia de Niveles Clave ({ticker})", expanded=False):
                disp_df = levels_data['summary_df'].drop(columns=['raw_price'], errors='ignore')
                st.dataframe(disp_df, width="stretch", hide_index=True)


# ----------------- SIDEBAR: BROKER & CONFIGURACIÓN -----------------
with st.sidebar:
    st.markdown('<div class="brand-title">⚡ TradingVolt</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">INSTITUTIONAL MARKET DESK</div>', unsafe_allow_html=True)

    # Manejo de redirección rápida desde botones globales
    if st.session_state.get("_pending_nav_target"):
        st.session_state["nav_view_sidebar"] = st.session_state.pop("_pending_nav_target")

    # Selector de navegación en Sidebar
    nav_options = [
        "🏠 Dashboard de Mercado",
        "🧠 Resumen Diario 360° (En Vivo)",
        "📰 Top Stories & Breaking News Desk",
        "⚡ Screener Cuantitativo",
        "🚀 Terminal CANSLIM Líderes (BO60)",
        "🎯 Quant Options & GEX Desk",
        "🕵️‍♂️ Dark Pool & Off-Exchange Tape",
        "🚨 Monitor LULD & Halts en Vivo",
        "📅 Calendario de Earnings (Split Chart)",
        "📈 New Highs & New Lows (Breadth)",
        "📊 COT Positioning (Futures)",
        "🧠 NAAIM / AAII Sentiment Desk",
        "🌐 Calendario Económico",
        "🏛️ Fed Labor Market & Sahm Rule Monitor",
        "📊 Stage Analysis (Sectores & Activos)",
        "🏆 Industry Rank Tables (Sectores & Grupos)",
        "⚡ Intraday Strength Watch (Bubble Map)",
        "🔄 Relative Rotation Graphs (RRG Desk)",
        "🏛️ Insider & Institutional Ownership (SEC 3, 4 & 13F)",
        "🔔 NYSE Order Imbalance Tracker (NOI Auctions)",
        "📑 Weekend Review Hub (Informe de Fin de Semana)"
    ]
    cur_nav_idx = 0
    if "nav_view_sidebar" in st.session_state and st.session_state["nav_view_sidebar"] in nav_options:
        cur_nav_idx = nav_options.index(st.session_state["nav_view_sidebar"])

    nav_view = st.radio(
        "Navegación Principal:",
        nav_options,
        index=cur_nav_idx,
        key="nav_view_sidebar"
    )

    st.divider()

    show_ticker_tape = st.toggle("📻 Ticker Tape en Vivo", value=True, key="tog_ticker_tape_banner", help="Cinta animada continua con cotizaciones en tiempo real de Índices, Futuros, Commodities, Ganadores y Perdedores")

    _filters_pdf_path = os.path.join(os.path.dirname(__file__), "TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.pdf")
    if os.path.exists(_filters_pdf_path):
        with open(_filters_pdf_path, "rb") as _fpdf:
            st.download_button(
                label="📄 Descargar Catálogo Filtros (.PDF)",
                data=_fpdf.read(),
                file_name="TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_dl_filters_pdf_sidebar",
                help="Descarga el documento PDF vectorial de 3 páginas con los 29 filtros cuantitativos y sus fórmulas exactas"
            )

    with st.expander("📱 Acceso desde Teléfono (QR & Nube 24/7)", expanded=False):
        import socket
        try:
            _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _s.connect(("8.8.8.8", 80))
            _lan_ip = _s.getsockname()[0]
            _s.close()
        except Exception:
            _lan_ip = "192.168.50.232"
        _lan_url = f"http://{_lan_ip}:8501"
        _qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&bgcolor=0E121A&color=00F0FF&data={urllib.parse.quote(_lan_url)}"
        st.markdown(f"""
        <div style="background:#0B111E;border:1px solid #1E293B;border-radius:8px;padding:10px;text-align:center;margin-bottom:8px;">
            <div style="font-size:11px;font-weight:800;color:#00FF87;margin-bottom:6px;">📶 OPCIÓN 1: WI-FI LOCAL (ESCANEA CON TU CÁMARA)</div>
            <img src="{_qr_api}" width="150" height="150" style="border-radius:6px;border:1px solid #1E293B;margin-bottom:6px;" />
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00F0FF;font-weight:700;">{_lan_url}</div>
        </div>
        <div style="font-size:11.5px;color:#CBD5E1;line-height:1.45;">
            <strong>☁️ OPCIÓN 3 (Nube 24/7 Independiente):</strong><br/>
            1. Sube esta carpeta a un repo privado en <b>GitHub</b> (ya incluye <code>requirements.txt</code> y <code>.streamlit/config.toml</code>).<br/>
            2. En <a href="https://share.streamlit.io" target="_blank" style="color:#00F0FF;">share.streamlit.io</a> elige <b>New App</b> &rarr; selecciona tu repo y <code>app.py</code>.<br/>
            3. Tendrás una URL propia <code>https://...streamlit.app</code> activa 24/7 aunque tu PC esté apagada.
        </div>
        """, unsafe_allow_html=True)

    # 1. Proveedor de datos
    st.subheader("🔌 Feed de Mercado")
    data_provider_choice = st.selectbox(
        "Fuente de cotizaciones:",
        ["⚡ Alpaca Markets (Tiempo Real IEX)", "🌐 Yahoo Finance (Sin Claves / Fallback)"],
        index=0 if config.get("data_provider", "Alpaca") == "Alpaca" else 1
    )

    use_alpaca = "Alpaca" in data_provider_choice
    provider_str = "Alpaca" if use_alpaca else "yfinance"

    alpaca_key = config.get("alpaca_api_key", "")
    alpaca_secret = config.get("alpaca_secret_key", "")

    if use_alpaca:
        alpaca_key = st.text_input(
            "Alpaca API Key ID:",
            value=alpaca_key,
            type="password",
            help="Clave pública de Paper Trading o Live"
        )
        alpaca_secret = st.text_input(
            "Alpaca Secret Key:",
            value=alpaca_secret,
            type="password"
        )

        if st.button("🧪 Verificar Conexión Alpaca", key="btn_test_alpaca"):
            valid, msg = engine.verify_alpaca_credentials(alpaca_key, alpaca_secret)
            if valid:
                st.success(f"✅ {msg}")
                save_config({
                    "alpaca_api_key": alpaca_key,
                    "alpaca_secret_key": alpaca_secret,
                    "data_provider": "Alpaca"
                })
            else:
                st.error(f"❌ {msg}")

        if alpaca_key != config.get("alpaca_api_key") or alpaca_secret != config.get("alpaca_secret_key"):
            save_config({
                "alpaca_api_key": alpaca_key,
                "alpaca_secret_key": alpaca_secret,
                "data_provider": "Alpaca"
            })
    else:
        save_config({"data_provider": "yfinance"})

    st.divider()

    # 2. Notificaciones Discord
    st.subheader("🔔 Alertas Discord")
    discord_url = st.text_input(
        "Webhook URL:",
        value=config.get("discord_webhook", ""),
        type="password",
        placeholder="https://discord.com/api/webhooks/..."
    )
    if discord_url != config.get("discord_webhook"):
        save_config({"discord_webhook": discord_url})

    if st.button("📡 Probar Webhook", key="btn_test_discord"):
        if discord_url:
            success, msg = discord.test_discord_webhook(discord_url)
            if success:
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.error("Configura el Webhook en este campo.")

    st.divider()

    st.markdown("""
    <div style="font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">
        🏛️ TRADINGVOLT CORE
    </div>
    <div style="font-size: 12px; color: #94A3B8; line-height: 1.6;">
        <strong>Dashboard</strong>: 31 Temáticas con ETF proxies, amplitud de mercado y análisis de etapas de Weinstein.<br><br>
        <strong>Screener</strong>: Filtros cuantitativos de alta precisión sobre mercado real de más de 500 acciones y canastas oficiales de Deepvue.
    </div>
    """, unsafe_allow_html=True)


# ----------------- TICKER TAPE BANNER ANIMADO EN VIVO -----------------
if show_ticker_tape and tbe:
    st.markdown(tbe.render_ticker_tape_html(), unsafe_allow_html=True)

# ----------------- BARRA GLOBAL DE SINCRONIZACIÓN & RESUMEN DIARIO 360° -----------------
if "last_global_sync_str" not in st.session_state:
    st.session_state["last_global_sync_str"] = datetime.now().strftime("%H:%M:%S")

gbar_c1, gbar_c2, gbar_c3, gbar_c4 = st.columns([1.45, 1.25, 1.15, 1.55], gap="small")
with gbar_c1:
    is_in_briefing = ("Resumen Diario 360" in nav_view)
    btn_briefing_lbl = "🧠 Resumen Diario 360° (Activo • Regenerar)" if is_in_briefing else "🧠 Resumen Diario 360° en Tiempo Real"
    if st.button(btn_briefing_lbl, key="btn_global_daily_briefing", type="primary", use_container_width=True, help="Abre el informe ejecutivo en tiempo real con Gamma Exposure (GEX), Breadth, Rotación RRG, Smart Money, Top Stories y Activos Más Relevantes"):
        if dbe is not None:
            dbe.trigger_global_terminal_sync(st_module=st, clear_disk=False)
        st.session_state["last_global_sync_str"] = datetime.now().strftime("%H:%M:%S")
        if not is_in_briefing:
            st.session_state["_pending_nav_target"] = "🧠 Resumen Diario 360° (En Vivo)"
        st.rerun()

with gbar_c2:
    if st.button("🔄 Actualizar Todo Ahora (Full Sync)", key="btn_global_full_sync", type="secondary", use_container_width=True, help="Limpia cachés de memoria y fuerza la descarga fresca de cotizaciones, GEX, amplitud, RRG y cables de noticias"):
        if dbe is not None:
            sync_info = dbe.trigger_global_terminal_sync(st_module=st, clear_disk=False)
            st.session_state["last_global_sync_str"] = sync_info["synced_at"]
        else:
            st.cache_data.clear()
            st.session_state["last_global_sync_str"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

with gbar_c3:
    auto_sync_map = {
        "⏱️ Auto-Sync: Cada 3 min": 180,
        "⏱️ Auto-Sync: Cada 1 min": 60,
        "⏱️ Auto-Sync: Cada 5 min": 300,
        "⏱️ Auto-Sync: Cada 15 min": 900,
        "⏸️ Auto-Sync: Manual": 0
    }
    sel_auto_sync = st.selectbox(
        "Auto-Refresco:",
        list(auto_sync_map.keys()),
        index=0,
        key="sel_global_auto_sync",
        label_visibility="collapsed"
    )
    auto_sync_secs = auto_sync_map.get(sel_auto_sync, 180)

with gbar_c4:
    sync_mode_txt = f"AUTO ({auto_sync_secs // 60}m)" if auto_sync_secs > 0 else "MANUAL"
    st.markdown(
        f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:8px;padding:7px 12px;display:flex;justify-content:space-between;align-items:center;font-family:monospace;font-size:11.5px;">'
        f'<span style="color:#10B981;font-weight:700;">● LIVE SYNC: {st.session_state["last_global_sync_str"]}</span>'
        f'<span style="color:#38BDF8;background:rgba(56,189,248,0.12);padding:2px 7px;border-radius:4px;font-weight:700;">{sync_mode_txt}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

if auto_sync_secs > 0:
    components.html(
        f"""<script>
        (function() {{
            const intervalMs = {auto_sync_secs * 1000};
            if (window._tvAutoSyncTimer) clearInterval(window._tvAutoSyncTimer);
            window._tvAutoSyncTimer = setInterval(function() {{
                try {{
                    const buttons = Array.from(window.parent.document.querySelectorAll('button'));
                    const syncBtn = buttons.find(b => b.innerText && b.innerText.includes('Actualizar Todo Ahora'));
                    if (syncBtn) syncBtn.click();
                }} catch (e) {{}}
            }}, intervalMs);
        }})();
        </script>""",
        height=0
    )

st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

# =====================================================================
# VISTA ESPECIAL: 🧠 RESUMEN DIARIO 360° EN TIEMPO REAL (MARKET BRIEFING)
# =====================================================================
if "Resumen Diario 360" in nav_view:
    if dbe is None:
        st.error("⚠️ El motor daily_briefing_engine.py no pudo cargarse.")
    else:
        with st.spinner("⚡ Compilando Inteligencia de Mercado 360° en Tiempo Real (Índices, CBOE GEX, Breadth, RRG, Smart Money & Noticias)..."):
            brief = dbe.generate_live_daily_briefing(force_refresh=False)

        score_v = brief.get("composite_score", 50.0)
        reg_lbl = brief.get("regime_label", "NEUTRAL")
        reg_col = brief.get("regime_color", "#38BDF8")
        stance_txt = brief.get("action_stance", "")
        gen_ts = brief.get("generated_at", "")
        lat_ms = brief.get("latency_ms", 0)
        bullets = brief.get("narrative_bullets", [])

        bullets_html = "".join([
            f'<div style="margin-bottom:6px;font-size:13.5px;color:#E2E8F0;line-height:1.5;">🔹 {b}</div>'
            for b in bullets
        ])

        # 0. BANNER EJECUTIVO & TERMÓMETRO CUANTITATIVO 360°
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#0B111E 0%,#0F172A 60%,#090D16 100%);border:1px solid #1E293B;border-left:5px solid {reg_col};border-radius:12px;padding:20px 24px;margin-bottom:18px;box-shadow:0 8px 28px rgba(0,0,0,0.45);">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px;margin-bottom:14px;">'
            f'<div>'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
            f'<span style="background:{reg_col}22;color:{reg_col};border:1px solid {reg_col}66;font-size:11px;font-weight:800;padding:3px 9px;border-radius:4px;letter-spacing:0.05em;">LIVE 360° INTELLIGENCE DESK</span>'
            f'<span style="color:#94A3B8;font-family:monospace;font-size:12px;">⏱️ Actualizado: {gen_ts} ({lat_ms} ms)</span>'
            f'</div>'
            f'<h2 style="margin:0;font-size:23px;font-weight:800;color:#F8FAFC;">🧠 Resumen Ejecutivo Diario en Tiempo Real</h2>'
            f'<div style="font-size:15px;font-weight:800;color:{reg_col};margin-top:4px;">{reg_lbl}</div>'
            f'</div>'
            f'<div style="background:#080C14;border:1px solid #1E293B;border-radius:10px;padding:10px 18px;text-align:center;min-width:170px;">'
            f'<div style="font-size:10.5px;color:#94A3B8;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">SCORE CUANTITATIVO 360°</div>'
            f'<div style="font-size:28px;font-weight:900;color:{reg_col};font-family:monospace;line-height:1.2;">{score_v:.1f}<span style="font-size:14px;color:#64748B;">/100</span></div>'
            f'<div style="width:100%;height:6px;background:#1E293B;border-radius:3px;overflow:hidden;margin-top:6px;">'
            f'<div style="width:{score_v}%;height:100%;background:{reg_col};"></div></div>'
            f'</div></div>'
            f'<div style="background:rgba(15,23,42,0.75);border:1px solid #1E293B;border-radius:8px;padding:14px 18px;margin-bottom:12px;">'
            f'<div style="font-size:12px;font-weight:800;color:#38BDF8;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">📋 SÍNTESIS EJECUTIVA MULTIDIMENSIONAL DEL DÍA</div>'
            f'{bullets_html}'
            f'</div>'
            f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:10px 16px;font-size:13px;color:#F8FAFC;">'
            f'🎯 <b>Plan de Acción Táctico Sugerido:</b> {stance_txt}'
            f'</div></div>',
            unsafe_allow_html=True
        )

        # 1. PILAR 1: PULSO MACRO & ÍNDICES GLOBALES
        st.markdown("### 🌍 1. Pulso Macro, Índices & Activos Cruzados en Vivo")
        macro_items = brief.get("macro_pulse", [])
        if macro_items:
            m_cols = st.columns(min(9, len(macro_items)))
            for idx_m, m_it in enumerate(macro_items[:9]):
                with m_cols[idx_m]:
                    c_col = "#00FF87" if m_it["chg_today"] >= 0 else "#FB7185"
                    op_col = "#34D399" if m_it["chg_from_open"] >= 0 else "#F43F5E"
                    vw_badge = "🟢 >VWAP" if m_it["pct_from_vwap"] >= 0 else "🔴 <VWAP"
                    st.markdown(
                        f'<div style="background:#0B111E;border:1px solid #1E293B;border-top:3px solid {c_col};border-radius:8px;padding:10px 10px;margin-bottom:10px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                        f'<span style="font-family:monospace;font-size:14px;font-weight:800;color:#F8FAFC;">{m_it["symbol"]}</span>'
                        f'<span style="font-size:10px;color:#94A3B8;">{vw_badge}</span></div>'
                        f'<div style="font-size:10.5px;color:#64748B;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:4px;">{m_it["name"]}</div>'
                        f'<div style="font-family:monospace;font-size:15px;font-weight:800;color:#FFFFFF;">${m_it["price"]:,.2f}</div>'
                        f'<div style="font-family:monospace;font-size:12.5px;font-weight:700;color:{c_col};">{m_it["chg_today"]:+.2f}% <span style="font-size:10px;color:#64748B;">Hoy</span></div>'
                        f'<div style="font-family:monospace;font-size:11px;color:{op_col};margin-top:2px;">{m_it["chg_from_open"]:+.2f}% Open • {m_it["rvol_20d"]:.1f}x Vol</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # 2. PILAR 2: GAMMA EXPOSURE (GEX) & POSICIONAMIENTO DE DEALERS EN ÍNDICES (CBOE)
        st.markdown("### 🎯 2. Gamma Exposure (GEX) & Niveles Clave de Opciones en Índices (CBOE Live)")
        gex_items = brief.get("gex_indices", [])
        if gex_items:
            g_cols = st.columns(len(gex_items))
            for idx_g, g_it in enumerate(gex_items):
                with g_cols[idx_g]:
                    g_col = g_it["color"]
                    pos_pct = g_it["pos_in_corridor"]
                    st.markdown(
                        f'<div style="background:#0B111E;border:1px solid #1E293B;border-left:4px solid {g_col};border-radius:10px;padding:14px 16px;margin-bottom:10px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
                        f'<span style="font-family:monospace;font-size:17px;font-weight:800;color:#F8FAFC;">{g_it["symbol"]} • Spot ${g_it["spot"]:,.2f}</span>'
                        f'<span style="background:{g_col}22;color:{g_col};border:1px solid {g_col}66;font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:4px;">{g_it["regime_short"].upper()}</span>'
                        f'</div>'
                        f'<div style="font-size:12px;color:{g_col};font-weight:700;margin-bottom:10px;">{g_it["regime"]}</div>'
                        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;background:#080C14;padding:8px 10px;border-radius:6px;border:1px solid #182030;font-family:monospace;margin-bottom:10px;">'
                        f'<div><div style="font-size:10px;color:#FB7185;">🔴 PUT WALL</div><div style="font-size:13.5px;font-weight:800;color:#F8FAFC;">${g_it["put_wall"]:,.0f}</div></div>'
                        f'<div><div style="font-size:10px;color:#FBBF24;">⚡ GAMMA FLIP</div><div style="font-size:13.5px;font-weight:800;color:#FBBF24;">${g_it["gamma_flip"]:,.1f}</div></div>'
                        f'<div><div style="font-size:10px;color:#00FF87;">🟢 CALL WALL</div><div style="font-size:13.5px;font-weight:800;color:#F8FAFC;">${g_it["call_wall"]:,.0f}</div></div>'
                        f'</div>'
                        f'<div style="font-size:11px;color:#94A3B8;margin-bottom:4px;display:flex;justify-content:space-between;">'
                        f'<span>Ubicación en Corredor GEX (Put Wall → Call Wall)</span>'
                        f'<span style="font-family:monospace;color:#38BDF8;font-weight:700;">{pos_pct:.0f}%</span></div>'
                        f'<div style="position:relative;width:100%;height:8px;background:#1E293B;border-radius:4px;overflow:hidden;margin-bottom:10px;">'
                        f'<div style="width:{pos_pct}%;height:100%;background:linear-gradient(90deg,#FB7185,#FBBF24,#00FF87);"></div></div>'
                        f'<div style="display:flex;justify-content:space-between;font-family:monospace;font-size:11.5px;color:#CBD5E1;border-top:1px solid #1E293B;padding-top:8px;">'
                        f'<span>Net GEX: <b style="color:{g_col};">${g_it["net_gex_m"]:+,.1f}M</b></span>'
                        f'<span>Call GEX: <b style="color:#00FF87;">${g_it["call_gex_m"]:+,.0f}M</b></span>'
                        f'<span>Put GEX: <b style="color:#FB7185;">${g_it["put_gex_m"]:+,.0f}M</b></span>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.info("Sincronizando cadenas de opciones CBOE...")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # 3. PILAR 3 & 4: MARKET BREADTH + ROTACIÓN DE CAPITAL (TEMÁTICAS & RRG)
        col_br_sec, col_rot_sec = st.columns([1.05, 1.35], gap="medium")

        with col_br_sec:
            st.markdown("### 📊 3. Market Breadth & Weinstein Stages")
            b_info = brief.get("breadth", {})
            if b_info:
                nh_nl = b_info.get("new_highs_lows", {"ratio_pct": 50, "highs": 0, "lows": 0})
                ad = b_info.get("advance_decline", {"ratio_pct": 50, "advance": 0, "decline": 0})
                up_op = b_info.get("up_down_open", {"ratio_pct": 50, "up": 0, "down": 0})
                up_vol = b_info.get("up_down_volume", {"ratio_pct": 50, "up": 0, "down": 0})
                up_4 = b_info.get("up_down_4pct", {"ratio_pct": 50, "up": 0, "down": 0})
                stages = b_info.get("stages", {"s1": {"pct": 20, "count": 0}, "s2": {"pct": 45, "count": 0}, "s3": {"pct": 20, "count": 0}, "s4": {"pct": 15, "count": 0}})

                breadth_rows = [
                    ("Advance vs Decline", ad["ratio_pct"], f"{ad['advance']} Adv", f"{ad['decline']} Dec"),
                    ("New Highs vs New Lows", nh_nl["ratio_pct"], f"{nh_nl['highs']} Highs", f"{nh_nl['lows']} Lows"),
                    ("Up vs Down desde Apertura", up_op["ratio_pct"], f"{up_op['up']} Up Open", f"{up_op['down']} Down Open"),
                    ("Up Volume vs Down Volume", up_vol["ratio_pct"], f"{up_vol['up']} Up Vol", f"{up_vol['down']} Down Vol"),
                    ("Explosión +4% vs -4% Hoy", up_4["ratio_pct"], f"{up_4['up']} (+4%)", f"{up_4['down']} (-4%)")
                ]

                b_bars_html = []
                for lbl_b, pct_b, left_txt, right_txt in breadth_rows:
                    p_col = "#00FF87" if pct_b >= 50 else "#FB7185"
                    b_bars_html.append(
                        f'<div style="margin-bottom:10px;">'
                        f'<div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:3px;">'
                        f'<span style="color:#E2E8F0;">{lbl_b}</span>'
                        f'<span style="font-family:monospace;color:{p_col};">{pct_b}% ({left_txt} / {right_txt})</span></div>'
                        f'<div style="display:flex;width:100%;height:7px;background:#1E293B;border-radius:4px;overflow:hidden;">'
                        f'<div style="width:{pct_b}%;height:100%;background:linear-gradient(90deg,#10B981,#00FF87);"></div>'
                        f'<div style="width:{100-pct_b}%;height:100%;background:linear-gradient(90deg,#F43F5E,#FB7185);"></div>'
                        f'</div></div>'
                    )

                s1_p = stages["s1"]["pct"]
                s2_p = stages["s2"]["pct"]
                s3_p = stages["s3"]["pct"]
                s4_p = stages["s4"]["pct"]

                st.markdown(
                    f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:10px;padding:16px 18px;">'
                    f'{"".join(b_bars_html)}'
                    f'<div style="border-top:1px solid #1E293B;padding-top:12px;margin-top:8px;">'
                    f'<div style="font-size:12.5px;font-weight:800;color:#F8FAFC;margin-bottom:6px;">📐 Ciclos de Stan Weinstein (4 Etapas)</div>'
                    f'<div style="display:flex;width:100%;height:10px;background:#1E293B;border-radius:5px;overflow:hidden;margin-bottom:8px;">'
                    f'<div style="width:{s1_p}%;height:100%;background:#64748B;"></div>'
                    f'<div style="width:{s2_p}%;height:100%;background:#38BDF8;"></div>'
                    f'<div style="width:{s3_p}%;height:100%;background:#FBBF24;"></div>'
                    f'<div style="width:{s4_p}%;height:100%;background:#FB7185;"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-family:monospace;font-size:11px;">'
                    f'<span style="color:#94A3B8;">● S1 Base: {s1_p}%</span>'
                    f'<span style="color:#38BDF8;font-weight:700;">● S2 Alcista: {s2_p}%</span>'
                    f'<span style="color:#FBBF24;">● S3 Techo: {s3_p}%</span>'
                    f'<span style="color:#FB7185;">● S4 Bajista: {s4_p}%</span>'
                    f'</div></div></div>',
                    unsafe_allow_html=True
                )

        with col_rot_sec:
            st.markdown("### 🔄 4. Rotación de Capital (Temáticas & Cuadrantes RRG)")
            rot = brief.get("rotation", {})
            top_th = rot.get("top_themes", [])
            bot_th = rot.get("bottom_themes", [])
            sec_rrg = rot.get("sectors_rrg", {})
            mtm_rrg = rot.get("leaders_rrg", {})

            th_top_badges = "".join([
                f'<span style="display:inline-block;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.4);color:#00FF87;font-family:monospace;font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:4px;margin-right:6px;margin-bottom:6px;">🔥 {t["Theme"]} ({t["ETF"]} {t["FormattedChange"]})</span>'
                for t in top_th[:6]
            ])
            th_bot_badges = "".join([
                f'<span style="display:inline-block;background:rgba(244,63,94,0.12);border:1px solid rgba(244,63,94,0.4);color:#FB7185;font-family:monospace;font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:4px;margin-right:6px;margin-bottom:6px;">❄️ {t["Theme"]} ({t["ETF"]} {t["FormattedChange"]})</span>'
                for t in bot_th[:5]
            ])

            sec_lead_str = ", ".join([f"{s['symbol']} ({s['name']})" for s in sec_rrg.get("Leading", [])]) or "Ninguno"
            sec_imp_str = ", ".join([f"{s['symbol']} ({s['name']})" for s in sec_rrg.get("Improving", [])]) or "Ninguno"
            sec_weak_str = ", ".join([f"{s['symbol']} ({s['name']})" for s in sec_rrg.get("Weakening", [])]) or "Ninguno"
            sec_lag_str = ", ".join([f"{s['symbol']} ({s['name']})" for s in sec_rrg.get("Lagging", [])]) or "Ninguno"

            mtm_lead_str = ", ".join([s["symbol"] for s in mtm_rrg.get("Leading", [])[:12]]) or "Ninguno"
            mtm_imp_str = ", ".join([s["symbol"] for s in mtm_rrg.get("Improving", [])[:12]]) or "Ninguno"

            st.markdown(
                f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:10px;padding:16px 18px;">'
                f'<div style="font-size:12px;font-weight:800;color:#00FF87;margin-bottom:6px;">🚀 TOP TEMÁTICAS LÍDERES HOY (ENTRADA DE CAPITAL)</div>'
                f'<div style="margin-bottom:10px;">{th_top_badges}</div>'
                f'<div style="font-size:12px;font-weight:800;color:#FB7185;margin-bottom:6px;">🔻 TEMÁTICAS REZAGADAS HOY (SALIDA DE CAPITAL)</div>'
                f'<div style="margin-bottom:12px;">{th_bot_badges}</div>'
                f'<div style="border-top:1px solid #1E293B;padding-top:10px;font-size:12px;line-height:1.6;">'
                f'<div style="font-weight:800;color:#F8FAFC;margin-bottom:4px;">🧭 RRG Sectores S&amp;P 500 (3M Diario vs $SPX):</div>'
                f'<div><b style="color:#00FF87;">🟢 Leading:</b> <span style="color:#E2E8F0;font-family:monospace;">{sec_lead_str}</span></div>'
                f'<div><b style="color:#38BDF8;">🔵 Improving (Giro Alcista):</b> <span style="color:#E2E8F0;font-family:monospace;">{sec_imp_str}</span></div>'
                f'<div><b style="color:#FBBF24;">🟡 Weakening:</b> <span style="color:#94A3B8;font-family:monospace;">{sec_weak_str}</span></div>'
                f'<div><b style="color:#FB7185;">🔴 Lagging:</b> <span style="color:#94A3B8;font-family:monospace;">{sec_lag_str}</span></div>'
                f'<div style="margin-top:8px;padding-top:8px;border-top:1px dashed #1E293B;">'
                f'<b style="color:#00FF87;">🏆 Líderes MTM Watchlist en Cuadrante Leading:</b> <span style="font-family:monospace;color:#38BDF8;">{mtm_lead_str}</span><br>'
                f'<b style="color:#38BDF8;">⚡ Líderes MTM Giran en Improving:</b> <span style="font-family:monospace;color:#CBD5E1;">{mtm_imp_str}</span>'
                f'</div></div></div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # 5. PILAR 5: SMART MONEY, FLUJO INSTITUCIONAL & ACTIVOS MÁS RELEVANTES HOY
        st.markdown("### 🐋 5. Smart Money, Flujo Institucional & Activos Más Relevantes Hoy")
        sm = brief.get("smart_money", {})
        p_leaders = sm.get("power_leaders", [])
        u_rvol = sm.get("unusual_rvol", [])
        ins_buys = sm.get("insider_buys", [])

        sm_c1, sm_c2 = st.columns([1.45, 1.0], gap="medium")
        with sm_c1:
            st.markdown("#### 🔥 Top 10 Activos Más Relevantes Hoy (Power Leaders de Filtros Actualizados)")
            if p_leaders:
                df_pl = pd.DataFrame(p_leaders)[["symbol", "price", "chg_today", "chg_from_open", "rvol_20d", "pct_from_vwap", "rs_1m", "dollar_vol_m"]].copy()
                df_pl.columns = ["Ticker", "Precio ($)", "% Chg Hoy", "% Desde Open", "RVOL 20d (x)", "% vs VWAP", "RS 1M", "$ Vol (M)"]
                st.dataframe(df_pl, use_container_width=True, hide_index=True)
            else:
                st.info("Calculando líderes intradía de tus filtros cuantitativos...")

        with sm_c2:
            rvol_pills = "".join([
                f'<span style="display:inline-block;background:#1E293B;border:1px solid #38BDF866;color:#38BDF8;font-family:monospace;font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:4px;margin-right:6px;margin-bottom:6px;">${r["symbol"]} • {r["rvol_20d"]:.2f}x RVOL ({r["chg_today"]:+.2f}%)</span>'
                for r in u_rvol[:8]
            ])
            ins_rows = "".join([
                f'<div style="font-size:11.5px;color:#CBD5E1;margin-bottom:4px;font-family:monospace;">• <b style="color:#00FF87;">${ib["ticker"]}</b> ({ib["owner_name"]} - {ib["officer_title"]}): Compra <b>${ib["transaction_value"]:,.0f}</b> @ ${ib["transaction_price_per_share"]:.2f}</div>'
                for ib in ins_buys[:4]
            ])
            st.markdown(
                f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:10px;padding:16px 18px;">'
                f'<div style="font-size:12px;font-weight:800;color:#38BDF8;margin-bottom:8px;">⚡ HUELLA DE VOLUMEN INUSUAL (TOP RVOL 20D)</div>'
                f'<div style="margin-bottom:12px;">{rvol_pills}</div>'
                f'<div style="border-top:1px solid #1E293B;padding-top:10px;margin-bottom:10px;display:flex;justify-content:space-between;font-family:monospace;font-size:12px;">'
                f'<span>🏦 <b>NAAIM Exposure:</b> <b style="color:#00FF87;">{sm.get("naaim_index", 87.7)}%</b> ({sm.get("naaim_stance", "Neutral")})</span>'
                f'<span>📊 <b>AAII Spread:</b> <b style="color:#FBBF24;">{sm.get("aaii_spread", -2.9):+.1f}%</b></span></div>'
                f'<div style="border-top:1px solid #1E293B;padding-top:10px;">'
                f'<div style="font-size:12px;font-weight:800;color:#A78BFA;margin-bottom:6px;">🏛️ COMPRAS DISCRECIONALES DE INSIDERS (SEC FORM 4)</div>'
                f'{ins_rows}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # 6. PILAR 6: TOP STORIES & BREAKING NEWS WIRE
        st.markdown("### 📰 6. Top Stories & Cables Institucionales de Alto Impacto")
        nw = brief.get("news", {})
        top_n_items = nw.get("top_items", [])
        top_n_tickers = nw.get("top_tickers", [])

        if top_n_tickers:
            tk_badges = "".join([
                f'<span style="display:inline-block;background:#1E293B;border:1px solid #334155;color:#38BDF8;font-family:monospace;font-size:12px;font-weight:700;padding:2px 8px;border-radius:4px;margin-right:6px;margin-bottom:4px;">${tk} <span style="color:#94A3B8;font-size:10px;">({cnt})</span></span>'
                for tk, cnt in top_n_tickers
            ])
            st.markdown(
                f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:8px;padding:10px 14px;margin-bottom:12px;">'
                f'<span style="color:#94A3B8;font-size:11.5px;font-weight:700;margin-right:10px;">🔥 TICKERS EN FOCO INFORMATIVO HOY:</span>{tk_badges}</div>',
                unsafe_allow_html=True
            )

        if top_n_items:
            nc1, nc2 = st.columns(2, gap="medium")
            for idx_n, it in enumerate(top_n_items[:8]):
                target_col = nc1 if idx_n % 2 == 0 else nc2
                with target_col:
                    safe_t = html.escape(it.get("title", ""))
                    t_pills = "".join([
                        f'<span style="background:rgba(56,189,248,0.15);color:#38BDF8;font-family:monospace;font-size:10.5px;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:4px;">${tk}</span>'
                        for tk in it.get("tickers", [])
                    ])
                    cat_str = " • ".join(it.get("categories", [])[:2])
                    st.markdown(
                        f'<div style="background:#0B111E;border:1px solid #1E293B;border-left:3px solid {it["color"]};border-radius:8px;padding:12px 14px;margin-bottom:10px;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;font-size:11px;">'
                        f'<span style="color:{it["color"]};font-weight:800;">{it["icon"]} {it["source_badge"]} • <span style="color:#94A3B8;">{cat_str}</span></span>'
                        f'<span style="color:#64748B;font-family:monospace;">{it["time_ago"]}</span></div>'
                        f'<div style="margin-bottom:6px;"><a href="{it["link"]}" target="_blank" style="color:#F8FAFC;text-decoration:none;font-size:14px;font-weight:700;line-height:1.35;">{safe_t}</a></div>'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                        f'<div>{t_pills}</div>'
                        f'<a href="{it["link"]}" target="_blank" style="color:#38BDF8;font-size:11px;text-decoration:none;font-weight:600;">Abrir cable ↗</a>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

# =====================================================================
# VISTA 1: 🏠 DASHBOARD DE MERCADO (PÁGINA INICIAL)
# =====================================================================
elif nav_view == "🏠 Dashboard de Mercado":
    # Top Bar Header
    col_dash_title, col_dash_status = st.columns([2.5, 1.5])
    with col_dash_title:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 26px; font-weight: 800; color: #FFFFFF;">🏠 Market Overview & Internal Health</span>
            <span class="badge-neon-bull">LIVE DESK</span>
        </div>
        <div style="font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-top: -2px; margin-bottom: 12px;">
            SECTORES TEMÁTICOS • AMPLITUD DE MERCADO • WEINSTEIN STAGE ANALYSIS
        </div>
        """, unsafe_allow_html=True)
    with col_dash_status:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; gap: 8px; align-items: center; padding-top: 6px;">
            <span class="badge-neon-cyan">FEED: {provider_str.upper()}</span>
            <span class="badge-neon-bull">TEMÁTICAS: 31</span>
            <span class="badge-neon-cyan">BREADTH: 200 LÍDERES</span>
        </div>
        """, unsafe_allow_html=True)

    col_theme_col, col_chart_breadth = st.columns([1.15, 1.85], gap="medium")

    # ------------------ COLUMNA IZQUIERDA: THEME TRACKER ------------------
    with col_theme_col:
        # Header del Theme Tracker
        col_tt_title, col_tt_tf = st.columns([1.2, 1.8])
        with col_tt_title:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 6px; padding-top: 4px;">
                <span style="font-size: 18px;">🔥</span>
                <span style="font-size: 16px; font-weight: 800; color: #FFFFFF;">Theme Tracker</span>
            </div>
            """, unsafe_allow_html=True)
        with col_tt_tf:
            theme_tf = st.selectbox(
                "Timeframe:",
                ["Today", "1W", "1M", "3M", "YTD"],
                index=0,
                key="theme_tf_select",
                label_visibility="collapsed"
            )

        # Estado de si hay una temática seleccionada para drill-down
        active_theme = st.session_state.get("selected_theme", None)

        if active_theme is not None:
            # MODO DRILL-DOWN: VER ACCIONES DE LA TEMÁTICA
            col_back, col_th_head = st.columns([0.8, 2.2])
            with col_back:
                if st.button("← Temáticas", key="btn_back_themes", use_container_width=True):
                    st.session_state["selected_theme"] = None
                    st.rerun()
            with col_th_head:
                etf_proxy = mde.THEMES_CATALOG.get(active_theme, {}).get("etf", "")
                st.markdown(f"""
                <div style="font-size: 14px; font-weight: 800; color: #00F0FF; padding-top: 6px;">
                    {active_theme} <span style="font-size: 11px; color: #94A3B8;">({etf_proxy})</span>
                </div>
                """, unsafe_allow_html=True)

            with st.spinner(f"Cargando acciones de {active_theme}..."):
                const_df = mde.fetch_theme_constituents(active_theme, timeframe=theme_tf)

            if const_df.empty:
                st.info(f"No se pudieron cargar datos para {active_theme}.")
            else:
                st.caption(f"{len(const_df)} acciones seguidas en **{active_theme}**")
                
                # Renderizar acciones con barras horizontales
                for _, row in const_df.iterrows():
                    t_ticker = row["Ticker"]
                    t_price = row["Price"]
                    t_chg = row["ChangePct"]
                    t_fmt = row["FormattedChange"]
                    t_dir = row["Direction"]
                    t_bar = row["BarWidthPct"]

                    col_s_tick, col_s_bar, col_s_val, col_s_act = st.columns([1.1, 1.8, 1.1, 0.8])
                    with col_s_tick:
                        st.markdown(f"""
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: #FFFFFF; padding-top: 6px;">
                            {t_ticker} <span style="font-size: 10px; color: #64748B;">${t_price:.2f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s_bar:
                        bar_color = "linear-gradient(90deg, #3B82F6, #00FF87)" if t_dir == "pos" else "linear-gradient(90deg, #F43F5E, #EC4899)"
                        st.markdown(f"""
                        <div style="padding-top: 10px;">
                            <div style="width: 100%; height: 7px; background: #151B28; border-radius: 4px; overflow: hidden;">
                                <div style="width: {t_bar}%; height: 100%; background: {bar_color}; border-radius: 4px;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s_val:
                        val_color = "#00FF87" if t_dir == "pos" else "#EC4899"
                        st.markdown(f"""
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: {val_color}; text-align: right; padding-top: 6px;">
                            {t_fmt}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s_act:
                        if st.button("📊", key=f"btn_chart_stock_{t_ticker}", help=f"Graficar {t_ticker}"):
                            st.session_state["dash_chart_ticker"] = t_ticker
                            st.rerun()

        else:
            # MODO OVERVIEW: VER TODAS LAS 31 TEMÁTICAS
            with st.spinner("Cargando rendimiento de 31 temáticas..."):
                themes_df = mde.fetch_themes_performance(timeframe=theme_tf)

            if themes_df.empty:
                st.info("Cargando temáticas de mercado...")
            else:
                # Buscador rápido de temática
                theme_search = st.text_input("🔍 Filtrar Temáticas:", placeholder="Ej. Crypto, Software, Semi...", label_visibility="collapsed")
                filtered_themes = themes_df
                if theme_search:
                    filtered_themes = themes_df[themes_df["Theme"].str.lower().str.contains(theme_search.lower()) | themes_df["ETF"].str.lower().str.contains(theme_search.lower())]

                st.markdown(f"<div style='font-size: 11px; color: #64748B; font-weight: 700; margin-bottom: 8px;'>31 RESULTADOS ({theme_tf.upper()})</div>", unsafe_allow_html=True)

                # Renderizado de lista de temáticas con diverging bars
                for _, row in filtered_themes.iterrows():
                    th_name = row["Theme"]
                    th_etf = row["ETF"]
                    th_chg = row["ChangePct"]
                    th_fmt = row["FormattedChange"]
                    th_dir = row["Direction"]
                    th_bar = row["BarWidthPct"]

                    col_t_info, col_t_bar, col_t_val, col_t_btn = st.columns([1.6, 1.5, 1.1, 0.7])
                    with col_t_info:
                        st.markdown(f"""
                        <div style="font-size: 12px; font-weight: 700; color: #F1F5F9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-top: 6px;">
                            {th_name} <span style="font-size: 10px; color: #64748B; font-family: 'JetBrains Mono', monospace;">{th_etf}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_t_bar:
                        # Barra divergente centrada con línea de referencia 0% (estilos inline blindados)
                        fill_w = min(50.0, max(2.5, th_bar * 0.5))
                        if th_dir == "pos":
                            bar_fill = f'<div style="position: absolute; left: 50%; top: 0; bottom: 0; width: {fill_w:.1f}%; background: linear-gradient(90deg, #10B981, #00FF87); border-radius: 0 4px 4px 0; z-index: 1;"></div>'
                        else:
                            bar_fill = f'<div style="position: absolute; right: 50%; top: 0; bottom: 0; width: {fill_w:.1f}%; background: linear-gradient(270deg, #F43F5E, #FF2E63); border-radius: 4px 0 0 4px; z-index: 1;"></div>'

                        st.markdown(f"""
                        <div style="padding-top: 10px; padding-bottom: 6px;">
                            <div style="position: relative; width: 100%; height: 8px; background: rgba(255, 255, 255, 0.08); border-radius: 4px; overflow: hidden;">
                                <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: rgba(255, 255, 255, 0.35); z-index: 2;"></div>
                                {bar_fill}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_t_val:
                        val_color = "#00FF87" if th_dir == "pos" else "#EC4899"
                        st.markdown(f"""
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: {val_color}; text-align: right; padding-top: 6px;">
                            {th_fmt}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_t_btn:
                        if st.button("🔍", key=f"btn_open_{th_name}", help=f"Explorar acciones de {th_name}"):
                            st.session_state["selected_theme"] = th_name
                            st.session_state["dash_chart_ticker"] = th_etf
                            st.rerun()

    # ------------------ COLUMNA DERECHA: GRÁFICO + AMPLITUD DE MERCADO ------------------
    with col_chart_breadth:
        # 1. GRÁFICO INTERACTIVO DE MERCADO
        current_chart_ticker = st.session_state.get("dash_chart_ticker", "SPY")

        # Barra rápida de índices
        col_idx_btns = st.columns([1, 1, 1, 1, 1, 1.8])
        indices = [("SPY", "S&P 500"), ("QQQ", "Nasdaq"), ("IWM", "Russell"), ("SMH", "Semis"), ("IBIT", "Bitcoin")]
        for idx_i, (t_sym, t_lbl) in enumerate(indices):
            with col_idx_btns[idx_i]:
                is_active = (current_chart_ticker == t_sym)
                btn_type = "primary" if is_active else "secondary"
                if st.button(t_sym, key=f"dash_idx_{t_sym}", type=btn_type, use_container_width=True):
                    st.session_state["dash_chart_ticker"] = t_sym
                    st.rerun()
        with col_idx_btns[5]:
            custom_chart_sym = st.text_input("Símbolo:", value=current_chart_ticker, label_visibility="collapsed")
            if custom_chart_sym and custom_chart_sym.upper() != current_chart_ticker:
                st.session_state["dash_chart_ticker"] = custom_chart_sym.upper()
                st.rerun()

        # Renderizar gráfico de velas institucionales
        render_institutional_chart(current_chart_ticker, key_suffix="dash_main")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        with st.spinner("Calculando amplitud global del mercado (NYSE + NASDAQ)..."):
            breadth_data = mde.fetch_market_breadth(provider=provider_str, alpaca_key=alpaca_key, alpaca_secret=alpaca_secret)

        if breadth_data:
            univ_name = breadth_data.get("universe_name", "NYSE + NASDAQ (5,000+ Acciones)")
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 18px;">📊</span>
                    <span style="font-size: 16px; font-weight: 800; color: #FFFFFF;">Market Breadth & Internals</span>
                </div>
                <span class="badge-neon-bull">● UNIVERSO: {univ_name.upper()}</span>
            </div>
            """, unsafe_allow_html=True)

            # 5 Tarjetas de Ratios de Amplitud (Grid 2 columnas)
            b_col1, b_col2 = st.columns(2)

            nh_nl = breadth_data["new_highs_lows"]
            ad = breadth_data["advance_decline"]
            up_dn_op = breadth_data["up_down_open"]
            up_dn_vol = breadth_data["up_down_volume"]
            up_dn_4 = breadth_data["up_down_4pct"]

            with b_col1:
                # 1. New Highs vs New Lows (Barra Dual Bicolor Proporcional)
                r_nh = nh_nl["ratio_pct"]
                cls_nh = "breadth-ratio-pos" if r_nh >= 50 else "breadth-ratio-neg"
                st.markdown(f"""
                <div class="breadth-card">
                    <div class="breadth-header">
                        <span class="breadth-title">New Highs vs New Lows</span>
                        <span class="{cls_nh}">{r_nh}%</span>
                    </div>
                    <div class="breadth-track" style="display:flex; width:100%; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; margin:8px 0;">
                        <div class="breadth-fill-pos" style="width:{r_nh}%; height:100%; background:linear-gradient(90deg, #10B981, #00FF87); border-radius:4px 0 0 4px;" title="Highs: {r_nh}%"></div>
                        <div class="breadth-fill-neg" style="width:{100 - r_nh}%; height:100%; background:linear-gradient(90deg, #FF2E63, #F43F5E); border-radius:0 4px 4px 0;" title="Lows: {100 - r_nh}%"></div>
                    </div>
                    <div class="breadth-footer">
                        <span><strong style="color:#00FF87;">{nh_nl['highs']:,}</strong> Highs</span>
                        <span><strong style="color:#FF2E63;">{nh_nl['lows']:,}</strong> Lows</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 3. Up from Open vs Down from Open
                r_op = up_dn_op["ratio_pct"]
                cls_op = "breadth-ratio-pos" if r_op >= 50 else "breadth-ratio-neg"
                st.markdown(f"""
                <div class="breadth-card">
                    <div class="breadth-header">
                        <span class="breadth-title">Up from Open vs Down from Open</span>
                        <span class="{cls_op}">{r_op}%</span>
                    </div>
                    <div class="breadth-track" style="display:flex; width:100%; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; margin:8px 0;">
                        <div class="breadth-fill-pos" style="width:{r_op}%; height:100%; background:linear-gradient(90deg, #10B981, #00FF87); border-radius:4px 0 0 4px;" title="Up: {r_op}%"></div>
                        <div class="breadth-fill-neg" style="width:{100 - r_op}%; height:100%; background:linear-gradient(90deg, #FF2E63, #F43F5E); border-radius:0 4px 4px 0;" title="Down: {100 - r_op}%"></div>
                    </div>
                    <div class="breadth-footer">
                        <span><strong style="color:#00FF87;">{up_dn_op['up']:,}</strong> Up</span>
                        <span><strong style="color:#FF2E63;">{up_dn_op['down']:,}</strong> Down</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 5. Up 4% vs Down 4%
                r_4 = up_dn_4["ratio_pct"]
                cls_4 = "breadth-ratio-pos" if r_4 >= 50 else "breadth-ratio-neg"
                st.markdown(f"""
                <div class="breadth-card">
                    <div class="breadth-header">
                        <span class="breadth-title">Up 4% vs Down 4%</span>
                        <span class="{cls_4}">{r_4}%</span>
                    </div>
                    <div class="breadth-track" style="display:flex; width:100%; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; margin:8px 0;">
                        <div class="breadth-fill-pos" style="width:{r_4}%; height:100%; background:linear-gradient(90deg, #10B981, #00FF87); border-radius:4px 0 0 4px;" title="Up 4%: {r_4}%"></div>
                        <div class="breadth-fill-neg" style="width:{100 - r_4}%; height:100%; background:linear-gradient(90deg, #FF2E63, #F43F5E); border-radius:0 4px 4px 0;" title="Down 4%: {100 - r_4}%"></div>
                    </div>
                    <div class="breadth-footer">
                        <span><strong style="color:#00FF87;">{up_dn_4['up']:,}</strong> Up</span>
                        <span><strong style="color:#FF2E63;">{up_dn_4['down']:,}</strong> Down</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with b_col2:
                # 2. Advance vs Decline
                r_ad = ad["ratio_pct"]
                cls_ad = "breadth-ratio-pos" if r_ad >= 50 else "breadth-ratio-neg"
                st.markdown(f"""
                <div class="breadth-card">
                    <div class="breadth-header">
                        <span class="breadth-title">Advance vs Decline</span>
                        <span class="{cls_ad}">{r_ad}%</span>
                    </div>
                    <div class="breadth-track" style="display:flex; width:100%; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; margin:8px 0;">
                        <div class="breadth-fill-pos" style="width:{r_ad}%; height:100%; background:linear-gradient(90deg, #10B981, #00FF87); border-radius:4px 0 0 4px;" title="Advance: {r_ad}%"></div>
                        <div class="breadth-fill-neg" style="width:{100 - r_ad}%; height:100%; background:linear-gradient(90deg, #FF2E63, #F43F5E); border-radius:0 4px 4px 0;" title="Decline: {100 - r_ad}%"></div>
                    </div>
                    <div class="breadth-footer">
                        <span><strong style="color:#00FF87;">{ad['advance']:,}</strong> Advance</span>
                        <span><strong style="color:#FF2E63;">{ad['decline']:,}</strong> Decline</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 4. Up on Volume vs Down on Volume
                r_vol = up_dn_vol["ratio_pct"]
                cls_vol = "breadth-ratio-pos" if r_vol >= 50 else "breadth-ratio-neg"
                st.markdown(f"""
                <div class="breadth-card">
                    <div class="breadth-header">
                        <span class="breadth-title">Up on Volume vs Down on Volume</span>
                        <span class="{cls_vol}">{r_vol}%</span>
                    </div>
                    <div class="breadth-track" style="display:flex; width:100%; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; margin:8px 0;">
                        <div class="breadth-fill-pos" style="width:{r_vol}%; height:100%; background:linear-gradient(90deg, #10B981, #00FF87); border-radius:4px 0 0 4px;" title="Up on Vol: {r_vol}%"></div>
                        <div class="breadth-fill-neg" style="width:{100 - r_vol}%; height:100%; background:linear-gradient(90deg, #FF2E63, #F43F5E); border-radius:0 4px 4px 0;" title="Down on Vol: {100 - r_vol}%"></div>
                    </div>
                    <div class="breadth-footer">
                        <span><strong style="color:#00FF87;">{up_dn_vol['up']:,}</strong> Up</span>
                        <span><strong style="color:#FF2E63;">{up_dn_vol['down']:,}</strong> Down</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # STAGE ANALYSIS (STAN WEINSTEIN)
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            stages = breadth_data["stages"]
            s1_p = stages["s1"]["pct"]
            s2_p = stages["s2"]["pct"]
            s3_p = stages["s3"]["pct"]
            s4_p = stages["s4"]["pct"]

            st.markdown(f"""
            <div style="background: #0E121B; border: 1px solid #182030; border-radius: 8px; padding: 14px 16px;">
                <div style="font-size: 13px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
                    Stage Analysis (Weinstein 4 Stages) • <span style="font-size: 11px; color: #64748B;">{breadth_data['total_stocks']:,} ACCIONES ANALIZADAS</span>
                </div>
                <!-- Barra Segmentada Multicolor Weinstein -->
                <div class="stage-track" style="display:flex; width:100%; height:9px; background:rgba(255,255,255,0.06); border-radius:5px; overflow:hidden; margin:10px 0 8px 0;">
                    <div class="stage-seg-1" style="width:{s1_p}%; height:100%; background:#64748B;" title="Stage 1: {s1_p}%"></div>
                    <div class="stage-seg-2" style="width:{s2_p}%; height:100%; background:linear-gradient(90deg, #2563EB, #38BDF8);" title="Stage 2: {s2_p}%"></div>
                    <div class="stage-seg-3" style="width:{s3_p}%; height:100%; background:#EAB308;" title="Stage 3: {s3_p}%"></div>
                    <div class="stage-seg-4" style="width:{s4_p}%; height:100%; background:linear-gradient(90deg, #EC4899, #F43F5E);" title="Stage 4: {s4_p}%"></div>
                </div>
                <!-- Leyenda de Etapas -->
                <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; font-family: 'JetBrains Mono', monospace; margin-top: 8px;">
                    <span style="color: #64748B;">● Stage 1: {stages['s1']['count']:,} · {s1_p}%</span>
                    <span style="color: #3B82F6;">● Stage 2: {stages['s2']['count']:,} · {s2_p}%</span>
                    <span style="color: #EAB308;">● Stage 3: {stages['s3']['count']:,} · {s3_p}%</span>
                    <span style="color: #EC4899;">● Stage 4: {stages['s4']['count']:,} · {s4_p}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # GRÁFICO HISTÓRICO: ETAPA 2 (ALCISTA) VS ETAPA 4 (BAJISTA)
            history_df = breadth_data.get("history_df", pd.DataFrame())
            if not history_df.empty:
                fig_breadth = go.Figure()
                fig_breadth.add_trace(go.Scatter(
                    x=history_df["Date"],
                    y=history_df["Stage 2 (Bullish)"],
                    mode="lines",
                    name="Stage 2 (Bullish Uptrend)",
                    line=dict(color="#3B82F6", width=2)
                ))
                fig_breadth.add_trace(go.Scatter(
                    x=history_df["Date"],
                    y=history_df["Stage 4 (Bearish)"],
                    mode="lines",
                    name="Stage 4 (Bearish Downtrend)",
                    line=dict(color="#EC4899", width=2)
                ))

                fig_breadth.update_layout(
                    template="plotly_dark",
                    height=240,
                    margin=dict(l=10, r=20, t=25, b=10),
                    paper_bgcolor="#0A0D14",
                    plot_bgcolor="#0A0D14",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=10, color="#94A3B8")
                    ),
                    yaxis=dict(
                        side="right",
                        gridcolor="#151C28",
                        zerolinecolor="#151C28",
                        ticksuffix="%",
                        tickfont=dict(family="JetBrains Mono", size=9, color="#94A3B8")
                    ),
                    xaxis=dict(
                        gridcolor="#151C28",
                        zerolinecolor="#151C28",
                        tickfont=dict(family="JetBrains Mono", size=9, color="#64748B")
                    )
                )
                st.plotly_chart(fig_breadth, width="stretch")


# =====================================================================
# VISTA: 📰 TOP STORIES & BREAKING NEWS DESK
# =====================================================================
elif "Top Stories" in nav_view or "Breaking News" in nav_view or "Noticias" in nav_view:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0B111E 0%, #0F172A 50%, #080D1A 100%); 
                border: 1px solid #1E293B; border-radius: 12px; padding: 22px 26px; margin-bottom: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="background: #E11D48; color: #FFF; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.05em;">LIVE WIRE</span>
                    <h2 style="margin: 0; font-size: 24px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">📰 Top Stories & Breaking News Desk</h2>
                </div>
                <div style="color: #94A3B8; font-size: 13.5px;">
                    Cables institucionales agregados en tiempo real: 
                    <span style="color: #F59E0B; font-weight: 600;">Bloomberg</span> • 
                    <span style="color: #06B6D4; font-weight: 600;">Benzinga</span> • 
                    <span style="color: #F97316; font-weight: 600;">Reuters</span> • 
                    <span style="color: #3B82F6; font-weight: 600;">CNBC</span> • 
                    <span style="color: #10B981; font-weight: 600;">MarketWatch</span> • 
                    <span style="color: #94A3B8; font-weight: 600;">Wall Street Journal</span> • 
                    <span style="color: #8B5CF6; font-weight: 600;">SEC EDGAR (8-K)</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; background: rgba(30,41,59,0.6); padding: 6px 12px; border-radius: 6px; border: 1px solid #334155;">
                    <span style="width: 8px; height: 8px; background: #10B981; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #10B981;"></span>
                    <span style="color: #CBD5E1; font-size: 12px; font-family: 'JetBrains Mono', monospace;">CABLES EN VIVO (LATENCIA &lt; 1s)</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if rne is None:
        st.error("⚠️ El módulo `realtime_news_engine` no se pudo cargar. Revisa que el archivo exista en el directorio de trabajo.")
    else:
        # Action bar: Refresh & Summary
        col_ref, col_info = st.columns([1, 4])
        with col_ref:
            btn_refresh = st.button("🔄 Refrescar Cables Ahora", key="btn_refresh_news_top", width="stretch")
        with col_info:
            cache_ts = rne._NEWS_CACHE.get("timestamp", 0)
            if cache_ts > 0:
                cache_str = datetime.fromtimestamp(cache_ts, tz=timezone.utc).strftime("%H:%M:%S UTC")
                st.caption(f"Última sincronización de fuentes: **{cache_str}** • Caché inteligente (60s TTL)")

        # Fetch items
        news_items = rne.fetch_all_news(force_refresh=btn_refresh)

        # Breaking Flash Ticker Tape (horizontal marquee)
        flash_items = [n for n in news_items if n.get("is_flash") or "🚨 FLASH" in n.get("categories", [])]
        if not flash_items:
            flash_items = news_items[:6]

        if flash_items:
            tape_spans = []
            for it in flash_items[:8]:
                t_esc = html.escape(it['title'][:85]) + ("..." if len(it['title']) > 85 else "")
                tape_spans.append(
                    f'<span style="display:inline-flex;align-items:center;gap:8px;">'
                    f'<span style="color:{it["color"]};font-weight:700;font-size:11px;">[{it["source_badge"]}]</span>'
                    f'<a href="{it["link"]}" target="_blank" style="color:#F8FAFC;text-decoration:none;font-weight:500;">{t_esc}</a>'
                    f'<span style="color:#64748B;font-size:11px;">• {it["time_ago"]}</span>'
                    f'<span style="color:#334155;margin-left:14px;">|</span>'
                    f'</span>'
                )
            tape_inner = "".join(tape_spans)
            tape_html = (
                f'<div style="background:#0F172A;border:1px solid #E11D48;border-radius:8px;padding:10px 14px;margin-bottom:20px;display:flex;align-items:center;overflow:hidden;">'
                f'<div style="background:#E11D48;color:#FFF;font-size:11px;font-weight:800;padding:4px 10px;border-radius:4px;margin-right:14px;white-space:nowrap;display:flex;align-items:center;gap:6px;">'
                f'<span style="width:6px;height:6px;background:#FFF;border-radius:50%;"></span>FLASH WIRE</div>'
                f'<div style="display:flex;gap:24px;overflow-x:auto;white-space:nowrap;font-size:13px;color:#F1F5F9;scrollbar-width:thin;">{tape_inner}</div>'
                f'</div>'
            )
            st.markdown(tape_html, unsafe_allow_html=True)

        # Top KPI Metrics Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        all_tickers = sorted(list({t for it in news_items for t in it.get("tickers", [])}))
        breaking_count = len([n for n in news_items if n.get("is_flash")])
        with kpi1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📡 CABLES EN VIVO</div>
                <div class="kpi-val" style="color: #38BDF8;">{len(news_items)}</div>
                <div class="kpi-sub">Noticias indexadas activas</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🚨 ALERTAS FLASH</div>
                <div class="kpi-val" style="color: #FB7185;">{breaking_count}</div>
                <div class="kpi-sub">Urgente / Market movers</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🏷️ TICKERS MENCIONADOS</div>
                <div class="kpi-val" style="color: #A78BFA;">{len(all_tickers)}</div>
                <div class="kpi-sub">Símbolos bursátiles detectados</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🏛️ FUENTES EN RED</div>
                <div class="kpi-val" style="color: #34D399;">8</div>
                <div class="kpi-sub">Bloomberg, Benzinga, SEC, etc.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Filters Bar
        st.markdown("### 🔍 Filtros & Búsqueda de Noticias")
        fcol1, fcol2, fcol3, fcol4 = st.columns([2.5, 1.2, 1.5, 1.5])
        with fcol1:
            search_query = st.text_input("Búsqueda libre por texto o titular:", value="", placeholder="Ej: chips, Powell, acquisition, crude oil...", key="input_news_search")
        with fcol2:
            search_ticker = st.text_input("Filtrar por Ticker ($):", value="", placeholder="TSLA, NVDA...", key="input_news_ticker")
        with fcol3:
            categories_list = ["Todas", "🚨 FLASH", "📊 Earnings", "🤝 M&A", "🎯 Analyst Ratings", "🏛️ Macro & Fed", "💻 Tech & AI", "🛢️ Commodities", "💊 FDA / Biotech", "🪙 Crypto", "🏦 Markets"]
            cat_selected = st.selectbox("Categoría Temática:", categories_list, index=0, key="select_news_cat")
        with fcol4:
            sources_list = ["Todas", "Bloomberg", "Benzinga", "Reuters", "CNBC", "CNBC Investing", "MarketWatch", "Wall Street Journal", "SEC EDGAR (8-K)"]
            source_selected = st.selectbox("Fuente / Agencia:", sources_list, index=0, key="select_news_source")

        # Ticker Cloud / Trend Badges
        if all_tickers:
            ticker_freq = {}
            for it in news_items:
                for tk in it.get("tickers", []):
                    ticker_freq[tk] = ticker_freq.get(tk, 0) + 1
            top_mentioned = sorted(ticker_freq.items(), key=lambda x: x[1], reverse=True)[:16]
            
            pills_spans = []
            for tk, count in top_mentioned:
                pills_spans.append(
                    f'<span style="display:inline-block;background:#1E293B;border:1px solid #334155;color:#38BDF8;font-family:monospace;font-size:12px;font-weight:700;padding:2px 8px;border-radius:4px;margin-right:6px;margin-bottom:4px;">'
                    f'${tk} <span style="color:#64748B;font-size:10px;font-weight:500;">({count})</span></span>'
                )
            pills_html = (
                f'<div style="background:rgba(15,23,42,0.6);border:1px solid #1E293B;border-radius:8px;padding:10px 14px;margin-bottom:20px;">'
                f'<span style="color:#94A3B8;font-size:11.5px;font-weight:700;margin-right:12px;letter-spacing:0.05em;">🔥 TICKERS MÁS MENCIONADOS EN LAS NOTICIAS HOY:</span>'
                f'{"".join(pills_spans)}</div>'
            )
            st.markdown(pills_html, unsafe_allow_html=True)

        # Perform Filtering
        filtered_items = rne.search_news(
            query=search_query,
            category=cat_selected,
            ticker=search_ticker,
            source=source_selected,
            force_refresh=False
        )

        st.caption(f"Mostrando **{len(filtered_items)}** cables que cumplen los criterios de filtrado.")

        # Pagination controls
        pcol1, pcol2 = st.columns([1, 4])
        with pcol1:
            items_per_page = st.selectbox("Cables por página:", [25, 50, 100, 200], index=1, key="sb_news_page_size")

        # Render News Cards with clean, non-indented contiguous HTML
        for it in filtered_items[:items_per_page]:
            t_badges_html = "".join([
                f'<span style="background:rgba(56,189,248,0.15);color:#38BDF8;border:1px solid rgba(56,189,248,0.4);font-family:monospace;font-size:11px;font-weight:700;padding:2px 7px;border-radius:4px;margin-right:6px;">${tk}</span>'
                for tk in it.get("tickers", [])
            ])

            c_badges_html = "".join([
                f'<span style="background:{"rgba(225,29,72,0.15)" if "FLASH" in c else "rgba(100,116,139,0.15)"};color:{"#E11D48" if "FLASH" in c else "#94A3B8"};border:1px solid {"#E11D4833" if "FLASH" in c else "#334155"};font-size:11px;font-weight:600;padding:2px 7px;border-radius:4px;margin-right:6px;">{c}</span>'
                for c in it.get("categories", [])
            ])

            safe_t = html.escape(it.get("title", ""))
            safe_s = html.escape(it.get("summary", "")) if it.get("summary") else ""
            summary_html = f'<div style="color:#94A3B8;font-size:13px;line-height:1.5;margin-top:8px;">{safe_s}</div>' if safe_s else ""

            card_border = "#E11D48" if it.get("is_flash") else "#1E293B"
            card_bg = "rgba(225,29,72,0.04)" if it.get("is_flash") else "rgba(15,23,42,0.5)"

            card_html = (
                f'<div style="background:{card_bg};border:1px solid {card_border};border-radius:10px;padding:16px 20px;margin-bottom:12px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px;">'
                f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
                f'<span style="background:{it["color"]}22;color:{it["color"]};border:1px solid {it["color"]}66;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;letter-spacing:0.05em;">{it["icon"]} {it["source_badge"]}</span>'
                f'{c_badges_html}</div>'
                f'<div style="color:#64748B;font-size:12px;font-family:monospace;font-weight:500;">⏱️ {it["time_ago"]}</div></div>'
                f'<div style="margin-bottom:6px;"><a href="{it["link"]}" target="_blank" style="color:#F8FAFC;text-decoration:none;font-size:16.5px;font-weight:700;line-height:1.4;">{safe_t}</a></div>'
                f'{summary_html}'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;flex-wrap:wrap;gap:10px;">'
                f'<div>{t_badges_html}</div>'
                f'<div><a href="{it["link"]}" target="_blank" style="background:#1E293B;color:#CBD5E1;border:1px solid #334155;font-size:12px;font-weight:600;padding:5px 12px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:5px;">🔗 Leer en {it["source_badge"]} ↗</a></div>'
                f'</div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)


# =====================================================================
# VISTA 2: ⚡ SCREENER CUANTITATIVO
# =====================================================================
elif nav_view == "⚡ Screener Cuantitativo":
    # ----------------- SCREENERS TOTALMENTE INDEPENDIENTES -----------------
    SCREENERS = {
        "📐 Daily Pivot Breakout Strategy": {
            "title": "📐 Daily Pivot Breakout Strategy Indicator (ROC 30% • EMA 100 Slope 20% • RVOL 20d)",
            "badge": "PIVOT BREAKOUT & MOMENTUM CANDLES",
            "type": "Swing",
            "strategy": "📐 Daily Pivot Breakout Strategy",
            "description": "Estrategia cuantitativa institucional de Ruptura de Pivotes Diarios (Daily Pivot Breakout Strategy Indicator). Identifica activos que rompen pivotes estructurales confirmados (Left Strength = 5, Right Strength = 5 en un Pivot Lookback de 100 velas) exigiendo simultáneamente: (1) Momentum fuerte con ROC de 100 días >= +30%, (2) Volumen relativo RVOL sobre media de 20 días > 1.0x confirmando fuerza compradora, (3) Tendencia principal alcista sobre EMA de 100 períodos con pendiente positiva mínima (EMA Slope Lookback 100d) >= +20% (Smooth Length = 1), y (4) Coloreado de velas por Momentum (Momentum Candle Colors).",
            "benchmark_tickers": getattr(engine, 'DAILY_PIVOT_BREAKOUT_TICKERS', ["INTC", "NVDA", "PLTR", "APP", "RDDT", "ALAB", "HOOD", "RKLB", "ASTS", "IONQ", "ANET", "VST", "CEG", "CLS", "CRDO"]),
            "criteria": [
                "Pivot High Confirmado (Left=5, Right=5, Lookback=100)",
                "Momentum: ROC (100 días) >= +30%",
                "Volumen: RVOL (20 días) > 1.0x Promedio",
                "Tendencia: EMA (100) con Pendiente (100d, Smooth=1) >= +20%",
                "Enable Momentum Candle Colors: Sí"
            ]
        },
        "🌅 Pre Market Movers & Gap Ups": {
            "title": "🌅 Pre Market Movers & Gap Ups",
            "badge": "PRE-MARKET & GAP UPS",
            "type": "Swing",
            "strategy": "🌅 Pre Market Movers & Gap Ups",
            "description": "Filtro oficial TradingVolt: Acciones sobre $5 con volumen activo en pre-market haciendo gap up > 2% o cotizando al alza, con volumen diario promedio superior a $10M o market cap > $500M.",
            "benchmark_tickers": engine.PRE_MARKET_MOVERS_TICKERS,
            "criteria": ["Precio > $5.0", "Gap Up >= +2% / Al Alza", "Vol. Dólares Diario > $10M", "Market Cap > $500M"]
        },
        "🌆 Post Market Movers": {
            "title": "🌆 Post Market Movers (After-Hours Reactions)",
            "badge": "AFTER-HOURS & EARNINGS",
            "type": "Swing",
            "strategy": "🌆 Post Market Movers",
            "description": "Filtro oficial Post Market Movers (Deepvue): Identifica 21 acciones sobre $5 con negociación activa en after-hours que registran movimientos superiores al 2% en cualquier dirección (+/- 2%), acotado a nombres líquidos (capitalización de mercado superior a $500M o volumen promedio diario en dólares > $10M). Diseñado para capturar reacciones inmediatas tras el cierre a resultados corporativos (earnings) o noticias de alto impacto.",
            "benchmark_tickers": getattr(engine, 'POST_MARKET_MOVERS_21_TICKERS', engine.POST_MARKET_MOVERS_TICKERS),
            "criteria": ["Precio > $5.00", "Movimiento >= 2% (Cualquier Dirección)", "Volumen Promedio Diario > $10M o Cap > $500M", "Reacciones Post-Cierre a Earnings / Noticias"]
        },
        "🌐 Deepvue Universe": {
            "title": "🌐 Deepvue Universe (752 Acciones Líquidas & Top Industrias)",
            "badge": "UNIVERSO MAESTRO INSTITUCIONAL",
            "type": "Swing",
            "strategy": "🌐 Deepvue Universe",
            "description": "Filtro y Universo oficial Deepvue: 752 acciones y ADRs que cumplen los 4 requisitos indispensables de inversión institucional de Deepvue: $Volumen 20d > $20M diarios, Precio >= $10.00, Fuerza Relativa mensual RS 1M > 45 y pertenencia a las industrias líderes a 1, 3 y 12 meses. Constituye la piscina de máxima calidad para todo el screening cuantitativo.",
            "benchmark_tickers": getattr(engine, 'DEEPVUE_UNIVERSE_752_TICKERS', []),
            "criteria": ["$Volumen 20d >= $20M Diarios", "Precio >= $10.00", "RS 1M > 45 (Fuerza Relativa)", "Grupos de Industria Líderes"]
        },
        "💎 Liquid Leaders": {
            "title": "💎 Liquid Leaders (Deepvue Alta Liquidez & RS)",
            "badge": "LÍDERES DE ALTA LIQUIDEZ",
            "type": "Swing",
            "strategy": "💎 Liquid Leaders (Alta Liquidez & RS)",
            "description": "Filtro oficial Liquid Leaders (Deepvue): Acciones altamente líquidas e institucionalmente operables ($Volumen Diario >= $15M-$20M) que demuestran una fuerza de precio excepcional tanto en términos absolutos (tendencia estructural sobre SMA 50/200) como relativos (RS vs SPY y cercanía a máximos anuales). Diseñado para carteras y fondos institucionales que requieren alta capacidad de absorción.",
            "benchmark_tickers": getattr(engine, 'LIQUID_LEADERS_187_TICKERS', []),
            "criteria": ["Alta Liquidez Institucional ($Vol >= $15M)", "Fuerza Relativa Superior (RS)", "Estructura Alcista SMA 50 / 200", "Dentro de 25% de Máximos de 52s"]
        },
        "🌱 Ameet Rai: IPO Last 1 Year": {
            "title": "🌱 Ameet Rai: IPO Last 1 Year (Weekend Routine)",
            "badge": "IPOS RECIENTES & RISK-ON",
            "type": "Swing",
            "strategy": "🌱 Ameet Rai: IPO Last 1 Year",
            "description": "Filtro oficial Ameet Rai (Deepvue): Rutina de fin de semana que escanea las 189 empresas que salieron a bolsa (IPO) en el último año. Funciona como un barómetro macro institucional de apetito por el riesgo (Risk-On vs. Risk-Off): si las acciones jóvenes del mercado están siendo apoyadas por las instituciones, el entorno es Risk-On; si pierden soporte masivamente, el entorno es Risk-Off.",
            "benchmark_tickers": getattr(engine, 'AMEET_RAI_IPO_1YR_189_TICKERS', []),
            "criteria": ["IPO Debut en Últimos 365 Días (<= 260 sesiones)", "Barómetro Institucional Risk-On / Risk-Off", "Soporte sobre Medias Móviles Cortas", "Rutina de Fin de Semana (Weekend Routine)"]
        },
        "⚡ Ameet Rai: HV Edge": {
            "title": "⚡ Ameet Rai: HV Edge (Daily Routine)",
            "badge": "HV EDGE & FIRMA DE VOLUMEN",
            "type": "Swing",
            "strategy": "⚡ Ameet Rai: HV Edge",
            "description": "Filtro oficial Ameet Rai (Deepvue): Rutina diaria que rastrea 45 activos que registran la firma de volumen 'HV Edge' (mayor volumen de negociación bajo 3 hitos estructurales: mayor volumen en 1 año, mayor volumen desde el debut de la IPO, o mayor volumen desde el último reporte de earnings). Diseñado para detectar en el día exacto la huella de acumulación institucional masiva.",
            "benchmark_tickers": getattr(engine, 'AMEET_RAI_HV_EDGE_45_TICKERS', []),
            "criteria": ["Mayor Volumen en 1 Año (HVE 1Y)", "Mayor Volumen desde IPO", "Mayor Volumen desde Últimos Earnings", "Rutina Diaria de Acumulación Institucional"]
        },
        "🚩 Ameet Rai: High Tight Flags": {
            "title": "🚩 Ameet Rai: High Tight Flags (Weekend Routine)",
            "badge": "HTF SETUP & EXPLOSIÓN",
            "type": "Swing",
            "strategy": "🚩 Ameet Rai: High Tight Flags",
            "description": "Filtro oficial Ameet Rai (Deepvue): Rutina de fin de semana que escanea activos que han subido al menos un 100% en las últimas 20 sesiones (duplicación explosiva de precio) y consolidan en una bandera alta y estrecha (High Tight Flag) con retroceso inferior al 25-30% desde máximos. Diseñado para preparar la lista de vigilancia de las roturas de mayor potencial explosivo del mercado.",
            "benchmark_tickers": getattr(engine, 'AMEET_RAI_HTF_12_TICKERS', []),
            "criteria": ["Subida >= 100% en 20 Sesiones (Mástil)", "Retroceso Bandera < 25-30% (Flag)", "Precio >= $1.00", "Rutina de Fin de Semana (HTF Watchlist)"]
        },
        "💧 Ameet Rai: Daily Liquidity": {
            "title": "💧 Ameet Rai: Daily Liquidity (Daily Routine)",
            "badge": "RUTINA DIARIA & ULTRA-LIQUIDEZ",
            "type": "Swing",
            "strategy": "💧 Ameet Rai: Daily Liquidity",
            "description": "Filtro oficial Ameet Rai (Deepvue): Rutina diaria institucional que rastrea las 296 acciones y ETFs líderes que negocian más de 8 millones de acciones en la sesión (Volumen > 8M). Permite monitorear qué está haciendo el dinero institucional pesado en tiempo real e identificar temáticas y rotaciones sectoriales que están emergiendo de forma temprana.",
            "benchmark_tickers": getattr(engine, 'AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS', []),
            "criteria": ["Volumen de la Sesión > 8 Millones", "Precio >= $2.00 & $Vol > $15M", "Detección Temprana de Temáticas", "Rutina Diaria Institucional"]
        },
        "🛡️ Ameet Rai: 62.5% RS Days": {
            "title": "🛡️ Ameet Rai: 62.5% RS Days (Corrections)",
            "badge": "CORRECCIONES & FUERZA RELATIVA",
            "type": "Swing",
            "strategy": "🛡️ Ameet Rai: 62.5% RS Days",
            "description": "Filtro oficial Ameet Rai (Deepvue): Identifica 191 acciones de alta liquidez cotizando sobre $3 que se encuentran en fase de Fuerza Relativa (Relative Strength Phase) y que han registrado sesiones de Fuerza Relativa (RS Days) en al menos el 62.5% de los días en cualquier ventana rodante de 5 a 60 sesiones. Filtro clave para detectar los líderes que muestran resiliencia y acumulación tenaz mientras el mercado general corrige.",
            "benchmark_tickers": getattr(engine, 'AMEET_RAI_RS_DAYS_191_TICKERS', []),
            "criteria": ["Sesiones RS >= 62.5% (Ventana 5 a 60 días)", "Precio >= $3.00 & Alta Liquidez", "En Fase de Fuerza Relativa (RS Phase)", "Resiliencia ante Debilidad de Mercado"]
        },
        "📅 Weekly Strength": {
            "title": "📅 Weekly Strength (Cierres en Máximos Semanales & RS)",
            "badge": "FUERZA SEMANAL & TENDENCIA",
            "type": "Swing",
            "strategy": "📅 Weekly Strength",
            "description": "Filtro oficial Weekly Strength (Deepvue): Identifica 399 acciones de alta liquidez que cierran en el tercio superior de su rango semanal (cerca de máximos de la semana), manteniéndose con solidez por encima de sus medias móviles clave (EMA 21, SMA 50, SMA 200) y demostrando Fuerza Relativa superior de medio plazo. Refleja fuerte acumulación institucional sostenida de viernes a viernes.",
            "benchmark_tickers": getattr(engine, 'WEEKLY_STRENGTH_399_TICKERS', []),
            "criteria": ["Cierre Cerca de Máximos Semanales (Top 30%)", "Sobre Medias Clave (EMA 21 & SMA 50/200)", "Fuerza Relativa Medio Plazo (RS 3M/6M)", "Alta Liquidez Institucional"]
        },
        "⚡ Power 21": {
            "title": "⚡ Power 21 (Deepvue 21 EMA Pullback & Absolute Strength)",
            "badge": "PULLBACK A 21 EMA & AS",
            "type": "Swing",
            "strategy": "⚡ Power 21",
            "description": "Filtro oficial Power 21 (Deepvue): Identifica acciones líderes de alto potencial y gran liquidez institucional que realizan un retroceso ordenado o consolidan en estrecha proximidad a su media móvil exponencial de 21 días (21 EMA). Combina estabilidad de precio en la media corta institucional con fuertes métricas recientes de Fuerza Absoluta (AS / Absolute Strength) previas a la reanudación del impulso.",
            "benchmark_tickers": getattr(engine, 'POWER_21_69_TICKERS', []),
            "criteria": ["Cerca de 21-Day EMA (-3.5% a +4.0%)", "Fuerte Fuerza Absoluta (AS)", "Alta Liquidez ($Vol >= $5M-$10M)", "Estructura de Momentum Sostenido"]
        },
        "💧 Volume Dry Up": {
            "title": "💧 Volume Dry Up (Secado de Volumen & RMV Tight)",
            "badge": "SECADO & PRE-MARKUP",
            "type": "Swing",
            "strategy": "💧 Volume Dry Up",
            "description": "Filtro oficial Volume Dry Up (Deepvue): Identifica acciones y ETFs de alta liquidez que cotizan por encima de su media móvil de 50 sesiones (SMA 50) mientras el volumen se contrae drásticamente. Señal constructiva de agotamiento de presión vendedora durante una base, retroceso ordenado (pullback) o consolidación de bandera alcista (bull-flag) con indicador RMV en compresión verde (RMV <= 10) previa a una rotura explosiva.",
            "benchmark_tickers": getattr(engine, 'VOLUME_DRY_UP_160_TICKERS', []),
            "criteria": ["Sobre Media Móvil de 50 Días (SMA 50)", "Contracción de Volumen (RVOL < 0.85x)", "Indicador RMV Tight (RMV <= 10-15%)", "Consolidación en Base / Bull-Flag"]
        },
        "🎯 Tight Range": {
            "title": "🎯 Tight Range (Compresión de Volatilidad)",
            "badge": "COMPRESIÓN & PRE-BREAKOUT",
            "type": "Swing",
            "strategy": "🎯 Tight Range (Compresión de Volatilidad)",
            "description": "Filtro oficial Tight Range (Deepvue): Identifica acciones en consolidación estrecha con volatilidad de rango a 15 días (RMV) inferior al 10% y Market Cap > $1B. Busca activos cotizando cerca de sus medias móviles de 50 y 200 días con una variación a 5 días de entre -4% y +4% o en patrón de Double Inside Days. Detecta la calma institucional previa a una ruptura explosiva.",
            "benchmark_tickers": getattr(engine, 'TIGHT_RANGE_26_TICKERS', []),
            "criteria": ["Rango 15d (RMV) < 10.0%", "Cambio 5d entre -4% y +4%", "Cerca de SMA 50 y SMA 200", "Double Inside Days Setup"]
        },
        "🎯 Pocket Pivots": {
            "title": "🎯 Pocket Pivots (Gil Morales & Dr. Chris Kacher)",
            "badge": "ACUMULACIÓN DENTRO DE BASE",
            "type": "Swing",
            "strategy": "🎯 Pocket Pivots (Morales & Kacher)",
            "description": "Filtro oficial Gil Morales & Dr. Chris Kacher (Deepvue): Acciones y ADRs en tendencia alcista que registran una sesión positiva con volumen SUPERIOR al volumen de cualquier día bajista de las 10 sesiones previas. Señal cuantitativa de acumulación institucional dentro de una base o en tendencia alcista, permitiendo entradas tempranas de bajo riesgo antes del breakout convencional.",
            "benchmark_tickers": getattr(engine, 'POCKET_PIVOTS_45_TICKERS', []),
            "criteria": ["Día Alcista (Up Day)", "Volumen > Máx Día Bajista (10d)", "Tendencia Alcista / Dentro de Base", "Entrada Temprana de Bajo Riesgo"]
        },
        "⚡ Episodic Pivot": {
            "title": "⚡ Qullamaggie: Episodic Pivot (EP)",
            "badge": "EP SETUP & BREAKOUT",
            "type": "Swing",
            "strategy": "⚡ Qullamaggie: Episodic Pivot (EP)",
            "description": "Filtro oficial Kristjan Qullamaggie: Salto explosivo (ganancia > 8% o gap > 5%) con volumen masivo (RVOL > 1.2x o > 500k acciones) ocurrido en las últimas 10 sesiones o hoy, manteniendo estructura alcista.",
            "benchmark_tickers": engine.EPISODIC_PIVOT_8_TICKERS,
            "criteria": ["Salto >= +8% / Gap >= +5%", "RVOL >= 1.2x o Vol >= 500k", "Ventana 10 Sesiones", "Sostiene Estructura"]
        },
        "🐜 David Ryan: Ants": {
            "title": "🐜 David Ryan: Ants (Acumulación Sostenida)",
            "badge": "ACUMULACIÓN INSTITUCIONAL",
            "type": "Swing",
            "strategy": "🐜 David Ryan: Ants (Acumulación Sostenida)",
            "description": "Filtro oficial David Ryan: Al menos 4-5 sesiones de acumulación en las últimas 15 sesiones (subidas con volumen superior al día previo o a la media) operando cerca de máximos.",
            "benchmark_tickers": engine.ANTS_3_TICKERS,
            "criteria": ["4-5 Días Acumulación / 15s", "Volumen > Media / Previo", "Dentro de 25% de Máximos"]
        },
        "📈 Up on Volume": {
            "title": "📈 Up on Volume (Cierre Alto + Volumen)",
            "badge": "VOLUMEN INSTITUCIONAL",
            "type": "Swing",
            "strategy": "📈 Up on Volume (Cierre Alto + Volumen)",
            "description": "Filtro oficial Up on Volume: Acciones líquidas con subida positiva cerrando en la mitad superior de su rango diario (>= 45-50%) con volumen relativo elevado.",
            "benchmark_tickers": engine.UP_ON_VOLUME_64_TICKERS,
            "criteria": ["Cambio > 0% / Sesión Activa", "Cierre en Rango >= 50%", "RVOL >= 1.0x"]
        },
        "🚀 Pure Momentum": {
            "title": "🚀 Pure Momentum (231-Leader Benchmark)",
            "badge": "ALTA VELOCIDAD & LIQUIDEZ",
            "type": "Swing",
            "strategy": "🚀 Pure Momentum (ADR > 3% + $Vol > $7M)",
            "description": "Filtro oficial TradingVolt Pure Momentum: Acciones comunes de alto volumen (Volumen Diario Promedio > $7M) y alto rango de movimiento útil (ADR(10) > 3%). Requiere Fuerza Absoluta (AS) > 95 a 1 mes o > 93 a 3 meses.",
            "benchmark_tickers": getattr(engine, 'PURE_MOMENTUM_231_TICKERS', PURE_MOMENTUM_205_TICKERS),
            "criteria": ["Volumen en Dólares >= $7M", "ADR(10) > 3.0%", "Fuerza Absoluta (AS 1M > 95 / 3M > 93)", "Momentum Sostenido"]
        },
        "🏆 CANSLIM® Official Leaders": {
            "title": "🏆 CANSLIM® Official Leaders (True Market Leaders)",
            "badge": "CANSLIM® OFICIAL",
            "type": "Swing",
            "strategy": "🏆 CANSLIM® Official Leaders",
            "description": "Filtro oficial CANSLIM® (TradingVolt): Identifica acciones con fuerte crecimiento de beneficios (EPS), ventas aceleradas, industrias líderes y creciente patrocinio institucional — los rasgos fundamentales de los verdaderos líderes de mercado.",
            "benchmark_tickers": getattr(engine, 'CANSLIM_OFFICIAL_36_TICKERS', []),
            "criteria": ["Crecimiento Acelerado Ventas/EPS", "Dentro de 15% de Máximos", "Etapa 2 Alcista (SMA 50 > SMA 200)", "Patrocinio Institucional Líquido"]
        },
        "🔥 Highest Volume IPO": {
            "title": "🔥 Highest Volume IPO (Highest Volume Since IPO Day)",
            "badge": "RÉCORD VOLUMEN IPO",
            "type": "Swing",
            "strategy": "🔥 Highest Volume IPO",
            "description": "Filtro oficial Highest Volume IPO (Deepvue): Identifica acciones e IPOs que registran la firma de volumen 'Highest Volume Since IPO Day' (volumen récord desde su debut bursátil). Exige un volumen promedio diario en dólares superior a $3 millones ($Vol > $3M), un rango de cierre diario (Daily Closing Range - DCR) superior al 40% y una variación diaria positiva de precio (> 0%). Diseñado para detectar entradas recientes al mercado con fuerte momentum institucional y demanda masiva.",
            "benchmark_tickers": getattr(engine, 'HV_IPO_7_TICKERS', getattr(engine, 'HVE_7_TICKERS', [])),
            "criteria": ["Volumen Récord desde Día de IPO", "$Vol Promedio Diario > $3M", "Daily Closing Range (DCR) > 40%", "Cierre Diario Positivo (> 0%)"]
        },
        "🌀 Minervini VCP Pattern": {
            "title": "🌀 Mark Minervini: Volatility Contraction Pattern (VCP)",
            "badge": "VCP CONTRACCIÓN",
            "type": "Swing",
            "strategy": "🌀 Minervini VCP Pattern",
            "description": "Filtro oficial Mark Minervini: Contracción progresiva de la volatilidad en el lado derecho de la base con secado de volumen previo a rotura alcista explosiva.",
            "benchmark_tickers": getattr(engine, 'VCP_MINERVINI_43_TICKERS', []),
            "criteria": ["Contracción de Volatilidad (VCP)", "Secado de Volumen en Consolidación", "Estructura Alcista Etapa 2", "Dentro de 20% de Máximos"]
        },
        "🚀 Sustained Momentum Leaders": {
            "title": "🚀 Sustained Momentum Leaders (Liquid RS Leaders)",
            "badge": "MOMENTUM SOSTENIDO",
            "type": "Swing",
            "strategy": "🚀 Sustained Momentum Leaders",
            "description": "Acciones de alta liquidez institucional ($Vol > $10M) exhibiendo momentum sostenido superior (Retorno 3M/6M > 35%) y liderazgo de fuerza relativa en el mercado.",
            "benchmark_tickers": getattr(engine, 'MOMENTUM_LEADERS_186_TICKERS', getattr(engine, 'MOMENTUM_LEADERS_187_TICKERS', [])),
            "criteria": ["Momentum Sostenido 3M/6M", "Fuerza Relativa (RS > 90)", "Volumen en Dólares >= $10M", "Sobre Medias SMA 50/200"]
        },
        "📈 Stage Analysis: Weinstein 2/2A": {
            "title": "📈 Stage Analysis Leaders (Weinstein Etapa 2 / 2A)",
            "badge": "WEINSTEIN STAGE 2 / 2A",
            "type": "Swing",
            "strategy": "📈 Stage Analysis: Weinstein 2/2A Leaders",
            "description": "Filtro oficial Stan Weinstein: Acciones en Etapa 2/2A (transición de base a markup alcista temprano), altísima liquidez ($Vol 20d > $20M), Fuerza Relativa superior (RS 1M/3M > 85) e industrias líderes del mercado.",
            "benchmark_tickers": getattr(engine, 'STAGE2_LEADERS_417_TICKERS', []),
            "criteria": ["Etapa 2 / 2A Alcista", "Volumen en Dólares >= $20M", "Fuerza Relativa (RS > 85)", "Industrias Top 25"]
        },
        "🚀 CANSLIM High RS Leaders": {
            "title": "🚀 CANSLIM High RS Leaders (Tech & Consumer Discretionary)",
            "badge": "FUERZA RELATIVA CANSLIM",
            "type": "Swing",
            "strategy": "🚀 CANSLIM High RS Leaders",
            "description": "Filtro oficial CANSLIM / William O'Neil: Líderes de Tecnología y Consumo Discrecional con alta Fuerza Relativa (RS vs SPY), liquidez institucional ($Vol > $15M) y estructura de Etapa 2.",
            "benchmark_tickers": getattr(engine, 'CANSLIM_HIGH_RS_137_TICKERS', []),
            "criteria": ["Fuerza Relativa (RS) Superior", "Tecnología & Consumo Cíclico", "$Vol Promedio >= $15M", "Estructura Alcista SMA 50/200"]
        },
        "🏆 True Market Leaders": {
            "title": "🏆 True Market Leaders (TML Momentum)",
            "badge": "LÍDERES DE MERCADO",
            "type": "Swing",
            "strategy": "🏆 True Market Leaders (TML Momentum)",
            "description": "Líderes de crecimiento institucional en Etapa 2 alcista (Precio > SMA 50 > SMA 200) cotizando a menos del 18% de sus máximos de 52 semanas.",
            "benchmark_tickers": TML_331_TICKERS,
            "criteria": ["Etapa 2 Alcista", "Dist. Máx 52s < 18%", "Precio > SMA 20"]
        },
        "🎯 Minervini Stage 2": {
            "title": "🎯 Trend Template (Etapa 2 Minervini)",
            "badge": "TENDENCIA ESTRUCTURAL",
            "type": "Swing",
            "strategy": "Trend Template (Etapa 2)",
            "description": "Plantilla clásica de Mark Minervini: Precio > SMA 50 > SMA 200, momentum en expansión y estructura técnica impecable.",
            "benchmark_tickers": engine.SP500_30_TICKERS,
            "criteria": ["Precio > SMA 50", "SMA 50 > SMA 200", "Dist. Máx < 20%"]
        },
        "🔄 Pullback a SMA 20/50": {
            "title": "🔄 Pullback a SMA 20/50 (Rebotes Técnicos)",
            "badge": "SOPORTES CLAVE",
            "type": "Swing",
            "strategy": "Pullback a SMA 20/50",
            "description": "Puntos de entrada de bajo riesgo: acciones en fuerte tendencia alcista descansando sobre su media móvil de 20 o 50 periodos.",
            "benchmark_tickers": engine.SP500_30_TICKERS,
            "criteria": ["Tendencia Alcista", "Testeo SMA 20 / SMA 50", "RSI 40 - 60"]
        },
        "💥 Breakout 20 Días": {
            "title": "💥 Ruptura de Resistencia (Breakout 20d)",
            "badge": "RUPTURA DE RANGO",
            "type": "Swing",
            "strategy": "Ruptura de Resistencia (Breakout)",
            "description": "Superación del máximo de las últimas 20 sesiones con volumen relativo anormal (RVOL > 1.2x).",
            "benchmark_tickers": engine.SP500_30_TICKERS,
            "criteria": ["Precio >= Máx 20d", "RVOL >= 1.2x", "Estructura Alcista"]
        },
        "🔥 Top Gappers & RVOL": {
            "title": "🔥 Top Gappers & RVOL (Intradía)",
            "badge": "VOLUMEN INTRADÍA",
            "type": "Day",
            "strategy": "Top Gappers & RVOL",
            "description": "Gaps de apertura superiores al 2% con explosión de volumen relativo superior a 1.2x veces el promedio intradía.",
            "benchmark_tickers": engine.MOMENTUM_25_TICKERS,
            "criteria": ["Gap Hoy >= +2%", "RVOL >= 1.2x", "Volumen en Expansión"]
        },
        "⚡ Impulso en Máximos": {
            "title": "⚡ Impulso cerca de Máximos del Día",
            "badge": "MÁXIMOS DE SESIÓN",
            "type": "Day",
            "strategy": "Impulso cerca de Máximos del Día",
            "description": "Activos operando en el 15% superior de su rango intradía con fuerte presión compradora.",
            "benchmark_tickers": engine.MOMENTUM_25_TICKERS,
            "criteria": ["Posición Rango >= 85%", "RVOL >= 1.2x", "Presión Compradora"]
        },
        "✏️ Scanner Personalizado": {
            "title": "✏️ Scanner Personalizado (Mi Canasta)",
            "badge": "MODO LIBRE",
            "type": "Custom",
            "strategy": "Custom",
            "description": "Escanea tu propia lista de acciones o canasta preferida aplicando la estrategia cuantitativa que elijas.",
            "benchmark_tickers": [],
            "criteria": ["Canasta a Elección", "Estrategia Libre", "Análisis a Medida"]
        }
    }

    # PANEL DE CONTROL INSTITUCIONAL (ESTRATEGIA + UNIVERSO)
    col_ctrl1, col_ctrl2 = st.columns([1.6, 1.4])
    with col_ctrl1:
        st.markdown("""
        <div style="margin-bottom: 4px;">
            <span style="font-size: 11px; font-weight: 700; color: #00F0FF; text-transform: uppercase; letter-spacing: 1px;">
                1. Estrategia Cuantitativa (Filtro)
            </span>
        </div>
        """, unsafe_allow_html=True)
        screener_names = list(SCREENERS.keys())
        selected_screener_name = st.selectbox(
            "Seleccionar Filtro Institucional:",
            screener_names,
            index=0,
            label_visibility="collapsed"
        )

    current_screener = SCREENERS[selected_screener_name]
    num_benchmark = len(current_screener["benchmark_tickers"])

    with col_ctrl2:
        st.markdown("""
        <div style="margin-bottom: 4px;">
            <span style="font-size: 11px; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px;">
                2. Universo a Escanear (Mercado)
            </span>
        </div>
        """, unsafe_allow_html=True)

        active_radar_data = are.get_active_radar() if are else {"tickers": [], "count": 0, "source": "Screener"}
        radar_count_now = active_radar_data.get("count", len(active_radar_data.get("tickers", [])))
        radar_src_now = active_radar_data.get("source", "Screener")

        is_pre_or_post = ("Pre Market" in selected_screener_name or "Post Market" in selected_screener_name or "Top Gappers" in selected_screener_name)
        default_idx = 1 if is_pre_or_post else 0

        universe_options = [
            f"📐 Daily Pivot Breakout Strategy ({len(getattr(engine, 'DAILY_PIVOT_BREAKOUT_TICKERS', []))} líderes)",
            f"🌱 Ameet Rai: IPO Last 1 Year ({len(getattr(eu, 'AMEET_RAI_IPO_1YR_189', getattr(engine, 'AMEET_RAI_IPO_1YR_189_TICKERS', [])))} acciones)",
            f"⚡ Ameet Rai: HV Edge ({len(getattr(eu, 'AMEET_RAI_HV_EDGE_45', getattr(engine, 'AMEET_RAI_HV_EDGE_45_TICKERS', [])))} acciones)",
            f"🌆 Post Market Movers ({len(getattr(engine, 'POST_MARKET_MOVERS_21_TICKERS', engine.POST_MARKET_MOVERS_TICKERS))} acciones)",
            f"🚩 Ameet Rai: High Tight Flags ({len(getattr(eu, 'AMEET_RAI_HTF_12', getattr(engine, 'AMEET_RAI_HTF_12_TICKERS', [])))} acciones)",
            f"💧 Ameet Rai: Daily Liquidity ({len(getattr(eu, 'AMEET_RAI_DAILY_LIQUIDITY_296', getattr(engine, 'AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS', [])))} acciones)",
            f"🛡️ Ameet Rai: 62.5% RS Days ({len(getattr(eu, 'AMEET_RAI_RS_DAYS_191', getattr(engine, 'AMEET_RAI_RS_DAYS_191_TICKERS', [])))} acciones)",
            f"🔥 Highest Volume IPO ({len(getattr(engine, 'HV_IPO_7_TICKERS', getattr(engine, 'HVE_7_TICKERS', [])))} acciones)",
            f"📅 Weekly Strength ({len(getattr(eu, 'WEEKLY_STRENGTH_399', getattr(engine, 'WEEKLY_STRENGTH_399_TICKERS', [])))} acciones)",
            f"⚡ Power 21 ({len(getattr(eu, 'POWER_21_69', getattr(engine, 'POWER_21_69_TICKERS', [])))} acciones)",
            f"💧 Volume Dry Up ({len(getattr(eu, 'VOLUME_DRY_UP_160', getattr(engine, 'VOLUME_DRY_UP_160_TICKERS', [])))} acciones)",
            f"🌐 Deepvue Universe ({len(getattr(eu, 'DEEPVUE_UNIVERSE_752', getattr(engine, 'DEEPVUE_UNIVERSE_752_TICKERS', [])))} acciones líquidas)",
            f"🚀 Momentum Leaders ({len(getattr(eu, 'MOMENTUM_LEADERS_186', getattr(engine, 'MOMENTUM_LEADERS_186_TICKERS', [])))} acciones)",
            f"💎 Liquid Leaders ({len(getattr(engine, 'LIQUID_LEADERS_187_TICKERS', []))} acciones)",
            f"🎯 Tight Range ({len(getattr(engine, 'TIGHT_RANGE_26_TICKERS', []))} acciones)",
            f"🎯 Pocket Pivots ({len(getattr(engine, 'POCKET_PIVOTS_45_TICKERS', []))} acciones)",
            "🤖 Líderes Autónomos TradingVolt (260 generados algorítmicamente)",
            "📡 Mercado en Vivo: Top Pre-Market & Movers (+350 en vivo)",
            f"🎯 Radar Activo Compartido ({radar_count_now} activos de {radar_src_now})",
            f"🇺🇸 US Broad Liquid Market ({len(eu.US_BROAD_MARKET_TICKERS):,} acciones)",
            f"🏆 S&P 500 Completo ({len(eu.SP500_COMPLETE_TICKERS)} acciones)",
            f"💻 Nasdaq 100 Completo ({len(eu.NASDAQ100_COMPLETE_TICKERS)} acciones)",
            f"🏢 S&P 400 Mid-Cap Growth ({len(eu.SP400_MIDCAP_TICKERS)} acciones)",
            f"⚡ S&P 600 Small-Cap Momentum ({len(eu.SP600_SMALLCAP_TICKERS)} acciones)",
            f"🚀 High Momentum Basket ({len(eu.HIGH_MOMENTUM_EXPANDED_TICKERS)} acciones)",
            "✏️ Personalizado (Escribir tickers)",
            f"🧪 Canasta Benchmark Auditoría Deepvue ({num_benchmark} activos)",
            f"🌐 True Market Leaders Oficiales Auditoría ({len(engine.TML_331_TICKERS)} acciones)"
        ]

        selected_universe_option = st.selectbox(
            "Seleccionar Universo:",
            universe_options,
            index=default_idx,
            label_visibility="collapsed"
        )

    # Determinar ticker list a escanear
    if "Daily Pivot Breakout" in selected_universe_option:
        ticker_list = getattr(engine, 'DAILY_PIVOT_BREAKOUT_TICKERS', ["INTC", "NVDA", "PLTR", "APP", "RDDT", "ALAB", "HOOD"])
        universe_label = f"📐 Daily Pivot Breakout Leaders ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Líderes Autónomos TradingVolt" in selected_universe_option:
        ticker_list = get_autonomous_market_leaders(top_n=260)
        universe_label = f"🤖 Líderes Autónomos TradingVolt ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Mercado en Vivo" in selected_universe_option:
        ticker_list = "LIVE_MOVERS"
        universe_label = "📡 Mercado en Vivo (Top Gappers & Movers en Tiempo Real)"
        ticker_count_display = "EN VIVO (~350+)"
    elif "Radar Activo Compartido" in selected_universe_option:
        ticker_list = are.get_active_radar_tickers(max_items=120) if are else ["NVDA", "PLTR", "TSLA"]
        universe_label = f"🎯 Radar Activo Compartido ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Deepvue Universe" in selected_universe_option:
        ticker_list = getattr(eu, 'DEEPVUE_UNIVERSE_752', getattr(engine, 'DEEPVUE_UNIVERSE_752_TICKERS', []))
        universe_label = f"🌐 Deepvue Universe ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Momentum Leaders" in selected_universe_option:
        ticker_list = getattr(eu, 'MOMENTUM_LEADERS_186', getattr(engine, 'MOMENTUM_LEADERS_186_TICKERS', []))
        universe_label = f"🚀 Momentum Leaders ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Post Market" in selected_universe_option:
        ticker_list = getattr(engine, 'POST_MARKET_MOVERS_21_TICKERS', engine.POST_MARKET_MOVERS_TICKERS)
        universe_label = f"🌆 Post Market Movers ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Highest Volume" in selected_universe_option or "HVE" in selected_universe_option or "IPO" in selected_universe_option:
        ticker_list = getattr(engine, 'HV_IPO_7_TICKERS', getattr(engine, 'HVE_7_TICKERS', []))
        universe_label = f"🔥 Highest Volume IPO ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "IPO Last 1 Year" in selected_universe_option:
        ticker_list = getattr(eu, 'AMEET_RAI_IPO_1YR_189', getattr(engine, 'AMEET_RAI_IPO_1YR_189_TICKERS', []))
        universe_label = f"🌱 Ameet Rai: IPO Last 1 Year ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "HV Edge" in selected_universe_option:
        ticker_list = getattr(eu, 'AMEET_RAI_HV_EDGE_45', getattr(engine, 'AMEET_RAI_HV_EDGE_45_TICKERS', []))
        universe_label = f"⚡ Ameet Rai: HV Edge ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "High Tight Flag" in selected_universe_option or "HTF" in selected_universe_option:
        ticker_list = getattr(eu, 'AMEET_RAI_HTF_12', getattr(engine, 'AMEET_RAI_HTF_12_TICKERS', []))
        universe_label = f"🚩 Ameet Rai: High Tight Flags ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Daily Liquidity" in selected_universe_option:
        ticker_list = getattr(eu, 'AMEET_RAI_DAILY_LIQUIDITY_296', getattr(engine, 'AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS', []))
        universe_label = f"💧 Ameet Rai: Daily Liquidity ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Ameet Rai" in selected_universe_option or "RS Days" in selected_universe_option:
        ticker_list = getattr(eu, 'AMEET_RAI_RS_DAYS_191', getattr(engine, 'AMEET_RAI_RS_DAYS_191_TICKERS', []))
        universe_label = f"🛡️ Ameet Rai: 62.5% RS Days ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Weekly Strength" in selected_universe_option:
        ticker_list = getattr(eu, 'WEEKLY_STRENGTH_399', getattr(engine, 'WEEKLY_STRENGTH_399_TICKERS', []))
        universe_label = f"📅 Weekly Strength ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Power 21" in selected_universe_option:
        ticker_list = getattr(eu, 'POWER_21_69', getattr(engine, 'POWER_21_69_TICKERS', []))
        universe_label = f"⚡ Power 21 ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Volume Dry Up" in selected_universe_option:
        ticker_list = getattr(eu, 'VOLUME_DRY_UP_160', getattr(engine, 'VOLUME_DRY_UP_160_TICKERS', []))
        universe_label = f"💧 Volume Dry Up ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Tight Range" in selected_universe_option:
        ticker_list = getattr(engine, 'TIGHT_RANGE_26_TICKERS', [])
        universe_label = f"🎯 Tight Range ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Pocket Pivots" in selected_universe_option:
        ticker_list = getattr(engine, 'POCKET_PIVOTS_45_TICKERS', [])
        universe_label = f"🎯 Pocket Pivots ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "US Broad Liquid Market" in selected_universe_option:
        ticker_list = eu.US_BROAD_MARKET_TICKERS
        universe_label = f"US Broad Liquid Market ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "S&P 500 Completo" in selected_universe_option:
        ticker_list = eu.SP500_COMPLETE_TICKERS
        universe_label = f"S&P 500 Completo ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Nasdaq 100 Completo" in selected_universe_option:
        ticker_list = eu.NASDAQ100_COMPLETE_TICKERS
        universe_label = f"Nasdaq 100 Completo ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "S&P 400" in selected_universe_option:
        ticker_list = eu.SP400_MIDCAP_TICKERS
        universe_label = f"S&P 400 Mid-Cap ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "S&P 600" in selected_universe_option:
        ticker_list = eu.SP600_SMALLCAP_TICKERS
        universe_label = f"S&P 600 Small-Cap ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "High Momentum Basket" in selected_universe_option:
        ticker_list = eu.HIGH_MOMENTUM_EXPANDED_TICKERS
        universe_label = f"High Momentum Basket ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Liquid Leaders" in selected_universe_option:
        ticker_list = getattr(engine, 'LIQUID_LEADERS_187_TICKERS', [])
        universe_label = f"Liquid Leaders ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS" 
    elif "True Market Leaders" in selected_universe_option:
        ticker_list = engine.TML_331_TICKERS
        universe_label = f"True Market Leaders ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Pure Momentum Basket" in selected_universe_option:
        ticker_list = engine.PURE_MOMENTUM_231_TICKERS
        universe_label = f"Pure Momentum Basket ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    elif "Canasta Benchmark Oficial" in selected_universe_option:
        ticker_list = current_screener["benchmark_tickers"]
        universe_label = f"Canasta Benchmark Oficial TradingVolt ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"
    else:
        custom_input = st.text_input(
            "Ingresa tickers separados por coma:",
            value="NVDA, TSLA, AAPL, AMD, PLTR, MSTR, COIN, SMCI"
        )
        ticker_list = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
        universe_label = f"Personalizado ({len(ticker_list)} activos)"
        ticker_count_display = f"{len(ticker_list)} ACTIVOS"

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # Card informativa del filtro activo
    criteria_badges = " ".join([f'<span class="badge-neon-bull">✓ {c}</span>' for c in current_screener["criteria"]])
    feed_badge = '<span class="badge-neon-bull">● ALPACA REAL-TIME (IEX)</span>' if use_alpaca else '<span class="badge-neon-cyan">● YAHOO FINANCE FEED</span>'

    st.markdown(f"""
    <div style="background: #0E121A; border: 1px solid #1C2433; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 17px; font-weight: 800; color: #FFFFFF;">{current_screener['title']}</span>
                {feed_badge}
            </div>
            <div style="font-size: 12px; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
                Universo: <strong style="color: #00F0FF;">{universe_label}</strong>
            </div>
        </div>
        <div style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 10px;">
            {current_screener['description']}
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            {criteria_badges}
        </div>
    </div>
    """, unsafe_allow_html=True)

    strategy = current_screener["strategy"]
    is_daytrade = (current_screener["type"] == "Day")
    is_pivot_strategy = ("Pivot Breakout" in selected_screener_name or "Daily Pivot" in selected_screener_name)
    st.session_state["active_screener_is_pivot"] = is_pivot_strategy

    pivot_params_active = None
    if is_pivot_strategy:
        with st.expander("⚙️ Daily Pivot Breakout Strategy Indicator (by Mike) — Panel de Parámetros & Indicador", expanded=True):
            # Fila 1 (idéntica a la captura): Left Strength | Right Strength | Pivot Lookback | ROC Period (days) | Minimum ROC (%)
            r1_c1, r1_c2, r1_c3, r1_c4, r1_c5 = st.columns(5)
            with r1_c1:
                piv_left = st.number_input("Left Strength", min_value=1, max_value=30, value=5, step=1, help="Cuántas velas a la izquierda del pivote deben tener un precio más bajo para confirmar un máximo de pivote válido.")
            with r1_c2:
                piv_right = st.number_input("Right Strength", min_value=1, max_value=30, value=5, step=1, help="Cuántas velas a la derecha del pivote deben tener un precio más bajo para confirmar el pivote.")
            with r1_c3:
                piv_lookback = st.number_input("Pivot Lookback", min_value=20, max_value=250, value=100, step=10, help="Cuántas velas hacia atrás busca pivotes históricos para identificar niveles de breakout.")
            with r1_c4:
                piv_roc_len = st.number_input("ROC Period (days)", min_value=10, max_value=250, value=100, step=5, help="Mide el cambio porcentual de precio en los últimos 100 días.")
            with r1_c5:
                piv_min_roc = st.number_input("Minimum ROC (%)", min_value=0.0, max_value=200.0, value=30.0, step=2.5, help="El precio debe haber subido al menos un 30% en esos 100 días para que el breakout sea válido.")

            # Fila 2 (idéntica a la captura): RVOL Period (days) | EMA Length | EMA Slope Lookback | EMA Smooth Length | Min EMA Slope %
            r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns(5)
            with r2_c1:
                piv_rvol_len = st.number_input("RVOL Period (days)", min_value=5, max_value=100, value=20, step=5, help="Calcula el volumen promedio de los últimos 20 días como referencia (RVOL > 1.0x).")
            with r2_c2:
                piv_ema_len = st.number_input("EMA Length", min_value=10, max_value=300, value=100, step=5, help="EMA de 100 períodos que define la dirección de la tendencia principal.")
            with r2_c3:
                piv_slope_lb = st.number_input("EMA Slope Lookback", min_value=10, max_value=250, value=100, step=5, help="Mide la pendiente porcentual de la EMA mirando 100 velas atrás.")
            with r2_c4:
                piv_smooth = st.number_input("EMA Smooth Length", min_value=1, max_value=20, value=1, step=1, help="Suavizado de la pendiente (1 = sin suavizado adicional).")
            with r2_c5:
                piv_min_slope = st.number_input("Min EMA Slope %", min_value=0.0, max_value=150.0, value=20.0, step=1.0, help="La EMA debe tener una inclinación positiva mínima del 20% para que el breakout sea válido.")

            # Fila 3 (idéntica a la captura): Enable Momentum Candle Colors | Pivot High (───) | 20% Trailing Stop (•••••••) | Entry Signals | Modo Escaneo
            r3_c1, r3_c2, r3_c3, r3_c4, r3_c5 = st.columns([1.1, 0.9, 1.0, 0.9, 1.5])
            with r3_c1:
                piv_mom_colors = st.checkbox("Enable Momentum Candle Colors", value=True, help="Colorea las velas según el momentum (como sobre INTC).")
            with r3_c2:
                piv_show_ph = st.checkbox("Pivot High (─── Verde)", value=True, help="Dibuja la línea horizontal verde continua de los Pivot Highs confirmados.")
            with r3_c3:
                piv_show_trail = st.checkbox("20% Trailing Stop (•••••••)", value=True, help="Dibuja el 20% Trailing Stop en puntos azules desde la señal de entrada.")
            with r3_c4:
                piv_show_entry = st.checkbox("Entry Signals (Breakout)", value=True, help="Muestra las etiquetas de entrada en Breakout y salida por Trailing Stop.")
            with r3_c5:
                piv_mode = st.selectbox(
                    "Modo de Escaneo",
                    ["🔥 Breakout Estricto (Sobre Pivote + RVOL > 1x)", "🎯 Breakout + En Zona de Pivote (-3.5% a +8%)"],
                    index=0,
                    label_visibility="collapsed"
                )

            pivot_params_active = {
                "left_strength": int(piv_left),
                "right_strength": int(piv_right),
                "pivot_lookback": int(piv_lookback),
                "roc_period": int(piv_roc_len),
                "min_roc_pct": float(piv_min_roc),
                "rvol_period": int(piv_rvol_len),
                "ema_length": int(piv_ema_len),
                "ema_slope_lookback": int(piv_slope_lb),
                "ema_smooth_length": int(piv_smooth),
                "min_ema_slope_pct": float(piv_min_slope),
                "trailing_stop_pct": 20.0,
                "enable_momentum_colors": bool(piv_mom_colors),
                "show_pivot_high": bool(piv_show_ph),
                "show_trailing_stop": bool(piv_show_trail),
                "show_entry_signals": bool(piv_show_entry),
                "min_rvol": 1.0,
                "include_near_pivot": ("Zona de Pivote" in piv_mode),
            }
            st.session_state["pivot_strategy_params"] = pivot_params_active

        pine_path = os.path.join(os.path.dirname(__file__), "TradingVolt_Daily_Pivot_Breakout_Mike.pine")
        if os.path.exists(pine_path):
            with st.expander("🌲 Código Pine Script v5 para TradingView: Daily Pivot Breakout Strategy Indicator [by Mike]", expanded=False):
                with open(pine_path, "r", encoding="utf-8") as f_pine:
                    pine_code_str = f_pine.read()
                st.download_button(
                    "📥 Descargar Indicador Pine Script (.pine)",
                    data=pine_code_str.encode("utf-8"),
                    file_name="TradingVolt_Daily_Pivot_Breakout_Mike.pine",
                    mime="text/plain"
                )
                st.code(pine_code_str, language="javascript")

    # Botón principal de escaneo
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    btn_scan = st.button(
        f"⚡ EJECUTAR ESCANEO INSTITUCIONAL ({ticker_count_display})",
        type="primary",
        use_container_width=True
    )

    # Si se pulsa el botón o ya tenemos resultados en sesión
    scan_state_key = f"scan_results_{selected_screener_name}_{selected_universe_option}"

    if btn_scan:
        with st.spinner(f"Escaneando {ticker_count_display} con {strategy} vía {provider_str}..."):
            start_t = datetime.now()
            if is_daytrade:
                results_df = engine.run_daytrade_scanner(
                    ticker_list,
                    strategy,
                    provider=provider_str,
                    alpaca_key=alpaca_key,
                    alpaca_secret=alpaca_secret
                )
            else:
                results_df = engine.run_swing_scanner(
                    ticker_list,
                    strategy,
                    provider=provider_str,
                    alpaca_key=alpaca_key,
                    alpaca_secret=alpaca_secret,
                    pivot_params=pivot_params_active
                )
            duration = (datetime.now() - start_t).total_seconds()
            st.session_state[scan_state_key] = (results_df, duration)

    if scan_state_key in st.session_state:
        results_df, duration = st.session_state[scan_state_key]
    else:
        results_df = pd.DataFrame()
        duration = 0

    if not results_df.empty:
        if "Ticker" in results_df.columns and are:
            disc_tickers = results_df["Ticker"].dropna().tolist()
            are.set_active_radar(
                tickers=disc_tickers,
                source_name=f"{selected_screener_name}",
                description=f"{len(disc_tickers)} activos detectados dinámicamente con {strategy}"
            )
            if qdp is not None:
                qdp.save_live_filter_execution(selected_screener_name, disc_tickers, results_df)
        
        st.markdown(f"""
        <div style="background:linear-gradient(90deg, rgba(0, 240, 255, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%); border-left:4px solid #00F0FF; border-radius:6px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-weight:800; color:#00F0FF; font-size:13px; letter-spacing:0.5px;">📤 RADAR ACTIVO ACTUALIZADO • {len(results_df)} ACTIVOS ENVIADOS AL PIPELINE GLOBAL</div>
                <div style="color:#94A3B8; font-size:11px; margin-top:2px;">
                    Disponibles automáticamente en: <strong>🎯 Quant Options & GEX</strong>, <strong>🚀 Terminal CANSLIM (BO60)</strong>, <strong>🕵️‍♂️ Dark Pool Tape</strong> y <strong>🔄 RRG Rotation Desk</strong>.
                </div>
            </div>
            <div style="display:flex; gap:6px;">
                <span class="badge-neon-bull">AUTOALIMENTACIÓN ACTIVA</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # HUD de métricas rápidas
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        with col_m1:
            st.markdown(f'<div class="hud-card"><div class="hud-label">COINCIDENCIAS</div><div class="hud-value">{len(results_df)}</div></div>', unsafe_allow_html=True)
        with col_m2:
            valid_chg = results_df["Cambio %"].dropna()
            mean_chg = valid_chg.mean() if not valid_chg.empty else 0.0
            st.markdown(f'<div class="hud-card"><div class="hud-label">CAMBIO MEDIO</div><div class="hud-value">{mean_chg:+.2f}%</div></div>', unsafe_allow_html=True)
        with col_m3:
            rsi_val = f'{results_df["RSI"].mean():.1f}' if "RSI" in results_df.columns else "N/A"
            st.markdown(f'<div class="hud-card"><div class="hud-label">RSI MEDIO</div><div class="hud-value">{rsi_val}</div></div>', unsafe_allow_html=True)
        with col_m4:
            rvol_val = f'{results_df["RVOL"].mean():.2f}x' if "RVOL" in results_df.columns else "N/A"
            st.markdown(f'<div class="hud-card"><div class="hud-label">RVOL MEDIO</div><div class="hud-value">{rvol_val}</div></div>', unsafe_allow_html=True)
        with col_m5:
            st.markdown(f'<div class="hud-card"><div class="hud-label">TIEMPO EJECUCIÓN</div><div class="hud-value">{duration:.2f}s</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        col_table, col_chart = st.columns([1.1, 1.9], gap="medium")

        with col_table:
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                <span style="font-size: 13px; font-weight: 700; color: #FFFFFF; text-transform: uppercase;">
                    Resultados del Screener
                </span>
                <span style="font-size: 11px; color: #00F0FF; font-weight: 600;">
                    💡 Haz clic en una fila para ver su gráfico
                </span>
            </div>
            """, unsafe_allow_html=True)

            compact_cols = ["Ticker", "Precio", "Cambio %"]
            if "Pivot High ($)" in results_df.columns:
                compact_cols.append("Pivot High ($)")
            if "Dist Pivot %" in results_df.columns:
                compact_cols.append("Dist Pivot %")
            if "20% Trailing Stop ($)" in results_df.columns:
                compact_cols.append("20% Trailing Stop ($)")
            if "ROC (100d) %" in results_df.columns:
                compact_cols.append("ROC (100d) %")
            if "EMA 100 Slope %" in results_df.columns:
                compact_cols.append("EMA 100 Slope %")
            if "Gap %" in results_df.columns and "Pivot High ($)" not in results_df.columns:
                compact_cols.append("Gap %")
            if "RVOL" in results_df.columns:
                compact_cols.append("RVOL")
            if "Vela Momentum" in results_df.columns:
                compact_cols.append("Vela Momentum")
            if "ADR (10s) %" in results_df.columns and "Pivot High ($)" not in results_df.columns:
                compact_cols.append("ADR (10s) %")
            if "Avg $Vol (20s) $M" in results_df.columns:
                compact_cols.append("Avg $Vol (20s) $M")
            elif "Vol Dólares ($M)" in results_df.columns:
                compact_cols.append("Vol Dólares ($M)")
            if "Posición Rango %" in results_df.columns and "Pivot High ($)" not in results_df.columns:
                compact_cols.append("Posición Rango %")

            table_df = results_df[compact_cols].copy()

            col_cfg = {
                "Ticker": st.column_config.TextColumn("Ticker", help="Símbolo del activo"),
                "Precio": st.column_config.NumberColumn("Precio", format="$%.2f"),
                "Cambio %": st.column_config.NumberColumn("Cambio %", format="%+.2f%%"),
                "Pivot High ($)": st.column_config.NumberColumn("Pivote (5L/5R)", format="$%.2f"),
                "Dist Pivot %": st.column_config.NumberColumn("Dist Pivote", format="%+.2f%%"),
                "20% Trailing Stop ($)": st.column_config.NumberColumn("Stop 20% (•••)", format="$%.2f"),
                "ROC (100d) %": st.column_config.NumberColumn("ROC 100d", format="%+.1f%%"),
                "EMA 100 Slope %": st.column_config.NumberColumn("EMA100 Slope", format="%+.1f%%"),
                "Vela Momentum": st.column_config.TextColumn("Vela Momentum"),
                "Gap %": st.column_config.NumberColumn("Gap %", format="%+.2f%%"),
                "RVOL": st.column_config.NumberColumn("RVOL 20d", format="%.2fx"),
                "ADR (10s) %": st.column_config.NumberColumn("ADR (10s) %", format="%.1f%%"),
                "Avg $Vol (20s) $M": st.column_config.NumberColumn("Vol 20d", format="$%.1fM"),
                "Vol Dólares ($M)": st.column_config.NumberColumn("Vol $", format="$%.0fM"),
                "Posición Rango %": st.column_config.NumberColumn("Rango %", format="%.0f%%")
            }

            selection = st.dataframe(
                table_df,
                width="stretch",
                height=460,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={k: v for k, v in col_cfg.items() if k in compact_cols}
            )

            if selection and hasattr(selection, "selection") and selection.selection.rows:
                clicked_idx = selection.selection.rows[0]
                if clicked_idx < len(table_df):
                    clicked_ticker = table_df.iloc[clicked_idx]["Ticker"]
                    if clicked_ticker != st.session_state.get("selected_screener_ticker"):
                        st.session_state["selected_screener_ticker"] = clicked_ticker
                        st.rerun()

            selected_ticker = st.session_state.get("selected_screener_ticker", table_df.iloc[0]["Ticker"])

            # Botones de difusión a Discord
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            col_disc_act1, col_disc_act2 = st.columns(2)
            with col_disc_act1:
                if st.button(f"📢 Alerta {selected_ticker}", use_container_width=True):
                    if discord_url:
                        row = results_df[results_df["Ticker"] == selected_ticker].iloc[0].to_dict()
                        ok = discord.send_trade_alert(discord_url, row, scan_type=strategy)
                        if ok: st.success(f"¡Enviado {selected_ticker}!")
                        else: st.error("Error al enviar.")
                    else:
                        st.error("Configura el Webhook en la barra lateral.")
            with col_disc_act2:
                if st.button("🚀 Enviar Todo", use_container_width=True):
                    if discord_url:
                        count = 0
                        for _, r in results_df.head(10).iterrows():
                            if discord.send_trade_alert(discord_url, r.to_dict(), scan_type=strategy):
                                count += 1
                        st.success(f"{count} alertas enviadas a Discord.")
                    else:
                        st.error("Configura el Webhook.")

        with col_chart:
            render_institutional_chart(selected_ticker, key_suffix="screener_main")

        # Tabla completa expandible con todas las métricas institucionales y exportación CSV
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.expander(f"📊 Tabla Cuantitativa Completa ({len(results_df)} activos) & Descarga CSV", expanded=False):
            st.dataframe(results_df, width="stretch")
            csv_data = results_df.to_csv(index=False).encode('utf-8')
            clean_strat = strategy.replace(' ', '_').replace(':', '').replace('>', 'GT').replace('(', '').replace(')', '').replace('$', 'USD_')
            st.download_button(
                label="📥 Descargar Resultados Cuantitativos (.CSV)",
                data=csv_data,
                file_name=f"TradingVolt_{clean_strat}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        if btn_scan:
            st.warning("⚠️ No se encontraron activos que cumplan con todos los criterios bajo los parámetros actuales.")
        else:
            st.info("👆 Selecciona tu filtro cuantitativo e inicia el escaneo con el botón principal.")


# -----------------------------------------------------------------------------
# VISTA 3: TERMINAL CANSLIM LÍDERES • BREAKOUT DESK (BO60)
# -----------------------------------------------------------------------------
elif "CANSLIM" in nav_view:
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(0, 255, 135, 0.08)); border: 1px solid rgba(14, 165, 233, 0.35); border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(14, 165, 233, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                        <span>🚀</span> Terminal CANSLIM Líderes • Breakout Desk (BO60)
                    </h2>
                    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;">
                        Estrategia de Rupturas de 60 Días & Zonas de Compra de William O'Neil [0%, +5%] aplicada con exclusividad sobre los activos de <strong>True Market Leaders (TML)</strong>.
                    </p>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: rgba(0, 255, 135, 0.15); border: 1px solid #00FF87; color: #00FF87; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">● TML EXCLUSIVE FILTER</span>
                    <span style="background: rgba(14, 165, 233, 0.15); border: 1px solid #38BDF8; color: #38BDF8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">BO60 STRATEGY</span>
                    <span style="background: rgba(168, 85, 247, 0.15); border: 1px solid #A855F7; color: #A855F7; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">CANSLIM 360°</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_top_ctrl1, col_top_ctrl2, col_top_ctrl3, col_top_ctrl4 = st.columns([1.5, 1.8, 1.2, 0.9])
    with col_top_ctrl1:
        active_radar_obj = are.get_active_radar() if are else {"tickers": [], "count": 0, "source": "Screener"}
        radar_count_val = active_radar_obj.get("count", len(active_radar_obj.get("tickers", [])))
        radar_src_val = active_radar_obj.get("source", "Screener")

        tml_source_choice = st.selectbox(
            "Fuente del Universo:",
            [
                "🤖 Detección Autónoma TradingVolt (Recomendado)",
                f"🎯 Radar Activo del Screener ({radar_count_val} activos de {radar_src_val})",
                "🏆 Lista Oficial TML (301 Activos - Benchmark Auditoría)"
            ],
            index=0,
            key="sel_tml_source"
        )
    with col_top_ctrl2:
        layout_mode = st.radio(
            "Disposición de Pantalla:",
            ["🖥️ Vista Pro Expandida (Recomendada)", "📊 Vista Multi-Panel (3 Col.)"],
            horizontal=True,
            index=0,
            key="rad_canslim_layout"
        )
    with col_top_ctrl3:
        max_scan_choice = st.selectbox("Profundidad:", ["Todos los Líderes (301)", "Top 100", "Top 50"], index=0, key="sel_tml_depth")
    with col_top_ctrl4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_rescan_tml = st.button("🔄 Refrescar", use_container_width=True, key="btn_rescan_tml")

    is_auto = "Autónoma" in tml_source_choice or "Autónomo" in tml_source_choice
    max_stocks = 301 if ("301" in max_scan_choice or "Todos" in max_scan_choice) else (100 if "100" in max_scan_choice else 50)
    tml_cache_key = f"canslim_tml_df_{'auto' if is_auto else 'official'}_{max_stocks}"

    if "Radar Activo" in tml_source_choice:
        raw_univ = are.get_active_radar_tickers(max_items=max_stocks) if are else cte.TML_UNIVERSE
        target_universe = raw_univ if raw_univ else cte.TML_UNIVERSE
        univ_label = f"🎯 Radar Activo del Screener ({len(target_universe)} activos)"
    elif is_auto:
        raw_univ = get_autonomous_market_leaders(top_n=max_stocks)
        target_universe = raw_univ if raw_univ else cte.TML_UNIVERSE
        univ_label = "🤖 Líderes Autónomos TradingVolt"
    else:
        target_universe = cte.TML_UNIVERSE
        univ_label = "🏆 Líderes Oficiales TML (Benchmark)"

    if btn_rescan_tml or tml_cache_key not in st.session_state:
        with st.spinner(f"Analizando {univ_label} ({len(target_universe)} activos) y calculando pivotes BO60..."):
            try:
                df_tml_scan = cte.scan_canslim_tml_universe(tickers=target_universe, max_stocks=max_stocks)
                st.session_state[tml_cache_key] = df_tml_scan
            except Exception as e:
                st.error(f"Error procesando escaneo CANSLIM: {e}")
                df_tml_scan = pd.DataFrame()
    else:
        df_tml_scan = st.session_state[tml_cache_key]

    if df_tml_scan is not None and not df_tml_scan.empty:
        # HUD Superior de Métricas con fuentes ampliadas
        n_total = len(df_tml_scan)
        n_uptrend = int(df_tml_scan["is_uptrend"].sum())
        n_bo_today = len(df_tml_scan[df_tml_scan["status_tag"].isin(["BREAKOUT_TODAY", "BREAKOUT_EXTENDED"])])
        n_buy_zone = len(df_tml_scan[df_tml_scan["status_tag"] == "IN_BUY_ZONE"])
        n_watch_pre = len(df_tml_scan[df_tml_scan["status_tag"] == "WATCH_PRE"])
        n_extended = len(df_tml_scan[df_tml_scan["status_tag"] == "EXTENDED"])

        st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 18px;">
                <div class="canslim-hud-big" style="border-left: 3px solid #00F0FF;">
                    <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Líderes TML</div>
                    <div style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-top: 4px;">{n_total}</div>
                    <div style="font-size: 11px; color: #38BDF8; font-weight: 600;">Universo Exclusivo</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #00FF87;">
                    <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">En Tendencia Alcista</div>
                    <div style="font-size: 26px; font-weight: 900; color: #00FF87; margin-top: 4px;">{n_uptrend}</div>
                    <div style="font-size: 11px; color: #00FF87; font-weight: 600;">{(n_uptrend/n_total)*100:.0f}% en Stage 2</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #FF8C00;">
                    <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">🚀 Breakout Hoy (BO60)</div>
                    <div style="font-size: 26px; font-weight: 900; color: #FF8C00; margin-top: 4px;">{n_bo_today}</div>
                    <div style="font-size: 11px; color: #FF8C00; font-weight: 600;">Entrada Inmediata</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #38BDF8;">
                    <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">🔵 En Zona Compra</div>
                    <div style="font-size: 26px; font-weight: 900; color: #38BDF8; margin-top: 4px;">{n_buy_zone}</div>
                    <div style="font-size: 11px; color: #38BDF8; font-weight: 600;">Rango [0%, +5%]</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #A855F7;">
                    <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">🔍 Vigilancia Pre-BO</div>
                    <div style="font-size: 26px; font-weight: 900; color: #A855F7; margin-top: 4px;">{n_watch_pre}</div>
                    <div style="font-size: 11px; color: #A855F7; font-weight: 600;">Rango [-2.5%, 0%]</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #F43F5E;">
                    <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">⚠️ Extendidas</div>
                    <div style="font-size: 26px; font-weight: 900; color: #F43F5E; margin-top: 4px;">{n_extended}</div>
                    <div style="font-size: 11px; color: #F43F5E; font-weight: 600;">&gt; +5% de compra</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        is_expanded_view = "Expandida" in layout_mode

        # ==================== CONTROLES DE LISTA Y FILTROS ====================
        def render_watchlist_controls():
            st.markdown("##### 📋 Listas y Filtros Tácticos")
            sub_uni = st.selectbox(
                "Sub-Universo:",
                [
                    "Todos los Líderes TML",
                    "En Tendencia Alcista (Stage 2)",
                    "Top 50 Composite Score",
                    "Solo Rupturas y Zona de Compra"
                ],
                index=0,
                key="sel_sub_uni_ctrl"
            )

            quick_filt = st.radio(
                "Filtro Rápido de Estado:",
                [
                    "🔘 Todos los Estados",
                    "🚀 Breakout Hoy (Entrada Inmediata)",
                    "🔵 En Zona de Compra (0% a +5%)",
                    "🔍 Vigilancia Pre-Breakout (-2.5% a 0%)",
                    "🔄 Breakout & Retest",
                    "⚠️ Extendidas (> +5%)"
                ],
                index=0,
                key="rad_quick_filt_ctrl"
            )

            filtered_df = df_tml_scan.copy()
            if "Tendencia Alcista" in sub_uni:
                filtered_df = filtered_df[filtered_df["is_uptrend"] == True]
            elif "Top 50" in sub_uni:
                filtered_df = filtered_df.head(50)
            elif "Solo Rupturas" in sub_uni:
                filtered_df = filtered_df[filtered_df["status_tag"].isin(["BREAKOUT_TODAY", "BREAKOUT_EXTENDED", "IN_BUY_ZONE", "WATCH_PRE", "RETEST"])]

            if "Breakout Hoy" in quick_filt:
                filtered_df = filtered_df[filtered_df["status_tag"].isin(["BREAKOUT_TODAY", "BREAKOUT_EXTENDED"])]
            elif "En Zona de Compra" in quick_filt:
                filtered_df = filtered_df[filtered_df["status_tag"] == "IN_BUY_ZONE"]
            elif "Vigilancia Pre-Breakout" in quick_filt:
                filtered_df = filtered_df[filtered_df["status_tag"] == "WATCH_PRE"]
            elif "Retest" in quick_filt:
                filtered_df = filtered_df[filtered_df["status_tag"] == "RETEST"]
            elif "Extendidas" in quick_filt:
                filtered_df = filtered_df[filtered_df["status_tag"] == "EXTENDED"]

            search_t = st.text_input("🔍 Buscar Ticker:", "", placeholder="Ej. NUTX, PLTR, CDNA...").strip().upper()
            if search_t:
                filtered_df = filtered_df[filtered_df["ticker"].str.contains(search_t)]

            st.caption(f"Mostrando **{len(filtered_df)}** de {len(df_tml_scan)} activos.")

            if not filtered_df.empty:
                ticker_options = []
                for _, r in filtered_df.iterrows():
                    lbl = f"{r['badge_icon']} {r['ticker']} • ${r['price']:.2f} ({r['change_pct']:+.1f}%) • Score {r['composite_score']} • {r['status']}"
                    ticker_options.append((r['ticker'], lbl))

                sel_ticker = st.selectbox(
                    "Seleccionar Activo para Análisis:",
                    options=[t[0] for t in ticker_options],
                    format_func=lambda x: next((t[1] for t in ticker_options if t[0] == x), x),
                    index=0,
                    key="sel_active_canslim_ticker"
                )

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.dataframe(
                    filtered_df[["ticker", "price", "dist_pivot_pct", "rvol", "composite_score", "status"]].rename(columns={
                        "ticker": "Ticker",
                        "price": "Precio ($)",
                        "dist_pivot_pct": "Pivote %",
                        "rvol": "RVOL",
                        "composite_score": "Score",
                        "status": "Estado"
                    }),
                    use_container_width=True,
                    height=380 if is_expanded_view else 280,
                    hide_index=True
                )
                return sel_ticker
            else:
                st.warning("No hay activos en este filtro.")
                return df_tml_scan["ticker"].iloc[0] if not df_tml_scan.empty else "NUTX"

        # ==================== RENDERIZADO DEL GRÁFICO PRO ====================
        def render_big_chart(selected_ticker, chart_height=560):
            sel_row = df_tml_scan[df_tml_scan["ticker"] == selected_ticker]
            if not sel_row.empty:
                row_data = sel_row.iloc[0].to_dict()
            else:
                row_data = {
                    "price": 100.0, "change_pct": 0.0, "pivot_60d": 100.0, "dist_pivot_pct": 0.0,
                    "rvol": 1.0, "atr_14": 2.5, "adr_10": 3.0, "status": "En Base", "status_color": "#00FF87",
                    "badge_icon": "🔵", "composite_score": 75, "rs_rating": 80, "ad_rating": "B"
                }

            s_piv = row_data.get("pivot_60d", 100.0)
            s_price = row_data.get("price", 100.0)
            s_dist = row_data.get("dist_pivot_pct", 0.0)
            s_rvol = row_data.get("rvol", 1.0)
            s_status = row_data.get("status", "En Base")
            s_color = row_data.get("status_color", "#38BDF8")
            s_atr = row_data.get("atr_14", 1.0)
            s_adr = row_data.get("adr_10", 2.0)

            # Header grande del ticker
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #0F141F 0%, #171E2E 100%); border: 1px solid #232D42; border-radius: 10px; padding: 14px 20px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <div>
                        <div style="display: flex; align-items: baseline; gap: 12px;">
                            <span style="font-size: 28px; font-weight: 900; color: #FFFFFF;">{selected_ticker}</span>
                            <span style="font-size: 24px; font-weight: 800; color: #00F0FF;">${s_price:.2f}</span>
                            <span style="font-size: 15px; font-weight: 700; color: {'#00FF87' if row_data.get('change_pct', 0) >= 0 else '#FF2E63'};">{row_data.get('change_pct', 0):+.2f}%</span>
                        </div>
                        <div style="font-size: 13px; color: #94A3B8; margin-top: 3px;">
                            Pivote 60d: <strong style="color: #FF8C00;">${s_piv:.2f}</strong> (<strong style="color: {'#00FF87' if s_dist>=0 else '#94A3B8'};">{s_dist:+.2f}%</strong>) • 
                            RVOL: <strong style="color: #00FF87;">{s_rvol:.2f}x</strong> • 
                            ATR: <strong>${s_atr:.2f}</strong> ({s_adr:.1f}% ADR)
                        </div>
                    </div>
                    <div>
                        <div style="background: rgba(19, 24, 38, 0.95); border: 2px solid {s_color}; border-radius: 8px; padding: 10px 18px; text-align: center; box-shadow: 0 0 16px {s_color}33;">
                            <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">ESTADO TÁCTICO O'NEIL</div>
                            <div style="font-size: 15px; font-weight: 900; color: {s_color}; margin-top: 3px;">{s_status}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            try:
                df_hist = yf.download(selected_ticker, period="1y", interval="1d", progress=False)
                if isinstance(df_hist.columns, pd.MultiIndex):
                    df_hist.columns = df_hist.columns.get_level_values(0)
                df_hist = df_hist.dropna()
            except Exception:
                df_hist = pd.DataFrame()

            if not df_hist.empty and len(df_hist) >= 20:
                df_hist['SMA_50'] = df_hist['Close'].rolling(50).mean()
                df_hist['SMA_200'] = df_hist['Close'].rolling(200).mean()
                df_hist['VOL_50'] = df_hist['Volume'].rolling(50).mean()

                sub_plot = df_hist.tail(120).copy()

                fig_can = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.74, 0.26]
                )

                fig_can.add_trace(go.Candlestick(
                    x=sub_plot.index,
                    open=sub_plot['Open'],
                    high=sub_plot['High'],
                    low=sub_plot['Low'],
                    close=sub_plot['Close'],
                    name=selected_ticker,
                    increasing_line_color="#00FF87",
                    decreasing_line_color="#FF2E63"
                ), row=1, col=1)

                fig_can.add_trace(go.Scatter(
                    x=sub_plot.index,
                    y=sub_plot['SMA_50'],
                    mode="lines",
                    name="SMA 50 (Institucional)",
                    line=dict(color="#00F0FF", width=2.0)
                ), row=1, col=1)

                if sub_plot['SMA_200'].notna().any():
                    fig_can.add_trace(go.Scatter(
                        x=sub_plot.index,
                        y=sub_plot['SMA_200'],
                        mode="lines",
                        name="SMA 200 (Tendencia)",
                        line=dict(color="#F59E0B", width=1.8, dash="dash")
                    ), row=1, col=1)

                fig_can.add_hline(
                    y=s_piv,
                    line_dash="dash",
                    line_color="#FF8C00",
                    line_width=2.5,
                    annotation_text=f"Pivote 60d (${s_piv:.2f})",
                    annotation_position="top left",
                    annotation_font=dict(size=12, color="#FF8C00"),
                    row=1, col=1
                )

                fig_can.add_hrect(
                    y0=s_piv,
                    y1=s_piv * 1.05,
                    fillcolor="rgba(14, 165, 233, 0.20)",
                    line_width=1.5,
                    line_color="#38BDF8",
                    annotation_text="Zona de Compra O'Neil (+5%)",
                    annotation_position="top right",
                    annotation_font=dict(size=11, color="#38BDF8"),
                    row=1, col=1
                )

                vol_colors = np.where(sub_plot['Close'] >= sub_plot['Open'], "#00FF87", "#FF2E63")
                fig_can.add_trace(go.Bar(
                    x=sub_plot.index,
                    y=sub_plot['Volume'],
                    name="Volumen",
                    marker_color=vol_colors,
                    opacity=0.8
                ), row=2, col=1)

                fig_can.add_trace(go.Scatter(
                    x=sub_plot.index,
                    y=sub_plot['VOL_50'],
                    mode="lines",
                    name="Media Vol 50d",
                    line=dict(color="#E2E8F0", width=1.8)
                ), row=2, col=1)

                fig_can.update_layout(
                    template="plotly_dark",
                    height=chart_height,
                    margin=dict(l=10, r=40, t=10, b=10),
                    paper_bgcolor="#0A0D14",
                    plot_bgcolor="#0A0D14",
                    xaxis_rangeslider_visible=False,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0,
                        font=dict(size=11, color="#94A3B8")
                    ),
                    yaxis=dict(side="right", gridcolor="#151C28", tickfont=dict(family="JetBrains Mono", size=11, color="#94A3B8")),
                    yaxis2=dict(side="right", gridcolor="#151C28", tickfont=dict(family="JetBrains Mono", size=10, color="#64748B"))
                )

                fig_can.update_xaxes(
                    rangebreaks=[dict(bounds=["sat", "mon"])],
                    gridcolor="#151C28",
                    tickfont=dict(family="JetBrains Mono", size=11, color="#64748B")
                )

                st.plotly_chart(fig_can, use_container_width=True)

            st.markdown(f"""
                <div style="display: flex; gap: 12px; margin-top: 4px; margin-bottom: 12px;">
                    <a href="https://www.tradingview.com/chart/?symbol={selected_ticker}" target="_blank" style="text-decoration: none; flex: 1;">
                        <div style="background: rgba(14, 165, 233, 0.15); border: 1px solid #38BDF8; color: #38BDF8; border-radius: 8px; padding: 10px 16px; text-align: center; font-size: 13px; font-weight: 800;">
                            📈 Abrir {selected_ticker} en Pantalla Completa (TradingView) ↗
                        </div>
                    </a>
                </div>
            """, unsafe_allow_html=True)
            return row_data

        # ==================== RENDERIZADO DEL SUPER PANEL CANSLIM 360° (GRAN FORMATO) ====================
        def render_canslim_full_matrix(row_data, selected_ticker):
            c_score = row_data.get("composite_score", 70)
            rs_score = row_data.get("rs_rating", 75)
            ad_score = row_data.get("ad_rating", "B")
            tech_s = row_data.get("tech_score", "4/5")

            st.markdown(f"""
                <div style="margin-top: 14px; margin-bottom: 16px;">
                    <h3 style="margin: 0; font-size: 20px; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 10px;">
                        <span>🔬</span> Diagnóstico Institucional CANSLIM 360° • William O'Neil Protocol ({selected_ticker})
                    </h3>
                    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;">
                        Evaluación integral de 7 factores de crecimiento, liderazgo técnico y acumulación de manos fuertes.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # 4 Grandes Tarjetas HUD Superiores
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.markdown(f"""
                    <div class="canslim-hud-big" style="border-top: 3px solid #00FF87;">
                        <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Puntaje Compuesto O'Neil</div>
                        <div style="font-size: 32px; font-weight: 900; color: #00FF87; margin-top: 4px;">{c_score} <span style="font-size: 16px; color: #64748B;">/ 99</span></div>
                        <div style="width: 100%; height: 10px; background: #1A2234; border-radius: 5px; overflow: hidden; margin-top: 8px;">
                            <div style="width: {c_score}%; height: 100%; background: linear-gradient(90deg, #3B82F6, #00FF87);"></div>
                        </div>
                        <div style="font-size: 11px; color: #38BDF8; font-weight: 600; margin-top: 6px;">Top {max(1, 100-c_score)}% del Mercado Global</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc2:
                st.markdown(f"""
                    <div class="canslim-hud-big" style="border-top: 3px solid #38BDF8;">
                        <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Fuerza Relativa IBD (RS)</div>
                        <div style="font-size: 32px; font-weight: 900; color: #38BDF8; margin-top: 4px;">{rs_score} <span style="font-size: 16px; color: #64748B;">/ 99</span></div>
                        <div style="font-size: 13px; color: #CBD5E1; font-weight: 700; margin-top: 6px;">Liderazgo vs S&P 500</div>
                        <div style="font-size: 11px; color: #00FF87; font-weight: 600; margin-top: 4px;">Supera al {rs_score}% de las acciones</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc3:
                st.markdown(f"""
                    <div class="canslim-hud-big" style="border-top: 3px solid #00FF87;">
                        <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Patrocinio Institucional</div>
                        <div style="font-size: 32px; font-weight: 900; color: #00FF87; margin-top: 4px;">Rating {ad_score}</div>
                        <div style="font-size: 13px; color: #CBD5E1; font-weight: 700; margin-top: 6px;">Acumulación 13 Semanas</div>
                        <div style="font-size: 11px; color: #00FF87; font-weight: 600; margin-top: 4px;">Flujo Dominante de Fondos</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc4:
                st.markdown(f"""
                    <div class="canslim-hud-big" style="border-top: 3px solid #F59E0B;">
                        <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Salud Técnica O'Neil</div>
                        <div style="font-size: 32px; font-weight: 900; color: #F59E0B; margin-top: 4px;">{tech_s} <span style="font-size: 16px; color: #64748B;">Alcista</span></div>
                        <div style="font-size: 13px; color: #CBD5E1; font-weight: 700; margin-top: 6px;">Stage 2 de Weinstein / O'Neil</div>
                        <div style="font-size: 11px; color: #38BDF8; font-weight: 600; margin-top: 4px;">Precio &gt; SMA 50 &gt; SMA 200</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Matriz C-A-N-S-L-I-M (7 Tarjetas Grandes y Espaciosas)
            diag = cte.get_canslim_360_diagnostic(row_data)

            # Fila 1 de Letras: C, A, N, S (4 columnas grandes)
            row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
            keys_row1 = ["C", "A", "N", "S"]
            cols_row1 = [row1_c1, row1_c2, row1_c3, row1_c4]

            for k, c_dest in zip(keys_row1, cols_row1):
                val = diag[k]
                stat_col = "#00FF87" if "🟢" in val["status"] else ("#EAB308" if "🟡" in val["status"] else "#FF2E63")
                bg_col = "rgba(0, 255, 135, 0.08)" if "🟢" in val["status"] else ("rgba(234, 179, 8, 0.08)" if "🟡" in val["status"] else "rgba(255, 46, 99, 0.08)")
                with c_dest:
                    st.markdown(f"""
                        <div class="canslim-card-box" style="border-top: 4px solid {stat_col}; min-height: 220px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="background: {stat_col}; color: #08090C; font-weight: 900; font-size: 13px; padding: 2px 8px; border-radius: 4px;">{val['letter']}</span>
                                        <span class="canslim-card-title">{val['title']}</span>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0;">
                                    <span style="background: {bg_col}; border: 1px solid {stat_col}; color: {stat_col}; font-weight: 800; font-size: 12px; padding: 4px 10px; border-radius: 6px;">
                                        {val['status']}
                                    </span>
                                    <span style="font-size: 12px; font-weight: 700; color: #FFFFFF;">
                                        {val.get('metric', '')}
                                    </span>
                                </div>
                                <div class="canslim-card-desc">
                                    {val['desc']}
                                </div>
                            </div>
                            <div class="canslim-rule-req">
                                📖 {val.get('rule', '')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            # Fila 2 de Letras: L, I, M (3 columnas grandes)
            row2_c1, row2_c2, row2_c3 = st.columns(3)
            keys_row2 = ["L", "I", "M"]
            cols_row2 = [row2_c1, row2_c2, row2_c3]

            for k, c_dest in zip(keys_row2, cols_row2):
                val = diag[k]
                stat_col = "#00FF87" if "🟢" in val["status"] else ("#EAB308" if "🟡" in val["status"] else "#FF2E63")
                bg_col = "rgba(0, 255, 135, 0.08)" if "🟢" in val["status"] else ("rgba(234, 179, 8, 0.08)" if "🟡" in val["status"] else "rgba(255, 46, 99, 0.08)")
                with c_dest:
                    st.markdown(f"""
                        <div class="canslim-card-box" style="border-top: 4px solid {stat_col}; min-height: 200px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="background: {stat_col}; color: #08090C; font-weight: 900; font-size: 13px; padding: 2px 8px; border-radius: 4px;">{val['letter']}</span>
                                        <span class="canslim-card-title">{val['title']}</span>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0;">
                                    <span style="background: {bg_col}; border: 1px solid {stat_col}; color: {stat_col}; font-weight: 800; font-size: 12px; padding: 4px 10px; border-radius: 6px;">
                                        {val['status']}
                                    </span>
                                    <span style="font-size: 12px; font-weight: 700; color: #FFFFFF;">
                                        {val.get('metric', '')}
                                    </span>
                                </div>
                                <div class="canslim-card-desc">
                                    {val['desc']}
                                </div>
                            </div>
                            <div class="canslim-rule-req">
                                📖 {val.get('rule', '')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        # ==================== HERRAMIENTAS CUANTITATIVAS (BACKTEST & RISK) ====================
        def render_quantitative_tools(selected_ticker, row_data):
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            tab_bt, tab_ps = st.tabs([
                f"🔬 Backtest Cuantitativo de Rupturas BO60 ({selected_ticker})",
                "🧮 Calculadora Táctica O'Neil (Position Sizing & Risk Management)"
            ])

            with tab_bt:
                st.markdown(f"<div style='font-size: 13px; color: #94A3B8; margin-bottom: 12px;'>Historial completo de todas las rupturas del máximo de 60 días capturadas en <strong>{selected_ticker}</strong> durante los últimos 2 años y su rentabilidad a 20 sesiones:</div>", unsafe_allow_html=True)
                
                with st.spinner(f"Analizando histórico de rupturas para {selected_ticker}..."):
                    bt_res = cte.run_canslim_bo60_backtest(selected_ticker, period_years=2, hold_days=20, stop_pct=7.0)

                if bt_res.get("success"):
                    bc1, bc2, bc3, bc4 = st.columns(4)
                    with bc1: st.metric("Rupturas Históricas", f"{bt_res['total_breakouts']}")
                    with bc2: st.metric("Win Rate (≥ 2R)", f"{bt_res['win_rate']}%", delta=f"{bt_res['win_trades']}/{bt_res['completed_trades']} éxitos")
                    with bc3: st.metric("Retorno Promedio R", f"{bt_res['avg_r']}R", help="Múltiplos de riesgo ganados sobre el stop loss de 7%")
                    with bc4: st.metric("Ganancia Máxima Promedio", f"+{bt_res['avg_max_gain_pct']}%", delta=f"Mejor: +{bt_res['best_r']}R")

                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                    if bt_res["trades"]:
                        df_bt_trades = pd.DataFrame(bt_res["trades"])
                        st.dataframe(
                            df_bt_trades.rename(columns={
                                "date": "Fecha Ruptura",
                                "entry": "Entrada ($)",
                                "pivot": "Pivote ($)",
                                "sl": "Stop Loss (-7%)",
                                "max_price": "Máx Precio ($)",
                                "max_pct": "Máx Ganancia (%)",
                                "max_r": "Múltiplo R",
                                "days_to_2r": "Días a 2R",
                                "result": "Resultado"
                            })[["Fecha Ruptura", "Entrada ($)", "Stop Loss (-7%)", "Máx Ganancia (%)", "Múltiplo R", "Días a 2R", "Resultado"]],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info(f"No se detectaron rupturas válidas con volumen en {selected_ticker} en los últimos 2 años.")
                else:
                    st.warning(bt_res.get("error", "No se pudo completar el backtest."))

            with tab_ps:
                st.markdown("<div style='font-size: 13px; color: #94A3B8; margin-bottom: 12px;'>Dimensionamiento institucional de la posición según la regla canónica del 7-8% de stop loss y targets escalonados:</div>", unsafe_allow_html=True)
                
                c_calc1, c_calc2, c_calc3 = st.columns(3)
                with c_calc1:
                    p_account = st.number_input("Capital de Cuenta ($):", min_value=1000.0, max_value=10_000_000.0, value=100_000.0, step=5000.0, key="ps_acc_wide")
                with c_calc2:
                    p_risk_pct = st.slider("Riesgo por Trade (% cuenta):", 0.25, 2.0, 1.0, 0.25, key="ps_risk_wide")
                with c_calc3:
                    p_stop_pct = st.slider("Stop Loss O'Neil (%):", 5.0, 10.0, 7.0, 0.5, key="ps_stop_pct_wide")

                c_entry = row_data.get("price", 100.0)
                c_sl = round(c_entry * (1.0 - (p_stop_pct / 100.0)), 2)

                ps_out = cte.calculate_position_sizing(p_account, p_risk_pct, c_entry, c_sl)

                if ps_out:
                    ps1, ps2, ps3, ps4 = st.columns(4)
                    with ps1: st.metric("Acciones a Comprar", f"{ps_out['shares']:,} acc")
                    with ps2: st.metric("Inversión Requerida", f"${ps_out['position_capital']:,.2f}", delta=f"{ps_out['position_portfolio_pct']}% cuenta")
                    with ps3: st.metric("Riesgo Máximo en $", f"${ps_out['dollar_risk']:,.2f}", delta=f"-{ps_out['risk_share_pct']}% acción")
                    with ps4: st.metric("Target O'Neil (+20%)", f"${ps_out['target_20pct']:.2f}", delta=f"+${ps_out['gain_t2']:,.2f} ({ps_out['rr_ratio_t2']} R:R)")

                    st.markdown(f"""
                        <div style="background: rgba(14, 165, 233, 0.08); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 8px; padding: 14px 18px; font-size: 13px; color: #CBD5E1; margin-top: 12px; line-height: 1.6;">
                            <strong>Plan de Salida Institucional:</strong><br>
                            • <strong>Stop Loss de Protección</strong>: <code>${c_sl:.2f}</code> (Pérdida monetaria limitada estrictamente a ${ps_out['dollar_risk']:,.2f}).<br>
                            • <strong>Objetivo 1 (+10%)</strong>: <code>${ps_out['target_10pct']:.2f}</code> (Ganancia esperada: +${ps_out['gain_t1']:,.2f} • Mover SL a Breakeven para asegurar trade sin riesgo).<br>
                            • <strong>Objetivo 2 (+20% O'Neil)</strong>: <code>${ps_out['target_20pct']:.2f}</code> (Ganancia esperada: +${ps_out['gain_t2']:,.2f} • Tomar beneficios institucionales 3:1).<br>
                            • <strong>Objetivo 3 (+25%)</strong>: <code>${ps_out['target_25pct']:.2f}</code> (Ganancia esperada: +${ps_out['gain_t3']:,.2f} • Ratio R:R de {round(ps_out['gain_t3']/(ps_out['dollar_risk']+1e-9), 1)}x).
                        </div>
                    """, unsafe_allow_html=True)

        # ==================== RENDERIZACIÓN SEGÚN EL MODO DE VISTA ====================
        if is_expanded_view:
            col_left, col_right = st.columns([1.05, 2.95], gap="medium")
            with col_left:
                selected_ticker = render_watchlist_controls()
            with col_right:
                row_data = render_big_chart(selected_ticker, chart_height=560)

            # Super Panel CANSLIM 360° a TODO EL ANCHO
            render_canslim_full_matrix(row_data, selected_ticker)

            # Herramientas Cuantitativas a TODO EL ANCHO
            render_quantitative_tools(selected_ticker, row_data)

        else:
            col_list, col_chart_bt, col_canslim_diag = st.columns([1.05, 1.85, 1.3], gap="medium")
            with col_list:
                selected_ticker = render_watchlist_controls()
            with col_chart_bt:
                row_data = render_big_chart(selected_ticker, chart_height=520)
                render_quantitative_tools(selected_ticker, row_data)
            with col_canslim_diag:
                st.markdown(f"##### 🔬 Diagnóstico CANSLIM 360° • {selected_ticker}")
                c_score = row_data.get("composite_score", 70)
                rs_score = row_data.get("rs_rating", 75)
                ad_score = row_data.get("ad_rating", "B")
                tech_s = row_data.get("tech_score", "4/5")

                st.markdown(f"""
                    <div style="background: #0E121B; border: 1px solid #1C2433; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px; font-weight: 700; color: #FFFFFF;">Composite Score</span>
                            <span style="font-size: 22px; font-weight: 900; color: #00FF87;">{c_score}/99</span>
                        </div>
                        <div style="width: 100%; height: 8px; background: #1A2234; border-radius: 4px; overflow: hidden; margin-top: 8px;">
                            <div style="width: {c_score}%; height: 100%; background: linear-gradient(90deg, #3B82F6, #00FF87);"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #94A3B8; margin-top: 10px;">
                            <span>RS: <strong style="color: #38BDF8;">{rs_score}/99</strong></span>
                            <span>A/D: <strong style="color: #00FF87;">{ad_score}</strong></span>
                            <span>Técnico: <strong style="color: #F59E0B;">{tech_s}</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                diag = cte.get_canslim_360_diagnostic(row_data)
                for key, val in diag.items():
                    stat_col = "#00FF87" if "🟢" in val["status"] else ("#EAB308" if "🟡" in val["status"] else "#FF2E63")
                    st.markdown(f"""
                        <div style="background: rgba(14, 18, 27, 0.85); border-left: 4px solid {stat_col}; border-radius: 6px; padding: 10px 12px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 13px; font-weight: 800; color: #E2E8F0;">{val['title']}</span>
                                <span style="font-size: 11px; font-weight: 800; color: {stat_col};">{val['status']}</span>
                            </div>
                            <div style="font-size: 12px; color: #CBD5E1; margin-top: 4px; line-height: 1.4;">
                                {val['desc']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    else:
        st.info("No hay datos de escaneo disponibles. Haz clic en 'Refrescar Líderes' para iniciar el análisis.")



# -----------------------------------------------------------------------------
# VISTA 4: QUANT OPTIONS & DEALER GEX DESK (QUANTLIB + CBOE LIVE GEX)
# -----------------------------------------------------------------------------
elif "Quant Options" in nav_view:
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(10, 14, 23, 0.95), rgba(19, 24, 38, 0.95)); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0, 240, 255, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                        <span>🎯</span> Quant Options & Dealer Gamma Desk
                    </h2>
                    <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 13px;">
                        Modelado institucional con <strong>QuantLib</strong> • Exposición Gamma de Creadores de Mercado (CBOE Live) • Niveles de Gamma Flip & Muros de Opciones
                    </p>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: rgba(0, 255, 135, 0.15); border: 1px solid #00FF87; color: #00FF87; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">● CBOE LIVE FEED</span>
                    <span style="background: rgba(0, 240, 255, 0.15); border: 1px solid #00F0FF; color: #00F0FF; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">QUANTLIB 20-ENGINE</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_uoa, tab_gex, tab_quantlib, tab_vbt = st.tabs([
        "🐋 Unusual Options Activity & Whale Flow (UOA)",
        "⚡ Dealer Gamma Exposure (GEX Live CBOE)",
        "🔬 Valorador Multi-Modelo QuantLib & Griegas",
        "📊 VectorBT: 4,851 Backtests Sweep"
    ])

    # ----------------- SUB-TAB 0: UNUSUAL OPTIONS ACTIVITY (UOA) -----------------
    with tab_uoa:
        st.markdown(r"""
            <div style="background: rgba(14, 18, 27, 0.7); border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-size: 15px; font-weight: 800; color: #FFFFFF;">🐋 Scanner de Actividad Inusual de Opciones (UOA) & Flujo de Ballenas</span>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">
                            Detección de aperturas institucionales agresivas donde <strong>Volumen &gt; Open Interest (V/OI &gt; 1.5x)</strong> y primas millonarias (100% Gratuito vía CBOE y Yahoo).
                        </div>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <span class="badge-neon-bull">V / OI ANOMALIES</span>
                        <span class="badge-neon-cyan">WHALE PREMIUMS</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_u_ctrl1, col_u_ctrl2, col_u_ctrl3, col_u_ctrl4, col_u_ctrl5 = st.columns([1.5, 1.1, 1.1, 1.1, 0.8])
        with col_u_ctrl1:
            uoa_preset = st.selectbox(
                "Activo o Canasta:",
                [
                    "🎯 Radar Activo del Screener (Canasta Dinámica)",
                    "🤖 Top Líderes Autónomos TradingVolt (Canasta)",
                    "NVDA (NVIDIA Corp)",
                    "SPY (S&P 500 ETF - CBOE Direct)",
                    "QQQ (Invesco QQQ Trust)",
                    "TSLA (Tesla Inc)",
                    "AAPL (Apple Inc)",
                    "PLTR (Palantir Tech)",
                    "AMD (Advanced Micro Devices)",
                    "AMZN (Amazon.com)",
                    "MSFT (Microsoft Corp)",
                    "META (Meta Platforms)",
                    "IWM (Russell 2000 ETF)",
                    "🏆 Top 10 Líderes TML (Benchmark Histórico)",
                    "✏️ Otro Ticker..."
                ],
                index=0,
                key="sel_uoa_preset"
            )
            if uoa_preset == "✏️ Otro Ticker...":
                uoa_sym = st.text_input("Ingresa Ticker:", "CRWD", key="txt_uoa_custom").strip().upper()
            else:
                uoa_sym = uoa_preset.split(" ")[0].strip()

        with col_u_ctrl2:
            voi_choices = {
                "≥ 1.5x (Aperturas)": 1.5,
                "≥ 2.0x (Anomalía)": 2.0,
                "≥ 3.0x (Alta Convicción)": 3.0,
                "≥ 5.0x (Extremo)": 5.0,
                "≥ 10.0x (Ultra Inusual)": 10.0
            }
            sel_voi_label = st.selectbox("Ratio V/OI Mínimo:", list(voi_choices.keys()), index=0, key="sel_uoa_voi")
            min_voi_val = voi_choices[sel_voi_label]

        with col_u_ctrl3:
            prem_choices = {
                "≥ $50,000": 50_000,
                "≥ $100,000 (Bloques)": 100_000,
                "≥ $250,000 (Institucional)": 250_000,
                "≥ $500,000 (Tiburón)": 500_000,
                "≥ $1,000,000 (Ballena)": 1_000_000
            }
            sel_prem_label = st.selectbox("Prima Mínima ($):", list(prem_choices.keys()), index=1, key="sel_uoa_prem")
            min_prem_val = prem_choices[sel_prem_label]

        with col_u_ctrl4:
            sent_choice = st.selectbox("Sentimiento:", ["Todos los Flujos", "🐂 Solo Calls (Alcistas)", "🐻 Solo Puts (Bajistas)"], index=0, key="sel_uoa_sent")

        with col_u_ctrl5:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_scan_uoa = st.button("🔄 Escanear UOA", use_container_width=True, key="btn_scan_uoa")

        uoa_cache_key = f"uoa_res_{uoa_sym}_{min_voi_val}_{min_prem_val}"

        if btn_scan_uoa or uoa_cache_key not in st.session_state:
            with st.spinner(f"Analizando actividad inusual de opciones para {uoa_sym}..."):
                if uoe:
                    if "Radar Activo" in uoa_preset or "🎯" in uoa_preset:
                        radar_syms = are.get_active_radar_tickers(max_items=12) if are else ["NVDA", "PLTR", "TSLA"]
                        df_uoa_raw = uoe.scan_multiticker_unusual_flow(radar_syms, min_v_oi=min_voi_val, min_premium=min_prem_val)
                    elif "Líderes Autónomos" in uoa_preset or "🤖" in uoa_preset:
                        auto_syms = get_autonomous_market_leaders(top_n=12)
                        df_uoa_raw = uoe.scan_multiticker_unusual_flow(auto_syms, min_v_oi=min_voi_val, min_premium=min_prem_val)
                    elif uoa_sym == "🏆":
                        tml_sample = ["AMN", "ALRM", "AMPL", "ANDG", "AGYS", "ANF", "CRWD", "NET", "FROG", "PLTR"]
                        df_uoa_raw = uoe.scan_multiticker_unusual_flow(tml_sample, min_v_oi=min_voi_val, min_premium=min_prem_val)
                    elif uoa_sym in ["SPY", "QQQ", "IWM", "SPX"]:
                        # CBOE official feed
                        df_cboe_raw = uoe.scan_cboe_unusual_options(uoa_sym, min_v_oi=min_voi_val, min_premium=min_prem_val)
                        if not df_cboe_raw.empty:
                            df_uoa_raw = df_cboe_raw.rename(columns={
                                "root": "Ticker",
                                "option": "Contrato",
                                "type": "Tipo",
                                "strike": "Strike ($)",
                                "exp_date": "Vencimiento",
                                "trade_time": "Hora Apertura (EST)",
                                "price": "Precio ($)",
                                "volume": "Volumen",
                                "open_interest": "Open Interest",
                                "v_oi_ratio": "Ratio V/OI",
                                "est_premium": "Prima Total ($)",
                                "premium_m": "Prima ($M)",
                                "sentiment": "Sentimiento"
                            })
                            df_uoa_raw["raw_prem"] = df_uoa_raw["Prima Total ($)"]
                        else:
                            df_uoa_raw = pd.DataFrame()
                    else:
                        df_uoa_raw = uoe.scan_single_stock_unusual_options(uoa_sym, min_v_oi=min_voi_val, min_premium=min_prem_val, max_expirations=4)
                    
                    st.session_state[uoa_cache_key] = df_uoa_raw
                else:
                    st.error("Módulo unusual_options_engine no disponible.")
                    df_uoa_raw = pd.DataFrame()
        else:
            df_uoa_raw = st.session_state[uoa_cache_key]

        if df_uoa_raw is not None and not df_uoa_raw.empty:
            df_uoa = df_uoa_raw.copy()
            if "Calls" in sent_choice:
                df_uoa = df_uoa[df_uoa["Tipo"] == "CALL"]
            elif "Puts" in sent_choice:
                df_uoa = df_uoa[df_uoa["Tipo"] == "PUT"]

            # Cálculos de Métricas HUD
            total_uoa_contracts = len(df_uoa)
            total_uoa_prem_m = (df_uoa["Prima Total ($)"].sum() / 1_000_000.0) if "Prima Total ($)" in df_uoa.columns else (df_uoa["Prima ($M)"].sum())
            max_voi = df_uoa["Ratio V/OI"].max() if "Ratio V/OI" in df_uoa.columns else 0.0

            call_prem = df_uoa[df_uoa["Tipo"] == "CALL"]["Prima Total ($)"].sum() if "Prima Total ($)" in df_uoa.columns else 0.0
            put_prem = df_uoa[df_uoa["Tipo"] == "PUT"]["Prima Total ($)"].sum() if "Prima Total ($)" in df_uoa.columns else 0.0
            tot_flow = call_prem + put_prem
            call_pct = (call_prem / tot_flow * 100.0) if tot_flow > 0 else 50.0

            bias_label = "🐂 ALCISTA (Call Sweeps)" if call_pct >= 60.0 else ("🐻 BAJISTA (Put Hedging)" if call_pct <= 40.0 else "⚖️ MIXTO / BIDIRECCIONAL")
            bias_color = "#00FF87" if call_pct >= 60.0 else ("#FF2E63" if call_pct <= 40.0 else "#00F0FF")

            st.markdown(f"""
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 18px;">
                    <div class="canslim-hud-big" style="border-left: 3px solid #00F0FF;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Contratos Inusuales</div>
                        <div style="font-size: 24px; font-weight: 900; color: #FFFFFF; margin-top: 4px;">{total_uoa_contracts}</div>
                        <div style="font-size: 11px; color: #38BDF8; font-weight: 600;">Filtrados V/OI &ge; {min_voi_val}x</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid #A855F7;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Prima Total Ballenas</div>
                        <div style="font-size: 24px; font-weight: 900; color: #A855F7; margin-top: 4px;">${total_uoa_prem_m:,.2f}M</div>
                        <div style="font-size: 11px; color: #A855F7; font-weight: 600;">En Dinero Comprometido</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid #FF8C00;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Máximo Ratio V / OI</div>
                        <div style="font-size: 24px; font-weight: 900; color: #FF8C00; margin-top: 4px;">{max_voi:.1f}x</div>
                        <div style="font-size: 11px; color: #FF8C00; font-weight: 600;">Apertura Más Agresiva</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid #38BDF8;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Ratio Calls vs Puts</div>
                        <div style="font-size: 24px; font-weight: 900; color: #38BDF8; margin-top: 4px;">{call_pct:.0f}% Calls</div>
                        <div style="font-size: 11px; color: #94A3B8; font-weight: 600;">{100-call_pct:.0f}% Puts en Primas</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid {bias_color};">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Sesgo Smart Money</div>
                        <div style="font-size: 17px; font-weight: 900; color: {bias_color}; margin-top: 6px;">{bias_label}</div>
                        <div style="font-size: 11px; color: {bias_color}; font-weight: 700;">Convicción Institucional</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Top 3 Whale Bets Cards
            st.markdown("##### 🏆 Mayores Apuestas Institucionales Detectadas:")
            top_3 = df_uoa.head(3)
            col_w1, col_w2, col_w3 = st.columns(3)
            for idx, (_, w_row) in enumerate(top_3.iterrows()):
                col_box = [col_w1, col_w2, col_w3][idx]
                w_col = "#00FF87" if w_row["Tipo"] == "CALL" else "#FF2E63"
                with col_box:
                    st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid {w_col}; border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="font-weight: 800; color: #FFFFFF; font-size: 15px;">{w_row.get('Ticker', uoa_sym)} ${w_row['Strike ($)']} {w_row['Tipo']}</span>
                                <span style="color: {w_col}; font-weight: 800; font-size: 14px;">${w_row['Prima ($M)']:.2f}M</span>
                            </div>
                            <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                                Vence: <strong style="color: #E2E8F0;">{w_row['Vencimiento']}</strong> | V/OI: <strong style="color: #FF8C00;">{w_row['Ratio V/OI']}x</strong>
                            </div>
                            <div style="font-size: 11px; color: #38BDF8; margin-top: 3px;">
                                ⏱️ Apertura: <strong style="color: #FFFFFF;">{w_row.get('Hora Apertura (EST)', 'N/A')}</strong>
                            </div>
                            <div style="font-size: 11px; color: #CBD5E1; margin-top: 4px;">
                                Vol: <strong>{w_row['Volumen']:,}</strong> vs OI: <strong>{w_row['Open Interest']:,}</strong> @ ${w_row['Precio ($)']:.2f}
                            </div>
                            <div style="font-size: 10.5px; color: {w_col}; font-weight: 700; margin-top: 6px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 4px;">
                                {w_row['Sentimiento']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            # Tabla completa de Opciones Inusuales
            st.markdown("##### 📋 Tabla de Flujo Inusual Completo")
            disp_cols = ["Ticker", "Contrato", "Tipo", "Strike ($)", "Vencimiento", "Hora Apertura (EST)", "Ratio V/OI", "Volumen", "Open Interest", "Precio ($)", "Prima ($M)", "Sentimiento"]
            available_cols = [c for c in disp_cols if c in df_uoa.columns]
            
            st.dataframe(
                df_uoa[available_cols],
                use_container_width=True,
                height=420,
                hide_index=True
            )

            # Exportación CSV
            csv_uoa = df_uoa.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Flujo Inusual (.CSV)",
                data=csv_uoa,
                file_name=f"TradingVolt_UOA_{uoa_sym}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No se detectaron contratos inusuales para {uoa_sym} que superen el filtro V/OI &ge; {min_voi_val}x y Prima &ge; ${min_prem_val:,.0f}. Prueba reduciendo los umbrales o refrescando el escaneo.")


    # ----------------- SUB-TAB 1: GEX LIVE CBOE -----------------
    with tab_gex:
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
        with col_ctrl1:
            sym_options = {
                "ES (Futuros E-mini S&P 500)": "ES",
                "NQ (Futuros E-mini Nasdaq 100)": "NQ",
                "SPY (SPDR S&P 500 ETF)": "SPY",
                "QQQ (Invesco QQQ Trust)": "QQQ",
                "SPX (S&P 500 Index CBOE)": "SPX",
                "IWM (Russell 2000 ETF)": "IWM",
                "NVDA (NVIDIA Corp)": "NVDA"
            }
            sel_label = st.selectbox("Activo Subyacente:", list(sym_options.keys()), index=0, key="gex_sym_sel")
            gex_sym = sym_options[sel_label]
        with col_ctrl2:
            r_rate = st.slider("Tasa Libre de Riesgo (%):", 0.0, 7.0, 4.5, 0.25, key="gex_rate_sel") / 100.0
        with col_ctrl3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_refresh_gex = st.button("🔄 Refrescar GEX en Vivo", use_container_width=True, key="btn_refresh_gex")

        cache_key = f"cboe_gex_data_{gex_sym}"
        if btn_refresh_gex or cache_key not in st.session_state:
            with st.spinner(f"Descargando cadena completa de opciones desde CBOE para {gex_sym}..."):
                try:
                    df_chain, spot_val, t_stamp, f_meta = qoe.fetch_cboe_option_chain(gex_sym)
                    gex_res = qoe.compute_dealer_gex(df_chain, spot_val, r=r_rate, futures_meta=f_meta)
                    gex_res["timestamp"] = t_stamp
                    gex_res["total_contracts"] = len(df_chain)
                    st.session_state[cache_key] = gex_res
                except Exception as e:
                    st.error(f"Error consultando CBOE: {e}")

        if cache_key in st.session_state and st.session_state[cache_key]:
            g_data = st.session_state[cache_key]
            is_fut = g_data.get("is_futures", False)
            f_meta = g_data.get("futures_meta", {})
            spot = g_data["spot"]
            cash_spot = g_data.get("cash_spot", spot)
            basis = g_data.get("basis", 0.0)
            net_gex = g_data["total_net_gex_m"]
            call_gex = g_data["total_call_gex_m"]
            put_gex = g_data["total_put_gex_m"]
            c_wall = g_data["call_wall"]
            p_wall = g_data["put_wall"]
            flip = g_data["gamma_flip"]
            regime = g_data["regime"]
            regime_col = g_data["regime_color"]

            unit_label = "pts" if is_fut else ""
            prefix = "" if is_fut else "$"

            # Banner si es contrato de futuros CME
            if is_fut:
                st.markdown(f"""
                    <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.35); border-radius: 8px; padding: 10px 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="font-weight: 800; color: #38BDF8; font-size: 14px;">⚡ Contrato de Futuros CME: {f_meta.get('name', gex_sym)} ({f_meta.get('ticker', '')})</span>
                            <span style="color: #94A3B8; font-size: 12px; margin-left: 12px;">Multiplicador: <strong>${f_meta.get('multiplier', 50)}/pt</strong></span>
                        </div>
                        <div style="font-size: 12px; color: #E2E8F0;">
                            Futuro: <strong style="color: #00F0FF;">{spot:,.2f} pts</strong> | 
                            Contado ({f_meta.get('cash_symbol', 'CASH')}): <strong>{cash_spot:,.2f}</strong> | 
                            Fair Value Basis: <strong style="color: {'#00FF87' if basis >= 0 else '#FF0055'};">{basis:+.2f} pts</strong> | 
                            Opciones CBOE: <strong>{g_data.get('total_contracts', 0):,}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Tarjetas de Métricas Clave
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            with m1:
                st.metric("Precio Spot", f"{prefix}{spot:,.2f} {unit_label}".strip(), delta=f"Base {basis:+.2f} pts" if is_fut else None)
            with m2:
                st.metric("Net Dealer GEX", f"${net_gex:,.1f}M / 1%", delta=f"{'+' if net_gex>=0 else ''}{net_gex:.1f}M")
            with m3:
                st.markdown(f"""
                    <div style="background: rgba(19, 24, 38, 0.8); border: 1px solid {regime_col}; border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="font-size: 11px; color: #94A3B8;">Régimen de Gamma</div>
                        <div style="font-size: 13px; font-weight: 800; color: {regime_col}; margin-top: 4px;">{regime.split('(')[0]}</div>
                    </div>
                """, unsafe_allow_html=True)
            with m4:
                st.metric("Nivel Gamma Flip", f"{prefix}{flip:,.2f} {unit_label}".strip(), delta=f"{spot - flip:+.2f} pts")
            with m5:
                st.metric("Call Wall (Techo)", f"{prefix}{c_wall:,.2f} {unit_label}".strip(), delta=f"{c_wall - spot:+.2f} pts")
            with m6:
                st.metric("Put Wall (Piso)", f"{prefix}{p_wall:,.2f} {unit_label}".strip(), delta=f"{p_wall - spot:+.2f} pts")

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # Gráficos de GEX
            col_chart1, col_chart2 = st.columns([3, 2])
            
            with col_chart1:
                # Gráfico de Barras: GEX por Strike
                strike_df = g_data["strike_data"]
                strike_col = "strike_display" if "strike_display" in strike_df.columns else "strike"
                # Filtrar strikes cercanos a spot (+/- 7%)
                strike_sub = strike_df[(strike_df[strike_col] >= spot * 0.93) & (strike_df[strike_col] <= spot * 1.07)]
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=strike_sub[strike_col],
                    y=strike_sub["call_gex_m"],
                    name="Call GEX (Positivo)",
                    marker_color="#00FF87"
                ))
                fig_bar.add_trace(go.Bar(
                    x=strike_sub[strike_col],
                    y=strike_sub["put_gex_m"],
                    name="Put GEX (Negativo)",
                    marker_color="#FF0055"
                ))
                
                # Líneas de Spot y Flip
                fig_bar.add_vline(x=spot, line_dash="dash", line_color="#00F0FF", annotation_text=f"Spot {spot:,.1f}", annotation_position="top left")
                fig_bar.add_vline(x=flip, line_dash="dot", line_color="#FFB800", annotation_text=f"Flip {flip:,.1f}", annotation_position="top right")
                
                fig_bar.update_layout(
                    title=f"<b>Distribución de Dealer Gamma por Strike ({gex_sym} {'Futuros' if is_fut else ''})</b>",
                    template="plotly_dark",
                    paper_bgcolor="rgba(10, 14, 23, 0.8)",
                    plot_bgcolor="rgba(10, 14, 23, 0.8)",
                    barmode="relative",
                    xaxis_title=f"Strike ({'Puntos de Futuro' if is_fut else '$'})",
                    yaxis_title="GEX ($ Millones por 1% de movimiento)",
                    height=420,
                    margin=dict(l=40, r=40, t=50, b=40),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_chart2:
                # Perfil continuo de Gamma
                grid_p = g_data["profile_grid"]
                prof_g = g_data["profile_gex"]
                
                fig_prof = go.Figure()
                fig_prof.add_trace(go.Scatter(
                    x=grid_p,
                    y=prof_g,
                    mode="lines",
                    name="Net Gamma Profile",
                    line=dict(color="#00F0FF", width=3)
                ))
                fig_prof.add_hline(y=0, line_color="#64748B", line_width=1)
                fig_prof.add_vline(x=spot, line_dash="dash", line_color="#FFFFFF", annotation_text=f"Spot {spot:,.1f}")
                fig_prof.add_vline(x=flip, line_dash="dot", line_color="#FFB800", annotation_text=f"Flip {flip:,.1f}")
                
                fig_prof.update_layout(
                    title=f"<b>Perfil Continuo de Gamma vs Precio ({gex_sym})</b>",
                    template="plotly_dark",
                    paper_bgcolor="rgba(10, 14, 23, 0.8)",
                    plot_bgcolor="rgba(10, 14, 23, 0.8)",
                    xaxis_title=f"Nivel de Precio {gex_sym} ({'Puntos' if is_fut else '$'})",
                    yaxis_title="Net GEX ($ Millones)",
                    height=420,
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig_prof, use_container_width=True)

            # Guía Interpretativa Rápida
            unit_str = "pts" if is_fut else "$"
            val_flip = f"{flip:,.2f} {unit_str}"
            val_cwall = f"{c_wall:,.2f} {unit_str}"
            val_pwall = f"{p_wall:,.2f} {unit_str}"
            st.markdown(f"""
                <div style="background: rgba(19, 24, 38, 0.7); border: 1px solid #2D3A54; border-radius: 8px; padding: 14px; margin-top: 10px;">
                    <div style="font-size: 13px; font-weight: 700; color: #00F0FF; margin-bottom: 6px;">🧠 Interpretación Institucional del Flujo de Gamma:</div>
                    <ul style="margin: 0; padding-left: 20px; font-size: 12px; color: #CBD5E1; line-height: 1.6;">
                        <li><strong>Long Gamma (Por encima de {val_flip})</strong>: Los creadores de mercado venden cuando el mercado sube y compran cuando baja. Esto <strong>amortigua la volatilidad</strong> y favorece estrategias de rango o reversión a la media.</li>
                        <li><strong>Short Gamma (Por debajo de {val_flip})</strong>: Los creadores de mercado venden cuando cae y compran cuando sube, <strong>acelerando las caídas y disparando la volatilidad</strong>. Si {gex_sym} pierde los {val_flip}, los movimientos intradiarios se vuelven violentos.</li>
                        <li><strong>Call Wall ({val_cwall})</strong> y <strong>Put Wall ({val_pwall})</strong>: Actúan como imanes y niveles clave de soporte y resistencia institucional.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

    # ----------------- SUB-TAB 2: QUANTLIB MULTI-MODEL PRICER -----------------
    with tab_quantlib:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        col_in1, col_in2 = st.columns([1, 2])
        
        with col_in1:
            st.markdown("#### ⚙️ Parámetros del Contrato")
            asset_preset = st.selectbox(
                "Preset de Instrumento:",
                [
                    "Futuros ES (E-mini S&P 500 - $50/pt)",
                    "Futuros NQ (E-mini Nasdaq 100 - $20/pt)",
                    "Acción / ETF ($100/contrato)",
                    "Personalizado"
                ],
                index=0,
                key="ql_asset_preset"
            )
            
            # Valores por defecto según el preset
            if "ES" in asset_preset:
                def_spot = 7705.0
                def_strike = 7710.0
                def_dte = 14
                def_iv = 14.5
                def_rf = 4.5
                def_div = 4.5
                def_mult = 50
                is_fut_preset = True
            elif "NQ" in asset_preset:
                def_spot = 29320.0
                def_strike = 29350.0
                def_dte = 14
                def_iv = 18.0
                def_rf = 4.5
                def_div = 4.5
                def_mult = 20
                is_fut_preset = True
            elif "Acción" in asset_preset:
                def_spot = 580.0
                def_strike = 585.0
                def_dte = 30
                def_iv = 16.0
                def_rf = 4.5
                def_div = 1.3
                def_mult = 100
                is_fut_preset = False
            else:
                def_spot = 100.0
                def_strike = 100.0
                def_dte = 30
                def_iv = 25.0
                def_rf = 4.5
                def_div = 1.0
                def_mult = 100
                is_fut_preset = False

            p_opt_type = st.radio("Tipo de Opción:", ["Call", "Put"], horizontal=True, key="ql_type")
            p_spot = st.number_input("Precio Spot / Futuro:", value=float(def_spot), step=5.0 if "NQ" in asset_preset else 1.0, key=f"ql_spot_{asset_preset}")
            p_strike = st.number_input("Strike:", value=float(def_strike), step=5.0 if "NQ" in asset_preset else 1.0, key=f"ql_strike_{asset_preset}")
            p_dte = st.slider("Días al Vencimiento (DTE):", 1, 365, int(def_dte), key=f"ql_dte_{asset_preset}")
            p_iv = st.slider("Volatilidad Implícita (%):", 5.0, 100.0, float(def_iv), 0.5, key=f"ql_iv_{asset_preset}") / 100.0
            p_rf = st.slider("Tasa Libre de Riesgo (%):", 0.0, 10.0, float(def_rf), 0.25, key=f"ql_rf_{asset_preset}") / 100.0
            
            if is_fut_preset:
                st.caption("ℹ️ *Modelo Black-76 para Futuros: el rendimiento por dividendo implícito se iguala automáticamente a la tasa libre de riesgo ($q = r$).*")
                p_div = p_rf
                p_mult = def_mult
                p_is_fut = True
            else:
                p_div = st.slider("Rendimiento por Dividendo (%):", 0.0, 5.0, float(def_div), 0.1, key=f"ql_div_{asset_preset}") / 100.0
                p_mult = st.number_input("Multiplicador del Contrato ($):", value=int(def_mult), step=10, key=f"ql_mult_{asset_preset}")
                p_is_fut = False

        with col_in2:
            st.markdown("#### 🔬 Valoración Multi-Modelo & Griegas (QuantLib)")
            res_ql = qoe.price_option_quantlib(
                spot=p_spot,
                strike=p_strike,
                dte_days=p_dte,
                iv=p_iv,
                rate=p_rf,
                div_yield=p_div,
                is_call=(p_opt_type == "Call"),
                is_futures=p_is_fut,
                multiplier=p_mult
            )

            if res_ql.get("success"):
                models = res_ql["models"]
                greeks = res_ql["greeks"]
                eep = res_ql["early_exercise_premium"]
                cost_bs = res_ql.get("contract_cost_bs", 0.0)
                cost_amer = res_ql.get("contract_cost_amer", 0.0)
                bs_name = "Black-76 (Europea)" if p_is_fut else "Black-Scholes (Europea)"

                # Métricas destacadas
                c_bs, c_bjer, c_cost, c_eep = st.columns(4)
                with c_bs:
                    st.metric(bs_name, f"{models.get(bs_name, 0):.2f} pts" if p_is_fut else f"${models.get(bs_name, 0):.4f}")
                with c_bjer:
                    st.metric("Bjerksund (Americana)", f"{models.get('Bjerksund-Stensland (Americana)', 0):.2f} pts" if p_is_fut else f"${models.get('Bjerksund-Stensland (Americana)', 0):.4f}")
                with c_cost:
                    st.metric("Costo x Contrato", f"${cost_amer:,.2f}", help=f"Prima Bjerksund multiplicada por ${p_mult}/contrato")
                with c_eep:
                    st.metric("Prima Anticipada (EEP)", f"{eep:.2f} pts" if p_is_fut else f"${eep:.4f}", help="Valor añadido por ejercicio anticipado americano")

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                # Tabla comparativa de modelos
                val_col_name = "Precio Teórico (Puntos)" if p_is_fut else "Precio Teórico ($)"
                df_models = pd.DataFrame([
                    {
                        "Modelo Cuantitativo": k,
                        "Tipo de Ejercicio": "Americana (CME)" if "Americana" in k else "Europea",
                        val_col_name: f"{v:.4f}",
                        "Costo Total Contrato ($)": f"${v * p_mult:,.2f}"
                    }
                    for k, v in models.items()
                ])
                st.dataframe(df_models, use_container_width=True, hide_index=True)

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("##### 📐 Griegas de Primer y Segundo Orden:")
                g1, g2, g3, g4, g5, g6, g7 = st.columns(7)
                with g1: st.metric("Delta (Δ)", f"{greeks.get('Delta', 0):.4f}")
                with g2: st.metric("Gamma (Γ)", f"{greeks.get('Gamma', 0):.4f}")
                with g3: st.metric("Vega (ν 1%)", f"${greeks.get('Vega (1%)', 0):.4f}")
                with g4: st.metric("Theta (θ 1d)", f"${greeks.get('Theta (1d)', 0):.4f}")
                with g5: st.metric("Rho (ρ 1%)", f"${greeks.get('Rho (1%)', 0):.4f}")
                with g6: st.metric("Vanna", f"{greeks.get('Vanna', 0):.4f}")
                with g7: st.metric("Volga", f"{greeks.get('Volga', 0):.4f}")
            else:
                st.error(f"Error calculando con QuantLib: {res_ql.get('error')}")

    # ----------------- SUB-TAB 3: VECTORBT SWEEP -----------------
    with tab_vbt:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="background: rgba(19, 24, 38, 0.7); border: 1px solid #2D3A54; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <h4 style="margin: 0 0 8px 0; color: #FFFFFF;">⚡ VectorBT: Barrido Vectorial de 4,851 Estrategias en SPY</h4>
                <p style="margin: 0; color: #94A3B8; font-size: 13px;">
                    Ejecutado sobre 10 años de datos diarios de SPY (2010 a 2019 in-sample). Se probaron todas las combinaciones de medias móviles rápidas y lentas de 2 a 100 días simultáneamente en <strong>4.5 segundos</strong> gracias a la compilación Numba JIT.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_vbt1, col_vbt2 = st.columns([1, 2])
        with col_vbt1:
            st.markdown("##### 🏆 Resultados Óptimos Encontrados:")
            st.markdown("""
                * **Mejor Pareja In-Sample (2010-2019)**:
                  * Media Rápida: **43 días**
                  * Media Lenta: **79 días**
                  * **Sharpe Ratio**: **1.25** (frente a 1.11 de Buy & Hold)
                  * Mediana de todas las 4,851 combinaciones: **0.88**
                * **Prueba Fuera de Muestra (Out-of-Sample 2020-2026)**:
                  * **Sharpe Ratio**: **1.10** (frente a 0.98 de Buy & Hold)
                  * **Retorno Total**: **+103%**
                  * **Máximo Drawdown**: **-21%** (frente al **-34%** de caída del Buy & Hold)
            """)
            st.info("💡 La estrategia 43/79 redujo el drawdown casi a la mitad preservando el Sharpe institucional.")

        with col_vbt2:
            heatmap_path = Path("C:/Users/kim17/.gemini/antigravity/scratch/quant-models/quant-options-tools/charts/vectorbt_sharpe_heatmap.png")
            if heatmap_path.exists():
                st.image(str(heatmap_path), caption="Mapa de Calor de Sharpe Ratio para 4,851 combinaciones de Medias Móviles en SPY (VectorBT)", use_container_width=True)
            else:
                st.warning("El gráfico del mapa de calor no fue encontrado en charts/. Puedes generarlo ejecutando `python vectorbt_sweep.py`.")


# -----------------------------------------------------------------------------
# VISTA 5: DARK POOL & OFF-EXCHANGE INSTITUTIONAL TAPE (100% GRATUITO)
# -----------------------------------------------------------------------------
elif "Dark Pool" in nav_view:
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(56, 189, 248, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                        <span>🕵️‍♂️</span> Dark Pool & Off-Exchange Institutional Tape
                    </h2>
                    <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 13px;">
                        Rastreo de transacciones ocultas en <strong>FINRA TRFs (Exchange 'D')</strong> • Clasificación de Ballenas (Whales ≥ $1M) • Sentimiento por Algoritmo Tick Rule • Clusters de Soportes Ocultos
                    </p>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: rgba(0, 255, 135, 0.15); border: 1px solid #00FF87; color: #00FF87; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">● 100% FREE FINRA TRF FEED</span>
                    <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">TICK RULE SENTIMENT</span>
                    <span style="background: rgba(168, 85, 247, 0.15); border: 1px solid #A855F7; color: #A855F7; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">WHALE CLUSTERS</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Controles superiores
    col_dp_ctrl1, col_dp_ctrl2, col_dp_ctrl3, col_dp_ctrl4 = st.columns([1.5, 1.3, 1.2, 0.9])
    
    with col_dp_ctrl1:
        dp_preset = st.selectbox(
            "Activo a Inspeccionar:",
            ["NVDA", "SPY", "QQQ", "TSLA", "AAPL", "AMZN", "MSFT", "META", "PLTR", "AMD", "✏️ Otro Ticker..."],
            index=0,
            key="dp_sel_preset"
        )
        if dp_preset == "✏️ Otro Ticker...":
            dp_ticker = st.text_input("Ingresa Ticker:", "R", key="dp_txt_custom").strip().upper()
        else:
            dp_ticker = dp_preset

    with col_dp_ctrl2:
        notional_choices = {
            "🔹 Sub-Bloques (≥ $50k)": 50_000,
            "📦 Bloques Estándar (≥ $100k)": 100_000,
            "🏛️ Gran Institucional (≥ $250k)": 250_000,
            "🦈 Tiburones (≥ $500k)": 500_000,
            "🐋 Solo Ballenas (≥ $1,000,000)": 1_000_000
        }
        sel_notional_label = st.selectbox("Filtro de Tamaño:", list(notional_choices.keys()), index=0, key="dp_sel_notional")
        min_notional_val = notional_choices[sel_notional_label]

    with col_dp_ctrl3:
        time_choices = {
            "Últimas 2 Horas": 120,
            "Últimas 4 Horas": 240,
            "Sesión Completa (8h)": 480
        }
        sel_time_label = st.selectbox("Ventana de Tiempo:", list(time_choices.keys()), index=1, key="dp_sel_time")
        lookback_mins = time_choices[sel_time_label]

    with col_dp_ctrl4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_refresh_dp = st.button("🔄 Refrescar Tape", use_container_width=True, key="btn_refresh_dp")

    dp_cache_key = f"dp_data_{dp_ticker}_{min_notional_val}_{lookback_mins}"
    
    if btn_refresh_dp or dp_cache_key not in st.session_state:
        with st.spinner(f"Analizando cinta de FINRA TRF / Dark Pools para {dp_ticker}..."):
            if dpe:
                dp_data = dpe.fetch_and_classify_dark_pools(
                    ticker=dp_ticker,
                    min_notional=min_notional_val,
                    lookback_minutes=lookback_mins,
                    limit=5000
                )
                st.session_state[dp_cache_key] = dp_data
            else:
                st.error("Módulo dark_pool_engine no disponible.")
                dp_data = {"success": False}
    else:
        dp_data = st.session_state[dp_cache_key]

    if dp_data and dp_data.get("success"):
        # HUD Superior de Dark Pool
        dpi_val = dp_data.get("dpi_pct", 0.0)
        tot_notional_m = dp_data.get("total_dp_notional", 0.0) / 1_000_000.0
        n_blocks = dp_data.get("matched_block_count", 0)
        bull_pct = dp_data.get("bull_ratio_pct", 50.0)
        sent_label = dp_data.get("sentiment_label", "EQUILIBRIO")
        sent_color = dp_data.get("sentiment_color", "#00F0FF")
        last_px = dp_data.get("last_price", 0.0)

        st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px;">
                <div class="canslim-hud-big" style="border-left: 3px solid #00F0FF;">
                    <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Activo & Precio</div>
                    <div style="font-size: 24px; font-weight: 900; color: #FFFFFF; margin-top: 4px;">{dp_ticker}</div>
                    <div style="font-size: 12px; color: #38BDF8; font-weight: 700;">${last_px:.2f} Spot</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid {'#00FF87' if dpi_val >= 50 else '#F59E0B'};">
                    <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Dark Pool Index (DPI)</div>
                    <div style="font-size: 24px; font-weight: 900; color: {'#00FF87' if dpi_val >= 50 else '#F59E0B'}; margin-top: 4px;">{dpi_val:.1f}%</div>
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 600;">Volumen Off-Exchange</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #A855F7;">
                    <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Nocional Oculto</div>
                    <div style="font-size: 24px; font-weight: 900; color: #A855F7; margin-top: 4px;">${tot_notional_m:,.2f}M</div>
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 600;">En Bloques Filtrados</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid #38BDF8;">
                    <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Bloques Detectados</div>
                    <div style="font-size: 24px; font-weight: 900; color: #38BDF8; margin-top: 4px;">{n_blocks:,}</div>
                    <div style="font-size: 11px; color: #38BDF8; font-weight: 600;">Impresiones TRF</div>
                </div>
                <div class="canslim-hud-big" style="border-left: 3px solid {sent_color};">
                    <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Sentimiento (Tick Rule)</div>
                    <div style="font-size: 18px; font-weight: 900; color: {sent_color}; margin-top: 6px;">{sent_label}</div>
                    <div style="font-size: 11px; color: {sent_color}; font-weight: 700;">{bull_pct:.1f}% Presión Compra</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_tape, tab_clusters, tab_multiscan, tab_stream = st.tabs([
            "🌊 Cinta de Prints Clasificados (Live Tape)",
            "🧱 Clusters de Precio (Soportes/Resistencias Ocultas)",
            "🏆 Scanner Multi-Activo (True Market Leaders)",
            "⚡ WebSocket Streaming en Terminal"
        ])

        # TAB 1: CINTA DE PRINTS
        with tab_tape:
            prints_df = dp_data.get("prints_df", pd.DataFrame())
            if not prints_df.empty:
                st.markdown(f"##### 📋 Impresiones Institucionales Registradas en FINRA TRF ({len(prints_df)} operaciones)")
                
                # Visualización estilizada
                st.dataframe(
                    prints_df[['time_str', 'price_str', 'size_str', 'notional_str', 'tier_label', 'side_label']].rename(columns={
                        'time_str': 'Hora (EST)',
                        'price_str': 'Precio',
                        'size_str': 'Acciones',
                        'notional_str': 'Nocional ($)',
                        'tier_label': 'Categoría Institucional',
                        'side_label': 'Dirección (Tick Rule)'
                    }),
                    use_container_width=True,
                    height=450,
                    hide_index=True
                )
            else:
                st.info(f"No se detectaron transacciones en Dark Pool con nocional superior a ${min_notional_val:,.0f} en la ventana seleccionada.")

        # TAB 2: CLUSTERS DE PRECIO
        with tab_clusters:
            clusters_df = dp_data.get("clusters_df", pd.DataFrame())
            if not clusters_df.empty:
                col_cl1, col_cl2 = st.columns([1.6, 1.4])
                with col_cl1:
                    st.markdown("##### 📊 Concentración de Volumen Institucional por Nivel de Precio")
                    fig_cl = go.Figure(go.Bar(
                        x=clusters_df['notional_m'],
                        y=[f"${p:.2f}" for p in clusters_df['price_cluster']],
                        orientation='h',
                        marker_color='#00F0FF',
                        text=[f"${v:.2f}M ({pct:.1f}%)" for v, pct in zip(clusters_df['notional_m'], clusters_df['pct_of_dp'])],
                        textposition='auto'
                    ))
                    fig_cl.update_layout(
                        template="plotly_dark",
                        height=380,
                        margin=dict(l=10, r=20, t=10, b=10),
                        paper_bgcolor="#0A0D14",
                        plot_bgcolor="#0A0D14",
                        xaxis_title="Nocional en Dark Pool ($M)",
                        yaxis_title="Nivel de Precio"
                    )
                    st.plotly_chart(fig_cl, use_container_width=True)

                with col_cl2:
                    st.markdown("##### 🎯 Tabla de Niveles Clave (Dark Pool Anclas)")
                    st.dataframe(
                        clusters_df[['price_cluster', 'notional_m', 'print_count', 'pct_of_dp']].rename(columns={
                            'price_cluster': 'Nivel ($)',
                            'notional_m': 'Total Nocional ($M)',
                            'print_count': 'Nº Prints',
                            'pct_of_dp': '% del Dark Pool'
                        }),
                        use_container_width=True,
                        height=380,
                        hide_index=True
                    )
            else:
                st.info("Sin suficientes datos para generar clusters de precio.")

        # TAB 3: SCANNER MULTI-ACTIVO
        with tab_multiscan:
            st.markdown("##### 🚀 Escaneo de Actividad en Dark Pools sobre Grupos de Activos")
            scan_group = st.selectbox(
                "Seleccionar Grupo:",
                ["🏆 Top 15 Líderes TML", "💻 Mega-Caps Tech", "⚡ ETFs Principales (SPY, QQQ, IWM, DIA, SMH)"],
                index=0,
                key="dp_sel_group"
            )
            if scan_group == "🏆 Top 15 Líderes TML":
                scan_tickers = ["AMN", "ALRM", "AMPL", "ANDG", "AGYS", "ANF", "CRWD", "NET", "FROG", "PLTR", "RHI", "GMAB", "TTAN", "TEAM", "FIGS"]
            elif scan_group == "💻 Mega-Caps Tech":
                scan_tickers = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "AMD", "NFLX"]
            else:
                scan_tickers = ["SPY", "QQQ", "IWM", "DIA", "SMH", "XLF", "XLE"]

            if st.button(f"🔍 Escanear Dark Pool en {len(scan_tickers)} Activos", key="btn_run_multi_dp"):
                with st.spinner("Descargando y analizando TRFs para el grupo..."):
                    df_multi = dpe.scan_multiticker_dark_pool_rankings(scan_tickers, min_notional=100_000, lookback_minutes=180)
                    if not df_multi.empty:
                        st.dataframe(
                            df_multi[['Ticker', 'Precio', 'DPI (%)', 'Nocional Dark Pool ($M)', 'Bloques Detectados', 'Ratio Comprador (%)', 'Sentimiento']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("No se encontraron bloques grandes en este grupo.")

        # TAB 4: GUÍA Y STREAMING TERMINAL
        with tab_stream:
            st.markdown("""
                <div style="background: rgba(14, 18, 27, 0.85); border: 1px solid #1E283D; border-radius: 8px; padding: 18px; margin-top: 10px;">
                    <h4 style="color: #00FF87; margin-top: 0;">⚡ Cómo ejecutar la Cinta en Tiempo Real por WebSocket (Ultra-Baja Latencia)</h4>
                    <p style="color: #CBD5E1; font-size: 13px; line-height: 1.6;">
                        Puedes abrir una consola independiente y dejar corriendo el Dark Pool Tape en vivo mientras operas. Cada vez que una ballena ejecute un bloque off-exchange, aparecerá en pantalla al milisegundo:
                    </p>
                    <div style="background: #08090C; border: 1px solid #1E2638; border-radius: 6px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #00F0FF; margin-bottom: 12px;">
                        python C:/Users/kim17/.gemini/antigravity/scratch/trading_screener/dark_pool_scanner.py --stream --ticker NVDA TSLA SPY QQQ --min-notional 100000
                    </div>
                    <ul style="color: #94A3B8; font-size: 12px; line-height: 1.8;">
                        <li><strong>100% Gratuito:</strong> Usa el feed IEX de tu cuenta de Alpaca sin costes de suscripción.</li>
                        <li><strong>Detección Inmediata:</strong> Filtra automáticamente los prints con <code>exchange == 'D'</code> (FINRA TRF).</li>
                        <li><strong>Parámetro <code>--min-notional</code>:</strong> Ajusta el umbral de dólares (ej. $50,000, $100,000, $1,000,000).</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error(f"Error cargando datos de Dark Pool: {dp_data.get('error', 'Desconocido')}")


# -----------------------------------------------------------------------------
# VISTA 6: MONITOR LULD & HALTS EN VIVO (GUARDARRAÍLES DE VOLATILIDAD NMS)
# -----------------------------------------------------------------------------
elif "LULD" in nav_view:
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(20, 10, 25, 0.95), rgba(35, 15, 30, 0.95)); border: 1px solid rgba(255, 0, 85, 0.35); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(255, 0, 85, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                        <span>🚨</span> Limit Up / Limit Down (LULD) & Market Halts Radar
                    </h2>
                    <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 13px;">
                        Monitoreo regulatorio del <strong>Plan NMS de la SEC</strong> • Techos y Suelos Legales de Volatilidad • Alerta Pre-Halt de 15 Segundos • Feed Oficial NASDAQ en Vivo
                    </p>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: rgba(0, 255, 135, 0.15); border: 1px solid #00FF87; color: #00FF87; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">● 100% FREE NASDAQ FEED</span>
                    <span style="background: rgba(255, 0, 85, 0.15); border: 1px solid #FF0055; color: #FF0055; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">TIER 1 (±5%) / TIER 2 (±10%)</span>
                    <span style="background: rgba(0, 240, 255, 0.15); border: 1px solid #00F0FF; color: #00F0FF; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">PRE-HALT RADAR</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_luld_guard, tab_halts_feed, tab_luld_chart, tab_luld_guide = st.tabs([
        "🛡️ Guardarraíles de Volatilidad (Índices, Mag 7 & Momentum)",
        "🛑 Feed en Vivo de Suspensiones (NASDAQ Live Halts)",
        "📊 Gráfico Interactivo con Bandas LULD",
        "📘 Manual Operativo de Halts & LULD"
    ])

    # ----------------- SUB-TAB 1: GUARDARRAÍLES LULD -----------------
    with tab_luld_guard:
        col_lg1, col_lg2, col_lg3 = st.columns([1.6, 1.4, 0.9])
        with col_lg1:
            luld_group_choice = st.selectbox(
                "Grupo a Monitorear:",
                [
                    "💻 Las 7 Magníficas (NVDA, AAPL, MSFT, AMZN, GOOGL, META, TSLA)",
                    "🏆 Índices & ETFs Core (SPY, QQQ, IWM, DIA, SMH, XLF, XBI)",
                    "🚀 Top Momentum Stocks (Líderes TML & Episodic Pivots)",
                    "✏️ Ticker Específico"
                ],
                index=0,
                key="luld_sel_grp"
            )
        with col_lg2:
            if "Magníficas" in luld_group_choice:
                active_luld_tickers = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA"]
            elif "Índices" in luld_group_choice:
                active_luld_tickers = ["SPY", "QQQ", "IWM", "DIA", "SMH", "XLF", "XBI"]
            elif "Momentum" in luld_group_choice:
                active_luld_tickers = ["PLTR", "RHI", "AMN", "ALRM", "AMPL", "CRWD", "NET", "FROG", "ANDG", "ANF"]
            else:
                cust_t = st.text_input("Ingresa Ticker:", "NVDA", key="txt_luld_single").strip().upper()
                active_luld_tickers = [cust_t]
        with col_lg3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_refresh_luld = st.button("🔄 Refrescar Bandas", use_container_width=True, key="btn_refresh_luld")

        # Escanear matriz LULD
        with st.spinner("Calculando techos y suelos LULD según Plan NMS..."):
            if le:
                df_luld_mat = le.get_luld_watchlist_matrix(active_luld_tickers)
            else:
                df_luld_mat = pd.DataFrame()

        if not df_luld_mat.empty:
            # Inspección rápida del primer activo o más cercano al halt
            top_stock = df_luld_mat.iloc[0]["Ticker"]
            g_top = le.calculate_luld_guardrails(top_stock)

            st.markdown(f"""
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px;">
                    <div class="canslim-hud-big" style="border-left: 3px solid #00F0FF;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Activo Focal</div>
                        <div style="font-size: 24px; font-weight: 900; color: #FFFFFF; margin-top: 4px;">{g_top['ticker']}</div>
                        <div style="font-size: 12px; color: #38BDF8; font-weight: 700;">${g_top['spot']:.2f} Spot</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid #FF0055;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Techo Limit Up</div>
                        <div style="font-size: 24px; font-weight: 900; color: #FF0055; margin-top: 4px;">${g_top['upper_band']:.2f}</div>
                        <div style="font-size: 11px; color: #FF0055; font-weight: 700;">+{g_top['dist_upper_pct']:.2f}% de margen</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid #00FF87;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Suelo Limit Down</div>
                        <div style="font-size: 24px; font-weight: 900; color: #00FF87; margin-top: 4px;">${g_top['lower_band']:.2f}</div>
                        <div style="font-size: 11px; color: #00FF87; font-weight: 700;">-{g_top['dist_lower_pct']:.2f}% de margen</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid #A855F7;">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Regulación NMS</div>
                        <div style="font-size: 22px; font-weight: 900; color: #A855F7; margin-top: 4px;">±{g_top['band_pct']:.1f}%</div>
                        <div style="font-size: 10.5px; color: #94A3B8; font-weight: 600;">{g_top['tier_desc']}</div>
                    </div>
                    <div class="canslim-hud-big" style="border-left: 3px solid {g_top['alert_color']};">
                        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Riesgo de Halt</div>
                        <div style="font-size: 18px; font-weight: 900; color: {g_top['alert_color']}; margin-top: 6px;">{g_top['risk_level']}</div>
                        <div style="font-size: 10.5px; color: {g_top['alert_color']}; font-weight: 700;">Margen: {g_top['min_dist_pct']:.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 📋 Matriz Comparativa de Guardarraíles LULD")
            st.dataframe(
                df_luld_mat[['Ticker', 'Spot ($)', 'Techo LULD (+Limit Up)', 'Suelo LULD (-Limit Down)', 'Banda (%)', 'Distancia al Halt', 'Alerta LULD']],
                use_container_width=True,
                height=350,
                hide_index=True
            )
        else:
            st.warning("No se pudieron cargar bandas LULD para los activos seleccionados.")

    # ----------------- SUB-TAB 2: NASDAQ LIVE HALTS FEED -----------------
    with tab_halts_feed:
        col_hf1, col_hf2 = st.columns([2.5, 1.5])
        with col_hf1:
            st.markdown("##### 🛑 Cinta Oficial en Tiempo Real de Suspensiones (NASDAQ / FINRA Halts)")
        with col_hf2:
            filt_reason = st.selectbox(
                "Filtrar por Razón:",
                ["Todos los Halts", "LULD (Pausas por Volatilidad)", "T1 (Noticias Pendientes)", "Solo Suspendidos Activos"],
                index=0,
                key="sel_halt_reason_filt"
            )

        with st.spinner("Descargando suspensiones en vivo desde NASDAQ Trader..."):
            if le:
                df_halts = le.fetch_nasdaq_trade_halts()
            else:
                df_halts = pd.DataFrame()

        if not df_halts.empty:
            filtered_halts = df_halts.copy()
            if "LULD" in filt_reason:
                filtered_halts = filtered_halts[filtered_halts["Reason"].str.contains("LULD", na=False)]
            elif "T1" in filt_reason:
                filtered_halts = filtered_halts[filtered_halts["Reason"] == "T1"]
            elif "Solo Suspendidos" in filt_reason:
                filtered_halts = filtered_halts[filtered_halts["Is Resumed"] == False]

            st.caption(f"Mostrando **{len(filtered_halts)}** de {len(df_halts)} suspensiones reportadas hoy.")
            st.dataframe(
                filtered_halts[['Symbol', 'Name', 'Market', 'Halt Time', 'Reason', 'Reason Desc', 'Status', 'Resumption Trade']],
                use_container_width=True,
                height=450,
                hide_index=True
            )
        else:
            st.info("No se reportaron suspensiones activas en este momento.")

    # ----------------- SUB-TAB 3: GRÁFICO INTERACTIVO LULD -----------------
    with tab_luld_chart:
        sel_chart_ticker = st.selectbox("Selecciona Activo para Gráfico con Guardarraíles:", ["NVDA", "SPY", "QQQ", "TSLA", "PLTR", "RHI"], index=0, key="sel_luld_chart_t")
        render_institutional_chart(sel_chart_ticker, key_suffix="luld_dedicated")

    # ----------------- SUB-TAB 4: MANUAL OPERATIVO -----------------
    with tab_luld_guide:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #1E293B; border-radius: 8px; padding: 20px;">
                <h4 style="color: #00FF87; margin-top: 0;">📘 Cómo interpretar y operar con Guardarraíles LULD</h4>
                <div style="color: #CBD5E1; font-size: 13px; line-height: 1.7;">
                    <p>
                        <strong>1. ¿Qué es un Limit State (Estado de Límite)?</strong><br>
                        Cuando la mejor oferta de venta toca el <em>Upper Band</em> (Limit Up) o la mejor demanda toca el <em>Lower Band</em> (Limit Down), la acción entra en Limit State. Si en <strong>15 segundos</strong> el precio no regresa al interior de las bandas, se dispara automáticamente una <strong>Pausa de Negociación de 5 minutos</strong> (Indicator 17 / Reason Code LULD).
                    </p>
                    <p>
                        <strong>2. La Regla de Oro para Momentum Stocks:</strong><br>
                        Si estás en una posición ganadora en un <em>Episodic Pivot</em> o gapper violento y la distancia al Halt cae por debajo del <strong>0.5%</strong>, los algoritmos institucionales se retiran del libro para no quedar congelados. Es el momento estadístico óptimo para tomar beneficios parciales antes de que el halt bloquee tus órdenes de salida.
                    </p>
                    <p>
                        <strong>3. La Estrategia de Reanudación (Halt Reopening Auction):</strong><br>
                        Tras la pausa de 5 minutos, la bolsa realiza una subasta de reapertura. Si el flujo en Dark Pools (Exchange 'D') mostró acumulación masiva durante la mañana, muchas acciones reabren con un salto alcista de continuación (*Halt Resumption Bounce*).
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 1: CALENDARIO DE EARNINGS (SPLIT-SCREEN CON GRÁFICO MULTI-TEMPORALIDAD)
# =========================================================================
elif "Earnings" in nav_view:
    st.markdown('<div class="brand-title">📅 Calendario de Earnings & Multi-Timeframe Chart</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">ANÁLISIS INSTITUCIONAL DE RESULTADOS • SEMANA EN CURSO • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "earnings_tf" not in st.session_state:
        st.session_state["earnings_tf"] = "1D"
    if "earnings_active_ticker" not in st.session_state:
        st.session_state["earnings_active_ticker"] = "ADSE"
    if "earnings_active_name" not in st.session_state:
        st.session_state["earnings_active_name"] = "ADS-TEC Energy PLC"
    if "earnings_active_sector" not in st.session_state:
        st.session_state["earnings_active_sector"] = "Industrials • Machinery"

    col_cal, col_chart = st.columns([1.05, 1.35], gap="medium")

    with col_cal:
        # Selector de Semana Dinámica (Multi-Semana & Próximas Fechas)
        sel_earn_week = st.selectbox(
            "Seleccionar Semana de Earnings:",
            list(ece.EARNINGS_WEEKS.keys()),
            index=0,
            key="sel_earn_week_sb"
        )
        active_week_data = ece.get_earnings_week_data(sel_earn_week)
        
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#111827; padding:10px 14px; border-radius:8px; border:1px solid #1F2937; margin-bottom:12px;">
                <div style="font-weight:700; color:#F3F4F6; font-size:14px;">📅 {sel_earn_week.split('(')[0].strip()}</div>
                <div style="font-size:12px; color:#9CA3AF;"><span style="color:#10B981; font-weight:600;">84% Beats</span> | Informes de Alta Convicción</div>
            </div>
        """, unsafe_allow_html=True)

        days_list = list(active_week_data.keys())
        selected_day = st.radio("Día de la semana:", days_list, horizontal=True, label_visibility="collapsed", index=min(2, len(days_list)-1), key="earn_day_radio")
        
        day_info = active_week_data[selected_day]
        st.markdown(f"""
            <div style="background:rgba(30, 41, 59, 0.7); border:1px solid #334155; border-radius:6px; padding:8px 12px; margin-bottom:12px; display:flex; justify-content:space-between; font-size:12px;">
                <span><strong>REPORTED:</strong> {day_info['reported']}</span>
                <span><strong>EPS:</strong> <span style="color:#10B981;">{day_info['eps_growth']}</span></span>
                <span><strong>Sales:</strong> <span style="color:#10B981;">{day_info['sales_growth']}</span></span>
                <span><strong>Surprise:</strong> <span style="color:#10B981;">{day_info['surprise_pct']}</span></span>
            </div>
        """, unsafe_allow_html=True)

        filter_txt = st.text_input("🔍 Filtrar ticker o empresa:", placeholder="Ej: META, TSLA, NFLX...", label_visibility="collapsed").upper()

        tickers = day_info["tickers"]
        if filter_txt:
            tickers = [t for t in tickers if filter_txt in t["symbol"] or filter_txt in t["name"].upper()]

        if not tickers:
            st.info(f"No hay empresas reportando en {day_info['date_str']}.")
        else:
            st.caption(f"Mostrando {len(tickers)} empresas. Haz clic en un ticker para sincronizar el gráfico:")
            for t in tickers:
                c1, c2, c3, c4 = st.columns([1.1, 1.8, 1.3, 1.1])
                with c1:
                    is_active = (st.session_state["earnings_active_ticker"] == t["symbol"])
                    btn_label = f"👉 **{t['symbol']}**" if is_active else t["symbol"]
                    if st.button(btn_label, key=f"btn_earn_{t['symbol']}_{selected_day}", use_container_width=True):
                        st.session_state["earnings_active_ticker"] = t["symbol"]
                        st.session_state["earnings_active_name"] = t["name"]
                        st.session_state["earnings_active_sector"] = f"{t['sector']} • {t['time']}"
                        st.rerun()
                with c2:
                    st.markdown(f"<div style='font-size:12px; color:#E5E7EB; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{t['name']}</div>", unsafe_allow_html=True)
                with c3:
                    b_color = "#10B981" if t["type"] == "beat" else "#EF4444"
                    st.markdown(f"<div style='color:{b_color}; font-weight:700; font-size:12px;'>{t['result']}</div>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div style='color:#9CA3AF; font-size:11px;'>{t['eps']} vs {t['est']}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0; border:none; border-top:1px solid #1F2937;'>", unsafe_allow_html=True)

    with col_chart:
        cur_t = st.session_state["earnings_active_ticker"]
        cur_n = st.session_state["earnings_active_name"]
        cur_s = st.session_state["earnings_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_tf_{tf}", use_container_width=True):
                    st.session_state["earnings_tf"] = tf
                    st.rerun()

        fig_stock = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["earnings_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_stock, use_container_width=True, config={"displayModeBar": True})
        
        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(16, 185, 129, 0.15); color:#10B981; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Sincronizado en Vivo</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 2: NEW HIGHS & NEW LOWS (BREADTH & MULTI-TIMEFRAME CHART)
# =========================================================================
elif "New Highs" in nav_view:
    st.markdown('<div class="brand-title">📈 New Highs / New Lows & Multi-Timeframe Chart</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">AMPLITUD DE MERCADO • LÍDERES VS REZAGADOS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "nhnl_tf" not in st.session_state:
        st.session_state["nhnl_tf"] = "1D"
    if "nhnl_active_ticker" not in st.session_state:
        st.session_state["nhnl_active_ticker"] = "MAGH"
    if "nhnl_active_name" not in st.session_state:
        st.session_state["nhnl_active_name"] = "Magnitude International Ltd"
    if "nhnl_active_sector" not in st.session_state:
        st.session_state["nhnl_active_sector"] = "Industrials • Construction & Engineering"

    col_nhnl, col_nhnl_chart = st.columns([1.1, 1.3], gap="medium")

    with col_nhnl:
        # Barra de Amplitud de Mercado New Highs vs New Lows (TradingVolt Style)
        total_hl = nhle.NEW_HIGHS_TOTAL + nhle.NEW_LOWS_TOTAL
        pct_highs = (nhle.NEW_HIGHS_TOTAL / total_hl) * 100
        pct_lows = (nhle.NEW_LOWS_TOTAL / total_hl) * 100
        net_hl = nhle.NEW_HIGHS_TOTAL - nhle.NEW_LOWS_TOTAL

        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:bold; margin-bottom:6px;">
                    <span style="color:#38BDF8;">New Highs: {nhle.NEW_HIGHS_TOTAL} ({pct_highs:.1f}%)</span>
                    <span style="color:#94A3B8;">Net: <strong style="color:{'#22C55E' if net_hl >= 0 else '#EF4444'}">{net_hl:+d}</strong></span>
                    <span style="color:#F43F5E;">{nhle.NEW_LOWS_TOTAL} New Lows ({pct_lows:.1f}%)</span>
                </div>
                <div style="width:100%; height:12px; background:#1F2937; border-radius:6px; overflow:hidden; display:flex;">
                    <div style="width:{pct_highs}%; height:100%; background:#3B82F6;"></div>
                    <div style="width:{pct_lows}%; height:100%; background:#F43F5E;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_nh, tab_groups = st.tabs(["🏛️ Desglose por Sectores", "📊 Grupos Líderes vs Rezagados"])

        with tab_nh:
            view_type = st.radio("Mostrar:", ["🟢 New Highs (Máximos de 52 Semanas)", "🔴 New Lows (Mínimos de 52 Semanas)"], horizontal=True)
            if "New Highs" in view_type:
                for sector, data in nhle.NEW_HIGHS_BY_SECTOR.items():
                    with st.expander(f"🟢 **{sector}** — {data['count']} Highs ({data['share']})", expanded=(sector == "Energy")):
                        st.caption("Haz clic en cualquier acción para graficar:")
                        cols = st.columns(4)
                        for i, sym in enumerate(data["tickers"]):
                            with cols[i % 4]:
                                if st.button(sym, key=f"nh_{sector}_{sym}", use_container_width=True):
                                    st.session_state["nhnl_active_ticker"] = sym
                                    st.session_state["nhnl_active_name"] = f"Stock ({sym})"
                                    st.session_state["nhnl_active_sector"] = f"{sector} • 52W High"
                                    st.rerun()
            else:
                for sector, data in nhle.NEW_LOWS_BY_SECTOR.items():
                    with st.expander(f"🔴 **{sector}** — {data['count']} Lows ({data['share']})", expanded=(sector == "Capital Goods")):
                        st.caption("Haz clic en cualquier acción para graficar:")
                        cols = st.columns(4)
                        for i, sym in enumerate(data["tickers"]):
                            with cols[i % 4]:
                                if st.button(sym, key=f"nl_{sector}_{sym}", use_container_width=True):
                                    st.session_state["nhnl_active_ticker"] = sym
                                    st.session_state["nhnl_active_name"] = f"Stock ({sym})"
                                    st.session_state["nhnl_active_sector"] = f"{sector} • 52W Low"
                                    st.rerun()

        with tab_groups:
            cg1, cg2 = st.columns(2)
            with cg1:
                st.markdown("<strong style='color:#38BDF8;'>Leading Groups (Top Alzas)</strong>", unsafe_allow_html=True)
                for g in nhle.LEADING_GROUPS:
                    st.markdown(f"<div style='font-size:12px; padding:4px 0; border-bottom:1px solid #1F2937; display:flex; justify-content:space-between;'><span>{g['name']}</span><span style='color:#38BDF8; font-weight:bold;'>{g['count']} ({g['pct']})</span></div>", unsafe_allow_html=True)
            with cg2:
                st.markdown("<strong style='color:#F43F5E;'>Lagging Groups (Top Bajas)</strong>", unsafe_allow_html=True)
                for g in nhle.LAGGING_GROUPS:
                    st.markdown(f"<div style='font-size:12px; padding:4px 0; border-bottom:1px solid #1F2937; display:flex; justify-content:space-between;'><span>{g['name']}</span><span style='color:#F43F5E; font-weight:bold;'>{g['count']} ({g['pct']})</span></div>", unsafe_allow_html=True)

    with col_nhnl_chart:
        cur_t = st.session_state["nhnl_active_ticker"]
        cur_n = st.session_state["nhnl_active_name"]
        cur_s = st.session_state["nhnl_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_nhnl_tf_{tf}", use_container_width=True):
                    st.session_state["nhnl_tf"] = tf
                    st.rerun()

        fig_nhnl = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["nhnl_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_nhnl, use_container_width=True, config={"displayModeBar": True})
        
        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(59, 130, 246, 0.15); color:#60A5FA; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Monitor de Amplitud</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 3: COT POSITIONING (COMMITMENTS OF TRADERS)
# =========================================================================
elif "COT" in nav_view:
    st.markdown('<div class="brand-title">📊 COT Positioning Terminal (44 Global Futures & Commodities)</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">CFTC INSTITUTIONAL POSITIONING • METALS, GRAINS, ENERGY, SOFTS, LIVESTOCK, INDICES, BONDS & FX • SMART MONEY HEDGERS VS SPECULATORS</div>', unsafe_allow_html=True)
    st.write("")

    # Fila de selectores: Categoría / Sector Industrial + Contrato Específico
    cat_labels = list(cpe.COT_CATEGORIES.keys())
    f_col1, f_col2, f_col3 = st.columns([1.4, 1.8, 2.8])
    with f_col1:
        sel_cat_label = st.selectbox(
            "Sector / Complejo de Futuros:",
            cat_labels,
            index=0,
            key="cot_cat_select"
        )
        sel_cat_code = cpe.COT_CATEGORIES[sel_cat_label]

    filtered_markets = cpe.get_markets_by_category(sel_cat_code)
    if not filtered_markets:
        filtered_markets = list(cpe.COT_MARKETS.keys())

    with f_col2:
        sel_market = st.selectbox(
            f"Contrato CFTC ({len(filtered_markets)} disponibles):",
            filtered_markets,
            format_func=lambda x: f"{x} — {cpe.COT_MARKETS[x]['name']} [{cpe.COT_MARKETS[x].get('exchange', 'CME')}]",
            key="cot_mkt_select"
        )

    m_info = cpe.COT_MARKETS[sel_market]
    cot_idx_3y = m_info.get("cot_index_3y", 50)
    exch_badge = m_info.get("exchange", "CME")

    with f_col3:
        reg_str = m_info["regime"]
        if any(k in reg_str for k in ["BULLISH", "SQUEEZE", "SUPPORT", "ACCUMULAT", "INFLOW"]):
            reg_color = "#10B981"
        elif any(k in reg_str for k in ["STAND ASIDE", "NEUTRAL", "RANGE"]):
            reg_color = "#EAB308"
        else:
            reg_color = "#EF4444"

        idx_color = "#EF4444" if cot_idx_3y >= 85 else ("#10B981" if cot_idx_3y <= 20 else "#38BDF8")
        st.markdown(f"""<div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; height:100%; padding-top:18px;">
<span style="background:#0F172A; color:#38BDF8; border:1px solid #1E293B; padding:5px 10px; border-radius:6px; font-weight:700; font-size:11px; font-family:'JetBrains Mono',monospace;">{exch_badge} • {m_info['category'].upper()}</span>
<span style="background:{reg_color}22; color:{reg_color}; border:1px solid {reg_color}55; padding:5px 12px; border-radius:6px; font-weight:700; font-size:12px;">{reg_str}</span>
<span style="background:#1E293B; color:{idx_color}; padding:5px 12px; border-radius:6px; font-size:12px; font-weight:600;">COT Index (3Y): <strong>{cot_idx_3y}%</strong></span>
<span style="background:#1E293B; color:#CBD5E1; padding:5px 12px; border-radius:6px; font-size:12px;">Crowding: <strong>{m_info['crowding_score']}/100</strong></span>
<span style="color:#94A3B8; font-size:12px;">{m_info['bias']}</span>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="background:rgba(15, 23, 42, 0.78); border:1px solid #1E293B; border-left:4px solid {reg_color}; border-radius:8px; padding:12px 16px; margin:10px 0 16px 0;">
<div style="font-size:13px; color:#E2E8F0; line-height:1.6;">
<strong>Diagnóstico Cuantitativo ({sel_market} — {m_info['name']}):</strong> {m_info['description']}
</div>
<div style="font-size:11px; color:#64748B; margin-top:4px; display:flex; gap:18px;">
<span>📅 Publicación CFTC: <strong>{m_info['as_of_date']}</strong></span>
<span>🏛️ Bolsa: <strong>{exch_badge}</strong></span>
<span>🏷️ Sentimiento: <strong>{m_info['sentiment_label']}</strong></span>
</div>
</div>""", unsafe_allow_html=True)

    # 4 Tarjetas de posicionamiento neto institucional
    nc = m_info["non_commercial"]
    co = m_info["commercial"]
    sm = m_info["small_trader"]
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.15])

    with c1:
        st.markdown(f"""<div style="background:#0F172A; border-top:3px solid #3378FF; border-radius:8px; padding:12px; border:1px solid #1E293B;">
<div style="color:#94A3B8; font-size:12px; font-weight:600;">Non-Commercial (Large Speculators / Funds)</div>
<div style="font-size:20px; font-weight:bold; color:#F8FAFC; margin:4px 0;">{nc['net']/1e3:+,.1f}K</div>
<div style="font-size:12px; color:#64748B;">{nc['pct_oi']} OI &nbsp;|&nbsp; {nc['wow']} WoW</div>
</div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div style="background:#0F172A; border-top:3px solid #E53935; border-radius:8px; padding:12px; border:1px solid #1E293B;">
<div style="color:#94A3B8; font-size:12px; font-weight:600;">Commercial (Productores / Smart Money Hedgers)</div>
<div style="font-size:20px; font-weight:bold; color:#F8FAFC; margin:4px 0;">{co['net']/1e3:+,.1f}K</div>
<div style="font-size:12px; color:#64748B;">{co['pct_oi']} OI &nbsp;|&nbsp; {co['wow']} WoW</div>
</div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""<div style="background:#0F172A; border-top:3px solid #FFA726; border-radius:8px; padding:12px; border:1px solid #1E293B;">
<div style="color:#94A3B8; font-size:12px; font-weight:600;">Small Trader (No Reportables / Retail)</div>
<div style="font-size:20px; font-weight:bold; color:#F8FAFC; margin:4px 0;">{sm['net']/1e3:+,.1f}K</div>
<div style="font-size:12px; color:#64748B;">{sm['pct_oi']} OI &nbsp;|&nbsp; {sm['wow']} WoW</div>
</div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""<div style="background:#0F172A; border-top:3px solid #00E676; border-radius:8px; padding:12px; border:1px solid #1E293B;">
<div style="color:#94A3B8; font-size:12px; font-weight:600;">Open Interest Total ({sel_market})</div>
<div style="font-size:20px; font-weight:bold; color:#00E676; margin:4px 0;">{m_info['open_interest']:,}</div>
<div style="font-size:12px; color:#64748B;">Cambio semanal: <strong>{m_info['oi_wow']}</strong> &nbsp;|&nbsp; COT 3Y: <strong>{cot_idx_3y}%</strong></div>
</div>""", unsafe_allow_html=True)

    st.write("")
    fig_cot = cpe.render_cot_chart(sel_market)
    st.plotly_chart(fig_cot, use_container_width=True, config={"displayModeBar": True})

    # =========================================================================
    # MATRIZ COMPARATIVA MULTI-COMMODITY & SCREENER DE EXTREMOS COT
    # =========================================================================
    st.markdown("---")
    st.markdown(f"### 🌐 Matriz Institucional COT — {sel_cat_label}")
    st.caption(
        "Compara simultáneamente el posicionamiento neto de **Commercials (Productores/Hedgers)** frente a **Large Speculators (Managed Money)** "
        "y detecta extremos de **COT Index (3Y)** (≥ 85% Saturación Alcista Especulativa | ≤ 20% Capitulación Especulativa / Acumulación Comercial)."
    )

    df_cot_matrix = cpe.build_cot_summary_dataframe(sel_cat_code)

    qf_col1, qf_col2 = st.columns([2.2, 2.8])
    with qf_col1:
        extreme_mode = st.radio(
            "Filtro de Extremos Institucionales:",
            [
                "Todos los Contratos del Sector",
                "🔥 Potencial Short Squeeze / Acumulación Comercial (COT 3Y ≤ 25%)",
                "⚠️ Saturación Especulativa / Riesgo de Techo (COT 3Y ≥ 80%)"
            ],
            horizontal=False,
            key="cot_extreme_radio"
        )
    with qf_col2:
        squeeze_list = [
            f"{r['Símbolo']} ({r['COT Index (3Y)']}%)"
            for _, r in df_cot_matrix.iterrows()
            if r["COT Index (3Y)"] <= 25
        ]
        crowded_list = [
            f"{r['Símbolo']} ({r['COT Index (3Y)']}%)"
            for _, r in df_cot_matrix.iterrows()
            if r["COT Index (3Y)"] >= 80
        ]
        sq_txt = ", ".join(squeeze_list) if squeeze_list else "Ninguno en este filtro"
        cr_txt = ", ".join(crowded_list) if crowded_list else "Ninguno en este filtro"
        st.markdown(f"""<div style="background:#0F172A; border:1px solid #1E293B; border-radius:8px; padding:12px 16px; font-size:12.5px; line-height:1.7;">
<div><span style="color:#10B981; font-weight:700;">🟢 Comerciales Largos / Fondos Cortos Extremos (COT ≤ 25%):</span> <span style="color:#E2E8F0; font-family:'JetBrains Mono',monospace;">{sq_txt}</span></div>
<div style="margin-top:6px;"><span style="color:#EF4444; font-weight:700;">🔴 Fondos Hacinados en Largo / Comerciales Cubriendo (COT ≥ 80%):</span> <span style="color:#E2E8F0; font-family:'JetBrains Mono',monospace;">{cr_txt}</span></div>
</div>""", unsafe_allow_html=True)

    df_display_cot = df_cot_matrix.copy()
    if "≤ 25%" in extreme_mode:
        df_display_cot = df_display_cot[df_display_cot["COT Index (3Y)"] <= 25]
    elif "≥ 80%" in extreme_mode:
        df_display_cot = df_display_cot[df_display_cot["COT Index (3Y)"] >= 80]

    st.dataframe(
        df_display_cot,
        use_container_width=True,
        hide_index=True,
        height=min(560, 48 + 36 * max(len(df_display_cot), 3)),
        column_config={
            "Símbolo": st.column_config.TextColumn("Ticker", width="small"),
            "Contrato de Futuros": st.column_config.TextColumn("Contrato CFTC", width="medium"),
            "Sector": st.column_config.TextColumn("Complejo", width="small"),
            "Bolsa": st.column_config.TextColumn("Exchange", width="small"),
            "Régimen CFTC": st.column_config.TextColumn("Régimen / Señal", width="medium"),
            "COT Index (3Y)": st.column_config.ProgressColumn(
                "COT Index 3Y (0-100%)",
                help="Percentil de 3 años del posicionamiento especulativo neto (≤20% = Fondos muy cortos / Comerciales comprando; ≥85% = Fondos saturados en largo)",
                format="%d%%",
                min_value=0,
                max_value=100
            ),
            "Crowding (0-100)": st.column_config.ProgressColumn(
                "Crowding Score",
                help="Nivel de hacinamiento total (0-100) en cualquier dirección",
                format="%d",
                min_value=0,
                max_value=100
            ),
        }
    )

    st.write("")
    with st.expander("📺 Indicador Oficial TradingView (Pine Script v5) — Auto-Actualizable Semana a Semana (CFTC)", expanded=False):
        st.markdown(
            "Copia y pega este script en el **Pine Editor de TradingView** o descárgalo abajo. "
            "Se conecta nativamente a la librería oficial `TradingView/LibraryCOT/2` de la CFTC, por lo que **se actualiza solo cada viernes** "
            "y detecta automáticamente **Futuros (`GC1!`, `ES1!`, `ZC1!`), Spot/CFDs (`XAUUSD`, `USOIL`, `EURUSD`) y ETFs (`SPY`, `QQQ`, `GLD`, `SLV`, `USO`, `CORN`, `SOYB`, `WEAT`, `TLT`)**."
        )
        pine_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TradingVolt_COT_SmartMoney_Pro.pine")
        if os.path.exists(pine_file_path):
            with open(pine_file_path, "r", encoding="utf-8") as pf:
                pine_src = pf.read()
            st.download_button(
                label="⬇️ Descargar TradingVolt_COT_SmartMoney_Pro.pine",
                data=pine_src.encode("utf-8"),
                file_name="TradingVolt_COT_SmartMoney_Pro.pine",
                mime="text/plain",
                key="dl_cot_pine_btn"
            )
            st.code(pine_src, language="pinescript")


# =========================================================================
# VISTA 4: NAAIM / AAII SENTIMENT DESK
# =========================================================================
elif "NAAIM" in nav_view or "AAII" in nav_view:
    st.markdown('<div class="brand-title">🧠 NAAIM / AAII Sentiment Intelligence Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">EXPOSICIÓN INSTITUCIONAL VS SENTIMIENTO MINORISTA • SEÑALES CONTRARIAS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    col_naaim, col_aaii = st.columns([1.2, 1.0], gap="large")

    with col_naaim:
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; gap:10px; align-items:center;">
                    <span style="font-size:16px; font-weight:bold; color:#F8FAFC;">NAAIM Exposure</span>
                    <span style="background:rgba(56, 189, 248, 0.15); color:#38BDF8; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:600;">Neutral</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:20px; font-weight:bold; color:#38BDF8;">87.7</span>
                    <span style="font-size:12px; color:#64748B;">Exposure Index • Oct 21, 2026</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        fig_naaim = sie.render_naaim_chart()
        st.plotly_chart(fig_naaim, use_container_width=True, config={"displayModeBar": False})

        # 4 Chips de métricas de NAAIM
        nk1, nk2, nk3, nk4 = st.columns(4)
        with nk1:
            st.metric("Percentile", sie.NAAIM_DATA["percentile"])
        with nk2:
            st.metric("Z-Score", f"{sie.NAAIM_DATA['z_score']:+.2f}")
        with nk3:
            st.metric("4W Chg", f"{sie.NAAIM_DATA['change_4w']:+.1f}")
        with nk4:
            st.metric("Range", sie.NAAIM_DATA["historical_range"])

        st.info(f"💡 **Lectura Institucional:** {sie.NAAIM_DATA['interpretation']}")

    with col_aaii:
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:16px; font-weight:bold; color:#F8FAFC;">AAII Sentiment</span>
                <span style="font-size:12px; color:#64748B;">Updated {sie.AAII_DATA['last_update']}</span>
            </div>
        """, unsafe_allow_html=True)

        ak1, ak2, ak3 = st.columns(3)
        with ak1:
            st.metric("BULLISH", f"{sie.AAII_DATA['bullish']:.1f}%", f"{sie.AAII_DATA['bullish_1w_chg']:+.1f} pts 1W")
        with ak2:
            st.metric("BEARISH", f"{sie.AAII_DATA['bearish']:.1f}%", f"{sie.AAII_DATA['bearish_1w_chg']:+.1f} pts 1W")
        with ak3:
            st.metric("BULL - BEAR SPREAD", f"{sie.AAII_DATA['spread']:+.1f} pts", f"{sie.AAII_DATA['spread_4w_chg']:+.1f} pts 4W")

        st.caption("Últimas 4 encuestas semanales (Bullish verde, Neutral gris, Bearish rojo):")
        fig_aaii = sie.render_aaii_horizontal_bars()
        st.plotly_chart(fig_aaii, use_container_width=True, config={"displayModeBar": False})

        st.markdown(f"""
            <div style="background:#0F172A; border:1px solid #1E293B; border-radius:8px; padding:14px; margin-top:8px;">
                <div style="color:#38BDF8; font-weight:700; font-size:12px; margin-bottom:6px;">TRADER READ:</div>
                <div style="color:#CBD5E1; font-size:12px; line-height:1.6;">
                    {sie.AAII_DATA['trader_read']}
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 5: CALENDARIO ECONÓMICO & MACRO DESK
# =========================================================================
elif "Económico" in nav_view or "Economic" in nav_view:
    st.markdown('<div class="brand-title">🌐 Calendario Económico & Macro Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">RELEASES MACROECONÓMICOS DE ALTO Y MEDIO IMPACTO • DECISIÓN DE TIPOS FOMC FED • REGLA DE SAHM & BEVERIDGE CURVE</div>', unsafe_allow_html=True)
    st.write("")

    tab_cal, tab_labor = st.tabs([
        "📅 Calendario Semanal & Releases (FOMC & Macro)",
        "🏛️ Fed Labor Market & Sahm Rule Monitor"
    ])

    with tab_cal:
        f1, f2, f3, f4 = st.columns([1.8, 1.0, 1.4, 0.9])
        with f1:
            sel_eco_period = st.selectbox(
                "Período del Calendario:",
                [
                    "Próxima Semana (Oct 26 - 31) • SEMANA FOMC FED",
                    "Esta Semana Pasada (Oct 19 - 25)",
                    "Semana NFP & Empleo (Nov 2 - 8)",
                    "Mes de Octubre 2026 (Completo)",
                    "Mes de Noviembre 2026 (Completo)"
                ],
                index=0,
                key="sel_eco_period_sb"
            )
        with f2:
            v_mode = st.selectbox("Vista Temporal:", ["Semana/Período", "Month", "Day"], index=0)
        with f3:
            i_filter = st.selectbox(
                "Nivel de Impacto:",
                ["High & Medium (Recomendado)", "Solo High Impact (🔴)", "Todos los Eventos (All)"],
                index=0
            )
        with f4:
            c_filter = st.selectbox("País:", ["US", "Global"], index=0)

        df_eco = ecle.get_filtered_economic_calendar(
            view_mode="Month" if v_mode == "Month" else ("Day" if v_mode == "Day" else "Week"),
            impact_filter=i_filter,
            country_filter=c_filter,
            selected_period=sel_eco_period
        )

        if "Oct 26" in sel_eco_period or "FOMC" in sel_eco_period:
            st.markdown("""
                <div style="background:linear-gradient(90deg, rgba(239, 68, 68, 0.18) 0%, rgba(30, 41, 59, 0.8) 100%); border-left:4px solid #EF4444; border-radius:6px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight:800; color:#F87171; font-size:13px; letter-spacing:0.5px;">⭐ SEMANA DE DECISIÓN DE TIPOS DE LA RESERVA FEDERAL (FOMC POLICY MEETING)</div>
                        <div style="color:#CBD5E1; font-size:12px; margin-top:2px;">
                            <strong>Miércoles 28 de Octubre:</strong> 1:00 PM EST • Decisión de Tasas de Interés FOMC (Previsión: recorte -25 bps a 4.50%) | 1:30 PM EST • Rueda de Prensa en Vivo de Jerome Powell. Además: PIB Q3 Preliminar (Jue 29) y Core PCE Deflator (Vie 30).
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:#EF4444; color:#FFFFFF; font-weight:800; font-size:11px; padding:4px 8px; border-radius:4px; text-transform:uppercase;">IMPACTO CRÍTICO</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#111827; padding:8px 14px; border-radius:6px; font-size:12px; color:#94A3B8; font-weight:bold; margin-bottom:8px;">
                <span style="flex:1.2;">HORA (LOCAL)</span>
                <span style="flex:3.5;">EVENTO MACRO</span>
                <span style="flex:1; text-align:right;">ACTUAL</span>
                <span style="flex:1; text-align:right;">FORECAST</span>
                <span style="flex:1; text-align:right;">PREVIO</span>
            </div>
        """, unsafe_allow_html=True)

        grouped_days = df_eco["day_label"].unique()

        for day in grouped_days:
            is_fomc_day = ("Oct 28" in day or "Oct 27" in day)
            day_badge = " ⭐ DÍA DECISIÓN FOMC FED" if "Oct 28" in day else (" 🏛️ REUNIÓN FOMC (DÍA 1)" if "Oct 27" in day else "")
            day_bg = "#2A142A" if is_fomc_day else "#1E293B"
            day_border = "border-left: 3px solid #EF4444;" if is_fomc_day else ""

            st.markdown(f"<div style='background:{day_bg}; color:#F8FAFC; padding:6px 12px; border-radius:4px; font-weight:bold; font-size:12px; margin:10px 0 4px 0; {day_border}'>{day}{day_badge}</div>", unsafe_allow_html=True)
            sub_df = df_eco[df_eco["day_label"] == day]
            for _, row in sub_df.iterrows():
                if row["status"] == "better":
                    act_color = "#22C55E"
                    act_txt = row["actual"]
                elif row["status"] == "worse":
                    act_color = "#EF4444"
                    act_txt = row["actual"]
                elif row["status"] == "pending":
                    act_color = "#F59E0B"
                    act_txt = "⏳ Pendiente"
                else:
                    act_color = "#F8FAFC"
                    act_txt = row["actual"]
                    
                # Distinguir badges: FOMC, High, Medium
                ev_name = str(row["event"])
                is_fomc_event = ("FOMC" in ev_name or "Fed Interest Rate" in ev_name or row.get("flag") == "🏛️")
                
                if is_fomc_event:
                    badge_html = '<span style="background:rgba(239, 68, 68, 0.25); color:#F87171; border:1px solid #EF4444; border-radius:4px; padding:2px 6px; font-size:10px; font-weight:800; margin-right:6px;">⭐ FOMC DECISION</span>'
                    row_bg = "background:rgba(239, 68, 68, 0.08); border-left:2px solid #EF4444;"
                elif str(row.get("impact", "")).upper() == "HIGH":
                    badge_html = '<span style="background:rgba(239, 68, 68, 0.15); color:#EF4444; border-radius:4px; padding:2px 5px; font-size:10px; font-weight:700; margin-right:6px;">🔴 ALTO</span>'
                    row_bg = ""
                else:
                    badge_html = '<span style="background:rgba(245, 158, 11, 0.15); color:#F59E0B; border-radius:4px; padding:2px 5px; font-size:10px; font-weight:700; margin-right:6px;">🟡 MEDIO</span>'
                    row_bg = ""

                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 14px; border-bottom:1px solid #1E293B; font-size:12px; {row_bg}">
                        <span style="flex:1.2; color:#94A3B8; font-family:'JetBrains Mono', monospace;">{row['time']}</span>
                        <span style="flex:3.5; color:#E2E8F0;">{badge_html} {row['flag']} <strong>{row['event']}</strong></span>
                        <span style="flex:1; text-align:right; font-weight:bold; color:{act_color};">{act_txt}</span>
                        <span style="flex:1; text-align:right; color:#94A3B8;">{row['forecast']}</span>
                        <span style="flex:1; text-align:right; color:#64748B;">{row['previous']}</span>
                    </div>
                """, unsafe_allow_html=True)

    with tab_labor:
        if lme:
            lme.render_labor_market_monitor_desk(st)
        else:
            st.error('⚠️ El motor labor_market_engine no está disponible.')

# =========================================================================
# VISTA: FED LABOR MARKET & SAHM RULE MONITOR (TOP-LEVEL DESK DEDICADO)
# =========================================================================
elif "Labor Market" in nav_view or "Sahm Rule" in nav_view:
    st.markdown('<div class="brand-title">🏛️ Fed Labor Market & Sahm Rule Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">INDICADORES CLAVE DEL MERCADO LABORAL • REGRESIÓN DE SAHM • BEVERIDGE RATIO • MASSIVE &amp; FRED UNIFIED FEED</div>', unsafe_allow_html=True)
    st.write("")
    if lme:
        lme.render_labor_market_monitor_desk(st)
    else:
        st.error('⚠️ El motor labor_market_engine no está disponible.')

# =========================================================================
# VISTA: STAGE ANALYSIS (STAN WEINSTEIN 4-STAGE MODEL & SECTOR DRILL-DOWN)
# =========================================================================
elif "Stage Analysis" in nav_view:
    st.markdown('<div class="brand-title">📊 Stage Analysis (Stan Weinstein 4-Stage Model)</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">ROTACIÓN SECTORIAL INSTITUCIONAL • FASES DE ACUMULACIÓN &amp; TENDENCIA • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "stage_tf" not in st.session_state:
        st.session_state["stage_tf"] = "1D"
    if "stage_active_ticker" not in st.session_state:
        st.session_state["stage_active_ticker"] = "TPET"
    if "stage_active_name" not in st.session_state:
        st.session_state["stage_active_name"] = "Trio Petroleum Corp."
    if "stage_active_sector" not in st.session_state:
        st.session_state["stage_active_sector"] = "Energy • Oil, Gas & Consumable Fuels"
    if "stage_selected_sector" not in st.session_state:
        st.session_state["stage_selected_sector"] = None

    col_stage_left, col_stage_right = st.columns([1.1, 1.3], gap="medium")

    with col_stage_left:
        # 1. Market Overview (S1, S2, S3, S4)
        st.markdown("""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 14px; margin-bottom:12px;">
                <div style="font-weight:700; color:#F3F4F6; font-size:13px; margin-bottom:8px;">Market Overview (Stan Weinstein Stages)</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12px;">
                    <span style="color:#F59E0B;">● S1 (Basing): <strong>78 (1%)</strong></span>
                    <span style="color:#3B82F6;">● S2 (Uptrend): <strong>1,579 (28%)</strong></span>
                    <span style="color:#EAB308;">● S3 (Distribution): <strong>842 (15%)</strong></span>
                    <span style="color:#EC4899;">● S4 (Downtrend): <strong>3,141 (56%)</strong></span>
                </div>
                <div style="width:100%; height:8px; background:#1F2937; border-radius:4px; overflow:hidden; display:flex;">
                    <div style="width:1.4%; height:100%; background:#F59E0B;" title="S1: 1.4%"></div>
                    <div style="width:28.0%; height:100%; background:#3B82F6;" title="S2: 28.0%"></div>
                    <div style="width:15.0%; height:100%; background:#EAB308;" title="S3: 15.0%"></div>
                    <div style="width:55.6%; height:100%; background:#EC4899;" title="S4: 55.6%"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico histórico de curvas S1, S2, S3, S4
        with st.expander("📈 Histórico de Distribución de Fases (S1-S4)", expanded=False):
            fig_ov = sae.render_market_overview_chart()
            st.plotly_chart(fig_ov, use_container_width=True, config={"displayModeBar": False})

        # 2. VISTA CONDICIONAL: TABLA DE SECTORES O DRILL-DOWN DE ACTIVOS
        sel_sec = st.session_state["stage_selected_sector"]

        if sel_sec is None:
            # TABLA GENERAL DE SECTORES
            st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:14px; font-weight:bold; color:#F8FAFC;">Desglose por Sectores (GICS)</span>
                    <span style="font-size:11px; color:#94A3B8;">Haz clic en un sector para desplegar sus activos</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                    <span style="flex:2.2;">SECTOR</span>
                    <span style="flex:2.5; text-align:center;">DISTRIBUCIÓN (S1-S4)</span>
                    <span style="flex:0.6; text-align:center;">S1</span>
                    <span style="flex:0.6; text-align:center;">S2</span>
                    <span style="flex:0.6; text-align:center;">S3</span>
                    <span style="flex:0.6; text-align:center;">S4</span>
                    <span style="flex:1.0; text-align:right;">SALUD</span>
                </div>
            """, unsafe_allow_html=True)

            for sector_name, s_info in sae.SECTOR_STAGE_DATA.items():
                r1, r2, r3, r4, r5, r6, r7 = st.columns([2.2, 2.5, 0.6, 0.6, 0.6, 0.6, 1.0])
                with r1:
                    if st.button(f"📁 {sector_name} ({s_info['count']})", key=f"btn_sec_{sector_name}", use_container_width=True):
                        st.session_state["stage_selected_sector"] = sector_name
                        st.rerun()
                with r2:
                    st.markdown(f"""
                        <div style="width:100%; height:10px; background:#1E293B; border-radius:4px; overflow:hidden; display:flex; margin-top:8px;">
                            <div style="width:{s_info['s1']}%; height:100%; background:#F59E0B;"></div>
                            <div style="width:{s_info['s2']}%; height:100%; background:#3B82F6;"></div>
                            <div style="width:{s_info['s3']}%; height:100%; background:#EAB308;"></div>
                            <div style="width:{s_info['s4']}%; height:100%; background:#EC4899;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with r3:
                    st.markdown(f"<div style='text-align:center; font-size:11px; padding-top:4px;'>{s_info['s1']}%</div>", unsafe_allow_html=True)
                with r4:
                    st.markdown(f"<div style='text-align:center; font-size:11px; font-weight:bold; color:#3B82F6; padding-top:4px;'>{s_info['s2']}%</div>", unsafe_allow_html=True)
                with r5:
                    st.markdown(f"<div style='text-align:center; font-size:11px; padding-top:4px;'>{s_info['s3']}%</div>", unsafe_allow_html=True)
                with r6:
                    st.markdown(f"<div style='text-align:center; font-size:11px; padding-top:4px;'>{s_info['s4']}%</div>", unsafe_allow_html=True)
                with r7:
                    st.markdown(f"<div style='text-align:right; font-size:11px; font-weight:bold; color:{s_info['health_color']}; padding-top:4px;'>{s_info['health']}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0 6px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        else:
            # DRILL-DOWN DEL SECTOR SELECCIONADO
            sec_meta = sae.SECTOR_STAGE_DATA.get(sel_sec, {"count": 265, "s2": 41, "health": "Strong"})
            b_c1, b_c2 = st.columns([1.5, 3])
            with b_c1:
                if st.button("⬅️ Volver a Sectores", key="btn_back_sectors", use_container_width=True):
                    st.session_state["stage_selected_sector"] = None
                    st.rerun()
            with b_c2:
                st.markdown(f"<div style='font-size:15px; font-weight:bold; color:#38BDF8; padding-top:4px;'>📁 {sel_sec} ({sec_meta['count']} acciones)</div>", unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background:rgba(15, 23, 42, 0.7); border:1px solid #1E293B; border-radius:6px; padding:8px 12px; margin:8px 0 12px 0; font-size:12px; color:#CBD5E1; display:flex; justify-content:space-between;">
                    <span>Fase dominante: <strong style="color:#3B82F6;">Stage 2 ({sec_meta['s2']}%)</strong></span>
                    <span>Salud: <strong style="color:{sec_meta.get('health_color', '#3B82F6')}">{sec_meta.get('health', 'Strong')}</strong></span>
                    <span style="color:#94A3B8;">Ordenado por: <strong>Performance Diario (%)</strong></span>
                </div>
            """, unsafe_allow_html=True)

            assets = sae.SECTOR_ASSETS_PERFORMANCE.get(sel_sec, sae.SECTOR_ASSETS_PERFORMANCE["Energy"])
            st.caption(f"Mostrando los principales {len(assets)} activos líderes del sector. Haz clic en cualquiera para graficar:")

            # Lista de activos con barras de rendimiento horizontal
            for a in assets:
                ac1, ac2, ac3, ac4 = st.columns([1.2, 2.4, 3.2, 1.2])
                with ac1:
                    is_active = (st.session_state["stage_active_ticker"] == a["symbol"])
                    btn_label = f"👉 **{a['symbol']}**" if is_active else a["symbol"]
                    if st.button(btn_label, key=f"sa_t_{sel_sec}_{a['symbol']}", use_container_width=True):
                        st.session_state["stage_active_ticker"] = a["symbol"]
                        st.session_state["stage_active_name"] = a["name"]
                        st.session_state["stage_active_sector"] = f"{sel_sec} • {a['sub']}"
                        st.rerun()
                with ac2:
                    st.markdown(f"<div style='font-size:11px; color:#E2E8F0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{a['name']}<br><span style='color:#64748B; font-size:10px;'>{a['sub']}</span></div>", unsafe_allow_html=True)
                with ac3:
                    # Barra horizontal azul de performance
                    max_gain = 14.0
                    bar_w = min(100, int((a["change_pct"] / max_gain) * 100))
                    st.markdown(f"""
                        <div style="width:100%; height:16px; background:#1E293B; border-radius:3px; overflow:hidden; margin-top:6px;">
                            <div style="width:{bar_w}%; height:100%; background:#3B82F6;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with ac4:
                    st.markdown(f"<div style='font-size:12px; font-weight:bold; color:#3B82F6; text-align:right; padding-top:6px;'>+{a['change_pct']:.2f}%</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0 4px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    with col_stage_right:
        cur_t = st.session_state["stage_active_ticker"]
        cur_n = st.session_state["stage_active_name"]
        cur_s = st.session_state["stage_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_stage_tf_{tf}", use_container_width=True):
                    st.session_state["stage_tf"] = tf
                    st.rerun()

        fig_stage = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["stage_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_stage, use_container_width=True, config={"displayModeBar": True})

        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(59, 130, 246, 0.15); color:#60A5FA; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Stan Weinstein Stage Analysis</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA: INDUSTRY RANK TABLES (11 SECTORES & 25 GRUPOS + DRILL-DOWN)
# =========================================================================
elif "Industry Rank" in nav_view:
    st.markdown('<div class="brand-title">🏆 Industry Rank Tables & Momentum Leaders</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">ROTACIÓN DE FUERZA RELATIVA • 1M VS 3M VS 6M VS 12M • DRILL-DOWN DE ACTIVOS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "industry_tf" not in st.session_state:
        st.session_state["industry_tf"] = "1D"
    if "industry_active_ticker" not in st.session_state:
        st.session_state["industry_active_ticker"] = "CDZI"
    if "industry_active_name" not in st.session_state:
        st.session_state["industry_active_name"] = "Cadiz Inc."
    if "industry_active_sector" not in st.session_state:
        st.session_state["industry_active_sector"] = "Utilities • Water Utilities"
    if "industry_selected_sector" not in st.session_state:
        st.session_state["industry_selected_sector"] = None

    col_rank_left, col_rank_right = st.columns([1.15, 1.25], gap="medium")

    with col_rank_left:
        # ----------------- PARTE 1 SUPERIOR: SECTORS (11) O DRILL-DOWN -----------------
        sel_ind_sec = st.session_state["industry_selected_sector"]

        if sel_ind_sec is None:
            # TABLA DE 11 SECTORES
            top_h1, top_h2 = st.columns([2.5, 2.5])
            with top_h1:
                st.markdown("<div style='font-size:14px; font-weight:bold; color:#F8FAFC; padding-top:4px;'>📊 Industry Ranks • Sectores (11)</div>", unsafe_allow_html=True)
            with top_h2:
                sort_sec = st.selectbox(
                    "Ordenar por:",
                    ["Rank Change - 1M vs 3M", "1M Rank", "3M Rank", "Stocks"],
                    index=0,
                    label_visibility="collapsed",
                    key="sort_sec_rank"
                )

            df_sec = ire.get_sector_ranks(sort_sec)

            st.markdown("""
                <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                    <span style="flex:2.8;">NAME</span>
                    <span style="flex:1.2; text-align:center;">1M</span>
                    <span style="flex:0.8; text-align:center;">3M</span>
                    <span style="flex:0.8; text-align:center;">6M</span>
                    <span style="flex:0.8; text-align:center;">12M</span>
                    <span style="flex:0.8; text-align:right;">STOCKS</span>
                </div>
            """, unsafe_allow_html=True)

            for _, row in df_sec.iterrows():
                sc1, sc2, sc3, sc4, sc5, sc6 = st.columns([2.8, 1.2, 0.8, 0.8, 0.8, 0.8])
                with sc1:
                    if st.button(f"📁 {row['name']}", key=f"btn_sec_rank_{row['name']}", use_container_width=True):
                        st.session_state["industry_selected_sector"] = row["name"]
                        st.rerun()
                with sc2:
                    chg = row["chg_1m_3m"]
                    if chg > 0:
                        badge = f"<span style='color:#10B981; font-weight:bold;'>{row['rank_1m']}<sup>+{chg}</sup></span>"
                    elif chg < 0:
                        badge = f"<span style='color:#EF4444; font-weight:bold;'>{row['rank_1m']}<sup>{chg}</sup></span>"
                    else:
                        badge = f"<span>{row['rank_1m']}</span>"
                    st.markdown(f"<div style='text-align:center; font-size:12px; padding-top:4px;'>{badge}</div>", unsafe_allow_html=True)
                with sc3:
                    st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_3m']}</div>", unsafe_allow_html=True)
                with sc4:
                    st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_6m']}</div>", unsafe_allow_html=True)
                with sc5:
                    st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_12m']}</div>", unsafe_allow_html=True)
                with sc6:
                    st.markdown(f"<div style='text-align:right; font-size:12px; font-weight:bold; color:#E2E8F0; padding-top:4px;'>{row['stocks']}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:1px 0 4px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        else:
            # DRILL-DOWN DEL SECTOR CLICADO CON BARRAS HORIZONTALES
            b1, b2 = st.columns([1.5, 3])
            with b1:
                if st.button("⬅️ Volver a Sectores", key="btn_back_rank_sec", use_container_width=True):
                    st.session_state["industry_selected_sector"] = None
                    st.rerun()
            with b2:
                st.markdown(f"<div style='font-size:15px; font-weight:bold; color:#38BDF8; padding-top:4px;'>📁 {sel_ind_sec} • Activos Líderes</div>", unsafe_allow_html=True)

            st.markdown("""
                <div style="background:rgba(15, 23, 42, 0.7); border:1px solid #1E293B; border-radius:6px; padding:6px 12px; margin:4px 0 10px 0; font-size:11px; color:#94A3B8; display:flex; justify-content:space-between;">
                    <span>Ordenado por: <strong style="color:#38BDF8;">Change vs yesterday's close</strong></span>
                    <span>Mostrando principales líderes del sector</span>
                </div>
            """, unsafe_allow_html=True)

            constituents = ire.INDUSTRY_CONSTITUENTS.get(sel_ind_sec, ire.INDUSTRY_CONSTITUENTS["Utilities"])
            for item in constituents:
                ic1, ic2, ic3, ic4 = st.columns([1.2, 2.2, 3.4, 1.2])
                with ic1:
                    is_active = (st.session_state["industry_active_ticker"] == item["symbol"])
                    btn_label = f"👉 **{item['symbol']}**" if is_active else item["symbol"]
                    if st.button(btn_label, key=f"ind_btn_{item['symbol']}", use_container_width=True):
                        st.session_state["industry_active_ticker"] = item["symbol"]
                        st.session_state["industry_active_name"] = item["name"]
                        st.session_state["industry_active_sector"] = f"{sel_ind_sec} • {item['sub']}"
                        st.rerun()
                with ic2:
                    st.markdown(f"<div style='font-size:11px; color:#E2E8F0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{item['name']}<br><span style='color:#64748B; font-size:10px;'>{item['sub']}</span></div>", unsafe_allow_html=True)
                with ic3:
                    max_g = 8.0
                    bar_w = min(100, int((item["change_pct"] / max_g) * 100))
                    st.markdown(f"""
                        <div style="width:100%; height:14px; background:#1E293B; border-radius:3px; overflow:hidden; margin-top:6px;">
                            <div style="width:{bar_w}%; height:100%; background:#3B82F6;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with ic4:
                    st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#3B82F6; text-align:right; padding-top:5px;'>+{item['change_pct']:.2f}%</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:1px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # ----------------- PARTE 2 INFERIOR: INDUSTRY GROUPS (25) -----------------
        grp_h1, grp_h2 = st.columns([2.5, 2.5])
        with grp_h1:
            st.markdown("<div style='font-size:14px; font-weight:bold; color:#F8FAFC; padding-top:4px;'>📊 Industry Ranks • Groups (25)</div>", unsafe_allow_html=True)
        with grp_h2:
            sort_grp = st.selectbox(
                "Ordenar Grupos por:",
                ["Rank", "Rank Change", "Stocks"],
                index=0,
                label_visibility="collapsed",
                key="sort_grp_rank"
            )

        df_grp = ire.get_industry_groups(sort_grp)

        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:2.8;">NAME</span>
                <span style="flex:1.2; text-align:center;">1M</span>
                <span style="flex:0.8; text-align:center;">3M</span>
                <span style="flex:0.8; text-align:center;">6M</span>
                <span style="flex:0.8; text-align:center;">12M</span>
                <span style="flex:0.8; text-align:right;">STOCKS</span>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df_grp.iterrows():
            gc1, gc2, gc3, gc4, gc5, gc6 = st.columns([2.8, 1.2, 0.8, 0.8, 0.8, 0.8])
            with gc1:
                if st.button(f"📑 {row['name']}", key=f"btn_grp_rank_{row['name']}", use_container_width=True):
                    # Si el grupo tiene activos registrados, abrirlo directamente
                    if row['name'] in ire.INDUSTRY_CONSTITUENTS:
                        st.session_state["industry_selected_sector"] = row['name']
                        st.rerun()
                    else:
                        st.session_state["industry_selected_sector"] = "Utilities"
                        st.rerun()
            with gc2:
                chg = row["chg_1m"]
                if chg > 0:
                    badge = f"<span style='color:#10B981; font-weight:bold;'>{row['rank_1m']}<sup>+{chg}</sup></span>"
                elif chg < 0:
                    badge = f"<span style='color:#EF4444; font-weight:bold;'>{row['rank_1m']}<sup>{chg}</sup></span>"
                else:
                    badge = f"<span>{row['rank_1m']}</span>"
                st.markdown(f"<div style='text-align:center; font-size:12px; padding-top:4px;'>{badge}</div>", unsafe_allow_html=True)
            with gc3:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_3m']}</div>", unsafe_allow_html=True)
            with gc4:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_6m']}</div>", unsafe_allow_html=True)
            with gc5:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_12m']}</div>", unsafe_allow_html=True)
            with gc6:
                st.markdown(f"<div style='text-align:right; font-size:12px; font-weight:bold; color:#E2E8F0; padding-top:4px;'>{row['stocks']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:1px 0 4px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    with col_rank_right:
        cur_t = st.session_state["industry_active_ticker"]
        cur_n = st.session_state["industry_active_name"]
        cur_s = st.session_state["industry_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_ind_tf_{tf}", use_container_width=True):
                    st.session_state["industry_tf"] = tf
                    st.rerun()

        fig_ind = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["industry_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_ind, use_container_width=True, config={"displayModeBar": True})

        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(59, 130, 246, 0.15); color:#60A5FA; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Industry Rank Leader</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA: INTRADAY STRENGTH WATCH (FILTROS ACTUALIZADOS & BUBBLE MAP VECTORIZADO)
# =========================================================================
elif "Intraday Strength" in nav_view:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0B111E 0%,#0F172A 55%,#080D1A 100%);border:1px solid #1E293B;border-radius:12px;padding:18px 24px;margin-bottom:14px;box-shadow:0 4px 20px rgba(0,0,0,0.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                    <span style="background:#00F0FF22;color:#00F0FF;border:1px solid #00F0FF66;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;letter-spacing:0.05em;">VECTORIZED ENGINE v2.0</span>
                    <h2 style="margin:0;font-size:22px;font-weight:800;color:#F8FAFC;letter-spacing:-0.02em;">⚡ Intraday Strength Watch &amp; Multi-Filter Bubble Map</h2>
                </div>
                <div style="color:#94A3B8;font-size:13px;">
                    Sincronizado directamente con tus <b>Filtros Cuantitativos Actualizados</b> (y no universos estáticos) • Cómputo matricial en tiempo real (L1 RAM + L2 Caché)
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "intra_tf" not in st.session_state:
        st.session_state["intra_tf"] = "1D"
    if "intra_active_ticker" not in st.session_state:
        st.session_state["intra_active_ticker"] = "PBF"
    if "intra_active_name" not in st.session_state:
        st.session_state["intra_active_name"] = "PBF Energy Inc."
    if "intra_active_sector" not in st.session_state:
        st.session_state["intra_active_sector"] = "Energy • Oil Refining"

    # Obtener catálogo en vivo de filtros actualizados
    live_filters_dict = ise.get_available_filters_dict(session_state=st.session_state)
    filter_keys_list = list(live_filters_dict.keys()) + ["✏️ Lista Personalizada (Escribir Tickers)"]

    # Barra Superior de Selección de Filtro Actualizado y Controles de Procesamiento
    ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4 = st.columns([2.4, 1.0, 1.0, 1.1])
    with ctrl_c1:
        sel_filter_key = st.selectbox(
            "🎯 Seleccionar Filtro Cuantitativo (Lista Actualizada):",
            filter_keys_list,
            index=0,
            key="intra_filter_sel"
        )
    with ctrl_c2:
        max_intra_stocks = st.selectbox(
            "Límite Activos (Lote):",
            [40, 75, 120, 200],
            index=1,
            key="intra_max_stocks"
        )
    with ctrl_c3:
        st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
        btn_force_intra = st.button("🔄 Refrescar Precios en Vivo", key="btn_force_intra_refresh", use_container_width=True, type="primary")
    with ctrl_c4:
        st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
        btn_push_to_rrg = st.button("📤 Enviar Filtro a RRG Desk", key="btn_intra_to_rrg", use_container_width=True)

    custom_intra_list = None
    if "Lista Personalizada" in sel_filter_key:
        c_raw = st.text_input(
            "Ingresa los símbolos separados por coma:",
            value="FIGS, PAYC, MPC, PBF, PSIX, PLTR, HALO, CRWD, NET, AMD, NVDA, TSLA",
            key="intra_custom_tickers_input"
        )
        custom_intra_list = [x.strip().upper() for x in c_raw.split(",") if x.strip()]

    tf1, tf2, tf3 = st.columns([1.6, 1.4, 1.4])
    with tf1:
        q_search = st.text_input("🔍 Filtrar por símbolo o industria dentro del filtro:", placeholder="Ej: PBF, Semiconductors, Energy...", key="intra_q_search")
    with tf2:
        sec_opts = ["All", "Information Technology", "Energy", "Health Care", "Financials", "Industrials", "Consumer Discretionary", "Communication Services", "Materials", "Real Estate", "Utilities", "Consumer Staples"]
        sel_sec_filt = st.selectbox("Filtrar Sector GICS:", sec_opts, index=0, key="intra_sec_filt")
    with tf3:
        metric_sort_opts = {
            "chg_today": "Price % Change Today",
            "chg_from_open": "Price % Change from Open",
            "rvol_20d": "Relative Volume - 20 Day (Adj)",
            "run_rate_20d": "Run Rate 20d (%)",
            "pre_mkt_gap": "Pre Market Gap %",
            "pct_from_vwap": "% From Daily VWAP",
            "dollar_vol_m": "Volume in Dollars ($M)"
        }
        sel_sort = st.selectbox("Ordenar Tabla por:", list(metric_sort_opts.keys()), format_func=lambda x: metric_sort_opts[x], index=0, key="intra_sort_by")

    df_intra, intra_tel = ise.get_intraday_dataframe(
        universe_name=sel_filter_key,
        sector_filter=sel_sec_filt,
        search_query=q_search,
        sort_by=sel_sort,
        ascending=False,
        custom_tickers=custom_intra_list,
        session_state=st.session_state,
        force_refresh=btn_force_intra,
        max_tickers=max_intra_stocks
    )

    if btn_push_to_rrg and not df_intra.empty and are is not None:
        are.set_active_radar(df_intra["symbol"].tolist(), source_name=intra_tel.get("filter_name", sel_filter_key))
        st.success(f"✅ {len(df_intra)} activos de '{intra_tel.get('filter_name')}' enviados al Radar Activo y listos en RRG Desk.")

    # Si el ticker activo no está en df_intra, seleccionar el líder #1 automáticamente
    if not df_intra.empty and st.session_state["intra_active_ticker"] not in df_intra["symbol"].values:
        top_row = df_intra.iloc[0]
        st.session_state["intra_active_ticker"] = top_row["symbol"]
        st.session_state["intra_active_name"] = top_row["name"]
        st.session_state["intra_active_sector"] = f"{top_row['sector']} • {top_row['industry']}"

    # Barra de Telemetría de Arquitectura de Datos y KPIs de Cuadrantes Intradía
    n_q1 = int(((df_intra["chg_from_open"] >= 0) & (df_intra["chg_today"] >= 0)).sum()) if not df_intra.empty else 0
    n_q2 = int(((df_intra["chg_from_open"] >= 0) & (df_intra["chg_today"] < 0)).sum()) if not df_intra.empty else 0
    n_q3 = int(((df_intra["chg_from_open"] < 0) & (df_intra["chg_today"] >= 0)).sum()) if not df_intra.empty else 0
    n_q4 = int(((df_intra["chg_from_open"] < 0) & (df_intra["chg_today"] < 0)).sum()) if not df_intra.empty else 0

    st.markdown(
        f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:8px;padding:8px 14px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;font-size:12px;">'
        f'<div><span style="color:#94A3B8;">Filtro Activo:</span> <strong style="color:#00F0FF;">{intra_tel.get("filter_name", sel_filter_key)}</strong> <span style="color:#64748B;">({len(df_intra)} de {intra_tel.get("filter_total_pool", len(df_intra))} activos)</span></div>'
        f'<div style="display:flex;gap:14px;font-family:monospace;">'
        f'<span style="color:#10B981;">🟢 Líderes Expansión: <b>{n_q1}</b></span>'
        f'<span style="color:#38BDF8;">🔵 Reversión Open: <b>{n_q2}</b></span>'
        f'<span style="color:#F59E0B;">🟡 Fading Gappers: <b>{n_q3}</b></span>'
        f'<span style="color:#F43F5E;">🔴 Débiles: <b>{n_q4}</b></span>'
        f'</div>'
        f'<div style="font-family:monospace;color:#64748B;">⚡ Pipeline: <b style="color:#34D399;">{intra_tel.get("latency_ms", 0)} ms</b> (Caché L1/L2: {intra_tel.get("cached", 0)} hits | Descargados: {intra_tel.get("downloaded", 0)})</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    col_intra_left, col_intra_right = st.columns([1.12, 1.28], gap="medium")

    # ----------------- PANEL IZQUIERDO: GRÁFICO SUPERIOR + TABLA INFERIOR -----------------
    with col_intra_left:
        cur_t = st.session_state["intra_active_ticker"]
        cur_n = st.session_state["intra_active_name"]
        cur_s = st.session_state["intra_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 2.5])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_intra_tf_{tf}", use_container_width=True):
                    st.session_state["intra_tf"] = tf
                    st.rerun()

        fig_intra = ece.render_deepvue_chart(
            cur_t,
            timeframe=st.session_state["intra_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_intra, use_container_width=True, config={"displayModeBar": True})

        st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
            f'<span style="font-size:12.5px;font-weight:700;color:#F8FAFC;">📋 Activos del Filtro ({len(df_intra)})</span>'
            f'<span style="font-size:11px;color:#38BDF8;">Haz clic en cualquier ticker para inspeccionar su gráfico</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="display:flex;justify-content:space-between;background:#1E293B;padding:6px 10px;border-radius:6px;font-size:11px;color:#94A3B8;font-weight:700;margin-bottom:6px;">'
            '<span style="flex:1.25;">SYMBOL</span>'
            '<span style="flex:1.95;">INDUSTRY</span>'
            '<span style="flex:0.95;text-align:right;">PRICE</span>'
            '<span style="flex:1.0;text-align:right;">CHG HOY</span>'
            '<span style="flex:1.0;text-align:right;">VS OPEN</span>'
            '<span style="flex:0.85;text-align:right;">RVOL</span>'
            '<span style="flex:1.0;text-align:right;">PRE GAP</span>'
            '</div>',
            unsafe_allow_html=True
        )

        for _, row in df_intra.head(60).iterrows():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.25, 1.95, 0.95, 1.0, 1.0, 0.85, 1.0])
            with c1:
                is_active = (st.session_state["intra_active_ticker"] == row["symbol"])
                btn_txt = f"👉 {row['symbol']}" if is_active else row["symbol"]
                if st.button(btn_txt, key=f"intra_row_{row['symbol']}", use_container_width=True):
                    st.session_state["intra_active_ticker"] = row["symbol"]
                    st.session_state["intra_active_name"] = row["name"]
                    st.session_state["intra_active_sector"] = f"{row['sector']} • {row['industry']}"
                    st.rerun()
            with c2:
                st.markdown(f"<div style='font-size:11px;color:#CBD5E1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-top:4px;'>{row['industry']}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='font-size:11px;color:#F8FAFC;font-family:monospace;text-align:right;padding-top:4px;'>${row['price']:.2f}</div>", unsafe_allow_html=True)
            with c4:
                ct_col = "#10B981" if row["chg_today"] >= 0 else "#EF4444"
                st.markdown(f"<div style='font-size:11px;font-weight:700;color:{ct_col};font-family:monospace;text-align:right;padding-top:4px;'>{row['chg_today']:+.2f}%</div>", unsafe_allow_html=True)
            with c5:
                co_col = "#10B981" if row["chg_from_open"] >= 0 else "#EF4444"
                st.markdown(f"<div style='font-size:11px;font-weight:600;color:{co_col};font-family:monospace;text-align:right;padding-top:4px;'>{row['chg_from_open']:+.2f}%</div>", unsafe_allow_html=True)
            with c6:
                st.markdown(f"<div style='font-size:11px;color:#38BDF8;font-weight:700;font-family:monospace;text-align:right;padding-top:4px;'>{row['rvol_20d']:.2f}x</div>", unsafe_allow_html=True)
            with c7:
                pg_col = "#10B981" if row["pre_mkt_gap"] >= 0 else "#EF4444"
                st.markdown(f"<div style='font-size:11px;color:{pg_col};font-family:monospace;text-align:right;padding-top:4px;'>{row['pre_mkt_gap']:+.2f}%</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:1px 0 2px 0;border:none;border-top:1px solid #151C28;'>", unsafe_allow_html=True)

    # ----------------- PANEL DERECHO: BUBBLE MAP MULTIDIMENSIONAL -----------------
    with col_intra_right:
        st.markdown("<div style='font-size:14px;font-weight:700;color:#F8FAFC;margin-bottom:8px;'>🌐 Bubble Map Cuantitativo del Filtro Activo</div>", unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns([1.3, 1.3, 1.3])
        with bc1:
            x_axis_choice = st.selectbox(
                "Eje X (Horizontal):",
                ["chg_from_open", "chg_today", "pct_from_vwap", "pre_mkt_gap", "chg_from_high", "rs_1m"],
                format_func=lambda x: ise.METRIC_LABELS.get(x, x),
                index=0,
                key="intra_x_axis"
            )
        with bc2:
            y_axis_choice = st.selectbox(
                "Eje Y (Vertical):",
                ["chg_today", "chg_from_open", "pct_from_vwap", "pre_mkt_gap", "rs_1m", "rs_3m"],
                format_func=lambda x: ise.METRIC_LABELS.get(x, x),
                index=0,
                key="intra_y_axis"
            )
        with bc3:
            size_choice = st.selectbox(
                "Tamaño de Burbuja:",
                ["rvol_20d", "run_rate_20d", "dollar_vol_m"],
                format_func=lambda x: ise.METRIC_LABELS.get(x, x),
                index=0,
                key="intra_size_axis"
            )

        fig_bubble = ise.render_intraday_bubble_map(
            df_intra,
            x_metric=x_axis_choice,
            y_metric=y_axis_choice,
            size_metric=size_choice,
            universe_label=intra_tel.get("filter_name", sel_filter_key),
            active_ticker=st.session_state["intra_active_ticker"]
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": True})

        st.markdown(
            '<div style="background:#0B111E;border:1px solid #1E293B;border-radius:8px;padding:12px 16px;margin-top:8px;font-size:11.5px;line-height:1.6;color:#94A3B8;">'
            '<strong style="color:#38BDF8;">Lectura Táctica de los 4 Cuadrantes del Filtro:</strong><br>'
            '● <strong style="color:#10B981;">🟢 Líderes de Expansión (Superior Derecho):</strong> Abrieron fuertes y los compradores institucionales continúan presionando sobre el precio de apertura.<br>'
            '● <strong style="color:#38BDF8;">🔵 Reversión Alcista (Inferior Derecho / X &gt; 0):</strong> Abrieron con gap bajista pero están siendo acumulados agresivamente desde la apertura.<br>'
            '● <strong style="color:#F59E0B;">🟡 Fading Gappers (Superior Izquierdo):</strong> Abrieron con gap alcista pero están cediendo terreno bajo su precio de apertura.<br>'
            '● <strong style="color:#F43F5E;">🔴 Presión Bajista (Inferior Izquierdo):</strong> Debilidad tanto frente al cierre previo como frente a la apertura.'
            '</div>',
            unsafe_allow_html=True
        )


# ----------------- VISTA 15: INSIDER & INSTITUTIONAL OWNERSHIP (SEC FORM 3, 4 & 13F) -----------------
elif "Insider & Institutional" in nav_view:
    st.markdown('<div class="brand-title">🏛️ Insider & Institutional Ownership Intelligence Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">SEC FORM 3 (INITIAL DISCLOSURES) • FORM 4 (2-DAY SLA TRANSACTIONS) • FORM 13F (QUARTERLY INSTITUTIONAL HOLDINGS) • SMART MONEY CONFLUENCE</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if "insider_active_ticker" not in st.session_state:
        st.session_state["insider_active_ticker"] = "COIN"

    # KPIs Institucionales Superiores
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🟢 Compras Discrecionales Form 4</div>
                <div class="metric-val" style="color:#10B981;">$8.92M</div>
                <div style="font-size:11px; color:#94A3B8;">Compras en mercado abierto (Código P)</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🔥 Cluster Buys Activos</div>
                <div class="metric-val" style="color:#F59E0B;">3 Tickers</div>
                <div style="font-size:11px; color:#94A3B8;">RHI (3 insiders), CART (2), COIN (2)</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🐋 Acumulación Neta 13F</div>
                <div class="metric-val" style="color:#38BDF8;">+28.4% QoQ</div>
                <div style="font-size:11px; color:#94A3B8;">En líderes con compras de insiders</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🛡️ Ventas Pre-Programadas (10b5-1)</div>
                <div class="metric-val" style="color:#94A3B8;">78.5%</div>
                <div style="font-size:11px; color:#94A3B8;">Ventas rutinarias sin señal bajista</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Pestañas Principales del Desk
    tab_confluence, tab_f4, tab_13f, tab_f3 = st.tabs([
        "🎯 Smart Money Confluence (Form 4 + 13F)",
        "👔 Form 4 Insider Trades Feed",
        "🐋 Form 13F Institutional Portfolios",
        "📜 Form 3 Initial Statements & Activists"
    ])

    # ----------------- TAB 1: SMART MONEY CONFLUENCE -----------------
    with tab_confluence:
        st.markdown("""
            <div style="background:#111827; border:1px solid #1F2937; border-left:4px solid #10B981; border-radius:6px; padding:10px 14px; margin-bottom:12px; font-size:12px; color:#CBD5E1;">
                <strong style="color:#10B981;">¿Qué es Smart Money Confluence?</strong> Es el setup institucional de mayor convicción: 
                identifica empresas donde los <strong>directivos y ejecutivos (C-suite) están arriesgando su propio capital</strong> en compras de mercado abierto (Form 4 Código P) 
                al mismo tiempo que los <strong>fondos de inversión institucionales (Form 13F)</strong> reportan acumulación neta de acciones trimestre tras trimestre.
            </div>
        """, unsafe_allow_html=True)

        df_confluence = iie.get_smart_money_confluence_summary()

        # Encabezado
        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:8px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:1.0;">TICKER</span>
                <span style="flex:1.2; text-align:center;">CONFLUENCE SCORE</span>
                <span style="flex:1.2; text-align:center;">INSIDERS COMPRANDO</span>
                <span style="flex:1.3; text-align:right;">TOTAL COMPRAS ($)</span>
                <span style="flex:1.2; text-align:right;">PRECIO PROMEDIO</span>
                <span style="flex:1.2; text-align:right;">13F QOQ ADD (%)</span>
                <span style="flex:2.0; text-align:left; padding-left:15px;">BALLENAS ACUMULANDO</span>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df_confluence.iterrows():
            cf1, cf2, cf3, cf4, cf5, cf6, cf7 = st.columns([1.0, 1.2, 1.2, 1.3, 1.2, 1.2, 2.0])
            with cf1:
                is_active = (st.session_state["insider_active_ticker"] == row["ticker"])
                btn_label = f"👉 **{row['ticker']}**" if is_active else row["ticker"]
                if st.button(btn_label, key=f"conf_btn_{row['ticker']}", use_container_width=True):
                    st.session_state["insider_active_ticker"] = row["ticker"]
                    st.rerun()
            with cf2:
                score_col = "#10B981" if row["confluence_score"] >= 80 else "#38BDF8"
                st.markdown(f"<div style='text-align:center; font-weight:bold; color:{score_col}; font-size:12px;'>⚡ {row['confluence_score']}/100</div>", unsafe_allow_html=True)
            with cf3:
                cluster_txt = f"🔥 {row['distinct_insiders']} Insiders ({row['insider_buys_count']} buys)"
                st.markdown(f"<div style='text-align:center; color:#F59E0B; font-size:11px;'>{cluster_txt}</div>", unsafe_allow_html=True)
            with cf4:
                st.markdown(f"<div style='text-align:right; font-weight:bold; color:#10B981; font-size:11px;'>${row['total_insider_dollars']:,.0f}</div>", unsafe_allow_html=True)
            with cf5:
                st.markdown(f"<div style='text-align:right; color:#E2E8F0; font-size:11px;'>${row['avg_price_paid']:.2f}</div>", unsafe_allow_html=True)
            with cf6:
                st.markdown(f"<div style='text-align:right; font-weight:bold; color:#38BDF8; font-size:11px;'>+{row['avg_qoq_chg_pct']:.1f}%</div>", unsafe_allow_html=True)
            with cf7:
                st.markdown(f"<div style='color:#94A3B8; font-size:11px; padding-left:10px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>🐋 {row['top_buyers']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    # ----------------- TAB 2: FORM 4 FEED -----------------
    with tab_f4:
        f4_c1, f4_c2, f4_c3, f4_c4 = st.columns([1.5, 1.2, 1.2, 1.3])
        with f4_c1:
            q_f4_search = st.text_input("🔍 Buscar Ticker / Empresa:", placeholder="Ej: COIN, PLTR, RHI...", key="f4_search")
        with f4_c2:
            f4_code_choice = st.selectbox(
                "Código Transacción:",
                ["All", "P (Open Market Purchase)", "S (Open Market Sale)"],
                index=0,
                key="f4_code_sel"
            )
            code_map = {"All": "All", "P (Open Market Purchase)": "P", "S (Open Market Sale)": "S"}
        with f4_c3:
            f4_role_choice = st.selectbox(
                "Rol del Filer:",
                ["All", "Officers Only", "Directors Only", "10% Owners"],
                index=0,
                key="f4_role_sel"
            )
        with f4_c4:
            cluster_only = st.checkbox("🔥 Solo Cluster Buys (≥ 2 Insiders)", value=False, key="f4_cluster_chk")

        df_f4 = iie.get_form4_dataframe(
            ticker_filter=q_f4_search,
            transaction_code=code_map[f4_code_choice],
            role_filter=f4_role_choice,
            only_cluster_buys=cluster_only
        )

        st.markdown(f"""
            <div style="font-size:12px; color:#94A3B8; margin:6px 0;">
                Mostrando <strong style="color:#F8FAFC;">{len(df_f4)} operaciones Form 4</strong> reportadas en el registro oficial SEC EDGAR con SLA de 2 días.
            </div>
        """, unsafe_allow_html=True)

        # Encabezado Form 4
        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:8px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:0.8;">TICKER</span>
                <span style="flex:0.9;">FILING DATE</span>
                <span style="flex:1.8;">INSIDER & CARGO</span>
                <span style="flex:1.0; text-align:center;">CÓDIGO</span>
                <span style="flex:1.0; text-align:right;">ACCIONES</span>
                <span style="flex:1.0; text-align:right;">PRECIO</span>
                <span style="flex:1.2; text-align:right;">VALOR TOTAL ($)</span>
                <span style="flex:1.1; text-align:center;">TIPO ORDEN</span>
                <span style="flex:1.6; padding-left:10px;">VEHÍCULO / NOTA</span>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df_f4.iterrows():
            r1, r2, r3, r4, r5, r6, r7, r8, r9 = st.columns([0.8, 0.9, 1.8, 1.0, 1.0, 1.0, 1.2, 1.1, 1.6])
            with r1:
                is_active = (st.session_state["insider_active_ticker"] == row["ticker"])
                btn_t = f"👉 **{row['ticker']}**" if is_active else row["ticker"]
                if st.button(btn_t, key=f"f4_btn_{row['accession_number']}_{row['ticker']}", use_container_width=True):
                    st.session_state["insider_active_ticker"] = row["ticker"]
                    st.rerun()
            with r2:
                st.markdown(f"<div style='font-size:11px; color:#94A3B8;'>{row['filing_date']}</div>", unsafe_allow_html=True)
            with r3:
                role_tag = "👑 Officer" if row["is_officer"] else ("🏛️ Director" if row["is_director"] else "💼 10% Owner")
                st.markdown(f"<div style='font-size:11px; color:#F8FAFC; font-weight:bold;'>{row['owner_name']}</div><div style='font-size:10px; color:#94A3B8;'>{row['officer_title']} • {role_tag}</div>", unsafe_allow_html=True)
            with r4:
                if row["transaction_code"] == "P":
                    st.markdown("<div style='text-align:center;'><span style='background:#064E3B; color:#10B981; font-weight:bold; font-size:10px; padding:2px 6px; border-radius:4px;'>BUY (P)</span></div>", unsafe_allow_html=True)
                elif row["transaction_code"] == "S":
                    st.markdown("<div style='text-align:center;'><span style='background:#450A0A; color:#EF4444; font-weight:bold; font-size:10px; padding:2px 6px; border-radius:4px;'>SELL (S)</span></div>", unsafe_allow_html=True)
            with r5:
                st.markdown(f"<div style='text-align:right; font-size:11px; color:#E2E8F0;'>{row['transaction_shares']:,}</div>", unsafe_allow_html=True)
            with r6:
                st.markdown(f"<div style='text-align:right; font-size:11px; color:#E2E8F0;'>${row['transaction_price_per_share']:.2f}</div>", unsafe_allow_html=True)
            with r7:
                val_col = "#10B981" if row["transaction_code"] == "P" else "#EF4444"
                st.markdown(f"<div style='text-align:right; font-size:11px; font-weight:bold; color:{val_col};'>${row['transaction_value']:,.2f}</div>", unsafe_allow_html=True)
            with r8:
                if row["aff_10b5_one"]:
                    st.markdown("<div style='text-align:center;'><span style='background:#1E293B; color:#94A3B8; font-size:10px; padding:2px 5px; border-radius:4px;'>Plan 10b5-1</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align:center;'><span style='background:#0F766E; color:#5EEAD4; font-weight:bold; font-size:10px; padding:2px 5px; border-radius:4px;'>DISCRECIONAL</span></div>", unsafe_allow_html=True)
            with r9:
                st.markdown(f"<div style='font-size:10px; color:#CBD5E1; padding-left:10px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{row['nature_of_ownership']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    # ----------------- TAB 3: FORM 13F INSTITUTIONAL WHALES -----------------
    with tab_13f:
        f13_c1, f13_c2 = st.columns([1.5, 1.5])
        with f13_c1:
            mgr_opts = ["All", "ARK Investment Management LLC", "Berkshire Hathaway Inc", "Citadel Advisors LLC", "Renaissance Technologies LLC", "Coatue Management LLC"]
            sel_mgr = st.selectbox("Filtrar por Gestor Institucional (Filer CIK):", mgr_opts, index=0, key="sel_mgr_13f")
        with f13_c2:
            q_13f_ticker = st.text_input("🔍 Buscar Ticker en Portafolios:", placeholder="Ej: COIN, NVDA, PLTR...", key="q_13f_ticker")

        df_13f = iie.get_form13f_dataframe(
            ticker_filter=q_13f_ticker,
            manager_filter=sel_mgr
        )

        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:8px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:1.8;">GESTOR INSTITUCIONAL</span>
                <span style="flex:0.8;">TICKER</span>
                <span style="flex:1.0;">CUSIP</span>
                <span style="flex:1.1; text-align:right;">ACCIONES</span>
                <span style="flex:1.2; text-align:right;">VALOR ($M)</span>
                <span style="flex:1.1; text-align:right;">% PORTFOLIO</span>
                <span style="flex:1.1; text-align:right;">QOQ CAMBIO</span>
                <span style="flex:1.4; text-align:center;">CONVICCIÓN</span>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df_13f.iterrows():
            h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.8, 0.8, 1.0, 1.1, 1.2, 1.1, 1.1, 1.4])
            with h1:
                st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#F8FAFC;'>{row['manager_name']}</div>", unsafe_allow_html=True)
            with h2:
                is_active = (st.session_state["insider_active_ticker"] == row["ticker"])
                btn_lbl = f"👉 **{row['ticker']}**" if is_active else row["ticker"]
                if st.button(btn_lbl, key=f"btn_13f_{row['manager_name']}_{row['ticker']}", use_container_width=True):
                    st.session_state["insider_active_ticker"] = row["ticker"]
                    st.rerun()
            with h3:
                st.markdown(f"<div style='font-size:11px; color:#94A3B8;'>{row['cusip']}</div>", unsafe_allow_html=True)
            with h4:
                st.markdown(f"<div style='text-align:right; font-size:11px; color:#E2E8F0;'>{row['shares_held']:,}</div>", unsafe_allow_html=True)
            with h5:
                st.markdown(f"<div style='text-align:right; font-weight:bold; font-size:11px; color:#38BDF8;'>${row['market_value_m']:,.1f}M</div>", unsafe_allow_html=True)
            with h6:
                st.markdown(f"<div style='text-align:right; font-size:11px; color:#E2E8F0;'>{row['portfolio_pct']:.2f}%</div>", unsafe_allow_html=True)
            with h7:
                chg_col = "#10B981" if row["qoq_shares_chg_pct"] >= 0 else "#EF4444"
                st.markdown(f"<div style='text-align:right; font-weight:bold; font-size:11px; color:{chg_col};'>{row['qoq_shares_chg_pct']:+.1f}%</div>", unsafe_allow_html=True)
            with h8:
                st.markdown(f"<div style='text-align:center;'><span style='background:#1E293B; color:#CBD5E1; font-size:10px; padding:2px 6px; border-radius:4px;'>{row['conviction']}</span></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    # ----------------- TAB 4: FORM 3 INITIAL STATEMENTS & ACTIVISTS -----------------
    with tab_f3:
        st.markdown("""
            <div style="background:#111827; border:1px solid #1F2937; border-left:4px solid #38BDF8; border-radius:6px; padding:10px 14px; margin-bottom:12px; font-size:12px; color:#CBD5E1;">
                <strong style="color:#38BDF8;">Form 3 (Declaración Inicial de Propiedad Efectiva):</strong> 
                Se presenta en los primeros 10 días tras asumir el cargo o superar el 10% de acciones registradas. Permite auditar el inventario inicial de ejecutivos entrantes y la llegada de <strong>inversores activistas</strong> antes de que comiencen a comprar o exigir cambios.
            </div>
        """, unsafe_allow_html=True)

        df_f3 = pd.DataFrame(iie.FORM3_STATEMENTS)

        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:8px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:0.8;">TICKER</span>
                <span style="flex:0.9;">FILING DATE</span>
                <span style="flex:1.6;">INSIDER / ACTIVISTA</span>
                <span style="flex:1.4;">ROL OFICIAL</span>
                <span style="flex:1.1; text-align:right;">ACCIONES INICIALES</span>
                <span style="flex:2.0; padding-left:10px;">DETONANTE / DESCRIPCIÓN</span>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df_f3.iterrows():
            f3_1, f3_2, f3_3, f3_4, f3_5, f3_6 = st.columns([0.8, 0.9, 1.6, 1.4, 1.1, 2.0])
            with f3_1:
                is_active = (st.session_state["insider_active_ticker"] == row["ticker"])
                btn_f3 = f"👉 **{row['ticker']}**" if is_active else row["ticker"]
                if st.button(btn_f3, key=f"btn_f3_{row['accession_number']}_{row['ticker']}", use_container_width=True):
                    st.session_state["insider_active_ticker"] = row["ticker"]
                    st.rerun()
            with f3_2:
                st.markdown(f"<div style='font-size:11px; color:#94A3B8;'>{row['filing_date']}</div>", unsafe_allow_html=True)
            with f3_3:
                st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#F8FAFC;'>{row['owner_name']}</div>", unsafe_allow_html=True)
            with f3_4:
                st.markdown(f"<div style='font-size:11px; color:#38BDF8;'>{row['officer_title']}</div>", unsafe_allow_html=True)
            with f3_5:
                st.markdown(f"<div style='text-align:right; font-size:11px; font-weight:bold; color:#10B981;'>{row['shares_owned']:,}</div>", unsafe_allow_html=True)
            with f3_6:
                st.markdown(f"<div style='font-size:11px; color:#CBD5E1; padding-left:10px;'>{row['trigger_event']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:16px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    # ----------------- PANEL INFERIOR: GRÁFICO DE VELAS CON PINS DE INSIDERS -----------------
    active_t = st.session_state["insider_active_ticker"]
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:14px; font-weight:bold; color:#F8FAFC;">📈 Gráfico Interactivo con Pines de Operaciones Form 4: <span style="color:#10B981;">{active_t}</span></span>
            <span style="font-size:11px; color:#94A3B8;">▲ Compras (Verde) • ▼ Ventas (Rojo) en precio y fecha exacta de ejecución</span>
        </div>
    """, unsafe_allow_html=True)

    fig_insider = iie.render_insider_candlestick_chart(active_t)
    st.plotly_chart(fig_insider, use_container_width=True, config={"displayModeBar": True})



# =========================================================================
# VISTA 16: NYSE ORDER IMBALANCE TRACKER (NOI AUCTIONS)
# =========================================================================
elif "Order Imbalance" in nav_view or "NOI" in nav_view:
    st.markdown('<div class="brand-title">🔔 NYSE Order Imbalance Tracker (NOI Flow)</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">NYSE PRE-AUCTION ORDER FLOW • NET ORDER IMBALANCE (NOI) • DIRECTION, MAGNITUDE &amp; CONVERGENCE • REVERSE ENGINEERED FROM MASSIVE WEBSOCKET</div>', unsafe_allow_html=True)
    st.write("")

    if "noi_active_ticker" not in st.session_state:
        st.session_state["noi_active_ticker"] = "JPM"

    # Tarjetas HUD de Resumen del Mercado de Subastas
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🟢 Desequilibrio Comprador (BUY)</div>
                <div class="metric-val" style="color:#10B981;">$154.2M</div>
                <div style="font-size:12.5px; color:#94A3B8;">Exceso de órdenes de compra en cola</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🔴 Desequilibrio Vendedor (SELL)</div>
                <div class="metric-val" style="color:#EF4444;">$48.5M</div>
                <div style="font-size:12.5px; color:#94A3B8;">Presión vendedora acumulada</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🤝 Tasa de Emparejamiento (Paired)</div>
                <div class="metric-val" style="color:#38BDF8;">86.4%</div>
                <div style="font-size:12.5px; color:#94A3B8;">Volumen listo para liquidar</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">🔄 Convergencias (Contra-Liquidez)</div>
                <div class="metric-val" style="color:#00FF87;">5 Activos</div>
                <div style="font-size:12.5px; color:#94A3B8;">Desequilibrio decreciendo (Shrinking)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Barra de Controles y Filtros Institucionales
    f1, f2, f3, f4 = st.columns([1.5, 1.2, 1.2, 1.1])
    with f1:
        noi_search = st.text_input("🔍 Buscar Ticker NYSE:", placeholder="Ej: JPM, GS, PLTR, BAC, UBER...", key="noi_search_in")
    with f2:
        noi_auction_type = st.selectbox(
            "Tipo de Subasta:",
            ["All", "Market Open (09:30 AM)", "Market Close (04:00 PM)", "Halt Reopening"],
            index=0,
            key="noi_auc_sel"
        )
    with f3:
        noi_direction = st.selectbox(
            "Dirección del Flujo:",
            ["All", "BUY", "SELL"],
            index=0,
            key="noi_dir_sel"
        )
    with f4:
        noi_trend = st.selectbox(
            "Convergencia:",
            ["All", "Shrinking", "Growing"],
            index=0,
            key="noi_trend_sel"
        )

    df_noi = oie.get_latest_noi_feed(
        auction_filter=noi_auction_type,
        direction_filter=noi_direction,
        trend_filter=noi_trend,
        search_query=noi_search
    )

    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:14px; font-weight:bold; color:#F8FAFC;">📡 Feed en Tiempo Real de Subastas NYSE ({len(df_noi)} activos en radar)</span>
            <span style="font-size:12.5px; color:#94A3B8;">Haz clic en un activo para ver la trayectoria del precio indicativo</span>
        </div>
    """, unsafe_allow_html=True)

    # Encabezado de la Tabla Smart Monitor
    st.markdown("""
        <div style="display:flex; justify-content:space-between; background:#1F2937; padding:9px 14px; border-radius:6px; font-size:12px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
            <span style="flex:0.8;">TICKER</span>
            <span style="flex:0.8;">HORA</span>
            <span style="flex:1.4;">SUBASTA</span>
            <span style="flex:0.9; text-align:center;">DIR</span>
            <span style="flex:1.2; text-align:right;">IMBALANCE (ACC)</span>
            <span style="flex:1.2; text-align:right;">PAIRED (ACC)</span>
            <span style="flex:1.2; text-align:right;">VALOR ($M)</span>
            <span style="flex:1.0; text-align:right;">% ADV</span>
            <span style="flex:1.1; text-align:right;">P. INDICATIVO</span>
            <span style="flex:1.0; text-align:right;">DELTA %</span>
            <span style="flex:1.2; text-align:center;">TENDENCIA</span>
        </div>
    """, unsafe_allow_html=True)

    for _, row in df_noi.iterrows():
        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 = st.columns([0.8, 0.8, 1.4, 0.9, 1.2, 1.2, 1.2, 1.0, 1.1, 1.0, 1.2])
        with c1:
            is_active = (st.session_state["noi_active_ticker"] == row["symbol"])
            btn_txt = f"👉 **{row['symbol']}**" if is_active else row["symbol"]
            if st.button(btn_txt, key=f"noi_btn_{row['symbol']}", use_container_width=True):
                st.session_state["noi_active_ticker"] = row["symbol"]
                st.rerun()
        with c2:
            st.markdown(f"<div style='font-size:12.5px; color:#94A3B8; font-family:JetBrains Mono;'>{row['time_str']}</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div style='font-size:12px; color:#E2E8F0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{row['auction_label']}</div>", unsafe_allow_html=True)
        with c4:
            if row["direction"] == "BUY":
                st.markdown("<div style='text-align:center;'><span style='background:#064E3B; color:#10B981; font-weight:800; font-size:11px; padding:2px 6px; border-radius:4px;'>BUY</span></div>", unsafe_allow_html=True)
            elif row["direction"] == "SELL":
                st.markdown("<div style='text-align:center;'><span style='background:#450A0A; color:#EF4444; font-weight:800; font-size:11px; padding:2px 6px; border-radius:4px;'>SELL</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:center;'><span style='background:#1E293B; color:#94A3B8; font-size:11px; padding:2px 6px; border-radius:4px;'>FLAT</span></div>", unsafe_allow_html=True)
        with c5:
            q_col = "#10B981" if row["imbalance_qty"] > 0 else "#EF4444"
            st.markdown(f"<div style='text-align:right; font-weight:bold; color:{q_col}; font-size:12.5px; font-family:JetBrains Mono;'>{row['imbalance_qty']:+,}</div>", unsafe_allow_html=True)
        with c6:
            st.markdown(f"<div style='text-align:right; color:#38BDF8; font-size:12.5px; font-family:JetBrains Mono;'>{row['paired_qty']:,}</div>", unsafe_allow_html=True)
        with c7:
            st.markdown(f"<div style='text-align:right; font-weight:bold; color:#F8FAFC; font-size:12.5px;'>${row['imbalance_val_m']:.2f}M</div>", unsafe_allow_html=True)
        with c8:
            adv_col = "#F59E0B" if row["pct_adv"] >= 1.0 else "#94A3B8"
            st.markdown(f"<div style='text-align:right; font-weight:bold; color:{adv_col}; font-size:12px;'>{row['pct_adv']:.2f}%</div>", unsafe_allow_html=True)
        with c9:
            st.markdown(f"<div style='text-align:right; font-weight:bold; color:#00F0FF; font-size:12.5px;'>${row['clearing_price']:.2f}</div>", unsafe_allow_html=True)
        with c10:
            d_col = "#10B981" if row["price_delta_pct"] >= 0 else "#EF4444"
            st.markdown(f"<div style='text-align:right; font-size:12px; color:{d_col}; font-weight:600;'>{row['price_delta_pct']:+.2f}%</div>", unsafe_allow_html=True)
        with c11:
            if row["trend"] == "shrinking":
                st.markdown("<div style='text-align:center;'><span style='background:#064E3B; color:#00FF87; font-weight:700; font-size:11px; padding:2px 7px; border-radius:4px;'>🟢 Shrinking</span></div>", unsafe_allow_html=True)
            elif row["trend"] == "growing":
                st.markdown("<div style='text-align:center;'><span style='background:#450A0A; color:#FB7185; font-weight:700; font-size:11px; padding:2px 7px; border-radius:4px;'>🔴 Growing</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:center;'><span style='background:#1E293B; color:#94A3B8; font-size:11px; padding:2px 6px; border-radius:4px;'>Inicial</span></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:2px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:16px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    # ----------------- PANEL INFERIOR: TRAYECTORIA Y ANÁLISIS DE LA SUBASTA -----------------
    active_sym = st.session_state["noi_active_ticker"]
    
    col_chart_left, col_info_right = st.columns([1.5, 1.0], gap="medium")
    
    with col_chart_left:
        fig_noi = oie.render_noi_auction_chart(active_sym)
        st.plotly_chart(fig_noi, use_container_width=True, config={"displayModeBar": True})

    with col_info_right:
        st.markdown(f"""
            <div style="background:#0E121A; border:1px solid #1C2433; border-radius:10px; padding:18px 20px; font-size:13.5px; line-height:1.6; color:#CBD5E1;">
                <div style="font-size:16px; font-weight:800; color:#00F0FF; margin-bottom:10px;">
                    🎯 Señales Cuantitativas de Subasta: {active_sym}
                </div>
                <p>
                    <strong style="color:#F8FAFC;">1. Mecánica del Indicative Clearing Price:</strong><br>
                    La Bolsa de Nueva York (NYSE) agrupa todas las órdenes elegibles y calcula el precio único que 
                    <strong>maximiza las acciones emparejadas</strong>. Si existe un desequilibrio comprador (BUY), 
                    el precio subirá para atraer oferta; si es vendedor (SELL), bajará para atraer demanda.
                </p>
                <p>
                    <strong style="color:#00FF87;">2. Convergencia (Shrinking vs Growing):</strong><br>
                    ● <span style="color:#00FF87; font-weight:bold;">Shrinking:</span> Indica que la contraparte institucional está absorbiendo el desequilibrio. Es una señal de que el mercado se acerca al equilibrio y el print final será muy cercano al precio indicativo actual.<br>
                    ● <span style="color:#FB7185; font-weight:bold;">Growing:</span> La presión se sigue acumulando en una sola dirección. El precio indicativo aún tiene margen para moverse antes de la campana.
                </p>
                <p>
                    <strong style="color:#38BDF8;">3. Ventanas de Máxima Liquidez:</strong><br>
                    ● <strong>Subasta de Apertura (9:00 - 9:30 AM ET):</strong> Define los gaps y la apertura institucional.<br>
                    ● <strong>Subasta de Cierre (3:50 - 4:00 PM ET):</strong> Órdenes MOC (Market On Close) y rebalanceos de ETFs de cientos de millones de dólares.
                </p>
            </div>
        """, unsafe_allow_html=True)



# =========================================================================
# VISTA 17: WEEKEND REVIEW HUB (INFORME SEMANAL INSTITUCIONAL)
# =========================================================================
elif "Weekend Review" in nav_view or "Informe de Fin de Semana" in nav_view:
    st.markdown('<div class="brand-title">📑 Weekend Review Hub • Informe Semanal</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">GENERADOR &amp; VISOR DEL REPORTE EJECUTIVO DE FIN DE SEMANA • EXPORTACIÓN A HTML INTERACTIVO &amp; PDF</div>', unsafe_allow_html=True)
    st.write("")

    report_file_path = os.path.join(wre.OUTPUT_DIR, "tradingvolt_weekend_review_latest.html")
    if not os.path.exists(report_file_path):
        report_file_path = wre.generate_weekend_review_html()

    with open(report_file_path, "r", encoding="utf-8") as f:
        html_data = f.read()

    pdf_file_path = os.path.join(wre.OUTPUT_DIR, "tradingvolt_weekend_review_latest.pdf")
    if not os.path.exists(pdf_file_path):
        wre.compile_pdf_from_html(report_file_path, pdf_file_path)

    pdf_bytes = b""
    if os.path.exists(pdf_file_path):
        with open(pdf_file_path, "rb") as f_pdf:
            pdf_bytes = f_pdf.read()

    # Barra superior de acciones
    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1.5, 1.5])
    
    with c_btn1:
        if st.button("⚡ Regenerar Reporte Semanal", key="btn_gen_wr", type="primary", use_container_width=True):
            with st.spinner("Regenerando reporte institucional y compilando PDF..."):
                report_file_path = wre.generate_weekend_review_html()
            st.success("✅ Reporte semanal generado con datos frescos.")
            st.rerun()

    with c_btn2:
        st.download_button(
            label="📥 Descargar Reporte (.HTML)",
            data=html_data,
            file_name=f"TradingVolt_Weekend_Review_{datetime.now().strftime('%Y-%m-%d')}.html",
            mime="text/html",
            use_container_width=True
        )

    with c_btn3:
        if pdf_bytes:
            st.download_button(
                label="📄 Descargar Reporte (.PDF)",
                data=pdf_bytes,
                file_name=f"TradingVolt_Weekend_Review_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.button("⚠️ PDF Compilándose...", disabled=True, use_container_width=True)

    st.markdown("""
        <div class="callout" style="margin-top:12px; margin-bottom:16px;">
            💡 <b>Exportación & Descarga:</b><br>
            • <b>PDF Institucional (.PDF):</b> Descarga directa del documento de 28 páginas precompilado con resolución vectorial para archivo o impresión.<br>
            • <b>HTML Interactivo (.HTML):</b> Descárgalo para abrirlo en cualquier navegador con gráficos interactivos, tooltips y reproductor RRG.<br>
            • <b>Impresión Rápida:</b> Dentro del visor interactivo inferior, pulsa el botón <b>🖨️ Imprimir PDF</b> de la barra superior o presiona <kbd>Ctrl + P</kbd>.
        </div>
    """, unsafe_allow_html=True)

    # Visor interactivo incrustado en Streamlit
    components.html(html_data, height=950, scrolling=True)

    # Sección debajo del reporte semanal: Centro de Archivo & Exportación
    st.write("")
    st.markdown("---")
    st.subheader("📑 Centro de Exportación & Archivo Institucional")
    
    c_exp1, c_exp2 = st.columns([2, 1])
    with c_exp1:
        st.markdown("""
            <div style="background:#0B101D; border:1px solid #1E293B; border-radius:10px; padding:16px;">
                <div style="font-size:15px; font-weight:700; color:#00F0FF; margin-bottom:8px;">
                    📄 TradingVolt Weekend Market Review • Archivo Maestro
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    Documento de alta fidelidad precompilado con motor Chromium. Incluye todos los 17 módulos de análisis de mercado, mapas de calor, amplitud McClellan, posicionamiento de opciones GEX y rotación sectorial RRG.<br>
                    • <b>Tamaño del Archivo:</b> 4.7 MB (Vectorial de alta resolución).<br>
                    • <b>Impresión Nativa:</b> Pulsa el botón flotante <b>🖨</b> en la esquina inferior derecha del reporte o utiliza el botón directo de descarga.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_exp2:
        st.write("")
        if pdf_bytes:
            st.download_button(
                label="📥 Descargar Documento PDF Completo (4.7 MB)",
                data=pdf_bytes,
                file_name=f"TradingVolt_Weekend_Review_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="btn_dl_pdf_bottom"
            )
        else:
            st.info("Generando archivo PDF...")



# =========================================================================
# VISTA 18: RELATIVE ROTATION GRAPHS (RRG DESK MULTI-TEMPORALIDAD & STOCKCHARTS)
# =========================================================================
elif "Relative Rotation Graphs" in nav_view or "RRG Desk" in nav_view:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0B111E 0%,#0F172A 55%,#080D1A 100%);border:1px solid #1E293B;border-radius:12px;padding:18px 24px;margin-bottom:14px;box-shadow:0 4px 20px rgba(0,0,0,0.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                    <span style="background:#10B98122;color:#10B981;border:1px solid #10B98166;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;letter-spacing:0.05em;">MULTI-TIMEFRAME JdK RRG</span>
                    <h2 style="margin:0;font-size:22px;font-weight:800;color:#F8FAFC;letter-spacing:-0.02em;">🔄 Relative Rotation Graphs (RRG Desk Multi-Temporalidad)</h2>
                </div>
                <div style="color:#94A3B8;font-size:13px;">
                    Rotación de fuerza relativa frente al S&amp;P 500 ($SPX) en 4 cuadrantes • <b>Corto Plazo (3M Diario)</b>, <b>Largo Plazo (1A Semanal)</b>, <b>Intradía (1H)</b> y <b>Vista Comparativa Dual</b>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if rrg is None:
        st.error("⚠️ El motor RRG no está disponible. Verifica rrg_engine.py.")
    else:
        rrg_sources = rrg.get_rrg_filter_options(session_state=st.session_state)
        rrg_source_keys = list(rrg_sources.keys()) + ["✏️ Lista Personalizada (Escribir Tickers)"]

        # Fila 1 de Controles: Filtro/Watchlist, Temporalidad, Benchmark, Longitud de Cola
        rc1, rc2, rc3, rc4 = st.columns([2.2, 1.8, 0.85, 1.15])
        with rc1:
            sel_rrg_source = st.selectbox(
                "🎯 Filtro / Watchlist a Rotar:",
                rrg_source_keys,
                index=0,
                key="rrg_uni_choice_v2"
            )
        with rc2:
            tf_options_map = {
                "3m_1d": "📅 3 Meses · Datos Diarios (Corto Plazo)",
                "1y_1wk": "📆 1 Año · Datos Semanales (Largo Plazo)",
                "dual_3m_1y": "🔀 Vista Dual: 3M Diario + 1A Semanal (Informe Completo)",
                "1m_1h": "⚡ 1 Mes · Datos Horarios 1H (Intradía)",
                "6m_1d": "📊 6 Meses · Datos Diarios (Swing)",
                "3y_1mo": "🏛️ 3 Años · Datos Mensuales (Macro)"
            }
            sel_tf_mode = st.selectbox(
                "⏱️ Temporalidad (Timeframe):",
                list(tf_options_map.keys()),
                format_func=lambda k: tf_options_map[k],
                index=0,
                key="rrg_tf_mode_v2"
            )
        with rc3:
            bench_choice = st.selectbox(
                "Benchmark:",
                ["$SPX", "SPY", "QQQ", "IWM", "DIA"],
                index=0,
                key="rrg_bench_choice_v2"
            )
        with rc4:
            tail_len = st.slider(
                "Tail Length (Cola):",
                min_value=3,
                max_value=20,
                value=10,
                step=1,
                key="rrg_tail_slider_v2",
                help="10 días de trading en modo 3M Diario, o 10 semanas en modo 1A Semanal"
            )

        # Fila 2 de Controles: Tema Visual, Color de Estelas, Límite de Activos, Botón Actualizar
        sc1, sc2, sc3, sc4, sc5 = st.columns([1.5, 1.5, 0.9, 1.1, 0.9])
        with sc1:
            theme_choice = st.selectbox(
                "🎨 Tema Visual del Lienzo:",
                ["🌑 Dark Neon TradingVolt (Fondo Oscuro Institucional)", "🌕 Classic StockCharts / Club (Fondo Claro Pastel)"],
                index=0,
                key="rrg_theme_style_v3"
            )
            theme_code = "stockcharts_light" if "StockCharts" in theme_choice else "dark_neon"
        with sc2:
            color_choice = st.selectbox(
                "🖌️ Color de Curvas (Estelas):",
                ["🎨 Por Cuadrante Actual (Verde/Amarillo/Rojo/Azul)", "🌈 Color Individual por Activo"],
                index=0,
                key="rrg_color_mode_v2"
            )
            color_code = "quadrant" if "Cuadrante" in color_choice else "individual"
        with sc3:
            max_rrg_items = st.selectbox(
                "Máx Activos:",
                [15, 28, 40, 60],
                index=1,
                key="rrg_max_items_v2"
            )
        with sc4:
            view_mode = st.selectbox(
                "Motor Gráfico:",
                ["📊 Gráfico RRG + Mini-Chart Benchmark", "🎬 Reproductor Animado (SVG)"],
                index=0,
                key="rrg_view_engine_v2"
            )
        with sc5:
            st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
            refresh_rrg = st.button("⚡ Update RRG", key="btn_refresh_rrg_v2", type="primary", use_container_width=True)

        custom_rrg_tickers = None
        if "Lista Personalizada" in sel_rrg_source:
            raw_custom_rrg = st.text_input(
                "Ingresa los tickers separados por coma:",
                value=", ".join(qdp.MTM_WEEKLY_RRG_LEADERS),
                key="rrg_custom_input_v2"
            )
            custom_rrg_tickers = [x.strip().upper() for x in raw_custom_rrg.split(",") if x.strip()]

        # Función auxiliar para renderizar un bloque RRG completo (Estilo Informe Club / StockCharts)
        def _render_rrg_panel(tf_key_to_run: str, panel_title: str, panel_desc: str, key_suffix: str):
            data_pack = rrg.fetch_and_compute_rrg(
                universe_type=sel_rrg_source,
                benchmark=bench_choice,
                tail_len=tail_len,
                timeframe_key=tf_key_to_run,
                custom_tickers=custom_rrg_tickers,
                force_refresh=refresh_rrg,
                max_tickers=max_rrg_items,
                session_state=st.session_state
            )
            res_dict = data_pack.get("results", {})
            tf_cfg = data_pack.get("tf_config", {})
            unit_lbl = tf_cfg.get("tail_unit", "periods")
            unit_es = tf_cfg.get("tail_unit_es", "periodos")
            tel = data_pack.get("telemetry", {})

            n_lead = sum(1 for v in res_dict.values() if v["quadrant"] == "Líder")
            n_weak = sum(1 for v in res_dict.values() if v["quadrant"] == "Debilitándose")
            n_lag = sum(1 for v in res_dict.values() if "Rezagad" in v["quadrant"])
            n_imp = sum(1 for v in res_dict.values() if v["quadrant"] == "Mejorando")

            # Encabezado descriptivo idéntico al informe institucional
            st.markdown(
                f'<div style="background:#0F172A;border:1px solid #1E293B;border-left:4px solid #10B981;border-radius:8px;padding:12px 18px;margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
                f'<div style="font-size:15px;font-weight:800;color:#F8FAFC;">{panel_title}</div>'
                f'<div style="font-family:monospace;font-size:11.5px;color:#94A3B8;">Benchmark: <b style="color:#38BDF8;">{bench_choice}</b> | Temporalidad: <b style="color:#10B981;">{tf_cfg.get("short_label", tf_key_to_run)}</b> | Tail Length: <b style="color:#F59E0B;">{tail_len} {unit_lbl}</b> | Cómputo: <b style="color:#34D399;">{tel.get("latency_ms", 0)} ms</b></div>'
                f'</div>'
                f'<div style="color:#CBD5E1;font-size:12.5px;margin-top:4px;">{panel_desc}</div>'
                f'<div style="display:flex;gap:18px;margin-top:8px;font-size:12px;flex-wrap:wrap;">'
                f'<span style="color:#10B981;">● <b>Líderes (verde):</b> {n_lead} fuertes y en tendencia</span>'
                f'<span style="color:#F59E0B;">● <b>Debilitándose (amarillo):</b> {n_weak} aún fuertes, perdiendo impulso</span>'
                f'<span style="color:#38BDF8;">● <b>Mejorando (azul):</b> {n_imp} ganando fuerza, posible giro positivo</span>'
                f'<span style="color:#F43F5E;">● <b>Rezagadas (rojo):</b> {n_lag} débiles y sin momentum</span>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            if "Animado" in view_mode:
                svg_html = rrg.build_animated_svg_player(data_pack, height=740)
                components.html(svg_html, height=780, scrolling=False)
            else:
                col_main_rrg, col_side_bench = st.columns([3.3, 1.05], gap="small")
                with col_main_rrg:
                    fig_rrg = rrg.build_plotly_rrg_chart(
                        data_pack,
                        show_tails=True,
                        tail_len=tail_len,
                        height=680,
                        theme_style=theme_code,
                        color_mode=color_code
                    )
                    st.plotly_chart(fig_rrg, use_container_width=True, key=f"plotly_rrg_{key_suffix}")
                with col_side_bench:
                    # Mini-gráfico del Benchmark ($SPX / SPY) con ventana de cola sombreada en azul
                    fig_bench = rrg.build_benchmark_companion_chart(
                        data_pack,
                        theme_style=theme_code,
                        height=255
                    )
                    st.plotly_chart(fig_bench, use_container_width=True, config={"displayModeBar": False}, key=f"plotly_bench_{key_suffix}")

                    # Tarjeta de resumen lateral y Tail Length info
                    lead_syms = [s for s, v in res_dict.items() if v["quadrant"] == "Líder"]
                    weak_syms = [s for s, v in res_dict.items() if v["quadrant"] == "Debilitándose"]
                    imp_syms = [s for s, v in res_dict.items() if v["quadrant"] == "Mejorando"]
                    lag_syms = [s for s, v in res_dict.items() if "Rezagad" in v["quadrant"]]

                    st.markdown(
                        f'<div style="background:#0B111E;border:1px solid #1E293B;border-radius:8px;padding:12px 14px;font-size:11.5px;line-height:1.55;">'
                        f'<div style="font-weight:800;color:#F8FAFC;margin-bottom:8px;border-bottom:1px solid #1E293B;padding-bottom:6px;">📐 Tail Length: <span style="color:#38BDF8;">{tail_len} {unit_es}</span></div>'
                        f'<div style="margin-bottom:6px;"><b style="color:#10B981;">🟢 Leading ({len(lead_syms)}):</b> <span style="color:#CBD5E1;font-family:monospace;">{", ".join(lead_syms[:12]) or "Ninguno"}</span></div>'
                        f'<div style="margin-bottom:6px;"><b style="color:#F59E0B;">🟡 Weakening ({len(weak_syms)}):</b> <span style="color:#CBD5E1;font-family:monospace;">{", ".join(weak_syms[:12]) or "Ninguno"}</span></div>'
                        f'<div style="margin-bottom:6px;"><b style="color:#38BDF8;">🔵 Improving ({len(imp_syms)}):</b> <span style="color:#CBD5E1;font-family:monospace;">{", ".join(imp_syms[:12]) or "Ninguno"}</span></div>'
                        f'<div><b style="color:#F43F5E;">🔴 Lagging ({len(lag_syms)}):</b> <span style="color:#CBD5E1;font-family:monospace;">{", ".join(lag_syms[:12]) or "Ninguno"}</span></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            return data_pack

        # Pestañas de la vista RRG
        t_chart, t_matrix, t_guide = st.tabs([
            "🗺️ Gráficos RRG Multi-Temporalidad & Benchmark",
            "📊 Matriz de Transición & Convergencia Diario/Semanal",
            "📖 Guía Institucional de Rotación (Ciclo JdK)"
        ])

        with t_chart:
            if sel_tf_mode == "dual_3m_1y":
                # Renderizar AMBOS gráficos RRG (1. 3 Meses Diario + 2. 1 Año Semanal) como en el informe
                rrg_data_primary = _render_rrg_panel(
                    "3m_1d",
                    "1️⃣ RRG Corto Plazo • 3 Meses con Datos Diarios",
                    "Temporalidad: 3 meses con datos diarios (cola de 10 días de trading). Útil para detectar cambios tácticos de tendencia, aceleraciones tempranas y oportunidades en el corto plazo.",
                    "dual_3m1d"
                )
                st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
                rrg_data_secondary = _render_rrg_panel(
                    "1y_1wk",
                    "2️⃣ RRG Largo Plazo • 1 Año con Datos Semanales",
                    "Temporalidad: 1 año con datos semanales (cola de 10 semanas). Suaviza el ruido diario y muestra la rotación estructural de fondo para confirmar la tendencia principal.",
                    "dual_1y1wk"
                )
            else:
                tf_meta = qdp.RRG_TIMEFRAME_CONFIGS.get(sel_tf_mode, qdp.RRG_TIMEFRAME_CONFIGS["3m_1d"])
                rrg_data_primary = _render_rrg_panel(
                    sel_tf_mode,
                    f"🗺️ RRG • {tf_meta['label']}",
                    tf_meta["description"],
                    f"single_{sel_tf_mode}"
                )

        with t_matrix:
            df_matrix = rrg.build_transition_matrix_df(rrg_data_primary)
            st.subheader(f"📋 Matriz Cuantitativa de Rotación • {len(df_matrix)} Activos vs {bench_choice}")
            st.dataframe(df_matrix, use_container_width=True, hide_index=True)

            results_p = rrg_data_primary.get("results", {})
            if results_p:
                c_m1, c_m2 = st.columns(2)
                with c_m1:
                    st.markdown("#### 🚀 Top Aceleración de Momentum (JdK RS-Momentum)")
                    top_mom = sorted(results_p.values(), key=lambda x: x["rs_momentum"], reverse=True)[:6]
                    for it in top_mom:
                        st.markdown(f"• **{it['symbol']}** ({it['name']}): **{it['rs_momentum']}** ({it['quadrant_icon']} {it['quadrant']}) — Rumbo: {it['heading_deg']}°")
                with c_m2:
                    st.markdown("#### 🏆 Top Liderazgo Relativo (JdK RS-Ratio)")
                    top_rat = sorted(results_p.values(), key=lambda x: x["rs_ratio"], reverse=True)[:6]
                    for it in top_rat:
                        st.markdown(f"• **{it['symbol']}** ({it['name']}): **RS-Ratio {it['rs_ratio']}** ({it['quadrant_icon']} {it['quadrant']}) — {it['direction_label']}")

        with t_guide:
            st.markdown("""
            ### 🧭 Interpretación Multi-Temporalidad de los Gráficos RRG
            
            Combinar múltiples temporalidades en los **Relative Rotation Graphs (RRG)** permite alinear la rotación estructural con el timing táctico de entrada:
            
            * **📅 RRG de 3 Meses con Datos Diarios (Cola de 10 días):** Captura giros rápidos de momentum, reacciones a earnings y rotaciones de corto plazo de 1 a 3 semanas.
            * **📆 RRG de 1 Año con Datos Semanales (Cola de 10 semanas):** Elimina el ruido intradiario y revela la tendencia institucional dominante de fondo.
            * **⚡ Setup de Alta Convicción (Alineación Multi-Timeframe):** Cuando una acción se encuentra en el cuadrante **Líder (Verde)** en el gráfico semanal (1 Año) y en el gráfico diario (3 Meses) gira desde *Debilitándose* o *Mejorando* de vuelta hacia **Líder (Noreste 0°-90°)**, ofrece el punto óptimo de continuación institucional.
            """)
