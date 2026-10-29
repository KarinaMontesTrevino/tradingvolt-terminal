import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

ep_tickers = [
    "PRSO", "BRZE", "MYGN", "SAIQ", "LION", "HAS", "XPEV", "CWST", 
    "KVYO", "SLS", "EFX", "NESR", "HTFL", "MNDY", "RVMD", "SPHR", "SYRE", "BB"
]

print(f"Downloading data for {len(ep_tickers)} candidate EP tickers...")
data = yf.download(ep_tickers, period="3mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)

records = []
for t in ep_tickers:
    try:
        if t not in data.columns.levels[0]:
            print(f"No data for {t}")
            continue
        df = data[t].dropna()
        if len(df) < 20:
            continue
            
        close = df["Close"]
        open_p = df["Open"]
        high = df["High"]
        low = df["Low"]
        vol = df["Volume"]
        
        # 50d avg volume (or expanding)
        vol_sma50 = vol.rolling(50, min_periods=10).mean()
        rvol = vol / vol_sma50
        
        # Daily return
        ret = close.pct_change() * 100.0
        
        # Gap % (Open vs prior Close)
        gap = ((open_p - close.shift(1)) / close.shift(1)) * 100.0
        
        # Range %
        day_range = ((high - low) / low) * 100.0
        
        # Closing Range: where did it close within the day's candle? (Close - Low) / (High - Low)
        candle_len = high - low
        closing_range = ((close - low) / (candle_len.replace(0, np.nan))) * 100.0
        
        # Find the max volume surge / max 1-day gain in the last 15 trading days
        lookback = min(20, len(df))
        recent_df = pd.DataFrame({
            "Date": df.index[-lookback:],
            "Close": close.iloc[-lookback:],
            "Return": ret.iloc[-lookback:],
            "Gap": gap.iloc[-lookback:],
            "RVOL": rvol.iloc[-lookback:],
            "Volume": vol.iloc[-lookback:],
            "VolSMA50": vol_sma50.iloc[-lookback:],
            "ClosingRange": closing_range.iloc[-lookback:]
        })
        
        # Find the day with the highest RVOL or largest positive jump in the last 15 days
        # An EP is characterized by a spike day
        # Filter for days with positive return or positive gap
        pos_days = recent_df[recent_df["Return"] > 0]
        if not pos_days.empty:
            # Day with highest RVOL that had a positive return or gap
            best_rvol_idx = recent_df["RVOL"].idxmax()
            best_ret_idx = recent_df["Return"].idxmax()
            
            # Let's inspect the most significant volume day
            pivot_row = recent_df.loc[best_rvol_idx]
            ret_pivot_row = recent_df.loc[best_ret_idx]
            
            # Days ago the pivot happened
            days_ago_rvol = len(df) - 1 - df.index.get_loc(best_rvol_idx)
            days_ago_ret = len(df) - 1 - df.index.get_loc(best_ret_idx)
            
            # Current price and current metrics
            curr_price = float(close.iloc[-1])
            curr_vol = float(vol.iloc[-1])
            curr_rvol = float(rvol.iloc[-1])
            curr_ret = float(ret.iloc[-1])
            curr_gap = float(gap.iloc[-1])
            
            # SMA 20, 50, 200
            sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else curr_price
            sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else curr_price
            
            # Performance since pivot
            pivot_close = float(pivot_row["Close"])
            ret_since_pivot = ((curr_price - pivot_close) / pivot_close) * 100.0
            
            records.append({
                "ticker": t,
                "curr_price": curr_price,
                "curr_ret_%": curr_ret,
                "curr_gap_%": curr_gap,
                "curr_rvol": curr_rvol,
                "pivot_date": str(best_rvol_idx.date()),
                "pivot_days_ago": days_ago_rvol,
                "pivot_ret_%": float(pivot_row["Return"]),
                "pivot_gap_%": float(pivot_row["Gap"]),
                "pivot_rvol": float(pivot_row["RVOL"]),
                "pivot_close_range_%": float(pivot_row["ClosingRange"]),
                "max_1d_gain_20d_%": float(ret_pivot_row["Return"]),
                "max_gain_days_ago": days_ago_ret,
                "max_rvol_20d": float(recent_df["RVOL"].max()),
                "ret_since_pivot_%": ret_since_pivot,
                "above_sma20": 1 if curr_price >= sma20 else 0,
                "above_sma50": 1 if curr_price >= sma50 else 0
            })
    except Exception as e:
        print(f"Error {t}: {e}")

df_ep = pd.DataFrame(records)
print("\n" + "="*95)
print("EPISODIC PIVOT (EP) CANDIDATES DETAILED QUANTITATIVE PROFILE")
print("="*95)
print(df_ep.to_string(index=False))

df_ep.to_csv(r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\ep_candidates_profile.csv", index=False)
