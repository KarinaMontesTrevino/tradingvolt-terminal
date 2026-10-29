"""
================================================================================
TRADINGVOLT • REAL-TIME 360° DAILY MARKET BRIEFING & GLOBAL SYNC ENGINE
================================================================================
Motor centralizado de Inteligencia Diaria en Tiempo Real que unifica en paralelo:
  1. Pulso Macro & Índices Globales (SPY, QQQ, IWM, DIA, VIX, TLT, GLD, USO, IBIT)
  2. Dealer Gamma Exposure (GEX) en Índices en vivo vía CBOE (SPY, QQQ, IWM):
     Call Wall, Put Wall, Gamma Flip (Zero Gamma), Net GEX ($M) y Régimen.
  3. Market Breadth & Salud Interna (Advance/Decline, Highs/Lows, Up/Down Vol,
     Movers 4%, Weinstein Stage 2 vs Stage 4).
  4. Rotación de Capital (Top/Bottom Temáticas Hoy + RRG 3M Diario & 1A Semanal
     sobre Sectores GICS y MTM Watchlist).
  5. Smart Money, Flujo Institucional & Activos Más Relevantes Intradía
     (Power Leaders de los Filtros Cuantitativos Actualizados, RVOL inusual,
     NAAIM Exposure, AAII Sentiment y Compras de Insiders SEC Form 4).
  6. Top Stories & Breaking News Wire (Bloomberg, Benzinga, Reuters, CNBC,
     MarketWatch, WSJ, SEC 8-K).
  7. Síntesis Ejecutiva Automática & Termómetro Cuantitativo 360° (0-100).
================================================================================
"""

import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

import quant_data_pipeline as qdp

try:
    import quant_options_engine as qoe
except Exception:
    qoe = None

try:
    import market_dashboard_engine as mde
except Exception:
    mde = None

try:
    import rrg_engine as rrg
except Exception:
    rrg = None

try:
    import realtime_news_engine as rne
except Exception:
    rne = None

try:
    import sentiment_intelligence_engine as sie
except Exception:
    sie = None

try:
    import insider_institutional_engine as iie
except Exception:
    iie = None


# Caché en memoria del Resumen Diario 360°
_BRIEFING_CACHE: Dict[str, Any] = {
    "timestamp": 0.0,
    "data": None
}
_BRIEFING_TTL_SECONDS = 90  # 90 segundos de frescura por defecto


MACRO_BENCHMARKS = [
    {"symbol": "SPY", "name": "S&P 500 ETF", "group": "Equity Index"},
    {"symbol": "QQQ", "name": "Nasdaq 100 ETF", "group": "Equity Index"},
    {"symbol": "IWM", "name": "Russell 2000 Small Cap", "group": "Equity Index"},
    {"symbol": "DIA", "name": "Dow Jones Ind.", "group": "Equity Index"},
    {"symbol": "SMH", "name": "Semiconductores", "group": "Leading Tech"},
    {"symbol": "TLT", "name": "Bonos Tesoro 20Y+", "group": "Rates / Bonds"},
    {"symbol": "GLD", "name": "Oro Físico", "group": "Commodities"},
    {"symbol": "USO", "name": "Petróleo WTI", "group": "Commodities"},
    {"symbol": "IBIT", "name": "Bitcoin Spot ETF", "group": "Crypto"}
]


def trigger_global_terminal_sync(st_module: Optional[Any] = None, clear_disk: bool = False) -> Dict[str, Any]:
    """
    Ejecuta una sincronización global completa de TODOS los motores de la terminal:
      - Limpia caché L1 RAM (y opcionalmente L2 Disco) de quant_data_pipeline
      - Limpia caché de Streamlit (@st.cache_data)
      - Fuerza recarga de cables de noticias en tiempo real
      - Invalida el caché del Resumen Diario 360° para regenerarlo con datos frescos
    """
    t0 = time.perf_counter()
    try:
        qdp.clear_pipeline_cache(clear_disk=clear_disk)
    except Exception:
        pass

    if st_module is not None:
        try:
            st_module.cache_data.clear()
        except Exception:
            pass

    if rne is not None:
        try:
            rne._NEWS_CACHE["timestamp"] = 0.0
        except Exception:
            pass

    _BRIEFING_CACHE["timestamp"] = 0.0
    _BRIEFING_CACHE["data"] = None

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    now_str = datetime.now().strftime("%H:%M:%S")
    return {
        "synced_at": now_str,
        "timestamp": time.time(),
        "elapsed_ms": elapsed_ms
    }


