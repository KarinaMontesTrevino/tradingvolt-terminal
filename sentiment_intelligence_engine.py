"""
TradingVolt • Sentiment Intelligence Desk (NAAIM & AAII)
Dynamic Engine with JSON cache persistence, automated calculation of
historical percentiles, Z-Scores, spreads and weekly updates.
"""

import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentiment_cache.json")


def load_sentiment_cache() -> dict:
    """Carga los datos de sentimiento desde el archivo JSON local."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al leer {CACHE_FILE}: {e}")
    
    # Fallback por defecto si no existe el archivo
    return {
        "naaim": {
            "current_index": 87.7,
            "stance": "Neutral",
            "last_report": "Oct 21, 2026",
            "percentile": "75%",
            "z_score": 0.72,
            "change_4w": -0.4,
            "historical_range": "13 - 108",
            "interpretation": "Exposure is not near a historical extreme, so the contrarian signal is neutral.",
            "history": []
        },
        "aaii": {
            "last_update": "Oct 19, 2026",
            "bullish": 38.7,
            "bullish_1w_chg": -1.8,
            "bearish": 41.6,
            "bearish_1w_chg": 2.8,
            "neutral": 19.7,
            "spread": -2.9,
            "spread_4w_chg": 21.6,
            "surveys": [
                {"date": "Oct 16, 2026", "bullish": 38.7, "neutral": 19.7, "bearish": 41.6, "spread": -2.9},
                {"date": "Oct 9, 2026", "bullish": 40.5, "neutral": 20.8, "bearish": 38.7, "spread": 1.8},
                {"date": "Oct 2, 2026", "bullish": 35.2, "neutral": 17.7, "bearish": 47.1, "spread": -11.9},
                {"date": "Sep 25, 2026", "bullish": 32.8, "neutral": 19.0, "bearish": 48.2, "spread": -15.4}
            ],
            "trader_read": "Sentiment is broadly balanced. Neither optimism nor pessimism is unusually crowded."
        }
    }


def save_sentiment_cache(data: dict) -> bool:
    """Guarda los datos de sentimiento en el archivo JSON local."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al escribir en {CACHE_FILE}: {e}")
        return False


def get_naaim_data() -> dict:
    """Devuelve el diccionario actual de NAAIM."""
    data = load_sentiment_cache()
    return data.get("naaim", {})


def get_aaii_data() -> dict:
    """Devuelve el diccionario actual de AAII."""
    data = load_sentiment_cache()
    return data.get("aaii", {})


# Compatibilidad hacia atrás con variables globales
NAAIM_DATA = get_naaim_data()
AAII_DATA = get_aaii_data()


