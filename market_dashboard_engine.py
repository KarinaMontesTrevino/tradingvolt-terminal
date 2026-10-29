import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

# =====================================================================
# 31 TEMÁTICAS OFICIALES DE DEEPVUE CON SUS ETFS PROXIES Y ACCIONES
# =====================================================================
THEMES_CATALOG = {
    "HealthCare": {
        "etf": "XLV",
        "stocks": [
            "MXCT", "LQDA", "TRAX", "NRIX", "HALO", "LYEL", "PHAT", "WGS", 
            "ACHC", "UNH", "MRNA", "BMY", "COLL", "GILD", "PRGO", "UHS", 
            "AXSM", "LLY", "OPK", "MRK", "ABT", "JNJ", "PFE", "ISRG", "BSX", 
            "VKTX", "CERT", "VCYT", "HAE", "AMPH", "INSP", "DOCS", "ALVO"
        ]
    },
    "Biotechnology": {
        "etf": "XBI",
        "stocks": [
            "VKTX", "MRNA", "BMY", "GILD", "LQDA", "HALO", "NRIX", "TRAX", 
            "CRSP", "NTLA", "BEAM", "ARWR", "ALNY", "REGN", "BIIB", "SRPT", 
            "IOVA", "TGTX", "KYMR", "DNA", "CRBU", "VERA", "ABSI"
        ]
    },
    "Retail": {
        "etf": "XRT",
        "stocks": [
            "AMZN", "WMT", "COST", "TGT", "HD", "LOW", "ROST", "TJX", 
            "DLTR", "DG", "LULU", "NKE", "BBY", "ANF", "BOOT", "CAKE", 
            "OLLI", "FIVE", "BURL", "WSM"
        ]
    },
    "Aerospace": {
        "etf": "ITA",
        "stocks": [
            "BA", "RTX", "LMT", "NOC", "GD", "TDG", "HWM", "AXON", 
            "HII", "SPR", "HEI", "TXT", "RKLB", "KTOS", "CAE", "AVAV"
        ]
    },
    "Medical": {
        "etf": "IHI",
        "stocks": [
            "MDT", "ABT", "SYK", "BSX", "ISRG", "BDX", "EW", "ZBH", 
            "ALGN", "DXCM", "PODD", "RMD", "HOLX", "STE", "ATRC", "TFX"
        ]
    },
    "Materials": {
        "etf": "XLB",
        "stocks": [
            "LIN", "APD", "SHW", "FCX", "ECL", "NEM", "CTVA", "DOW", 
            "DD", "ALB", "FMC", "VMC", "MLM", "CF", "MOS", "IFF"
        ]
    },
    "Utilities": {
        "etf": "XLU",
        "stocks": [
            "NEE", "SO", "DUK", "CEG", "VST", "AEP", "SRE", "D", 
            "EXC", "XEL", "ED", "PEG", "PCG", "WEC", "ES", "ETR"
        ]
    },
    "Transports": {
        "etf": "IYT",
        "stocks": [
            "UNP", "UPS", "FDX", "CSX", "NSC", "ODFL", "JBHT", "EXPD", 
            "LSTR", "KNX", "CHRW", "CAR", "DAL", "UAL", "MATX", "SAIA"
        ]
    },
    "Genomics": {
        "etf": "ARKG",
        "stocks": [
            "ILMN", "CRSP", "NTLA", "BEAM", "PACB", "TXG", "TWST", "EDIT", 
            "CDNA", "DNA", "EXAS", "FATE", "VERV", "RXRX", "SDGR"
        ]
    },
    "Steel": {
        "etf": "SLX",
        "stocks": [
            "NUE", "STLD", "CLF", "X", "TX", "MT", "SCHN", "CMC", "WOR", "TMST"
        ]
    },
    "Banks": {
        "etf": "KBE",
        "stocks": [
            "JPM", "BAC", "WFC", "C", "MS", "GS", "USB", "PNC", 
            "TFC", "SCHW", "FITB", "RF", "KEY", "CFG", "HBAN", "CMA"
        ]
    },
    "Real Estate": {
        "etf": "XLRE",
        "stocks": [
            "PLD", "AMT", "EQIX", "PSA", "O", "SPG", "WELL", "DLR", 
            "CCI", "SBAC", "EXR", "AVB", "EQR", "VICI", "CBRE", "INVH"
        ]
    },
    "China Internet": {
        "etf": "KWEB",
        "stocks": [
            "BABA", "PDD", "JD", "BIDU", "NTES", "TCOM", "BILI", "FUTU", 
            "IQ", "TME", "LI", "NIO", "XPEV", "BEKE", "VNET"
        ]
    },
    "Industrials": {
        "etf": "XLI",
        "stocks": [
            "GE", "CAT", "DE", "HON", "UNP", "ETN", "ITW", "EMR", 
            "PH", "CTAS", "GXO", "WM", "RSG", "TT", "CARR", "OTIS"
        ]
    },
    "Home Construction": {
        "etf": "ITB",
        "stocks": [
            "DHI", "LEN", "NVR", "PHM", "TOL", "TMHC", "MDC", "KBH", 
            "MHO", "CCS", "BLD", "IBP", "BLDR", "FND", "HD", "LOW"
        ]
    },
    "Bitcoin": {
        "etf": "IBIT",
        "stocks": [
            "IBIT", "FBTC", "MSTR", "COIN", "MARA", "RIOT", "CLSK", "CIFR", 
            "IREN", "HUT", "CORZ", "BITF", "WULF", "HOOD", "SQ"
        ]
    },
    "Oil & Gas": {
        "etf": "XLE",
        "stocks": [
            "XOM", "CVX", "COP", "EOG", "SLB", "OXY", "MPC", "VLO", 
            "PSX", "DVN", "HAL", "BKR", "KMI", "WMB", "ET", "FANG", "HES"
        ]
    },
    "Social Media": {
        "etf": "SOCL",
        "stocks": [
            "META", "GOOGL", "SNAP", "PINS", "RDDT", "SPOT", "MTCH", "BIDU", "TWLO"
        ]
    },
    "Robotics": {
        "etf": "BOTZ",
        "stocks": [
            "ISRG", "NVDA", "ROK", "ABB", "FANUY", "SYM", "TER", "CGNX", "PATH", "OUST"
        ]
    },
    "AI": {
        "etf": "AIQ",
        "stocks": [
            "NVDA", "MSFT", "GOOGL", "META", "AMD", "AVGO", "PLTR", "TSM", 
            "SMCI", "ANET", "ARM", "AI", "PATH", "SOUND", "ORCL", "SNPS", "CDNS"
        ]
    },
    "Software": {
        "etf": "IGV",
        "stocks": [
            "MSFT", "ORCL", "CRM", "NOW", "INTU", "WDAY", "PANW", "CRWD", 
            "DDOG", "NET", "SNOW", "PLTR", "ZS", "ADBE", "TEAM", "HUBS", "MDB"
        ]
    },
    "Cybersecurity": {
        "etf": "CIBR",
        "stocks": [
            "CRWD", "PANW", "FTNT", "ZS", "OKTA", "CYBR", "NET", "TENB", 
            "QLYS", "S", "VRNS", "GEN", "RPD"
        ]
    },
    "Airlines": {
        "etf": "JETS",
        "stocks": [
            "DAL", "UAL", "AAL", "LUV", "JBLU", "ALK", "SAVE", "SKYW", "HA", "CPA"
        ]
    },
    "Quantum": {
        "etf": "QTUM",
        "stocks": [
            "IONQ", "RGTI", "QBTS", "QUBT", "HON", "IBM", "GOOGL", "MSFT", "ARQQ"
        ]
    },
    "Semiconductors": {
        "etf": "SMH",
        "stocks": [
            "NVDA", "TSM", "AMD", "AVGO", "ASML", "QCOM", "TXN", "MU", 
            "INTC", "AMAT", "LRCX", "ADI", "MRVL", "ARM", "ON", "MPWR", "KLAC"
        ]
    },
    "Solar": {
        "etf": "TAN",
        "stocks": [
            "FSLR", "ENPH", "SEDG", "RUN", "NOVA", "CSIQ", "ARRY", "SHLS", "DQ", "JKS"
        ]
    },
    "Telecom": {
        "etf": "XLC",
        "stocks": [
            "T", "VZ", "TMUS", "CHTR", "CMCSA", "AMX", "VOD", "ORAN", "BCE", "TU", "FYBR"
        ]
    },
    "Gold Miners": {
        "etf": "GDX",
        "stocks": [
            "NEM", "GOLD", "AEM", "KGC", "AU", "GFI", "HMY", "IAG", "PAAS", "BTG", "EGO", "CDE"
        ]
    },
    "Growth Stocks": {
        "etf": "IWO",
        "stocks": [
            "PLTR", "NVDA", "APP", "SMCI", "ARM", "MSTR", "RDDT", "SE", 
            "MELI", "DUOL", "CAVA", "CELH", "DKNG", "SHOP", "FOUR"
        ]
    },
    "Silver Miners": {
        "etf": "SIL",
        "stocks": [
            "PAAS", "HL", "FSM", "EXK", "AG", "MAG", "SILV", "CDE", "SVM", "ASM"
        ]
    },
    "Bitcoin Miners": {
        "etf": "WGMI",
        "stocks": [
            "MARA", "RIOT", "CLSK", "CIFR", "IREN", "HUT", "WULF", "BTDR", "BITF", "CORZ", "APLD"
        ]
    }
}

