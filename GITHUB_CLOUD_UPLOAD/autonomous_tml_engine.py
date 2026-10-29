"""
TradingVolt Autonomous Market Leaders Engine (TML Engine)
=========================================================
Algoritmo de detección y clasificación 100% autónomo para identificar los líderes
del mercado de acciones de EE.UU. sin depender de herramientas de terceros.

Basado en el análisis cuantitativo de 274 líderes históricos:
- Fuerza Relativa (RS vs SPY a 3M y 6M)
- Estructura de Tendencia (Stage 2 / Minervini Trend Template)
- Proximidad a Máximos de 52 Semanas
- Aceleración de Momentum a Corto Plazo (1M)
- Acumulación Institucional (Up/Down Volume Ratio y Dólar-Volumen)
"""

import os
import sys
import json
import time

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

# Importar universos expandidos
try:
    from expanded_universes import US_BROAD_MARKET_TICKERS, HIGH_MOMENTUM_EXPANDED_TICKERS
except ImportError:
    US_BROAD_MARKET_TICKERS = []
    HIGH_MOMENTUM_EXPANDED_TICKERS = []

CACHE_FILE = Path(__file__).parent / "autonomous_leaders_cache.json"

def clean_ticker(t: str) -> str:
    return t.replace(".", "-").strip().upper()

def calculate_leader_metrics(ticker: str, df: pd.DataFrame, spy_close: pd.Series = None) -> dict:
    """Calcula todas las métricas cuantitativas de liderazgo para un activo."""
    if len(df) < 50:
        return None
        
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    vol = df["Volume"]
    
    curr_price = float(close.iloc[-1])
    if curr_price < 3.0: # Filtro de penny stocks ilíquidas
        return None
        
    # Medias Móviles
    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else curr_price
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else curr_price
    sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else sma50
    sma200_20d_ago = float(close.rolling(200).mean().iloc[-20]) if len(close) >= 220 else sma200
    
    # 52w High / Low
    high52 = float(high.max())
    low52 = float(low.min())
    dist_52h = ((curr_price - high52) / high52) * 100.0
    dist_52l = ((curr_price - low52) / low52) * 100.0
    
    # Retornos / Momentum
    roc_21 = float(((curr_price / close.iloc[-21]) - 1.0) * 100.0) if len(close) >= 22 else 0.0
    roc_63 = float(((curr_price / close.iloc[-63]) - 1.0) * 100.0) if len(close) >= 64 else 0.0
    roc_126 = float(((curr_price / close.iloc[-126]) - 1.0) * 100.0) if len(close) >= 127 else roc_63
    
    # RS vs SPY
    spy_roc_63 = 0.0
    if spy_close is not None and len(spy_close) >= 64:
        spy_roc_63 = float(((spy_close.iloc[-1] / spy_close.iloc[-63]) - 1.0) * 100.0)
    rs_vs_spy_3m = roc_63 - spy_roc_63
    
    # RS Line proximity to 52w peak
    rs_line_dist_high = -20.0
    if spy_close is not None:
        rs_line = (close / spy_close).dropna()
        if len(rs_line) > 20:
            rs_peak = float(rs_line.max())
            rs_line_dist_high = ((float(rs_line.iloc[-1]) - rs_peak) / rs_peak) * 100.0
            
    # ADR% (20d)
    daily_range_pct = (high - low) / close
    adr20_pct = float(daily_range_pct.iloc[-20:].mean() * 100.0) if len(daily_range_pct) >= 20 else 0.0
    
    # Dollar Volume (20d)
    dollar_vol_20d = float((close * vol).iloc[-20:].mean()) if len(close) >= 20 else 0.0
    dollar_vol_mil = dollar_vol_20d / 1e6
    if dollar_vol_mil < 10.0: # Mínimo $10M diarios de liquidez
        return None
        
    # Up/Down Volume Ratio (50d)
    if len(close) >= 51:
        price_diff = close.diff().iloc[-50:]
        vols_50 = vol.iloc[-50:]
        up_vol = vols_50[price_diff > 0].sum()
        down_vol = vols_50[price_diff < 0].sum()
        ud_ratio = float(up_vol / (down_vol + 1e-6))
    else:
        ud_ratio = 1.0
        
    # Flags de estructura
    above_sma20 = 1 if curr_price > sma20 else 0
    above_sma50 = 1 if curr_price > sma50 else 0
    above_sma200 = 1 if curr_price > sma200 else 0
    sma50_above_200 = 1 if sma50 > sma200 else 0
    sma200_rising = 1 if sma200 >= sma200_20d_ago else 0
    stage_2 = 1 if (above_sma50 and above_sma200 and sma50_above_200) else 0
    
    # Puntuación Compuesta (0 a 100 pts)
    score = 0.0
    if above_sma20: score += 5
    if above_sma50: score += 8
    if above_sma200: score += 7
    if sma50_above_200: score += 5
    
    # Fuerza Relativa
    if rs_vs_spy_3m >= 30.0: score += 15
    elif rs_vs_spy_3m >= 15.0: score += 12
    elif rs_vs_spy_3m >= 5.0: score += 8
    elif rs_vs_spy_3m >= 0.0: score += 4
    
    # Aceleración 1M
    if roc_21 >= 15.0: score += 10
    elif roc_21 >= 8.0: score += 6
    elif roc_21 >= 3.0: score += 3
    
    # RS Line peak
    if rs_line_dist_high >= -5.0: score += 5
    elif rs_line_dist_high >= -15.0: score += 3
    
    # Proximidad Máximos 52s
    if dist_52h >= -5.0: score += 20
    elif dist_52h >= -10.0: score += 16
    elif dist_52h >= -18.0: score += 12
    elif dist_52h >= -25.0: score += 7
    
    # Mínimos 52s
    if dist_52l >= 60.0: score += 5
    elif dist_52l >= 30.0: score += 3
    
    # Acumulación Volumen
    if ud_ratio >= 1.30: score += 10
    elif ud_ratio >= 1.10: score += 7
    elif ud_ratio >= 0.95: score += 4
    
    # Liquidez Institucional
    if dollar_vol_mil >= 50.0: score += 10
    elif dollar_vol_mil >= 25.0: score += 7
    elif dollar_vol_mil >= 10.0: score += 4
    
    # Sub-persona
    if dist_52h >= -12.0 and above_sma50:
        persona = "Apex Leader (Cerca de Máximos)"
    elif dist_52h >= -22.0 and (roc_63 >= 15.0 or roc_126 >= 25.0):
        persona = "Pullback de Base / Setup VCP"
    elif roc_21 >= 12.0 and dist_52l >= 35.0:
        persona = "Acelerador 1M / Giro Explosivo"
    elif rs_line_dist_high >= -8.0 and above_sma200:
        persona = "Líder de Fuerza Relativa (RS)"
    else:
        persona = "Líder de Consolidación"
        
    return {
        "ticker": ticker,
        "price": round(curr_price, 2),
        "score": round(score, 1),
        "persona": persona,
        "dist_52h": round(dist_52h, 2),
        "dist_52l": round(dist_52l, 2),
        "roc_21": round(roc_21, 2),
        "roc_63": round(roc_63, 2),
        "rs_vs_spy_3m": round(rs_vs_spy_3m, 2),
        "adr20_pct": round(adr20_pct, 2),
        "dollar_vol_mil": round(dollar_vol_mil, 1),
        "ud_ratio": round(ud_ratio, 2),
        "stage_2": stage_2,
        "above_sma20": above_sma20,
        "above_sma50": above_sma50,
        "above_sma200": above_sma200
    }

