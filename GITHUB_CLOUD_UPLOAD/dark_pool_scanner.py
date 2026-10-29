"""
TradingVolt • Free Real-Time Dark Pool & TRF Block Scanner
Uses Alpaca's free market data feed (IEX/SIP) to filter for FINRA TRF / off-exchange prints.
Exchange 'D' = FINRA Trade Reporting Facility (Off-Exchange / Dark Pool executions).
"""
import argparse
import os
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockTradesRequest

EASTERN = ZoneInfo("America/New_York")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
API_KEY = ""
SECRET_KEY = ""

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            API_KEY = cfg.get("alpaca_api_key", "")
            SECRET_KEY = cfg.get("alpaca_secret_key", "")
    except Exception:
        pass

if not API_KEY or not SECRET_KEY:
    API_KEY = os.getenv("ALPACA_API_KEY", "")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

EXCHANGE_NAMES = {
    "D": "FINRA TRF (Dark Pool / Off-Exchange)",
    "V": "Investors Exchange (IEX)",
    "P": "NYSE Arca",
    "T": "NASDAQ (Carteret)",
    "Q": "NASDAQ",
    "N": "New York Stock Exchange (NYSE)",
    "A": "NYSE American",
    "Z": "Cboe BZX",
    "K": "Cboe EDGX",
    "J": "Cboe EDGA",
    "B": "NASDAQ OMX BX"
}

def fmt_time(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(EASTERN).strftime("%Y-%m-%d %H:%M:%S EST")

def format_dark_pool_print(symbol: str, price: float, size: int, exchange: str, timestamp: datetime, conditions=None) -> str:
    notional = price * size
    venue = EXCHANGE_NAMES.get(exchange, f"Exchange {exchange}")
    cond_str = ", ".join(conditions) if conditions else "Regular"
    
    lines = [
        "",
        f"⚡ DARK POOL BLOCK PRINT: {symbol}",
        f"  Precio:    ${price:,.2f}",
        f"  Tamaño:    {size:,} acciones",
        f"  Nocional:  ${notional:,.2f}",
        f"  Venue:     {venue}",
        f"  Timestamp: {fmt_time(timestamp)}",
        f"  Condición: {cond_str}",
        "  " + ("-" * 32)
    ]
    return "\n".join(lines)

def scan_recent_dark_pools(symbols: list[str], min_notional: float = 100_000, minutes_back: int = 120):
    """Escanea trades históricos recientes buscando bloques de Dark Pool (TRF)."""
    client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    start_time = datetime.now() - timedelta(minutes=minutes_back)
    
    print(f"\n[+] Buscando impresiones de Dark Pool (TRF) >= ${min_notional:,.0f} en los últimos {minutes_back} min...")
    total_dp_volume = 0
    total_dp_notional = 0
    matched_blocks = []

    for sym in symbols:
        try:
            req = StockTradesRequest(
                symbol_or_symbols=sym,
                start=start_time,
                limit=1000
            )
            trades = client.get_stock_trades(req)
            if trades.df.empty:
                continue
            
            df = trades.df
            if sym in df.index.levels[0]:
                df = df.loc[sym]
                
            for ts, row in df.iterrows():
                exch = str(row.get('exchange', ''))
                # 'D' = FINRA TRF / Dark Pool
                if exch == 'D':
                    p = float(row.get('price', 0))
                    s = int(row.get('size', 0))
                    notional = p * s
                    if notional >= min_notional:
                        matched_blocks.append({
                            'symbol': sym,
                            'price': p,
                            'size': s,
                            'notional': notional,
                            'exchange': exch,
                            'timestamp': ts,
                            'conditions': row.get('conditions', [])
                        })
                        total_dp_volume += s
                        total_dp_notional += notional
        except Exception as e:
            print(f"Error procesando {sym}: {e}")
            
    print(f"[✓] Encontrados {len(matched_blocks)} bloques institucionales de Dark Pool.")
    for b in matched_blocks[-10:]: # Mostrar últimos 10
        print(format_dark_pool_print(
            b['symbol'], b['price'], b['size'], b['exchange'], b['timestamp'], b['conditions']
        ))
    return matched_blocks

def stream_live_dark_pools(symbols: list[str], min_notional: float = 100_000):
    """Escucha en tiempo real vía WebSocket prints de Dark Pool (FINRA TRF exchange 'D')."""
    if not API_KEY or not SECRET_KEY:
        print("[!] Error: Se requieren credenciales de Alpaca para WebSocket.")
        return

    sym_label = ", ".join(symbols) if symbols else "TODOS LOS ACTIVOS"
    print(f"\n⚡ INICIANDO WEBSOCKET STREAMING EN VIVO (DARK POOL / TRF)")
    print(f"  Activos:   {sym_label}")
    print(f"  Filtro:    Bloques >= ${min_notional:,.0f} nocional")
    print(f"  Venue:     Exchange 'D' (FINRA TRF Carteret / Chicago / NYSE TRF)")
    print(f"  Presiona Ctrl+C para detener.\n")

    stream = StockDataStream(API_KEY, SECRET_KEY)

    async def trade_callback(trade):
        exch = str(getattr(trade, "exchange", ""))
        if exch == "D":
            price = float(getattr(trade, "price", 0))
            size = int(getattr(trade, "size", 0))
            notional = price * size
            if notional >= min_notional:
                cond = getattr(trade, "conditions", [])
                ts = getattr(trade, "timestamp", datetime.now())
                print(format_dark_pool_print(
                    trade.symbol, price, size, exch, ts, cond
                ), flush=True)

    target_syms = symbols if symbols else ["*"]
    stream.subscribe_trades(trade_callback, *target_syms)
    try:
        stream.run()
    except KeyboardInterrupt:
        print("\nStream detenido por el usuario.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TradingVolt Free Dark Pool / TRF Scanner")
    parser.add_argument("--ticker", nargs="+", default=["SPY", "QQQ", "NVDA", "AAPL", "TSLA"], help="Tickers a vigilar")
    parser.add_argument("--min-notional", type=float, default=100_000, help="Nocional mínimo en USD (default: $100,000)")
    parser.add_argument("--minutes", type=int, default=180, help="Minutos hacia atrás para escaneo histórico")
    parser.add_argument("--stream", action="store_true", help="Activar modo streaming en tiempo real vía WebSocket")
    args = parser.parse_args()

    if args.stream:
        stream_live_dark_pools(args.ticker, min_notional=args.min_notional)
    else:
        scan_recent_dark_pools(args.ticker, min_notional=args.min_notional, minutes_back=args.minutes)