def update_sentiment_record(naaim_val: float, aaii_bull: float, aaii_neutral: float, 
                             aaii_bear: float, report_date: datetime = None,
                             spy_price: float = None, qqq_price: float = None) -> tuple:
    """
    Registra una nueva lectura semanal de NAAIM y AAII, recalculando
    automáticamente percentiles, Z-Score, spreads y deltas de 1W y 4W.
    """
    if report_date is None:
        report_date = datetime.now()
    
    date_str_short = report_date.strftime("%b %d")
    date_str_full = report_date.strftime("%b %d, %Y")
    date_str_iso = report_date.strftime("%Y-%m-%d")

    data = load_sentiment_cache()
    naaim_dict = data.setdefault("naaim", {})
    aaii_dict = data.setdefault("aaii", {})

    # 1. ACTUALIZAR HISTÓRICO Y MÉTRICAS DE NAAIM
    history = naaim_dict.get("history", [])
    
    # Obtener precios de referencia para el punto en el gráfico
    if spy_price is None and len(history) > 0:
        spy_price = history[-1].get("spy", 580.0)
    elif spy_price is None:
        spy_price = 580.0

    if qqq_price is None and len(history) > 0:
        qqq_price = history[-1].get("qqq", 490.0)
    elif qqq_price is None:
        qqq_price = 490.0

    # Evitar duplicar el mismo día
    if len(history) > 0 and history[-1].get("date") == date_str_iso:
        history[-1] = {"date": date_str_iso, "naaim": float(naaim_val), "spy": float(spy_price), "qqq": float(qqq_price)}
    else:
        history.append({"date": date_str_iso, "naaim": float(naaim_val), "spy": float(spy_price), "qqq": float(qqq_price)})

    # Recalcular métricas cuantitativas sobre el histórico
    naaim_values = [h["naaim"] for h in history]
    mean_val = np.mean(naaim_values) if len(naaim_values) > 0 else 75.0
    std_val = np.std(naaim_values) if len(naaim_values) > 0 else 18.0
    z_score = (naaim_val - mean_val) / std_val if std_val > 0 else 0.0

    # Percentil empírico
    percentile_num = int(np.mean(np.array(naaim_values) <= naaim_val) * 100)
    
    # Cambio 4 semanas
    change_4w = 0.0
    if len(history) >= 5:
        change_4w = round(naaim_val - history[-5]["naaim"], 1)

    # Rango histórico
    min_val = int(np.min(naaim_values)) if len(naaim_values) > 0 else 13
    max_val = int(np.max(naaim_values)) if len(naaim_values) > 0 else 108

    # Stance institucional
    if naaim_val >= 100.0:
        stance = "Extreme Greed (Crowded Long)"
        interpretation = "Active managers are fully leveraged long (>100%). Extreme bullish crowding creates contrarian downside vulnerability."
    elif naaim_val >= 80.0:
        stance = "Bullish / Overweight"
        interpretation = "Active exposure is elevated. Systematic momentum is high, but watch for signs of institutional exhaustion."
    elif naaim_val <= 25.0:
        stance = "Extreme Fear (Capitulation)"
        interpretation = "Active managers have purged equity exposure (<25%). Historical extreme oversold condition sets up high-probability contrarian rallies."
    elif naaim_val <= 50.0:
        stance = "Defensive / Underweight"
        interpretation = "Managers maintain a defensive posture. Risk of cash re-allocation if market breaks upward."
    else:
        stance = "Neutral"
        interpretation = "Exposure is not near a historical extreme, so the contrarian signal is neutral."

    naaim_dict.update({
        "current_index": round(float(naaim_val), 1),
        "stance": stance,
        "last_report": date_str_full,
        "percentile": f"{percentile_num}%",
        "z_score": round(float(z_score), 2),
        "change_4w": float(change_4w),
        "historical_range": f"{min_val} - {max_val}",
        "interpretation": interpretation,
        "history": history
    })

    # 2. ACTUALIZAR MÉTRICAS Y ENCUESTAS DE AAII
    surveys = aaii_dict.get("surveys", [])
    new_spread = round(float(aaii_bull - aaii_bear), 1)

    prev_bull = aaii_dict.get("bullish", aaii_bull)
    prev_bear = aaii_dict.get("bearish", aaii_bear)
    bull_1w_chg = round(float(aaii_bull - prev_bull), 1)
    bear_1w_chg = round(float(aaii_bear - prev_bear), 1)

    # Insertar nueva encuesta
    new_entry = {
        "date": date_str_short,
        "bullish": round(float(aaii_bull), 1),
        "neutral": round(float(aaii_neutral), 1),
        "bearish": round(float(aaii_bear), 1),
        "spread": new_spread
    }

    # Evitar duplicados por fecha
    if len(surveys) > 0 and surveys[0].get("date") == date_str_short:
        surveys[0] = new_entry
    else:
        surveys.insert(0, new_entry)

    # Mantener las últimas 4 encuestas para el gráfico
    surveys = surveys[:4]

    # Spread 4W change
    spread_4w_chg = 0.0
    if len(surveys) >= 4:
        spread_4w_chg = round(new_spread - surveys[-1]["spread"], 1)

    # Trader Read dinámico
    if new_spread > 25.0:
        trader_read = (
            f"Retail optimism is heavily crowded (Bull-Bear spread at {new_spread:+.1f} pts). "
            "High complacency levels suggest caution against chasing extended breakouts. "
            "Wait for pullbacks or tight consolidation pivots."
        )
    elif new_spread < -20.0:
        trader_read = (
            f"Retail pessimism is deep (Bull-Bear spread at {new_spread:+.1f} pts). "
            "Historically, extreme retail despair often forms the foundation for durable market bottoms. "
            "Look for institutional accumulation and leading CANSLIM breakouts."
        )
    else:
        trader_read = (
            f"Sentiment is broadly balanced (Spread {new_spread:+.1f} pts). Neither optimism nor pessimism is unusually crowded. "
            "Week-over-week direction may be more useful than the absolute reading. "
            "Use AAII as context, not a standalone signal. Confirm extremes with price, breadth, and your risk process."
        )

    aaii_dict.update({
        "last_update": date_str_full,
        "bullish": round(float(aaii_bull), 1),
        "bullish_1w_chg": bull_1w_chg,
        "bearish": round(float(aaii_bear), 1),
        "bearish_1w_chg": bear_1w_chg,
        "neutral": round(float(aaii_neutral), 1),
        "spread": new_spread,
        "spread_4w_chg": spread_4w_chg,
        "surveys": surveys,
        "trader_read": trader_read
    })

    # Guardar en JSON
    success = save_sentiment_cache(data)
    
    # Actualizar variables globales en memoria
    global NAAIM_DATA, AAII_DATA
    NAAIM_DATA = naaim_dict
    AAII_DATA = aaii_dict

    return success, f"Reporte semanal ({date_str_full}) guardado con éxito. NAAIM: {naaim_val}% | AAII Spread: {new_spread:+.1f}%"


