import urllib.request
import pandas as pd
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# Nasdaq 100 components from slickcharts or wikipedia
url = 'https://www.slickcharts.com/nasdaq100'
req = urllib.request.Request(url, headers=headers)
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    tables = pd.read_html(html)
    ndx = tables[0]['Symbol'].str.replace('.', '-').str.strip().tolist()
    print(f"Nasdaq 100 fetched: {len(ndx)} tickers")
except Exception as e:
    print(f"Slickcharts fallback: {e}")
    # Standard official 101 Nasdaq 100 tickers
    ndx = [
        "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD", "AMGN",
        "AMZN", "ANSS", "APP", "ARM", "ASML", "AVGO", "AXON", "BIIB", "BKNG", "BKR",
        "CCEP", "CDNS", "CDW", "CEG", "CHTR", "CMCSA", "COST", "CPRT", "CRWD", "CSCO",
        "CSGP", "CSX", "CTAS", "CTSH", "DASH", "DDOG", "DLTR", "DXCM", "EA", "EXC",
        "FANG", "FAST", "FTNT", "GEHC", "GFS", "GILD", "GOOG", "GOOGL", "HON", "IDXX",
        "ILMN", "INTC", "INTU", "ISRG", "KDP", "KHC", "KLAC", "LIN", "LRCX", "LULU",
        "MAR", "MCHP", "MDB", "MDLZ", "MELI", "META", "MNST", "MRNA", "MRVL", "MSFT",
        "MSTR", "MU", "NFLX", "NVDA", "NXPI", "ODFL", "ON", "ORLY", "PANW", "PAYX",
        "PCAR", "PDD", "PEP", "PLTR", "PYPL", "QCOM", "REGN", "ROP", "ROST", "SBUX",
        "SNPS", "TEAM", "TMUS", "TSLA", "TTD", "TTWO", "TXN", "VRSK", "VRTX", "WBD",
        "WDAY", "XEL", "ZS"
    ]
    print(f"Using standard Nasdaq 100: {len(ndx)} tickers")

with open('C:/Users/kim17/.gemini/antigravity/scratch/trading_screener/ndx_cache.json', 'w') as f:
    json.dump(sorted(list(set(ndx))), f, indent=2)
print("Saved ndx_cache.json")
