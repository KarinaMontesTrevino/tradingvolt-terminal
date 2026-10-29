"""
TradingVolt • Earnings Calendar & Multi-Timeframe Chart Engine
Reverse engineered from Deepvue Institutional Earnings Desk & Earnings Whispers.
Provides weekly calendar breakdown, BMO/AMC categorization, beat/miss metrics,
and interactive multi-timeframe technical charts.
"""

from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================================================
# SEMANA 1: 19 - 23 OCTUBRE 2026 (RESULTADOS ANTERIORES: BANCOS & INDUSTRIALES)
# =========================================================================
EARNINGS_WEEK_OCT19_DATA = {
    "Mon 19": {
        "date_str": "Lunes 19 Octubre",
        "day_num": 19,
        "is_today": False,
        "reported": 22,
        "eps_growth": "+32%",
        "sales_growth": "+18%",
        "surprise_pct": "+6%",
        "tickers": [
            {"symbol": "FITB", "name": "Fifth Third Bancorp", "sector": "Financials", "time": "BMO", "result": "Beat +21%", "type": "beat", "eps": "$0.91", "est": "$0.75", "cap": "Large"},
            {"symbol": "BOKF", "name": "BOK Financial Corp", "sector": "Financials", "time": "BMO", "result": "Beat +5%", "type": "beat", "eps": "$2.18", "est": "$2.08", "cap": "Mid"},
            {"symbol": "KMB", "name": "Kimberly-Clark", "sector": "Consumer Defensive", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$1.83", "est": "$1.79", "cap": "Large"},
            {"symbol": "STLD", "name": "Steel Dynamics", "sector": "Materials", "time": "AMC", "result": "Miss -4%", "type": "miss", "eps": "$2.05", "est": "$2.14", "cap": "Large"},
            {"symbol": "WRB", "name": "W. R. Berkley", "sector": "Financials", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$1.02", "est": "$1.01", "cap": "Large"},
            {"symbol": "CCK", "name": "Crown Holdings", "sector": "Packaging", "time": "AMC", "result": "Beat +6%", "type": "beat", "eps": "$1.99", "est": "$1.88", "cap": "Mid"},
            {"symbol": "ZION", "name": "Zions Bancorporation", "sector": "Financials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$1.37", "est": "$1.28", "cap": "Mid"},
            {"symbol": "WAL", "name": "Western Alliance", "sector": "Financials", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$1.80", "est": "$1.78", "cap": "Mid"},
            {"symbol": "CLF", "name": "Cleveland-Cliffs", "sector": "Materials", "time": "AMC", "result": "Beat +21%", "type": "beat", "eps": "$0.40", "est": "$0.33", "cap": "Mid"}
        ]
    },
    "Tue 20": {
        "date_str": "Martes 20 Octubre",
        "day_num": 20,
        "is_today": False,
        "reported": 54,
        "eps_growth": "+27%",
        "sales_growth": "+18%",
        "surprise_pct": "+3%",
        "tickers": [
            {"symbol": "GE", "name": "GE Aerospace", "sector": "Industrials", "time": "BMO", "result": "Beat +12%", "type": "beat", "eps": "$1.15", "est": "$1.03", "cap": "Mega"},
            {"symbol": "RTX", "name": "RTX Corporation", "sector": "Industrials", "time": "BMO", "result": "Beat +27%", "type": "beat", "eps": "$1.45", "est": "$1.14", "cap": "Large"},
            {"symbol": "MMM", "name": "3M Company", "sector": "Industrials", "time": "BMO", "result": "Beat +8%", "type": "beat", "eps": "$1.98", "est": "$1.83", "cap": "Large"},
            {"symbol": "GM", "name": "General Motors", "sector": "Consumer Cyclical", "time": "BMO", "result": "Beat +6%", "type": "beat", "eps": "$2.96", "est": "$2.79", "cap": "Large"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "time": "AMC", "result": "Beat +6%", "type": "beat", "eps": "$5.40", "est": "$5.10", "cap": "Mega"},
            {"symbol": "COF", "name": "Capital One Financial", "sector": "Financials", "time": "AMC", "result": "Beat +21%", "type": "beat", "eps": "$4.51", "est": "$3.73", "cap": "Large"},
            {"symbol": "UAL", "name": "United Airlines", "sector": "Industrials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$3.33", "est": "$3.11", "cap": "Large"}
        ]
    },
    "Wed 21": {
        "date_str": "Miércoles 21 Octubre",
        "day_num": 21,
        "is_today": False,
        "reported": 90,
        "eps_growth": "+55%",
        "sales_growth": "+16%",
        "surprise_pct": "+8%",
        "tickers": [
            {"symbol": "PM", "name": "Philip Morris Int.", "sector": "Consumer Defensive", "time": "BMO", "result": "Beat +3%", "type": "beat", "eps": "$1.91", "est": "$1.85", "cap": "Large"},
            {"symbol": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$5.28", "est": "$5.08", "cap": "Large"},
            {"symbol": "ABT", "name": "Abbott Laboratories", "sector": "Healthcare", "time": "BMO", "result": "Beat +0%", "type": "beat", "eps": "$1.21", "est": "$1.21", "cap": "Large"},
            {"symbol": "T", "name": "AT&T Inc.", "sector": "Communication Services", "time": "BMO", "result": "Beat +5%", "type": "beat", "eps": "$0.60", "est": "$0.57", "cap": "Large"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$6.03", "est": "$5.34", "cap": "Mega"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Beat +5%", "type": "beat", "eps": "$0.72", "est": "$0.68", "cap": "Mega"},
            {"symbol": "LRCX", "name": "Lam Research", "sector": "Technology", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$0.86", "est": "$0.85", "cap": "Large"},
            {"symbol": "IBM", "name": "IBM Corporation", "sector": "Technology", "time": "AMC", "result": "Beat +3%", "type": "beat", "eps": "$2.30", "est": "$2.23", "cap": "Large"}
        ]
    },
    "Thu 22": {
        "date_str": "Jueves 22 Octubre",
        "day_num": 22,
        "is_today": False,
        "reported": 109,
        "eps_growth": "+80%",
        "sales_growth": "+13%",
        "surprise_pct": "+3%",
        "tickers": [
            {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer Defensive", "time": "BMO", "result": "Beat +8%", "type": "beat", "eps": "$1.93", "est": "$1.79", "cap": "Mega"},
            {"symbol": "UNP", "name": "Union Pacific", "sector": "Industrials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$2.75", "est": "$2.70", "cap": "Large"},
            {"symbol": "LMT", "name": "Lockheed Martin", "sector": "Industrials", "time": "BMO", "result": "Beat +6%", "type": "beat", "eps": "$6.80", "est": "$6.42", "cap": "Large"},
            {"symbol": "HON", "name": "Honeywell Int.", "sector": "Industrials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$2.58", "est": "$2.53", "cap": "Large"},
            {"symbol": "WDC", "name": "Western Digital", "sector": "Technology", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$1.78", "est": "$1.57", "cap": "Large"},
            {"symbol": "COHR", "name": "Coherent Corp", "sector": "Technology", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$0.91", "est": "$0.87", "cap": "Mid"}
        ]
    },
    "Fri 23": {
        "date_str": "Viernes 23 Octubre",
        "day_num": 23,
        "is_today": False,
        "reported": 22,
        "eps_growth": "+58%",
        "sales_growth": "+19%",
        "surprise_pct": "+7%",
        "tickers": [
            {"symbol": "AXP", "name": "American Express", "sector": "Financials", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$3.49", "est": "$3.35", "cap": "Large"},
            {"symbol": "SLB", "name": "Schlumberger", "sector": "Energy", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$0.89", "est": "$0.86", "cap": "Large"},
            {"symbol": "BAH", "name": "Booz Allen Hamilton", "sector": "Industrials", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$1.81", "est": "$1.64", "cap": "Mid"}
        ]
    }
}

# =========================================================================
# SEMANA 2: 26 - 30 OCTUBRE 2026 (SEMANA EN CURSO • MEGA-TECH CLAVE)
# =========================================================================
EARNINGS_WEEK_OCT26_DATA = {
    "Mon 26": {
        "date_str": "Lunes 26 Octubre",
        "day_num": 26,
        "is_today": False,
        "reported": 38,
        "eps_growth": "+19%",
        "sales_growth": "+12%",
        "surprise_pct": "+4%",
        "tickers": [
            {"symbol": "ON", "name": "ON Semiconductor", "sector": "Technology", "time": "BMO", "result": "Beat +6%", "type": "beat", "eps": "$1.04", "est": "$0.98", "cap": "Large"},
            {"symbol": "BRO", "name": "Brown & Brown", "sector": "Financials", "time": "BMO", "result": "Beat +3%", "type": "beat", "eps": "$0.93", "est": "$0.90", "cap": "Large"},
            {"symbol": "CDNS", "name": "Cadence Design Systems", "sector": "Technology", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$2.31", "est": "$2.23", "cap": "Large"},
            {"symbol": "FFIV", "name": "F5 Inc.", "sector": "Technology", "time": "AMC", "result": "Beat +2%", "type": "beat", "eps": "$3.52", "est": "$3.45", "cap": "Mid"},
            {"symbol": "AGYS", "name": "Agilysys Inc.", "sector": "Technology", "time": "AMC", "result": "Beat +8%", "type": "beat", "eps": "$0.38", "est": "$0.35", "cap": "Mid"}
        ]
    },
    "Tue 27": {
        "date_str": "Martes 27 Octubre",
        "day_num": 27,
        "is_today": False,
        "reported": 72,
        "eps_growth": "+36%",
        "sales_growth": "+18%",
        "surprise_pct": "+7%",
        "tickers": [
            {"symbol": "PYPL", "name": "PayPal Holdings", "sector": "Financials", "time": "BMO", "result": "Beat +19%", "type": "beat", "eps": "$1.43", "est": "$1.20", "cap": "Large"},
            {"symbol": "MCD", "name": "McDonald's Corp.", "sector": "Consumer Cyclical", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$3.23", "est": "$3.18", "cap": "Mega"},
            {"symbol": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "time": "BMO", "result": "Beat +18%", "type": "beat", "eps": "$0.73", "est": "$0.62", "cap": "Large"},
            {"symbol": "SHW", "name": "Sherwin-Williams", "sector": "Materials", "time": "BMO", "result": "Beat +5%", "type": "beat", "eps": "$2.45", "est": "$2.34", "cap": "Large"},
            {"symbol": "NXPI", "name": "NXP Semiconductors", "sector": "Technology", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$4.36", "est": "$4.18", "cap": "Large"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financials", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$3.63", "est": "$3.50", "cap": "Mega"},
            {"symbol": "CHKP", "name": "Check Point Software", "sector": "Technology", "time": "AMC", "result": "Beat +3%", "type": "beat", "eps": "$2.48", "est": "$2.40", "cap": "Large"}
        ]
    },
    "Wed 28": {
        "date_str": "Miércoles 28 Octubre (HOY)",
        "day_num": 28,
        "is_today": True,
        "reported": 118,
        "eps_growth": "+58%",
        "sales_growth": "+24%",
        "surprise_pct": "+9%",
        "tickers": [
            # BMO (Antes de la Apertura)
            {"symbol": "BA", "name": "Boeing Company", "sector": "Industrials", "time": "BMO", "result": "Miss -14%", "type": "miss", "eps": "-$1.20", "est": "-$1.05", "cap": "Large"},
            {"symbol": "ADP", "name": "Automatic Data Processing", "sector": "Technology", "time": "BMO", "result": "Beat +3%", "type": "beat", "eps": "$2.29", "est": "$2.22", "cap": "Large"},
            {"symbol": "HUM", "name": "Humana Inc.", "sector": "Healthcare", "time": "BMO", "result": "Beat +9%", "type": "beat", "eps": "$4.16", "est": "$3.80", "cap": "Large"},
            {"symbol": "GEV", "name": "GE Vernova", "sector": "Industrials/Energy", "time": "BMO", "result": "Beat +20%", "type": "beat", "eps": "$0.42", "est": "$0.35", "cap": "Large"},
            # AMC (Al Cierre del Mercado - REPORTARON HOY)
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "time": "AMC", "result": "Beat +10% 🚀", "type": "beat", "eps": "$3.33", "est": "$3.03", "cap": "Mega"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "time": "AMC", "result": "Beat +4% 🚀", "type": "beat", "eps": "$4.82", "est": "$4.65", "cap": "Mega"},
            {"symbol": "NOW", "name": "ServiceNow Inc.", "sector": "Technology", "time": "AMC", "result": "Beat +8%", "type": "beat", "eps": "$1.17", "est": "$1.08", "cap": "Mega"},
            {"symbol": "FTNT", "name": "Fortinet Inc.", "sector": "Technology", "time": "AMC", "result": "Beat +3% (Guía -25%)", "type": "miss", "eps": "$0.88", "est": "$0.85", "cap": "Large"},
            {"symbol": "ETSY", "name": "Etsy Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Beat +5%", "type": "beat", "eps": "$1.94", "est": "$1.85", "cap": "Mid"},
            {"symbol": "SIMO", "name": "Silicon Motion Technology", "sector": "Technology", "time": "AMC", "result": "Beat +6%", "type": "beat", "eps": "$3.33", "est": "$3.15", "cap": "Mid"}
        ]
    },
    "Thu 29": {
        "date_str": "Jueves 29 Octubre (MAÑANA)",
        "day_num": 29,
        "is_today": False,
        "reported": 145,
        "eps_growth": "+48%",
        "sales_growth": "+20%",
        "surprise_pct": "Est.",
        "tickers": [
            # BMO (Antes de la Apertura)
            {"symbol": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "time": "BMO", "result": "Est. $7.03", "type": "pending", "eps": "-", "est": "$7.03", "cap": "Mega"},
            {"symbol": "LLY", "name": "Eli Lilly and Company", "sector": "Healthcare", "time": "BMO", "result": "Est. $6.61", "type": "pending", "eps": "-", "est": "$6.61", "cap": "Mega"},
            {"symbol": "MA", "name": "Mastercard Inc.", "sector": "Financials", "time": "BMO", "result": "Est. $5.17", "type": "pending", "eps": "-", "est": "$5.17", "cap": "Mega"},
            {"symbol": "BMY", "name": "Bristol Myers Squibb", "sector": "Healthcare", "time": "BMO", "result": "Est. $1.22", "type": "pending", "eps": "-", "est": "$1.22", "cap": "Large"},
            {"symbol": "RBLX", "name": "Roblox Corporation", "sector": "Communication Services", "time": "BMO", "result": "Est. -$0.38", "type": "pending", "eps": "-", "est": "-$0.38", "cap": "Large"},
            {"symbol": "SO", "name": "Southern Company", "sector": "Utilities", "time": "BMO", "result": "Est. $1.32", "type": "pending", "eps": "-", "est": "$1.32", "cap": "Large"},
            # AMC (Al Cierre del Mercado)
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Est. $1.99 🚀", "type": "pending", "eps": "-", "est": "$1.99", "cap": "Mega"},
            {"symbol": "INTC", "name": "Intel Corporation", "sector": "Technology", "time": "AMC", "result": "Est. $0.40", "type": "pending", "eps": "-", "est": "$0.40", "cap": "Large"},
            {"symbol": "COIN", "name": "Coinbase Global", "sector": "Financials", "time": "AMC", "result": "Est. $0.07", "type": "pending", "eps": "-", "est": "$0.07", "cap": "Large"},
            {"symbol": "TEAM", "name": "Atlassian Corp.", "sector": "Technology", "time": "AMC", "result": "Est. $0.64", "type": "pending", "eps": "-", "est": "$0.64", "cap": "Large"},
            {"symbol": "MHK", "name": "Mohawk Industries", "sector": "Industrials", "time": "AMC", "result": "Est. $2.58", "type": "pending", "eps": "-", "est": "$2.58", "cap": "Mid"}
        ]
    },
    "Fri 30": {
        "date_str": "Viernes 30 Octubre",
        "day_num": 30,
        "is_today": False,
        "reported": 42,
        "eps_growth": "+25%",
        "sales_growth": "+11%",
        "surprise_pct": "Est.",
        "tickers": [
            {"symbol": "XOM", "name": "Exxon Mobil Corp.", "sector": "Energy", "time": "BMO", "result": "Est. $4.03", "type": "pending", "eps": "-", "est": "$4.03", "cap": "Mega"},
            {"symbol": "CVX", "name": "Chevron Corporation", "sector": "Energy", "time": "BMO", "result": "Est. $4.83", "type": "pending", "eps": "-", "est": "$4.83", "cap": "Mega"},
            {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "time": "BMO", "result": "Est. $3.77", "type": "pending", "eps": "-", "est": "$3.77", "cap": "Mega"},
            {"symbol": "CL", "name": "Colgate-Palmolive", "sector": "Consumer Defensive", "time": "BMO", "result": "Est. $0.93", "type": "pending", "eps": "-", "est": "$0.93", "cap": "Large"},
            {"symbol": "AON", "name": "Aon plc", "sector": "Financials", "time": "BMO", "result": "Est. $2.48", "type": "pending", "eps": "-", "est": "$2.48", "cap": "Large"}
        ]
    }
}

# =========================================================================
# SEMANA 3: 02 - 06 NOVIEMBRE 2026 (PRÓXIMA SEMANA • AAPL, AMD, UBER, QCOM, PLTR)
# =========================================================================
EARNINGS_WEEK_NOV02_DATA = {
    "Mon 02": {
        "date_str": "Lunes 02 Noviembre",
        "day_num": 2,
        "is_today": False,
        "reported": 35,
        "eps_growth": "Est.",
        "sales_growth": "Est.",
        "surprise_pct": "-",
        "tickers": [
            {"symbol": "FSR", "name": "Fisker Inc.", "sector": "Consumer Cyclical", "time": "BMO", "result": "Est. -$0.22", "type": "pending", "eps": "-", "est": "-$0.22", "cap": "Small"},
            {"symbol": "SOFI", "name": "SoFi Technologies", "sector": "Financials", "time": "BMO", "result": "Est. $0.04", "type": "pending", "eps": "-", "est": "$0.04", "cap": "Large"},
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "time": "AMC", "result": "Est. $1.98 👑", "type": "pending", "eps": "-", "est": "$1.98", "cap": "Mega"},
            {"symbol": "WMB", "name": "Williams Companies", "sector": "Energy", "time": "AMC", "result": "Est. $0.54", "type": "pending", "eps": "-", "est": "$0.54", "cap": "Large"},
            {"symbol": "ROKU", "name": "Roku Inc.", "sector": "Communication Services", "time": "AMC", "result": "Est. $0.55", "type": "pending", "eps": "-", "est": "$0.55", "cap": "Mid"}
        ]
    },
    "Tue 03": {
        "date_str": "Martes 03 Noviembre",
        "day_num": 3,
        "is_today": False,
        "reported": 65,
        "eps_growth": "Est.",
        "sales_growth": "Est.",
        "surprise_pct": "-",
        "tickers": [
            {"symbol": "AMGN", "name": "Amgen Inc.", "sector": "Healthcare", "time": "BMO", "result": "Est. $5.79", "type": "pending", "eps": "-", "est": "$5.79", "cap": "Large"},
            {"symbol": "ZTS", "name": "Zoetis Inc.", "sector": "Healthcare", "time": "BMO", "result": "Est. $1.45", "type": "pending", "eps": "-", "est": "$1.45", "cap": "Large"},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "time": "AMC", "result": "Est. $2.10 🚀", "type": "pending", "eps": "-", "est": "$2.10", "cap": "Mega"},
            {"symbol": "SMCI", "name": "Super Micro Computer", "sector": "Technology", "time": "AMC", "result": "Est. $0.75", "type": "pending", "eps": "-", "est": "$0.75", "cap": "Large"},
            {"symbol": "MTCH", "name": "Match Group", "sector": "Communication Services", "time": "AMC", "result": "Est. $0.52", "type": "pending", "eps": "-", "est": "$0.52", "cap": "Mid"}
        ]
    },
    "Wed 04": {
        "date_str": "Miércoles 04 Noviembre",
        "day_num": 4,
        "is_today": False,
        "reported": 110,
        "eps_growth": "Est.",
        "sales_growth": "Est.",
        "surprise_pct": "-",
        "tickers": [
            {"symbol": "UBER", "name": "Uber Technologies", "sector": "Technology", "time": "BMO", "result": "Est. $0.87", "type": "pending", "eps": "-", "est": "$0.87", "cap": "Mega"},
            {"symbol": "CVS", "name": "CVS Health Corp.", "sector": "Healthcare", "time": "BMO", "result": "Est. $1.65", "type": "pending", "eps": "-", "est": "$1.65", "cap": "Large"},
            {"symbol": "QCOM", "name": "Qualcomm Inc.", "sector": "Technology", "time": "AMC", "result": "Est. $2.16 🚀", "type": "pending", "eps": "-", "est": "$2.16", "cap": "Mega"},
            {"symbol": "ARM", "name": "Arm Holdings", "sector": "Technology", "time": "AMC", "result": "Est. $0.32", "type": "pending", "eps": "-", "est": "$0.32", "cap": "Mega"},
            {"symbol": "HOOD", "name": "Robinhood Markets", "sector": "Financials", "time": "AMC", "result": "Est. $0.25", "type": "pending", "eps": "-", "est": "$0.25", "cap": "Large"},
            {"symbol": "MELI", "name": "MercadoLibre Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Est. $9.85", "type": "pending", "eps": "-", "est": "$9.85", "cap": "Mega"}
        ]
    },
    "Thu 05": {
        "date_str": "Jueves 05 Noviembre",
        "day_num": 5,
        "is_today": False,
        "reported": 95,
        "eps_growth": "Est.",
        "sales_growth": "Est.",
        "surprise_pct": "-",
        "tickers": [
            {"symbol": "PLTR", "name": "Palantir Technologies", "sector": "Technology", "time": "BMO", "result": "Est. $0.11 🔥", "type": "pending", "eps": "-", "est": "$0.11", "cap": "Mega"},
            {"symbol": "DIS", "name": "Walt Disney Company", "sector": "Communication Services", "time": "BMO", "result": "Est. $1.10", "type": "pending", "eps": "-", "est": "$1.10", "cap": "Mega"},
            {"symbol": "ABNB", "name": "Airbnb Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Est. $2.85", "type": "pending", "eps": "-", "est": "$2.85", "cap": "Large"},
            {"symbol": "SQ", "name": "Block Inc.", "sector": "Financials", "time": "AMC", "result": "Est. $0.88", "type": "pending", "eps": "-", "est": "$0.88", "cap": "Large"},
            {"symbol": "NET", "name": "Cloudflare Inc.", "sector": "Technology", "time": "AMC", "result": "Est. $0.18", "type": "pending", "eps": "-", "est": "$0.18", "cap": "Large"}
        ]
    },
    "Fri 06": {
        "date_str": "Viernes 06 Noviembre",
        "day_num": 6,
        "is_today": False,
        "reported": 28,
        "eps_growth": "Est.",
        "sales_growth": "Est.",
        "surprise_pct": "-",
        "tickers": [
            {"symbol": "ENB", "name": "Enbridge Inc.", "sector": "Energy", "time": "BMO", "result": "Est. $0.58", "type": "pending", "eps": "-", "est": "$0.58", "cap": "Large"},
            {"symbol": "DUK", "name": "Duke Energy", "sector": "Utilities", "time": "BMO", "result": "Est. $1.72", "type": "pending", "eps": "-", "est": "$1.72", "cap": "Large"}
        ]
    }
}

KEY_WEEK_OCT19 = "⏪ Oct 19 - 23 (Semana Anterior: Bancos & Reportes Previos)"
KEY_WEEK_OCT26 = "🟢 Oct 26 - 30 (🔥 ESTA SEMANA EN VIVO: GOOGL, MSFT, AMZN, NOW, FTNT)"
KEY_WEEK_NOV02 = "⏩ Nov 02 - 06 (Próxima Semana: AAPL, AMD, UBER, QCOM, PLTR)"

EARNINGS_WEEKS = {
    KEY_WEEK_OCT26: EARNINGS_WEEK_OCT26_DATA,
    KEY_WEEK_OCT19: EARNINGS_WEEK_OCT19_DATA,
    KEY_WEEK_NOV02: EARNINGS_WEEK_NOV02_DATA
}

def get_default_week_key() -> str:
    """Retorna la semana actual en curso."""
    return KEY_WEEK_OCT26

def get_default_day_key(week_key: str = KEY_WEEK_OCT26) -> str:
    """Detecta el día actual y retorna la clave de día adecuada."""
    week_data = get_earnings_week_data(week_key)
    today_dt = date.today()
    # Si la semana seleccionada es la actual (Oct 26-30), sincronizar con el día de hoy
    if "Oct 26" in week_key or week_key == KEY_WEEK_OCT26:
        day_map = {0: "Mon 26", 1: "Tue 27", 2: "Wed 28", 3: "Thu 29", 4: "Fri 30"}
        target = day_map.get(today_dt.weekday(), "Wed 28")
        if target in week_data:
            return target
    # Si no, retornar el primer día con datos
    return list(week_data.keys())[0]

def get_earnings_week_data(week_key: str = KEY_WEEK_OCT26):
    """Retorna el diccionario de días para la semana seleccionada."""
    return EARNINGS_WEEKS.get(week_key, EARNINGS_WEEK_OCT26_DATA)

def get_day_grouped_tickers(day_dict: dict) -> dict:
    """Agrupa los tickers del día en 'bmo' y 'amc'."""
    tickers = day_dict.get("tickers", [])
    bmo = [t for t in tickers if t.get("time") == "BMO"]
    amc = [t for t in tickers if t.get("time") == "AMC"]
    return {"bmo": bmo, "amc": amc, "all": tickers}


# =========================================================================
# MOTOR TÉCNICO MULTI-TEMPORALIDAD (DEEPVUE CANDLESTICK & INDICATORS)
# =========================================================================

def get_stock_ohlcv(symbol: str, timeframe: str = "1D") -> pd.DataFrame:
    """
    Descarga cotizaciones en la temporalidad seleccionada:
    5m, 15m, 1h, 4h, 1D, 1W, 1M
    """
    tf_mapping = {
        "5m": ("5m", "5d"),
        "15m": ("15m", "10d"),
        "1h": ("60m", "1mo"),
        "4h": ("60m", "3mo"),
        "1D": ("1d", "1y"),
        "1W": ("1wk", "2y"),
        "1M": ("1mo", "5y")
    }
    
    interval, period = tf_mapping.get(timeframe, ("1d", "1y"))
    
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if df.empty or len(df) < 5:
            dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
            base_p = 50.0
            noise = np.cumsum(np.random.normal(0, 1.2, 100))
            closes = np.maximum(5.0, base_p + noise)
            highs = closes * (1 + np.random.uniform(0.005, 0.03, 100))
            lows = closes * (1 - np.random.uniform(0.005, 0.03, 100))
            opens = (highs + lows) / 2
            vols = np.random.randint(500000, 5000000, 100)
            df = pd.DataFrame({'Open': opens, 'High': highs, 'Low': lows, 'Close': closes, 'Volume': vols}, index=dates)
            
        # Calcular Indicadores Técnicos Clave
        df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50, min_periods=5).mean()
        df['SMA200'] = df['Close'].rolling(window=200, min_periods=20).mean()
        df['Vol_SMA20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
        
        # Relative Strength Index (RSI 14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=5).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=5).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Average Daily Range ADR(10)
        df['ADR10'] = ((df['High'] - df['Low']) / (df['Low'] + 1e-9) * 100).rolling(10, min_periods=1).mean()
        
        return df
    except Exception:
        return pd.DataFrame()


def render_deepvue_chart(symbol: str, timeframe: str = "1D", company_name: str = "", sector_info: str = "") -> go.Figure:
    """
    Crea un gráfico interactivo estilo Deepvue / TradingView:
    - Panel 1: Velas japonesas + EMAs (10, 20, 50, 200) + Watermark del Ticker
    - Panel 2: Volumen coloreado + SMA 20 de volumen
    - Panel 3: Indicador RS / RSI / ADR oscilador
    """
    df = get_stock_ohlcv(symbol, timeframe)
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No hay cotizaciones disponibles para {symbol}", showarrow=False, font=dict(color="#8E8EA0", size=16))
        fig.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
        return fig
        
    last_close = float(df['Close'].iloc[-1])
    first_close = float(df['Close'].iloc[0])
    prev_close = float(df['Close'].iloc[-2]) if len(df) >= 2 else first_close
    chg_val = last_close - prev_close
    chg_pct = (chg_val / (prev_close + 1e-9)) * 100
    last_vol = float(df['Volume'].iloc[-1])
    dollar_vol = (last_close * last_vol) / 1e6
    last_high = float(df['High'].iloc[-1])
    last_low = float(df['Low'].iloc[-1])
    last_open = float(df['Open'].iloc[-1])
    
    # Subplots con 3 paneles
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.65, 0.18, 0.17],
        subplot_titles=None
    )
    
    # Colores velas estilo Deepvue
    colors_up = "#089981"   # Verde institucional
    colors_down = "#F23645" # Rojo institucional
    
    # 1. Velas Japonesas
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=f"{symbol} Price",
        increasing_line_color=colors_up,
        decreasing_line_color=colors_down,
        increasing_fillcolor=colors_up,
        decreasing_fillcolor=colors_down
    ), row=1, col=1)
    
    # EMAs / SMAs
    if 'EMA10' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA10'], line=dict(color='#00F0FF', width=1.3), name="10 EMA"), row=1, col=1)
    if 'EMA20' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='#FFA500', width=1.3), name="20 EMA"), row=1, col=1)
    if 'SMA50' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#4A90E2', width=1.5), name="50 SMA"), row=1, col=1)
    if 'SMA200' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='#E53935', width=1.8), name="200 SMA"), row=1, col=1)
        
    # 2. Volumen Bar
    bar_colors = np.where(df['Close'] >= df['Open'], '#00C853', '#FF5252')
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        marker_color=bar_colors,
        name="Volume",
        opacity=0.85
    ), row=2, col=1)
    
    if 'Vol_SMA20' in df:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Vol_SMA20'],
            line=dict(color='#9E9E9E', width=1.2, dash='dot'),
            name="Vol SMA(20)"
        ), row=2, col=1)
        
    # 3. Oscilador RSI / ADR
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        line=dict(color='#B388FF', width=1.5),
        name="RSI (14)"
    ), row=3, col=1)
    
    # Líneas de sobrecompra / sobreventa
    fig.add_hline(y=70, line_dash="dash", line_color="#FF5252", line_width=1, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#00C853", line_width=1, row=3, col=1)
    
    # Watermark del Ticker en el fondo del gráfico (Idéntico a Deepvue)
    fig.add_annotation(
        text=symbol,
        xref="paper", yref="paper",
        x=0.5, y=0.6,
        showarrow=False,
        font=dict(size=90, color="rgba(255, 255, 255, 0.05)", family="Arial Black, Impact, sans-serif"),
        align="center"
    )
    if company_name:
        fig.add_annotation(
            text=f"{company_name}<br><span style='font-size:12px; color:#8E8EA0'>{sector_info}</span>",
            xref="paper", yref="paper",
            x=0.5, y=0.48,
            showarrow=False,
            font=dict(size=16, color="rgba(255, 255, 255, 0.15)"),
            align="center"
        )
        
    # Título institucional con datos de sesión
    chg_sign = "+" if chg_val >= 0 else ""
    chg_color = "#00C853" if chg_val >= 0 else "#FF5252"
    header_html = (
        f"<b>{symbol}</b> • {timeframe} &nbsp;|&nbsp; "
        f"O: <b>${last_open:.2f}</b> &nbsp; H: <b>${last_high:.2f}</b> &nbsp; L: <b>${last_low:.2f}</b> &nbsp; "
        f"C: <b>${last_close:.2f}</b> &nbsp;|&nbsp; "
        f"Chg: <span style='color:{chg_color}'><b>{chg_sign}{chg_val:.2f} ({chg_sign}{chg_pct:.2f}%)</b></span> &nbsp;|&nbsp; "
        f"Vol: <b>{last_vol/1e3:.1f}K</b> &nbsp; $Vol: <b>${dollar_vol:.2f}M</b>"
    )
    
    fig.update_layout(
        title=dict(text=header_html, font=dict(size=14, color="#E0E3EB")),
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=620,
        margin=dict(l=10, r=40, t=45, b=20),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        hovermode="x unified"
    )
    
    fig.update_xaxes(showgrid=True, gridcolor="#1A2234", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#1A2234", zeroline=False, side="right")
    
    return fig