def fetch_aaii_from_nasdaq(api_key: str) -> tuple:
    """
    Descarga el último informe oficial de AAII Sentiment Survey desde
    Nasdaq Data Link usando la API key del usuario.
    """
    if not api_key or not api_key.strip():
        return False, "La API Key de Nasdaq Data Link está vacía."
    
    try:
        import quandl
        quandl.ApiConfig.api_key = api_key.strip()
        
        df = None
        last_err = ""
        for code in ["AAII/AAII_SENTIMENT", "AAII/SENTIMENT"]:
            try:
                df = quandl.get(code, rows=1)
                if df is not None and not df.empty:
                    break
            except Exception as e:
                last_err = str(e)
                continue
        
        if df is None or df.empty:
            if "403" in last_err:
                return False, (
                    "Error 403 (Incapsula WAF / Verificación): Nasdaq Data Link activó su firewall antibot para esta IP o tu cuenta aún no valida el email. "
                    "Te recomendamos ingresar los 3 números semanales en el formulario rápido de arriba (tarda 10 segundos cada jueves) sin depender del bloqueo de Nasdaq."
                )
            return False, f"Nasdaq Data Link no devolvió datos: {last_err}"
        
        latest_row = df.iloc[-1]
        report_date = df.index[-1]
        
        # Nasdaq entrega los valores en porcentaje (ej 38.7 o 0.387 según la versión)
        bull = float(latest_row.get("Bullish", 0.0))
        neutral = float(latest_row.get("Neutral", 0.0))
        bear = float(latest_row.get("Bearish", 0.0))
        
        if bull < 1.0 and bull > 0: bull *= 100.0
        if neutral < 1.0 and neutral > 0: neutral *= 100.0
        if bear < 1.0 and bear > 0: bear *= 100.0

        # Mantener el valor de NAAIM actual
        naaim_curr = get_naaim_data()
        naaim_val = naaim_curr.get("current_index", 87.7)

        ok, msg = update_sentiment_record(
            naaim_val=naaim_val,
            aaii_bull=bull,
            aaii_neutral=neutral,
            aaii_bear=bear,
            report_date=report_date
        )

        return True, f"¡Éxito! Encuesta AAII descargada de Nasdaq Data Link: Bullish {bull:.1f}% | Bearish {bear:.1f}% | Neutral {neutral:.1f}% (Fecha: {report_date.strftime('%b %d, %Y')})"
    except Exception as e:
        return False, f"Error al consultar Nasdaq Data Link: {e}"


def generate_naaim_timeseries(num_weeks: int = 156) -> pd.DataFrame:
    """Obtiene la serie de tiempo de NAAIM para graficar."""
    naaim_dict = get_naaim_data()
    history = naaim_dict.get("history", [])

    if len(history) >= 20:
        df = pd.DataFrame(history)
        df['Date'] = pd.to_datetime(df['date'])
        df = df.set_index('Date')
        df = df.rename(columns={'naaim': 'NAAIM', 'spy': 'SPY', 'qqq': 'QQQ'})
        return df[['NAAIM', 'SPY', 'QQQ']].sort_index()

    # Si no hay suficiente historial, generamos la base sintética normalizada
    np.random.seed(101)
    end_date = datetime.now()
    dates = [end_date - timedelta(weeks=i) for i in range(num_weeks)]
    dates.reverse()

    t = np.linspace(0, 10, num_weeks)
    trend = 380 + 20 * t + 15 * np.sin(t)
    spy_prices = trend + np.random.normal(0, 4, num_weeks)
    qqq_prices = trend * 1.15 + np.random.normal(0, 6, num_weeks)

    curr_idx = naaim_dict.get("current_index", 87.7)
    naaim_base = 75 + 25 * np.sin(t * 1.5) + np.random.normal(0, 8, num_weeks)
    naaim = np.clip(naaim_base, 13.0, 108.0)
    naaim[-1] = curr_idx

    df = pd.DataFrame({
        "Date": dates,
        "NAAIM": naaim,
        "SPY": spy_prices,
        "QQQ": qqq_prices
    }).set_index("Date")

    return df


def render_naaim_chart() -> go.Figure:
    """Genera el gráfico interactivo de la línea de exposición NAAIM con SPY y QQQ."""
    df = generate_naaim_timeseries()

    fig = go.Figure()

    # 1. NAAIM Exposure Line (Azul cielo)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['NAAIM'],
        name="NAAIM Exposure",
        line=dict(color="#38BDF8", width=2.0),
        yaxis="y1"
    ))

    # 2. SPY Benchmark (Naranja)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SPY'],
        name="SPY (S&P 500)",
        line=dict(color="#FB923C", width=1.4),
        yaxis="y2"
    ))

    # 3. QQQ Benchmark (Índigo punteado)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['QQQ'],
        name="QQQ (Nasdaq 100)",
        line=dict(color="#818CF8", width=1.2, dash="dot"),
        yaxis="y2"
    ))

    # Zonas de referencia
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
    """Genera las barras horizontales de las últimas encuestas AAII."""
    aaii_dict = get_aaii_data()
    surveys = aaii_dict.get("surveys", [])

    if not surveys:
        surveys = [
            {"date": "Semana Actual", "bullish": 38.7, "neutral": 19.7, "bearish": 41.6, "spread": -2.9}
        ]

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

    # 2. Neutral (Gris)
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

    # Anotaciones de spread
    for d, sp in zip(dates, spreads):
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
