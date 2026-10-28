"""
TradingVolt • Free Unusual Options Activity (UOA) & Whale Flow Engine
100% Free - Powered by CBOE Official CDN & Yahoo Finance Option Chains.
No OPRA fees, no Massive paid subscription needed.

Mathematical Anomalies Detected:
1. Volume / Open Interest Ratio (V/OI >= 1.5x, 3.0x, 10.0x) -> Confirms NEW positions opened
2. Whale Premium Threshold (Price * Volume * 100 >= $100k, $500k, $1M)
3. Moneyness & Convexity (OTM, ATM, ITM)
4. Bullish vs Bearish Sentiment Skew (Call Sweeps vs Put Blocks)
"""
import urllib.request
import json
import re
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf

# Patrón estándar OSI de opciones
OSI_REGEX = re.compile(r"^([A-Z]+)(\d{6})([CP])(\d{8})$")

def format_trade_time(val) -> str:
    """Convierte cualquier timestamp (UTC o ISO) a hora oficial de mercado de Nueva York (EST/EDT)."""
    if pd.isna(val) or val is None or val == "":
        return "N/A"
    try:
        dt = pd.to_datetime(val)
        if dt.tzinfo is not None:
            dt_est = dt.tz_convert("America/New_York")
        else:
            # Si no trae zona horaria (ej. CBOE local exchange time), se formatea directo
            dt_est = dt
        return dt_est.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(val)

def parse_osi_symbol(symbol: str) -> dict:
    """Parsea el símbolo OSI estándar (ej. NVDA261026C00200000)."""
    clean_sym = symbol.replace("O:", "").strip().upper()
    match = OSI_REGEX.match(clean_sym)
    if not match:
        return {
            "root": clean_sym,
            "exp_date": "N/A",
            "type": "N/A",
            "strike": 0.0
        }
    root, exp_str, cp, strike_str = match.groups()
    exp_formatted = f"20{exp_str[0:2]}-{exp_str[2:4]}-{exp_str[4:6]}"
    opt_type = "CALL" if cp == "C" else "PUT"
    strike = int(strike_str) / 1000.0
    return {
        "root": root,
        "exp_date": exp_formatted,
        "type": opt_type,
        "strike": strike
    }


def scan_cboe_unusual_options(symbol: str = "SPY", min_v_oi: float = 1.5, min_premium: float = 250_000) -> pd.DataFrame:
    """
    Escanea la cadena de opciones oficial de CBOE para un ETF/Índice (SPY, QQQ, IWM, etc.)
    detectando órdenes institucionales inusuales (100% gratuito).
    """
    url = f"https://cdn.cboe.com/api/global/delayed_quotes/options/{symbol.upper()}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_options = data.get("data", {}).get("options", [])
            spot_price = float(data.get("data", {}).get("current_price", 0.0))
            
            if not raw_options:
                return pd.DataFrame()
                
            df = pd.DataFrame(raw_options)
            
            # Filtro base: volumen positivo y precio negociado
            df = df[df["volume"] > 0].copy()
            df["price"] = df["last_trade_price"].fillna(df["bid"])
            df = df[df["price"] > 0]
            
            # Cálculo de Ratio V/OI y Prima Nocional Total
            df["v_oi_ratio"] = df["volume"] / (df["open_interest"] + 1e-9)
            df["est_premium"] = df["volume"] * df["price"] * 100.0
            
            # Filtrar anomalías cuantitativas
            unusual = df[(df["v_oi_ratio"] >= min_v_oi) & (df["est_premium"] >= min_premium)].copy()
            
            if unusual.empty:
                return pd.DataFrame()
                
            # Parsear datos de contrato
            parsed = [parse_osi_symbol(s) for s in unusual["option"]]
            unusual["root"] = [p["root"] for p in parsed]
            unusual["exp_date"] = [p["exp_date"] for p in parsed]
            unusual["type"] = [p["type"] for p in parsed]
            unusual["strike"] = [p["strike"] for p in parsed]
            
            # Moneyness (OTM vs ITM)
            if spot_price > 0:
                unusual["moneyness_pct"] = ((unusual["strike"] / spot_price) - 1.0) * 100.0
            else:
                unusual["moneyness_pct"] = 0.0
                
            unusual["sentiment"] = np.where(
                unusual["type"] == "CALL",
                np.where(unusual["moneyness_pct"] >= 0, "🐂 BULLISH (Call OTM)", "🟢 BULLISH (Call ITM)"),
                np.where(unusual["moneyness_pct"] <= 0, "🐻 BEARISH (Put OTM)", "🔴 BEARISH (Put ITM)")
            )
            
            # Formatear columnas para visualización
            unusual["trade_time"] = unusual["last_trade_time"].apply(format_trade_time)
            unusual["premium_m"] = unusual["est_premium"] / 1_000_000.0
            unusual = unusual.sort_values(by="est_premium", ascending=False).reset_index(drop=True)
            
            return unusual[[
                "root", "option", "type", "strike", "exp_date", "trade_time", "price", 
                "volume", "open_interest", "v_oi_ratio", "est_premium", "premium_m", "sentiment"
            ]]
    except Exception as e:
        print(f"Error escaneando CBOE {symbol}: {e}")
        return pd.DataFrame()


