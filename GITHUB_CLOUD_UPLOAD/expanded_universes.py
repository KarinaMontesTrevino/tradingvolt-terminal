"""
TradingVolt Institutional Universe Engine
Expands the trading universe from a static 469-ticker list to:
- S&P 500 Completo (503 acciones)
- Nasdaq 100 Completo (103 acciones)
- S&P 400 Mid-Cap Growth (400 acciones)
- S&P 600 Small-Cap Momentum (603 acciones)
- US Broad Liquid Market (+1,800 acciones S&P 1500 + NDX + TML)
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

# Cargar S&P 1500 de la caché local
SP1500_PATH = os.path.join(BASE_DIR, "sp1500_cache.json")
NDX_PATH = os.path.join(BASE_DIR, "ndx_cache.json")

SP500_COMPLETE_TICKERS = []
SP400_MIDCAP_TICKERS = []
SP600_SMALLCAP_TICKERS = []
NASDAQ100_COMPLETE_TICKERS = []

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

# Fallback si no existen los archivos
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

# Universo US Broad Market consolidado y deduplicado (+1,800 acciones líquidas)
# Tickers adicionales de alta actividad institucional y movers
EXTRA_ACTIVE_MOVERS = ['XHG', 'VET', 'TIC', 'SPT', 'SITC', 'PAR', 'OSPN', 'MAX', 'INN', 'GLND', 'EVH', 'EVER', 'ESRT', 'BXC', 'BKYI', 'BETR', 'SKWD', 'PNTG', 'PAGP', 'KRP', 'GLBE', 'PUSH', 'GPUS', 'FLXR', 'EWZS', 'CBRX', 'WGS', 'VRDN', 'TNGX', 'ORIC', 'MLYS', 'METC', 'IONS', 'HHH', 'AIOK', 'VERX', 'STNE', 'REAL', 'PICS', 'ODD', 'OCTV', 'HPK', 'HIPO', 'BRBR', 'BHC', 'ARHS', 'ZIM', 'XLAB', 'WTM', 'WIT', 'WCN', 'UGP', 'TW', 'TRAX', 'TEVA', 'TAK', 'SPOT', 'SONY', 'SMA', 'SLN', 'SHEL', 'SGRY', 'SBS', 'RXRX', 'RPRX', 'RPD', 'RELX', 'QTEX', 'PBR-A', 'PBA', 'PAGS', 'PACB', 'NU', 'NAUT', 'MANE', 'KOS', 'IRON', 'IDT', 'HMC', 'HLN', 'GFL', 'FMX', 'FCNCA', 'E', 'DEO', 'CYPH', 'CBZ', 'BZ', 'BUD', 'BBD', 'ATEC', 'ASAN', 'ARX', 'ABEV', 'SAP', 'NICE', 'NCNO', 'LOGI', 'GIB', 'DSGX', 'DOX', 'AAOI', 'AEHR', 'ALM', 'AMRZ', 'AVBP', 'BHVN', 'BLZE', 'BRUN', 'BTDR', 'CBRS', 'CCC', 'CLS', 'DYN', 'EROC', 'FCEL', 'FIGR', 'HUT', 'IAG', 'INFQ', 'MLTX', 'OUST', 'POET', 'RARE', 'SNDX', 'TECK', 'WYFI', 'XE']

US_BROAD_MARKET_TICKERS = sorted(list(set(
    SP500_COMPLETE_TICKERS +
    NASDAQ100_COMPLETE_TICKERS +
    SP400_MIDCAP_TICKERS +
    SP600_SMALLCAP_TICKERS +
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
                    # Filtro de símbolos válidos (acciones ordinarias y ADRs)
                    if sym and "^" not in sym and "=" not in sym and not sym.endswith("W") and len(sym) <= 5:
                        # Extraer precios de pre-market, mercado regular o after-hours
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
        except Exception as e:
            # Fallback tolerante si falla un screener
            continue
            
    # Si la consulta en vivo retornó resultados, actualizar la caché
    if all_tickers:
        ticker_list = sorted(list(all_tickers), key=lambda x: ticker_meta.get(x, {}).get("change_pct", 0), reverse=True)
        _LIVE_CACHE = {
            "timestamp": now,
            "tickers": ticker_list,
            "meta": ticker_meta
        }
        return ticker_list, ticker_meta
        
    # Si la API falló por red, retornar como fallback el High Momentum Basket
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

# ==========================================================
# 🌐 DEEPVUE UNIVERSE MASTER (752 ACCIONES LÍQUIDAS & TOP INDUSTRIAS)
# ==========================================================
DEEPVUE_UNIVERSE_752 = ['NU', 'INFY', 'AAPL', 'TSLA', 'PFE', 'CLF', 'PATH', 'PBR', 'VG', 'MRNA', 'SLB', 'KMI', 'KO', 'WMT', 'S', 'PLTR', 'ERIC', 'CCL', 'CCI', 'TNGX', 'HLN', 'CSX', 'PBR-A', 'MSFT', 'CSCO', 'CART', 'KDP', 'CRWD', 'DVN', 'GMAB', 'HAL', 'ACI', 'XP', 'HPQ', 'OXY', 'FIG', 'XOM', 'NOW', 'KVUE', 'PG', 'VLY', 'BMY', 'PR', 'PINS', 'DOW', 'BP', 'ROL', 'AMT', 'NTSK', 'CRBG', 'CRGY', 'MRK', 'GME', 'MNST', 'ROIV', 'CVX', 'KR', 'DT', 'AVTR', 'HST', 'IOVA', 'TXN', 'VFC', 'CSGP', 'COP', 'VTRS', 'QGEN', 'EQT', 'APA', 'CVE', 'RHI', 'ACN', 'LYFT', 'EQNR', 'DIS', 'PANW', 'ET', 'CNQ', 'SAIL', 'MO', 'CTSH', 'STNE', 'GFL', 'BRZE', 'GILD', 'MDT', 'MET', 'TALO', 'IBM', 'ASST', 'AI', 'CRM', 'FOXA', 'FAST', 'RBLX', 'KMB', 'TEVA', 'COLB', 'CHWY', 'EQH', 'BBWI', 'JNJ', 'U', 'PTEN', 'KSS', 'TENB', 'OSCR', 'AIG', 'SO', 'V', 'BAX', 'AMRX', 'CL', 'SHEL', 'NOV', 'ASAN', 'ABBV', 'RNG', 'MAT', 'PK', 'RXO', 'PAGS', 'KVYO', 'PENG', 'RY', 'DXC', 'CNC', 'BRK-B', 'M', 'VMRK', 'NDAQ', 'BEN', 'SHOP', 'EL', 'RBRK', 'RPRX', 'ZS', 'BBY', 'DHR', 'OTIS', 'GAP', 'SONY', 'RDY', 'BZ', 'UNH', 'AR', 'DHT', 'VSTM', 'FRSH', 'PAA', 'ZLAB', 'REAL', 'PM', 'BAH', 'EBAY', 'SWKS', 'PCOR', 'UNP', 'GTLB', 'AEO', 'JCI', 'SGRY', 'MAC', 'EMR', 'SLS', 'ROKU', 'UL', 'EOG', 'FTNT', 'TGT', 'PBF', 'SNOW', 'AMCR', 'RELX', 'RPD', 'ATEC', 'RRC', 'ZETA', 'DBX', 'IOT', 'EW', 'OVV', 'OKTA', 'ZM', 'SIRI', 'TRU', 'VRNS', 'ISRG', 'ASB', 'SBAC', 'LFST', 'GEHC', 'PAGP', 'EBC', 'WCN', 'NWSA', 'ZTS', 'FIGS', 'KD', 'MTCH', 'SUNB', 'LYB', 'AEP', 'Z', 'WM', 'PSX', 'HAS', 'USFD', 'RYAN', 'MA', 'SM', 'BOX', 'LION', 'OPCH', 'MAS', 'FRO', 'PEGA', 'CHKP', 'FTI', 'SU', 'OKE', 'ED', 'INTU', 'BZH', 'ABNB', 'CP', 'HOG', 'SSNC', 'EXLS', 'BRO', 'PEB', 'SPOT', 'FIVN', 'ADI', 'BUD', 'ETSY', 'DLTR', 'TAP', 'COST', 'VLO', 'BSY', 'FULT', 'XERS', 'BF-B', 'PAYX', 'DRH', 'LNG', 'LLY', 'CAI', 'TTE', 'MRSH', 'DDOG', 'FBP', 'SSL', 'WTRG', 'CME', 'BNY', 'CLBK', 'NOG', 'HLT', 'SLN', 'RELY', 'P', 'ESTC', 'WELL', 'HAFN', 'TAK', 'SAP', 'AMTM', 'EXEL', 'PCVX', 'CERT', 'AMGN', 'GO', 'TMO', 'EFX', 'CF', 'VNOM', 'CHYM', 'AMPL', 'TEAM', 'VRSK', 'ZBH', 'NE', 'DOCU', 'SYK', 'G', 'AWK', 'CHD', 'STZ', 'WDAY', 'NCNO', 'BJ', 'CTAS', 'DG', 'MTDR', 'WRBY', 'EC', 'SPGI', 'NRIX', 'BGC', 'FROG', 'RLAY', 'TECH', 'RSG', 'ROST', 'SHO', 'CBOE', 'DINO', 'ARQT', 'AJG', 'GLBE', 'NAVN', 'AVAH', 'TNDM', 'LMT', 'ALKT', 'BALL', 'ALLE', 'TTEK', 'AXTA', 'OTEX', 'LW', 'BTSG', 'CI', 'FA', 'FANG', 'PGR', 'FBIN', 'CVBF', 'A', 'DFTX', 'LOGI', 'SIGI', 'APLE', 'ADMA', 'NTAP', 'TTAN', 'ARX', 'VIR', 'RCL', 'AVPT', 'PBI', 'SLDE', 'GH', 'LIN', 'CAH', 'DNOW', 'PNW', 'CB', 'CDW', 'ADP', 'SOLV', 'PLNT', 'RLJ', 'OLLI', 'SHAK', 'AAP', 'PD', 'CCEP', 'DOCS', 'W', 'PTC', 'UCB', 'TREX', 'HNGE', 'WAY', 'HTFL', 'PRGO', 'WLTH', 'CNK', 'MUR', 'HALO', 'DV', 'ZION', 'OCTV', 'NTNX', 'CNX', 'SFNC', 'BKH', 'VRSN', 'IFF', 'SWK', 'TRI', 'MPC', 'PACS', 'APPN', 'XNCR', 'UNM', 'BSP', 'ACHC', 'TRMB', 'ANF', 'HMC', 'MSI', 'EPAM', 'QDEL', 'TDC', 'FTS', 'POOL', 'VEEV', 'KBR', 'MAR', 'PHG', 'MFC', 'SNN', 'TW', 'GDDY', 'BDX', 'INGM', 'TRV', 'ADSK', 'CON', 'PFG', 'MOH', 'VIST', 'ILMN', 'FLYW', 'SBH', 'HRB', 'CNXC', 'QLYS', 'GLOB', 'VNT', 'PRCH', 'BMO', 'BL', 'HUM', 'IT', 'LIFE', 'SDRL', 'WMG', 'VRDN', 'VSXY', 'ELV', 'COR', 'NUE', 'ROP', 'DK', 'ALL', 'KNTK', 'OLED', 'BWIN', 'QTWO', 'BIIB', 'VLTO', 'TRGP', 'LXP', 'ZYME', 'PSNL', 'RVTY', 'SEIC', 'PSN', 'WSM', 'NTRA', 'CNI', 'EYE', 'SOBO', 'FTDR', 'EXPE', 'BR', 'EWBC', 'MGNI', 'OGN', 'TCBI', 'CUBI', 'SONO', 'LDOS', 'FFBC', 'RMD', 'NIQ', 'HCA', 'BILL', 'ICLR', 'CBZ', 'HQY', 'TRMD', 'ELF', 'SN', 'SITE', 'FTRE', 'NICE', 'LAUR', 'RLI', 'EXPD', 'UBSI', 'AME', 'DEO', 'PBA', 'MKTX', 'STNG', 'IQV', 'LPX', 'WSBC', 'NWS', 'GKOS', 'ENOV', 'OUT', 'DGX', 'IMAX', 'MANH', 'AMN', 'INTA', 'APD', 'AGIO', 'EWTX', 'WAT', 'VCYT', 'INSW', 'TS', 'WING', 'CVLT', 'KFY', 'PARR', 'HWC', 'RAMP', 'DOX', 'SBLK', 'LNTH', 'ACA', 'HUBS', 'ALKS', 'OPLN', 'SIG', 'WIX', 'WKC', 'TRAX', 'EFOR', 'BNS', 'HZO', 'HSIC', 'VRTX', 'STLD', 'CRL', 'ASO', 'WK', 'EHC', 'RH', 'TBBB', 'CHRD', 'SWX', 'VOYA', 'HAE', 'TD', 'HURN', 'AVY', 'PRCT', 'MNDY', 'IEX', 'CVI', 'RGR', 'URBN', 'ACIW', 'SYNA', 'EDU', 'YOU', 'GWRE', 'RAL', 'PVH', 'MMSI', 'CBC', 'SMG', 'FOX', 'VAL', 'CDNA', 'GRMN', 'BMI', 'WST', 'LTC', 'PKG', 'SNX', 'ECO', 'ALRM', 'COKE', 'CXT', 'SMA', 'HP', 'WHD', 'CBRL', 'R', 'KTB', 'BUSE', 'E', 'PRVA', 'VIRT', 'LH', 'TDW', 'JXN', 'CWST', 'ZG', 'CNO', 'WEX', 'GFF', 'UTHR', 'CATY', 'LIND', 'MCK', 'FFIV', 'DVA', 'CCK', 'APPF', 'ITGR', 'UNFI', 'INSP', 'KMPR', 'KNSA', 'GRAL', 'PCRX', 'LIVN', 'PGNY', 'STE', 'PAY', 'BPOP', 'TYL', 'NWE', 'MSCI', 'URI', 'SEZL', 'CMBT', 'ULTA', 'FDS', 'WTW', 'TTC', 'AVNT', 'RNR', 'REGN', 'KOD', 'PAYC', 'WSFS', 'KYMR', 'NATL', 'MAZE', 'TFX', 'SYRE', 'HHH', 'GSAT', 'LPG', 'VCEL', 'ATRC', 'MMS', 'GEF', 'CM', 'RHP', 'AZTA', 'ZIM', 'ANDG', 'FIVE', 'SAM', 'MRX', 'THC', 'GCT', 'PCTY', 'IRTC', 'DLB', 'MEOH', 'BLKB', 'ZBRA', 'CLH', 'UHS', 'CHEF', 'SPSC', 'MSGS', 'SLF', 'CASY', 'ASH', 'MANE', 'FCN', 'PTGX', 'EG', 'INDB', 'SAIC', 'SXT', 'VCTR', 'MUSA', 'HNI', 'GIB', 'AMG', 'NSIT', 'AIZ', 'NDSN', 'EXPO', 'LGND', 'AFG', 'PAG', 'TX', 'FMX', 'PRGS', 'SR', 'RGA', 'TNET', 'UNF', 'BAP', 'DSGX', 'CACI', 'CFR', 'ZD', 'XRPN', 'MATX', 'TNK', 'ONC', 'MEDP', 'WTS', 'DAVE', 'IMO', 'AGYS', 'FCNCA', 'CPAY', 'MORN', 'ICUI', 'TM', 'SLAB', 'PLMR', 'DGII', 'CVSA', 'ARCB', 'RS', 'MCY', 'SUNC', 'THG', 'CIB', 'AAMI', 'SUN', 'ADUS', 'GWW', 'MSGE', 'PSMT', 'MTD', 'LOPE', 'NHC', 'HCI', 'ERIE', 'BIO', 'NIC', 'CHE', 'JOYY', 'IPAR', 'IDT', 'CRAI', 'IDCC', 'NUTX', 'DAC', 'AZO', 'NEU', 'IOSP', 'UFPT', 'KOF', 'DDS', 'BH', 'BH-A', 'GHC', 'WTM', 'BRK-A']

# ==========================================================
# 🚀 MOMENTUM LEADERS (186 ACCIONES - SUSTAINED MOMENTUM & RS)
# ==========================================================
MOMENTUM_LEADERS_186 = ['ABCL', 'ACN', 'AGYS', 'ALRM', 'ALVO', 'AMN', 'AMPL', 'ANF', 'APA', 'APPN', 'ARHS', 'ASAN', 'ASO', 'ASST', 'ATRC', 'AVPT', 'AVTR', 'BBD', 'BBWI', 'BHC', 'BL', 'BLKB', 'BOX', 'BRBR', 'BRO', 'BRZE', 'BSP', 'BSY', 'BTE', 'CAI', 'CART', 'CBLL', 'CBOE', 'CBRL', 'CCI', 'CCL', 'CDNA', 'COTY', 'CRAI', 'CRL', 'CRM', 'CRWD', 'CSGP', 'CTSH', 'CVI', 'CXM', 'CXT', 'DOCS', 'DOCU', 'DT', 'DXC', 'ECO', 'EFOR', 'EFX', 'EPAM', 'ESTC', 'ETSY', 'EXLS', 'EXPO', 'FCN', 'FDS', 'FIGS', 'FIVN', 'FIZZ', 'FRSH', 'G', 'GCT', 'GIB', 'GLOB', 'GMAB', 'GRAL', 'GTLB', 'GWRE', 'HAE', 'HALO', 'HAS', 'HCSG', 'HIPO', 'HNGE', 'HPK', 'HSTM', 'HTFL', 'HUBS', 'HURN', 'HZO', 'IBTA', 'IDT', 'INTA', 'INTR', 'INTU', 'IOVA', 'IT', 'KD', 'KOD', 'KSS', 'KVYO', 'LIFE', 'LIND', 'LW', 'LZ', 'MANE', 'MANH', 'MAT', 'MNDY', 'MPC', 'MRNA', 'MSTR', 'NAVN', 'NIQ', 'NOW', 'NSIT', 'NTRA', 'NTSK', 'ODD', 'OKTA', 'OMER', 'OPCH', 'OTEX', 'P', 'PAGS', 'PAYC', 'PBR', 'PBR-A', 'PCOR', 'PCRX', 'PCTY', 'PD', 'PICS', 'PLNT', 'PLSE', 'PLTR', 'POOL', 'PRGO', 'PSIX', 'PTC', 'QLYS', 'QTWO', 'RBRK', 'REAL', 'RELX', 'REPX', 'RHI', 'RNG', 'ROP', 'RPD', 'RSKD', 'RVTY', 'RXO', 'SAM', 'SBS', 'SDGR', 'SEZL', 'SG', 'SLDE', 'SSL', 'STNE', 'STZ', 'SYNA', 'TBBB', 'TEAM', 'TEM', 'TENB', 'TRAX', 'TRI', 'TRU', 'TRUP', 'TTAN', 'TW', 'TWST', 'TXG', 'USDE', 'UTHR', 'VEEV', 'VEON', 'VERX', 'VFC', 'VIA', 'VMRK', 'WING', 'WIT', 'WIX', 'WK', 'XP', 'ZBRA', 'ZETA', 'ZS']

# ==========================================================
# 💧 VOLUME DRY UP (160 ACCIONES - VDU & RMV TIGHT COMPRESSION)
# ==========================================================
VOLUME_DRY_UP_160 = ['ADI', 'ADT', 'AKRE', 'ALL', 'AMDD', 'APEI', 'ARKB', 'ASO', 'ASTH', 'AZO', 'BALT', 'BCI', 'BITO', 'BITU', 'BITX', 'BKMI', 'BOW', 'BSX', 'CBRL', 'CBRZ', 'CBZ', 'CCB', 'CCK', 'CERY', 'CGMU', 'CHWY', 'CMF', 'CRMG', 'CRNC', 'CRSR', 'CSL', 'CSV', 'CVS', 'DEC', 'DHT', 'DK', 'DMII', 'DRH', 'DRI', 'DSP', 'DUST', 'EDZ', 'ESRT', 'FAST', 'FDV', 'FLMI', 'FRO', 'FTMA', 'FXU', 'GGOV', 'GMED', 'GMEU', 'GRAL', 'GSK', 'GWRE', 'HALO', 'HIG', 'HLI', 'HYD', 'IALT', 'IBB', 'IBTH', 'ICE', 'IDNA', 'IDXX', 'IHF', 'ILMN', 'IMO', 'IOSP', 'IOVA', 'IREZ', 'JJSF', 'JMST', 'JOYY', 'KMPR', 'KRNT', 'KVUE', 'L', 'LMAT', 'LMUB', 'LPX', 'LYFT', 'M', 'MA', 'MAZE', 'MDT', 'MG', 'MGPI', 'MNDY', 'MNRO', 'MPC', 'MQ', 'MSFT', 'MTN', 'MUB', 'MUNI', 'NAT', 'NBIZ', 'NOMD', 'NRIX', 'NTNX', 'OAKM', 'OFIX', 'OSW', 'P', 'PAHC', 'PEG', 'PEP', 'PGNY', 'PGR', 'PLTU', 'PMI', 'PODD', 'PPG', 'PRCH', 'PRF', 'PRGO', 'PRGS', 'PRVA', 'PTIR', 'QDEL', 'RAMZ', 'REG', 'RIGL', 'RPC', 'RSKD', 'RVTY', 'RWL', 'SCHP', 'SFNC', 'SHM', 'SHOP', 'SKHZ', 'SMG', 'SNDQ', 'SPXU', 'SR', 'SUB', 'SWKS', 'TASK', 'TAXE', 'TDTF', 'THC', 'TME', 'TOST', 'TRMD', 'TSN', 'UNH', 'VCRM', 'VMD', 'VRDN', 'VRTX', 'VSTS', 'VSXY', 'VTEC', 'VTES', 'WMG', 'ZG', 'ZOCT', 'ZTS']

# ==========================================================
# ⚡ POWER 21 (69 ACCIONES - 21 EMA PULLBACK & ABSOLUTE STRENGTH)
# ==========================================================
POWER_21_69 = ['ADMA', 'AGL', 'AMC', 'APPF', 'ARXS', 'AZTA', 'BBD', 'BH', 'BIO', 'BLMN', 'BWLP', 'BXC', 'CACI', 'CCL', 'CHYM', 'CRCL', 'CRSR', 'CVI', 'DINO', 'FRO', 'FSLY', 'FTNT', 'GCT', 'GH', 'HP', 'ILMN', 'INSP', 'INSW', 'KMPR', 'KNTK', 'LIND', 'LPG', 'MDB', 'MEOH', 'MLAB', 'MPC', 'NAT', 'NEOG', 'NET', 'NTAP', 'NTNX', 'NTRA', 'OLLI', 'PANW', 'PAYS', 'PLTR', 'PRCH', 'PSX', 'QNST', 'QTEX', 'RCL', 'RDNT', 'RGEN', 'RGR', 'S', 'SHOP', 'SRZN', 'STAA', 'STGW', 'SWKS', 'TMO', 'TNK', 'TSLA', 'UFPT', 'VLO', 'WHD', 'WING', 'XERS', 'XNCR']

# ==========================================================
# 📅 WEEKLY STRENGTH (399 ACCIONES - WEEKLY HIGHS & MEDIUM-TERM RS)
# ==========================================================
WEEKLY_STRENGTH_399 = ['CART', 'RHI', 'CUBI', 'OSPN', 'EGBN', 'GMAB', 'CENTA', 'CHKP', 'BCPC', 'GBCI', 'R', 'RPD', 'BAH', 'COLB', 'NICE', 'SGRY', 'LMRI', 'QTWO', 'NE', 'SDRL', 'ACT', 'MSI', 'QLYS', 'WSFS', 'TALO', 'E', 'TCBI', 'PAA', 'VG', 'INTA', 'CNOB', 'BMI', 'DCOM', 'CRWD', 'MANH', 'S', 'KFY', 'EQNR', 'RYAN', 'DVN', 'HCSG', 'RSG', 'PAGP', 'SLB', 'ALRM', 'ZS', 'ROP', 'APPN', 'SPOT', 'VIST', 'EPAM', 'CVLT', 'ASB', 'LNG', 'TENB', 'CATY', 'UCB', 'RBRK', 'LMT', 'HFWA', 'GLOB', 'WCN', 'FIBK', 'EL', 'MTDR', 'PNFP', 'NET', 'KMI', 'BBY', 'SLDE', 'CBOE', 'BR', 'EFOR', 'HBNC', 'PBR-A', 'FULT', 'VLY', 'FIVN', 'IT', 'SAIL', 'QGEN', 'ISRG', 'OTEX', 'APA', 'CACI', 'NTSK', 'RELX', 'NDAQ', 'OXY', 'SSL', 'RPRX', 'FFBC', 'AJG', 'DAKT', 'CVBF', 'KELYA', 'EC', 'HOG', 'EBC', 'AMRX', 'HQY', 'PANW', 'BL', 'COP', 'BWLP', 'CNQ', 'ARHS', 'SWX', 'MMSI', 'D', 'WEX', 'NSIT', 'ANDG', 'KSS', 'SPT', 'NWBI', 'EWBC', 'EOG', 'RRC', 'GTE', 'FIG', 'WM', 'AGYS', 'CHRD', 'ESTC', 'ICLR', 'CTAS', 'AI', 'HAS', 'WDS', 'UNF', 'PCOR', 'CDW', 'PR', 'DOW', 'INSW', 'FSUN', 'FROG', 'AMPL', 'EXLS', 'CVX', 'HZO', 'G', 'NBBK', 'ED', 'JKHY', 'FNB', 'PLSE', 'NOG', 'BKH', 'ZBH', 'SPNT', 'RDWR', 'PHR', 'CME', 'ASC', 'OZK', 'AMN', 'PBR', 'ARLP', 'WTFC', 'RCEL', 'ACIW', 'UBSI', 'SM', 'TNET', 'LH', 'EQT', 'AWK', 'NCNO', 'BBT', 'HOPE', 'NU', 'BLKB', 'SSB', 'HPQ', 'GPRK', 'AR', 'BP', 'XOM', 'BSM', 'TRGP', 'NSP', 'PFS', 'BSY', 'BOX', 'VNT', 'WIX', 'NOW', 'KRP', 'IBM', 'LFST', 'RNST', 'ZION', 'OVV', 'TTEK', 'SONY', 'MITK', 'SAIC', 'NBTB', 'AUB', 'NWE', 'GKOS', 'SPGI', 'BVS', 'TRI', 'BCC', 'KNTK', 'TILE', 'THG', 'VNOM', 'HCA', 'SPSC', 'OKTA', 'FLYW', 'LIVN', 'INGM', 'BRZE', 'GH', 'AMAL', 'URI', 'HOMB', 'HTFL', 'PD', 'DBX', 'VEEV', 'APD', 'FA', 'TTAN', 'WLY', 'MUR', 'SMA', 'EFX', 'RMD', 'TW', 'MEDP', 'BLLN', 'SBH', 'CWST', 'ASAN', 'FTNT', 'LPG', 'WDAY', 'FMNB', 'BUSE', 'VCEL', 'TRU', 'GIB', 'DEO', 'WTRG', 'PAYC', 'IMAX', 'CUBE', 'PSA', 'EXR', 'CNMD', 'TOWN', 'TYL', 'ADP', 'VIA', 'MSCI', 'GEHC', 'BIIB', 'CBC', 'CNX', 'TTE', 'CIB', 'VERX', 'DGX', 'NIQ', 'BDX', 'KBR', 'ECO', 'LYB', 'CWT', 'DXC', 'MRSH', 'GTLB', 'AVTR', 'SAP', 'KVYO', 'HNGE', 'VAL', 'GWW', 'ZYME', 'SCSC', 'FANG', 'HPK', 'MD', 'GDDY', 'BAX', 'STE', 'OKE', 'ICE', 'INDB', 'LIN', 'TDC', 'STNG', 'TRMK', 'TEAM', 'SIBN', 'PTEN', 'INVX', 'FCF', 'PAYX', 'IFF', 'NTCT', 'PM', 'HNI', 'DIS', 'PCTY', 'SR', 'LION', 'TNK', 'PNTG', 'MPLX', 'SIRI', 'TAK', 'DOCU', 'DV', 'CRL', 'AGIO', 'ARDT', 'CRGY', 'VCYT', 'IQV', 'SU', 'SFNC', 'BBNX', 'CBZ', 'ABM', 'CERT', 'BLCO', 'ZD', 'CRM', 'IOT', 'TK', 'DHT', 'DLB', 'BILL', 'AVAH', 'TRMB', 'WAY', 'FDS', 'LSPD', 'CNXC', 'HUBS', 'HRB', 'HHH', 'SHEL', 'ADSK', 'KHC', 'DGII', 'HAFN', 'TFX', 'VSTM', 'UTHR', 'AVPT', 'MNDY', 'VLTO', 'NAVN', 'DEC', 'NTAP', 'KD', 'VSTS', 'HALO', 'DSGX', 'WRBY', 'M', 'PGR', 'GWRE', 'EXPO', 'BOBS', 'FRO', 'NTNX', 'CRSR', 'WLTH', 'SONO', 'GRAL', 'ATRC', 'RAMP', 'NEOG', 'PGNY', 'MH', 'PRGS', 'WK', 'EVAC', 'FRSH', 'SWKS', 'SEPN', 'DOCS', 'TRMD', 'DSP', 'AZTA', 'SLN', 'TD', 'ZIM', 'AFYA', 'PCRX']

# ==========================================================
# 🔥 HIGHEST VOLUME IPO (7 ACCIONES - HIGHEST VOLUME SINCE IPO DAY)
# ==========================================================
HV_IPO_7 = ['AIOK', 'CBRX', 'EWZS', 'FLXR', 'GMAB', 'GPUS', 'PUSH']

# ==========================================================
# 🛡️ AMEET RAI: 62.5% RS DAYS (191 ACCIONES - CORRECTIONS RESILIENCE)
# ==========================================================
AMEET_RAI_RS_DAYS_191 = ['AAPL', 'ABBV', 'ABEV', 'ABT', 'ACI', 'ACN', 'ADT', 'AES', 'AI', 'AIG', 'APA', 'AS', 'ASAN', 'ASST', 'AVTR', 'BA', 'BAX', 'BB', 'BBWI', 'BCE', 'BKYI', 'BMBL', 'BP', 'BRZE', 'BSX', 'BTE', 'BTI', 'BX', 'CAG', 'CARR', 'CCI', 'CCL', 'CELH', 'CFG', 'CHWY', 'CLF', 'CMCSA', 'CNP', 'CNQ', 'COMP', 'COP', 'COTY', 'COUR', 'CPRT', 'CRBG', 'CRH', 'CRM', 'CRWD', 'CSGP', 'CSX', 'CTSH', 'CVE', 'CVS', 'CVX', 'CX', 'DHT', 'DIS', 'DKNG', 'DOC', 'DOW', 'DT', 'DX', 'DXC', 'EIX', 'EQT', 'ERAS', 'ERIC', 'ET', 'EXC', 'FAST', 'FHN', 'FIG', 'FIS', 'FISV', 'FITB', 'FNB', 'FRSH', 'GEN', 'GENI', 'GGB', 'GIS', 'GSK', 'HAL', 'HBAN', 'HD', 'HLN', 'HPQ', 'HR', 'HRL', 'HST', 'IBM', 'IBN', 'INFY', 'INTR', 'INVH', 'IOVA', 'JBS', 'KDP', 'KEY', 'KHC', 'KKR', 'KMI', 'KVUE', 'KVYO', 'LEN', 'LEVI', 'LQDA', 'LUV', 'LYFT', 'M', 'MAT', 'MCD', 'MDLZ', 'MDT', 'MNST', 'MO', 'MSFT', 'NAUT', 'NCLH', 'NEE', 'NI', 'NKE', 'NOW', 'NTSK', 'O', 'ONB', 'OPCH', 'ORLY', 'OWL', 'OXY', 'PANW', 'PATH', 'PBR', 'PBR-A', 'PDD', 'PEP', 'PFE', 'PG', 'PINS', 'PLTR', 'PPL', 'PR', 'PTEN', 'PYPL', 'QGEN', 'RBLX', 'RF', 'RIG', 'RITM', 'RKT', 'ROIV', 'ROL', 'RUN', 'S', 'SAIQ', 'SBS', 'SBUX', 'SHEL', 'SHOP', 'SKYD', 'SLB', 'SLN', 'SLS', 'SNAP', 'SO', 'STNE', 'SWKS', 'TFC', 'TJX', 'TME', 'TOST', 'TSCO', 'TSLA', 'TU', 'TXN', 'UNH', 'V', 'VFC', 'VG', 'VICI', 'VISN', 'VLY', 'VSTM', 'VZ', 'WMT', 'WU', 'WY', 'XEL', 'XOM', 'XP', 'ZETA']

# ==========================================================
# 💧 AMEET RAI: DAILY LIQUIDITY (296 ACCIONES - VOLUME > 8M)
# ==========================================================
AMEET_RAI_DAILY_LIQUIDITY_296 = ['AAOI', 'AAPL', 'ABT', 'ACN', 'AES', 'AGG', 'AMAT', 'AMD', 'AMT', 'AMZN', 'APA', 'APH', 'APLD', 'AS', 'ASTS', 'ASX', 'AVGO', 'AVTR', 'AXTI', 'B', 'BA', 'BABA', 'BAC', 'BCS', 'BE', 'BEX', 'BIL', 'BKLN', 'BMNR', 'BMY', 'BND', 'BOIL', 'BP', 'BRZE', 'BSX', 'BX', 'C', 'CART', 'CBRS', 'CCI', 'CCL', 'CFG', 'CMCSA', 'CMG', 'CNP', 'CNQ', 'COHR', 'COIN', 'COP', 'CPB', 'CPRT', 'CRBG', 'CRCL', 'CRDO', 'CRWD', 'CRWV', 'CSCO', 'CSGP', 'CSX', 'CTSH', 'CVE', 'CVNA', 'CVX', 'DECK', 'DIS', 'DKNG', 'DOC', 'DOG', 'DOW', 'DRAM', 'DT', 'DVN', 'EEM', 'EFA', 'EQNR', 'EQT', 'ET', 'EWY', 'EWZ', 'EWZS', 'FCX', 'FIG', 'FIGR', 'FITB', 'FNB', 'FPS', 'FXI', 'GDX', 'GE', 'GFL', 'GILD', 'GIS', 'GLD', 'GLW', 'GM', 'GMAB', 'GME', 'GOOG', 'GOOGL', 'GOVT', 'GTX', 'HAL', 'HBAN', 'HDB', 'HDV', 'HIMS', 'HOOD', 'HPE', 'HPQ', 'HST', 'HWM', 'HYG', 'IBIT', 'IEF', 'IEFA', 'IEMG', 'IGV', 'INDA', 'INTC', 'INVH', 'IONQ', 'IREN', 'IUSB', 'IVZ', 'IWF', 'IWM', 'IYR', 'JAAA', 'JCPB', 'JD', 'JNK', 'JPST', 'KDP', 'KEY', 'KHC', 'KLAC', 'KMI', 'KO', 'KR', 'KRE', 'KVUE', 'KWEB', 'LBRT', 'LKQ', 'LQD', 'LRCX', 'LUV', 'LYFT', 'MBB', 'MCHP', 'MDLN', 'MDLZ', 'MDT', 'META', 'MINT', 'MNST', 'MO', 'MOS', 'MRK', 'MRNA', 'MRVL', 'MS', 'MSFT', 'MSTR', 'MU', 'MUB', 'MUU', 'MXL', 'NBIS', 'NCLH', 'NEE', 'NEM', 'NFLX', 'NKE', 'NLY', 'NOW', 'NTSK', 'NU', 'NVDA', 'NVDL', 'NVO', 'O', 'OKLO', 'ON', 'ONON', 'ORCL', 'OXY', 'PANW', 'PBR', 'PBR-A', 'PEP', 'PFE', 'PG', 'PINS', 'PLTR', 'PPL', 'PR', 'PSLV', 'PSQ', 'PYLD', 'PYPL', 'QCOM', 'QGEN', 'QQQ', 'REXR', 'RF', 'RHI', 'RKLB', 'ROIV', 'ROL', 'RSP', 'S', 'SAIL', 'SCHB', 'SCHD', 'SCHF', 'SCHG', 'SCHH', 'SCHW', 'SCHX', 'SCO', 'SDOW', 'SE', 'SGOV', 'SH', 'SHV', 'SJNK', 'SKHY', 'SLB', 'SLM', 'SLV', 'SMCI', 'SMH', 'SNDK', 'SNDQ', 'SOXL', 'SOXS', 'SOXX', 'SPCX', 'SPIB', 'SPTI', 'SPTL', 'SPXS', 'SPY', 'SPYM', 'SQQQ', 'SRLN', 'STM', 'T', 'TFC', 'TLT', 'TMUS', 'TNGX', 'TQQQ', 'TSCO', 'TSLA', 'TSLQ', 'TSM', 'TTMI', 'TXN', 'UBER', 'UDR', 'UMC', 'USHY', 'USO', 'UVXY', 'VCIT', 'VCSH', 'VEA', 'VFC', 'VICI', 'VO', 'VRT', 'VST', 'VTEB', 'VTRS', 'VWO', 'VXX', 'VZ', 'WDC', 'WFC', 'WMT', 'WY', 'XBI', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY', 'XOM', 'XP']

# ==========================================================
# 🚩 AMEET RAI: HIGH TIGHT FLAGS (12 ACCIONES - RUN >= 100% IN 20D)
# ==========================================================
AMEET_RAI_HTF_12 = ['MAGH', 'IRLA', 'FGC', 'BMBL', 'TJGC', 'KOD', 'MSGKW', 'SCAT', 'IPHX', 'SA40MA-NYSE', 'NH-NYSE', 'SA20MA-NYSE']

# ==========================================================
# 🌆 POST MARKET MOVERS (21 ACCIONES - AFTER-HOURS EARNINGS/NEWS)
# ==========================================================
POST_MARKET_MOVERS_21 = ['AIOK', 'TNGX', 'WGS', 'SNDX', 'VLY', 'CI', 'KNSA', 'ORIC', 'IONS', 'MLYS', 'HHH', 'BRBR', 'DNOW', 'LFST', 'VRDN', 'PCAR', 'METC', 'IOT', 'FICO', 'USDE', 'LYCA']

# ==========================================================
# ⚡ AMEET RAI: HV EDGE (45 ACCIONES - 1Y/IPO/EARNINGS VOL RECORD)
# ==========================================================
AMEET_RAI_HV_EDGE_45 = ['AIBN', 'AIOK', 'AMT', 'BOLT', 'CCI', 'CGCF', 'CTJL', 'CTMA', 'EAFH', 'EMAU', 'ENTL', 'EWZS', 'FCNCA', 'FLXR', 'GMAB', 'GMIE', 'GUAC', 'HJLY', 'IDJN', 'IEAG', 'JADB', 'JULC', 'LCIV', 'LEGO', 'LFAW', 'LTGR', 'LUNC', 'MAYC', 'OIM', 'POMG', 'PUSH', 'QJL', 'QMY', 'QQJN', 'QQMY', 'RBTX', 'RECI', 'S4-USA', 'SCJL', 'TIPD', 'TMTS', 'TPEI', 'XIII', 'XKRE', 'XLEM']

# ==========================================================
# 🌱 AMEET RAI: IPO LAST 1 YEAR (189 ACCIONES - RISK-ON BAROMETER)
# ==========================================================
AMEET_RAI_IPO_1YR_189 = ['AADX', 'ACCV', 'ADBT', 'ADIG', 'ADRX', 'AERO', 'AGBK', 'AIAI', 'AIB', 'AIBZ', 'AIOK', 'AKTS', 'ALMR', 'AMRO', 'AMSS', 'ANDG', 'APMD', 'APUR', 'ARXS', 'ATTO', 'AVEX', 'AVLN', 'AYA', 'AZIO', 'BBCI', 'BETA', 'BIOT', 'BLLN', 'BMM', 'BOBS', 'BOT', 'BPRE', 'BRUN', 'BRVE', 'BSP', 'BTGO', 'BXDC', 'CAST', 'CBC', 'CBRS', 'CCXI', 'CDNL', 'CHGA', 'CNXU', 'COAG', 'CSHR', 'CSQR', 'CTY', 'CVSA', 'CYAB', 'DMII', 'DPC', 'EDVA', 'EIKN', 'ELE', 'ELMT', 'EMAT', 'ENHA', 'EQPT', 'EROC', 'EROK', 'ETRA', 'EVMN', 'EXYN', 'FBDT', 'FDXF', 'FISN', 'FJET', 'FPS', 'FRNM', 'FRTT', 'FRVO', 'FSSL', 'GCDT', 'GENB', 'GIXI', 'GLAS', 'GLND', 'GLOO', 'GMRS', 'GMTL', 'GOOGM', 'GOOGN', 'GYGY', 'HAWK', 'HLSQ', 'HONA', 'HOS', 'HOST', 'HSLV', 'HUCK', 'IA', 'IAM', 'IEAG', 'INFQ', 'INIO', 'IOND', 'IPHX', 'IQMX', 'ITG', 'IVAI', 'JAN', 'JMKE', 'KARD', 'KBON', 'KLRA', 'LABT', 'LCLN', 'LFTO', 'LIFE', 'LIME', 'LMRI', 'LTGO', 'LYCA', 'LYNX', 'MAIR', 'MANE', 'MBGL', 'MDA', 'MDLN', 'MFP', 'MICC', 'MMED', 'MRLN', 'MWH', 'NAVN', 'NHP', 'NWCL', 'NXAT', 'NXTS', 'OBX', 'OCTV', 'ODTX', 'OFRM', 'OGG', 'OIG', 'ONEN', 'PAAI', 'PAYP', 'PBLS', 'PICS', 'PS', 'PSQL', 'PURR', 'Q', 'QMLS', 'QNT', 'QVCG', 'REF', 'RNA', 'SCAT', 'SCTX', 'SECZ', 'SHAZ', 'SKHY', 'SKYD', 'SMJF', 'SPCX', 'SPTX', 'SSMR', 'STDN', 'STLN', 'SUJA', 'SUNB', 'SUNC', 'SWMR', 'TCGX', 'TMTS', 'TRAX', 'TRXB', 'VCX', 'VGNT', 'VMET', 'VRXA', 'VSNT', 'VTIX', 'VYLR', 'WHK', 'WLTH', 'WSE', 'XE', 'XLAB', 'XMAX', 'XNDU', 'XTND', 'XZO', 'YFOR', 'YSS', 'YSWY']
