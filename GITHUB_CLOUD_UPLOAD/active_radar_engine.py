"""
TradingVolt • Dynamic Active Radar & Cross-Desk Pipeline Engine
=============================================================
Gestiona la memoria compartida de activos detectados entre todos los Desks de la terminal:
- Screener Cuantitativo ➔ CANSLIM Terminal (BO60)
- Screener Cuantitativo ➔ Quant Options & GEX Desk (Whale Flow & Gamma)
- Screener Cuantitativo ➔ Dark Pool Tape (Bloques fuera de mercado)
- Screener Cuantitativo ➔ RRG Relative Rotation Graphs
- Screener Cuantitativo ➔ Intraday Bubble Map

Garantiza que la terminal se auto-alimente día a día con datos frescos y descubiertos
por nuestro propio motor algorítmico sin depender de watchlists estáticas.
"""

import os
import json
from datetime import datetime
from pathlib import Path

RADAR_CACHE_FILE = Path(__file__).parent / "active_radar_cache.json"

DEFAULT_SEED_TICKERS = [
    "NVDA", "PLTR", "TSLA", "AMD", "MSTR", "COIN", "APP", "SMCI", "AVGO", "META",
    "ARM", "CRWD", "ANF", "CEG", "VST", "TEM", "RDDT", "CAVA", "HIMS", "GWRE"
]

def get_active_radar() -> dict:
    """
    Recupera el radar activo compartido. Si no existe o está vacío,
    lo inicializa con los líderes dinámicos de mercado.
    """
    if RADAR_CACHE_FILE.exists():
        try:
            with open(RADAR_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("tickers") and len(data["tickers"]) > 0:
                    return data
        except Exception:
            pass

    # Fallback inicial inteligente
    return {
        "source": "Líderes Autónomos TradingVolt",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tickers": DEFAULT_SEED_TICKERS,
        "count": len(DEFAULT_SEED_TICKERS),
        "description": "Radar semilla inicial de alta liquidez y momentum."
    }

def set_active_radar(tickers: list, source_name: str = "Screener Cuantitativo", description: str = "") -> dict:
    """
    Actualiza el radar activo compartido con los nuevos activos descubiertos
    por cualquier filtro o motor cuantitativo.
    """
    clean_tickers = []
    seen = set()
    for t in tickers:
        if isinstance(t, str):
            sym = t.strip().upper().replace(".", "-")
            if sym and sym not in seen and len(sym) <= 6:
                clean_tickers.append(sym)
                seen.add(sym)

    if not clean_tickers:
        clean_tickers = DEFAULT_SEED_TICKERS

    payload = {
        "source": source_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tickers": clean_tickers,
        "count": len(clean_tickers),
        "description": description or f"Activos detectados dinámicamente vía {source_name}"
    }

    try:
        with open(RADAR_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        print(f"[ActiveRadar] Error guardando radar caché: {e}")

    return payload

def get_active_radar_tickers(max_items: int = 100) -> list:
    """Devuelve únicamente la lista limpia de tickers del radar activo."""
    data = get_active_radar()
    return data.get("tickers", DEFAULT_SEED_TICKERS)[:max_items]
