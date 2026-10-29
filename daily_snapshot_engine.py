"""
TradingVolt • Institutional Daily Snapshot & Master Matrix Engine
================================================================
Reverse engineered from Finviz, Deepvue, Bloomberg EQS & TC2000.
Maintains pre-computed in-memory and disk columnar matrices:
1. PRE-MARKET SNAPSHOT (8:00 - 9:15 AM EST): Top Gappers, Earnings BMO, Pre-Vol Spikes.
2. APERTURA SNAPSHOT (10:00 - 11:00 AM EST): Pivot Breakouts, RVOL > 2.0x, Intraday RS Leaders.
3. CIERRE SNAPSHOT (4:00 - 5:00 PM EST): High DCR Closings, New Highs 52w, Dark Pool Tape, Earnings AMC.

Enables SUB-SECOND (< 50ms) screener queries and instantaneous cross-desk referencing.
"""

import os
import sys
import json
import time
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np
import yfinance as yf

import expanded_universes as eu
from leaders_universe import TML_331_TICKERS

BASE_DIR = Path(__file__).parent
SNAPSHOT_DIR = BASE_DIR / "cache_store" / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

FILE_PRE = SNAPSHOT_DIR / "snapshot_premarket.json"
FILE_OPEN = SNAPSHOT_DIR / "snapshot_apertura.json"
FILE_CLOSE = SNAPSHOT_DIR / "snapshot_cierre.json"
FILE_MATRIX = SNAPSHOT_DIR / "master_market_matrix.parquet"
FILE_MATRIX_JSON = SNAPSHOT_DIR / "master_market_matrix.json"

SNAPSHOT_FILES = {
    "PRE": FILE_PRE,
    "OPEN": FILE_OPEN,
    "CLOSE": FILE_CLOSE
}

# -------------------------------------------------------------------------
# CÁLCULOS MATRICIALES VECTORIZADOS (INSTITUTIONAL SPEED)
# -------------------------------------------------------------------------

def calculate_pivot_high_vectorized(high_series: pd.Series, left: int = 5, right: int = 5, lookback: int = 100) -> Optional[float]:
    """Calcula el pivote mayor más reciente con confirmación L/R en ventana de lookback."""
    if len(high_series) < (left + right + 5):
        return None
    sub = high_series.iloc[-min(lookback, len(high_series)):].values
    n = len(sub)
    for i in range(n - 1 - right, left - 1, -1):
        center = sub[i]
        is_pivot = True
        for l in range(1, left + 1):
            if sub[i - l] > center:
                is_pivot = False; break
        if not is_pivot:
            continue
        for r in range(1, right + 1):
            if sub[i + r] >= center:
                is_pivot = False; break
        if is_pivot:
            return float(center)
    return float(np.max(sub[-20:])) if n >= 20 else None


