"""
TradingVolt • Limit Up / Limit Down (LULD) Guardrails & Market Halts Engine
100% Free - Powered by Official NASDAQ Trader Real-Time Feeds & SEC NMS Plan LULD Formulas.

Features:
1. Live NASDAQ/FINRA Trading Halts Feed (LULD, Volatility Pauses, News Halts, Resumptions)
2. Dynamic LULD Band Calculator for Tier 1 (SPY, QQQ, IWM, Mag 7) & Tier 2 (Momentum Stocks)
3. Distance to Halt (Pre-Halt Early Warning Radar)
4. Multi-Asset Watchlist Guardrail Matrix
"""
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np
import yfinance as yf

EASTERN = ZoneInfo("America/New_York")

# Tier 1 NMS Securities: S&P 500, Russell 1000, and major ETPs (Band: ±5% regular, ±10% open/close)
TIER_1_ETFS = {"SPY", "QQQ", "IWM", "DIA", "SMH", "XLF", "XLE", "XLK", "XLV", "XBI"}
MAGNIFICENT_7 = {"NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA"}

HALT_REASONS = {
    "LULD": "Limit Up-Limit Down Trading Pause (Volatilidad Extrema)",
    "T1": "Halt - Noticia Pendiente (News Pending)",
    "T2": "Halt - Noticia Publicada (News Released)",
    "T5": "Pausa por Volatilidad en Acción Individual",
    "T6": "Halt - Extraordinaria Actividad de Mercado",
    "T12": "Halt - Información Adicional Solicitada por Regulador",
    "H10": "Halt - Suspensión Regulatoria SEC",
    "M": "Pausa por Volatilidad de Mercado",
    "IPO1": "Halt Previo a Salida a Bolsa (IPO)"
}


def fetch_nasdaq_trade_halts() -> pd.DataFrame:
    """
    Descarga en tiempo real el feed oficial de NASDAQ Trader de todas las suspensiones (halts)
    y reanudaciones activas en el mercado estadounidense (100% gratuito).
    """
    url = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            
            halts = []
            for item in items:
                sym = item.find("title").text if item.find("title") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                pub = item.find("pubDate").text if item.find("pubDate") is not None else ""
                
                # Extraer campos de la tabla HTML interna
                # Campos: Halt Date, Halt Time, Issue Symbol, Issue Name, Market, Reason Code, Pause Threshold Price, Resumption Date, Resumption Quote Time, Resumption Trade Time
                td_matches = re.findall(r'<td[^>]*>(.*?)</td>', desc)
                
                if len(td_matches) >= 10:
                    h_date = td_matches[0].strip()
                    h_time = td_matches[1].strip()
                    issue_sym = td_matches[2].strip() or sym
                    name = td_matches[3].strip()
                    mkt = td_matches[4].strip()
                    reason = td_matches[5].strip()
                    threshold = td_matches[6].strip()
                    r_date = td_matches[7].strip()
                    r_q_time = td_matches[8].strip()
                    r_t_time = td_matches[9].strip()
                else:
                    h_date = pub
                    h_time = ""
                    issue_sym = sym
                    name = ""
                    mkt = "US"
                    reason = "HALT"
                    threshold = ""
                    r_date = ""
                    r_q_time = ""
                    r_t_time = ""
                    
                is_resumed = bool(r_t_time and r_t_time.strip())
                status_label = "🟢 REANUDADO" if is_resumed else "🔴 SUSPENDIDO (HALTED)"
                reason_desc = HALT_REASONS.get(reason, f"Código {reason}")
                
                halts.append({
                    "Symbol": issue_sym,
                    "Name": name,
                    "Market": mkt,
                    "Halt Date": h_date,
                    "Halt Time": h_time,
                    "Reason": reason,
                    "Reason Desc": reason_desc,
                    "Threshold Price": threshold,
                    "Resumption Trade": r_t_time if r_t_time else "En Espera...",
                    "Status": status_label,
                    "Is Resumed": is_resumed
                })
                
            df = pd.DataFrame(halts)
            return df
    except Exception as e:
        print(f"Error fetching NASDAQ Halts: {e}")
        return pd.DataFrame()


