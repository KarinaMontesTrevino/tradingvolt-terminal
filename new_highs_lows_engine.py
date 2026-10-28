"""
TradingVolt • New Highs / New Lows Engine
Reverse engineered directly from Deepvue Market Breadth & New Highs/Lows Screener.
Provides net breadth bar, leading vs lagging groups, sector/industry breakdowns, and interactive chart sync.
"""

from datetime import datetime
import pandas as pd
import numpy as np

# ----------------- BENCHMARK DATA: NEW HIGHS & NEW LOWS -----------------
NEW_HIGHS_TOTAL = 138
NEW_LOWS_TOTAL = 183

LEADING_GROUPS = [
    {"name": "Energy", "count": 24, "pct": "16%"},
    {"name": "Software & Services", "count": 23, "pct": "15%"},
    {"name": "Banks", "count": 20, "pct": "14%"},
    {"name": "Insurance", "count": 13, "pct": "10%"},
    {"name": "Commercial & Professional Services", "count": 9, "pct": "7%"},
    {"name": "Financial Services", "count": 9, "pct": "7%"},
    {"name": "Health Care Equipment & Services", "count": 5, "pct": "4%"},
    {"name": "Pharmaceuticals, Biotech & Life Sci", "count": 5, "pct": "4%"},
    {"name": "Utilities", "count": 5, "pct": "4%"},
    {"name": "Capital Goods", "count": 4, "pct": "3%"},
    {"name": "Technology Hardware & Equipment", "count": 3, "pct": "2%"},
    {"name": "Consumer Discretionary Distribution", "count": 2, "pct": "1%"}
]

LAGGING_GROUPS = [
    {"name": "Capital Goods", "count": 50, "pct": "19%"},
    {"name": "Pharmaceuticals, Biotech & Life Sci", "count": 36, "pct": "14%"},
    {"name": "Materials", "count": 27, "pct": "10%"},
    {"name": "Software & Services", "count": 19, "pct": "7%"},
    {"name": "Financial Services", "count": 16, "pct": "6%"},
    {"name": "Unclassified", "count": 14, "pct": "5%"},
    {"name": "Automobiles & Components", "count": 10, "pct": "4%"},
    {"name": "Consumer Services", "count": 10, "pct": "4%"},
    {"name": "Consumer Discretionary Distribution", "count": 9, "pct": "3%"},
    {"name": "Energy", "count": 8, "pct": "3%"},
    {"name": "Technology Hardware & Equipment", "count": 8, "pct": "3%"}
]

NEW_HIGHS_BY_SECTOR = {
    "Energy": {
        "count": 24, "share": "16%",
        "tickers": ["ROFX", "EQNR", "CHRD", "APA", "MUR", "PR", "OVV", "EOG", "BTC", "KMI", "MTDR", "OXY", "PSX", "RIG", "SLB", "VLO", "CVE", "PBR", "WMB", "DVN", "HAL", "BKR", "FANG", "TRGP"]
    },
    "Software & Services": {
        "count": 23, "share": "15%",
        "tickers": ["RBRK", "TEM", "OSPN", "ENG", "GLYS", "AVPT", "ALRM", "REXD", "APPN", "AMPL", "CRWD", "DDOG", "MNDY", "NOW", "PLTR", "ZS", "GTLB", "HUBS", "NET", "SNOW", "PATH", "ESTC", "DOCU"]
    },
    "Banks": {
        "count": 20, "share": "14%",
        "tickers": ["FCNCA", "CUBI", "FRGA", "CBOE", "CCSN", "FMAO", "AMTB", "CZFS", "CBO", "FNLG", "JPM", "BAC", "WFC", "C", "FITB", "HBAN", "ZION", "KEY", "WAL", "CFG"]
    },
    "Insurance": {
        "count": 13, "share": "10%",
        "tickers": ["SIGI", "SLDE", "UVE", "SAFT", "WTG", "KPR", "MRSH", "NLPE", "BIG", "PLRO", "PGR", "ALL", "TRV"]
    },
    "Commercial & Professional Services": {
        "count": 9, "share": "7%",
        "tickers": ["RHI", "TNET", "HURN", "MMS", "PAYC", "CTAG", "ANDG", "RSG", "ADP"]
    },
    "Financial Services": {
        "count": 9, "share": "7%",
        "tickers": ["AXS", "ZNB", "OPN", "CUPR", "GLXY", "GRN", "FRMI", "GEMI", "MCO"]
    },
    "Health Care Equipment & Services": {
        "count": 5, "share": "4%",
        "tickers": ["AMN", "HTFL", "HSTM", "CRVL", "MD"]
    },
    "Pharmaceuticals, Biotech & Life Sci": {
        "count": 5, "share": "4%",
        "tickers": ["BOLT", "GMAB", "HALO", "TAK", "PBYI"]
    },
    "Capital Goods": {
        "count": 4, "share": "3%",
        "tickers": ["MAGH", "ACA", "ATKR", "TTC"]
    },
    "Technology Hardware & Equipment": {
        "count": 3, "share": "2%",
        "tickers": ["NSIT", "QCOM", "AAPL"]
    }
}

NEW_LOWS_BY_SECTOR = {
    "Capital Goods": {
        "count": 50, "share": "19%",
        "tickers": ["SOST", "FJET", "TGE", "IEP", "FSN", "HWM", "CROC", "SERV", "ARRY", "GIC", "BA", "LMT", "NOC", "GD", "TXT", "PWR", "EMR"]
    },
    "Pharmaceuticals, Biotech & Life Sci": {
        "count": 36, "share": "14%",
        "tickers": ["AARD", "SBPH", "SPRC", "CLMA", "NAMS", "UPR", "MRNA", "BNTX", "BIIB", "ILMN", "CRSP", "NTLA"]
    },
    "Materials": {
        "count": 27, "share": "10%",
        "tickers": ["NWGL", "NVA", "USAS", "IDR", "TMQ", "USAR", "AA", "FCX", "NUE", "DOW", "ALB"]
    },
    "Software & Services": {
        "count": 19, "share": "7%",
        "tickers": ["HUSB", "FROT", "MI", "QNC", "BTBT", "OMLE", "WYFI", "CHDW", "RTOR", "CYAR"]
    },
    "Financial Services": {
        "count": 16, "share": "6%",
        "tickers": ["AXS", "ZNB", "OPN", "CUPR", "LU", "GLXY", "GRN", "FRMI", "GEMI", "BKKT"]
    },
    "Automobiles & Components": {
        "count": 10, "share": "4%",
        "tickers": ["VC", "MBLY", "GNTX", "STLA", "DCX", "ADNT", "APTV", "KDK", "RIVN", "DCH"]
    },
    "Consumer Services": {
        "count": 10, "share": "4%",
        "tickers": ["KRUS", "PZN", "MLCO", "MGM", "DNUT", "WYNN", "PZZA", "NTCL", "CMG", "DRI"]
    }
}
