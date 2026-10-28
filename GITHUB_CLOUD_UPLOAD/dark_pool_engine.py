"""
TradingVolt • Dark Pool & Off-Exchange Analytics Engine
100% Free - Powered by FINRA TRF trade reporting via Alpaca API.

Key Capabilities:
1. TRF Off-Exchange Filtering (Exchange code 'D' = FINRA TRF)
2. Institutional Classification (Whale >= $1M, Large >= $250k, Block >= $100k)
3. Sentiment / Tick Rule (Uptick = Buyer Agression, Downtick = Seller Agression, Midpoint = Neutral)
4. Dark Pool Index (DPI %): Off-Exchange Volume vs Lit Volume
5. Dark Pool Clustering (Key Support/Resistance levels where whales transacted)
"""
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockTradesRequest
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

EASTERN = ZoneInfo("America/New_York")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_alpaca_credentials():
    api_key, secret_key = "", ""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_key = cfg.get("alpaca_api_key", "")
                secret_key = cfg.get("alpaca_secret_key", "")
        except Exception:
            pass
    if not api_key or not secret_key:
        api_key = os.getenv("ALPACA_API_KEY", "")
        secret_key = os.getenv("ALPACA_SECRET_KEY", "")
    return api_key, secret_key


def classify_trade_tier(notional: float) -> tuple[str, str]:
    """Clasifica el tamaño institucional de la orden en Dark Pool."""
    if notional >= 1_000_000:
        return "WHALE_MEGA", "🐋 WHALE (≥ $1M)"
    elif notional >= 500_000:
        return "WHALE_LARGE", "🦈 TIBURÓN (≥ $500k)"
    elif notional >= 250_000:
        return "INST_LARGE", "🏛️ INSTITUCIONAL (≥ $250k)"
    elif notional >= 100_000:
        return "BLOCK_STD", "📦 BLOQUE (≥ $100k)"
    elif notional >= 50_000:
        return "BLOCK_MED", "🔹 SUB-BLOQUE (≥ $50k)"
    else:
        return "RETAIL_CROSS", "▫️ MENOR (< $50k)"


