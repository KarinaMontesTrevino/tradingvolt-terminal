import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks

# =====================================================================
# MOTOR DE NIVELES CLAVE INSTITUCIONALES (KEY LEVELS ENGINE)
# ADAPTABLE A CUALQUIER ACTIVO (ACCIONES, ETFS, CRIPTO, SMALL/LARGE CAPS)
# =====================================================================

def calculate_key_levels(df, atr_period=14, lookback_bars=150, cluster_tolerance_mult=0.45):
    """
    Calcula los niveles clave institucionales con alta confluencia:
    1. Perfil de Volumen (Volume Profile): Point of Control (POC) y Nodos de Alto Volumen (HVN).
    2. Swings Fractales Ponderados por Volumen (Pivotes estructurales con volumen institucional).
    3. Anclas Macro: Máximo y Mínimo de 52 semanas, Rango Semanal Previo (PWH, PWL) y Gaps no cubiertos.
    4. Memoria de Rebotes y Polaridad (toques históricos de rechazo).
    5. Agrupación y Puntuación de Confluencia adaptativa normalizada por ATR (funciona para cualquier precio y volatilidad).
    """
    if df.empty or len(df) < 20:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    close = df['Close']
    high = df['High']
    low = df['Low']
    vol = df['Volume']
    spot = float(close.iloc[-1])

    # 1. Volatilidad Dinámica (ATR 14) para normalización universal
    hl = high - low
    hc = (high - close.shift()).abs()
    lc = (low - close.shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr_series = tr.rolling(atr_period, min_periods=5).mean()
    atr = float(atr_series.iloc[-1]) if not np.isnan(atr_series.iloc[-1]) else float(tr.mean())
    if atr <= 0 or np.isnan(atr):
        atr = spot * 0.02 # Fallback 2%

    # 2. Perfil de Volumen (Volume Profile sobre ventana lookback)
    recent_len = min(lookback_bars, len(df))
    recent_df = df.iloc[-recent_len:]
    p_min = float(recent_df['Low'].min())
    p_max = float(recent_df['High'].max())

    bin_size = max(atr * 0.25, spot * 0.002)
    num_bins = max(int((p_max - p_min) / bin_size) + 1, 10)
    bins = np.linspace(p_min, p_max, num_bins)
    vol_hist = np.zeros(len(bins) - 1)

    for _, row in recent_df.iterrows():
        b_low, b_high, b_v = row['Low'], row['High'], row['Volume']
        if b_high <= b_low or np.isnan(b_v):
            continue
        overlap_bins = np.where((bins[:-1] < b_high) & (bins[1:] > b_low))[0]
        if len(overlap_bins) > 0:
            vol_hist[overlap_bins] += (b_v / len(overlap_bins))

    poc_idx = int(np.argmax(vol_hist))
    poc_price = float((bins[poc_idx] + bins[poc_idx + 1]) / 2.0)

    # Nodos secundarios de alto volumen (HVN)
    smoothed_vol = pd.Series(vol_hist).rolling(3, min_periods=1, center=True).mean().values
    max_vol = smoothed_vol.max() if len(smoothed_vol) > 0 else 1.0
    peaks, _ = find_peaks(smoothed_vol, distance=4, prominence=max_vol * 0.15)
    hvn_prices = [float((bins[p] + bins[p + 1]) / 2.0) for p in peaks if p != poc_idx]

    # 3. Pivotes Fractales Multiescala con Ponderación de Volumen
    swing_highs = []
    swing_lows = []
    avg_vol = vol.rolling(20, min_periods=5).mean()

    # Ventana de 5 barras
    for i in range(5, len(df) - 5):
        w_h = high.iloc[i - 5 : i + 6]
        w_l = low.iloc[i - 5 : i + 6]
        c_v = vol.iloc[i]
        m_v = avg_vol.iloc[i] if not np.isnan(avg_vol.iloc[i]) else 1.0
        v_mult = float(min(c_v / max(m_v, 1.0), 3.0))

        if high.iloc[i] == w_h.max():
            swing_highs.append((float(high.iloc[i]), v_mult))
        if low.iloc[i] == w_l.min():
            swing_lows.append((float(low.iloc[i]), v_mult))

    # 4. Anclas Macro Estructurales
    max_52w = float(high.rolling(min(250, len(df)), min_periods=50).max().iloc[-1])
    min_52w = float(low.rolling(min(250, len(df)), min_periods=50).min().iloc[-1])

    # Gaps institucionales significativos (mayores a 0.75 * ATR)
    gap_levels = []
    for i in range(1, len(recent_df)):
        prev_h = recent_df['High'].iloc[i - 1]
        prev_l = recent_df['Low'].iloc[i - 1]
        curr_l = recent_df['Low'].iloc[i]
        curr_h = recent_df['High'].iloc[i]

        if curr_l > prev_h and (curr_l - prev_h) >= 0.75 * atr:
            gap_levels.append((float(prev_h), 'Gap Up Base'))
            gap_levels.append((float(curr_l), 'Gap Up Techo'))
        elif curr_h < prev_l and (prev_l - curr_h) >= 0.75 * atr:
            gap_levels.append((float(prev_l), 'Gap Down Techo'))
            gap_levels.append((float(curr_h), 'Gap Down Base'))

    # 5. Consolidación de Candidatos
    candidates = []
    candidates.append({'price': poc_price, 'tag': 'POC (Volume Magnet)', 'score': 35})
    for h in hvn_prices:
        candidates.append({'price': h, 'tag': 'HVN (Volume Node)', 'score': 20})
    for sh, vm in swing_highs[-18:]:
        candidates.append({'price': sh, 'tag': 'Swing High', 'score': 15 * vm})
    for sl, vm in swing_lows[-18:]:
        candidates.append({'price': sl, 'tag': 'Swing Low', 'score': 15 * vm})
    if max_52w > 0:
        candidates.append({'price': max_52w, 'tag': '52w High (ATH/Major)', 'score': 30})
    if min_52w > 0:
        candidates.append({'price': min_52w, 'tag': '52w Low (Major Support)', 'score': 30})
    for gl, g_tag in gap_levels[-6:]:
        candidates.append({'price': gl, 'tag': g_tag, 'score': 18})

    # 6. Agrupamiento Adaptativo por ATR (Clustering)
    cluster_tol = atr * cluster_tolerance_mult
    sorted_cands = sorted(candidates, key=lambda x: x['price'])
    clusters = []

    for c in sorted_cands:
        if not clusters:
            clusters.append([c])
        else:
            curr_avg = np.mean([item['price'] for item in clusters[-1]])
            if abs(c['price'] - curr_avg) <= cluster_tol:
                clusters[-1].append(c)
            else:
                clusters.append([c])

    # 7. Puntuación de Confluencia y Clasificación
    final_levels = []
    for cl in clusters:
        cl_prices = [item['price'] for item in cl]
        cl_scores = [item['score'] for item in cl]
        cl_tags = list(dict.fromkeys([item['tag'] for item in cl]))

        rep_price = float(np.average(cl_prices, weights=cl_scores))
        raw_score = sum(cl_scores)

        # Memoria histórica: conteo de toques/rechazos
        touches = int(((high >= rep_price - 0.25 * atr) & (low <= rep_price + 0.25 * atr)).sum())
        confluence_score = min(int(raw_score + min(touches * 2.5, 20)), 100)

        dist_pct = ((rep_price / spot) - 1.0) * 100.0
        dist_abs = abs(dist_pct)

        if rep_price > spot:
            lvl_type = 'RESISTENCIA'
        elif rep_price < spot:
            lvl_type = 'SOPORTE'
        else:
            lvl_type = 'SPOT'

        # Clasificación por Estrellas
        if confluence_score >= 65:
            stars = '⭐⭐⭐⭐⭐'
            rating = 'Crítico Institucional'
        elif confluence_score >= 45:
            stars = '⭐⭐⭐⭐'
            rating = 'Fuerte / Estructural'
        elif confluence_score >= 30:
            stars = '⭐⭐⭐'
            rating = 'Relevante'
        else:
            stars = '⭐⭐'
            rating = 'Menor'

        final_levels.append({
            'Price': rep_price,
            'Type': lvl_type,
            'ConfluenceScore': confluence_score,
            'Stars': stars,
            'Rating': rating,
            'Tags': ' + '.join(cl_tags),
            'Touches': touches,
            'DistPct': dist_pct,
            'DistAbs': dist_abs,
            'ZoneTop': rep_price + (0.15 * atr),
            'ZoneBottom': rep_price - (0.15 * atr)
        })

    # Filtrar y ordenar los mejores niveles arriba y abajo
    resistances = [l for l in final_levels if l['Type'] == 'RESISTENCIA']
    supports = [l for l in final_levels if l['Type'] == 'SOPORTE']

    # Las 3 resistencias más cercanas ordenadas de menor a mayor precio
    resistances = sorted(resistances, key=lambda x: x['Price'])[:3]
    # Los 3 soportes más cercanos ordenados de mayor a menor precio
    supports = sorted(supports, key=lambda x: x['Price'], reverse=True)[:3]

    # Asignar etiquetas R1, R2, R3 y S1, S2, S3
    for idx, r in enumerate(resistances):
        r['Label'] = f"R{idx+1}"
    for idx, s in enumerate(supports):
        s['Label'] = f"S{idx+1}"

    # Construir DataFrame resumen
    summary_rows = []
    for r in reversed(resistances):
        summary_rows.append({
            'Nivel': r['Label'],
            'Tipo': '🔴 Resistencia',
            'Precio': f"${r['Price']:.2f}",
            'Distancia': f"{r['DistPct']:+.2f}%",
            'Confluencia': f"{r['Stars']} ({r['ConfluenceScore']})",
            'Factores Institucionales': r['Tags'],
            'Toques': r['Touches'],
            'raw_price': r['Price']
        })

    # Fila de Spot
    summary_rows.append({
        'Nivel': '🎯 SPOT',
        'Tipo': '⚪ Precio Actual',
        'Precio': f"${spot:.2f}",
        'Distancia': "0.00%",
        'Confluencia': 'ACTIVO',
        'Factores Institucionales': f'ATR(14): ${atr:.2f} ({atr/spot*100:.1f}%)',
        'Toques': len(df),
        'raw_price': spot
    })

    for s in supports:
        summary_rows.append({
            'Nivel': s['Label'],
            'Tipo': '🟢 Soporte',
            'Precio': f"${s['Price']:.2f}",
            'Distancia': f"{s['DistPct']:+.2f}%",
            'Confluencia': f"{s['Stars']} ({s['ConfluenceScore']})",
            'Factores Institucionales': s['Tags'],
            'Toques': s['Touches'],
            'raw_price': s['Price']
        })

    summary_df = pd.DataFrame(summary_rows)

    return {
        'spot': spot,
        'atr': atr,
        'poc_price': poc_price,
        'resistances': resistances,
        'supports': supports,
        'summary_df': summary_df,
        'all_levels': resistances + supports
    }


def add_key_levels_to_chart(fig, levels_data, is_intraday=False, font_size=10, x_dates=None):
    """
    Dibuja los niveles clave institucionales de forma limpia, elegante y no intrusiva en el gráfico Plotly.
    - Rayos horizontales recientes (últimas 35-40 barras) para evitar saturar el historial de velas
    - Filtra para dibujar únicamente los niveles más relevantes (Top 2 Resistencias, Top 2 Soportes y POC)
    - Etiquetas tipo píldora nítidas en el extremo derecho
    - NUNCA distorsiona el eje X ni provoca saltos a 1970
    """
    if not levels_data or 'all_levels' not in levels_data or not fig:
        return fig

    # Extraer fechas del gráfico si no se pasaron explícitamente
    if x_dates is None:
        try:
            x_dates = fig.data[0].x
        except Exception:
            x_dates = None

    if x_dates is None or len(x_dates) == 0:
        return fig

    spot = levels_data.get('spot', 0)
    atr = levels_data.get('atr', 1.0)
    sub_font_size = max(int(font_size * 0.82), 8)

    # Anclar líneas a las últimas 35-40 barras para máxima limpieza y visibilidad
    lookback_bars = min(40, len(x_dates))
    x_start = x_dates[-lookback_bars]
    x_end = x_dates[-1]

    # Filtrar sólo los niveles clave más accionables:
    # Top 2 Resistencias más cercanas
    top_res = levels_data.get('resistances', [])[:2]
    # Top 2 Soportes más cercanos
    top_sup = levels_data.get('supports', [])[:2]
    
    levels_to_draw = top_res + top_sup

    for lvl in levels_to_draw:
        p = lvl['Price']
        label = lvl.get('Label', '')
        lvl_type = lvl['Type']
        dist_str = f"{lvl['DistPct']:+.1f}%"

        if lvl_type == 'RESISTENCIA':
            line_col = 'rgba(255, 46, 99, 0.75)'
            border_col = 'rgba(255, 46, 99, 0.60)'
            bg_col = 'rgba(24, 14, 20, 0.92)'
            txt_col = '#FF4B72'
        else:
            line_col = 'rgba(0, 230, 138, 0.75)'
            border_col = 'rgba(0, 230, 138, 0.60)'
            bg_col = 'rgba(10, 24, 18, 0.92)'
            txt_col = '#00FF87'

        # 1. Segmento de línea acotado en el tiempo (reciente, no infinito)
        fig.add_shape(
            type="line",
            x0=x_start,
            x1=x_end,
            y0=p,
            y1=p,
            xref="x",
            yref="y",
            line=dict(color=line_col, width=1.4, dash='dash'),
            row=1, col=1
        )

        # 2. Anotación compacta y elegante anclada al extremo derecho del gráfico
        annotation_text = f"<b>{label}</b> ${p:.2f} <span style='font-size:{sub_font_size}px; color:#94A3B8;'>({dist_str})</span>"
        fig.add_annotation(
            xref="x",
            yref="y",
            x=x_end,
            y=p,
            text=annotation_text,
            showarrow=False,
            xanchor="right",
            yanchor="middle",
            font=dict(size=font_size, color=txt_col, family="JetBrains Mono, monospace"),
            bgcolor=bg_col,
            bordercolor=border_col,
            borderwidth=1,
            borderpad=3,
            opacity=0.95,
            row=1, col=1
        )

    # 3. Línea de POC Institucional (si no coincide con ningún nivel dibujado)
    poc = levels_data.get('poc_price', 0)
    if poc > 0 and levels_to_draw:
        nearest_diff = min([abs(lvl['Price'] - poc) for lvl in levels_to_draw])
        if nearest_diff > 0.4 * atr:
            poc_dist = ((poc / spot) - 1.0) * 100.0 if spot > 0 else 0.0
            fig.add_shape(
                type="line",
                x0=x_start,
                x1=x_end,
                y0=poc,
                y1=poc,
                xref="x",
                yref="y",
                line=dict(color='rgba(0, 240, 255, 0.75)', width=1.4, dash='dot'),
                row=1, col=1
            )
            fig.add_annotation(
                xref="x",
                yref="y",
                x=x_end,
                y=poc,
                text=f"<b>POC</b> ${poc:.2f} <span style='font-size:{sub_font_size}px; color:#94A3B8;'>({poc_dist:+.1f}%)</span>",
                showarrow=False,
                xanchor="right",
                yanchor="middle",
                font=dict(size=font_size, color='#00F0FF', family="JetBrains Mono, monospace"),
                bgcolor='rgba(10, 22, 28, 0.92)',
                bordercolor='rgba(0, 240, 255, 0.60)',
                borderwidth=1,
                borderpad=3,
                opacity=0.95,
                row=1, col=1
            )

    return fig

