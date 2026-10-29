"""
================================================================================
TRADINGVOLT • LARGE-SCALE QUANTITATIVE DATA PIPELINE & VECTORIZED ENGINE
================================================================================
Arquitectura de Datos a Gran Escala para Procesamiento Vectorizado en Tiempo Real:
  1. Caché Multinivel (L1 RAM Vector Store + L2 Disco Comprimido Pickle) con TTL.
  2. Descarga Incremental por Lotes (Smart Delta Batching): solo descarga tickers
     faltantes o expirados usando multithreading de alta concurrencia.
  3. Cómputo Matricial Vectorizado (NumPy / Pandas C-Engine):
     - Cálculo simultáneo de métricas Intraday Strength (Gap, Vs Open, RVOL,
       Run Rate, % VWAP, RS 1M/3M, $Vol) sin bucles lentos.
     - Cálculo matricial JdK RS-Ratio y RS-Momentum multi-temporalidad (1H, 1D,
       1W, 1M) para Relative Rotation Graphs (RRG).
  4. Registro Centralizado de los Filtros Cuantitativos Actualizados (conecta
     Screener Cuantitativo, Radar Activo, Intraday Strength Watch y RRG Desk).
================================================================================
"""

import os
import time
import json
import math
import pickle
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

import screener_engine as engine
import expanded_universes as eu
try:
    import active_radar_engine as are
except ImportError:
    are = None

# Directorio de caché persistente L2
CACHE_DIR = Path(__file__).parent / "cache_store"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FILTER_RESULTS_CACHE_FILE = CACHE_DIR / "live_filter_results.json"

# Caché en memoria L1: {(period, interval): {"ts": float, "close": DataFrame, "open": DataFrame, "high": DataFrame, "low": DataFrame, "volume": DataFrame}}
_L1_MATRIX_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}
_PIPELINE_LOCK = threading.RLock()

# TTL por intervalo (segundos)
_TTL_MAP = {
    "5m": 120,
    "15m": 180,
    "1h": 300,
    "1d": 600,
    "1wk": 1800,
    "1mo": 3600
}

# Watchlist de líderes mostrada en los ejemplos RRG (MTM WL de la Semana)
MTM_WEEKLY_RRG_LEADERS = [
    "FIGS", "PAYC", "MPC", "PBF", "PSIX", "PLTR", "HALO", "CRWD", "NET", "AMD",
    "HPE", "ILMN", "CDNA", "FTNT", "OKTA", "PAYS", "ETON", "ANF", "EQNR", "BP",
    "INSW", "LPG", "DHT", "FRO", "NTAP", "EOG", "DVN", "APA"
]