def fetch_and_classify_dark_pools(
    ticker: str,
    api_key: str = None,
    secret_key: str = None,
    min_notional: float = 50_000,
    lookback_minutes: int = 240,
    limit: int = 5000
) -> dict:
    """
    Descarga y clasifica todas las transacciones de Dark Pool (TRF) para un ticker.
    Calcula:
    - Lista de prints clasificados
    - Sentimiento (Tick Rule / Presión Compra vs Venta)
    - Dark Pool Index (DPI %)
    - Niveles clave de acumulación institucional (Clusters)
    """
    if not api_key or not secret_key:
        api_key, secret_key = load_alpaca_credentials()
        
    if not api_key or not secret_key or not ALPACA_AVAILABLE:
        return {
            "success": False,
            "error": "Credenciales de Alpaca no configuradas o SDK no disponible."
        }
        
    client = StockHistoricalDataClient(api_key.strip(), secret_key.strip())
    start_time = datetime.now() - timedelta(minutes=lookback_minutes)
    
    clean_sym = ticker.strip().upper().replace('-', '.')
    
    try:
        req = StockTradesRequest(
            symbol_or_symbols=clean_sym,
            start=start_time,
            limit=limit
        )
        trades_res = client.get_stock_trades(req)
        raw_df = trades_res.df
        
        if raw_df.empty:
            return {
                "success": True,
                "ticker": ticker,
                "total_trades": 0,
                "dp_trades": 0,
                "dpi_pct": 0.0,
                "prints_df": pd.DataFrame(),
                "clusters_df": pd.DataFrame(),
                "sentiment_summary": {}
            }
            
        if clean_sym in raw_df.index.levels[0]:
            df = raw_df.loc[clean_sym].copy()
        else:
            df = raw_df.copy()
            
        # Ordenar por timestamp
        df = df.sort_index()
        
        # Total volumen negociado en la muestra (Lit + Dark Pool)
        total_sample_volume = int(df['size'].sum())
        total_sample_trades = len(df)
        
        # Filtro Dark Pool: Exchange 'D' (FINRA TRF)
        dp_mask = (df['exchange'] == 'D')
        dp_df = df[dp_mask].copy()
        
        dp_volume = int(dp_df['size'].sum()) if not dp_df.empty else 0
        dpi_pct = (dp_volume / total_sample_volume * 100.0) if total_sample_volume > 0 else 0.0
        
        if dp_df.empty:
            return {
                "success": True,
                "ticker": ticker,
                "total_trades": total_sample_trades,
                "dp_trades": 0,
                "dpi_pct": 0.0,
                "prints_df": pd.DataFrame(),
                "clusters_df": pd.DataFrame(),
                "sentiment_summary": {}
            }
            
        # 1. Aplicación de Tick Rule para clasificar intención compradora / vendedora
        # Compara el precio de cada trade con el del trade anterior
        dp_df['prev_price'] = dp_df['price'].shift(1).fillna(dp_df['price'])
        price_diff = dp_df['price'] - dp_df['prev_price']
        
        conditions = [
            (price_diff > 0),
            (price_diff < 0),
            (price_diff == 0)
        ]
        choices_side = ['BUY', 'SELL', 'NEUTRAL']
        choices_label = ['🟢 COMPRA (Uptick)', '🔴 VENTA (Downtick)', '⚪ NEUTRO (Midpoint)']
        choices_color = ['#00FF87', '#FF2E63', '#94A3B8']
        
        dp_df['side'] = np.select(conditions, choices_side, default='NEUTRAL')
        dp_df['side_label'] = np.select(conditions, choices_label, default='⚪ NEUTRO')
        dp_df['side_color'] = np.select(conditions, choices_color, default='#94A3B8')
        
        dp_df['notional'] = dp_df['price'] * dp_df['size']
        
        # 2. Asignar Tiers institucionales
        tiers = [classify_trade_tier(n) for n in dp_df['notional']]
        dp_df['tier_code'] = [t[0] for t in tiers]
        dp_df['tier_label'] = [t[1] for t in tiers]
        
        # 3. Filtrar por notional mínimo solicitado
        filtered_dp = dp_df[dp_df['notional'] >= min_notional].copy()
        
        # 4. Métricas de Sentimiento Institucional
        buy_notional = float(filtered_dp[filtered_dp['side'] == 'BUY']['notional'].sum())
        sell_notional = float(filtered_dp[filtered_dp['side'] == 'SELL']['notional'].sum())
        neutral_notional = float(filtered_dp[filtered_dp['side'] == 'NEUTRAL']['notional'].sum())
        total_filtered_notional = buy_notional + sell_notional + neutral_notional
        
        active_flow = buy_notional + sell_notional
        bull_ratio = (buy_notional / active_flow * 100.0) if active_flow > 0 else 50.0
        
        sentiment_label = "ACUMULACIÓN NETA (BULL)" if bull_ratio >= 55.0 else ("DISTRIBUCIÓN NETA (BEAR)" if bull_ratio <= 45.0 else "EQUILIBRIO / CROSS")
        sentiment_color = "#00FF87" if bull_ratio >= 55.0 else ("#FF2E63" if bull_ratio <= 45.0 else "#00F0FF")
        
        # 5. Detección de Clusters de Precio (Dark Pool Support / Resistance)
        # Agrupa los prints en niveles de precio redondeados a centavos o rangos según el precio
        round_digits = 1 if dp_df['price'].iloc[-1] >= 100 else 2
        filtered_dp['price_cluster'] = filtered_dp['price'].round(round_digits)
        
        clusters = filtered_dp.groupby('price_cluster').agg(
            total_notional=('notional', 'sum'),
            total_shares=('size', 'sum'),
            print_count=('size', 'count'),
            buy_notional=('notional', lambda x: x[filtered_dp.loc[x.index, 'side'] == 'BUY'].sum()),
            sell_notional=('notional', lambda x: x[filtered_dp.loc[x.index, 'side'] == 'SELL'].sum())
        ).reset_index()
        
        clusters = clusters.sort_values(by='total_notional', ascending=False).reset_index(drop=True)
        clusters['notional_m'] = clusters['total_notional'] / 1_000_000.0
        clusters['pct_of_dp'] = (clusters['total_notional'] / (total_filtered_notional + 1e-9)) * 100.0
        
        # 6. Formatear DataFrame de Prints para visualización UI
        disp_prints = filtered_dp.reset_index().copy()
        disp_prints['time_str'] = pd.to_datetime(disp_prints['timestamp']).dt.tz_convert(EASTERN).dt.strftime('%H:%M:%S')
        disp_prints['notional_str'] = disp_prints['notional'].apply(lambda x: f"${x:,.2f}")
        disp_prints['price_str'] = disp_prints['price'].apply(lambda x: f"${x:.2f}")
        disp_prints['size_str'] = disp_prints['size'].apply(lambda x: f"{x:,}")
        
        # Orden descendente por tiempo (más reciente primero)
        disp_prints = disp_prints.sort_values(by='timestamp', ascending=False).reset_index(drop=True)
        
        return {
            "success": True,
            "ticker": ticker,
            "total_trades": total_sample_trades,
            "dp_trades": len(dp_df),
            "matched_block_count": len(filtered_dp),
            "dpi_pct": dpi_pct,
            "total_dp_notional": total_filtered_notional,
            "buy_notional": buy_notional,
            "sell_notional": sell_notional,
            "neutral_notional": neutral_notional,
            "bull_ratio_pct": bull_ratio,
            "sentiment_label": sentiment_label,
            "sentiment_color": sentiment_color,
            "last_price": float(df['price'].iloc[-1]) if not df.empty else 0.0,
            "clusters_df": clusters.head(10),
            "prints_df": disp_prints[[
                'time_str', 'price_str', 'size_str', 'notional_str', 'tier_label', 'side_label', 'price', 'size', 'notional'
            ]]
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error descargando trades de Alpaca: {e}"
        }


