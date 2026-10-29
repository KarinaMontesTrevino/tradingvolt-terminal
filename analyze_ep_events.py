import yfinance as yf
import pandas as pd
import numpy as np

ep_tickers = [
    "PRSO", "BRZE", "MYGN", "SAIQ", "LION", "HAS", "XPEV", "CWST", 
    "KVYO", "SLS", "EFX", "NESR", "HTFL", "MNDY", "RVMD", "SPHR", "SYRE", "BB"
]

data = yf.download(ep_tickers, period="3mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)

for t in ep_tickers:
    if t not in data.columns.levels[0]:
        continue
    df = data[t].dropna()
    if len(df) < 15:
        continue
        
    close = df["Close"]
    open_p = df["Open"]
    high = df["High"]
    low = df["Low"]
    vol = df["Volume"]
    vol_sma50 = vol.rolling(50, min_periods=10).mean()
    rvol = vol / vol_sma50
    ret = close.pct_change() * 100.0
    gap = ((open_p - close.shift(1)) / close.shift(1)) * 100.0
    
    # Check last 15 trading days
    recent = pd.DataFrame({
        "Close": close,
        "Open": open_p,
        "High": high,
        "Low": low,
        "Return": ret,
        "Gap": gap,
        "Volume": vol,
        "RVOL": rvol
    }).iloc[-15:]
    
    # Find candidate pivot days where RVOL >= 1.4 or Gap >= 4% or Return >= 5%
    pivots = recent[(recent["RVOL"] >= 1.3) | (recent["Return"] >= 5.0) | (recent["Gap"] >= 3.0)]
    
    print(f"\n=================== {t} ===================")
    for idx, row in pivots.iterrows():
        print(f"  {idx.strftime('%Y-%m-%d')}: Gap={row['Gap']:>+6.1f}% | Ret={row['Return']:>+6.1f}% | RVOL={row['RVOL']:>4.1f}x | Close=${row['Close']:>7.2f} | Vol={row['Volume']/1e6:>5.2f}M")