# Mapa rápido de Sector e Industria para enriquecimiento instantáneo sin latencia de red
SECTOR_INDUSTRY_MAP = {
    "NVDA": ("Information Technology", "Semiconductors"),
    "AMD": ("Information Technology", "Semiconductors"),
    "AVGO": ("Information Technology", "Semiconductors"),
    "TSM": ("Information Technology", "Semiconductors"),
    "MU": ("Information Technology", "Semiconductors"),
    "KLAC": ("Information Technology", "Semiconductor Equipment"),
    "LRCX": ("Information Technology", "Semiconductor Equipment"),
    "AMAT": ("Information Technology", "Semiconductor Equipment"),
    "ARM": ("Information Technology", "Semiconductors"),
    "SMCI": ("Information Technology", "Computer Hardware"),
    "DELL": ("Information Technology", "Computer Hardware"),
    "HPE": ("Information Technology", "Computer Hardware"),
    "NTAP": ("Information Technology", "Data Storage"),
    "WDC": ("Information Technology", "Data Storage"),
    "SNDK": ("Information Technology", "Data Storage"),
    "PLTR": ("Information Technology", "AI & Big Data Software"),
    "CRWD": ("Information Technology", "Cybersecurity Software"),
    "PANW": ("Information Technology", "Cybersecurity Software"),
    "FTNT": ("Information Technology", "Cybersecurity Software"),
    "ZS": ("Information Technology", "Cybersecurity Software"),
    "OKTA": ("Information Technology", "Identity Security"),
    "NET": ("Information Technology", "Cloud & Edge Network"),
    "NOW": ("Information Technology", "Enterprise Software"),
    "MSFT": ("Information Technology", "Systems Software"),
    "ORCL": ("Information Technology", "Database & Cloud"),
    "APP": ("Information Technology", "AdTech Software"),
    "PAYC": ("Information Technology", "HR & Payroll Software"),
    "PAYS": ("Information Technology", "Payment Processing"),
    "IOT": ("Information Technology", "IoT Cloud Software"),
    "FICO": ("Information Technology", "Analytics Software"),
    "AAPL": ("Information Technology", "Consumer Tech"),
    "GOOGL": ("Communication Services", "Interactive Media"),
    "GOOG": ("Communication Services", "Interactive Media"),
    "META": ("Communication Services", "Social Media & AI"),
    "NFLX": ("Communication Services", "Streaming Entertainment"),
    "RDDT": ("Communication Services", "Digital Communities"),
    "ASTS": ("Communication Services", "Satellite Telecom"),
    "TMUS": ("Communication Services", "Wireless Telecom"),
    "AMZN": ("Consumer Discretionary", "E-Commerce & Cloud"),
    "TSLA": ("Consumer Discretionary", "EV & Autonomous Robotics"),
    "CAVA": ("Consumer Discretionary", "Fast Casual Restaurants"),
    "CMG": ("Consumer Discretionary", "Restaurants"),
    "ANF": ("Consumer Discretionary", "Apparel Retail"),
    "FIGS": ("Consumer Discretionary", "Healthcare Apparel"),
    "DECK": ("Consumer Discretionary", "Footwear & Apparel"),
    "ONON": ("Consumer Discretionary", "Athletic Footwear"),
    "CVNA": ("Consumer Discretionary", "Auto E-Commerce"),
    "CART": ("Consumer Discretionary", "Online Grocery"),
    "UBER": ("Industrials", "Mobility & Delivery"),
    "GE": ("Industrials", "Aerospace & Defense"),
    "HWM": ("Industrials", "Aerospace Components"),
    "RKLB": ("Industrials", "Space Launch Systems"),
    "PWR": ("Industrials", "Grid Infrastructure"),
    "VRT": ("Industrials", "Data Center Cooling"),
    "PSIX": ("Industrials", "Power Systems"),
    "RHI": ("Industrials", "Staffing Services"),
    "PCAR": ("Industrials", "Heavy Duty Trucks"),
    "DNOW": ("Industrials", "Industrial Distribution"),
    "XOM": ("Energy", "Integrated Oil & Gas"),
    "CVX": ("Energy", "Integrated Oil & Gas"),
    "EQNR": ("Energy", "Integrated Energy"),
    "BP": ("Energy", "Integrated Oil & Gas"),
    "COP": ("Energy", "Oil & Gas E&P"),
    "EOG": ("Energy", "Oil & Gas E&P"),
    "DVN": ("Energy", "Oil & Gas E&P"),
    "OXY": ("Energy", "Oil & Gas E&P"),
    "APA": ("Energy", "Oil & Gas E&P"),
    "PR": ("Energy", "Permian Basin E&P"),
    "MPC": ("Energy", "Oil Refining & Marketing"),
    "PBF": ("Energy", "Oil Refining"),
    "VLO": ("Energy", "Oil Refining"),
    "SLB": ("Energy", "Oilfield Services"),
    "HAL": ("Energy", "Oilfield Services"),
    "LBRT": ("Energy", "Oilfield Services"),
    "INSW": ("Energy", "Crude Tankers & Shipping"),
    "FRO": ("Energy", "Oil Tankers"),
    "DHT": ("Energy", "VLCC Crude Tankers"),
    "LPG": ("Energy", "LPG Maritime Transport"),
    "ET": ("Energy", "Midstream Pipelines"),
    "KMI": ("Energy", "Natural Gas Pipelines"),
    "CEG": ("Utilities", "Nuclear & Clean Power"),
    "VST": ("Utilities", "Independent Power"),
    "OKLO": ("Utilities", "Advanced Nuclear SMR"),
    "NEE": ("Utilities", "Renewable Utilities"),
    "LLY": ("Health Care", "Pharmaceuticals"),
    "NVO": ("Health Care", "Pharmaceuticals"),
    "HALO": ("Health Care", "Biotechnology"),
    "ILMN": ("Health Care", "Genomics & Life Sciences"),
    "CDNA": ("Health Care", "Transplant Diagnostics"),
    "ETON": ("Health Care", "Specialty Pharma"),
    "HIMS": ("Health Care", "Telehealth & Wellness"),
    "WGS": ("Health Care", "Genetic Testing"),
    "TNGX": ("Health Care", "Targeted Oncology"),
    "SNDX": ("Health Care", "Oncology Biotech"),
    "KNSA": ("Health Care", "Cardiopulmonary Biotech"),
    "ORIC": ("Health Care", "Oncology Biotech"),
    "IONS": ("Health Care", "RNA-Targeted Therapeutics"),
    "MLYS": ("Health Care", "Cardiorenal Biotech"),
    "VRDN": ("Health Care", "Autoimmune Biotech"),
    "LFST": ("Health Care", "Mental Health Services"),
    "CI": ("Health Care", "Managed Health Care"),
    "JPM": ("Financials", "Money Center Banks"),
    "GS": ("Financials", "Investment Banking"),
    "MS": ("Financials", "Investment Banking"),
    "BAC": ("Financials", "Diversified Banks"),
    "WFC": ("Financials", "Diversified Banks"),
    "C": ("Financials", "Money Center Banks"),
    "BX": ("Financials", "Alternative Asset Mgmt"),
    "KKR": ("Financials", "Private Equity"),
    "APO": ("Financials", "Alternative Asset Mgmt"),
    "HOOD": ("Financials", "Retail Brokerage & Crypto"),
    "COIN": ("Financials", "Crypto Exchange"),
    "MSTR": ("Information Technology", "Bitcoin Treasury & BI"),
    "FCNCA": ("Financials", "Regional Banking"),
    "VLY": ("Financials", "Regional Banking"),
    "FITB": ("Financials", "Regional Banking"),
    "HBAN": ("Financials", "Regional Banking"),
    "RF": ("Financials", "Regional Banking"),
    "CFG": ("Financials", "Regional Banking"),
    "KEY": ("Financials", "Regional Banking"),
    "NEM": ("Materials", "Gold Mining"),
    "AEM": ("Materials", "Gold Mining"),
    "FCX": ("Materials", "Copper & Gold Mining"),
    "AAUC": ("Materials", "Gold Mining"),
    "METC": ("Materials", "Metallurgical Coal"),
    "CCI": ("Real Estate", "Telecom Tower REITs"),
    "AMT": ("Real Estate", "Telecom Tower REITs"),
    "VICI": ("Real Estate", "Experiential REITs"),
    "HHH": ("Real Estate", "Master Planned Communities"),
}

_FALLBACK_SECTORS = [
    ("Information Technology", "Software & Tech"),
    ("Health Care", "Biotech & Medical"),
    ("Industrials", "Industrial Tech"),
    ("Financials", "Capital Markets"),
    ("Energy", "Oil & Gas"),
    ("Consumer Discretionary", "Consumer Growth"),
    ("Materials", "Specialty Materials"),
    ("Communication Services", "Digital Media")
]


def get_sector_and_industry(symbol: str) -> Tuple[str, str]:
    """Retorna (Sector, Industria) de forma determinista y sin latencia."""
    if symbol in SECTOR_INDUSTRY_MAP:
        return SECTOR_INDUSTRY_MAP[symbol]
    idx = sum(ord(c) for c in symbol) % len(_FALLBACK_SECTORS)
    return _FALLBACK_SECTORS[idx]


# ==============================================================================
# 1. CATÁLOGO CENTRALIZADO DE FILTROS CUANTITATIVOS CON LISTAS ACTUALIZADAS
# ==============================================================================

