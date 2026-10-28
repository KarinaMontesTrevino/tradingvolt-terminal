"""
TradingVolt Quant Options & GEX Engine
======================================
Integra:
1. Dealer Gamma Exposure (GEX), Gamma Flip y Muros de Opciones en vivo desde CBOE.
   Soporte para:
   - Futuros de Índices: ES (E-mini S&P 500) y NQ (E-mini Nasdaq 100) con base en tiempo real.
   - Acciones / ETFs: SPY, QQQ, SPX, NDX, IWM, NVDA.
2. Valoración multi-modelo institucional con QuantLib (Black-Scholes, Black-76 para Futuros,
   Binomial CRR, Bjerksund-Stensland, Barone-Adesi, Diferencias Finitas) y Griegas de 1° y 2° orden.
"""

import os
import sys
import json
import re
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm
import yfinance as yf

# QuantLib
try:
    import QuantLib as ql
    QUANTLIB_AVAILABLE = True
except ImportError:
    QUANTLIB_AVAILABLE = False

# CBOE Constants & Endpoints
CBOE_ENDPOINTS = {
    "SPY": "https://cdn.cboe.com/api/global/delayed_quotes/options/SPY.json",
    "QQQ": "https://cdn.cboe.com/api/global/delayed_quotes/options/QQQ.json",
    "SPX": "https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json",
    "_SPX": "https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json",
    "NDX": "https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json",
    "_NDX": "https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json",
    "ES": "https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json",
    "NQ": "https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json",
    "IWM": "https://cdn.cboe.com/api/global/delayed_quotes/options/IWM.json",
    "NVDA": "https://cdn.cboe.com/api/global/delayed_quotes/options/NVDA.json"
}

FUTURES_MAP = {
    "ES": {"ticker": "ES=F", "cash": "SPX", "name": "E-mini S&P 500 Futures", "multiplier": 50, "cboe_chain": "_SPX"},
    "NQ": {"ticker": "NQ=F", "cash": "NDX", "name": "E-mini Nasdaq 100 Futures", "multiplier": 20, "cboe_chain": "_NDX"}
}

OCC_PATTERN = re.compile(r"^(?P<root>[A-Z_]+)(?P<ymd>\d{6})(?P<side>[CP])(?P<strike>\d{8})$")
MULTIPLIER = 100
YEAR_HOURS = 365.25 * 24

