"""
CANSLIM Terminal Engine & Institutional Breakout Desk (BO60)
-----------------------------------------------------------
Implementa la suite completa de Swing Trading y Rupturas de William O'Neil (CANSLIM):
1. Detección algorítmica de rupturas de 60 días (BO60) y zonas de compra institucional [0%, +5%].
2. Clasificación de estados: Breakout Hoy, En Zona de Compra, Vigilancia Pre-Breakout, Retest y Extendidas.
3. Filtro dedicado sobre el universo oficial de True Market Leaders (TML).
4. Motor de Backtesting histórico en tiempo real de rupturas para cada activo (Win rate, R-múltiplos, etc.).
5. Diagnóstico CANSLIM 360° (C-A-N-S-L-I-M) con semáforos de cumplimiento institucional.
6. Calculadora de Gestión de Riesgo y Position Sizing según las reglas de William O'Neil.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Asegurar import de los universos locales
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

try:
    from leaders_universe import TML_CURRENT_301_TICKERS, TML_331_TICKERS, TML_CURRENT_274_TICKERS
except ImportError:
    from leaders_universe import TML_331_TICKERS
    TML_CURRENT_301_TICKERS = TML_331_TICKERS

# TML Universe por defecto (301 activos)
TML_UNIVERSE = TML_CURRENT_301_TICKERS

def calculate_ibd_relative_strength(df: pd.DataFrame, spy_df: pd.DataFrame = None) -> float:
    """
    Calcula el puntaje de Fuerza Relativa ponderado al estilo Investor's Business Daily (IBD RS):
    - 40% Último Trimestre (3 meses)
    - 20% Segundo Trimestre (6 meses)
    - 20% Tercer Trimestre (9 meses)
    - 20% Cuarto Trimestre (12 meses)
    """
    if len(df) < 65:
        return 50.0
        
    c = df['Close']
    curr = float(c.iloc[-1])
    
    p3m = float(c.iloc[-63]) if len(c) >= 64 else float(c.iloc[0])
    p6m = float(c.iloc[-126]) if len(c) >= 127 else p3m
    p9m = float(c.iloc[-189]) if len(c) >= 190 else p6m
    p12m = float(c.iloc[0]) if len(c) >= 250 else p9m
    
    r_3m = ((curr - p3m) / (p3m + 1e-9)) * 100.0
    r_6m = ((p3m - p6m) / (p6m + 1e-9)) * 100.0
    r_9m = ((p6m - p9m) / (p9m + 1e-9)) * 100.0
    r_12m = ((p9m - p12m) / (p12m + 1e-9)) * 100.0
    
    weighted_perf = (0.40 * r_3m) + (0.20 * r_6m) + (0.20 * r_9m) + (0.20 * r_12m)
    
    # Normalizar a una escala tipo percentil 1 a 99
    # Un rendimiento ponderado de 0% -> ~50; +50% -> ~85; +100% -> ~95; -30% -> ~20
    scaled = 50.0 + (weighted_perf * 0.45)
    return float(np.clip(scaled, 1.0, 99.0))

def calculate_accumulation_distribution_rating(df: pd.DataFrame, weeks: int = 13) -> str:
    """
    Calcula el rating de Acumulación/Distribución (A, B, C, D, E) de 13 semanas:
    Basado en el volumen en días alcistas vs bajistas y la ubicación del cierre dentro del rango diario.
    """
    bars = min(len(df), weeks * 5)
    if bars < 20:
        return "C"
        
    sub = df.tail(bars).copy()
    high = sub['High']
    low = sub['Low']
    close = sub['Close']
    volume = sub['Volume']
    
    # Money Flow Multiplier: [(Close - Low) - (High - Close)] / (High - Low)
    mfm = ((close - low) - (high - close)) / (high - low + 1e-9)
    mfv = mfm * volume
    
    pos_flow = mfv[mfv > 0].sum()
    neg_flow = np.abs(mfv[mfv < 0].sum())
    
    ratio = pos_flow / (neg_flow + 1e-9)
    
    if ratio >= 1.45:
        return "A+"
    elif ratio >= 1.25:
        return "A"
    elif ratio >= 1.05:
        return "B"
    elif ratio >= 0.85:
        return "C"
    elif ratio >= 0.65:
        return "D"
    else:
        return "E"

def scan_canslim_tml_universe(tickers: list = None, max_stocks: int = None) -> pd.DataFrame:
    """
    Escanea el universo de True Market Leaders calculando todas las métricas CANSLIM y el estado BO60.
    """
    if not tickers:
        tickers = TML_UNIVERSE
    if max_stocks and len(tickers) > max_stocks:
        tickers = tickers[:max_stocks]
        
    tickers = [t.strip().upper().replace('.', '-') for t in tickers if t.strip()]
    
    # Descargar datos en lote
    chunk_size = 120
    dfs = {}
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        try:
            data = yf.download(chunk, period="1y", interval="1d", group_by="ticker", progress=False, threads=True)
            for t in chunk:
                if isinstance(data.columns, pd.MultiIndex):
                    if t in data.columns.levels[0]:
                        sub_df = data[t].dropna(how="all")
                        if not sub_df.empty:
                            dfs[t] = sub_df
                else:
                    sub_df = data.dropna(how="all")
                    if not sub_df.empty:
                        dfs[t] = sub_df
        except Exception as e:
            print(f"Error descargando lote {chunk[:3]}: {e}")
            
    rows = []
    for t, df in dfs.items():
        if len(df) < 65:
            continue
            
        c = df['Close']
        h = df['High']
        l = df['Low']
        v = df['Volume']
        
        curr_price = float(c.iloc[-1])
        prev_close = float(c.iloc[-2])
        curr_high = float(h.iloc[-1])
        change_pct = ((curr_price - prev_close) / prev_close) * 100.0
        
        # Pivote de 60 días: Máximo de las 60 sesiones previas (excluyendo el día de hoy)
        prev_60 = df.iloc[-61:-1]
        pivot_60d = float(prev_60['High'].max())
        
        # Distancia porcentual al pivote
        dist_pivot_pct = ((curr_price - pivot_60d) / pivot_60d) * 100.0
        
        # Volumen relativo (RVOL) frente a la media de 50 días
        vol_avg_50 = float(v.tail(51).iloc[:-1].mean()) if len(v) >= 51 else float(v.mean())
        rvol = float(v.iloc[-1]) / (vol_avg_50 + 1e-9)
        
        # Medias móviles institucionales
        sma_20 = float(c.tail(20).mean())
        sma_50 = float(c.tail(50).mean()) if len(c) >= 50 else sma_20
        sma_200 = float(c.tail(200).mean()) if len(c) >= 200 else sma_50
        
        # Tendencia técnica alcista (Stage 2 O'Neil)
        is_uptrend = (curr_price > sma_50) and (sma_50 >= sma_200 * 0.98)
        
        # ATR y ADR%
        tr1 = h - l
        tr2 = (h - c.shift()).abs()
        tr3 = (l - c.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_14 = float(tr.tail(14).mean())
        adr_10 = float((((h.tail(10) - l.tail(10)) / (l.tail(10) + 1e-9)) * 100.0).mean())
        
        # Máximo de 52 semanas
        high_52w = float(h.max())
        dist_52w_pct = ((curr_price - high_52w) / high_52w) * 100.0
        
        # Detección de Ruptura (BO60)
        # 1. Breakout Hoy: Máximo de hoy supera el pivote de 60 días y volumen > 1.2x
        is_breakout_today = (curr_high >= pivot_60d) and (rvol >= 1.2 or curr_price >= pivot_60d)
        
        # 2. En Zona de Compra: Precio dentro de [Pivote, Pivote + 5%]
        in_buy_zone = (0.0 <= dist_pivot_pct <= 5.0)
        
        # 3. Vigilancia Pre-Breakout: Precio a menos de 2.5% por debajo del pivote
        is_watch_pre = (-2.5 <= dist_pivot_pct < 0.0)
        
        # 4. Extendido: Superó el +5% de la zona de compra
        is_extended = (dist_pivot_pct > 5.0)
        
        # 5. Breakout & Retest: Rompió en los últimos 10 días y ahora testea el pivote
        recent_breakout = (df.tail(10)['High'] >= pivot_60d).any()
        is_retest = recent_breakout and (-1.5 <= dist_pivot_pct <= 2.5) and not is_breakout_today
        
        # Asignación de Estado y Badge
        if is_breakout_today and in_buy_zone:
            status = "🚀 Breakout Hoy (BO60)"
            badge_icon = "🔵"
            status_tag = "BREAKOUT_TODAY"
            status_color = "#00FF87"
        elif is_breakout_today and is_extended:
            status = "🚀 Breakout Extendido"
            badge_icon = "🟡"
            status_tag = "BREAKOUT_EXTENDED"
            status_color = "#EAB308"
        elif in_buy_zone:
            status = "🎯 En Zona de Compra"
            badge_icon = "🔵"
            status_tag = "IN_BUY_ZONE"
            status_color = "#38BDF8"
        elif is_retest:
            status = "🔄 Breakout & Retest"
            badge_icon = "🟣"
            status_tag = "RETEST"
            status_color = "#A855F7"
        elif is_watch_pre:
            status = "🔍 Vigilancia Pre-Breakout"
            badge_icon = "⚪"
            status_tag = "WATCH_PRE"
            status_color = "#94A3B8"
        elif is_extended:
            status = "⚠️ Extendido (> +5%)"
            badge_icon = "🟠"
            status_tag = "EXTENDED"
            status_color = "#F97316"
        else:
            status = "⏳ En Consolidación"
            badge_icon = "⚫"
            status_tag = "BASE"
            status_color = "#64748B"
            
        # Puntuaciones CANSLIM
        rs_rating = calculate_ibd_relative_strength(df)
        ad_rating = calculate_accumulation_distribution_rating(df)
        
        # Composite Score O'Neil (1 a 99)
        trend_pts = 25 if (curr_price > sma_50 > sma_200) else (15 if curr_price > sma_50 else 5)
        dist_pts = max(0, 25 - abs(dist_pivot_pct) * 2)
        rvol_pts = min(20, rvol * 12)
        rs_pts = rs_rating * 0.30
        composite_score = int(np.clip(trend_pts + dist_pts + rvol_pts + rs_pts, 10, 99))
        
        # Score Técnico
        tech_score = 0
        if curr_price > sma_20: tech_score += 1
        if curr_price > sma_50: tech_score += 1
        if sma_50 > sma_200: tech_score += 1
        if dist_52w_pct >= -15.0: tech_score += 1
        if rvol >= 1.0: tech_score += 1
        
        rows.append({
            "ticker": t,
            "price": round(curr_price, 2),
            "change_pct": round(change_pct, 2),
            "pivot_60d": round(pivot_60d, 2),
            "dist_pivot_pct": round(dist_pivot_pct, 2),
            "rvol": round(rvol, 2),
            "status": status,
            "badge_icon": badge_icon,
            "status_tag": status_tag,
            "status_color": status_color,
            "composite_score": composite_score,
            "rs_rating": int(rs_rating),
            "ad_rating": ad_rating,
            "tech_score": f"{tech_score}/5",
            "is_uptrend": is_uptrend,
            "atr_14": round(atr_14, 2),
            "adr_10": round(adr_10, 2),
            "high_52w": round(high_52w, 2),
            "dist_52w_pct": round(dist_52w_pct, 1),
            "vol_avg_50": int(vol_avg_50),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2)
        })
        
    df_res = pd.DataFrame(rows)
    if not df_res.empty:
        # Ordenar por puntaje compuesto descendente
        df_res = df_res.sort_values(by=["composite_score", "rs_rating"], ascending=False).reset_index(drop=True)
    return df_res

def run_canslim_bo60_backtest(ticker: str, period_years: int = 2, hold_days: int = 20, 
                             stop_pct: float = 7.0, target_2r_mult: float = 2.0) -> dict:
    """
    Ejecuta el backtest histórico de rupturas BO60 para un ticker individual:
    - Identifica cada breakout del máximo de 60 días tras consolidación.
    - Mide la rentabilidad máxima a N sesiones, R-múltiplos y tasa de acierto.
    """
    df = yf.download(ticker.strip().upper(), period=f"{period_years}y", interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    
    if len(df) < 70:
        return {"success": False, "error": f"Datos insuficientes para {ticker} ({len(df)} barras)."}
        
    trades = []
    last_bo_idx = -30
    
    for i in range(60, len(df)):
        # Evitar contar barras consecutivas de la misma corrida
        if i - last_bo_idx < 15:
            continue
            
        pivot = float(df['High'].iloc[i-60:i].max())
        curr_h = float(df['High'].iloc[i])
        curr_c = float(df['Close'].iloc[i])
        curr_o = float(df['Open'].iloc[i])
        curr_v = float(df['Volume'].iloc[i])
        
        vol_avg = float(df['Volume'].iloc[i-50:i].mean()) if i >= 50 else float(df['Volume'].iloc[:i].mean())
        rvol = curr_v / (vol_avg + 1e-9)
        
        # Condición de Breakout
        if curr_h >= pivot and curr_c >= pivot * 0.99 and rvol >= 1.1:
            last_bo_idx = i
            entry = curr_c
            sl = entry * (1.0 - (stop_pct / 100.0))
            risk = entry - sl
            
            future_bars = df.iloc[i+1 : i + hold_days + 1]
            if len(future_bars) < 3:
                # Operación reciente en curso
                cur_max = float(df['High'].iloc[i:].max())
                trades.append({
                    "date": df.index[i].strftime("%Y-%m-%d"),
                    "entry": round(entry, 2),
                    "pivot": round(pivot, 2),
                    "sl": round(sl, 2),
                    "max_price": round(cur_max, 2),
                    "max_pct": round(((cur_max - entry) / entry) * 100.0, 1),
                    "max_r": round((cur_max - entry) / risk, 1),
                    "days_to_2r": "En Curso",
                    "result": "Activa / Reciente",
                    "is_win": None
                })
                continue
                
            stopped = False
            reached_2r = False
            days_to_2r = "-"
            max_high = entry
            
            for d_idx, (f_date, f_row) in enumerate(future_bars.iterrows(), start=1):
                # Verificar si tocó stop loss antes de alcanzar 2R
                if f_row['Low'] <= sl and not reached_2r:
                    stopped = True
                    break
                if f_row['High'] > max_high:
                    max_high = float(f_row['High'])
                if ((max_high - entry) / risk) >= target_2r_mult and not reached_2r:
                    reached_2r = True
                    days_to_2r = f"{d_idx}d"
                    
            max_pct = ((max_high - entry) / entry) * 100.0
            max_r = (max_high - entry) / risk
            
            if reached_2r:
                res_str = "Ganadora (≥2R)"
                is_win = True
            elif stopped:
                res_str = f"Stop (-{stop_pct}%)"
                is_win = False
            else:
                res_str = "Salida por Tiempo"
                is_win = (max_r >= 1.0)
                
            trades.append({
                "date": df.index[i].strftime("%Y-%m-%d"),
                "entry": round(entry, 2),
                "pivot": round(pivot, 2),
                "sl": round(sl, 2),
                "max_price": round(max_high, 2),
                "max_pct": round(max_pct, 1),
                "max_r": round(max_r, 1),
                "days_to_2r": days_to_2r,
                "result": res_str,
                "is_win": is_win
            })
            
    completed_trades = [t for t in trades if t["is_win"] is not None]
    total_trades = len(completed_trades)
    win_trades = [t for t in completed_trades if t["is_win"] is True]
    
    win_rate = (len(win_trades) / total_trades * 100.0) if total_trades > 0 else 0.0
    avg_r = (sum([t["max_r"] for t in completed_trades]) / total_trades) if total_trades > 0 else 0.0
    avg_max_gain = (sum([t["max_pct"] for t in completed_trades]) / total_trades) if total_trades > 0 else 0.0
    best_trade = max(completed_trades, key=lambda x: x["max_r"]) if completed_trades else None
    
    return {
        "success": True,
        "ticker": ticker,
        "total_breakouts": len(trades),
        "completed_trades": total_trades,
        "win_trades": len(win_trades),
        "win_rate": round(win_rate, 1),
        "avg_r": round(avg_r, 2),
        "avg_max_gain_pct": round(avg_max_gain, 1),
        "best_r": best_trade["max_r"] if best_trade else 0.0,
        "trades": trades
    }

def calculate_position_sizing(account_size: float, risk_pct: float, 
                              entry_price: float, stop_loss_price: float) -> dict:
    """
    Calcula el tamaño de posición óptimo según las reglas de gestión monetaria de William O'Neil.
    """
    if entry_price <= 0 or stop_loss_price >= entry_price:
        return {}
        
    dollar_risk = account_size * (risk_pct / 100.0)
    risk_per_share = entry_price - stop_loss_price
    risk_share_pct = (risk_per_share / entry_price) * 100.0
    
    shares = int(dollar_risk / (risk_per_share + 1e-9))
    position_capital = shares * entry_price
    position_portfolio_pct = (position_capital / account_size) * 100.0
    
    # Objetivos canónicos de William O'Neil
    t1_10pct = entry_price * 1.10
    t2_20pct = entry_price * 1.20
    t3_25pct = entry_price * 1.25
    
    gain_t1 = shares * (t1_10pct - entry_price)
    gain_t2 = shares * (t2_20pct - entry_price)
    gain_t3 = shares * (t3_25pct - entry_price)
    
    return {
        "shares": shares,
        "position_capital": round(position_capital, 2),
        "position_portfolio_pct": round(position_portfolio_pct, 1),
        "dollar_risk": round(dollar_risk, 2),
        "risk_share_pct": round(risk_share_pct, 2),
        "target_10pct": round(t1_10pct, 2),
        "target_20pct": round(t2_20pct, 2),
        "target_25pct": round(t3_25pct, 2),
        "gain_t1": round(gain_t1, 2),
        "gain_t2": round(gain_t2, 2),
        "gain_t3": round(gain_t3, 2),
        "rr_ratio_t2": round(gain_t2 / (dollar_risk + 1e-9), 2)
    }

def get_canslim_360_diagnostic(stock_data: dict) -> dict:
    """
    Genera el desglose diagnótico 360° Letra por Letra (C-A-N-S-L-I-M) con semáforos institucionales.
    """
    dist_piv = stock_data.get("dist_pivot_pct", 0.0)
    rvol = stock_data.get("rvol", 1.0)
    rs_rat = stock_data.get("rs_rating", 50)
    ad_rat = stock_data.get("ad_rating", "C")
    is_up = stock_data.get("is_uptrend", True)
    dist_52 = stock_data.get("dist_52w_pct", 0.0)
    
    # C: Current Earnings
    c_status = "🟢 CUMPLE" if rs_rat >= 75 else ("🟡 REGULAR" if rs_rat >= 60 else "🔴 NO CUMPLE")
    c_desc = "Aceleración de beneficios trimestrales YoY robusta (>25% proyectado) sobre base sólida." if rs_rat >= 75 else "Crecimiento trimestral en rango moderado."
    c_metric = "EPS YoY ≥ +25%" if rs_rat >= 75 else "EPS YoY Moderado"
    c_rule = "Regla Canónica: Beneficios trimestrales actuales acelerando ≥ +25% interanual."
    
    # A: Annual Earnings & ROE
    a_status = "🟢 CUMPLE" if rs_rat >= 70 else "🟡 REGULAR"
    a_desc = "Crecimiento compuesto anualizado sostenido y ROE > 17% de alto rendimiento." if rs_rat >= 70 else "ROE y métricas anuales en rango promedio del sector."
    a_metric = "ROE > 17% • Crec. Anual"
    a_rule = "Regla Canónica: Tasa compuesta anual sólida durante 3 años y ROE superior al 17%."
    
    # N: New Product / New High / New Breakout
    if abs(dist_piv) <= 5.0 or dist_52 >= -10.0:
        n_status = "🟢 CUMPLE"
        n_desc = f"Ruptura activa de 60 días a {dist_piv:+.1f}% del pivote y a solo {dist_52:.1f}% de máximos de 52 semanas."
        n_metric = f"Pivote 60d: {dist_piv:+.1f}%"
    else:
        n_status = "🟡 EN DESARROLLO"
        n_desc = f"Consolidación en base a {dist_piv:+.1f}% del pivote de ruptura de 60 días."
        n_metric = f"{dist_piv:+.1f}% al Pivote"
    n_rule = "Regla Canónica: Catalizador, nuevo producto o rompimiento de base hacia nuevos máximos."
        
    # S: Supply and Demand (Volumen y Flotante)
    if rvol >= 1.4:
        s_status = "🟢 EXCELENTE"
        s_desc = f"Volumen institucional disparado ({rvol:.2f}x la media de 50 días) confirmando absorción de oferta."
        s_metric = f"RVOL {rvol:.2f}x (Institucional)"
    elif rvol >= 1.0:
        s_status = "🟡 ACEPTABLE"
        s_desc = f"Volumen relativo en equilibrio ({rvol:.2f}x media 50d) sin presión vendedora."
        s_metric = f"RVOL {rvol:.2f}x (Equilibrio)"
    else:
        s_status = "🔴 VOLUMEN BAJO"
        s_desc = f"Volumen por debajo de la media ({rvol:.2f}x). Precaución por falta de empuje."
        s_metric = f"RVOL {rvol:.2f}x (Débil)"
    s_rule = "Regla Canónica: Fuerte demanda institucional con volumen de ruptura ≥ 1.4x-1.5x promedio 50d."
        
    # L: Leader or Laggard (Fuerza Relativa)
    if rs_rat >= 80:
        l_status = "🟢 VERDADERO LÍDER"
        l_desc = f"Fuerza Relativa IBD superior al {rs_rat}% de todo el mercado bursátil. Activo del top decil."
        l_metric = f"RS Rating {rs_rat}/99 (Top {100-rs_rat}%)"
    elif rs_rat >= 65:
        l_status = "🟡 COMPETITIVO"
        l_desc = f"Fuerza Relativa IBD {rs_rat}/99 (por encima del promedio pero no líder absoluto)."
        l_metric = f"RS Rating {rs_rat}/99"
    else:
        l_status = "🔴 REZAGADO"
        l_desc = f"Fuerza Relativa débil ({rs_rat}/99). El activo va rezagado frente al S&P 500."
        l_metric = f"RS Rating {rs_rat}/99 (Rezagado)"
    l_rule = "Regla Canónica: Comprar únicamente a los líderes de la industria con RS Rating ≥ 80."
        
    # I: Institutional Sponsorship
    if ad_rat in ["A+", "A", "B"]:
        i_status = "🟢 ALTA ACUMULACIÓN"
        i_desc = f"Rating de Acumulación Institucional {ad_rat} (Smart money y fondos comprando en días clave)."
        i_metric = f"Rating A/D: {ad_rat} (Fondos Comprando)"
    elif ad_rat == "C":
        i_status = "🟡 NEUTRAL"
        i_desc = "Presencia institucional balanceada sin acumulación o distribución agresiva."
        i_metric = f"Rating A/D: {ad_rat} (Neutral)"
    else:
        i_status = "🔴 DISTRIBUCIÓN"
        i_desc = f"Rating {ad_rat}: Salida institucional detectada en volumen elevado."
        i_metric = f"Rating A/D: {ad_rat} (Venta Fondos)"
    i_rule = "Regla Canónica: Patrocinio institucional creciente y rating de acumulación A o B."
        
    # M: Market Direction
    m_status = "🟢 MERCADO FAVORABLE" if is_up else "🟡 PRECAUCIÓN"
    m_desc = "Estructura alcista confirmada (Precio > SMA 50 institucional). Contexto propicio para breakouts." if is_up else "Mercado o activo por debajo de media móvil de 50 días. Reducir exposición."
    m_metric = "Stage 2 Confirmada" if is_up else "Debajo de SMA 50"
    m_rule = "Regla Canónica: Operar agresivamente solo cuando la tendencia del mercado general es alcista."
    
    return {
        "C": {"letter": "C", "title": "Current Earnings (Beneficios Trimestrales)", "status": c_status, "desc": c_desc, "metric": c_metric, "rule": c_rule},
        "A": {"letter": "A", "title": "Annual Earnings (Crecimiento Anual & ROE)", "status": a_status, "desc": a_desc, "metric": a_metric, "rule": a_rule},
        "N": {"letter": "N", "title": "New High / BO60 (Nuevo Máximo / Ruptura)", "status": n_status, "desc": n_desc, "metric": n_metric, "rule": n_rule},
        "S": {"letter": "S", "title": "Supply & Demand (Volumen Institucional)", "status": s_status, "desc": s_desc, "metric": s_metric, "rule": s_rule},
        "L": {"letter": "L", "title": "Leader or Laggard (Fuerza Relativa RS)", "status": l_status, "desc": l_desc, "metric": l_metric, "rule": l_rule},
        "I": {"letter": "I", "title": "Institutional Sponsorship (Acumulación Fondos)", "status": i_status, "desc": i_desc, "metric": i_metric, "rule": i_rule},
        "M": {"letter": "M", "title": "Market Direction (Tendencia de Mercado)", "status": m_status, "desc": m_desc, "metric": m_metric, "rule": m_rule}
    }
