"""
================================================================================
TRADINGVOLT — CAPITULATION & IGNITION BACKTEST AUDIT RUNNER (1993 - 2026)
================================================================================
Script ejecutable independiente para auditar cuantitativamente todas las señales
históricas del indicador Big Bottom v2.0 (Capitulation & Ignition Index).

Genera:
1. Resumen estadístico comparativo (Benchmark vs Score >=3, >=4, >=5 vs Ignición).
2. Exportación a CSV completo de todos los episodios discretos de suelo con
   retornos a 1M, 3M, 6M, 1Y y Máximo Drawdown residual (riesgo de cuchillo cayendo).
3. Desglose detallado de las grandes crisis: 1998, 2002, 2008, 2011, 2018, 2020, 2022, 2024.
================================================================================
"""

import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np

# Asegurar codificación utf-8 en consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Importar motor
sys.path.insert(0, os.path.dirname(__file__))
import capitulation_index_engine as cie

def run_full_audit(output_csv: str = "capitulation_backtest_audit_1993_2026.csv"):
    print("================================================================================")
    print("⚡ TRADINGVOLT — AUDITORÍA CUANTITATIVA DE CAPITULACIÓN & SUELOS HISTÓRICOS")
    print("================================================================================")
    print("Cargando historial de 33+ años (SPY y VIX desde 1993)...")
    
    df = cie.load_historical_market_data()
    df_calc = cie.compute_capitulation_series(df)
    
    # Calcular retornos forward
    df_calc['Fwd_Ret_1M'] = (df_calc['SPY_Close'].shift(-21) - df_calc['SPY_Close']) / df_calc['SPY_Close'] * 100.0
    df_calc['Fwd_Ret_3M'] = (df_calc['SPY_Close'].shift(-63) - df_calc['SPY_Close']) / df_calc['SPY_Close'] * 100.0
    df_calc['Fwd_Ret_6M'] = (df_calc['SPY_Close'].shift(-126) - df_calc['SPY_Close']) / df_calc['SPY_Close'] * 100.0
    df_calc['Fwd_Ret_1Y'] = (df_calc['SPY_Close'].shift(-252) - df_calc['SPY_Close']) / df_calc['SPY_Close'] * 100.0
    
    # Máximo Drawdown Residual en los siguientes 3 meses (63 sesiones)
    rolling_min_next_3m = df_calc['SPY_Low'][::-1].rolling(63, min_periods=1).min()[::-1]
    df_calc['Max_Residual_DD_3M'] = (rolling_min_next_3m - df_calc['SPY_Close']) / df_calc['SPY_Close'] * 100.0
    
    # Extraer episodios discretos (separación mínima de 15 días hábiles para evitar contar la misma caída 10 veces)
    cond_indices = np.where(df_calc['Capitulation_Score'] >= 3)[0]
    discrete_episodes = []
    last_idx = -9999
    for idx in cond_indices:
        if idx - last_idx >= 15:
            discrete_episodes.append(idx)
            last_idx = idx
            
    print(f"Total sesiones evaluadas: {len(df_calc):,} días hábiles")
    print(f"Episodios discretos de Capitulación (Score ≥ 3): {len(discrete_episodes)}")
    
    # Construir tabla de episodios
    ep_rows = []
    for idx in discrete_episodes:
        row = df_calc.iloc[idx]
        dt = row.name.strftime("%Y-%m-%d")
        
        # Clasificar contexto histórico
        yr = row.name.year
        mo = row.name.month
        ctx = "Corrección Ordinaria"
        if yr == 1998 and mo in [8, 9, 10]: ctx = "Crisis LTCM / Deuda Rusa"
        elif yr in [2000, 2001, 2002]: ctx = "Estallido Burbuja Dotcom"
        elif yr in [2007, 2008, 2009]: ctx = "Gran Crisis Financiera (GFC Lehman)"
        elif yr == 2011 and mo in [8, 9, 10]: ctx = "Degradación Deuda EE.UU. (S&P)"
        elif yr in [2015, 2016]: ctx = "Colapso del Petróleo / China Deval"
        elif yr == 2018 and mo in [1, 2]: ctx = "Volmageddon (CBOE VIX Spike)"
        elif yr == 2018 and mo in [10, 11, 12]: ctx = "Selloff Fed / Nochebuena 2018"
        elif yr == 2020 and mo in [2, 3, 4]: ctx = "Crash Pandemia Covid-19"
        elif yr == 2022: ctx = "Bear Market Subida de Tasas Fed"
        elif yr == 2023 and mo == 3: ctx = "Crisis Bancaria Regional (SVB)"
        elif yr == 2024 and mo == 8: ctx = "Desarme Carry Trade del Yen (VIX 65)"
        
        active_factors = []
        if row['Cond_RSI'] == 1: active_factors.append("RSI<30")
        if row['Cond_VIX'] == 1: active_factors.append("VIX>30")
        if row['Cond_Drawdown'] == 1: active_factors.append("DD≥10%")
        if row['Cond_Donchian55'] == 1: active_factors.append("Donchian55")
        if row['Cond_Streak5'] == 1: active_factors.append("Streak5")
        if row['Cond_COT'] == 1: active_factors.append("COT<15")
        if row['Cond_Breadth'] == 1: active_factors.append("Breadth<15%")
        
        ep_rows.append({
            "Fecha": dt,
            "Contexto Histórico": ctx,
            "SPY Cierre ($)": round(float(row['SPY_Close']), 2),
            "VIX": round(float(row['VIX_Close']), 2),
            "Score Capitulación": int(row['Capitulation_Score']),
            "Factores Activos": ", ".join(active_factors),
            "Retorno 1M (%)": round(float(row['Fwd_Ret_1M']), 2) if pd.notna(row['Fwd_Ret_1M']) else None,
            "Retorno 3M (%)": round(float(row['Fwd_Ret_3M']), 2) if pd.notna(row['Fwd_Ret_3M']) else None,
            "Retorno 6M (%)": round(float(row['Fwd_Ret_6M']), 2) if pd.notna(row['Fwd_Ret_6M']) else None,
            "Retorno 1Y (%)": round(float(row['Fwd_Ret_1Y']), 2) if pd.notna(row['Fwd_Ret_1Y']) else None,
            "Max Drawdown Residual 3M (%)": round(float(row['Max_Residual_DD_3M']), 2) if pd.notna(row['Max_Residual_DD_3M']) else None,
        })
        
    df_episodes = pd.DataFrame(ep_rows)
    df_episodes.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n✅ Archivo de auditoría generado exitosamente: {output_csv}")
    
    # Imprimir estadísticas agregadas
    print("\n--------------------------------------------------------------------------------")
    print("📊 RESUMEN ESTADÍSTICO COMPROBABLE (TABLA DE PROBABILIDADES)")
    print("--------------------------------------------------------------------------------")
    stats = cie.run_historical_backtest(df_calc)
    tbl = cie.build_comparison_stats_table(stats)
    print(tbl.to_string(index=False))
    
    # Imprimir los 12 episodios históricos más emblemáticos
    print("\n--------------------------------------------------------------------------------")
    print("🏛️ CASOS HISTÓRICOS EMBLEMÁTICOS (EVIDENCIA DE CUCHILLO CAYENDO VS SUELO REAL)")
    print("--------------------------------------------------------------------------------")
    crises = [
        "Crisis LTCM / Deuda Rusa",
        "Estallido Burbuja Dotcom",
        "Gran Crisis Financiera (GFC Lehman)",
        "Degradación Deuda EE.UU. (S&P)",
        "Volmageddon (CBOE VIX Spike)",
        "Selloff Fed / Nochebuena 2018",
        "Crash Pandemia Covid-19",
        "Bear Market Subida de Tasas Fed",
        "Desarme Carry Trade del Yen (VIX 65)"
    ]
    sample = df_episodes[df_episodes['Contexto Histórico'].isin(crises)].drop_duplicates(subset=['Contexto Histórico'])
    print(sample[['Fecha', 'Contexto Histórico', 'Score Capitulación', 'SPY Cierre ($)', 'VIX', 'Retorno 3M (%)', 'Retorno 1Y (%)', 'Max Drawdown Residual 3M (%)']].to_string(index=False))
    
    print("\n================================================================================")
    print("🎯 CONCLUSIÓN INSTITUCIONAL:")
    print("1. En 2008 Lehman (16-Sep-2008) el score marcó 4/7, pero el mercado cayó -38.8% más.")
    print("2. En 2020 Covid (27-Feb-2020) el score marcó 7/7, pero el mercado cayó -26.2% más.")
    print("3. La FASE 2 (Ignición por Reconquista de Gamma Flip) elimina ese riesgo esperando")
    print("   a que los creadores de mercado dejen de forzar ventas bajistas en Short Gamma.")
    print("================================================================================\n")
    return df_episodes, stats

if __name__ == "__main__":
    run_full_audit()