def scan_multiticker_dark_pool_rankings(
    tickers: list[str],
    min_notional: float = 100_000,
    lookback_minutes: int = 120
) -> pd.DataFrame:
    """
    Escanea una lista de tickers (ej. Top 30 Leaders) y rankea los que tienen mayor actividad
    anormal en Dark Pools (mayor DPI % y mayor volumen nocional oculto).
    """
    api_key, secret_key = load_alpaca_credentials()
    if not api_key or not secret_key:
        return pd.DataFrame()
        
    results = []
    for t in tickers:
        try:
            res = fetch_and_classify_dark_pools(
                ticker=t,
                api_key=api_key,
                secret_key=secret_key,
                min_notional=min_notional,
                lookback_minutes=lookback_minutes,
                limit=1500
            )
            if res.get("success") and res.get("matched_block_count", 0) > 0:
                results.append({
                    "Ticker": t,
                    "Precio": f"${res['last_price']:.2f}",
                    "DPI (%)": round(res["dpi_pct"], 1),
                    "Nocional Dark Pool ($M)": round(res["total_dp_notional"] / 1_000_000, 2),
                    "Bloques Detectados": res["matched_block_count"],
                    "Ratio Comprador (%)": f"{res['bull_ratio_pct']:.1f}%",
                    "Sentimiento": res["sentiment_label"],
                    "raw_notional": res["total_dp_notional"],
                    "raw_dpi": res["dpi_pct"]
                })
        except Exception:
            continue
            
    if not results:
        return pd.DataFrame()
        
    df_rank = pd.DataFrame(results)
    return df_rank.sort_values(by="raw_notional", ascending=False).reset_index(drop=True)