def scan_single_stock_unusual_options(
    ticker: str,
    min_v_oi: float = 1.5,
    min_premium: float = 100_000,
    max_expirations: int = 4
) -> pd.DataFrame:
    """
    Escanea las opciones de CUALQUIER acción estadounidense (NVDA, TSLA, AAPL, PLTR, TML Leaders)
    utilizando Yahoo Finance Option Chains en múltiples fechas de vencimiento.
    """
    clean_ticker = ticker.strip().upper()
    try:
        t = yf.Ticker(clean_ticker)
        expirations = t.options
        if not expirations:
            return pd.DataFrame()
            
        spot_price = float(t.fast_info.get("lastPrice", 0.0))
        
        all_unusual = []
        # Escanear las expiraciones más cercanas y activas (donde se concentra el flujo institucional)
        for exp in expirations[:max_expirations]:
            try:
                chain = t.option_chain(exp)
                for opt_type, opt_df in [("CALL", chain.calls), ("PUT", chain.puts)]:
                    if opt_df.empty:
                        continue
                        
                    df = opt_df[opt_df["volume"] > 0].copy()
                    df["price"] = df["lastPrice"].fillna(df["bid"])
                    df = df[df["price"] > 0]
                    
                    df["v_oi_ratio"] = df["volume"] / (df["openInterest"] + 1e-9)
                    df["est_premium"] = df["volume"] * df["price"] * 100.0
                    
                    # Filtro de anomalía: V/OI alto y Prima significativa
                    matches = df[(df["v_oi_ratio"] >= min_v_oi) & (df["est_premium"] >= min_premium)].copy()
                    
                    for _, r in matches.iterrows():
                        k = float(r["strike"])
                        moneyness_pct = ((k / spot_price) - 1.0) * 100.0 if spot_price > 0 else 0.0
                        trade_time_str = format_trade_time(r.get("lastTradeDate"))
                        
                        sentiment = "🐂 BULLISH (Call Sweep)" if opt_type == "CALL" else "🐻 BEARISH (Put Block)"
                        if abs(moneyness_pct) >= 4.0:
                            sentiment += " ⚡ OTM Convexity"
                            
                        all_unusual.append({
                            "Ticker": clean_ticker,
                            "Contrato": r["contractSymbol"],
                            "Tipo": opt_type,
                            "Strike ($)": k,
                            "Vencimiento": exp,
                            "Hora Apertura (EST)": trade_time_str,
                            "Precio ($)": float(r["price"]),
                            "Volumen": int(r["volume"]),
                            "Open Interest": int(r["openInterest"]),
                            "Ratio V/OI": round(float(r["v_oi_ratio"]), 2),
                            "Prima Total ($)": float(r["est_premium"]),
                            "Prima ($M)": round(float(r["est_premium"]) / 1_000_000.0, 2),
                            "Sentimiento": sentiment,
                            "raw_prem": float(r["est_premium"])
                        })
            except Exception:
                continue
                
        if not all_unusual:
            return pd.DataFrame()
            
        res_df = pd.DataFrame(all_unusual)
        return res_df.sort_values(by="raw_prem", ascending=False).reset_index(drop=True)
    except Exception as e:
        print(f"Error escaneando opciones para {clean_ticker}: {e}")
        return pd.DataFrame()


def scan_multiticker_unusual_flow(tickers: list[str], min_v_oi: float = 1.5, min_premium: float = 100_000) -> pd.DataFrame:
    """Escanea una lista completa de acciones buscando actividad inusual consolidada."""
    all_dfs = []
    for sym in tickers:
        df_sym = scan_single_stock_unusual_options(sym, min_v_oi=min_v_oi, min_premium=min_premium, max_expirations=3)
        if not df_sym.empty:
            all_dfs.append(df_sym)
            
    if not all_dfs:
        return pd.DataFrame()
        
    final_df = pd.concat(all_dfs, ignore_index=True)
    return final_df.sort_values(by="raw_prem", ascending=False).reset_index(drop=True)