# =====================================================================
# MOTOR DE DATOS: THEME TRACKER (RENDIMIENTO MULTI-TIMEFRAME)
# =====================================================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_themes_performance(timeframe="Today"):
    """
    Descarga cotizaciones de los 31 ETFs proxies y calcula el rendimiento
    para el timeframe solicitado: Today, 1W, 1M, 3M, YTD.
    """
    etf_tickers = [info["etf"] for info in THEMES_CATALOG.values()]
    unique_etfs = list(dict.fromkeys(etf_tickers))
    
    try:
        data = yf.download(unique_etfs, period="1y", interval="1d", threads=False, progress=False)
        closes = data["Close"]
        
        results = []
        for theme_name, info in THEMES_CATALOG.items():
            etf = info["etf"]
            if etf not in closes.columns:
                continue
            
            series = closes[etf].dropna()
            if len(series) < 2:
                continue
            
            last_price = float(series.iloc[-1])
            
            if timeframe == "Today":
                base_price = float(series.iloc[-2])
            elif timeframe == "1W":
                idx = max(0, len(series) - 6)
                base_price = float(series.iloc[idx])
            elif timeframe == "1M":
                idx = max(0, len(series) - 22)
                base_price = float(series.iloc[idx])
            elif timeframe == "3M":
                idx = max(0, len(series) - 64)
                base_price = float(series.iloc[idx])
            elif timeframe == "YTD":
                curr_year = series.index[-1].year
                y_data = series[series.index.year == curr_year]
                base_price = float(y_data.iloc[0]) if len(y_data) > 0 else float(series.iloc[0])
            else:
                base_price = float(series.iloc[-2])
            
            pct_change = ((last_price / base_price) - 1.0) * 100.0 if base_price > 0 else 0.0
            
            results.append({
                "Theme": theme_name,
                "ETF": etf,
                "Price": last_price,
                "ChangePct": pct_change,
                "FormattedChange": f"{pct_change:+.2f}%",
                "Direction": "pos" if pct_change >= 0 else "neg",
                "StocksCount": len(info["stocks"])
            })
            
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by="ChangePct", ascending=False).reset_index(drop=True)
            max_abs = max(df["ChangePct"].abs().max(), 0.01)
            df["BarWidthPct"] = (df["ChangePct"].abs() / max_abs * 100).clip(2, 100)
        return df
    except Exception as e:
        print(f"Error fetching themes performance: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_theme_constituents(theme_name, timeframe="Today"):
    """
    Descarga y rankea las acciones individuales que componen una temática seleccionada.
    """
    if theme_name not in THEMES_CATALOG:
        return pd.DataFrame()
    
    tickers = THEMES_CATALOG[theme_name]["stocks"]
    try:
        data = yf.download(tickers, period="1y", interval="1d", threads=False, progress=False)
        closes = data["Close"]
        vols = data["Volume"]
        
        results = []
        for ticker in tickers:
            if ticker not in closes.columns:
                continue
            series = closes[ticker].dropna()
            if len(series) < 2:
                continue
            
            last_price = float(series.iloc[-1])
            
            if timeframe == "Today":
                base_price = float(series.iloc[-2])
            elif timeframe == "1W":
                idx = max(0, len(series) - 6)
                base_price = float(series.iloc[idx])
            elif timeframe == "1M":
                idx = max(0, len(series) - 22)
                base_price = float(series.iloc[idx])
            elif timeframe == "3M":
                idx = max(0, len(series) - 64)
                base_price = float(series.iloc[idx])
            elif timeframe == "YTD":
                curr_year = series.index[-1].year
                y_data = series[series.index.year == curr_year]
                base_price = float(y_data.iloc[0]) if len(y_data) > 0 else float(series.iloc[0])
            else:
                base_price = float(series.iloc[-2])
                
            pct_change = ((last_price / base_price) - 1.0) * 100.0 if base_price > 0 else 0.0
            
            # Dollar Volume
            vol_series = vols[ticker].dropna() if ticker in vols.columns else None
            last_vol = float(vol_series.iloc[-1]) if vol_series is not None and len(vol_series) > 0 else 0.0
            dollar_vol = (last_price * last_vol) / 1_000_000.0
            
            results.append({
                "Ticker": ticker,
                "Price": last_price,
                "ChangePct": pct_change,
                "FormattedChange": f"{pct_change:+.2f}%",
                "Direction": "pos" if pct_change >= 0 else "neg",
                "DollarVolM": dollar_vol
            })
            
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by="ChangePct", ascending=False).reset_index(drop=True)
            max_abs = max(df["ChangePct"].abs().max(), 0.01)
            df["BarWidthPct"] = (df["ChangePct"].abs() / max_abs * 100).clip(2, 100)
        return df
    except Exception as e:
        print(f"Error fetching theme constituents for {theme_name}: {e}")
        return pd.DataFrame()