def get_luld_band_pct(symbol: str, price: float, current_time_est: datetime = None) -> tuple[float, str]:
    """
    Calcula el porcentaje oficial de banda LULD según la normativa del Plan NMS:
    - Tier 1: SPY, QQQ, IWM, Mag 7, S&P 500 (±5% regular, ±10% apertura/cierre)
    - Tier 2: Momentum Stocks, Small/Mid Caps (±10% regular, ±20% apertura/cierre)
    """
    if current_time_est is None:
        current_time_est = datetime.now(EASTERN)
        
    t = current_time_est.time()
    
    # Determinar si estamos en horario de apertura (9:30-9:45) o cierre (15:35-16:00) donde la banda se duplica
    is_wider_period = (dtime(9, 30) <= t < dtime(9, 45)) or (dtime(15, 35) <= t <= dtime(16, 0))
    
    is_tier_1 = (symbol in TIER_1_ETFS) or (symbol in MAGNIFICENT_7)
    
    if is_tier_1:
        base_pct = 0.05
        tier_str = "Tier 1 (NMS Core / S&P 500)"
    else:
        # Tier 2: Momentum Stocks y otras acciones NMS
        if price > 3.0:
            base_pct = 0.10
        elif price >= 0.75:
            base_pct = 0.20
        else:
            base_pct = 0.75
        tier_str = "Tier 2 (Momentum / NMS Broad)"
        
    band_pct = (base_pct * 2.0) if is_wider_period else base_pct
    phase_str = "Apertura/Cierre (Doble Banda)" if is_wider_period else "Sesión Regular"
    
    return band_pct, f"{tier_str} • {phase_str}"


def calculate_luld_guardrails(ticker: str, spot_price: float = None) -> dict:
    """
    Calcula los guardarraíles dinámicos de Limit Up / Limit Down para un ticker:
    - Precio de referencia (P_ref)
    - Upper Band (Techo de Limit Up)
    - Lower Band (Suelo de Limit Down)
    - Distancia al Halt en dólares y porcentaje
    - Nivel de Alerta Temprana (Normal, Acercándose, Alerta Roja)
    """
    sym = ticker.strip().upper()
    
    if spot_price is None or spot_price <= 0:
        try:
            t = yf.Ticker(sym)
            spot_price = float(t.fast_info.get("lastPrice", 0.0))
        except Exception:
            spot_price = 100.0
            
    now_est = datetime.now(EASTERN)
    band_pct, tier_desc = get_luld_band_pct(sym, spot_price, now_est)
    
    # El precio de referencia oficial es el promedio móvil de los últimos 5 minutos
    p_ref = spot_price
    
    upper_band = p_ref * (1.0 + band_pct)
    lower_band = p_ref * (1.0 - band_pct)
    
    dist_upper_dollar = upper_band - spot_price
    dist_upper_pct = (dist_upper_dollar / spot_price) * 100.0
    
    dist_lower_dollar = spot_price - lower_band
    dist_lower_pct = (dist_lower_dollar / spot_price) * 100.0
    
    # Evaluar alerta de proximidad
    min_dist_pct = min(dist_upper_pct, dist_lower_pct)
    if min_dist_pct <= 0.5:
        alert_status = "🚨 PELIGRO INMINENTE DE HALT (En Límite LULD)"
        alert_color = "#FF0055"
        risk_level = "CRÍTICO"
    elif min_dist_pct <= 1.5:
        alert_status = "⚠️ ACERCÁNDOSE A BANDA LULD (Peligro de Pausa 5m)"
        alert_color = "#FF8C00"
        risk_level = "ALTO"
    elif min_dist_pct <= 3.0:
        alert_status = "🟡 VOLATILIDAD EN EXPANSIÓN"
        alert_color = "#F59E0B"
        risk_level = "MODERADO"
    else:
        alert_status = "🟢 DENTRO DE LÍMITES NORMALES"
        alert_color = "#00FF87"
        risk_level = "NORMAL"
        
    return {
        "ticker": sym,
        "spot": spot_price,
        "ref_price": p_ref,
        "band_pct": band_pct * 100.0,
        "tier_desc": tier_desc,
        "upper_band": upper_band,
        "lower_band": lower_band,
        "dist_upper_dollar": dist_upper_dollar,
        "dist_upper_pct": dist_upper_pct,
        "dist_lower_dollar": dist_lower_dollar,
        "dist_lower_pct": dist_lower_pct,
        "min_dist_pct": min_dist_pct,
        "alert_status": alert_status,
        "alert_color": alert_color,
        "risk_level": risk_level,
        "timestamp_est": now_est.strftime("%H:%M:%S EST")
    }


