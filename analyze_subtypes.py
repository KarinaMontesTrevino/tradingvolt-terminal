import pandas as pd

df = pd.read_csv(r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\tml_statistical_study.csv")
tml = df[df["is_tml"] == 1]

print(f"Total TML: {len(tml)}")
p_leaders = tml[(tml["above_sma20"] == 1) & (tml["above_sma50"] == 1) & (tml["dist_52h"] >= -15)]
print(f"1. Classic Stage 2 Momentum Leaders (Dist52H >= -15% & >SMA20 & >SMA50): {len(p_leaders)} ({len(p_leaders)/len(tml)*100:.1f}%)")

pullback = tml[(tml["dist_52h"] >= -25) & ((tml["above_sma20"] == 0) | (tml["above_sma50"] == 0))]
print(f"2. High RS Pullback / Base Consolidations (Dist52H >= -25% but testing SMA20/50): {len(pullback)} ({len(pullback)/len(tml)*100:.1f}%)")

turnaround = tml[tml["dist_52h"] < -25]
print(f"3. Velocity Turnarounds / EP / Bottom Rockets (Dist52H < -25%): {len(turnaround)} ({len(turnaround)/len(tml)*100:.1f}%)")
print("\nSample Turnarounds / Explosive Reversals:")
for _, r in turnaround.sort_values(by="roc_63", ascending=False).head(10).iterrows():
    print(f"   {r['ticker']:<6}: 3M ROC = +{r['roc_63']:>5.1f}% | 1M ROC = +{r['roc_21']:>5.1f}% | Dist52H = {r['dist_52h']:>5.1f}% | Dist52L = +{r['dist_52l']:>5.1f}%")

print("\nSample Classic Stage 2 Leaders:")
for _, r in p_leaders.sort_values(by="weighted_rs", ascending=False).head(10).iterrows():
    print(f"   {r['ticker']:<6}: Weighted RS = {r['weighted_rs']:>5.1f} | 3M ROC = +{r['roc_63']:>5.1f}% | Dist52H = {r['dist_52h']:>5.1f}% | U/D Vol = {r['ud_ratio']:.2f}")