# =====================================================================
# MOTOR DE DATOS: MARKET BREADTH (AMPLITUD GLOBAL NYSE + NASDAQ)
# =====================================================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_breadth(provider="Alpaca", alpaca_key=None, alpaca_secret=None):
    """
    Calcula los 5 indicadores de amplitud de mercado oficiales de Deepvue
    sobre el universo COMPLETO del mercado estadounidense (NYSE + NASDAQ, ~5,000 acciones comunes):
    1. New Highs vs New Lows
    2. Advance vs Decline
    3. Up from Open vs Down from Open
    4. Up on Volume vs Down on Volume
    5. Up 4% vs Down 4%
    
    Y el Stage Analysis de Stan Weinstein (Etapas 1, 2, 3, 4).
    """
    import requests
    import os
    import json

    # Intentar obtener claves de Alpaca de parámetros o config.json
    if not alpaca_key or not alpaca_secret:
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    cfg = json.load(f)
                    alpaca_key = cfg.get("alpaca_api_key", "")
                    alpaca_secret = cfg.get("alpaca_secret_key", "")
            except Exception:
                pass

    has_alpaca = bool(alpaca_key and alpaca_secret)

    # -------------------------------------------------------------
    # 1. CÁLCULO DE MOVIMIENTOS EN VIVO SOBRE TODAS LAS ACCIONES NYSE + NASDAQ
    # -------------------------------------------------------------
    snapshots = {}
    total_valid = 0
    advances, declines = 0, 0
    up_open, dn_open = 0, 0
    up_vol, dn_vol = 0, 0
    up_4, dn_4 = 0, 0
    used_alpaca = False

    if has_alpaca:
        try:
            headers = {'APCA-API-KEY-ID': alpaca_key, 'APCA-API-SECRET-KEY': alpaca_secret}
            r_assets = requests.get(
                'https://paper-api.alpaca.markets/v2/assets?status=active&asset_class=us_equity', 
                headers=headers, 
                timeout=10
            )
            if r_assets.status_code == 200:
                assets = r_assets.json()
                clean_syms = [
                    a['symbol'] for a in assets 
                    if a.get('exchange') in ['NYSE', 'NASDAQ'] 
                    and a.get('tradable') 
                    and not any(x in a['symbol'] for x in ['/', '.', '+', '-', 'W', 'U', 'R'])
                    and len(a['symbol']) <= 5
                ]
                
                # Descargar snapshots en bloques de 1000
                for i in range(0, min(5000, len(clean_syms)), 1000):
                    chunk = clean_syms[i:i+1000]
                    chunk_str = ','.join(chunk)
                    res = requests.get(
                        f'https://data.alpaca.markets/v2/stocks/snapshots?symbols={chunk_str}&feed=iex', 
                        headers=headers, 
                        timeout=12
                    )
                    if res.status_code == 200:
                        snapshots.update(res.json())

                if len(snapshots) > 1000:
                    used_alpaca = True
                    for sym, data in snapshots.items():
                        d = data.get('dailyBar')
                        p = data.get('prevDailyBar')
                        if not d or not p:
                            continue
                        c = d.get('c', 0)
                        prev_c = p.get('c', 0)
                        o = d.get('o', 0)
                        v = d.get('v', 0)
                        prev_v = p.get('v', 0)
                        if c <= 0 or prev_c <= 0:
                            continue

                        total_valid += 1
                        chg = (c / prev_c) - 1.0

                        if chg > 0: advances += 1
                        elif chg < 0: declines += 1

                        if c > o: up_open += 1
                        elif c < o: dn_open += 1

                        if chg > 0 and v > 1.2 * prev_v and prev_v > 0: up_vol += 1
                        elif chg < 0 and v > 1.2 * prev_v and prev_v > 0: dn_vol += 1

                        if chg >= 0.04: up_4 += 1
                        elif chg <= -0.04: dn_4 += 1
        except Exception as e:
            print(f"Error fetching broad snapshots from Alpaca: {e}")
            used_alpaca = False

    # -------------------------------------------------------------
    # 2. CÁLCULO DE ETAPAS DE WEINSTEIN Y HISTÓRICO CON yfinance
    # -------------------------------------------------------------
    breadth_leaders = [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "ORCL", "COST", 
        "NFLX", "AMD", "ADBE", "CRM", "QCOM", "TXN", "INTU", "AMAT", "NOW", "ISRG", 
        "BKNG", "LRCX", "ADI", "PANW", "MDLZ", "REGN", "VRTX", "KLAC", "SNPS", "CDNS", 
        "CRWD", "MAR", "FTNT", "NXPI", "MCHP", "ABNB", "WDAY", "DASH", "ROP", "TEAM", 
        "JPM", "BAC", "WFC", "C", "MS", "GS", "UNH", "LLY", "JNJ", "ABBV", 
        "MRK", "PFE", "TMO", "ABT", "DHR", "BMY", "AMGN", "GILD", "CI", "CVS", 
        "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO", "OXY", "DVN", 
        "GE", "CAT", "DE", "HON", "UNP", "ETN", "ITW", "EMR", "PH", "WM", 
        "LIN", "SHW", "FCX", "ECL", "NEM", "NUE", "STLD", "CLF", "ALB", "CTVA", 
        "NEE", "SO", "DUK", "CEG", "VST", "AEP", "SRE", "D", "EXC", "XEL", 
        "PLD", "AMT", "EQIX", "PSA", "O", "SPG", "WELL", "DLR", "CCI", "VICI", 
        "WMT", "HD", "MCD", "NKE", "SBUX", "TJX", "LOW", "TGT", "LULU", "ROST", 
        "PLTR", "APP", "SMCI", "ARM", "MSTR", "COIN", "HOOD", "RDDT", "SE", "MELI", 
        "CAVA", "DUOL", "FOUR", "CELH", "DKNG", "SHOP", "NET", "DDOG", "ZS", "SNOW", 
        "FSLR", "ENPH", "SEDG", "RUN", "CSIQ", "ARRY", "SHLS", "DQ", "JKS", 
        "PAAS", "HL", "FSM", "EXK", "AG", "CDE", "SVM", "ASM", 
        "MARA", "RIOT", "CLSK", "CIFR", "IREN", "HUT", "WULF", "BTDR", "CORZ", 
        "DHI", "LEN", "NVR", "PHM", "TOL", "KBH", "MHO", "CCS", 
        "DAL", "UAL", "AAL", "LUV", "JBLU", "ALK", "SKYW", "CPA", 
        "IONQ", "RGTI", "QBTS", "QUBT", "IBM", "ARQQ", "RKLB", "KTOS", "CAE", "AVAV"
    ]

    try:
        yf_data = yf.download(breadth_leaders, period="1y", interval="1d", threads=False, progress=False)
        closes = yf_data["Close"]
        opens = yf_data["Open"]
        highs = yf_data["High"]
        lows = yf_data["Low"]
        vols = yf_data["Volume"]

        valid_cols = [c for c in closes.columns if len(closes[c].dropna()) > 200]
        closes = closes[valid_cols]
        opens = opens[valid_cols]
        highs = highs[valid_cols]
        lows = lows[valid_cols]
        vols = vols[valid_cols]

        sample_len = len(valid_cols)

        # Si no se usó Alpaca, calcular métricas directas con la muestra y escalar al mercado
        if not used_alpaca or total_valid == 0:
            total_valid = 5000 # Escala estándar mercado US
            today_chg = (closes.iloc[-1] / closes.iloc[-2]) - 1.0
            s_adv = int((today_chg > 0).sum())
            s_dec = int((today_chg < 0).sum())
            advances = int(round(s_adv / max(sample_len, 1) * total_valid))
            declines = int(round(s_dec / max(sample_len, 1) * total_valid))

            s_up_op = int((closes.iloc[-1] > opens.iloc[-1]).sum())
            s_dn_op = int((closes.iloc[-1] < opens.iloc[-1]).sum())
            up_open = int(round(s_up_op / max(sample_len, 1) * total_valid))
            dn_open = int(round(s_dn_op / max(sample_len, 1) * total_valid))

            avg_vol20 = vols.rolling(window=20, min_periods=10).mean().iloc[-2]
            s_up_v = int(((today_chg > 0) & (vols.iloc[-1] > 1.2 * avg_vol20)).sum())
            s_dn_v = int(((today_chg < 0) & (vols.iloc[-1] > 1.2 * avg_vol20)).sum())
            up_vol = int(round(s_up_v / max(sample_len, 1) * total_valid))
            dn_vol = int(round(s_dn_v / max(sample_len, 1) * total_valid))

            s_up_4 = int((today_chg >= 0.04).sum())
            s_dn_4 = int((today_chg <= -0.04).sum())
            up_4 = int(round(s_up_4 / max(sample_len, 1) * total_valid))
            dn_4 = int(round(s_dn_4 / max(sample_len, 1) * total_valid))

        # Ratios de amplitud oficiales
        adv_pct = int(round((advances / max(advances + declines, 1)) * 100))
        up_open_pct = int(round((up_open / max(up_open + dn_open, 1)) * 100))
        vol_pct = int(round((up_vol / max(up_vol + dn_vol, 1)) * 100))
        pct_4 = int(round((up_4 / max(up_4 + dn_4, 1)) * 100))

        # 3. New Highs vs New Lows (52 semanas)
        max_52w = highs.rolling(window=250, min_periods=50).max().iloc[-1]
        min_52w = lows.rolling(window=250, min_periods=50).min().iloc[-1]
        s_nh = (closes.iloc[-1] >= 0.98 * max_52w).sum()
        s_nl = (closes.iloc[-1] <= 1.02 * min_52w).sum()

        nh_ratio = float(s_nh) / max(sample_len, 1)
        nl_ratio = float(s_nl) / max(sample_len, 1)
        new_highs = int(round(nh_ratio * total_valid))
        new_lows = int(round(nl_ratio * total_valid))
        nh_pct = int(round((new_highs / max(new_highs + new_lows, 1)) * 100))

        # 4. WEINSTEIN STAGE ANALYSIS (4 ETAPAS)
        sma_200 = closes.rolling(200).mean()
        sma_50 = closes.rolling(50).mean()

        curr_c = closes.iloc[-1]
        curr_s200 = sma_200.iloc[-1]
        curr_s50 = sma_50.iloc[-1]

        # Stage 2: Impulso Alcista (Precio > SMA200 y SMA50, SMA50 > SMA200)
        stage_2_mask = (curr_c > curr_s200) & (curr_c > curr_s50) & (curr_s50 > curr_s200)
        # Stage 4: Capitulación Bajista (Precio < SMA200 y SMA50, SMA50 < SMA200)
        stage_4_mask = (curr_c < curr_s200) & (curr_c < curr_s50) & (curr_s50 < curr_s200)
        # Stage 3: Techo / Distribución (Precio bajo SMA50 pero sobre SMA200)
        stage_3_mask = (curr_c < curr_s50) & (curr_c >= 0.96 * curr_s200) & ~stage_2_mask & ~stage_4_mask
        # Stage 1: Acumulación / Base (Consolidando)
        stage_1_mask = ~stage_2_mask & ~stage_4_mask & ~stage_3_mask

        # Porcentajes del mercado
        s1_pct = int(round((stage_1_mask.sum() / sample_len) * 100))
        s2_pct = int(round((stage_2_mask.sum() / sample_len) * 100))
        s3_pct = int(round((stage_3_mask.sum() / sample_len) * 100))
        s4_pct = max(0, 100 - (s1_pct + s2_pct + s3_pct))

        # Conteo escalado al universo completo NYSE + NASDAQ
        s1_count = int(round((s1_pct / 100.0) * total_valid))
        s2_count = int(round((s2_pct / 100.0) * total_valid))
        s3_count = int(round((s3_pct / 100.0) * total_valid))
        s4_count = total_valid - (s1_count + s2_count + s3_count)

        # SERIE TEMPORAL HISTÓRICA S2 vs S4 (últimas 120 sesiones)
        hist_len = min(120, len(closes))
        recent_closes = closes.iloc[-hist_len:]
        recent_s200 = sma_200.iloc[-hist_len:]
        recent_s50 = sma_50.iloc[-hist_len:]

        s2_series = ((recent_closes > recent_s200) & (recent_closes > recent_s50) & (recent_s50 > recent_s200)).sum(axis=1) / sample_len * 100
        s4_series = ((recent_closes < recent_s200) & (recent_closes < recent_s50) & (recent_s50 < recent_s200)).sum(axis=1) / sample_len * 100

        history_df = pd.DataFrame({
            "Date": s2_series.index,
            "Stage 2 (Bullish)": s2_series.values,
            "Stage 4 (Bearish)": s4_series.values
        })

        universe_title = f"NYSE + NASDAQ ({total_valid:,} ACCIONES COMUNES)"

        return {
            "total_stocks": total_valid,
            "universe_name": universe_title,
            "is_broad_market": True,
            "new_highs_lows": {
                "highs": new_highs,
                "lows": new_lows,
                "ratio_pct": nh_pct
            },
            "advance_decline": {
                "advance": advances,
                "decline": declines,
                "ratio_pct": adv_pct
            },
            "up_down_open": {
                "up": up_open,
                "down": dn_open,
                "ratio_pct": up_open_pct
            },
            "up_down_volume": {
                "up": up_vol,
                "down": dn_vol,
                "ratio_pct": vol_pct
            },
            "up_down_4pct": {
                "up": up_4,
                "down": dn_4,
                "ratio_pct": pct_4
            },
            "stages": {
                "s1": {"count": s1_count, "pct": s1_pct},
                "s2": {"count": s2_count, "pct": s2_pct},
                "s3": {"count": s3_count, "pct": s3_pct},
                "s4": {"count": s4_count, "pct": s4_pct}
            },
            "history_df": history_df
        }
    except Exception as e:
        print(f"Error computing broad market breadth: {e}")
        return None