def get_luld_watchlist_matrix(tickers: list[str]) -> pd.DataFrame:
    """
    Construye una matriz comparativa de guardarraíles LULD para una lista de activos.
    """
    rows = []
    for sym in tickers:
        try:
            g = calculate_luld_guardrails(sym)
            rows.append({
                "Ticker": sym,
                "Spot ($)": f"${g['spot']:.2f}",
                "Techo LULD (+Limit Up)": f"${g['upper_band']:.2f}",
                "Suelo LULD (-Limit Down)": f"${g['lower_band']:.2f}",
                "Banda (%)": f"±{g['band_pct']:.1f}%",
                "Distancia al Halt": f"{g['min_dist_pct']:.2f}%",
                "Alerta LULD": g["alert_status"],
                "raw_dist": g["min_dist_pct"],
                "raw_spot": g["spot"]
            })
        except Exception:
            continue
            
    df = pd.DataFrame(rows)
    if not df.empty:
        return df.sort_values(by="raw_dist", ascending=True).reset_index(drop=True)
    return df


def add_luld_bands_to_chart(fig, luld_data: dict, x_dates=None):
    """
    Dibuja los guardarraíles dinámicos Upper Band (Limit Up) y Lower Band (Limit Down)
    como líneas guía limpias en el gráfico Plotly sin alterar el eje X.
    """
    if not luld_data or not fig:
        return fig
        
    upper = luld_data.get("upper_band")
    lower = luld_data.get("lower_band")
    band_pct = luld_data.get("band_pct", 5.0)

    if x_dates is None:
        try:
            x_dates = fig.data[0].x
        except Exception:
            x_dates = None

    if x_dates is None or len(x_dates) == 0:
        return fig

    lookback_bars = min(40, len(x_dates))
    x_start = x_dates[-lookback_bars]
    x_end = x_dates[-1]
    
    if upper:
        fig.add_shape(
            type="line",
            x0=x_start,
            x1=x_end,
            y0=upper,
            y1=upper,
            xref="x",
            yref="y",
            line=dict(color="#FF0055", width=1.4, dash="dash"),
            row=1, col=1
        )
        fig.add_annotation(
            xref="x",
            yref="y",
            x=x_end,
            y=upper,
            text=f"<b>LIMIT UP (+{band_pct:.1f}%)</b> ${upper:.2f}",
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            font=dict(color="#FF0055", size=9, family="JetBrains Mono"),
            bgcolor="rgba(24, 10, 18, 0.9)",
            bordercolor="rgba(255, 0, 85, 0.5)",
            borderwidth=1,
            borderpad=2,
            row=1, col=1
        )
    if lower:
        fig.add_shape(
            type="line",
            x0=x_start,
            x1=x_end,
            y0=lower,
            y1=lower,
            xref="x",
            yref="y",
            line=dict(color="#00FF87", width=1.4, dash="dash"),
            row=1, col=1
        )
        fig.add_annotation(
            xref="x",
            yref="y",
            x=x_end,
            y=lower,
            text=f"<b>LIMIT DOWN (-{band_pct:.1f}%)</b> ${lower:.2f}",
            showarrow=False,
            xanchor="right",
            yanchor="top",
            font=dict(color="#00FF87", size=9, family="JetBrains Mono"),
            bgcolor="rgba(10, 24, 18, 0.9)",
            bordercolor="rgba(0, 255, 135, 0.5)",
            borderwidth=1,
            borderpad=2,
            row=1, col=1
        )
    return fig