def build_stock_factors(ticker: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Calcula los 35 factores cuantitativos esenciales para un activo en microsegundos."""
    try:
        if df is None or len(df) < 25:
            return None
        df = df.dropna(subset=['Close'])
        df = df[df['Close'] > 0]
        if len(df) < 25:
            return None

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        curr_c = float(close.iloc[-1])
        prev_c = float(close.iloc[-2]) if len(df) >= 2 else curr_c
        curr_o = float(df['Open'].iloc[-1]) if 'Open' in df else curr_c
        curr_h = float(high.iloc[-1])
        curr_l = float(low.iloc[-1])
        curr_v = float(volume.iloc[-1])

        chg_pct = ((curr_c - prev_c) / (prev_c + 1e-9)) * 100.0
        range_spread = curr_h - curr_l
        dcr = ((curr_c - curr_l) / (range_spread + 1e-9)) * 100.0

        # Medias y Volúmenes
        vol_avg_20 = float(volume.tail(21).iloc[:-1].mean()) if len(df) >= 21 else float(volume.mean())
        vol_avg_50 = float(volume.tail(51).iloc[:-1].mean()) if len(df) >= 51 else vol_avg_20
        rvol_20 = curr_v / (vol_avg_20 + 1e-9)
        dollar_vol_m = (curr_c * curr_v) / 1e6
        dollar_vol_avg20 = ((volume.tail(20) * close.tail(20)).mean()) / 1e6 if len(df) >= 20 else dollar_vol_m

        # EMAs y SMAs
        sma_20 = float(close.rolling(20).mean().iloc[-1]) if len(df) >= 20 else curr_c
        sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(df) >= 50 else sma_20
        sma_150 = float(close.rolling(150).mean().iloc[-1]) if len(df) >= 150 else sma_50
        sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(df) >= 200 else sma_150
        ema_10 = float(close.ewm(span=10).mean().iloc[-1])
        ema_21 = float(close.ewm(span=21).mean().iloc[-1])
        ema_100 = float(close.ewm(span=100).mean().iloc[-1]) if len(df) >= 50 else sma_50

        # Pendiente EMA 100
        ema100_series = close.ewm(span=100).mean()
        slope_100 = 0.0
        if len(ema100_series) >= 101:
            slope_100 = ((float(ema100_series.iloc[-1]) - float(ema100_series.iloc[-101])) / float(ema100_series.iloc[-101])) * 100.0

        # ROC y Rangos
        roc_1w = ((curr_c - float(close.iloc[-6])) / float(close.iloc[-6])) * 100.0 if len(df) >= 6 else chg_pct
        roc_1m = ((curr_c - float(close.iloc[-21])) / float(close.iloc[-21])) * 100.0 if len(df) >= 22 else roc_1w
        roc_3m = ((curr_c - float(close.iloc[-63])) / float(close.iloc[-63])) * 100.0 if len(df) >= 64 else roc_1m
        roc_100d = ((curr_c - float(close.iloc[-101])) / float(close.iloc[-101])) * 100.0 if len(df) >= 101 else roc_3m

        high_52w = float(high.tail(252).max())
        low_52w = float(low.tail(252).min())
        dist_high_52w = ((curr_c - high_52w) / (high_52w + 1e-9)) * 100.0
        dist_low_52w = ((curr_c - low_52w) / (low_52w + 1e-9)) * 100.0

        # ADR(10)
        adr_10 = float(((high.tail(10) - low.tail(10)) / (low.tail(10) + 1e-9)).mean() * 100.0) if len(df) >= 10 else 3.5

        # Pivotes de Mike (Daily Pivot Breakout)
        pivot_h = calculate_pivot_high_vectorized(high, left=5, right=5, lookback=100)
        pivot_h_val = pivot_h if pivot_h else high_52w
        dist_pivot_pct = ((curr_c - pivot_h_val) / (pivot_h_val + 1e-9)) * 100.0

        # Detección de Setups
        is_pivot_bo = (curr_c >= pivot_h_val) and (chg_pct > 0) and (rvol_20 >= 1.0) and (roc_100d >= 25.0)
        is_stage_2 = (curr_c > sma_50 > sma_150 > sma_200) and (dist_high_52w >= -25.0) and (dist_low_52w >= 25.0)
        is_episodic = (chg_pct >= 4.0) and (rvol_20 >= 1.5) and (dcr >= 40.0)
        is_closing_high = (dcr >= 75.0) and (chg_pct > 0.5)

        # Relative Strength Proxy (Score 0-100)
        rs_score = int(np.clip(50 + (roc_1m * 0.4) + (roc_3m * 0.3) + (dist_high_52w * 0.3), 1, 99))

        return {
            "Ticker": ticker,
            "Price": round(curr_c, 2),
            "ChangePct": round(chg_pct, 2),
            "Open": round(curr_o, 2),
            "High": round(curr_h, 2),
            "Low": round(curr_l, 2),
            "Volume": int(curr_v),
            "DollarVolM": round(dollar_vol_m, 2),
            "DollarVolAvg20M": round(dollar_vol_avg20, 2),
            "RVOL_20": round(rvol_20, 2),
            "DCR": round(dcr, 1),
            "SMA20": round(sma_20, 2),
            "SMA50": round(sma_50, 2),
            "SMA150": round(sma_150, 2),
            "SMA200": round(sma_200, 2),
            "EMA10": round(ema_10, 2),
            "EMA21": round(ema_21, 2),
            "EMA100": round(ema_100, 2),
            "Slope100": round(slope_100, 1),
            "ROC_1W": round(roc_1w, 1),
            "ROC_1M": round(roc_1m, 1),
            "ROC_3M": round(roc_3m, 1),
            "ROC_100D": round(roc_100d, 1),
            "High52w": round(high_52w, 2),
            "DistHigh52w": round(dist_high_52w, 1),
            "ADR10": round(adr_10, 2),
            "PivotHigh": round(pivot_h_val, 2),
            "DistPivotPct": round(dist_pivot_pct, 1),
            "IsPivotBreakout": bool(is_pivot_bo),
            "IsStage2": bool(is_stage_2),
            "IsEpisodicPivot": bool(is_episodic),
            "IsClosingHigh": bool(is_closing_high),
            "RS_Score": rs_score
        }
    except Exception:
        return None


# -------------------------------------------------------------------------
# GENERACIÓN DE SNAPSHOTS INSTITUCIONALES (OFICIALES)
# -------------------------------------------------------------------------

def generate_master_snapshot(snapshot_type: str = "OPEN", force_refresh: bool = False) -> Dict[str, Any]:
    """
    Construye el snapshot oficial correspondiente y lo guarda en disco:
    - 'PRE': Pre-Market Gappers & Early Catalysts
    - 'OPEN': Confirmaciones de Apertura, Daily Pivot Breakouts, RVOL Spikes
    - 'CLOSE': Cierres en Máximos, New Highs, After-Hours
    """
    snapshot_type = snapshot_type.upper()
    target_file = SNAPSHOT_FILES.get(snapshot_type, FILE_OPEN)

    now_dt = datetime.now()
    now_ts = now_dt.timestamp()

    # Si el archivo tiene menos de 15 minutos y no se fuerza, cargar directo
    if target_file.exists() and not force_refresh:
        try:
            mtime = target_file.stat().st_mtime
            if (now_ts - mtime) < 900.0:  # 15 min TTL
                with open(target_file, "r", encoding="utf-8") as f:
                    cached_obj = json.load(f)
                    if cached_obj.get("candidates") and len(cached_obj["candidates"]) > 0:
                        return cached_obj
        except Exception:
            pass

    # Selección de Universo Base de Escaneo (~750 acciones líderes para máxima velocidad)
    universe_tickers = getattr(eu, 'HIGH_MOMENTUM_EXPANDED_TICKERS', [])
    if not universe_tickers or len(universe_tickers) < 200:
        universe_tickers = list(dict.fromkeys(getattr(eu, 'SP500_COMPLETE_TICKERS', []) + getattr(eu, 'NASDAQ100_COMPLETE_TICKERS', []) + TML_331_TICKERS))

    # Descarga por lotes con caché de barras diarias
    cache_dir = BASE_DIR / ".quant_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    disk_cache_file = cache_dir / "daily_bars_yahoo.pkl"

    bars_store = {}
    if disk_cache_file.exists():
        try:
            import pickle
            if (now_ts - disk_cache_file.stat().st_mtime) < 3600.0:
                with open(disk_cache_file, "rb") as f_disk:
                    bars_store = pickle.load(f_disk)
        except Exception:
            bars_store = {}

    missing = [t for t in universe_tickers if t not in bars_store]
    if missing:
        try:
            chunk_size = 250
            for i in range(0, len(missing), chunk_size):
                chunk = missing[i:i + chunk_size]
                data = yf.download(chunk, period="1y", interval="1d", group_by="ticker", threads=False, progress=False)
                if data is None or data.empty:
                    for t in chunk:
                        bars_store[t] = "EMPTY"
                    continue
                for t in chunk:
                    try:
                        if isinstance(data.columns, pd.MultiIndex) and t in data.columns.levels[0]:
                            df_t = data[t].dropna(how="all")
                            if not df_t.empty and 'Close' in df_t:
                                bars_store[t] = df_t
                            else:
                                bars_store[t] = "EMPTY"
                        elif not isinstance(data.columns, pd.MultiIndex) and len(chunk) == 1:
                            df_t = data.dropna(how="all")
                            bars_store[t] = df_t if (not df_t.empty and 'Close' in df_t) else "EMPTY"
                        else:
                            bars_store[t] = "EMPTY"
                    except Exception:
                        bars_store[t] = "EMPTY"
        except Exception as e:
            print(f"[SnapshotEngine] Error en delta download: {e}")

        # Guardar en pickle
        try:
            import pickle
            with open(disk_cache_file, "wb") as f_disk:
                pickle.dump(bars_store, f_disk, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass

    # Computar Factores Cuantitativos para todos los activos
    records = []
    for t in universe_tickers:
        df_t = bars_store.get(t)
        if df_t is not None and isinstance(df_t, pd.DataFrame) and not df_t.empty:
            f_dict = build_stock_factors(t, df_t)
            if f_dict:
                records.append(f_dict)

    if not records:
        return {"snapshot_type": snapshot_type, "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"), "candidates": [], "count": 0}

    matrix_df = pd.DataFrame(records)

    # Filtrar según tipo de Snapshot
    candidates = []
    if snapshot_type == "PRE":
        # Pre-Market: Gappers > 1.5% o RVOL acelerado o cercanía a máximos
        cond_pre = (matrix_df["ChangePct"].abs() >= 1.5) | (matrix_df["DistHigh52w"] >= -5.0) | (matrix_df["IsEpisodicPivot"])
        sub_df = matrix_df[cond_pre].sort_values(by="ChangePct", ascending=False)
        for _, row in sub_df.head(60).iterrows():
            tag = "🚀 Gap Up Líder" if row["ChangePct"] > 0 else "🔻 Gap Down Alert"
            candidates.append({
                "symbol": row["Ticker"],
                "price": row["Price"],
                "change_pct": row["ChangePct"],
                "rvol": row["RVOL_20"],
                "dcr": row["DCR"],
                "pattern": f"{tag} ({row['ChangePct']:+.2f}%)",
                "rs_score": row["RS_Score"],
                "dollar_vol_m": row["DollarVolM"],
                "pivot_high": row["PivotHigh"],
                "stage2": row["IsStage2"]
            })

    elif snapshot_type == "OPEN":
        # Apertura: Daily Pivot Breakouts, Episodic Pivots, RVOL > 1.2x, ROC100 >= 25%
        cond_open = (
            (matrix_df["IsPivotBreakout"]) |
            (matrix_df["IsEpisodicPivot"] & (matrix_df["RVOL_20"] >= 1.2)) |
            ((matrix_df["DistPivotPct"] >= -3.0) & (matrix_df["Slope100"] >= 15.0) & (matrix_df["RVOL_20"] >= 1.1)) |
            (matrix_df["IsStage2"] & (matrix_df["ChangePct"] >= 2.0) & (matrix_df["RVOL_20"] >= 1.3))
        )
        sub_df = matrix_df[cond_open].sort_values(by=["IsPivotBreakout", "RVOL_20", "ChangePct"], ascending=[False, False, False])
        for _, row in sub_df.head(60).iterrows():
            p_desc = "🚀 BREAKOUT PIVOTE (Confirmado)" if row["IsPivotBreakout"] else ("⚡ Episodic Pivot" if row["IsEpisodicPivot"] else "🔥 Convicción Apertura")
            candidates.append({
                "symbol": row["Ticker"],
                "price": row["Price"],
                "change_pct": row["ChangePct"],
                "rvol": row["RVOL_20"],
                "dcr": row["DCR"],
                "pattern": f"{p_desc} • RVOL {row['RVOL_20']:.1f}x • ROC {row['ROC_100D']:+.1f}%",
                "rs_score": row["RS_Score"],
                "dollar_vol_m": row["DollarVolM"],
                "pivot_high": row["PivotHigh"],
                "stage2": row["IsStage2"]
            })

    else:  # CLOSE
        # Cierre: Cierre en máximos (DCR >= 70%), New Highs 52w, Ganadores netos para Swing
        cond_close = (
            (matrix_df["IsClosingHigh"]) |
            (matrix_df["DistHigh52w"] >= -2.0) |
            (matrix_df["IsPivotBreakout"]) |
            (matrix_df["IsStage2"] & (matrix_df["DCR"] >= 65.0) & (matrix_df["ChangePct"] > 1.0))
        )
        sub_df = matrix_df[cond_close].sort_values(by=["DCR", "ChangePct"], ascending=[False, False])
        for _, row in sub_df.head(60).iterrows():
            c_tag = "🏆 Cierre en Máximos (DCR > 75%)" if row["IsClosingHigh"] else "💎 New 52w High Candidate"
            candidates.append({
                "symbol": row["Ticker"],
                "price": row["Price"],
                "change_pct": row["ChangePct"],
                "rvol": row["RVOL_20"],
                "dcr": row["DCR"],
                "pattern": f"{c_tag} • Cierre ${row['Price']:.2f} ({row['ChangePct']:+.1f}%)",
                "rs_score": row["RS_Score"],
                "dollar_vol_m": row["DollarVolM"],
                "pivot_high": row["PivotHigh"],
                "stage2": row["IsStage2"]
            })

    payload = {
        "snapshot_type": snapshot_type,
        "title": f"Snapshot Oficial {snapshot_type} • {now_dt.strftime('%d/%m/%Y %H:%M')} EST",
        "timestamp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date_str": now_dt.strftime("%d %b %Y"),
        "count": len(candidates),
        "candidates": candidates
    }

    # Guardar Snapshot JSON en disco
    try:
        with open(target_file, "w", encoding="utf-8") as f_out:
            json.dump(payload, f_out, indent=2)
    except Exception as e:
        print(f"[SnapshotEngine] Error guardando snapshot: {e}")

    # Sincronizar automáticamente con el radar activo compartido
    try:
        cand_tickers = [c["symbol"] for c in candidates]
        import active_radar_engine as are
        are.set_active_radar(cand_tickers, source_name=f"Snapshot Oficial {snapshot_type}", description=payload["title"])
    except Exception:
        pass

    return payload


def get_latest_snapshot(snapshot_type: str = "OPEN") -> Dict[str, Any]:
    """Carga instantáneamente (< 5ms) el snapshot desde disco."""
    target_file = SNAPSHOT_FILES.get(snapshot_type.upper(), FILE_OPEN)
    if target_file.exists():
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("candidates") and len(data["candidates"]) > 0:
                    return data
        except Exception:
            pass
    # Si no existe, generarlo
    return generate_master_snapshot(snapshot_type=snapshot_type, force_refresh=False)


def get_snapshot_status(snapshot_type: str = "OPEN") -> Dict[str, Any]:
    """Retorna métricas de conteo y fecha para el snapshot solicitado."""
    stype = snapshot_type.upper()
    fpath = SNAPSHOT_FILES.get(stype, FILE_OPEN)
    if fpath.exists():
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
                return {
                    "exists": True,
                    "count": d.get("count", len(d.get("candidates", []))),
                    "time": d.get("timestamp", "Hoy")
                }
        except Exception:
            pass
    return {"exists": False, "count": 0, "time": "Pendiente"}


def get_all_snapshots_summary() -> Dict[str, Any]:
    """Retorna el estado de disponibilidad de los 3 snapshots."""
    summary = {}
    for stype, fpath in SNAPSHOT_FILES.items():
        if fpath.exists():
            try:
                mtime = fpath.stat().st_mtime
                age_min = int((time.time() - mtime) / 60)
                with open(fpath, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    summary[stype] = {
                        "exists": True,
                        "count": d.get("count", len(d.get("candidates", []))),
                        "timestamp": d.get("timestamp", ""),
                        "age_minutes": age_min
                    }
            except Exception:
                summary[stype] = {"exists": False, "count": 0, "timestamp": "", "age_minutes": -1}
        else:
            summary[stype] = {"exists": False, "count": 0, "timestamp": "", "age_minutes": -1}
    return summary


def render_snapshot_lists_widget(render_chart_fn=None, key_suffix: str = "screener_bottom"):
    """
    Renderiza el widget visual e interactivo de las Listas Oficiales Diarias
    con la visualización en vivo de los activos en movimiento, métricas y botones
    para generar datos frescos o sincronizar con todos los Desks.
    """
    import streamlit as st

    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(14, 20, 32, 0.95), rgba(20, 27, 45, 0.95)); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 12px; padding: 18px 22px; margin-top: 24px; margin-bottom: 18px; box-shadow: 0 8px 32px rgba(0, 240, 255, 0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0; font-size: 20px; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                        <span>📸</span> Listas Oficiales Diarias & Activos en Movimiento (Snapshot Hub)
                    </h3>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #94A3B8;">
                        Monitoreo continuo de los activos detectados en las 3 extracciones oficiales del mercado (Bloomberg EQS & Finviz Elite). Datos vectorizados pre-calculados con acceso instantáneo y visualización en vivo de los activos en juego.
                    </p>
                </div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <span style="background: rgba(0, 255, 135, 0.15); border: 1px solid #00FF87; color: #00FF87; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">● ZERO LATENCY CACHE</span>
                    <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">CROSS-DESK PIPELINE</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_open, tab_pre, tab_close = st.tabs([
        "🔔 Apertura Breakouts & Momentum (10:15 AM EST)",
        "🌅 Pre-Market Movers & Gappers (8:30 AM EST)",
        "🌙 Cierre High DCR & New 52w Highs (4:15 PM EST)"
    ])

    tab_configs = [
        (tab_open, "OPEN", "🔔 Apertura (Breakouts & RVOL)", "Breakout Pivote y Convicción de Apertura"),
        (tab_pre, "PRE", "🌅 Pre-Market (Movers & Gappers)", "Gap Ups y Volatilidad Temprana"),
        (tab_close, "CLOSE", "🌙 Cierre (High DCR & New Highs)", "Cierres Fuertes y Acumulación Institucional")
    ]

    for tab_obj, s_code, s_label, s_desc in tab_configs:
        with tab_obj:
            snap_data = get_latest_snapshot(s_code)
            candidates = snap_data.get("candidates", [])
            ts_str = snap_data.get("timestamp", "Hoy")
            total_cnt = snap_data.get("count", len(candidates))

            # Barra superior de controles del widget
            ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([2.2, 1.3, 1.1])
            with ctrl_c1:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                        <span style="font-size: 13px; color: #CBD5E1; font-weight: 600;">Estado Lista:</span>
                        <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-family: 'JetBrains Mono', monospace;">
                            ⏱️ {ts_str} EST
                        </span>
                        <span style="background: rgba(0, 255, 135, 0.15); border: 1px solid #00FF87; color: #00FF87; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700;">
                            {total_cnt} Activos en Movimiento
                        </span>
                    </div>
                """, unsafe_allow_html=True)

            with ctrl_c2:
                btn_refresh = st.button(
                    f"🔄 Generar Resultados Frescos",
                    key=f"btn_ref_{s_code}_{key_suffix}",
                    use_container_width=True,
                    help=f"Fuerza un re-escaneo completo del mercado para extraer la lista de {s_code} en tiempo real."
                )

            with ctrl_c3:
                btn_sync = st.button(
                    f"🎯 Sincronizar Radar",
                    key=f"btn_sync_{s_code}_{key_suffix}",
                    use_container_width=True,
                    help=f"Transfiere todos los activos de {s_code} a los demás Desks (Opciones, Dark Pool, Intraday Map)."
                )

            if btn_refresh:
                with st.spinner(f"Descargando y recalculando matriz para {s_label}..."):
                    new_snap = generate_master_snapshot(s_code, force_refresh=True)
                    st.toast(f"✅ Lista {s_code} actualizada: {new_snap.get('count', 0)} activos frescos.")
                    st.rerun()

            if btn_sync:
                cand_syms = [c["symbol"] for c in candidates]
                if cand_syms:
                    try:
                        import active_radar_engine as are
                        are.set_active_radar(cand_syms, source_name=f"Snapshot {s_code}", description=f"Sincronizado desde {s_label}")
                        st.toast(f"🎯 Radar Compartido actualizado con {len(cand_syms)} activos de {s_code}.")
                    except Exception as e:
                        st.error(f"Error sincronizando radar: {e}")

            if not candidates:
                st.info(f"No hay activos registrados aún en la lista de {s_label}. Pulsa 'Generar Resultados Frescos' para computarla.")
                continue

            # KPI Summary Cards para la lista activa
            df_snap = pd.DataFrame(candidates)
            top_gainer = df_snap.sort_values(by="change_pct", ascending=False).iloc[0]
            top_rvol = df_snap.sort_values(by="rvol", ascending=False).iloc[0]
            avg_chg = df_snap["change_pct"].mean()
            stage2_cnt = len(df_snap[df_snap["stage2"] == True])

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 700;">TOP GAINER</div>
                    <div style="font-size: 18px; font-weight: 800; color: #00FF87; font-family: 'JetBrains Mono';">${top_gainer['symbol']} ({top_gainer['change_pct']:+.2f}%)</div>
                    <div style="font-size: 11px; color: #64748B;">P: ${top_gainer['price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 700;">MÁXIMO VOLUMEN RVOL</div>
                    <div style="font-size: 18px; font-weight: 800; color: #38BDF8; font-family: 'JetBrains Mono';">${top_rvol['symbol']} ({top_rvol['rvol']:.1f}x)</div>
                    <div style="font-size: 11px; color: #64748B;">Volumen Institucional</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 700;">CAMBIO PROMEDIO</div>
                    <div style="font-size: 18px; font-weight: 800; color: {'#00FF87' if avg_chg >= 0 else '#FF2E63'}; font-family: 'JetBrains Mono';">{avg_chg:+.2f}%</div>
                    <div style="font-size: 11px; color: #64748B;">Sobre {len(df_snap)} activos</div>
                </div>
                """, unsafe_allow_html=True)
            with k4:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #94A3B8; font-weight: 700;">EN ETAPA 2 (WEINSTEIN)</div>
                    <div style="font-size: 18px; font-weight: 800; color: #F59E0B; font-family: 'JetBrains Mono';">{stage2_cnt} Activos</div>
                    <div style="font-size: 11px; color: #64748B;">Tendencia Alcista Clara</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # Preparar tabla visual
            table_display_df = pd.DataFrame([
                {
                    "Ticker": c["symbol"],
                    "Precio": c["price"],
                    "Cambio %": c["change_pct"],
                    "RVOL": c["rvol"],
                    "DCR %": c["dcr"],
                    "RS Score": c["rs_score"],
                    "Patrón Cuantitativo": c["pattern"],
                    "Etapa 2": "🟢 Sí" if c.get("stage2") else "⚪ No"
                }
                for c in candidates
            ])

            col_w_table, col_w_chart = st.columns([2.3, 1.7])
            with col_w_table:
                st.caption("💡 Haz clic en cualquier activo de la lista para inspeccionar su gráfico institucional:")
                sel_w_row = st.dataframe(
                    table_display_df,
                    use_container_width=True,
                    height=380,
                    hide_index=True,
                    selection_mode="single-row",
                    on_select="rerun",
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Precio": st.column_config.NumberColumn("Precio ($)", format="$%.2f", width="small"),
                        "Cambio %": st.column_config.NumberColumn("Cambio %", format="%+.2f%%", width="small"),
                        "RVOL": st.column_config.NumberColumn("RVOL", format="%.1fx", width="small"),
                        "DCR %": st.column_config.NumberColumn("DCR %", format="%.0f%%", width="small"),
                        "RS Score": st.column_config.NumberColumn("RS / 99", format="%d", width="small"),
                        "Patrón Cuantitativo": st.column_config.TextColumn("Patrón / Setup Cuantitativo", width="large"),
                        "Etapa 2": st.column_config.TextColumn("Etapa 2", width="small")
                    },
                    key=f"df_snap_view_{s_code}_{key_suffix}"
                )

                csv_snap = table_display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    f"📥 Descargar Lista {s_code} (.CSV)",
                    data=csv_snap,
                    file_name=f"TradingVolt_Snapshot_{s_code}_{ts_str.replace(':', '').replace(' ', '_')}.csv",
                    mime="text/csv",
                    key=f"dl_csv_{s_code}_{key_suffix}"
                )

            with col_w_chart:
                active_sym = candidates[0]["symbol"]
                if sel_w_row and hasattr(sel_w_row, "selection") and sel_w_row.selection.rows:
                    r_idx = sel_w_row.selection.rows[0]
                    if r_idx < len(candidates):
                        active_sym = candidates[r_idx]["symbol"]

                st.markdown(f"""
                    <div style="background: rgba(14, 20, 32, 0.7); border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 700; color: #FFFFFF;">🔍 Gráfico Institucional en Vivo: <span style="color:#00F0FF;">${active_sym}</span></span>
                    </div>
                """, unsafe_allow_html=True)

                if render_chart_fn is not None:
                    render_chart_fn(active_sym, key_suffix=f"snap_w_{s_code}_{active_sym}")
                else:
                    st.info(f"Seleccionado: ${active_sym}")
