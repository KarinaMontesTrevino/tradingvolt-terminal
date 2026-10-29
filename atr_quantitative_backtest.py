"""
atr_quantitative_backtest.py
============================
Backtest cuantitativo riguroso del comportamiento del ATR (14 periodos)
en el mercado accionario estadounidense (ETFs, Megacaps, High Beta, Defensivos).

Preguntas cuantitativas a responder:
1. ¿Qué % de las sesiones el rango total (High - Low) es <= 100% del ATR(14)?
2. ¿Cuál es la probabilidad empírica de alcanzar +25%, +50%, +75%, +100%, +125%, +150% ATR desde el Open?
3. Cuando el precio toca +100% ATR, ¿cuántas veces cierra por debajo (agotamiento/reversión) vs continúa subiendo?
4. ¿Cómo cambia el comportamiento en función del Volumen Relativo (RVol)?
"""

import sys
import numpy as np
import pandas as pd
import yfinance as yf

# Universo de prueba representativo
UNIVERSE = [
    # Índices y ETFs
    "SPY", "QQQ", "IWM",
    # Megacaps
    "AAPL", "NVDA", "MSFT", "TSLA",
    # Momentum / High Beta
    "AMD", "PLTR", "META",
    # Valor / Defensivos
    "JNJ", "KO", "XOM"
]

