import json
import screener_engine as se
import discord_notifier as dn

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        webhook = json.load(f)["discord_webhook"]

    print("Escaneando mercado en tiempo real...")
    universe = se.UNIVERSES["Momentum & Alta Volatilidad (25)"]
    
    # 1. Escaneo de Swing (Trend Template)
    df_swing = se.run_swing_scanner(universe, "Trend Template (Etapa 2)", min_volume=500_000, min_price=10.0, max_dist_52w=25.0)
    print(f"Coincidencias de Swing encontradas: {len(df_swing)}")
    
    if not df_swing.empty:
        for _, row in df_swing.head(3).iterrows():
            ok = dn.send_trade_alert(webhook, row.to_dict(), scan_type="Swing Trading")
            print(f"Alerta Swing enviada para {row['Ticker']}: {ok}")

    # 2. Escaneo de Momentum / Day Trading
    df_day = se.run_daytrade_scanner(universe, "Top Gappers & RVOL", min_gap=0.5, min_rvol=1.0, min_price=5.0)
    print(f"Coincidencias de Day Trading encontradas: {len(df_day)}")
    
    if not df_day.empty:
        for _, row in df_day.head(2).iterrows():
            ok = dn.send_trade_alert(webhook, row.to_dict(), scan_type="Day Trading")
            print(f"Alerta Day Trading enviada para {row['Ticker']}: {ok}")

if __name__ == "__main__":
    main()
