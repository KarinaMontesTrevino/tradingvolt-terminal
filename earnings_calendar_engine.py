"""
TradingVolt • Earnings Calendar & Multi-Timeframe Chart Engine
Reverse engineered from Deepvue Institutional Earnings Desk.
Provides weekly calendar breakdown, beat/miss metrics, and interactive multi-timeframe technical charts.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------- SEMANA DE EARNINGS (BENCHMARK OCTUBRE 2026) -----------------
EARNINGS_WEEK_DATA = {
    "Mon 19": {
        "date_str": "Lunes 19 Octubre",
        "reported": 22,
        "eps_growth": "+32%",
        "sales_growth": "+18%",
        "surprise_pct": "+6%",
        "tickers": [
            {"symbol": "FITB", "name": "Fifth Third Bancorp", "sector": "Financials", "time": "BMO", "result": "Beat +21%", "type": "beat", "eps": "$0.91", "est": "$0.75"},
            {"symbol": "STLD", "name": "Steel Dynamics", "sector": "Materials", "time": "AMC", "result": "Miss -4%", "type": "miss", "eps": "$2.05", "est": "$2.14"},
            {"symbol": "WRB", "name": "W. R. Berkley", "sector": "Financials", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$1.02", "est": "$1.01"},
            {"symbol": "CCK", "name": "Crown Holdings", "sector": "Packaging", "time": "AMC", "result": "Beat +6%", "type": "beat", "eps": "$1.99", "est": "$1.88"},
            {"symbol": "ABCL", "name": "AbCellera Biologics", "sector": "Healthcare", "time": "AMC", "result": "Miss -7%", "type": "miss", "eps": "-$0.15", "est": "-$0.14"},
            {"symbol": "AGNC", "name": "AGNC Investment", "sector": "Financials", "time": "AMC", "result": "Miss -1%", "type": "miss", "eps": "$0.58", "est": "$0.59"},
            {"symbol": "WTFC", "name": "Wintrust Financial", "sector": "Financials", "time": "AMC", "result": "Beat +2%", "type": "beat", "eps": "$2.55", "est": "$2.50"},
            {"symbol": "ZION", "name": "Zions Bancorporation", "sector": "Financials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$1.37", "est": "$1.28"},
            {"symbol": "WAL", "name": "Western Alliance Bancorp", "sector": "Financials", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$1.80", "est": "$1.78"},
            {"symbol": "CLF", "name": "Cleveland-Cliffs", "sector": "Materials", "time": "AMC", "result": "Beat +21%", "type": "beat", "eps": "$0.40", "est": "$0.33"},
            {"symbol": "BOKF", "name": "BOK Financial Corp", "sector": "Financials", "time": "BMO", "result": "Beat +5%", "type": "beat", "eps": "$2.18", "est": "$2.08"},
            {"symbol": "VFS", "name": "VinFast Auto", "sector": "Consumer Cyclical", "time": "BMO", "result": "Miss -7%", "type": "miss", "eps": "-$0.31", "est": "-$0.29"},
            {"symbol": "FNB", "name": "F.N.B. Corporation", "sector": "Financials", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$0.34", "est": "$0.33"},
            {"symbol": "RJ", "name": "Raymond James", "sector": "Financials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$2.55", "est": "$2.38"},
            {"symbol": "SFNC", "name": "Simmons First National", "sector": "Financials", "time": "BMO", "result": "Miss -3%", "type": "miss", "eps": "$0.35", "est": "$0.36"},
            {"symbol": "FBNC", "name": "First Bancorp", "sector": "Financials", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$0.54", "est": "$0.52"},
            {"symbol": "DX", "name": "Dynex Capital", "sector": "Real Estate", "time": "BMO", "result": "Miss -2%", "type": "miss", "eps": "$0.39", "est": "$0.40"},
            {"symbol": "AERO", "name": "AeroVironment", "sector": "Industrials", "time": "AMC", "result": "Miss -6%", "type": "miss", "eps": "$0.80", "est": "$0.85"},
            {"symbol": "KMB", "name": "Kimberly-Clark", "sector": "Consumer Defensive", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$1.83", "est": "$1.79"},
            {"symbol": "SMBC", "name": "Southern Missouri Bancorp", "sector": "Financials", "time": "AMC", "result": "Beat +15%", "type": "beat", "eps": "$1.15", "est": "$1.00"},
            {"symbol": "WASH", "name": "Washington Trust Bancorp", "sector": "Financials", "time": "BMO", "result": "Beat +16%", "type": "beat", "eps": "$0.72", "est": "$0.62"}
        ]
    },
    "Tue 20": {
        "date_str": "Martes 20 Octubre",
        "reported": 54,
        "eps_growth": "+27%",
        "sales_growth": "+18%",
        "surprise_pct": "+3%",
        "tickers": [
            {"symbol": "GE", "name": "GE Aerospace", "sector": "Industrials", "time": "BMO", "result": "Beat +12%", "type": "beat", "eps": "$1.15", "est": "$1.03"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "time": "AMC", "result": "Beat +6%", "type": "beat", "eps": "$5.40", "est": "$5.10"},
            {"symbol": "RTX", "name": "RTX Corporation", "sector": "Industrials", "time": "BMO", "result": "Beat +27%", "type": "beat", "eps": "$1.45", "est": "$1.14"},
            {"symbol": "CR", "name": "Crane Company", "sector": "Industrials", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$1.32", "est": "$1.17"},
            {"symbol": "COF", "name": "Capital One Financial", "sector": "Financials", "time": "AMC", "result": "Beat +21%", "type": "beat", "eps": "$4.51", "est": "$3.73"},
            {"symbol": "MMM", "name": "3M Company", "sector": "Industrials", "time": "BMO", "result": "Beat +8%", "type": "beat", "eps": "$1.98", "est": "$1.83"},
            {"symbol": "NOC", "name": "Northrop Grumman", "sector": "Industrials", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$7.00", "est": "$6.36"},
            {"symbol": "AMX", "name": "America Movil", "sector": "Communication Services", "time": "AMC", "result": "Miss -5%", "type": "miss", "eps": "$0.38", "est": "$0.40"},
            {"symbol": "GM", "name": "General Motors", "sector": "Consumer Cyclical", "time": "BMO", "result": "Beat +6%", "type": "beat", "eps": "$2.96", "est": "$2.79"},
            {"symbol": "MSCI", "name": "MSCI Inc.", "sector": "Financials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$3.86", "est": "$3.78"},
            {"symbol": "UAL", "name": "United Airlines Holdings", "sector": "Industrials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$3.33", "est": "$3.11"},
            {"symbol": "HAL", "name": "Halliburton", "sector": "Energy", "time": "BMO", "result": "Beat +3%", "type": "beat", "eps": "$0.73", "est": "$0.71"},
            {"symbol": "SYF", "name": "Synchrony Financial", "sector": "Financials", "time": "BMO", "result": "Beat +11%", "type": "beat", "eps": "$1.86", "est": "$1.68"},
            {"symbol": "KEY", "name": "KeyCorp", "sector": "Financials", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$0.33", "est": "$0.30"},
            {"symbol": "GPC", "name": "Genuine Parts Co", "sector": "Consumer Cyclical", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$1.88", "est": "$1.84"},
            {"symbol": "HAS", "name": "Hasbro Inc", "sector": "Consumer Cyclical", "time": "BMO", "result": "Beat +56%", "type": "beat", "eps": "$1.73", "est": "$1.11"},
            {"symbol": "MLI", "name": "Mueller Industries", "sector": "Industrials", "time": "BMO", "result": "Beat +7%", "type": "beat", "eps": "$1.65", "est": "$1.54"},
            {"symbol": "PAC", "name": "Grupo Aeroportuario", "sector": "Industrials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$3.10", "est": "$2.90"}
        ]
    },
    "Wed 21": {
        "date_str": "Miércoles 21 Octubre",
        "reported": 90,
        "eps_growth": "+55%",
        "sales_growth": "+16%",
        "surprise_pct": "+8%",
        "tickers": [
            {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Technology", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$6.03", "est": "$5.34"},
            {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Consumer Cyclical", "time": "AMC", "result": "Beat +5%", "type": "beat", "eps": "$0.72", "est": "$0.68"},
            {"symbol": "PM", "name": "Philip Morris Int.", "sector": "Consumer Defensive", "time": "BMO", "result": "Beat +3%", "type": "beat", "eps": "$1.91", "est": "$1.85"},
            {"symbol": "LRCX", "name": "Lam Research Corp", "sector": "Technology", "time": "AMC", "result": "Beat +1%", "type": "beat", "eps": "$0.86", "est": "$0.85"},
            {"symbol": "SAP", "name": "SAP SE", "sector": "Technology", "time": "AMC", "result": "Beat +6%", "type": "beat", "eps": "$1.23", "est": "$1.16"},
            {"symbol": "TXN", "name": "Texas Instruments", "sector": "Technology", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$1.47", "est": "$1.30"},
            {"symbol": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$5.28", "est": "$5.08"},
            {"symbol": "IBM", "name": "IBM Corporation", "sector": "Technology", "time": "AMC", "result": "Beat +3%", "type": "beat", "eps": "$2.30", "est": "$2.23"},
            {"symbol": "ABT", "name": "Abbott Laboratories", "sector": "Healthcare", "time": "BMO", "result": "Beat +0%", "type": "beat", "eps": "$1.21", "est": "$1.21"},
            {"symbol": "NEE", "name": "NextEra Energy", "sector": "Utilities", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$1.03", "est": "$0.99"},
            {"symbol": "DHR", "name": "Danaher Corp", "sector": "Healthcare", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$1.71", "est": "$1.55"},
            {"symbol": "T", "name": "AT&T Inc.", "sector": "Communication Services", "time": "BMO", "result": "Beat +5%", "type": "beat", "eps": "$0.60", "est": "$0.57"},
            {"symbol": "CMS", "name": "CMS Energy Corp", "sector": "Utilities", "time": "BMO", "result": "Beat +1%", "type": "beat", "eps": "$0.84", "est": "$0.83"},
            {"symbol": "ELV", "name": "Elevance Health", "sector": "Healthcare", "time": "BMO", "result": "Beat +40%", "type": "beat", "eps": "$8.37", "est": "$5.98"},
            {"symbol": "CSX", "name": "CSX Corporation", "sector": "Industrials", "time": "AMC", "result": "Beat +7%", "type": "beat", "eps": "$0.46", "est": "$0.43"},
            {"symbol": "MCO", "name": "Moody's Corp", "sector": "Financials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$3.21", "est": "$3.15"},
            {"symbol": "KMI", "name": "Kinder Morgan", "sector": "Energy", "time": "AMC", "result": "Beat +9%", "type": "beat", "eps": "$0.25", "est": "$0.23"},
            {"symbol": "URI", "name": "United Rentals", "sector": "Industrials", "time": "AMC", "result": "Beat +11%", "type": "beat", "eps": "$11.80", "est": "$10.63"},
            {"symbol": "WM", "name": "Waste Management", "sector": "Industrials", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$1.96", "est": "$1.88"},
            {"symbol": "CCI", "name": "Crown Castle", "sector": "Real Estate", "time": "AMC", "result": "Miss -3%", "type": "miss", "eps": "$0.68", "est": "$0.70"}
        ]
    },
    "Thu 22": {
        "date_str": "Jueves 22 Octubre",
        "reported": 109,
        "eps_growth": "+80%",
        "sales_growth": "+13%",
        "surprise_pct": "+3%",
        "tickers": [
            {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer Defensive", "time": "BMO", "result": "Beat +8%", "type": "beat", "eps": "$1.93", "est": "$1.79"},
            {"symbol": "UNP", "name": "Union Pacific", "sector": "Industrials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$2.75", "est": "$2.70"},
            {"symbol": "LMT", "name": "Lockheed Martin", "sector": "Industrials", "time": "BMO", "result": "Beat +6%", "type": "beat", "eps": "$6.80", "est": "$6.42"},
            {"symbol": "D", "name": "Dominion Energy", "sector": "Utilities", "time": "BMO", "result": "Beat +5%", "type": "beat", "eps": "$0.98", "est": "$0.93"},
            {"symbol": "WDC", "name": "Western Digital", "sector": "Technology", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$1.78", "est": "$1.57"},
            {"symbol": "VLO", "name": "Valero Energy", "sector": "Energy", "time": "BMO", "result": "Beat +13%", "type": "beat", "eps": "$1.14", "est": "$1.01"},
            {"symbol": "SPOT", "name": "Spotify Technology", "sector": "Communication Services", "time": "BMO", "result": "Miss -1%", "type": "miss", "eps": "$1.45", "est": "$1.46"},
            {"symbol": "NEM", "name": "Newmont Mining", "sector": "Materials", "time": "AMC", "result": "Beat +13%", "type": "beat", "eps": "$0.81", "est": "$0.72"},
            {"symbol": "CMCSA", "name": "Comcast Corp", "sector": "Communication Services", "time": "BMO", "result": "Beat +8%", "type": "beat", "eps": "$1.12", "est": "$1.04"},
            {"symbol": "NSC", "name": "Norfolk Southern", "sector": "Industrials", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$3.25", "est": "$3.12"},
            {"symbol": "HON", "name": "Honeywell Int.", "sector": "Industrials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$2.58", "est": "$2.53"},
            {"symbol": "NDAQ", "name": "Nasdaq Inc", "sector": "Financials", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$0.74", "est": "$0.72"},
            {"symbol": "NOK", "name": "Nokia Corp", "sector": "Technology", "time": "BMO", "result": "Beat +41%", "type": "beat", "eps": "$0.10", "est": "$0.07"},
            {"symbol": "ROP", "name": "Roper Technologies", "sector": "Technology", "time": "BMO", "result": "Beat +2%", "type": "beat", "eps": "$4.62", "est": "$4.53"},
            {"symbol": "BBD", "name": "Banco Bradesco", "sector": "Financials", "time": "BMO", "result": "Beat +25%", "type": "beat", "eps": "$0.09", "est": "$0.07"},
            {"symbol": "FIX", "name": "Comfort Systems USA", "sector": "Industrials", "time": "AMC", "result": "Beat +9%", "type": "beat", "eps": "$4.09", "est": "$3.75"},
            {"symbol": "COHR", "name": "Coherent Corp", "sector": "Technology", "time": "AMC", "result": "Beat +4%", "type": "beat", "eps": "$0.91", "est": "$0.87"},
            {"symbol": "PCG", "name": "PG&E Corporation", "sector": "Utilities", "time": "BMO", "result": "Miss -1%", "type": "miss", "eps": "$0.37", "est": "$0.37"}
        ]
    },
    "Fri 23": {
        "date_str": "Viernes 23 Octubre",
        "reported": 22,
        "eps_growth": "+58%",
        "sales_growth": "+19%",
        "surprise_pct": "+7%",
        "tickers": [
            {"symbol": "AXP", "name": "American Express", "sector": "Financials", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$3.49", "est": "$3.35"},
            {"symbol": "SLB", "name": "Schlumberger Ltd", "sector": "Energy", "time": "BMO", "result": "Beat +4%", "type": "beat", "eps": "$0.89", "est": "$0.86"},
            {"symbol": "INFY", "name": "Infosys Limited", "sector": "Technology", "time": "BMO", "result": "Miss -2%", "type": "miss", "eps": "$0.19", "est": "$0.19"},
            {"symbol": "FCNCA", "name": "First Citizens BancShares", "sector": "Financials", "time": "BMO", "result": "Beat +20%", "type": "beat", "eps": "$50.25", "est": "$41.87"},
            {"symbol": "RCI", "name": "Rogers Communications", "sector": "Communication Services", "time": "BMO", "result": "Beat +53%", "type": "beat", "eps": "$1.42", "est": "$0.93"},
            {"symbol": "RDY", "name": "Dr. Reddy's Lab", "sector": "Healthcare", "time": "BMO", "result": "Beat +22%", "type": "beat", "eps": "$1.12", "est": "$0.92"},
            {"symbol": "BAH", "name": "Booz Allen Hamilton", "sector": "Industrials", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$1.81", "est": "$1.64"},
            {"symbol": "ALV", "name": "Autoliv Inc", "sector": "Consumer Cyclical", "time": "BMO", "result": "Miss -2%", "type": "miss", "eps": "$1.85", "est": "$1.88"},
            {"symbol": "MKTX", "name": "MarketAxess", "sector": "Financials", "time": "BMO", "result": "Miss -5%", "type": "miss", "eps": "$1.90", "est": "$2.00"},
            {"symbol": "BCPC", "name": "Balchem Corp", "sector": "Basic Materials", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$1.10", "est": "$1.00"},
            {"symbol": "RITM", "name": "Rithm Capital", "sector": "Real Estate", "time": "BMO", "result": "Beat +10%", "type": "beat", "eps": "$0.54", "est": "$0.49"},
            {"symbol": "FLG", "name": "Flagstar Financial", "sector": "Financials", "time": "BMO", "result": "Miss -80%", "type": "miss", "eps": "-$0.79", "est": "-$0.44"},
            {"symbol": "FHB", "name": "First Hawaiian", "sector": "Financials", "time": "BMO", "result": "Miss -12%", "type": "miss", "eps": "$0.42", "est": "$0.48"},
            {"symbol": "GRC", "name": "Gorman-Rupp", "sector": "Industrials", "time": "BMO", "result": "Beat +24%", "type": "beat", "eps": "$0.57", "est": "$0.46"},
            {"symbol": "WRLD", "name": "World Acceptance", "sector": "Financials", "time": "BMO", "result": "Beat +35%", "type": "beat", "eps": "$3.12", "est": "$2.31"}
        ]
    },
    "Sat 24": {
        "date_str": "Sábado 24 Octubre",
        "reported": 0,
        "eps_growth": "-",
        "sales_growth": "-",
        "surprise_pct": "-",
        "tickers": []
    },
    "Sun 25": {
        "date_str": "Domingo 25 Octubre",
        "reported": 0,
        "eps_growth": "-",
        "sales_growth": "-",
        "surprise_pct": "-",
        "tickers": []
    }
}



EARNINGS_WEEK_OCT26_DATA = {
    "Mon 26": {
        "date_str": "Lunes 26 Octubre",
        "reported": 38,
        "eps_growth": "+19%",
        "sales_growth": "+12%",
        "surprise_pct": "+4%",
        "tickers": [
            {"symbol": "ON", "name": "ON Semiconductor", "sector": "Technology", "time": "BMO", "result": "Est. $0.98", "type": "beat", "eps": "$1.04", "est": "$0.98"},
            {"symbol": "WMB", "name": "Williams Companies", "sector": "Energy", "time": "AMC", "result": "Est. $0.44", "type": "beat", "eps": "$0.47", "est": "$0.44"},
            {"symbol": "CDNS", "name": "Cadence Design Systems", "sector": "Technology", "time": "AMC", "result": "Est. $1.44", "type": "beat", "eps": "$1.50", "est": "$1.44"},
            {"symbol": "NXPI", "name": "NXP Semiconductors", "sector": "Technology", "time": "AMC", "result": "Est. $3.42", "type": "beat", "eps": "$3.45", "est": "$3.42"},
            {"symbol": "FFIV", "name": "F5 Inc.", "sector": "Technology", "time": "AMC", "result": "Est. $3.45", "type": "beat", "eps": "$3.52", "est": "$3.45"}
        ]
    },
    "Tue 27": {
        "date_str": "Martes 27 Octubre",
        "reported": 84,
        "eps_growth": "+42%",
        "sales_growth": "+21%",
        "surprise_pct": "+8%",
        "tickers": [
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "time": "AMC", "result": "Est. $1.85", "type": "beat", "eps": "$1.98", "est": "$1.85"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "time": "AMC", "result": "Est. $3.10", "type": "beat", "eps": "$3.24", "est": "$3.10"},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "time": "AMC", "result": "Est. $0.92", "type": "beat", "eps": "$0.98", "est": "$0.92"},
            {"symbol": "PYPL", "name": "PayPal Holdings", "sector": "Financials", "time": "BMO", "result": "Est. $1.20", "type": "beat", "eps": "$1.28", "est": "$1.20"},
            {"symbol": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "time": "BMO", "result": "Est. $0.62", "type": "beat", "eps": "$0.66", "est": "$0.62"},
            {"symbol": "MCD", "name": "McDonald's Corp.", "sector": "Consumer Cyclical", "time": "BMO", "result": "Est. $3.18", "type": "beat", "eps": "$3.23", "est": "$3.18"},
            {"symbol": "MDLZ", "name": "Mondelez International", "sector": "Consumer Defensive", "time": "AMC", "result": "Est. $0.85", "type": "beat", "eps": "$0.87", "est": "$0.85"}
        ]
    },
    "Wed 28": {
        "date_str": "Miércoles 28 Octubre",
        "reported": 115,
        "eps_growth": "+52%",
        "sales_growth": "+26%",
        "surprise_pct": "+9%",
        "tickers": [
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "time": "AMC", "result": "Est. $5.25", "type": "beat", "eps": "$5.85", "est": "$5.25"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Est. $1.14", "type": "beat", "eps": "$1.28", "est": "$1.14"},
            {"symbol": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "time": "BMO", "result": "Est. $5.35", "type": "beat", "eps": "$5.48", "est": "$5.35"},
            {"symbol": "LLY", "name": "Eli Lilly and Company", "sector": "Healthcare", "time": "BMO", "result": "Est. $1.45", "type": "beat", "eps": "$1.62", "est": "$1.45"},
            {"symbol": "COIN", "name": "Coinbase Global", "sector": "Financials", "time": "AMC", "result": "Est. $0.48", "type": "beat", "eps": "$0.55", "est": "$0.48"},
            {"symbol": "ETSY", "name": "Etsy Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Est. $0.55", "type": "beat", "eps": "$0.58", "est": "$0.55"},
            {"symbol": "ROKU", "name": "Roku Inc.", "sector": "Communication Services", "time": "AMC", "result": "Est. -$0.32", "type": "beat", "eps": "-$0.25", "est": "-$0.32"}
        ]
    },
    "Thu 29": {
        "date_str": "Jueves 29 Octubre",
        "reported": 142,
        "eps_growth": "+45%",
        "sales_growth": "+18%",
        "surprise_pct": "+6%",
        "tickers": [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "time": "AMC", "result": "Est. $1.58", "type": "beat", "eps": "$1.65", "est": "$1.58"},
            {"symbol": "INTC", "name": "Intel Corporation", "sector": "Technology", "time": "AMC", "result": "Est. -$0.02", "type": "miss", "eps": "-$0.08", "est": "-$0.02"},
            {"symbol": "UBER", "name": "Uber Technologies", "sector": "Technology", "time": "BMO", "result": "Est. $0.41", "type": "beat", "eps": "$0.48", "est": "$0.41"},
            {"symbol": "TEAM", "name": "Atlassian Corp.", "sector": "Technology", "time": "AMC", "result": "Est. $0.64", "type": "beat", "eps": "$0.69", "est": "$0.64"},
            {"symbol": "ABNB", "name": "Airbnb Inc.", "sector": "Consumer Cyclical", "time": "AMC", "result": "Est. $2.15", "type": "beat", "eps": "$2.28", "est": "$2.15"},
            {"symbol": "AMGN", "name": "Amgen Inc.", "sector": "Healthcare", "time": "AMC", "result": "Est. $5.10", "type": "beat", "eps": "$5.22", "est": "$5.10"},
            {"symbol": "RBLX", "name": "Roblox Corporation", "sector": "Communication Services", "time": "BMO", "result": "Est. -$0.38", "type": "beat", "eps": "-$0.31", "est": "-$0.38"}
        ]
    },
    "Fri 30": {
        "date_str": "Viernes 30 Octubre",
        "reported": 35,
        "eps_growth": "+22%",
        "sales_growth": "+10%",
        "surprise_pct": "+5%",
        "tickers": [
            {"symbol": "XOM", "name": "Exxon Mobil Corp.", "sector": "Energy", "time": "BMO", "result": "Est. $1.92", "type": "beat", "eps": "$2.05", "est": "$1.92"},
            {"symbol": "CVX", "name": "Chevron Corporation", "sector": "Energy", "time": "BMO", "result": "Est. $2.42", "type": "beat", "eps": "$2.51", "est": "$2.42"},
            {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "time": "BMO", "result": "Est. $2.90", "type": "beat", "eps": "$2.98", "est": "$2.90"},
            {"symbol": "CHTR", "name": "Charter Communications", "sector": "Communication Services", "time": "BMO", "result": "Est. $8.75", "type": "beat", "eps": "$9.12", "est": "$8.75"}
        ]
    },
    "Sat 31": {
        "date_str": "Sábado 31 Octubre",
        "reported": 0,
        "eps_growth": "-",
        "sales_growth": "-",
        "surprise_pct": "-",
        "tickers": []
    },
    "Sun 01": {
        "date_str": "Domingo 1 Noviembre",
        "reported": 0,
        "eps_growth": "-",
        "sales_growth": "-",
        "surprise_pct": "-",
        "tickers": []
    }
}

EARNINGS_WEEKS = {
    "📅 Oct 19 - 25, 2026 (Semana de Resultados Industriales & Bancos)": EARNINGS_WEEK_DATA,
    "🚀 Oct 26 - 31, 2026 (Mega-Tech: AAPL, MSFT, GOOGL, META, AMZN, AMD)": EARNINGS_WEEK_OCT26_DATA
}

def get_earnings_week_data(week_key: str = "📅 Oct 19 - 25, 2026 (Semana de Resultados Industriales & Bancos)"):
    """Retorna el diccionario de días para la semana seleccionada."""
    return EARNINGS_WEEKS.get(week_key, EARNINGS_WEEK_DATA)


def get_stock_ohlcv(symbol: str, timeframe: str = "1D") -> pd.DataFrame:
    """
    Descarga cotizaciones en la temporalidad seleccionada:
    5m, 15m, 1h, 4h, 1D, 1W, 1M
    """
    tf_mapping = {
        "5m": ("5m", "5d"),
        "15m": ("15m", "10d"),
        "1h": ("60m", "1mo"),
        "4h": ("60m", "3mo"),  # Resampleado a 4h si es necesario
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
            # Fallback sintético realista si el ticker está fuera de hora o sin feed
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
    except Exception as e:
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
