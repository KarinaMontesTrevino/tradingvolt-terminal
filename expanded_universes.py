"""
TradingVolt Institutional Universe Engine
Expands the trading universe to:
- S&P 500 Completo (503 acciones)
- Dow Jones 30 Completo (30 acciones)
- Nasdaq 100 Completo (103 acciones)
- S&P 400 Mid-Cap Growth (400 acciones)
- S&P 600 Small-Cap Momentum (603 acciones)
- S&P 1500 Composite (1,506 acciones)
- Russell 2000 Completo (~2,075 acciones)
- Nasdaq Composite Líquido (~3,258 acciones)
- US Broad Liquid Market (+1,800 acciones S&P 1500 + NDX + TML)
- Master Total US Market (~3,500+ acciones consolidadas)
- Live Real-Time Market Movers Engine (Top Gainers, Pre-Market Movers & Gappers en vivo)
"""

import json
import os
import time
import urllib.request
from typing import Dict, List, Tuple

from leaders_universe import TML_331_TICKERS
try:
    from pure_momentum_universe import PURE_MOMENTUM_231_TICKERS, PURE_MOMENTUM_205_TICKERS
except Exception:
    from pure_momentum_universe import PURE_MOMENTUM_205_TICKERS
    PURE_MOMENTUM_231_TICKERS = PURE_MOMENTUM_205_TICKERS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar archivos de caché locales
SP1500_PATH = os.path.join(BASE_DIR, "sp1500_cache.json")
NDX_PATH = os.path.join(BASE_DIR, "ndx_cache.json")
DOW30_PATH = os.path.join(BASE_DIR, "dow30_cache.json")
RUSSELL2000_PATH = os.path.join(BASE_DIR, "russell2000_cache.json")
NASDAQ_COMPOSITE_PATH = os.path.join(BASE_DIR, "nasdaq_composite_cache.json")

SP500_COMPLETE_TICKERS = []
SP400_MIDCAP_TICKERS = []
SP600_SMALLCAP_TICKERS = []
NASDAQ100_COMPLETE_TICKERS = []
DOW30_COMPLETE_TICKERS = []
RUSSELL2000_COMPLETE_TICKERS = []
NASDAQ_COMPOSITE_COMPLETE_TICKERS = []

