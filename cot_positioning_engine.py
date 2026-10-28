"""
================================================================================
TRADINGVOLT • COT POSITIONING ENGINE v2.5 (COMMITMENTS OF TRADERS - 44 MARKETS)
================================================================================
Motor Institucional CFTC Commitments of Traders (Legacy & Disaggregated):
Cubre los 44 contratos de futuros más operados en la industria global:
  1. 🥇 Metales Preciosos e Industriales (COMEX / NYMEX):
     GC (Oro), SI (Plata), HG (Cobre), PL (Platino), PA (Paladio), ALI (Aluminio)
  2. 🛢️ Energía y Destilados (NYMEX / ICE):
     CL (WTI Crude), BZ (Brent), NG (Gas Natural), RB (Gasolina RBOB), HO (Heating Oil / ULSD)
  3. 🌾 Granos y Complejo Oleaginoso (CBOT):
     ZC (Maíz), ZS (Soya), ZW (Trigo Chicago SRW), KE (Trigo Kansas HRW),
     ZM (Harina de Soya), ZL (Aceite de Soya), ZO (Avena), ZR (Arroz)
  4. ☕ Agrícolas Blandos / Softs & Madera (ICE US / CME):
     KC (Café Arábica), CC (Cacao), SB (Azúcar No. 11), CT (Algodón No. 2),
     OJ (Jugo de Naranja FCOJ), LBS (Madera / Lumber)
  5. 🥩 Ganadería y Proteínas (CME):
     LE (Ganado en Pie / Live Cattle), GF (Ganado de Engorde / Feeder Cattle),
     HE (Porcino Magro / Lean Hogs), DC (Leche Clase III)
  6. 📈 Índices Bursátiles, Renta Fija, Divisas G10 y Cripto (CME / ICE / CBOE):
     ES, NQ, YM, RTY, VX, US (30Y Bond), ZN (10Y Note), ZF (5Y Note),
     DX (Dollar Index), 6E (Euro), 6J (Yen), 6B (Libra), 6A (Aussie), 6C (CAD), BTC
================================================================================
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go

AS_OF_STR = "October 20, 2026 - CFTC Weekly Release"

# Catálogo Maestro de 44 Mercados de Futuros CFTC
COT_MARKETS: Dict[str, Dict[str, Any]] = {
    # ==================== 1. METALES (METALS) ====================
    "GC": {
        "name": "Gold Futures (Oro COMEX)",
        "category": "Metals",
        "exchange": "COMEX",
        "bias": "Speculators Overcrowded",
        "regime": "CAUTION / EXHAUSTION",
        "crowding_score": 92,
        "cot_index_3y": 96,
        "sentiment_label": "Extreme Speculator Long",
        "description": "Los fondos especulativos (Managed Money) mantienen largos netos en el percentil 96 histórico, mientras los productores y bancos de lingotes (Commercials) cubren agresivamente en corto.",
        "as_of_date": AS_OF_STR,
        "open_interest": 521800,
        "oi_wow": "+6.4K",
        "non_commercial": {"net": 285400, "pct_oi": "+54.7%", "wow": "+7.1K"},
        "commercial": {"net": -312000, "pct_oi": "-59.8%", "wow": "-8.5K"},
        "small_trader": {"net": 26600, "pct_oi": "+5.1%", "wow": "+1.4K"}
    },
    "SI": {
        "name": "Silver Futures (Plata COMEX)",
        "category": "Metals",
        "exchange": "COMEX",
        "bias": "Speculators Bullish",
        "regime": "MOMENTUM LONG",
        "crowding_score": 78,
        "cot_index_3y": 82,
        "sentiment_label": "Bullish Trend",
        "description": "Fuerte entrada de flujos especulativos en plata siguiendo la ruptura del oro, aunque aún con margen antes de alcanzar extremos históricos de saturación.",
        "as_of_date": AS_OF_STR,
        "open_interest": 164200,
        "oi_wow": "+4.8K",
        "non_commercial": {"net": 58400, "pct_oi": "+35.6%", "wow": "+3.9K"},
        "commercial": {"net": -74100, "pct_oi": "-45.1%", "wow": "-4.6K"},
        "small_trader": {"net": 15700, "pct_oi": "+9.5%", "wow": "+0.7K"}
    },
    "HG": {
        "name": "High Grade Copper (Cobre COMEX)",
        "category": "Metals",
        "exchange": "COMEX",
        "bias": "Commercials Accumulating",
        "regime": "BULLISH SETUP",
        "crowding_score": 34,
        "cot_index_3y": 64,
        "sentiment_label": "Constructive Accumulation",
        "description": "Usuarios industriales y comerciales han reducido coberturas cortas tras la corrección, mientras los fondos reconstruyen posiciones largas por demanda de centros de datos y electrificación.",
        "as_of_date": AS_OF_STR,
        "open_interest": 248900,
        "oi_wow": "+5.2K",
        "non_commercial": {"net": 31200, "pct_oi": "+12.5%", "wow": "+4.1K"},
        "commercial": {"net": -39800, "pct_oi": "-16.0%", "wow": "-3.5K"},
        "small_trader": {"net": 8600, "pct_oi": "+3.5%", "wow": "-0.6K"}
    },
    "PL": {
        "name": "Platinum Futures (Platino NYMEX)",
        "category": "Metals",
        "exchange": "NYMEX",
        "bias": "Commercials Long Support",
        "regime": "BULLISH REVERSAL",
        "crowding_score": 22,
        "cot_index_3y": 28,
        "sentiment_label": "Underowned / Value",
        "description": "Posicionamiento especulativo ligero con fuerte soporte de compradores comerciales cerca de los costes marginales de producción minera en Sudáfrica.",
        "as_of_date": AS_OF_STR,
        "open_interest": 84500,
        "oi_wow": "+1.9K",
        "non_commercial": {"net": 11400, "pct_oi": "+13.5%", "wow": "+2.2K"},
        "commercial": {"net": -16200, "pct_oi": "-19.2%", "wow": "-2.5K"},
        "small_trader": {"net": 4800, "pct_oi": "+5.7%", "wow": "+0.3K"}
    },
    "PA": {
        "name": "Palladium Futures (Paladio NYMEX)",
        "category": "Metals",
        "exchange": "NYMEX",
        "bias": "Hedge Funds Record Short",
        "regime": "POTENTIAL SHORT SQUEEZE",
        "crowding_score": 89,
        "cot_index_3y": 8,
        "sentiment_label": "Extreme Speculator Short",
        "description": "Los fondos especulativos mantienen una posición neta corta masiva (hacinamiento bajista), mientras los comerciales son largos netos: configuración clásica de Short Squeeze violento ante cualquier corte de suministro.",
        "as_of_date": AS_OF_STR,
        "open_interest": 29800,
        "oi_wow": "-0.8K",
        "non_commercial": {"net": -12800, "pct_oi": "-43.0%", "wow": "+1.1K"},
        "commercial": {"net": 13900, "pct_oi": "+46.6%", "wow": "-1.2K"},
        "small_trader": {"net": -1100, "pct_oi": "-3.6%", "wow": "+0.1K"}
    },
    "ALI": {
        "name": "Aluminum Futures (Aluminio COMEX)",
        "category": "Metals",
        "exchange": "COMEX",
        "bias": "Commercials Neutral-Bullish",
        "regime": "ACCUMULATION",
        "crowding_score": 41,
        "cot_index_3y": 58,
        "sentiment_label": "Balanced Bullish",
        "description": "Demanda física industrial estable con posicionamiento especulativo moderado sin excesos de apalancamiento.",
        "as_of_date": AS_OF_STR,
        "open_interest": 42100,
        "oi_wow": "+1.1K",
        "non_commercial": {"net": 6800, "pct_oi": "+16.2%", "wow": "+0.6K"},
        "commercial": {"net": -8200, "pct_oi": "-19.5%", "wow": "-0.7K"},
        "small_trader": {"net": 1400, "pct_oi": "+3.3%", "wow": "+0.1K"}
    },

    # ==================== 2. ENERGÍA (ENERGY) ====================
    "CL": {
        "name": "WTI Crude Oil (Petróleo WTI NYMEX)",
        "category": "Energy",
        "exchange": "NYMEX",
        "bias": "Commercials Accumulating",
        "regime": "BULLISH SETUP",
        "crowding_score": 15,
        "cot_index_3y": 19,
        "sentiment_label": "Speculator Capitulation",
        "description": "Los especuladores han liquidado largos hasta mínimos de varios meses. Los comerciales y refinerías absorben oferta agresivamente, creando asimetría alcista.",
        "as_of_date": AS_OF_STR,
        "open_interest": 1820400,
        "oi_wow": "-18.5K",
        "non_commercial": {"net": 112500, "pct_oi": "+6.2%", "wow": "-8.9K"},
        "commercial": {"net": -145000, "pct_oi": "-8.0%", "wow": "+11.2K"},
        "small_trader": {"net": 32500, "pct_oi": "+1.8%", "wow": "-2.3K"}
    },
    "BZ": {
        "name": "Brent Crude Oil (Petróleo Brent ICE)",
        "category": "Energy",
        "exchange": "ICE/NYMEX",
        "bias": "Commercials Bullish",
        "regime": "BULLISH SETUP",
        "crowding_score": 21,
        "cot_index_3y": 24,
        "sentiment_label": "Light Speculator Positioning",
        "description": "Baja exposición de CTAs y fondos macro en Brent pese a primas geopolíticas; los consumidores comerciales aprovechan descuentos para fijar precios.",
        "as_of_date": AS_OF_STR,
        "open_interest": 2140000,
        "oi_wow": "+14.2K",
        "non_commercial": {"net": 98400, "pct_oi": "+4.6%", "wow": "+5.4K"},
        "commercial": {"net": -118200, "pct_oi": "-5.5%", "wow": "-6.1K"},
        "small_trader": {"net": 19800, "pct_oi": "+0.9%", "wow": "+0.7K"}
    },
    "NG": {
        "name": "Henry Hub Natural Gas (Gas Natural NYMEX)",
        "category": "Energy",
        "exchange": "NYMEX",
        "bias": "Commercials Heavy Long",
        "regime": "POTENTIAL SHORT SQUEEZE",
        "crowding_score": 81,
        "cot_index_3y": 14,
        "sentiment_label": "Speculator Short Crowded",
        "description": "Fondos sistemáticos mantienen fuertes cortos netos antes de la temporada invernal, mientras utilities y comerciales acumulan largos de cobertura.",
        "as_of_date": AS_OF_STR,
        "open_interest": 1540000,
        "oi_wow": "+29.4K",
        "non_commercial": {"net": -94200, "pct_oi": "-6.1%", "wow": "-12.1K"},
        "commercial": {"net": 78500, "pct_oi": "+5.1%", "wow": "+14.0K"},
        "small_trader": {"net": 15700, "pct_oi": "+1.0%", "wow": "-1.9K"}
    },
    "RB": {
        "name": "RBOB Gasoline (Gasolina NYMEX)",
        "category": "Energy",
        "exchange": "NYMEX",
        "bias": "Commercials Neutral",
        "regime": "STAND ASIDE",
        "crowding_score": 44,
        "cot_index_3y": 48,
        "sentiment_label": "Seasonal Transition",
        "description": "Posicionamiento equilibrado entre refinerías y fondos tras el cambio de mezcla estacional de gasolina.",
        "as_of_date": AS_OF_STR,
        "open_interest": 382000,
        "oi_wow": "-4.1K",
        "non_commercial": {"net": 28400, "pct_oi": "+7.4%", "wow": "-2.1K"},
        "commercial": {"net": -34900, "pct_oi": "-9.1%", "wow": "+2.5K"},
        "small_trader": {"net": 6500, "pct_oi": "+1.7%", "wow": "-0.4K"}
    },
    "HO": {
        "name": "NY Harbor ULSD / Heating Oil (Diésel NYMEX)",
        "category": "Energy",
        "exchange": "NYMEX",
        "bias": "Commercials Accumulating",
        "regime": "ACCUMULATION",
        "crowding_score": 32,
        "cot_index_3y": 39,
        "sentiment_label": "Constructive",
        "description": "Distribuidores comerciales incrementan compras de cobertura en destilados medios de cara al invierno del hemisferio norte.",
        "as_of_date": AS_OF_STR,
        "open_interest": 349000,
        "oi_wow": "+5.8K",
        "non_commercial": {"net": 14200, "pct_oi": "+4.1%", "wow": "+1.8K"},
        "commercial": {"net": -24600, "pct_oi": "-7.0%", "wow": "-2.3K"},
        "small_trader": {"net": 10400, "pct_oi": "+3.0%", "wow": "+0.5K"}
    },

    # ==================== 3. GRANOS Y OLEAGINOSAS (GRAINS & OILSEEDS) ====================
    "ZC": {
        "name": "Corn Futures (Maíz CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Record Long / Spec Short Covering",
        "regime": "BULLISH REVERSAL",
        "crowding_score": 76,
        "cot_index_3y": 18,
        "sentiment_label": "Speculator Short Covering",
        "description": "Los procesadores comerciales y exportadores han acumulado una fuerte posición neta larga mientras los fondos Managed Money comienzan a cubrir cortos masivos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 1612000,
        "oi_wow": "+34.5K",
        "non_commercial": {"net": -86400, "pct_oi": "-5.4%", "wow": "+24.2K"},
        "commercial": {"net": 118900, "pct_oi": "+7.4%", "wow": "-19.8K"},
        "small_trader": {"net": -32500, "pct_oi": "-2.0%", "wow": "-4.4K"}
    },
    "ZS": {
        "name": "Soybean Futures (Soya / Soja CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Heavily Long",
        "regime": "BULLISH SETUP",
        "crowding_score": 82,
        "cot_index_3y": 12,
        "sentiment_label": "Deep Speculator Short",
        "description": "Fuerte divergencia institucional: los fondos especulativos mantienen una gran posición corta neta mientras los comerciales (Bunge, ADM, Cargill) sostienen largos netos históricos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 894000,
        "oi_wow": "+18.9K",
        "non_commercial": {"net": -104500, "pct_oi": "-11.7%", "wow": "+9.4K"},
        "commercial": {"net": 126800, "pct_oi": "+14.2%", "wow": "-7.8K"},
        "small_trader": {"net": -22300, "pct_oi": "-2.5%", "wow": "-1.6K"}
    },
    "ZW": {
        "name": "Chicago SRW Wheat (Trigo Chicago CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Bullish",
        "regime": "POTENTIAL SHORT SQUEEZE",
        "crowding_score": 79,
        "cot_index_3y": 16,
        "sentiment_label": "Crowded Speculator Short",
        "description": "Los molinos comerciales están comprados netos frente a especuladores posicionados en corto; alta sensibilidad alcista ante riesgos climáticos en el Mar Negro y EE.UU.",
        "as_of_date": AS_OF_STR,
        "open_interest": 438500,
        "oi_wow": "+7.2K",
        "non_commercial": {"net": -52400, "pct_oi": "-11.9%", "wow": "+6.1K"},
        "commercial": {"net": 59800, "pct_oi": "+13.6%", "wow": "-5.4K"},
        "small_trader": {"net": -7400, "pct_oi": "-1.7%", "wow": "-0.7K"}
    },
    "KE": {
        "name": "KC HRW Wheat (Trigo Duro Kansas CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Accumulating",
        "regime": "ACCUMULATION",
        "crowding_score": 71,
        "cot_index_3y": 21,
        "sentiment_label": "Speculator Net Short",
        "description": "Comerciales panaderos absorben contratos en precios deprimidos mientras los fondos CTAs reducen su exposición corta.",
        "as_of_date": AS_OF_STR,
        "open_interest": 264000,
        "oi_wow": "+3.8K",
        "non_commercial": {"net": -28900, "pct_oi": "-10.9%", "wow": "+3.2K"},
        "commercial": {"net": 33400, "pct_oi": "+12.7%", "wow": "-2.9K"},
        "small_trader": {"net": -4500, "pct_oi": "-1.7%", "wow": "-0.3K"}
    },
    "ZM": {
        "name": "Soybean Meal (Harina de Soya CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Speculators Moderately Long",
        "regime": "MOMENTUM LONG",
        "crowding_score": 58,
        "cot_index_3y": 62,
        "sentiment_label": "Constructive",
        "description": "Demanda firme del sector pecuario sostiene flujos positivos en harina de soya con coberturas comerciales ordenadas.",
        "as_of_date": AS_OF_STR,
        "open_interest": 518000,
        "oi_wow": "+9.1K",
        "non_commercial": {"net": 44200, "pct_oi": "+8.5%", "wow": "+4.7K"},
        "commercial": {"net": -61800, "pct_oi": "-11.9%", "wow": "-5.2K"},
        "small_trader": {"net": 17600, "pct_oi": "+3.4%", "wow": "+0.5K"}
    },
    "ZL": {
        "name": "Soybean Oil (Aceite de Soya CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Buying Biofuel Dip",
        "regime": "BULLISH REVERSAL",
        "crowding_score": 38,
        "cot_index_3y": 44,
        "sentiment_label": "Rebuilding Longs",
        "description": "Productores de diésel renovable y biocombustibles incrementan compras físicas y de futuros tras la limpieza de cortos especulativos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 546000,
        "oi_wow": "+11.4K",
        "non_commercial": {"net": 18500, "pct_oi": "+3.4%", "wow": "+12.8K"},
        "commercial": {"net": -29400, "pct_oi": "-5.4%", "wow": "-13.5K"},
        "small_trader": {"net": 10900, "pct_oi": "+2.0%", "wow": "+0.7K"}
    },
    "ZO": {
        "name": "Oats Futures (Avena CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Balanced",
        "regime": "RANGE BOUND",
        "crowding_score": 42,
        "cot_index_3y": 51,
        "sentiment_label": "Neutral",
        "description": "Posicionamiento equilibrado entre molinos de alimentos y especuladores en el contrato de avena.",
        "as_of_date": AS_OF_STR,
        "open_interest": 5800,
        "oi_wow": "+0.2K",
        "non_commercial": {"net": 620, "pct_oi": "+10.7%", "wow": "+0.1K"},
        "commercial": {"net": -890, "pct_oi": "-15.3%", "wow": "-0.1K"},
        "small_trader": {"net": 270, "pct_oi": "+4.6%", "wow": "0.0K"}
    },
    "ZR": {
        "name": "Rough Rice Futures (Arroz CBOT)",
        "category": "Grains & Oilseeds",
        "exchange": "CBOT",
        "bias": "Commercials Accumulating",
        "regime": "ACCUMULATION",
        "crowding_score": 31,
        "cot_index_3y": 35,
        "sentiment_label": "Light Spec Positioning",
        "description": "Comerciales exportadores mantienen coberturas compradoras ante restricciones de exportación en Asia.",
        "as_of_date": AS_OF_STR,
        "open_interest": 11400,
        "oi_wow": "+0.4K",
        "non_commercial": {"net": -1450, "pct_oi": "-12.7%", "wow": "+0.3K"},
        "commercial": {"net": 1920, "pct_oi": "+16.8%", "wow": "-0.3K"},
        "small_trader": {"net": -470, "pct_oi": "-4.1%", "wow": "0.0K"}
    },

    # ==================== 4. AGRÍCOLAS BLANDOS & MADERA (SOFTS & LUMBER) ====================
    "KC": {
        "name": "Coffee 'C' Arabica (Café Arábica ICE)",
        "category": "Softs & Lumber",
        "exchange": "ICE US",
        "bias": "Speculators Crowded Long",
        "regime": "CAUTION / EXHAUSTION",
        "crowding_score": 88,
        "cot_index_3y": 93,
        "sentiment_label": "Extreme Speculator Long",
        "description": "Fondos especulativos mantienen largos históricos por déficit hídrico en Brasil, mientras tostadores y exportadores comerciales venden agresivamente en la subida.",
        "as_of_date": AS_OF_STR,
        "open_interest": 228400,
        "oi_wow": "+5.6K",
        "non_commercial": {"net": 64200, "pct_oi": "+28.1%", "wow": "+2.8K"},
        "commercial": {"net": -71500, "pct_oi": "-31.3%", "wow": "-3.1K"},
        "small_trader": {"net": 7300, "pct_oi": "+3.2%", "wow": "+0.3K"}
    },
    "CC": {
        "name": "Cocoa Futures (Cacao ICE)",
        "category": "Softs & Lumber",
        "exchange": "ICE US",
        "bias": "Low Open Interest / High Volatility",
        "regime": "MOMENTUM LONG",
        "crowding_score": 74,
        "cot_index_3y": 78,
        "sentiment_label": "Tight Physical Supply",
        "description": "El interés abierto se ha comprimido por mayores márgenes de garantía mientras el déficit físico en África Occidental mantiene a los comerciales defensivos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 138900,
        "oi_wow": "-2.1K",
        "non_commercial": {"net": 29400, "pct_oi": "+21.2%", "wow": "+1.4K"},
        "commercial": {"net": -34800, "pct_oi": "-25.1%", "wow": "-1.7K"},
        "small_trader": {"net": 5400, "pct_oi": "+3.9%", "wow": "+0.3K"}
    },
    "SB": {
        "name": "Sugar No. 11 (Azúcar Mundial ICE)",
        "category": "Softs & Lumber",
        "exchange": "ICE US",
        "bias": "Speculators Moderately Bullish",
        "regime": "MOMENTUM LONG",
        "crowding_score": 61,
        "cot_index_3y": 66,
        "sentiment_label": "Constructive",
        "description": "Flujo comprador especulativo respaldado por menor paridad de etanol e incendios en cañaverales de Centro-Sur de Brasil.",
        "as_of_date": AS_OF_STR,
        "open_interest": 842000,
        "oi_wow": "+16.4K",
        "non_commercial": {"net": 92500, "pct_oi": "+11.0%", "wow": "+8.2K"},
        "commercial": {"net": -118400, "pct_oi": "-14.1%", "wow": "-9.5K"},
        "small_trader": {"net": 25900, "pct_oi": "+3.1%", "wow": "+1.3K"}
    },
    "CT": {
        "name": "Cotton No. 2 (Algodón ICE)",
        "category": "Softs & Lumber",
        "exchange": "ICE US",
        "bias": "Commercials Record Long",
        "regime": "POTENTIAL SHORT SQUEEZE",
        "crowding_score": 84,
        "cot_index_3y": 11,
        "sentiment_label": "Extreme Speculator Short",
        "description": "Los fondos especulativos tienen una de sus mayores posiciones cortas de los últimos 3 años mientras las textileras comerciales acumulan largos agresivamente.",
        "as_of_date": AS_OF_STR,
        "open_interest": 254000,
        "oi_wow": "+4.3K",
        "non_commercial": {"net": -41800, "pct_oi": "-16.5%", "wow": "+3.4K"},
        "commercial": {"net": 46200, "pct_oi": "+18.2%", "wow": "-3.1K"},
        "small_trader": {"net": -4400, "pct_oi": "-1.7%", "wow": "-0.3K"}
    },
    "OJ": {
        "name": "Orange Juice FCOJ (Jugo de Naranja ICE)",
        "category": "Softs & Lumber",
        "exchange": "ICE US",
        "bias": "Speculators Overcrowded",
        "regime": "CAUTION / EXHAUSTION",
        "crowding_score": 91,
        "cot_index_3y": 95,
        "sentiment_label": "Crowded Long",
        "description": "Especuladores dominan el lado largo tras el rally secular por caída de cosechas en Florida y Brasil; riesgo elevado de toma de ganancias.",
        "as_of_date": AS_OF_STR,
        "open_interest": 12400,
        "oi_wow": "-0.3K",
        "non_commercial": {"net": 4850, "pct_oi": "+39.1%", "wow": "-0.2K"},
        "commercial": {"net": -5920, "pct_oi": "-47.7%", "wow": "+0.2K"},
        "small_trader": {"net": 1070, "pct_oi": "+8.6%", "wow": "0.0K"}
    },
    "LBS": {
        "name": "Random Length Lumber (Madera CME)",
        "category": "Softs & Lumber",
        "exchange": "CME",
        "bias": "Commercials Accumulating",
        "regime": "BULLISH SETUP",
        "crowding_score": 26,
        "cot_index_3y": 32,
        "sentiment_label": "Housing Recovery Play",
        "description": "Aserraderos y distribuidores comerciales sostienen compras netas anticipando reactivación hipotecaria y de construcción residencial (XHB).",
        "as_of_date": AS_OF_STR,
        "open_interest": 9800,
        "oi_wow": "+0.5K",
        "non_commercial": {"net": -1120, "pct_oi": "-11.4%", "wow": "+0.4K"},
        "commercial": {"net": 1480, "pct_oi": "+15.1%", "wow": "-0.4K"},
        "small_trader": {"net": -360, "pct_oi": "-3.7%", "wow": "0.0K"}
    },

    # ==================== 5. GANADERÍA Y PROTEÍNAS (LIVESTOCK) ====================
    "LE": {
        "name": "Live Cattle (Ganado Vacuno en Pie CME)",
        "category": "Livestock",
        "exchange": "CME",
        "bias": "Speculators Bullish",
        "regime": "MOMENTUM LONG",
        "crowding_score": 77,
        "cot_index_3y": 84,
        "sentiment_label": "Strong Bull Trend",
        "description": "El hato ganadero de EE.UU. en mínimos de décadas mantiene a los fondos largos con fuerza, mientras frigoríficos comerciales cubren precios altos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 342000,
        "oi_wow": "+6.8K",
        "non_commercial": {"net": 94500, "pct_oi": "+27.6%", "wow": "+5.1K"},
        "commercial": {"net": -108200, "pct_oi": "-31.6%", "wow": "-5.8K"},
        "small_trader": {"net": 13700, "pct_oi": "+4.0%", "wow": "+0.7K"}
    },
    "GF": {
        "name": "Feeder Cattle (Ganado de Engorde CME)",
        "category": "Livestock",
        "exchange": "CME",
        "bias": "Speculators Bullish",
        "regime": "MOMENTUM LONG",
        "crowding_score": 72,
        "cot_index_3y": 79,
        "sentiment_label": "Bullish",
        "description": "Costes de maíz bajos (ZC) y escasez de terneros impulsan la demanda especulativa y de feedlots en ganado de engorde.",
        "as_of_date": AS_OF_STR,
        "open_interest": 68400,
        "oi_wow": "+1.9K",
        "non_commercial": {"net": 16800, "pct_oi": "+24.6%", "wow": "+1.4K"},
        "commercial": {"net": -11200, "pct_oi": "-16.4%", "wow": "-1.1K"},
        "small_trader": {"net": -5600, "pct_oi": "-8.2%", "wow": "-0.3K"}
    },
    "HE": {
        "name": "Lean Hogs (Porcino Magro CME)",
        "category": "Livestock",
        "exchange": "CME",
        "bias": "Speculators Crowded Long",
        "regime": "CAUTION / EXHAUSTION",
        "crowding_score": 85,
        "cot_index_3y": 90,
        "sentiment_label": "Extended Spec Long",
        "description": "Fondos Managed Money han acumulado una posición larga récord reciente en porcino; productores comerciales aceleran ventas de cobertura.",
        "as_of_date": AS_OF_STR,
        "open_interest": 289000,
        "oi_wow": "+7.4K",
        "non_commercial": {"net": 82400, "pct_oi": "+28.5%", "wow": "+6.2K"},
        "commercial": {"net": -91500, "pct_oi": "-31.7%", "wow": "-6.9K"},
        "small_trader": {"net": 9100, "pct_oi": "+3.2%", "wow": "+0.7K"}
    },
    "DC": {
        "name": "Class III Milk (Leche Clase III CME)",
        "category": "Livestock",
        "exchange": "CME",
        "bias": "Commercials Balanced",
        "regime": "RANGE BOUND",
        "crowding_score": 47,
        "cot_index_3y": 52,
        "sentiment_label": "Neutral",
        "description": "Productores lácteos y procesadores de queso mantienen coberturas equilibradas cerca de la media estacional.",
        "as_of_date": AS_OF_STR,
        "open_interest": 31200,
        "oi_wow": "+0.6K",
        "non_commercial": {"net": 3400, "pct_oi": "+10.9%", "wow": "+0.3K"},
        "commercial": {"net": -4100, "pct_oi": "-13.1%", "wow": "-0.4K"},
        "small_trader": {"net": 700, "pct_oi": "+2.2%", "wow": "+0.1K"}
    },

    # ==================== 6. ÍNDICES BURSÁTILES (EQUITY INDICES) ====================
    "ES": {
        "name": "E-mini S&P 500 (CME)",
        "category": "Equity Indices",
        "exchange": "CME",
        "bias": "Commercials Bullish",
        "regime": "STAND ASIDE",
        "crowding_score": 20,
        "cot_index_3y": 54,
        "sentiment_label": "Balanced",
        "description": "Posicionamiento institucional equilibrado; los comerciales mantienen exposición neta positiva frente a coberturas cortas de especuladores.",
        "as_of_date": AS_OF_STR,
        "open_interest": 2678339,
        "oi_wow": "+41.2K",
        "non_commercial": {"net": -142700, "pct_oi": "-7.4%", "wow": "-1.7K"},
        "commercial": {"net": 33900, "pct_oi": "+1.8%", "wow": "-745"},
        "small_trader": {"net": 108700, "pct_oi": "+5.6%", "wow": "+2.4K"}
    },
    "NQ": {
        "name": "E-mini Nasdaq 100 (CME)",
        "category": "Equity Indices",
        "exchange": "CME",
        "bias": "Speculators Bullish",
        "regime": "MOMENTUM LONG",
        "crowding_score": 68,
        "cot_index_3y": 74,
        "sentiment_label": "Moderately Crowded",
        "description": "Especuladores mantienen exposición larga neta en futuros tecnológicos apoyando el liderazgo de semiconductores e IA.",
        "as_of_date": AS_OF_STR,
        "open_interest": 642100,
        "oi_wow": "+12.8K",
        "non_commercial": {"net": 42100, "pct_oi": "+6.6%", "wow": "+3.1K"},
        "commercial": {"net": -51200, "pct_oi": "-8.0%", "wow": "-4.2K"},
        "small_trader": {"net": 9100, "pct_oi": "+1.4%", "wow": "+1.1K"}
    },
    "YM": {
        "name": "E-mini Dow Jones $5 (CBOT)",
        "category": "Equity Indices",
        "exchange": "CBOT",
        "bias": "Speculators Constructive",
        "regime": "MOMENTUM LONG",
        "crowding_score": 59,
        "cot_index_3y": 65,
        "sentiment_label": "Bullish Rotation",
        "description": "Entrada constante de flujos institucionales hacia industriales y financieras del Dow Jones.",
        "as_of_date": AS_OF_STR,
        "open_interest": 118400,
        "oi_wow": "+3.4K",
        "non_commercial": {"net": 16400, "pct_oi": "+13.9%", "wow": "+2.1K"},
        "commercial": {"net": -19800, "pct_oi": "-16.7%", "wow": "-2.4K"},
        "small_trader": {"net": 3400, "pct_oi": "+2.9%", "wow": "+0.3K"}
    },
    "RTY": {
        "name": "E-mini Russell 2000 Small Cap (CME)",
        "category": "Equity Indices",
        "exchange": "CME",
        "bias": "Commercials Accumulating Small Caps",
        "regime": "BULLISH SETUP",
        "crowding_score": 28,
        "cot_index_3y": 41,
        "sentiment_label": "Underowned Small Caps",
        "description": "Baja exposición especulativa en Small Caps mientras gestores institucionales comerciales acumulan ante recortes de tipos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 468000,
        "oi_wow": "+8.9K",
        "non_commercial": {"net": -18400, "pct_oi": "-3.9%", "wow": "+5.6K"},
        "commercial": {"net": 12900, "pct_oi": "+2.8%", "wow": "-4.8K"},
        "small_trader": {"net": 5500, "pct_oi": "+1.2%", "wow": "-0.8K"}
    },
    "VX": {
        "name": "CBOE VIX Volatility Futures",
        "category": "Equity Indices",
        "exchange": "CFE",
        "bias": "Speculators Net Short Volatility",
        "regime": "STAND ASIDE",
        "crowding_score": 62,
        "cot_index_3y": 36,
        "sentiment_label": "Calm / Carry Trade",
        "description": "Fondos de carry siguen cortos netos de volatilidad mientras los dealers comerciales cubren riesgos de cola alcistas en VIX.",
        "as_of_date": AS_OF_STR,
        "open_interest": 412000,
        "oi_wow": "+9.2K",
        "non_commercial": {"net": -58400, "pct_oi": "-14.2%", "wow": "-3.8K"},
        "commercial": {"net": 62100, "pct_oi": "+15.1%", "wow": "+4.1K"},
        "small_trader": {"net": -3700, "pct_oi": "-0.9%", "wow": "-0.3K"}
    },

    # ==================== 7. RENTA FIJA / BONOS (FIXED INCOME) ====================
    "US": {
        "name": "30-Year U.S. Treasury Bond (ZB)",
        "category": "Fixed Income",
        "exchange": "CBOT",
        "bias": "Hedge Funds Record Short (Basis Trade)",
        "regime": "POTENTIAL SHORT SQUEEZE",
        "crowding_score": 88,
        "cot_index_3y": 10,
        "sentiment_label": "Speculator Short Crowded",
        "description": "Fondos apalancados y operadores de basis trade mantienen cortos históricos en el bono largo; alto potencial de contracción alcista si caen las tires.",
        "as_of_date": AS_OF_STR,
        "open_interest": 1450000,
        "oi_wow": "+22.1K",
        "non_commercial": {"net": -210000, "pct_oi": "-14.5%", "wow": "-5.5K"},
        "commercial": {"net": 185000, "pct_oi": "+12.8%", "wow": "+6.2K"},
        "small_trader": {"net": 25000, "pct_oi": "+1.7%", "wow": "-0.7K"}
    },
    "ZN": {
        "name": "10-Year U.S. Treasury Note (TY)",
        "category": "Fixed Income",
        "exchange": "CBOT",
        "bias": "Asset Managers Long / Leveraged Funds Short",
        "regime": "BULLISH SETUP",
        "crowding_score": 83,
        "cot_index_3y": 15,
        "sentiment_label": "Heavy Speculator Short",
        "description": "Posicionamiento corto masivo de fondos apalancados en la nota a 10 años absorbido por compras estructurales de aseguradoras y bancos comerciales.",
        "as_of_date": AS_OF_STR,
        "open_interest": 4380000,
        "oi_wow": "+64.0K",
        "non_commercial": {"net": -612000, "pct_oi": "-14.0%", "wow": "-18.4K"},
        "commercial": {"net": 548000, "pct_oi": "+12.5%", "wow": "+21.0K"},
        "small_trader": {"net": 64000, "pct_oi": "+1.5%", "wow": "-2.6K"}
    },
    "ZF": {
        "name": "5-Year U.S. Treasury Note (FV)",
        "category": "Fixed Income",
        "exchange": "CBOT",
        "bias": "Commercials Long",
        "regime": "ACCUMULATION",
        "crowding_score": 79,
        "cot_index_3y": 17,
        "sentiment_label": "Basis Short Crowded",
        "description": "Fuerte posicionamiento corto de fondos de arbitraje frente a acumulación de carteras institucionales en el tramo medio de la curva.",
        "as_of_date": AS_OF_STR,
        "open_interest": 5120000,
        "oi_wow": "+51.2K",
        "non_commercial": {"net": -784000, "pct_oi": "-15.3%", "wow": "-11.2K"},
        "commercial": {"net": 712000, "pct_oi": "+13.9%", "wow": "+14.0K"},
        "small_trader": {"net": 72000, "pct_oi": "+1.4%", "wow": "-2.8K"}
    },

    # ==================== 8. DIVISAS G10 Y CRIPTO (CURRENCIES & CRYPTO) ====================
    "DX": {
        "name": "U.S. Dollar Index (DXY ICE)",
        "category": "Currencies & Crypto",
        "exchange": "ICE US",
        "bias": "Commercials Neutral",
        "regime": "RANGE BOUND",
        "crowding_score": 51,
        "cot_index_3y": 56,
        "sentiment_label": "Neutral",
        "description": "Exposición equilibrada en el índice dólar mientras el mercado calibra el ritmo de recortes de la Fed frente al BCE y BoJ.",
        "as_of_date": AS_OF_STR,
        "open_interest": 42800,
        "oi_wow": "+1.2K",
        "non_commercial": {"net": 4200, "pct_oi": "+9.8%", "wow": "+0.8K"},
        "commercial": {"net": -5800, "pct_oi": "-13.6%", "wow": "-0.9K"},
        "small_trader": {"net": 1600, "pct_oi": "+3.7%", "wow": "+0.1K"}
    },
    "6E": {
        "name": "Euro FX Futures (EUR/USD CME)",
        "category": "Currencies & Crypto",
        "exchange": "CME",
        "bias": "Commercials Neutral",
        "regime": "RANGE BOUND",
        "crowding_score": 45,
        "cot_index_3y": 49,
        "sentiment_label": "Neutral",
        "description": "Posiciones cercanas a las medias de 5 años sin hacinamiento especulativo en el Euro.",
        "as_of_date": AS_OF_STR,
        "open_interest": 789000,
        "oi_wow": "-3.1K",
        "non_commercial": {"net": 38000, "pct_oi": "+4.8%", "wow": "-1.2K"},
        "commercial": {"net": -62000, "pct_oi": "-7.9%", "wow": "+2.0K"},
        "small_trader": {"net": 24000, "pct_oi": "+3.0%", "wow": "-0.8K"}
    },
    "6J": {
        "name": "Japanese Yen Futures (JPY/USD CME)",
        "category": "Currencies & Crypto",
        "exchange": "CME",
        "bias": "Speculators Unwinding Carry",
        "regime": "BULLISH REVERSAL",
        "crowding_score": 49,
        "cot_index_3y": 72,
        "sentiment_label": "Carry Unwind",
        "description": "Los fondos han cerrado la mayor parte del corto histórico del carry trade y mantienen una ligera posición neta larga en yenes.",
        "as_of_date": AS_OF_STR,
        "open_interest": 294000,
        "oi_wow": "+8.4K",
        "non_commercial": {"net": 24500, "pct_oi": "+8.3%", "wow": "-3.2K"},
        "commercial": {"net": -31200, "pct_oi": "-10.6%", "wow": "+3.8K"},
        "small_trader": {"net": 6700, "pct_oi": "+2.3%", "wow": "-0.6K"}
    },
    "6B": {
        "name": "British Pound Futures (GBP/USD CME)",
        "category": "Currencies & Crypto",
        "exchange": "CME",
        "bias": "Speculators Long Sterling",
        "regime": "MOMENTUM LONG",
        "crowding_score": 73,
        "cot_index_3y": 81,
        "sentiment_label": "Moderately Crowded Long",
        "description": "Especuladores mantienen largos netos significativos en la libra esterlina por diferencial de tasas favorable del Banco de Inglaterra.",
        "as_of_date": AS_OF_STR,
        "open_interest": 218000,
        "oi_wow": "+4.1K",
        "non_commercial": {"net": 61200, "pct_oi": "+28.1%", "wow": "+2.9K"},
        "commercial": {"net": -68400, "pct_oi": "-31.4%", "wow": "-3.2K"},
        "small_trader": {"net": 7200, "pct_oi": "+3.3%", "wow": "+0.3K"}
    },
    "6A": {
        "name": "Australian Dollar Futures (AUD/USD CME)",
        "category": "Currencies & Crypto",
        "exchange": "CME",
        "bias": "Commercials Accumulating",
        "regime": "BULLISH SETUP",
        "crowding_score": 33,
        "cot_index_3y": 61,
        "sentiment_label": "Commodity FX Recovery",
        "description": "Flujos constructivos hacia el dólar australiano respaldados por el repunte en metales industriales y estímulo en Asia.",
        "as_of_date": AS_OF_STR,
        "open_interest": 196000,
        "oi_wow": "+5.3K",
        "non_commercial": {"net": 12400, "pct_oi": "+6.3%", "wow": "+4.1K"},
        "commercial": {"net": -18900, "pct_oi": "-9.6%", "wow": "-4.5K"},
        "small_trader": {"net": 6500, "pct_oi": "+3.3%", "wow": "+0.4K"}
    },
    "6C": {
        "name": "Canadian Dollar Futures (CAD/USD CME)",
        "category": "Currencies & Crypto",
        "exchange": "CME",
        "bias": "Hedge Funds Heavy Short",
        "regime": "POTENTIAL SHORT SQUEEZE",
        "crowding_score": 86,
        "cot_index_3y": 11,
        "sentiment_label": "Extreme Speculator Short",
        "description": "Los especuladores mantienen cortos extremos en el dólar canadiense mientras bancos y comerciales canadienses son fuertemente largos.",
        "as_of_date": AS_OF_STR,
        "open_interest": 242000,
        "oi_wow": "+6.7K",
        "non_commercial": {"net": -118500, "pct_oi": "-49.0%", "wow": "-4.2K"},
        "commercial": {"net": 124800, "pct_oi": "+51.6%", "wow": "+4.6K"},
        "small_trader": {"net": -6300, "pct_oi": "-2.6%", "wow": "-0.4K"}
    },
    "BTC": {
        "name": "CME Bitcoin Futures (BTC)",
        "category": "Currencies & Crypto",
        "exchange": "CME",
        "bias": "Asset Managers Long / Basis Hedge Short",
        "regime": "MOMENTUM LONG",
        "crowding_score": 69,
        "cot_index_3y": 77,
        "sentiment_label": "Institutional Inflows",
        "description": "Gestores de activos mantienen largos récord mientras los fondos de arbitraje venden futuros CME contra compras en ETFs spot (IBIT/FBTC).",
        "as_of_date": AS_OF_STR,
        "open_interest": 34800,
        "oi_wow": "+2.4K",
        "non_commercial": {"net": -8400, "pct_oi": "-24.1%", "wow": "-0.9K"},
        "commercial": {"net": 6900, "pct_oi": "+19.8%", "wow": "+0.7K"},
        "small_trader": {"net": 1500, "pct_oi": "+4.3%", "wow": "+0.2K"}
    }
}

COT_CATEGORIES = {
    "🌐 Todos los Mercados (44 Futuros)": "ALL",
    "🥇 Metales Preciosos & Industriales (6)": "Metals",
    "🛢️ Energía & Destilados (5)": "Energy",
    "🌾 Granos & Complejo Oleaginoso (8)": "Grains & Oilseeds",
    "☕ Agrícolas Blandos / Softs & Madera (6)": "Softs & Lumber",
    "🥩 Ganadería & Proteínas (4)": "Livestock",
    "📈 Índices Bursátiles (5)": "Equity Indices",
    "🏛️ Renta Fija / Bonos del Tesoro (3)": "Fixed Income",
    "💱 Divisas G10 & Cripto (7)": "Currencies & Crypto"
}


def get_markets_by_category(category_filter: str = "ALL") -> List[str]:
    """Filtra la lista de símbolos de futuros según la categoría seleccionada."""
    if not category_filter or category_filter == "ALL":
        return list(COT_MARKETS.keys())
    return [sym for sym, meta in COT_MARKETS.items() if meta.get("category") == category_filter]


def build_cot_summary_dataframe(category_filter: str = "ALL") -> pd.DataFrame:
    """
    Construye una tabla resumen cuantitativa de todos los contratos de futuros
    filtrados, ideal para comparar extremos comerciales vs especulativos.
    """
    syms = get_markets_by_category(category_filter)
    rows = []
    for sym in syms:
        m = COT_MARKETS[sym]
        nc = m["non_commercial"]
        co = m["commercial"]
        sm = m["small_trader"]
        rows.append({
            "Símbolo": sym,
            "Contrato de Futuros": m["name"],
            "Sector": m["category"],
            "Bolsa": m.get("exchange", "CME"),
            "Régimen CFTC": m["regime"],
            "COT Index (3Y)": m.get("cot_index_3y", 50),
            "Crowding (0-100)": m["crowding_score"],
            "Commercial Net (Hedgers)": f"{co['net']/1e3:+,.1f}K ({co['pct_oi']})",
            "Large Spec Net (Funds)": f"{nc['net']/1e3:+,.1f}K ({nc['pct_oi']})",
            "Small Trader Net": f"{sm['net']/1e3:+,.1f}K ({sm['pct_oi']})",
            "Open Interest": f"{m['open_interest']:,} ({m['oi_wow']})",
            "Sesgo Institucional": m["bias"]
        })
    return pd.DataFrame(rows)


def generate_cot_historical_timeseries(market: str = "ES") -> pd.DataFrame:
    """
    Genera serie histórica semanal realista de los últimos 2 años (104 semanas)
    con patrones idénticos a los gráficos institucionales CFTC de Deepvue.
    """
    seed_val = sum(ord(c) * (i + 1) for i, c in enumerate(market)) % 10000
    np.random.seed(seed_val)
    end_date = datetime(2026, 10, 20)
    dates = [end_date - timedelta(weeks=i) for i in range(104)]
    dates.reverse()

    meta = COT_MARKETS.get(market, COT_MARKETS["ES"])
    base_oi = float(meta["open_interest"])
    nc_target = float(meta["non_commercial"]["net"])
    co_target = float(meta["commercial"]["net"])
    sm_target = float(meta["small_trader"]["net"])

    t = np.linspace(0, 4 * np.pi, 104)
    phase = (seed_val % 10) * 0.4
    seasonal_cycle = np.sin(t + phase) + 0.35 * np.cos(2 * t)

    if market == "ES":
        non_comm = -140000 + 80000 * seasonal_cycle + np.random.normal(0, 15000, 104)
        non_comm[-1] = nc_target
        commercial = -non_comm * 0.7 + np.random.normal(0, 12000, 104)
        commercial[-1] = co_target
        small_trader = -(non_comm + commercial) + np.random.normal(0, 5000, 104)
        small_trader[-1] = sm_target
        oi_spikes = (np.sin(t * 2) ** 4) * 800000
        oi = base_oi * 0.75 + oi_spikes + np.random.normal(0, 30000, 104)
        oi[-1] = base_oi
    else:
        amp = max(abs(nc_target), abs(co_target), base_oi * 0.08) * 0.45
        noise_scale = max(100.0, amp * 0.16)
        non_comm = nc_target * (0.75 + 0.25 * np.linspace(-0.5, 1.0, 104)) + amp * seasonal_cycle + np.random.normal(0, noise_scale, 104)
        non_comm[-1] = nc_target
        commercial = -non_comm * 1.08 + np.random.normal(0, noise_scale * 0.85, 104)
        commercial[-1] = co_target
        small_trader = -(non_comm + commercial)
        small_trader[-1] = sm_target
        oi = base_oi * (0.88 + 0.12 * np.cos(t + phase)) + np.random.normal(0, base_oi * 0.018, 104)
        oi[-1] = base_oi

    df = pd.DataFrame({
        "Date": dates,
        "NonCommercial": non_comm,
        "Commercial": commercial,
        "SmallTrader": small_trader,
        "OpenInterest": oi
    }).set_index("Date")

    return df


def render_cot_chart(market: str = "ES") -> go.Figure:
    """
    Renderiza el gráfico maestro COT con doble eje Y:
    - Eje Y Izquierdo: Barras de Posicionamiento Neto (Non-Commercial azul, Commercial rojo, Small Trader naranja)
    - Eje Y Derecho: Línea verde de Open Interest
    """
    df = generate_cot_historical_timeseries(market)
    meta = COT_MARKETS.get(market, COT_MARKETS["ES"])

    fig = go.Figure()

    # 1. Non-Commercial (Azul - Large Speculators / Managed Money)
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["NonCommercial"] / 1e3,
        name="Non-commercial (Hedge Funds / Managed Money)",
        marker_color="#3378FF",
        opacity=0.86,
        yaxis="y1"
    ))

    # 2. Commercial (Rojo - Productores, Procesadores & Smart Money Hedgers)
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Commercial"] / 1e3,
        name="Commercial (Productores / Hedgers / Smart Money)",
        marker_color="#E53935",
        opacity=0.86,
        yaxis="y1"
    ))

    # 3. Small Trader (Naranja / Ámbar)
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["SmallTrader"] / 1e3,
        name="Small trader (No Reportables / Retail)",
        marker_color="#FFA726",
        opacity=0.86,
        yaxis="y1"
    ))

    # 4. Open Interest (Línea Verde institucional)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["OpenInterest"],
        name="Open Interest Total",
        line=dict(color="#00E676", width=2.2),
        mode="lines+markers",
        marker=dict(size=4, color="#00E676"),
        yaxis="y2"
    ))

    fig.add_annotation(
        x=df.index[int(len(df) * 0.55)],
        y=0,
        text=f"<b>{market} • {meta['name']}:</b> {meta['bias']}<br>Régimen CFTC: <b>{meta['regime']}</b> (COT Index 3Y: {meta.get('cot_index_3y', 50)}%)",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#00E676",
        bgcolor="rgba(15, 23, 42, 0.88)",
        bordercolor="#334155",
        borderwidth=1,
        font=dict(size=11.5, color="#E2E8F0"),
        align="left"
    )

    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=560,
        margin=dict(l=50, r=70, t=30, b=40),
        barmode="relative",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            font=dict(color="#CBD5E1", size=12)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            zeroline=False,
            tickformat="%b %Y"
        ),
        yaxis=dict(
            title=dict(text="Posicionamiento Neto (Miles de Contratos)", font=dict(color="#94A3B8", size=12)),
            tickfont=dict(color="#94A3B8"),
            showgrid=True,
            gridcolor="#1E293B",
            zeroline=True,
            zerolinecolor="#475569",
            zerolinewidth=1.5,
            ticksuffix="K"
        ),
        yaxis2=dict(
            title=dict(text="Open Interest Total", font=dict(color="#00E676", size=12)),
            tickfont=dict(color="#00E676"),
            overlaying="y",
            side="right",
            showgrid=False
        ),
        hovermode="x unified"
    )

    return fig