PERIOD = "5y"  # 5 años de histórico (~1,260 días por ticker)

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calcula el ATR clásico de Wilder de 14 periodos."""
    high = df['High']
    low = df['Low']
    prev_close = df['Close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # Wilder EMA / RMA smoothing
    atr = tr.ewm(alpha=1.0/period, adjust=False).mean()
    return atr

def extract_ticker_data(raw_data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if isinstance(raw_data.columns, pd.MultiIndex):
        if 'Ticker' in raw_data.columns.names:
            df = raw_data.xs(ticker, level='Ticker', axis=1).copy()
        elif ticker in raw_data.columns.levels[0]:
            df = raw_data[ticker].copy()
        else:
            df = raw_data.xs(ticker, level=1, axis=1).copy()
    else:
        df = raw_data.copy()
    return df

def analyze_ticker(ticker: str, data: pd.DataFrame) -> dict:
    df = extract_ticker_data(data, ticker)
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
    if len(df) < 100:
        return None
    
    # Calcular ATR(14)
    df['ATR'] = compute_atr(df, period=14)
    
    # IMPORTANTE: Para evitar lookahead bias, el ATR de hoy es el ATR cerrado de ayer: ATR[1]
    df['ATR_ref'] = df['ATR'].shift(1)
    
    # Volumen Relativo (RVol = Vol / SMA20(Vol)[1])
    vol_sma20 = df['Volume'].rolling(20).mean().shift(1)
    df['RVol'] = df['Volume'] / vol_sma20
    
    # Descartar las primeras 25 barras de calentamiento
    df = df.dropna(subset=['ATR_ref', 'RVol']).copy()
    
    n_days = len(df)
    
    # 1. Rango diario total respecto al ATR: (High - Low) / ATR_ref
    df['Daily_Range_Ratio'] = (df['High'] - df['Low']) / df['ATR_ref']
    
    # 2. Expansiones desde el Open
    df['Up_Exp_Ratio']   = (df['High'] - df['Open']) / df['ATR_ref']
    df['Down_Exp_Ratio'] = (df['Open'] - df['Low']) / df['ATR_ref']
    
    # 3. Probabilidad de que el rango total <= 100% ATR
    pct_range_under_100 = (df['Daily_Range_Ratio'] <= 1.0).mean() * 100.0
    pct_range_under_125 = (df['Daily_Range_Ratio'] <= 1.25).mean() * 100.0
    pct_range_under_150 = (df['Daily_Range_Ratio'] <= 1.50).mean() * 100.0
    median_range_ratio  = df['Daily_Range_Ratio'].median()
    p75_range_ratio     = df['Daily_Range_Ratio'].quantile(0.75)
    p85_range_ratio     = df['Daily_Range_Ratio'].quantile(0.85)
    p90_range_ratio     = df['Daily_Range_Ratio'].quantile(0.90)
    
    # 4. Probabilidades de alcance alcista desde el Open
    p_up_25  = (df['Up_Exp_Ratio'] >= 0.25).mean() * 100.0
    p_up_50  = (df['Up_Exp_Ratio'] >= 0.50).mean() * 100.0
    p_up_75  = (df['Up_Exp_Ratio'] >= 0.75).mean() * 100.0
    p_up_100 = (df['Up_Exp_Ratio'] >= 1.00).mean() * 100.0
    p_up_125 = (df['Up_Exp_Ratio'] >= 1.25).mean() * 100.0
    p_up_150 = (df['Up_Exp_Ratio'] >= 1.50).mean() * 100.0
    
    # 5. Probabilidades de alcance bajista desde el Open
    p_dn_25  = (df['Down_Exp_Ratio'] >= 0.25).mean() * 100.0
    p_dn_50  = (df['Down_Exp_Ratio'] >= 0.50).mean() * 100.0
    p_dn_75  = (df['Down_Exp_Ratio'] >= 0.75).mean() * 100.0
    p_dn_100 = (df['Down_Exp_Ratio'] >= 1.00).mean() * 100.0
    p_dn_125 = (df['Down_Exp_Ratio'] >= 1.25).mean() * 100.0
    p_dn_150 = (df['Down_Exp_Ratio'] >= 1.50).mean() * 100.0
    
    # 6. Agotamiento / Reversión en el 100% ATR Alcista:
    # Si tocó +100% ATR (Up_Exp_Ratio >= 1.0), ¿cuántas veces cerró por debajo de ese nivel?
    # Nivel de precio +100% ATR = Open + ATR_ref
    touched_100_up = df[df['Up_Exp_Ratio'] >= 1.0].copy()
    if len(touched_100_up) > 0:
        target_p100 = touched_100_up['Open'] + touched_100_up['ATR_ref']
        # Cerró por debajo de +100% ATR (significa que retrocedió o no pudo sostenerlo)
        faded_p100_count = (touched_100_up['Close'] < target_p100).sum()
        pct_fade_p100 = (faded_p100_count / len(touched_100_up)) * 100.0
        
        # Retroceso promedio desde el High del día hasta el Cierre (en % de ATR)
        avg_pullback_from_high_atr = ((touched_100_up['High'] - touched_100_up['Close']) / touched_100_up['ATR_ref']).mean()
        
        # Segmentación por RVol:
        # Volumen bajo/normal (RVol <= 1.2)
        normal_vol = touched_100_up[touched_100_up['RVol'] <= 1.2]
        pct_fade_normal_vol = ((normal_vol['Close'] < (normal_vol['Open'] + normal_vol['ATR_ref'])).sum() / len(normal_vol) * 100.0) if len(normal_vol) > 0 else np.nan
        
        # Volumen anormal institucional (RVol > 2.0)
        high_vol = touched_100_up[touched_100_up['RVol'] > 2.0]
        pct_fade_high_vol = ((high_vol['Close'] < (high_vol['Open'] + high_vol['ATR_ref'])).sum() / len(high_vol) * 100.0) if len(high_vol) > 0 else np.nan
        pct_expand_to_150_high_vol = ((high_vol['Up_Exp_Ratio'] >= 1.50).sum() / len(high_vol) * 100.0) if len(high_vol) > 0 else np.nan
    else:
        pct_fade_p100 = np.nan
        avg_pullback_from_high_atr = np.nan
        pct_fade_normal_vol = np.nan
        pct_fade_high_vol = np.nan
        pct_expand_to_150_high_vol = np.nan

    return {
        'ticker': ticker,
        'n_days': n_days,
        # Distribución de Rango
        'range_under_100': pct_range_under_100,
        'range_under_125': pct_range_under_125,
        'median_range': median_range_ratio,
        'p85_range': p85_range_ratio,
        # Probabilidades Alcistas
        'p_up_25': p_up_25,
        'p_up_50': p_up_50,
        'p_up_75': p_up_75,
        'p_up_100': p_up_100,
        'p_up_125': p_up_125,
        'p_up_150': p_up_150,
        # Probabilidades Bajistas
        'p_dn_25': p_dn_25,
        'p_dn_50': p_dn_50,
        'p_dn_75': p_dn_75,
        'p_dn_100': p_dn_100,
        'p_dn_125': p_dn_125,
        'p_dn_150': p_dn_150,
        # Estadísticas de Agotamiento en +100%
        'touched_100_days': len(touched_100_up),
        'pct_fade_p100': pct_fade_p100,
        'avg_pullback_atr': avg_pullback_from_high_atr,
        'pct_fade_normal_vol': pct_fade_normal_vol,
        'pct_fade_high_vol': pct_fade_high_vol,
        'pct_expand_to_150_high_vol': pct_expand_to_150_high_vol
    }

def main():
    print(f"Descargando datos históricos de 5 años para {len(UNIVERSE)} activos...")
    raw_data = yf.download(UNIVERSE, period=PERIOD, interval="1d", group_by="ticker", auto_adjust=False, progress=False)
    
    results = []
    for ticker in UNIVERSE:
        try:
            res = analyze_ticker(ticker, raw_data)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Error procesando {ticker}: {e}")
            
    df_res = pd.DataFrame(results)
    
    print("\n" + "="*80)
    print("           RESULTADOS DEL BACKTEST CUANTITATIVO DEL ATR (5 AÑOS)           ")
    print("="*80)
    
    total_days = df_res['n_days'].sum()
    print(f"Activos analizados: {len(df_res)} | Total de sesiones evaluadas: {total_days:,}")
    
    print("\n1. DISTRIBUCIÓN DEL RANGO DIARIO (High - Low) RESPECTO AL ATR(14):")
    print("-" * 75)
    print(f"{'Ticker':<8} {'Sesiones':<10} {'Mediana':<10} {'P85':<10} {'% Días <= 100% ATR':<22} {'% Días <= 125% ATR':<20}")
    print("-" * 75)
    for _, r in df_res.iterrows():
        print(f"{r['ticker']:<8} {int(r['n_days']):<10} {r['median_range']:.2f} ATR   {r['p85_range']:.2f} ATR   {r['range_under_100']:.1f}%                {r['range_under_125']:.1f}%")
    print("-" * 75)
    print(f"{'PROMEDIO':<8} {int(df_res['n_days'].mean()):<10} {df_res['median_range'].mean():.2f} ATR   {df_res['p85_range'].mean():.2f} ATR   {df_res['range_under_100'].mean():.1f}%                {df_res['range_under_125'].mean():.1f}%")
    
    print("\n\n2. PROBABILIDAD DE ALCANCE DESDE EL RTH OPEN (Hacia arriba):")
    print("-" * 75)
    print(f"{'Ticker':<8} {'>= +25% ATR':<14} {'>= +50% ATR':<14} {'>= +75% ATR':<14} {'>= +100% ATR':<14} {'>= +150% ATR':<14}")
    print("-" * 75)
    for _, r in df_res.iterrows():
        print(f"{r['ticker']:<8} {r['p_up_25']:>9.1f}%     {r['p_up_50']:>9.1f}%     {r['p_up_75']:>9.1f}%     {r['p_up_100']:>9.1f}%     {r['p_up_150']:>9.1f}%")
    print("-" * 75)
    print(f"{'PROMEDIO':<8} {df_res['p_up_25'].mean():>9.1f}%     {df_res['p_up_50'].mean():>9.1f}%     {df_res['p_up_75'].mean():>9.1f}%     {df_res['p_up_100'].mean():>9.1f}%     {df_res['p_up_150'].mean():>9.1f}%")

    print("\n\n3. PROBABILIDAD DE ALCANCE DESDE EL RTH OPEN (Hacia abajo / Bajista):")
    print("-" * 75)
    print(f"{'Ticker':<8} {'<= -25% ATR':<14} {'<= -50% ATR':<14} {'<= -75% ATR':<14} {'<= -100% ATR':<14} {'<= -150% ATR':<14}")
    print("-" * 75)
    for _, r in df_res.iterrows():
        print(f"{r['ticker']:<8} {r['p_dn_25']:>9.1f}%     {r['p_dn_50']:>9.1f}%     {r['p_dn_75']:>9.1f}%     {r['p_dn_100']:>9.1f}%     {r['p_dn_150']:>9.1f}%")
    print("-" * 75)
    print(f"{'PROMEDIO':<8} {df_res['p_dn_25'].mean():>9.1f}%     {df_res['p_dn_50'].mean():>9.1f}%     {df_res['p_dn_75'].mean():>9.1f}%     {df_res['p_dn_100'].mean():>9.1f}%     {df_res['p_dn_150'].mean():>9.1f}%")

    print("\n\n3. PRUEBA DE AGOTAMIENTO CUANDO SE TOCA EL +100% ATR:")
    print("-" * 75)
    print(f"{'Ticker':<8} {'Días tocado':<12} {'% Cierre < 100% (Fade)':<25} {'Retroceso Medio (ATR)':<22}")
    print("-" * 75)
    for _, r in df_res.iterrows():
        print(f"{r['ticker']:<8} {int(r['touched_100_days']):<12} {r['pct_fade_p100']:>18.1f}%         {r['avg_pullback_atr']:>15.2f} ATR")
    print("-" * 75)
    print(f"{'PROMEDIO':<8} {int(df_res['touched_100_days'].mean()):<12} {df_res['pct_fade_p100'].mean():>18.1f}%         {df_res['avg_pullback_atr'].mean():>15.2f} ATR")

    print("\n\n4. EFECTO DEL VOLUMEN RELATIVO (RVol) EN EL +100% ATR:")
    print("-" * 75)
    print(f"{'Ticker':<8} {'% Fade con Vol Normal (<=1.2)':<32} {'% Expansión a 150% con RVol > 2.0':<32}")
    print("-" * 75)
    for _, r in df_res.iterrows():
        print(f"{r['ticker']:<8} {r['pct_fade_normal_vol']:>24.1f}%          {r['pct_expand_to_150_high_vol']:>28.1f}%")
    print("-" * 75)
    print(f"{'PROMEDIO':<8} {df_res['pct_fade_normal_vol'].mean():>24.1f}%          {df_res['pct_expand_to_150_high_vol'].mean():>28.1f}%")
    print("=" * 80)

if __name__ == '__main__':
    main()