def scan_and_generate_leaders(universe_tickers=None, top_n: int = 260) -> pd.DataFrame:
    """Ejecuta el escaneo de líderes sobre el universo amplio y devuelve el Top N ordenado."""
    if universe_tickers is None or len(universe_tickers) == 0:
        universe_tickers = list(set(US_BROAD_MARKET_TICKERS + HIGH_MOMENTUM_EXPANDED_TICKERS))
        
    clean_list = list(set([clean_ticker(t) for t in universe_tickers if t and len(t) <= 6]))
    download_list = list(set(clean_list + ["SPY"]))
    
    print(f"[TradingVolt] Escaneando líderes autónomos sobre {len(clean_list)} activos...")
    
    # Descargar datos en bloques para estabilidad
    chunk_size = 150
    chunks = [download_list[i:i + chunk_size] for i in range(0, len(download_list), chunk_size)]
    
    all_dfs = {}
    spy_close = None
    
    for idx, chunk in enumerate(chunks):
        try:
            d = yf.download(chunk, period="1y", interval="1d", group_by="ticker", auto_adjust=True, progress=False, threads=True)
            if "SPY" in d.columns.levels[0] and spy_close is None:
                spy_close = d["SPY"]["Close"].dropna()
                
            for t in chunk:
                if t in d.columns.levels[0]:
                    df_t = d[t].dropna()
                    if len(df_t) >= 50:
                        all_dfs[t] = df_t
        except Exception as e:
            print(f"Advertencia en chunk {idx+1}: {e}")
            
    print(f"[OK] Datos descargados con éxito para {len(all_dfs)} activos. Calculando métricas de liderazgo...")
    
    records = []
    for t, df_t in all_dfs.items():
        if t == "SPY":
            continue
        try:
            m = calculate_leader_metrics(t, df_t, spy_close)
            if m is not None:
                records.append(m)
        except Exception:
            pass
            
    df_leaders = pd.DataFrame(records)
    if df_leaders.empty:
        return pd.DataFrame()
        
    # Ordenar por Leader Score descendente
    df_leaders = df_leaders.sort_values(by=["score", "roc_63", "dist_52h"], ascending=[False, False, False]).reset_index(drop=True)
    
    top_leaders = df_leaders.head(top_n)
    
    # Guardar en caché con metadatos
    cache_payload = {
        "timestamp": datetime.now().isoformat(),
        "total_scanned": len(all_dfs),
        "total_qualified": len(df_leaders),
        "top_n": top_n,
        "tickers": top_leaders["ticker"].tolist(),
        "leaders": top_leaders.to_dict(orient="records")
    }
    
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_payload, f, indent=2)
        print(f"[OK] Guardados {len(top_leaders)} líderes autónomos en {CACHE_FILE}")
    except Exception as e:
        print(f"Error guardando caché: {e}")
        
    return top_leaders

def get_autonomous_market_leaders(top_n: int = 260, max_age_hours: int = 48) -> list:
    """Devuelve la lista de tickers de los líderes autónomos actuales desde la caché o regenera."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cache_time = datetime.fromisoformat(data["timestamp"])
            if (datetime.now() - cache_time).total_seconds() < max_age_hours * 3600:
                return data.get("tickers", [])[:top_n]
        except Exception:
            pass
            
    # Si no hay caché o expiró, generamos
    df = scan_and_generate_leaders(top_n=top_n)
    if not df.empty:
        return df["ticker"].tolist()
    return []

if __name__ == "__main__":
    df_res = scan_and_generate_leaders(top_n=260)
    print("\n" + "="*80)
    print("TOP 25 LÍDERES AUTÓNOMOS GENERADOS POR TRADINGVOLT:")
    print("="*80)
    print(df_res[["ticker", "price", "score", "persona", "roc_63", "dist_52h", "ud_ratio", "dollar_vol_mil"]].head(25).to_string(index=False))