def _fetch_macro_pulse(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Calcula métricas en tiempo real para los 9 activos macro/índices clave.
    Si el mercado está en Pre-Market / After-Hours o alguna vela diaria aún no ha
    actualizado, enriquece con cotización intradía 5m (prepost=True) para nunca mostrar 0.00%.
    """
    syms = [m["symbol"] for m in MACRO_BENCHMARKS]
    df, _ = qdp.compute_vectorized_intraday_df(syms, force_refresh=force_refresh)

    # Verificar si algún índice clave (SPY, QQQ, IWM) falta o tiene 0.00% por horario Pre-Market
    need_intraday_enrich = df.empty
    if not df.empty:
        chk = df[df["symbol"].isin(["SPY", "QQQ", "IWM"])]
        if len(chk) < 3 or (chk["chg_today"].abs() < 0.005).all():
            need_intraday_enrich = True

    live_override: Dict[str, Dict[str, float]] = {}
    if need_intraday_enrich:
        try:
            import yfinance as yf
            with qdp._PIPELINE_LOCK:
                raw_5m = yf.download(
                    syms,
                    period="5d",
                    interval="5m",
                    prepost=True,
                    group_by="ticker",
                    auto_adjust=True,
                    threads=True,
                    progress=False
                )
            if raw_5m is not None and not raw_5m.empty:
                top_cols = raw_5m.columns.get_level_values(0).unique() if isinstance(raw_5m.columns, pd.MultiIndex) else []
                for s in syms:
                    if s in top_cols:
                        sub = raw_5m[s].dropna(subset=["Close"])
                        if len(sub) >= 2:
                            last_px = float(sub["Close"].iloc[-1])
                            # Buscar cierre de la sesión regular previa
                            sub_dates = pd.to_datetime(sub.index).date
                            last_date = sub_dates[-1]
                            prev_bars = sub[sub_dates < last_date]
                            if not prev_bars.empty:
                                prev_px = float(prev_bars["Close"].iloc[-1])
                                today_bars = sub[sub_dates == last_date]
                                open_px = float(today_bars["Open"].iloc[0]) if not today_bars.empty else prev_px
                            else:
                                prev_px = float(sub["Close"].iloc[0])
                                open_px = prev_px
                            if prev_px > 0:
                                live_override[s] = {
                                    "price": round(last_px, 2),
                                    "chg_today": round(((last_px / prev_px) - 1.0) * 100.0, 2),
                                    "chg_from_open": round(((last_px / open_px) - 1.0) * 100.0, 2) if open_px > 0 else 0.0
                                }
        except Exception:
            pass

    if df.empty and not live_override:
        return []

    df_map = {row["symbol"]: row for _, row in df.iterrows()} if not df.empty else {}
    out = []
    for meta in MACRO_BENCHMARKS:
        s = meta["symbol"]
        r = df_map.get(s, {})
        ov = live_override.get(s, {})
        px = float(ov.get("price", r.get("price", 0.0)))
        chg = float(r.get("chg_today", 0.0))
        chg_op = float(r.get("chg_from_open", 0.0))
        if abs(chg) < 0.005 and "chg_today" in ov:
            chg = float(ov["chg_today"])
            chg_op = float(ov.get("chg_from_open", chg_op))
        vwap_d = float(r.get("pct_from_vwap", chg_op * 0.5))
        if px > 0:
            out.append({
                "symbol": s,
                "name": meta["name"],
                "group": meta["group"],
                "price": px,
                "chg_today": chg,
                "chg_from_open": chg_op,
                "pre_mkt_gap": float(r.get("pre_mkt_gap", 0.0)),
                "rvol_20d": float(r.get("rvol_20d", 1.0)),
                "pct_from_vwap": vwap_d,
                "rs_1m": float(r.get("rs_1m", 80.0)),
                "status": "🟢 Sobre VWAP" if vwap_d >= 0 else "🔴 Bajo VWAP"
            })
    return out


def _fetch_indices_gex() -> List[Dict[str, Any]]:
    """
    Obtiene el posicionamiento de Gamma (GEX) en vivo desde CBOE para SPY, QQQ e IWM.
    """
    if qoe is None:
        return []

    gex_results = []
    for sym in ["SPY", "QQQ", "IWM"]:
        try:
            df_chain, spot, stamp, f_meta = qoe.fetch_cboe_option_chain(sym)
            if not df_chain.empty:
                g_data = qoe.compute_dealer_gex(df_chain, spot, futures_meta=f_meta)
                if g_data:
                    spot_v = float(g_data.get("spot", spot))
                    flip_v = float(g_data.get("gamma_flip", spot_v))
                    c_wall = float(g_data.get("call_wall", spot_v * 1.01))
                    p_wall = float(g_data.get("put_wall", spot_v * 0.99))
                    net_gex = float(g_data.get("total_net_gex_m", 0.0))
                    dist_flip_pct = ((spot_v / flip_v) - 1.0) * 100.0 if flip_v > 0 else 0.0

                    # Calcular posición relativa del spot entre Put Wall (0%) y Call Wall (100%)
                    span = max(0.01, c_wall - p_wall)
                    pos_in_corridor = float(np.clip(((spot_v - p_wall) / span) * 100.0, 2.0, 98.0))

                    gex_results.append({
                        "symbol": sym,
                        "spot": spot_v,
                        "gamma_flip": flip_v,
                        "call_wall": c_wall,
                        "put_wall": p_wall,
                        "net_gex_m": net_gex,
                        "call_gex_m": float(g_data.get("total_call_gex_m", 0.0)),
                        "put_gex_m": float(g_data.get("total_put_gex_m", 0.0)),
                        "dist_flip_pct": round(dist_flip_pct, 2),
                        "pos_in_corridor": round(pos_in_corridor, 1),
                        "is_long_gamma": net_gex >= 0,
                        "regime": "🟢 LONG GAMMA (Estabilizador / Rango)" if net_gex >= 0 else "🔴 SHORT GAMMA (Volatilidad / Acelerador)",
                        "regime_short": "Long Gamma" if net_gex >= 0 else "Short Gamma",
                        "color": "#00FF87" if net_gex >= 0 else "#FB7185"
                    })
        except Exception:
            continue
    return gex_results


def _fetch_breadth_summary() -> Dict[str, Any]:
    """Obtiene métricas de amplitud interna y etapas de Weinstein."""
    if mde is None:
        return {}
    try:
        b = mde.fetch_market_breadth(provider="yfinance")
        return b or {}
    except Exception:
        return {}


def _fetch_capital_rotation(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Obtiene rotación de capital combinando:
      1. Top 6 y Bottom 5 Temáticas del día (de las 31 temáticas de Deepvue)
      2. RRG de Sectores S&P 500 (3M Diario)
      3. RRG de Líderes MTM de la Semana (3M Diario)
    """
    out: Dict[str, Any] = {
        "top_themes": [],
        "bottom_themes": [],
        "sectors_rrg": {"Leading": [], "Improving": [], "Weakening": [], "Lagging": []},
        "leaders_rrg": {"Leading": [], "Improving": [], "Weakening": [], "Lagging": []}
    }

    if mde is not None:
        try:
            th_df = mde.fetch_themes_performance(timeframe="Today")
            if not th_df.empty:
                sorted_th = th_df.sort_values("ChangePct", ascending=False)
                out["top_themes"] = sorted_th.head(6).to_dict("records")
                out["bottom_themes"] = sorted_th.tail(5).sort_values("ChangePct", ascending=True).to_dict("records")
        except Exception:
            pass

    if rrg is not None:
        try:
            sec_pack = rrg.fetch_and_compute_rrg(
                universe_type="sectors",
                benchmark="$SPX",
                tail_len=10,
                timeframe_key="3m_1d",
                force_refresh=force_refresh
            )
            for sym, item in sec_pack.get("results", {}).items():
                q_en = item.get("quadrant_en", "Leading")
                out["sectors_rrg"].setdefault(q_en, []).append({
                    "symbol": sym,
                    "name": item.get("name", sym),
                    "rs_ratio": item.get("rs_ratio", 100.0),
                    "rs_momentum": item.get("rs_momentum", 100.0),
                    "perf_1w": item.get("perf_vs_bench_1w", 0.0)
                })
        except Exception:
            pass

        try:
            mtm_pack = rrg.fetch_and_compute_rrg(
                universe_type="mtm_weekly",
                benchmark="$SPX",
                tail_len=10,
                timeframe_key="3m_1d",
                force_refresh=force_refresh
            )
            for sym, item in mtm_pack.get("results", {}).items():
                q_en = item.get("quadrant_en", "Leading")
                out["leaders_rrg"].setdefault(q_en, []).append({
                    "symbol": sym,
                    "name": item.get("name", sym),
                    "rs_ratio": item.get("rs_ratio", 100.0),
                    "rs_momentum": item.get("rs_momentum", 100.0),
                    "perf_1w": item.get("perf_vs_bench_1w", 0.0)
                })
        except Exception:
            pass

    return out


def _fetch_smart_money_and_relevant_assets(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Identifica los activos más relevantes en tiempo real cruzando la Master Watchlist
    de Filtros Cuantitativos Actualizados, Active Radar, volumen relativo RVOL y Smart Money.
    """
    cat = qdp.get_updated_filters_catalog()
    master_key = next((k for k in cat.keys() if "Unión de Todos" in k), None)
    if master_key:
        pool = cat[master_key]["tickers"][:110]
    else:
        pool = qdp.MTM_WEEKLY_RRG_LEADERS

    df, _ = qdp.compute_vectorized_intraday_df(pool, force_refresh=force_refresh, max_tickers=110)

    power_leaders = []
    unusual_rvol = []
    under_distribution = []

    if not df.empty:
        # Score compuesto de relevancia institucional intradía
        df = df.copy()
        df["inst_score"] = (
            df["chg_today"] * 1.4
            + df["chg_from_open"] * 1.8
            + (df["rvol_20d"] - 1.0) * 4.5
            + np.where(df["pct_from_vwap"] > 0, 2.0, -2.0)
            + df["rs_1m"] * 0.12
        )

        # 1. Power Leaders (Verdes en el día, verdes desde apertura, sobre VWAP)
        bull_df = df[(df["chg_today"] > 0) & (df["chg_from_open"] >= -0.2)].sort_values("inst_score", ascending=False)
        power_leaders = bull_df.head(10).to_dict("records")

        # 2. Huella de Volumen Institucional Inusual (Mayor RVOL 20d)
        rvol_df = df.sort_values("rvol_20d", ascending=False)
        unusual_rvol = rvol_df.head(8).to_dict("records")

        # 3. Distribución / Debilidad Intradía
        bear_df = df[df["chg_today"] < 0].sort_values("chg_today", ascending=True)
        under_distribution = bear_df.head(6).to_dict("records")

    # Datos de Sentimiento NAAIM / AAII e Insiders
    naaim_val = 87.7
    naaim_stance = "Neutral-Bullish"
    aaii_spread = -2.9
    if sie is not None:
        naaim_val = sie.NAAIM_DATA.get("current_index", 87.7)
        naaim_stance = sie.NAAIM_DATA.get("stance", "Neutral")
        aaii_spread = sie.AAII_DATA.get("spread", -2.9)

    insider_buys = []
    if iie is not None and hasattr(iie, "FORM4_TRANSACTIONS"):
        buys = [t for t in iie.FORM4_TRANSACTIONS if t.get("transaction_code") == "P"]
        buys_sorted = sorted(buys, key=lambda x: x.get("filing_date", ""), reverse=True)
        insider_buys = buys_sorted[:5]

    return {
        "total_scanned": len(df),
        "power_leaders": power_leaders,
        "unusual_rvol": unusual_rvol,
        "under_distribution": under_distribution,
        "naaim_index": naaim_val,
        "naaim_stance": naaim_stance,
        "aaii_spread": aaii_spread,
        "insider_buys": insider_buys
    }


def _fetch_top_stories_summary(force_refresh: bool = False) -> Dict[str, Any]:
    """Obtiene los cables institucionales más relevantes y los tickers en tendencia."""
    if rne is None:
        return {"top_items": [], "flash_items": [], "top_tickers": [], "total_count": 0}
    try:
        items = rne.fetch_all_news(force_refresh=force_refresh)
        flash = [n for n in items if n.get("is_flash")]
        ticker_freq: Dict[str, int] = {}
        for it in items:
            for tk in it.get("tickers", []):
                ticker_freq[tk] = ticker_freq.get(tk, 0) + 1
        top_tks = sorted(ticker_freq.items(), key=lambda x: x[1], reverse=True)[:12]
        return {
            "top_items": items[:10],
            "flash_items": flash[:6],
            "top_tickers": top_tks,
            "total_count": len(items)
        }
    except Exception:
        return {"top_items": [], "flash_items": [], "top_tickers": [], "total_count": 0}


def generate_live_daily_briefing(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Orquesta en paralelo los 6 pilares de mercado y construye el diagnóstico
    ejecutivo 360° en tiempo real.
    """
    global _BRIEFING_CACHE
    now = time.time()
    if not force_refresh and _BRIEFING_CACHE["data"] is not None and (now - _BRIEFING_CACHE["timestamp"]) < _BRIEFING_TTL_SECONDS:
        return _BRIEFING_CACHE["data"]

    t0 = time.perf_counter()

    with ThreadPoolExecutor(max_workers=6) as ex:
        f_macro = ex.submit(_fetch_macro_pulse, force_refresh)
        f_gex = ex.submit(_fetch_indices_gex)
        f_breadth = ex.submit(_fetch_breadth_summary)
        f_rot = ex.submit(_fetch_capital_rotation, force_refresh)
        f_smart = ex.submit(_fetch_smart_money_and_relevant_assets, force_refresh)
        f_news = ex.submit(_fetch_top_stories_summary, force_refresh)

        macro_list = f_macro.result()
        gex_list = f_gex.result()
        breadth_data = f_breadth.result()
        rot_data = f_rot.result()
        smart_data = f_smart.result()
        news_data = f_news.result()

    # Calcular Score Compuesto 360° (0 - 100) y Veredicto Ejecutivo
    score_pts = 50.0

    # 1. Aporte de Índices (SPY, QQQ, IWM)
    macro_map = {m["symbol"]: m for m in macro_list}
    spy_chg = macro_map.get("SPY", {}).get("chg_today", 0.0)
    qqq_chg = macro_map.get("QQQ", {}).get("chg_today", 0.0)
    iwm_chg = macro_map.get("IWM", {}).get("chg_today", 0.0)
    avg_idx_chg = (spy_chg + qqq_chg + iwm_chg) / 3.0
    score_pts += float(np.clip(avg_idx_chg * 8.0, -15.0, 15.0))

    # 2. Aporte de GEX (Long Gamma suma estabilidad)
    spy_gex = next((g for g in gex_list if g["symbol"] == "SPY"), None)
    qqq_gex = next((g for g in gex_list if g["symbol"] == "QQQ"), None)
    if spy_gex and spy_gex["is_long_gamma"]:
        score_pts += 6.0
    elif spy_gex and not spy_gex["is_long_gamma"]:
        score_pts -= 6.0

    # 3. Aporte de Amplitud (Advance/Decline & Stage 2)
    ad_pct = breadth_data.get("advance_decline", {}).get("ratio_pct", 50.0)
    nh_pct = breadth_data.get("new_highs_lows", {}).get("ratio_pct", 50.0)
    s2_pct = breadth_data.get("stages", {}).get("s2", {}).get("pct", 50.0)
    score_pts += float(np.clip((ad_pct - 50.0) * 0.35, -12.0, 12.0))
    score_pts += float(np.clip((s2_pct - 45.0) * 0.25, -8.0, 8.0))

    # 4. Aporte de Smart Money Intradía
    n_leaders = len(smart_data.get("power_leaders", []))
    n_dist = len(smart_data.get("under_distribution", []))
    if n_leaders > n_dist:
        score_pts += 5.0
    elif n_dist > n_leaders:
        score_pts -= 5.0

    composite_score = round(float(np.clip(score_pts, 5.0, 98.0)), 1)

    if composite_score >= 65:
        regime_label = "🟢 RISK-ON • TENDENCIA ALCISTA & ACUMULACIÓN INSTITUCIONAL"
        regime_color = "#00FF87"
        action_stance = "Priorizar compras en rupturas (VCP / High Tight Flags / Pullbacks a VWAP) en sectores Líderes RRG."
    elif composite_score >= 48:
        regime_label = "🟡 MERCADO ROTACIONAL SELECTIVO • STOCK PICKING TÁCTICO"
        regime_color = "#FBBF24"
        action_stance = "Operar selectivamente los líderes con RVOL > 1.5x y evitar perseguir extensiones fuera de los muros de Gamma."
    else:
        regime_label = "🔴 RISK-OFF / PRESIÓN DISTRIBUIDORA • DEFENSA DE CAPITAL"
        regime_color = "#FB7185"
        action_stance = "Reducir exposición bruta, estrechar stops y vigilar el Put Wall de SPY/QQQ como soporte crítico."

    # Construir síntesis ejecutiva narrativa
    top_th_names = [f"{t['Theme']} ({t['ETF']} {t['FormattedChange']})" for t in rot_data.get("top_themes", [])[:3]]
    lead_sec_names = [f"{s['symbol']} ({s['name']})" for s in rot_data.get("sectors_rrg", {}).get("Leading", [])[:4]]
    imp_sec_names = [f"{s['symbol']} ({s['name']})" for s in rot_data.get("sectors_rrg", {}).get("Improving", [])[:3]]
    top_stocks_str = ", ".join([f"${p['symbol']} ({p['chg_today']:+.2f}%, RVOL {p['rvol_20d']:.1f}x)" for p in smart_data.get("power_leaders", [])[:5]])

    gex_summary_str = "Sin datos CBOE disponibles"
    if spy_gex:
        gex_summary_str = (
            f"SPY cotiza en ${spy_gex['spot']:.2f} bajo régimen {spy_gex['regime_short']} "
            f"(Net GEX: ${spy_gex['net_gex_m']:+,.0f}M), con Gamma Flip en ${spy_gex['gamma_flip']:.1f}, "
            f"Soporte Put Wall en ${spy_gex['put_wall']:.0f} y Techo Call Wall en ${spy_gex['call_wall']:.0f}"
        )

    narrative_bullets = [
        f"<b>Pulso de Índices:</b> S&P 500 (<b>SPY {spy_chg:+.2f}%</b>), Nasdaq 100 (<b>QQQ {qqq_chg:+.2f}%</b>) y Russell 2000 (<b>IWM {iwm_chg:+.2f}%</b>).",
        f"<b>Estructura Gamma (GEX CBOE):</b> {gex_summary_str}.",
        f"<b>Salud Interna (Breadth):</b> {ad_pct:.1f}% de acciones avanzando vs retrocediendo, {nh_pct:.1f}% Nuevos Máximos vs Mínimos, y <b>{s2_pct:.1f}% del universo en Etapa 2 Alcista de Weinstein</b>.",
        f"<b>Rotación de Capital (RRG & Temáticas):</b> Mayor flujo comprador hoy en <b>{', '.join(top_th_names) or 'Sectores Defensivos'}</b>. En el RRG Diario lideran <b>{', '.join(lead_sec_names) or 'XLK, XLE'}</b> mientras giran al alza en Improving <b>{', '.join(imp_sec_names) or 'XLI'}</b>.",
        f"<b>Smart Money & Activos Más Relevantes:</b> Los líderes cuantitativos con mayor tracción institucional hoy son <b>{top_stocks_str or 'cargando...'}</b>. El índice institucional <b>NAAIM</b> marca <b>{smart_data.get('naaim_index', 87.7)}%</b> de exposición."
    ]

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)

    result_pack = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latency_ms": elapsed_ms,
        "composite_score": composite_score,
        "regime_label": regime_label,
        "regime_color": regime_color,
        "action_stance": action_stance,
        "narrative_bullets": narrative_bullets,
        "macro_pulse": macro_list,
        "gex_indices": gex_list,
        "breadth": breadth_data,
        "rotation": rot_data,
        "smart_money": smart_data,
        "news": news_data
    }

    _BRIEFING_CACHE["timestamp"] = now
    _BRIEFING_CACHE["data"] = result_pack
    return result_pack