try:
    if os.path.exists(SP1500_PATH):
        with open(SP1500_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            SP500_COMPLETE_TICKERS = data.get("sp500", [])
            SP400_MIDCAP_TICKERS = data.get("sp400", [])
            SP600_SMALLCAP_TICKERS = data.get("sp600", [])
except Exception as e:
    print(f"Error cargando sp1500_cache.json: {e}")

try:
    if os.path.exists(NDX_PATH):
        with open(NDX_PATH, "r", encoding="utf-8") as f:
            NASDAQ100_COMPLETE_TICKERS = json.load(f)
except Exception as e:
    print(f"Error cargando ndx_cache.json: {e}")

try:
    if os.path.exists(DOW30_PATH):
        with open(DOW30_PATH, "r", encoding="utf-8") as f:
            DOW30_COMPLETE_TICKERS = json.load(f)
except Exception as e:
    print(f"Error cargando dow30_cache.json: {e}")

try:
    if os.path.exists(RUSSELL2000_PATH):
        with open(RUSSELL2000_PATH, "r", encoding="utf-8") as f:
            RUSSELL2000_COMPLETE_TICKERS = json.load(f)
except Exception as e:
    print(f"Error cargando russell2000_cache.json: {e}")

try:
    if os.path.exists(NASDAQ_COMPOSITE_PATH):
        with open(NASDAQ_COMPOSITE_PATH, "r", encoding="utf-8") as f:
            NASDAQ_COMPOSITE_COMPLETE_TICKERS = json.load(f)
except Exception as e:
    print(f"Error cargando nasdaq_composite_cache.json: {e}")

# Fallbacks si no existen los archivos
if not DOW30_COMPLETE_TICKERS:
    DOW30_COMPLETE_TICKERS = [
        "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS",
        "GS", "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK",
        "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"
    ]

if not SP500_COMPLETE_TICKERS:
    SP500_COMPLETE_TICKERS = [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "JPM", "V",
        "UNH", "XOM", "MA", "PG", "JNJ", "HD", "COST", "ABBV", "MRK", "CVX",
        "CRM", "AMD", "BAC", "NFLX", "KO", "PEP", "WMT", "LIN", "TMO", "DIS"
    ]

if not NASDAQ100_COMPLETE_TICKERS:
    NASDAQ100_COMPLETE_TICKERS = [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "ASML",
        "NFLX", "AMD", "PEP", "LIN", "AZN", "CSCO", "TMUS", "ADBE", "QCOM", "TXN",
        "INTU", "AMGN", "ISRG", "CMCSA", "HON", "BKNG", "VRTX", "PANW", "SBUX", "MDLZ"
    ]

# S&P 1500 consolidado (S&P 500 + S&P 400 MidCap + S&P 600 SmallCap)
SP1500_COMPLETE_TICKERS = sorted(list(set(
    SP500_COMPLETE_TICKERS +
    SP400_MIDCAP_TICKERS +
    SP600_SMALLCAP_TICKERS
)))

# Tickers adicionales de alta actividad institucional y movers
EXTRA_ACTIVE_MOVERS = ['XHG', 'VET', 'TIC', 'SPT', 'SITC', 'PAR', 'OSPN', 'MAX', 'INN', 'GLND', 'EVH', 'EVER', 'ESRT', 'BXC', 'BKYI', 'BETR', 'SKWD', 'PNTG', 'PAGP', 'KRP', 'GLBE', 'PUSH', 'GPUS', 'FLXR', 'EWZS', 'CBRX', 'WGS', 'VRDN', 'TNGX', 'ORIC', 'MLYS', 'METC', 'IONS', 'HHH', 'AIOK', 'VERX', 'STNE', 'REAL', 'PICS', 'ODD', 'OCTV', 'HPK', 'HIPO', 'BRBR', 'BHC', 'ARHS', 'ZIM', 'XLAB', 'WTM', 'WIT', 'WCN', 'UGP', 'TW', 'TRAX', 'TEVA', 'TAK', 'SPOT', 'SONY', 'SMA', 'SLN', 'SHEL', 'SGRY', 'SBS', 'RXRX', 'RPRX', 'RPD', 'RELX', 'QTEX', 'PBR-A', 'PBA', 'PAGS', 'PACB', 'NU', 'NAUT', 'MANE', 'KOS', 'IRON', 'IDT', 'HMC', 'HLN', 'GFL', 'FMX', 'FCNCA', 'E', 'DEO', 'CYPH', 'CBZ', 'BZ', 'BUD', 'BBD', 'ATEC', 'ASAN', 'ARX', 'ABEV', 'SAP', 'NICE', 'NCNO', 'LOGI', 'GIB', 'DSGX', 'DOX', 'AAOI', 'AEHR', 'ALM', 'AMRZ', 'AVBP', 'BHVN', 'BLZE', 'BRUN', 'BTDR', 'CBRS', 'CCC', 'CLS', 'DYN', 'EROC', 'FCEL', 'FIGR', 'HUT', 'IAG', 'INFQ', 'MLTX', 'OUST', 'POET', 'RARE', 'SNDX', 'TECK', 'WYFI', 'XE']

US_BROAD_MARKET_TICKERS = sorted(list(set(
    SP1500_COMPLETE_TICKERS +
    NASDAQ100_COMPLETE_TICKERS +
    DOW30_COMPLETE_TICKERS +
    TML_331_TICKERS +
    PURE_MOMENTUM_205_TICKERS +
    EXTRA_ACTIVE_MOVERS
)))

# Universo Maestro Total del Mercado Estadounidense (S&P 1500 + Russell 2000 + Nasdaq Composite + Dow 30 + TML)
US_MASTER_TOTAL_MARKET_TICKERS = sorted(list(set(
    SP1500_COMPLETE_TICKERS +
    DOW30_COMPLETE_TICKERS +
    NASDAQ100_COMPLETE_TICKERS +
    RUSSELL2000_COMPLETE_TICKERS +
    NASDAQ_COMPOSITE_COMPLETE_TICKERS +
    TML_331_TICKERS +
    PURE_MOMENTUM_205_TICKERS +
    EXTRA_ACTIVE_MOVERS
)))

# Universo High Momentum & Liquid Growth
HIGH_MOMENTUM_EXPANDED_TICKERS = sorted(list(set(
    TML_331_TICKERS +
    PURE_MOMENTUM_205_TICKERS +
    NASDAQ100_COMPLETE_TICKERS +
    [t for t in SP400_MIDCAP_TICKERS[:150]] +
    [t for t in SP600_SMALLCAP_TICKERS[:150]]
)))

# =====================================================================
# MOTOR DINÁMICO DE MERCADO EN VIVO (LIVE MOVERS & GAP-UPS SCANNER)
# =====================================================================
_LIVE_CACHE = {
    "timestamp": 0,
    "tickers": [],
    "meta": {}
}

def fetch_live_market_movers(force_refresh: bool = False, min_price: float = 1.5, min_vol: int = 50_000) -> Tuple[List[str], Dict[str, dict]]:
    """
    Consulta en tiempo real los Top Gainers, Pre-Market Movers, Most Actives 
    y High Growth Small Caps en todo el mercado estadounidense (NYSE, NASDAQ, AMEX).
    Utiliza caché en memoria de 120 segundos para evitar límites de tasa.
    """
    global _LIVE_CACHE
    now = time.time()
    
    # Reutilizar caché si tiene menos de 2 minutos
    if not force_refresh and _LIVE_CACHE["tickers"] and (now - _LIVE_CACHE["timestamp"]) < 120:
        return _LIVE_CACHE["tickers"], _LIVE_CACHE["meta"]
        
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    screeners = [
        "day_gainers",
        "most_actives",
        "aggressive_small_caps",
        "growth_technology_stocks",
        "small_cap_gainers"
    ]
    
    all_tickers = set()
    ticker_meta = {}
    
    for scr in screeners:
        try:
            url = f"https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&lang=en-US&region=US&scrIds={scr}&count=100"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                quotes = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
                for q in quotes:
                    sym = q.get("symbol", "").strip().upper()
                    if sym and "^" not in sym and "=" not in sym and not sym.endswith("W") and len(sym) <= 5:
                        reg_price = q.get("regularMarketPrice")
                        pre_price = q.get("preMarketPrice")
                        post_price = q.get("postMarketPrice")
                        price = pre_price or reg_price or post_price or 0.0
                        
                        reg_chg = q.get("regularMarketChangePercent")
                        pre_chg = q.get("preMarketChangePercent")
                        post_chg = q.get("postMarketChangePercent")
                        chg_pct = pre_chg if pre_chg is not None else (reg_chg if reg_chg is not None else (post_chg or 0.0))
                        
                        vol = q.get("regularMarketVolume") or q.get("averageDailyVolume10Day") or 0
                        
                        if price >= min_price and vol >= min_vol:
                            all_tickers.add(sym)
                            ticker_meta[sym] = {
                                "price": float(price),
                                "change_pct": float(chg_pct),
                                "volume": int(vol),
                                "name": q.get("shortName") or q.get("longName") or sym,
                                "market_cap": q.get("marketCap", 0),
                                "exchange": q.get("fullExchangeName", "US"),
                                "screener_origin": scr
                            }
        except Exception:
            continue
            
    if all_tickers:
        ticker_list = sorted(list(all_tickers), key=lambda x: ticker_meta.get(x, {}).get("change_pct", 0), reverse=True)
        _LIVE_CACHE = {
            "timestamp": now,
            "tickers": ticker_list,
            "meta": ticker_meta
        }
        return ticker_list, ticker_meta
        
    fallback = HIGH_MOMENTUM_EXPANDED_TICKERS[:150]
    return fallback, {}

def get_premarket_top_gappers(min_gap: float = 2.0, limit: int = 100) -> Tuple[List[str], Dict[str, dict]]:
    """Filtra específicamente las acciones que están haciendo Gap Up positivo en vivo."""
    tickers, meta = fetch_live_market_movers()
    gappers = []
    gapper_meta = {}
    for t in tickers:
        m = meta.get(t, {})
        chg = m.get("change_pct", 0.0)
        if chg >= min_gap:
            gappers.append(t)
            gapper_meta[t] = m
    return gappers[:limit], gapper_meta