def save_live_filter_execution(filter_name: str, tickers: List[str], df_results: Optional[pd.DataFrame] = None) -> None:
    """
    Registra la lista actualizada de un filtro ejecutado en el Screener para que
    esté disponible instantáneamente en Intraday Strength Watch y RRG Desk.
    """
    clean_t = [str(t).strip().upper() for t in tickers if str(t).strip()]
    if not clean_t:
        return
    try:
        data = {}
        if FILTER_RESULTS_CACHE_FILE.exists():
            with open(FILTER_RESULTS_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[filter_name] = {
            "tickers": clean_t,
            "count": len(clean_t),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(FILTER_RESULTS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load_saved_filter_executions() -> Dict[str, Dict[str, Any]]:
    """Carga los resultados de filtros ejecutados recientemente."""
    if FILTER_RESULTS_CACHE_FILE.exists():
        try:
            with open(FILTER_RESULTS_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_updated_filters_catalog(session_state: Optional[Any] = None) -> Dict[str, Dict[str, Any]]:
    """
    Construye el catálogo completo de TODOS los filtros cuantitativos con sus listas
    actualizadas (priorizando resultados en vivo en session_state / disco y las
    canastas calibradas de cada filtro del motor cuantitativo).
    """
    catalog: Dict[str, Dict[str, Any]] = {}
    saved_runs = load_saved_filter_executions()

    # 1. Radar Activo Compartido (Último filtro corrido en Screener)
    if are is not None:
        radar = are.get_active_radar()
        r_tickers = radar.get("tickers", [])
        r_src = radar.get("source", "Screener")
        r_ts = radar.get("timestamp", "Hoy")
        if r_tickers:
            key = f"🎯 Radar Activo: {r_src} ({len(r_tickers)} activos)"
            catalog[key] = {
                "name": key,
                "short_name": f"Radar: {r_src}",
                "tickers": r_tickers,
                "category": "En Vivo",
                "updated_at": r_ts,
                "is_live_session": True
            }

    # 2. Revisar si hay ejecuciones en st.session_state de la sesión actual
    if session_state is not None:
        for k, v in list(session_state.items()):
            if str(k).startswith("scan_results_") and isinstance(v, tuple) and len(v) == 2:
                df_res, _ = v
                if isinstance(df_res, pd.DataFrame) and not df_res.empty and "Ticker" in df_res.columns:
                    t_list = df_res["Ticker"].dropna().unique().tolist()
                    parts = str(k).replace("scan_results_", "").split("_")
                    f_label = parts[0] if parts else "Filtro Screener"
                    key = f"🟢 [EN VIVO] {f_label} ({len(t_list)} filtrados)"
                    catalog[key] = {
                        "name": key,
                        "short_name": f_label,
                        "tickers": t_list,
                        "category": "Sesión Activa",
                        "updated_at": "Recién ejecutado",
                        "is_live_session": True
                    }

    # 3. Todos los Filtros Cuantitativos Oficiales con sus Listas Actualizadas
    official_filters = [
        ("🌅 Pre Market Movers & Gap Ups", getattr(engine, "PRE_MARKET_MOVERS_TICKERS", []), "Intraday / Pre-Market"),
        ("🌆 Post Market Movers (After-Hours)", getattr(engine, "POST_MARKET_MOVERS_21_TICKERS", getattr(engine, "POST_MARKET_MOVERS_TICKERS", [])), "After-Hours / Earnings"),
        ("📋 MTM WL de la Semana (Club RRG Leaders)", MTM_WEEKLY_RRG_LEADERS, "Rotación RRG Semanal"),
        ("⚡ Power 21 (Pullback 21 EMA & AS)", getattr(eu, "POWER_21_69", getattr(engine, "POWER_21_69_TICKERS", [])), "Deepvue Oficial"),
        ("💧 Volume Dry Up & RMV Tight", getattr(eu, "VOLUME_DRY_UP_160", getattr(engine, "VOLUME_DRY_UP_160_TICKERS", [])), "Deepvue Oficial"),
        ("🔥 Highest Volume IPO (Since IPO Day)", getattr(engine, "HV_IPO_7_TICKERS", getattr(engine, "HVE_7_TICKERS", [])), "Deepvue Oficial"),
        ("⚡ Ameet Rai: HV Edge (Daily Routine)", getattr(eu, "AMEET_RAI_HV_EDGE_45", getattr(engine, "AMEET_RAI_HV_EDGE_45_TICKERS", [])), "Ameet Rai"),
        ("🚩 Ameet Rai: High Tight Flags (HTF)", getattr(eu, "AMEET_RAI_HTF_12", getattr(engine, "AMEET_RAI_HTF_12_TICKERS", [])), "Ameet Rai"),
        ("🛡️ Ameet Rai: 62.5% RS Days (Corrections)", getattr(eu, "AMEET_RAI_RS_DAYS_191", getattr(engine, "AMEET_RAI_RS_DAYS_191_TICKERS", [])), "Ameet Rai"),
        ("💧 Ameet Rai: Daily Liquidity (>8M Vol)", getattr(eu, "AMEET_RAI_DAILY_LIQUIDITY_296", getattr(engine, "AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS", [])), "Ameet Rai"),
        ("🌱 Ameet Rai: IPO Last 1 Year", getattr(eu, "AMEET_RAI_IPO_1YR_189", getattr(engine, "AMEET_RAI_IPO_1YR_189_TICKERS", [])), "Ameet Rai"),
        ("🚀 Momentum Leaders (Liquid RS)", getattr(eu, "MOMENTUM_LEADERS_186", getattr(engine, "MOMENTUM_LEADERS_186_TICKERS", [])), "Deepvue Oficial"),
        ("💎 Liquid Leaders (Alta Liquidez & RS)", getattr(engine, "LIQUID_LEADERS_187_TICKERS", []), "Deepvue Oficial"),
        ("📅 Weekly Strength (Cierre Semanal Alto)", getattr(eu, "WEEKLY_STRENGTH_399", getattr(engine, "WEEKLY_STRENGTH_399_TICKERS", [])), "Deepvue Oficial"),
        ("🎯 Tight Range (RMV < 10% Compression)", getattr(engine, "TIGHT_RANGE_26_TICKERS", []), "Deepvue Oficial"),
        ("🎯 Pocket Pivots (Morales & Kacher)", getattr(engine, "POCKET_PIVOTS_45_TICKERS", []), "Deepvue Oficial"),
        ("⚡ Qullamaggie: Episodic Pivot (EP)", getattr(engine, "EPISODIC_PIVOT_8_TICKERS", []), "Qullamaggie"),
        ("🌀 Mark Minervini: VCP Pattern", getattr(engine, "VCP_MINERVINI_43_TICKERS", []), "Minervini"),
        ("🏆 CANSLIM® Official Leaders", getattr(engine, "CANSLIM_OFFICIAL_36_TICKERS", []), "O'Neil CANSLIM"),
        ("🚀 CANSLIM High RS Leaders (Tech/Cons)", getattr(engine, "CANSLIM_HIGH_RS_137_TICKERS", []), "O'Neil CANSLIM"),
        ("📈 Up on Volume (Acumulación Institucional)", getattr(engine, "UP_ON_VOLUME_64_TICKERS", []), "Volumen & Flujo"),
        ("🐜 David Ryan: Ants (Acumulación 15d)", getattr(engine, "ANTS_3_TICKERS", []), "David Ryan"),
        ("🚀 Pure Momentum (ADR > 3% & AS > 95)", getattr(engine, "PURE_MOMENTUM_231_TICKERS", []), "Momentum"),
        ("📈 Stage Analysis: Weinstein Etapa 2/2A", getattr(engine, "STAGE2_LEADERS_417_TICKERS", []), "Stan Weinstein"),
        ("🏆 True Market Leaders (TML 331)", getattr(engine, "TML_331_TICKERS", []), "Líderes Estructurales"),
        ("🌐 Deepvue Universe (752 Líquidas)", getattr(eu, "DEEPVUE_UNIVERSE_752", getattr(engine, "DEEPVUE_UNIVERSE_752_TICKERS", [])), "Universo Maestro"),
        ("🔥 Top Gappers & RVOL Intradía", getattr(engine, "MOMENTUM_25_TICKERS", []), "Day Trading"),
        ("🎯 Minervini Trend Template (S&P Leaders)", getattr(engine, "SP500_30_TICKERS", []), "Minervini")
    ]

    for f_title, f_tickers, f_cat in official_filters:
        # Si el filtro fue re-ejecutado y guardado en disco, usar su lista más reciente
        if f_title in saved_runs and saved_runs[f_title].get("tickers"):
            t_list = saved_runs[f_title]["tickers"]
            upd = saved_runs[f_title].get("updated_at", "Actualizado")
        else:
            t_list = list(f_tickers) if f_tickers else []
            upd = "Lista Calibrada Activa"

        # Limpiar símbolos especiales de índices internos (ej. SA40MA-NYSE) para descargas limpias
        clean_list = [
            str(t).strip().upper().replace(".", "-")
            for t in t_list
            if str(t).strip() and not str(t).endswith("-NYSE") and not str(t).endswith("-USA")
        ]
        if not clean_list:
            continue

        display_key = f"{f_title} ({len(clean_list)} activos)"
        catalog[display_key] = {
            "name": display_key,
            "short_name": f_title,
            "tickers": clean_list,
            "category": f_cat,
            "updated_at": upd,
            "is_live_session": False
        }

    return catalog


# ==============================================================================
# 2. MOTOR DE DESCARGA INCREMENTAL & CACHÉ MULTINIVEL (L1 RAM + L2 DISCO)
# ==============================================================================

def _get_l2_cache_path(period: str, interval: str) -> Path:
    safe_p = re.sub(r'[^a-zA-Z0-9]', '', period)
    safe_i = re.sub(r'[^a-zA-Z0-9]', '', interval)
    return CACHE_DIR / f"matrix_{safe_p}_{safe_i}.pkl"


import re


def _normalize_df_index(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Normaliza el DatetimeIndex para evitar desalineaciones de zona horaria o filas NaN."""
    if df is None or df.empty:
        return df
    out = df.copy()
    try:
        idx = pd.to_datetime(out.index)
        if getattr(idx, "tz", None) is not None:
            idx = idx.tz_localize(None)
        if interval in ("1d", "1wk", "1mo"):
            idx = idx.normalize()
        out.index = idx
        out = out[~out.index.duplicated(keep="last")].sort_index()
    except Exception:
        pass
    return out


def fetch_ohlcv_matrix(
    tickers: List[str],
    period: str = "6mo",
    interval: str = "1d",
    force_refresh: bool = False,
    max_symbols: int = 120
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """
    Descarga y mantiene en caché matrices vectorizadas (Tiempo x Símbolo) para
    Close, Open, High, Low y Volume. Protegido con RLock contra colisiones de hilos en yfinance.
    """
    t0 = time.perf_counter()
    clean_tickers = []
    seen = set()
    for t in tickers[:max_symbols]:
        s = str(t).strip().upper().replace(".", "-")
        if s and s not in seen and len(s) <= 6:
            clean_tickers.append(s)
            seen.add(s)

    cache_key = (period, interval)
    ttl = _TTL_MAP.get(interval, 600)
    now = time.time()

    with _PIPELINE_LOCK:
        cached_pack = _L1_MATRIX_CACHE.get(cache_key)
        l2_path = _get_l2_cache_path(period, interval)

        if cached_pack is None and l2_path.exists() and not force_refresh:
            try:
                with open(l2_path, "rb") as f:
                    disk_pack = pickle.load(f)
                if isinstance(disk_pack, dict) and (now - disk_pack.get("ts", 0)) < ttl * 3:
                    cached_pack = disk_pack
                    _L1_MATRIX_CACHE[cache_key] = cached_pack
            except Exception:
                cached_pack = None

        col_ts_map: Dict[str, float] = {}
        existing_cols = set()
        if cached_pack is not None and "close" in cached_pack and isinstance(cached_pack["close"], pd.DataFrame):
            existing_cols = set(cached_pack["close"].columns)
            col_ts_map = dict(cached_pack.get("col_ts", {}))
            default_ts = float(cached_pack.get("ts", 0))
            for c_name in existing_cols:
                if c_name not in col_ts_map:
                    col_ts_map[c_name] = default_ts

        if force_refresh or cached_pack is None:
            missing_tickers = list(clean_tickers)
        else:
            missing_tickers = [
                t for t in clean_tickers
                if (t not in existing_cols) or ((now - col_ts_map.get(t, 0.0)) >= ttl)
            ]

        downloaded_count = 0
        if missing_tickers:
            try:
                import yfinance as yf
                raw = yf.download(
                    missing_tickers,
                    period=period,
                    interval=interval,
                    group_by="ticker",
                    auto_adjust=True,
                    threads=True,
                    progress=False
                )
                if raw is not None and not raw.empty:
                    c_dict, o_dict, h_dict, l_dict, v_dict = {}, {}, {}, {}, {}
                    if len(missing_tickers) == 1:
                        sym = missing_tickers[0]
                        if "Close" in raw.columns and not raw["Close"].dropna().empty:
                            c_dict[sym] = raw["Close"]
                            o_dict[sym] = raw.get("Open", raw["Close"])
                            h_dict[sym] = raw.get("High", raw["Close"])
                            l_dict[sym] = raw.get("Low", raw["Close"])
                            v_dict[sym] = raw.get("Volume", pd.Series(0, index=raw.index))
                    else:
                        top_Result = raw.columns.get_level_values(0).unique() if isinstance(raw.columns, pd.MultiIndex) else []
                        for sym in missing_tickers:
                            if sym in top_Result:
                                sub = raw[sym]
                                if "Close" in sub.columns and not sub["Close"].dropna().empty:
                                    c_dict[sym] = sub["Close"]
                                    o_dict[sym] = sub.get("Open", sub["Close"])
                                    h_dict[sym] = sub.get("High", sub["Close"])
                                    l_dict[sym] = sub.get("Low", sub["Close"])
                                    v_dict[sym] = sub.get("Volume", pd.Series(0, index=sub.index))

                    if c_dict:
                        new_close = _normalize_df_index(pd.DataFrame(c_dict), interval)
                        new_open = _normalize_df_index(pd.DataFrame(o_dict), interval)
                        new_high = _normalize_df_index(pd.DataFrame(h_dict), interval)
                        new_low = _normalize_df_index(pd.DataFrame(l_dict), interval)
                        new_vol = _normalize_df_index(pd.DataFrame(v_dict), interval)
                        downloaded_count = len(c_dict)

                        for s_dl in c_dict.keys():
                            col_ts_map[s_dl] = now

                        if cached_pack is not None and "close" in cached_pack and not cached_pack["close"].empty:
                            for k_mat, new_df in [("close", new_close), ("open", new_open), ("high", new_high), ("low", new_low), ("volume", new_vol)]:
                                old_df = _normalize_df_index(cached_pack.get(k_mat, pd.DataFrame()), interval)
                                if not old_df.empty:
                                    keep_old_cols = [c for c in old_df.columns if c not in new_df.columns]
                                    combined = pd.concat([old_df[keep_old_cols], new_df], axis=1).sort_index()
                                    cached_pack[k_mat] = combined
                                else:
                                    cached_pack[k_mat] = new_df
                            cached_pack["ts"] = now
                            cached_pack["col_ts"] = col_ts_map
                        else:
                            cached_pack = {
                                "ts": now,
                                "col_ts": col_ts_map,
                                "close": new_close,
                                "open": new_open,
                                "high": new_high,
                                "low": new_low,
                                "volume": new_vol
                            }

                        _L1_MATRIX_CACHE[cache_key] = cached_pack
                        try:
                            with open(l2_path, "wb") as f:
                                pickle.dump(cached_pack, f, protocol=pickle.HIGHEST_PROTOCOL)
                        except Exception:
                            pass
            except Exception as e:
                print(f"[QuantDataPipeline] Warning in batch download: {e}")

        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)

        if cached_pack is None or "close" not in cached_pack:
            return {}, {"latency_ms": elapsed_ms, "downloaded": 0, "cached": 0, "total_tickers": 0}

        avail = [t for t in clean_tickers if t in cached_pack["close"].columns]
        matrices = {
            "close": cached_pack["close"][avail].copy(),
            "open": cached_pack["open"][avail].copy(),
            "high": cached_pack["high"][avail].copy(),
            "low": cached_pack["low"][avail].copy(),
            "volume": cached_pack["volume"][avail].copy()
        }
        telemetry = {
            "latency_ms": elapsed_ms,
            "downloaded": downloaded_count,
            "cached": max(0, len(avail) - downloaded_count),
            "total_tickers": len(avail),
            "cache_timestamp": datetime.fromtimestamp(cached_pack.get("ts", now)).strftime("%H:%M:%S")
        }
        return matrices, telemetry


# ==============================================================================
# 3. MOTOR VECTORIZADO INTRADAY STRENGTH (CÁLCULO POR SÍMBOLO SIN FFILL FALSO)
# ==============================================================================

def compute_vectorized_intraday_df(
    tickers: List[str],
    force_refresh: bool = False,
    max_tickers: int = 120
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calcula las métricas de Intraday Strength Watch extrayendo para cada activo
    sus propias velas válidas no nulas (evitando que un .ffill() matricial copie
    el cierre previo sobre la fila actual y produzca +0.00%).
    """
    matrices, telemetry = fetch_ohlcv_matrix(
        tickers=tickers,
        period="3mo",
        interval="1d",
        force_refresh=force_refresh,
        max_symbols=max_tickers
    )

    if not matrices or "close" not in matrices or matrices["close"].empty:
        return pd.DataFrame(), telemetry

    df_c = matrices["close"]
    df_o = matrices["open"]
    df_h = matrices["high"]
    df_l = matrices["low"]
    df_v = matrices["volume"]

    raw_rows = []
    for sym in df_c.columns:
        s_c = df_c[sym].dropna()
        if len(s_c) < 2:
            continue

        valid_idx = s_c.index
        s_o = df_o[sym].reindex(valid_idx).ffill().bfill()
        s_h = df_h[sym].reindex(valid_idx).ffill().bfill()
        s_l = df_l[sym].reindex(valid_idx).ffill().bfill()
        s_v = df_v[sym].reindex(valid_idx).fillna(0.0)

        cur_px = float(s_c.iloc[-1])
        prev_px = float(s_c.iloc[-2])
        cur_op = float(s_o.iloc[-1])
        cur_hi = float(s_h.iloc[-1])
        cur_lo = float(s_l.iloc[-1])
        cur_vl = float(s_v.iloc[-1])

        # Si Yahoo Finance devuelve una fila placeholder duplicada antes de la apertura (Close[-1] == Close[-2] y Vol == 0)
        if abs(cur_px - prev_px) < 1e-6 and len(s_c) >= 3 and (cur_vl == 0 or abs(cur_px - cur_op) < 1e-6):
            prev_px = float(s_c.iloc[-3])

        if cur_px <= 0 or prev_px <= 0:
            continue

        vol_slice = s_v.iloc[-21:-1] if len(s_v) > 21 else s_v.iloc[:-1]
        vol_pos = vol_slice[vol_slice > 0]
        avg_v20 = float(vol_pos.mean()) if not vol_pos.empty else max(1.0, cur_vl)

        chg_td = ((cur_px / prev_px) - 1.0) * 100.0
        chg_op = ((cur_px / cur_op) - 1.0) * 100.0 if cur_op > 0 else 0.0
        gap_pm = ((cur_op / prev_px) - 1.0) * 100.0 if prev_px > 0 else 0.0
        chg_hi = ((cur_px / cur_hi) - 1.0) * 100.0 if cur_hi > 0 else 0.0
        chg_lo = ((cur_px / cur_lo) - 1.0) * 100.0 if cur_lo > 0 else 0.0

        typ_px = (cur_hi + cur_lo + cur_px) / 3.0
        vwap_d = ((cur_px / typ_px) - 1.0) * 100.0 if typ_px > 0 else 0.0

        raw_rvol = (cur_vl / avg_v20) if avg_v20 > 0 and cur_vl > 0 else 0.85
        d_vol_m = (cur_px * (cur_vl if cur_vl > 0 else avg_v20)) / 1e6

        idx_1m = max(0, len(s_c) - 21)
        idx_3m = max(0, len(s_c) - 60)
        p_1m = float(s_c.iloc[idx_1m])
        p_3m = float(s_c.iloc[idx_3m])
        ret_1m = ((cur_px / p_1m) - 1.0) * 100.0 if p_1m > 0 else 0.0
        ret_3m = ((cur_px / p_3m) - 1.0) * 100.0 if p_3m > 0 else 0.0

        sec, ind = get_sector_and_industry(sym)
        raw_rows.append({
            "symbol": sym,
            "name": f"{sym} ({ind})",
            "industry": ind,
            "sector": sec,
            "price": round(cur_px, 2),
            "chg_today": round(chg_td, 2),
            "chg_from_open": round(chg_op, 2),
            "chg_from_high": round(chg_hi, 2),
            "chg_from_low": round(chg_lo, 2),
            "raw_rvol": raw_rvol,
            "pre_mkt_gap": round(gap_pm, 2),
            "post_mkt_chg": 0.0,
            "pct_from_vwap": round(vwap_d, 2),
            "ret_1m": ret_1m,
            "ret_3m": ret_3m,
            "dollar_vol_m": round(d_vol_m, 1)
        })

    if not raw_rows:
        return pd.DataFrame(), telemetry

    result_df = pd.DataFrame(raw_rows)
    med_rvol = float(result_df["raw_rvol"].median()) if not result_df.empty else 1.0
    session_frac = float(np.clip(med_rvol / 0.95, 0.15, 1.0)) if med_rvol < 0.75 else 1.0
    result_df["rvol_20d"] = (result_df["raw_rvol"] / session_frac).clip(lower=0.15, upper=25.0).round(2)
    result_df["run_rate_20d"] = (result_df["rvol_20d"] * 100.0).round(1)
    result_df["rs_1m"] = (result_df["ret_1m"].rank(pct=True) * 49.0 + 50.0).fillna(75.0).round(0).astype(int)
    result_df["rs_3m"] = (result_df["ret_3m"].rank(pct=True) * 49.0 + 50.0).fillna(75.0).round(0).astype(int)
    result_df.drop(columns=["raw_rvol", "ret_1m", "ret_3m"], inplace=True, errors="ignore")

    return result_df, telemetry


# ==============================================================================
# 4. MOTOR VECTORIZADO MULTI-TEMPORALIDAD PARA RRG (JULIUS DE KEMPENAER)
# ==============================================================================

RRG_TIMEFRAME_CONFIGS = {
    "3m_1d": {
        "label": "📅 3 Meses · Datos Diarios (Corto Plazo)",
        "short_label": "3 months • Daily",
        "description": "Temporalidad: 3 meses con datos diarios. Útil para detectar cambios de tendencia y oportunidades o riesgos en el corto plazo.",
        "dl_period": "6mo",
        "interval": "1d",
        "chart_bars": 64,       # ~3 meses de sesiones diarias
        "default_tail": 10,     # 10 trading days
        "tail_unit": "trading days",
        "tail_unit_es": "días de trading",
        "window": 14
    },
    "1y_1wk": {
        "label": "📆 1 Año · Datos Semanales (Medio/Largo Plazo)",
        "short_label": "1 year • Weekly",
        "description": "Temporalidad: 1 año con datos semanales (cola de 10 semanas). Suaviza el ruido diario y muestra la rotación estructural de fondo.",
        "dl_period": "2y",
        "interval": "1wk",
        "chart_bars": 52,       # 52 semanas (1 año)
        "default_tail": 10,     # 10 weeks
        "tail_unit": "weeks",
        "tail_unit_es": "semanas",
        "window": 14
    },
    "1m_1h": {
        "label": "⚡ 1 Mes · Datos Horarios 1H (Intradía / Táctico)",
        "short_label": "1 month • Hourly (1H)",
        "description": "Temporalidad: 1 mes con datos horarios (1H). Diseñado para capturar rotaciones rápidas intradía y liderazgo de muy corto plazo.",
        "dl_period": "1mo",
        "interval": "1h",
        "chart_bars": 140,
        "default_tail": 10,
        "tail_unit": "hours",
        "tail_unit_es": "horas",
        "window": 14
    },
    "6m_1d": {
        "label": "📊 6 Meses · Datos Diarios (Swing Intermedio)",
        "short_label": "6 months • Daily",
        "description": "Temporalidad: 6 meses con datos diarios. Equilibrio entre sensibilidad táctica y tendencia intermedia.",
        "dl_period": "1y",
        "interval": "1d",
        "chart_bars": 126,
        "default_tail": 12,
        "tail_unit": "trading days",
        "tail_unit_es": "días de trading",
        "window": 14
    },
    "3y_1mo": {
        "label": "🏛️ 3 Años · Datos Mensuales (Macro Secular)",
        "short_label": "3 years • Monthly",
        "description": "Temporalidad: 3 años con datos mensuales. Muestra grandes ciclos macroeconómicos y rotación secular de capital.",
        "dl_period": "5y",
        "interval": "1mo",
        "chart_bars": 36,
        "default_tail": 6,
        "tail_unit": "months",
        "tail_unit_es": "meses",
        "window": 10
    }
}


def get_rrg_quadrant_info(rs_ratio: float, rs_mom: float) -> Tuple[str, str, str, str]:
    """
    Retorna (nombre_es, nombre_en, color_neon, color_stockcharts).
    """
    if rs_ratio >= 100.0 and rs_mom >= 100.0:
        return "Líder", "Leading", "#00FF87", "#15803D"
    elif rs_ratio >= 100.0 and rs_mom < 100.0:
        return "Debilitándose", "Weakening", "#FFB300", "#D97706"
    elif rs_ratio < 100.0 and rs_mom < 100.0:
        return "Rezagada", "Lagging", "#FF3366", "#DC2626"
    else:
        return "Mejorando", "Improving", "#00D4FF", "#2563EB"


def compute_vectorized_rrg(
    tickers: List[str],
    benchmark: str = "SPY",
    timeframe_key: str = "3m_1d",
    tail_len: Optional[int] = None,
    force_refresh: bool = False,
    max_tickers: int = 60,
    custom_meta: Optional[Dict[str, Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Computa de manera 100% vectorizada las coordenadas JdK RS-Ratio y RS-Momentum
    para cualquier temporalidad ('3m_1d', '1y_1wk', '1m_1h', '6m_1d', '3y_1mo')
    y retorna además la serie histórica del Benchmark para el mini-gráfico lateral.
    """
    tf_cfg = RRG_TIMEFRAME_CONFIGS.get(timeframe_key, RRG_TIMEFRAME_CONFIGS["3m_1d"])
    dl_period = tf_cfg["dl_period"]
    interval = tf_cfg["interval"]
    window = tf_cfg["window"]
    chart_bars = tf_cfg["chart_bars"]
    if tail_len is None:
        tail_len = tf_cfg["default_tail"]

    clean_bench = benchmark.replace("$SPX", "SPY").strip().upper()
    all_req = [clean_bench] + [t for t in tickers[:max_tickers] if t != clean_bench]

    matrices, telemetry = fetch_ohlcv_matrix(
        tickers=all_req,
        period=dl_period,
        interval=interval,
        force_refresh=force_refresh,
        max_symbols=max_tickers + 5
    )

    if not matrices or "close" not in matrices or matrices["close"].empty or clean_bench not in matrices["close"].columns:
        return {
            "timeframe_key": timeframe_key,
            "tf_config": tf_cfg,
            "benchmark": benchmark,
            "tail_len": tail_len,
            "results": {},
            "bench_series": [],
            "bench_dates": [],
            "telemetry": telemetry
        }

    df_close = matrices["close"].ffill()
    bench_s = df_close[clean_bench].dropna()
    if len(bench_s) < window + 4:
        return {
            "timeframe_key": timeframe_key,
            "tf_config": tf_cfg,
            "benchmark": benchmark,
            "tail_len": tail_len,
            "results": {},
            "bench_series": [],
            "bench_dates": [],
            "telemetry": telemetry
        }

    asset_cols = [c for c in df_close.columns if c != clean_bench]
    df_assets = df_close.loc[bench_s.index, asset_cols]

    # 1. Fuerza Relativa matricial: RS = (Asset / Benchmark) * 100
    rs_mat = df_assets.div(bench_s, axis=0) * 100.0

    # 2. JdK RS-Ratio vectorizado centrado en 100 con suavizado EMA orgánico
    min_p = max(4, window // 2)
    rs_mean = rs_mat.rolling(window=window, min_periods=min_p).mean()
    rs_std = rs_mat.rolling(window=window, min_periods=min_p).std().replace(0, np.nan)
    rs_ratio_raw = 100.0 + ((rs_mat - rs_mean) / rs_std) * 4.5
    rs_ratio_mat = rs_ratio_raw.ewm(span=3, adjust=False).mean()

    # 3. JdK RS-Momentum vectorizado centrado en 100 con suavizado EMA orgánico
    rr_mean = rs_ratio_mat.rolling(window=window, min_periods=min_p).mean()
    rr_std = rs_ratio_mat.rolling(window=window, min_periods=min_p).std().replace(0, np.nan)
    rs_mom_raw = 100.0 + ((rs_ratio_mat - rr_mean) / rr_std) * 4.5
    rs_mom_mat = rs_mom_raw.ewm(span=3, adjust=False).mean()

    # Formato de fecha según temporalidad
    if interval == "1h":
        date_fmt = "%d %b %H:%M"
    elif interval == "1mo":
        date_fmt = "%b %Y"
    else:
        date_fmt = "%d %b %Y"

    results = {}
    palette = [
        "#00FF87", "#00F0FF", "#38BDF8", "#A855F7", "#EC4899", "#F59E0B",
        "#EAB308", "#10B981", "#6366F1", "#14B8A6", "#F43F5E", "#84CC16"
    ]

    for idx_col, sym in enumerate(asset_cols):
        r_series = rs_ratio_mat[sym].dropna()
        m_series = rs_mom_mat[sym].dropna()
        common_t = r_series.index.intersection(m_series.index)
        if len(common_t) < 3:
            continue

        r_s = r_series.loc[common_t]
        m_s = m_series.loc[common_t]
        a_s = df_assets.loc[common_t, sym].dropna()
        b_s = bench_s.loc[common_t]

        cur_r = round(float(r_s.iloc[-1]), 2)
        cur_m = round(float(m_s.iloc[-1]), 2)
        prev_r = round(float(r_s.iloc[-2]), 2)
        prev_m = round(float(m_s.iloc[-2]), 2)

        q_es, q_en, q_neon, q_sc = get_rrg_quadrant_info(cur_r, cur_m)
        prev_q_es, _, _, _ = get_rrg_quadrant_info(prev_r, prev_m)

        # Extraer cola de longitud tail_len + 1 puntos (para tener tail_len segmentos)
        n_pts = min(tail_len + 1, len(common_t))
        tail_pts = []
        tail_dates = []
        for k in range(-n_pts, 0):
            tail_pts.append([round(float(r_s.iloc[k]), 2), round(float(m_s.iloc[k]), 2)])
            tail_dates.append(common_t[k].strftime(date_fmt))

        # Vector de rumbo y velocidad
        dx = tail_pts[-1][0] - tail_pts[-2][0] if len(tail_pts) >= 2 else 0.0
        dy = tail_pts[-1][1] - tail_pts[-2][1] if len(tail_pts) >= 2 else 0.0
        vel = round(math.sqrt(dx * dx + dy * dy), 2)
        angle_deg = round(math.degrees(math.atan2(dy, dx)) % 360.0, 1)

        if 0 <= angle_deg < 45 or 315 <= angle_deg < 360:
            dir_lbl = "Hacia Líder (Este-Noreste) ↗️"
        elif 45 <= angle_deg < 135:
            dir_lbl = "Aceleración Fuerte (Norte) ⬆️"
        elif 135 <= angle_deg < 225:
            dir_lbl = "Giro a Rezagado (Oeste) ⬅️"
        else:
            dir_lbl = "Pérdida de Impulso (Sur) ⬇️"

        # Desempeño relativo reciente vs Benchmark
        p_1 = round(float(((a_s.iloc[-1] / a_s.iloc[-2]) - (b_s.iloc[-1] / b_s.iloc[-2])) * 100.0), 2) if len(a_s) >= 2 else 0.0
        step_back = min(len(a_s) - 1, max(1, tail_len))
        p_tail = round(float(((a_s.iloc[-1] / a_s.iloc[-1 - step_back]) - (b_s.iloc[-1] / b_s.iloc[-1 - step_back])) * 100.0), 2) if len(a_s) > step_back else 0.0

        sec_name, ind_name = get_sector_and_industry(sym)
        if custom_meta and sym in custom_meta:
            c_meta = custom_meta[sym]
            disp_name = c_meta.get("name", f"{sym} ({ind_name})")
            disp_sec = c_meta.get("sector") or c_meta.get("theme", sec_name)
            indiv_color = c_meta.get("color", palette[idx_col % len(palette)])
        else:
            disp_name = f"{sym} ({ind_name})"
            disp_sec = f"{sec_name} • {ind_name}"
            indiv_color = palette[idx_col % len(palette)]

        q_icon_map = {"Líder": "🟢", "Debilitándose": "🟡", "Rezagada": "🔴", "Mejorando": "🔵"}

        results[sym] = {
            "symbol": sym,
            "name": disp_name,
            "sector": disp_sec,
            "color": indiv_color,
            "quadrant_color_neon": q_neon,
            "quadrant_color_sc": q_sc,
            "rs_ratio": cur_r,
            "rs_momentum": cur_m,
            "prev_ratio": prev_r,
            "prev_mom": prev_m,
            "quadrant": q_es,
            "quadrant_en": q_en,
            "quadrant_icon": q_icon_map.get(q_es, "⚪"),
            "quadrant_color": q_neon,
            "prev_quadrant": prev_q_es,
            "quadrant_changed": (q_es != prev_q_es),
            "heading_deg": angle_deg,
            "velocity": vel,
            "direction_label": dir_lbl,
            "perf_vs_bench_1w": p_1,
            "perf_vs_bench_4w": p_tail,
            "tail": tail_pts,
            "tail_dates": tail_dates
        }

    # Serie del Benchmark para el Mini-Gráfico lateral (exactamente las barras de la ventana visual)
    bench_window = bench_s.iloc[-chart_bars:] if len(bench_s) > chart_bars else bench_s
    # Si el usuario eligió $SPX y descargamos SPY, escalar por ~10x para mostrar nivel índice S&P 500 (~5800-7100) o mantener SPY
    scale_factor = 10.0 if benchmark.upper() == "$SPX" and float(bench_window.iloc[-1]) < 1500 else 1.0
    bench_vals = [round(float(v * scale_factor), 2) for v in bench_window.values]
    bench_dts = [d.strftime("%Y-%m-%d %H:%M" if interval == "1h" else "%Y-%m-%d") for d in bench_window.index]

    return {
        "timeframe_key": timeframe_key,
        "tf_config": tf_cfg,
        "benchmark": benchmark,
        "as_of_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tail_len": tail_len,
        "results": results,
        "tail_dates": tail_dates if results else [],
        "bench_series": bench_vals,
        "bench_dates": bench_dts,
        "telemetry": telemetry
    }
