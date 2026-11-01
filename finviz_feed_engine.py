"""
TradingVolt • Finviz Live Screener & Fundamental Feed Engine
============================================================
Powered by finvizfinance + Direct Resilient Parser for Finviz 2026 Layout.
Features:
1. Live Signals (Top Gainers, 52w New Highs, Unusual Volume, Breakouts, Most Volatile).
2. Deep Fundamentals 360° (P/E, Forward P/E, Short Float %, Institutional Own %, Target Price).
3. Insider Transactions & Real-time Financial News Feeds.
4. Instant Radar Synchronization with Cross-Desk Matrix & GEX.
"""

import os
import json
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
import bs4
import pandas as pd

# Try import finvizfinance for Quotes and Groups
try:
    import finvizfinance
    from finvizfinance.quote import finvizfinance as FinvizQuote
    from finvizfinance.group.overview import Overview as FinvizGroupOverview
    from finvizfinance.group.performance import Performance as FinvizGroupPerformance
    FINVIZ_FINANCE_AVAILABLE = True
except ImportError:
    FINVIZ_FINANCE_AVAILABLE = False
    FinvizQuote = None
    FinvizGroupOverview = None
    FinvizGroupPerformance = None

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / ".quant_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SIGNALS_CACHE_FILE = CACHE_DIR / "finviz_signals_cache.json"

FINVIZ_SIGNALS_MAP = {
    "🚀 Top Gainers (Máximas Ganancias)": "ta_topgainers",
    "👑 New 52-Week Highs (Rupturas de Máximos)": "ta_newhigh",
    "🌊 Unusual Volume (Volumen Inusual Institucional)": "ta_unusualvolume",
    "⚡ Multiple Tops / Breakouts (Rupturas de Resistencia)": "ta_p_multipletop",
    "🌪️ Most Volatile (Líderes de Volatilidad Intradía)": "ta_mostvolatile",
    "🎯 Most Active (Mayor Volumen Operado)": "ta_mostactive",
    "💎 Oversold RSI (< 30 Rebote Técnico)": "ta_oversold",
    "🔥 Upgrades / Calificaciones Positivas": "n_upgrades"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

def fetch_finviz_screener_tickers(signal_key: str = "ta_topgainers", max_pages: int = 2) -> List[str]:
    """
    Extrae los tickers de la señal oficial de Finviz en tiempo real (< 1.5s).
    Compatible con la estructura HTML moderna de Finviz 2026.
    """
    tickers = []
    seen = set()
    for p in range(max_pages):
        r_offset = p * 20 + 1
        url = f"https://finviz.com/screener.ashx?v=111&s={signal_key}&r={r_offset}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                break
            soup = bs4.BeautifulSoup(resp.text, "html.parser")
            new_in_page = 0
            for a in soup.find_all("a"):
                href = a.get("href", "")
                if "/quote?t=" in href or "quote.ashx?t=" in href:
                    parsed = urllib.parse.urlparse(href)
                    qs = urllib.parse.parse_qs(parsed.query)
                    t_val = qs.get("t", [None])[0]
                    if t_val and t_val not in seen and len(t_val) <= 6:
                        t_clean = t_val.strip().upper().replace(".", "-")
                        seen.add(t_clean)
                        tickers.append(t_clean)
                        new_in_page += 1
            if new_in_page == 0:
                break
        except Exception as e:
            print(f"[FinvizEngine] Error fetching {signal_key} page {p}: {e}")
            break
    return tickers

def get_finviz_signal_candidates(signal_name: str, force_refresh: bool = False, max_pages: int = 2) -> List[str]:
    """
    Carga los tickers de una señal de Finviz con caché de 15 minutos en disco.
    """
    sig_code = FINVIZ_SIGNALS_MAP.get(signal_name, "ta_topgainers")
    now_ts = time.time()
    
    cache_store = {}
    if SIGNALS_CACHE_FILE.exists() and not force_refresh:
        try:
            with open(SIGNALS_CACHE_FILE, "r", encoding="utf-8") as f:
                cache_store = json.load(f)
            cached_item = cache_store.get(sig_code)
            if cached_item and (now_ts - cached_item.get("timestamp", 0)) < 900.0:
                return cached_item.get("tickers", [])
        except Exception:
            cache_store = {}

    tickers = fetch_finviz_screener_tickers(sig_code, max_pages=max_pages)
    if tickers:
        cache_store[sig_code] = {
            "timestamp": now_ts,
            "signal_name": signal_name,
            "tickers": tickers
        }
        try:
            with open(SIGNALS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache_store, f, indent=2)
        except Exception:
            pass
    return tickers

def get_finviz_fundamental_profile(ticker: str) -> Dict[str, Any]:
    """
    Obtiene métricas fundamentales enriquecidas de Finviz (Short Float, P/E, EPS, etc.).
    """
    if not FINVIZ_FINANCE_AVAILABLE or not FinvizQuote:
        return {}
    try:
        stock = FinvizQuote(ticker.strip().upper().replace("-", "."))
        fund = stock.ticker_fundament() or {}
        desc = stock.ticker_description() or ""
        return {
            "Company": fund.get("Company", ""),
            "Sector": fund.get("Sector", ""),
            "Industry": fund.get("Industry", ""),
            "Market Cap": fund.get("Market Cap", "N/A"),
            "P/E": fund.get("P/E", "N/A"),
            "Forward P/E": fund.get("Forward P/E", "N/A"),
            "PEG": fund.get("PEG", "N/A"),
            "Short Float": fund.get("Short Float", "N/A"),
            "Inst Own": fund.get("Inst Own", "N/A"),
            "Insider Own": fund.get("Insider Own", "N/A"),
            "RSI (14)": fund.get("RSI (14)", "N/A"),
            "Target Price": fund.get("Target Price", "N/A"),
            "52W Range": fund.get("52W Range", "N/A"),
            "Description": desc
        }
    except Exception as e:
        return {"error": str(e)}

def get_finviz_insider_trades(ticker: str) -> Optional[pd.DataFrame]:
    """
    Devuelve las transacciones de insiders de Finviz.
    """
    if not FINVIZ_FINANCE_AVAILABLE or not FinvizQuote:
        return None
    try:
        stock = FinvizQuote(ticker.strip().upper().replace("-", "."))
        df = stock.ticker_inside_trader()
        return df if (df is not None and not df.empty) else None
    except Exception:
        return None

def get_finviz_news(ticker: str) -> Optional[pd.DataFrame]:
    """
    Devuelve las noticias financieras en tiempo real de Finviz.
    """
    if not FINVIZ_FINANCE_AVAILABLE or not FinvizQuote:
        return None
    try:
        stock = FinvizQuote(ticker.strip().upper().replace("-", "."))
        df = stock.ticker_news()
        return df if (df is not None and not df.empty) else None
    except Exception:
        return None