def fetch_cboe_option_chain(symbol: str = "SPY") -> tuple[pd.DataFrame, float, str, dict]:
    """
    Descarga la cadena completa de opciones desde CBOE para el activo o futuro.
    Devuelve (df_chain, spot_price, timestamp, futures_meta).
    """
    sym = symbol.upper().replace("^", "_")
    is_futures = sym in FUTURES_MAP
    f_info = FUTURES_MAP.get(sym, None)
    
    # URL de CBOE correspondiente
    cboe_sym = f_info["cboe_chain"] if is_futures else sym
    url = CBOE_ENDPOINTS.get(cboe_sym, f"https://cdn.cboe.com/api/global/delayed_quotes/options/{cboe_sym}.json")
    
    req = urllib.request.Request(url, headers={"User-Agent": "TradingVolt-Institutional/2.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
        
    cash_spot = float(raw["data"]["current_price"])
    stamp = raw.get("timestamp") or datetime.now().isoformat()
    today = date.fromisoformat(stamp[:10])
    
    # Si es futuro (ES o NQ), obtener la cotización del futuro en vivo para calcular la base
    futures_meta = {"is_futures": False, "basis": 0.0, "multiplier": 100}
    spot = cash_spot
    
    if is_futures:
        try:
            f_ticker = yf.Ticker(f_info["ticker"])
            f_hist = f_ticker.history(period="1d")
            if not f_hist.empty:
                futures_spot = float(f_hist["Close"].iloc[-1])
            else:
                futures_spot = cash_spot
        except Exception:
            futures_spot = cash_spot
            
        basis = futures_spot - cash_spot
        futures_meta = {
            "is_futures": True,
            "futures_symbol": sym,
            "futures_ticker": f_info["ticker"],
            "futures_name": f_info["name"],
            "futures_price": round(futures_spot, 2),
            "cash_symbol": f_info["cash"],
            "cash_price": round(cash_spot, 2),
            "basis": round(basis, 2),
            "multiplier": f_info["multiplier"]
        }
        spot = futures_spot
    
    rows = []
    for opt in raw["data"].get("options", []):
        m = OCC_PATTERN.match(opt.get("option", ""))
        if m:
            exp_date = date(2000 + int(m["ymd"][:2]), int(m["ymd"][2:4]), int(m["ymd"][4:]))
            strike = int(m["strike"]) / 1000.0
            is_call = (m["side"] == "C")
            oi = float(opt.get("open_interest", 0.0))
            iv = float(opt.get("iv", 0.0))
            vol = float(opt.get("volume", 0.0))
            last = float(opt.get("last_trade_price", 0.0))
            bid = float(opt.get("bid", 0.0))
            ask = float(opt.get("ask", 0.0))
            
            rows.append({
                "option": opt.get("option"),
                "expiry": exp_date,
                "is_call": is_call,
                "strike": strike,
                "oi": oi,
                "iv": iv,
                "volume": vol,
                "last": last,
                "bid": bid,
                "ask": ask
            })
            
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(), spot, stamp, futures_meta
        
    df["days"] = [(e - today).days for e in df.expiry]
    # Filtrar strikes razonables (dentro del +/- 25% del spot de contado) y días >= 0
    df = df[(df.days >= 0) & (df.oi > 0) & (np.abs(np.log(df.strike / cash_spot)) < 0.25)].reset_index(drop=True)
    df["same_day"] = (df.days == 0)
    
    # Imputar IV para opciones con IV vacía o defectuosa
    valid_iv = df[df.iv > 0.01]
    if not valid_iv.empty:
        median_iv = valid_iv["iv"].median()
        df["iv"] = np.where(df.iv < 0.01, median_iv, df.iv)
    else:
        df["iv"] = 0.15
        
    return df, spot, stamp, futures_meta

def calculate_black_scholes_gamma(S, K, T, sigma, r=0.045):
    """Calcula Gamma de Black-Scholes vectorizado."""
    T = np.maximum(T, 1e-4)
    sigma = np.maximum(sigma, 1e-4)
    srt = sigma * np.sqrt(T)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / srt
    gamma = np.exp(-0.5 * d1 ** 2) / (np.sqrt(2 * np.pi) * S * srt)
    return gamma

def compute_dealer_gex(df: pd.DataFrame, spot: float, r: float = 0.045, futures_meta: dict = None) -> dict:
    """Calcula la exposición total de Gamma de los creadores de mercado (GEX) y el Gamma Flip."""
    if df.empty:
        return {}
        
    is_futures = futures_meta and futures_meta.get("is_futures", False)
    cash_spot = futures_meta.get("cash_price", spot) if is_futures else spot
    basis = futures_meta.get("basis", 0.0) if is_futures else 0.0
    
    # Dealer convention: Dealers typically LONG calls, SHORT puts (contraparte del retail/institucional)
    sign = np.where(df.is_call, 1.0, -1.0)
    T = np.where(df.same_day, 6.0 / YEAR_HOURS, np.maximum(df.days, 0.5) / 365.25)
    
    # Gamma de cada contrato usando el spot de contado (SPX o NDX para opciones CBOE)
    gammas = calculate_black_scholes_gamma(cash_spot, df.strike.to_numpy(), T, df.iv.to_numpy(), r=r)
    
    # GEX en dólares por movimiento del 1% del spot ($ Millions per 1%)
    gex_contract_m = (sign * gammas * df.oi.to_numpy() * MULTIPLIER * (cash_spot ** 2) * 0.01) / 1e6
    df["gex_m"] = gex_contract_m
    
    # GEX por llamada y put
    df["call_gex_m"] = np.where(df.is_call, gex_contract_m, 0.0)
    df["put_gex_m"] = np.where(~df.is_call, gex_contract_m, 0.0) # negativo
    
    total_net_gex = float(df["gex_m"].sum())
    total_call_gex = float(df["call_gex_m"].sum())
    total_put_gex = float(df["put_gex_m"].sum())
    
    # GEX agrupado por Strike
    strike_agg = df.groupby("strike").agg({
        "gex_m": "sum",
        "call_gex_m": "sum",
        "put_gex_m": "sum",
        "oi": "sum",
        "volume": "sum"
    }).reset_index().sort_values("strike")
    
    # Si es futuro, añadir columna de strike en puntos de futuro
    strike_agg["strike_display"] = strike_agg["strike"] + basis if is_futures else strike_agg["strike"]
    
    # Call Wall (strike con mayor Call GEX o Call OI)
    call_wall_row = strike_agg.loc[strike_agg["call_gex_m"].idxmax()] if not strike_agg.empty else None
    call_wall = float(call_wall_row["strike"]) if call_wall_row is not None else cash_spot
    
    # Put Wall (strike con mayor Put GEX negativo / Put OI)
    put_wall_row = strike_agg.loc[strike_agg["put_gex_m"].idxmin()] if not strike_agg.empty else None
    put_wall = float(put_wall_row["strike"]) if put_wall_row is not None else cash_spot
    
    # Gamma Flip: Simular el perfil de GEX en una rejilla alrededor de spot para encontrar el cruce por cero
    grid_prices = np.linspace(cash_spot * 0.94, cash_spot * 1.06, 120)
    profile_gex = []
    for test_s in grid_prices:
        test_gamma = calculate_black_scholes_gamma(test_s, df.strike.to_numpy(), T, df.iv.to_numpy(), r=r)
        test_gex = (sign * test_gamma * df.oi.to_numpy() * MULTIPLIER * (test_s ** 2) * 0.01 / 1e6).sum()
        profile_gex.append(float(test_gex))
        
    profile_gex = np.array(profile_gex)
    
    # Encontrar el punto donde profile_gex cruza de negativo a positivo
    gamma_flip = None
    min_dist = float("inf")
    for i in range(len(grid_prices) - 1):
        if (profile_gex[i] <= 0 and profile_gex[i+1] >= 0) or (profile_gex[i] >= 0 and profile_gex[i+1] <= 0):
            s1, s2 = grid_prices[i], grid_prices[i+1]
            g1, g2 = profile_gex[i], profile_gex[i+1]
            zero_s = s1 - g1 * (s2 - s1) / (g2 - g1 + 1e-9)
            if abs(zero_s - cash_spot) < min_dist:
                min_dist = abs(zero_s - cash_spot)
                gamma_flip = float(zero_s)
                
    if gamma_flip is None:
        gamma_flip = cash_spot if total_net_gex >= 0 else cash_spot * 1.02
        
    # Régimen de Gamma
    regime = "Long Gamma (Amortiguador / Rango)" if total_net_gex >= 0 else "Short Gamma (Acelerador / Volatilidad)"
    regime_color = "#00FF87" if total_net_gex >= 0 else "#FF0055"
    
    # Coordenadas en puntos de futuros si aplica
    call_wall_display = call_wall + basis if is_futures else call_wall
    put_wall_display = put_wall + basis if is_futures else put_wall
    gamma_flip_display = gamma_flip + basis if is_futures else gamma_flip
    grid_prices_display = grid_prices + basis if is_futures else grid_prices
    
    return {
        "spot": round(spot, 2),
        "cash_spot": round(cash_spot, 2),
        "basis": round(basis, 2),
        "is_futures": is_futures,
        "futures_meta": futures_meta or {},
        "total_net_gex_m": round(total_net_gex, 2),
        "total_call_gex_m": round(total_call_gex, 2),
        "total_put_gex_m": round(total_put_gex, 2),
        "call_wall": round(call_wall_display, 2),
        "put_wall": round(put_wall_display, 2),
        "gamma_flip": round(gamma_flip_display, 2),
        "call_wall_cash": round(call_wall, 2),
        "put_wall_cash": round(put_wall, 2),
        "gamma_flip_cash": round(gamma_flip, 2),
        "regime": regime,
        "regime_color": regime_color,
        "strike_data": strike_agg,
        "profile_grid": grid_prices_display,
        "profile_gex": profile_gex
    }

# =====================================================================
# QUANTLIB MULTI-MODEL PRICER
# =====================================================================

def price_option_quantlib(spot: float, strike: float, dte_days: int, iv: float,
                          rate: float = 0.045, div_yield: float = 0.013,
                          is_call: bool = True, is_futures: bool = False,
                          multiplier: int = 100) -> dict:
    """
    Calcula el precio de una opción usando 6 modelos en QuantLib y extrae las Griegas completas.
    Soporta opciones sobre acciones/ETFs y opciones sobre futuros (Black-76 con q=r).
    """
    effective_div = rate if is_futures else div_yield
    
    if not QUANTLIB_AVAILABLE:
        return _fallback_black_scholes_pricing(spot, strike, dte_days, iv, rate, is_call, multiplier, is_futures)
        
    try:
        eval_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = eval_date
        
        calendar = ql.TARGET()
        day_count = ql.Actual365Fixed()
        settlement_date = eval_date
        
        maturity_date = eval_date + ql.Period(max(1, int(dte_days)), ql.Days)
        
        opt_type = ql.Option.Call if is_call else ql.Option.Put
        payoff = ql.PlainVanillaPayoff(opt_type, float(strike))
        
        european_exercise = ql.EuropeanExercise(maturity_date)
        american_exercise = ql.AmericanExercise(settlement_date, maturity_date)
        
        european_option = ql.VanillaOption(payoff, european_exercise)
        american_option = ql.VanillaOption(payoff, american_exercise)
        
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(float(spot)))
        rate_curve = ql.YieldTermStructureHandle(ql.FlatForward(settlement_date, float(rate), day_count))
        div_curve = ql.YieldTermStructureHandle(ql.FlatForward(settlement_date, float(effective_div), day_count))
        vol_curve = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(settlement_date, calendar, float(iv), day_count))
        
        bs_process = ql.BlackScholesMertonProcess(spot_handle, div_curve, rate_curve, vol_curve)
        
        # 1. Analytic European (Black-Scholes / Black-76)
        bs_engine = ql.AnalyticEuropeanEngine(bs_process)
        european_option.setPricingEngine(bs_engine)
        p_bs = european_option.NPV()
        delta = european_option.delta()
        gamma = european_option.gamma()
        vega = european_option.vega() / 100.0 # por 1% vol
        theta = european_option.theta() / 365.0 # por día
        rho = european_option.rho() / 100.0 # por 1% rate
        
        # 2. Barone-Adesi / Whaley (American Analytic Approximation)
        baw_engine = ql.BaroneAdesiWhaleyApproximationEngine(bs_process)
        american_option.setPricingEngine(baw_engine)
        p_baw = american_option.NPV()
        
        # 3. Bjerksund / Stensland (American Analytic Approximation)
        bs2_engine = ql.BjerksundStenslandApproximationEngine(bs_process)
        american_option.setPricingEngine(bs2_engine)
        p_bjerksund = american_option.NPV()
        
        # 4. Binomial Cox-Ross-Rubinstein (CRR - 200 pasos)
        crr_engine = ql.BinomialVanillaEngine(bs_process, "CRR", 200)
        american_option.setPricingEngine(crr_engine)
        p_crr = american_option.NPV()
        
        # 5. Binomial Leisen-Reimer (LR - 200 pasos)
        lr_engine = ql.BinomialVanillaEngine(bs_process, "LR", 200)
        american_option.setPricingEngine(lr_engine)
        p_lr = american_option.NPV()
        
        # 6. Finite Differences (Crank-Nicolson PDE)
        fd_engine = ql.FdBlackScholesVanillaEngine(bs_process, 200, 200)
        american_option.setPricingEngine(fd_engine)
        p_fd = american_option.NPV()
        
        # Vanna y Volga numérico
        d_vol = 0.005
        vol_up = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(settlement_date, calendar, float(iv + d_vol), day_count))
        vol_dn = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(settlement_date, calendar, float(max(0.01, iv - d_vol)), day_count))
        
        bs_proc_up = ql.BlackScholesMertonProcess(spot_handle, div_curve, rate_curve, vol_up)
        bs_proc_dn = ql.BlackScholesMertonProcess(spot_handle, div_curve, rate_curve, vol_dn)
        
        opt_up = ql.VanillaOption(payoff, european_exercise)
        opt_up.setPricingEngine(ql.AnalyticEuropeanEngine(bs_proc_up))
        opt_dn = ql.VanillaOption(payoff, european_exercise)
        opt_dn.setPricingEngine(ql.AnalyticEuropeanEngine(bs_proc_dn))
        
        delta_up = opt_up.delta()
        delta_dn = opt_dn.delta()
        vanna = (delta_up - delta_dn) / (2 * d_vol) / 100.0
        
        vega_up = opt_up.vega()
        vega_dn = opt_dn.vega()
        volga = (vega_up - vega_dn) / (2 * d_vol) / 100.0
        
        early_exercise_premium = max(0.0, p_bjerksund - p_bs)
        
        # Valor monetario total por contrato
        contract_cost_bs = p_bs * multiplier
        contract_cost_amer = p_bjerksund * multiplier
        
        model_name_bs = "Black-76 (Europea)" if is_futures else "Black-Scholes (Europea)"
        
        return {
            "success": True,
            "is_futures": is_futures,
            "multiplier": multiplier,
            "contract_cost_bs": round(contract_cost_bs, 2),
            "contract_cost_amer": round(contract_cost_amer, 2),
            "models": {
                model_name_bs: round(p_bs, 4),
                "Bjerksund-Stensland (Americana)": round(p_bjerksund, 4),
                "Barone-Adesi / Whaley (Americana)": round(p_baw, 4),
                "Binomial CRR 200 (Americana)": round(p_crr, 4),
                "Binomial Leisen-Reimer (Americana)": round(p_lr, 4),
                "Diferencias Finitas PDE (Americana)": round(p_fd, 4),
            },
            "early_exercise_premium": round(early_exercise_premium, 4),
            "greeks": {
                "Delta": round(delta, 4),
                "Gamma": round(gamma, 6 if is_futures else 4),
                "Vega (1%)": round(vega, 4),
                "Theta (1d)": round(theta, 4),
                "Rho (1%)": round(rho, 4),
                "Vanna": round(vanna, 4),
                "Volga": round(volga, 4)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def _fallback_black_scholes_pricing(S, K, dte, sigma, r, is_call, multiplier=100, is_futures=False):
    """Fallback analítico en scipy si QuantLib fallara."""
    T = max(dte, 1) / 365.25
    q = r if is_futures else 0.013
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if is_call:
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = np.exp(-q * T) * norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        delta = -np.exp(-q * T) * norm.cdf(-d1)
    gamma = np.exp(-q * T) * norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100.0
    theta = (-(S * sigma * np.exp(-q * T) * norm.pdf(d1)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if is_call else -d2)) / 365.0
    return {
        "success": True,
        "is_futures": is_futures,
        "multiplier": multiplier,
        "contract_cost_bs": round(price * multiplier, 2),
        "contract_cost_amer": round(price * multiplier, 2),
        "models": {"Black-76 (Futuros)" if is_futures else "Black-Scholes (Estándar)": round(price, 4)},
        "early_exercise_premium": 0.0,
        "greeks": {
            "Delta": round(delta, 4),
            "Gamma": round(gamma, 6 if is_futures else 4),
            "Vega (1%)": round(vega, 4),
            "Theta (1d)": round(theta, 4),
            "Rho (1%)": 0.0,
            "Vanna": 0.0,
            "Volga": 0.0
        }
    }
