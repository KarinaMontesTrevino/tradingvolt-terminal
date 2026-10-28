import yfinance as yf
import pandas as pd
import numpy as np

# 18 Target EP tickers from the user
target_eps = [
    "PRSO", "BRZE", "MYGN", "SAIQ", "LION", "HAS", "XPEV", "CWST", 
    "KVYO", "SLS", "EFX", "NESR", "HTFL", "MNDY", "RVMD", "SPHR", "SYRE", "BB"
]

print("Verifying the 18 EP candidates against technical EP criteria...")

# Download data for target EPs
data = yf.download(target_eps, period="1mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)

results = []
for t in target_eps:
    if t not in data.columns.levels[0]:
        continue
    df = data[t].dropna()
    if len(df) < 5:
        continue
        
    close = df["Close"]
    open_p = df["Open"]
    high = df["High"]
    low = df["Low"]
    vol = df["Volume"]
    
    vol_sma20 = vol.rolling(20, min_periods=5).mean()
    
    # Check today (last bar) and yesterday (last 2 bars)
    for offset in [0, 1]:
        bar_idx = -(offset + 1)
        curr_c = float(close.iloc[bar_idx])
        curr_o = float(open_p.iloc[bar_idx])
        curr_h = float(high.iloc[bar_idx])
        curr_l = float(low.iloc[bar_idx])
        curr_v = float(vol.iloc[bar_idx])
        
        prev_c = float(close.iloc[bar_idx - 1])
        prior_h = float(high.iloc[bar_idx - 1])
        avg_v = float(vol_sma20.iloc[bar_idx - 1])
        
        pct_change = ((curr_c - prev_c) / prev_c) * 100.0
        gap_pct = ((curr_o - prev_c) / prev_c) * 100.0
        rvol = curr_v / (avg_v + 1e-6)
        
        candle_range = curr_h - curr_l
        closing_range = ((curr_c - curr_l) / (candle_range if candle_range > 0 else 1.0)) * 100.0
        closed_above_prior_high = 1 if curr_c > prior_h else 0
        
        # 10-day breakout
        prior_10d_high = float(high.iloc[max(0, len(df) - 12):-1].max()) if len(df) >= 12 else prior_h
        breakout_10d = 1 if curr_h >= prior_10d_high else 0

        results.append({
            "ticker": t,
            "day_offset": offset,
            "date": str(df.index[bar_idx].date()),
            "close": curr_c,
            "pct_change": round(pct_change, 2),
            "gap_pct": round(gap_pct, 2),
            "rvol": round(rvol, 2),
            "volume_mil": round(curr_v / 1e6, 2),
            "closing_range_%": round(closing_range, 1),
            "above_prior_high": closed_above_prior_high,
            "breakout_10d": breakout_10d
        })

df_eval = pd.DataFrame(results)
print("\n=== EP EVALUATION ACROSS THE 18 CANDIDATES ===")
print(df_eval[df_eval["day_offset"] == 0][["ticker", "close", "pct_change", "gap_pct", "rvol", "volume_mil", "closing_range_%", "above_prior_high", "breakout_10d"]].to_string(index=False))
