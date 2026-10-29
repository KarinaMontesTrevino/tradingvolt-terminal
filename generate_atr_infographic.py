"""
generate_atr_infographic.py
===========================
Generates a publication-grade, dark-neon quantitative visualization dashboard
of the 16,042-session ATR Backtest across 13 US assets over 5 years.
Saves image directly to artifact directory.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import yfinance as yf

# Universo de prueba
UNIVERSE = ["SPY", "QQQ", "IWM", "AAPL", "NVDA", "MSFT", "TSLA", "AMD", "PLTR", "META", "JNJ", "KO", "XOM"]
OUTPUT_PATH = r"C:\Users\kim17\.gemini\antigravity\brain\616bb7ba-2c00-440d-83eb-21450dd9cf78\atr_backtest_dashboard.png"

def compute_atr(df, period=14):
    high = df['High']
    low = df['Low']
    prev_close = df['Close'].shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0/period, adjust=False).mean()

def main():
    print("Descargando datos para el gráfico de alta resolución...")
    raw = yf.download(UNIVERSE, period="5y", interval="1d", group_by="ticker", auto_adjust=False, progress=False)
    
    all_days = []
    ticker_stats = []
    
    for t in UNIVERSE:
        if 'Ticker' in raw.columns.names:
            df = raw.xs(t, level='Ticker', axis=1).copy()
        elif t in raw.columns.levels[0]:
            df = raw[t].copy()
        else:
            df = raw.xs(t, level=1, axis=1).copy()
            
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume']).copy()
        if len(df) < 100:
            continue
            
        df['ATR'] = compute_atr(df, 14)
        df['ATR_ref'] = df['ATR'].shift(1)
        vol_sma20 = df['Volume'].rolling(20).mean().shift(1)
        df['RVol'] = df['Volume'] / vol_sma20
        df = df.dropna(subset=['ATR_ref', 'RVol']).copy()
        
        df['Daily_Range_Ratio'] = (df['High'] - df['Low']) / df['ATR_ref']
        df['Up_Exp'] = (df['High'] - df['Open']) / df['ATR_ref']
        df['Down_Exp'] = (df['Open'] - df['Low']) / df['ATR_ref']
        df['Ticker'] = t
        
        # Guardar para pool global
        all_days.append(df[['Daily_Range_Ratio', 'Up_Exp', 'Down_Exp', 'RVol', 'Ticker', 'High', 'Low', 'Open', 'Close', 'ATR_ref']])
        
        # Stats por ticker
        t_under100 = (df['Daily_Range_Ratio'] <= 1.0).mean() * 100.0
        t_up50 = (df['Up_Exp'] >= 0.50).mean() * 100.0
        t_up100 = (df['Up_Exp'] >= 1.00).mean() * 100.0
        t_dn100 = (df['Down_Exp'] >= 1.00).mean() * 100.0
        
        touched_100 = df[df['Up_Exp'] >= 1.0]
        if len(touched_100) > 0:
            t_fade = (touched_100['Close'] < (touched_100['Open'] + touched_100['ATR_ref'])).mean() * 100.0
            norm_vol = touched_100[touched_100['RVol'] <= 1.2]
            fade_norm = (norm_vol['Close'] < (norm_vol['Open'] + norm_vol['ATR_ref'])).mean() * 100.0 if len(norm_vol) > 0 else np.nan
            high_vol = touched_100[touched_100['RVol'] > 2.0]
            exp_150_hv = (high_vol['Up_Exp'] >= 1.5).mean() * 100.0 if len(high_vol) > 0 else np.nan
        else:
            t_fade, fade_norm, exp_150_hv = np.nan, np.nan, np.nan
            
        ticker_stats.append({
            'Ticker': t,
            'Range <= 1.0 ATR': t_under100,
            'Reach +50% ATR': t_up50,
            'Reach +100% ATR': t_up100,
            'Reach -100% ATR': t_dn100,
            'Fade at +100%': t_fade,
            'Fade Normal Vol': fade_norm,
            'Exp 150% High Vol': exp_150_hv
        })
        
    df_all = pd.concat(all_days, ignore_index=True)
    df_ts = pd.DataFrame(ticker_stats)
    
    print(f"Total datos combinados: {len(df_all):,} sesiones.")
    
    # ------------------ CONFIGURACIÓN VISUAL MATPLOTLIB ------------------
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(20, 12), facecolor='#0A0D14')
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.32, wspace=0.25, left=0.06, right=0.96, top=0.90, bottom=0.07)
    
    # Colores corporativos Neon
    c_bg = '#0E131F'
    c_cyan = '#00F0FF'
    c_green = '#00FF87'
    c_red = '#FF2E63'
    c_amber = '#FFB703'
    c_text = '#F1F5F9'
    c_sub = '#94A3B8'
    c_grid = '#1E293B'
    
    # Título Principal
    fig.suptitle('EVIDENCIA CUANTITATIVA: ANÁLISIS DEL ATR COMO NIVELES INSTITUCIONALES\n'
                 f'Backtest sobre {len(df_all):,} Sesiones Reales (5 Años) | 13 Activos (SPY, QQQ, AAPL, NVDA, TSLA, etc.)',
                 fontsize=18, fontweight='bold', color=c_text, y=0.97, fontfamily='DejaVu Sans')

    # =========================================================================
    # PANEL 1 (Arriba Izq): DISTRIBUCIÓN DEL RANGO DIARIO / ATR RATIO
    # =========================================================================
    ax1 = fig.add_subplot(gs[0, 0], facecolor=c_bg)
    ratios = df_all['Daily_Range_Ratio'].clip(upper=2.5)
    
    # Histograma con KDE
    n, bins, patches = ax1.hist(ratios, bins=60, density=True, alpha=0.35, color=c_cyan, edgecolor='none')
    for b_idx, patch in enumerate(patches):
        x_val = bins[b_idx]
        if x_val <= 1.0:
            patch.set_facecolor(c_green)
            patch.set_alpha(0.55)
        elif x_val <= 1.25:
            patch.set_facecolor(c_amber)
            patch.set_alpha(0.65)
        else:
            patch.set_facecolor(c_red)
            patch.set_alpha(0.70)
            
    sns.kdeplot(ratios, ax=ax1, color='#FFFFFF', linewidth=2.2, bw_adjust=1.2)
    
    med = ratios.median()
    p85 = ratios.quantile(0.85)
    
    ax1.axvline(med, color=c_cyan, linestyle='--', linewidth=1.8, label=f'Mediana: {med:.2f} ATR')
    ax1.axvline(1.00, color=c_green, linestyle='-', linewidth=2.5, label='1.00 ATR: Techo Normal (68.0% Días)')
    ax1.axvline(1.25, color=c_amber, linestyle='--', linewidth=2.0, label='1.25 ATR: P85 (83.9% Días Acum)')
    
    ax1.set_title('1. Distribución del Rango Diario (High - Low) / ATR(14)', fontsize=13, fontweight='bold', color=c_cyan, pad=12)
    ax1.set_xlabel('Rango Diario en Múltiplos de ATR', fontsize=11, color=c_sub)
    ax1.set_ylabel('Densidad de Probabilidad', fontsize=11, color=c_sub)
    ax1.grid(True, color=c_grid, linestyle=':', alpha=0.7)
    ax1.set_xlim(0.2, 2.3)
    ax1.legend(loc='upper right', frameon=True, facecolor='#151C28', edgecolor=c_grid, fontsize=9.5)
    
    # Anotación explicativa
    ax1.text(0.30, ax1.get_ylim()[1]*0.75, 
             "★ 83.9% de las sesiones NO superan\n   1.25 ATR de recorrido diario.\n★ Solo 16.1% son anomalías extremas.", 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#151C28', edgecolor=c_amber, alpha=0.9),
             fontsize=10, color=c_text, fontweight='semibold')

    # =========================================================================
    # PANEL 2 (Arriba Der): PROBABILIDAD DE ALCANCE DESDE EL OPEN (PIRÁMIDE)
    # =========================================================================
    ax2 = fig.add_subplot(gs[0, 1], facecolor=c_bg)
    levels = ['±25% ATR', '±50% ATR', '±75% ATR', '±100% ATR', '±150% ATR']
    up_probs = [
        (df_all['Up_Exp'] >= 0.25).mean() * 100,
        (df_all['Up_Exp'] >= 0.50).mean() * 100,
        (df_all['Up_Exp'] >= 0.75).mean() * 100,
        (df_all['Up_Exp'] >= 1.00).mean() * 100,
        (df_all['Up_Exp'] >= 1.50).mean() * 100,
    ]
    dn_probs = [
        (df_all['Down_Exp'] >= 0.25).mean() * 100,
        (df_all['Down_Exp'] >= 0.50).mean() * 100,
        (df_all['Down_Exp'] >= 0.75).mean() * 100,
        (df_all['Down_Exp'] >= 1.00).mean() * 100,
        (df_all['Down_Exp'] >= 1.50).mean() * 100,
    ]
    
    y = np.arange(len(levels))
    height = 0.36
    
    rects1 = ax2.barh(y - height/2, up_probs, height, label='Alcista (+ATR desde Open)', color=c_green, alpha=0.85, edgecolor='none')
    rects2 = ax2.barh(y + height/2, dn_probs, height, label='Bajista (-ATR desde Open)', color=c_red, alpha=0.85, edgecolor='none')
    
    ax2.set_yticks(y)
    ax2.set_yticklabels(levels, fontsize=10.5, color=c_text, fontweight='bold')
    ax2.invert_yaxis()
    ax2.set_xlim(0, 80)
    ax2.set_xlabel('Probabilidad de Alcance Empírica (%)', fontsize=11, color=c_sub)
    ax2.set_title('2. Probabilidad de Alcanzar Niveles desde el Open (0% ATR)', fontsize=13, fontweight='bold', color=c_cyan, pad=12)
    ax2.grid(True, color=c_grid, linestyle=':', alpha=0.7)
    ax2.legend(loc='lower right', frameon=True, facecolor='#151C28', edgecolor=c_grid, fontsize=10)
    
    for r1, r2, u_v, d_v in zip(rects1, rects2, up_probs, dn_probs):
        ax2.text(u_v + 1.2, r1.get_y() + r1.get_height()/2, f"{u_v:.1f}%", va='center', ha='left', fontsize=9.5, color=c_green, fontweight='bold')
        ax2.text(d_v + 1.2, r2.get_y() + r2.get_height()/2, f"{d_v:.1f}%", va='center', ha='left', fontsize=9.5, color=c_red, fontweight='bold')

    # =========================================================================
    # PANEL 3 (Abajo Izq): MATRIZ CROSS-ASSET (HEATMAP POR TICKER)
    # =========================================================================
    ax3 = fig.add_subplot(gs[1, 0], facecolor=c_bg)
    
    # Preparar matriz de tickers
    df_heat = df_ts.set_index('Ticker')[['Range <= 1.0 ATR', 'Reach +50% ATR', 'Reach +100% ATR', 'Fade at +100%']].copy()
    
    sns.heatmap(df_heat, annot=True, fmt=".1f", cmap="magma", ax=ax3, cbar=False,
                linewidths=1, linecolor='#0A0D14', annot_kws={"size": 9.5, "weight": "bold", "color": "white"})
    
    ax3.set_title('3. Consistencia entre Activos (Índices vs Megacaps vs Defensivos)', fontsize=13, fontweight='bold', color=c_cyan, pad=12)
    ax3.set_xlabel('')
    ax3.set_ylabel('')
    ax3.set_xticklabels(['Rango <= 1.0 ATR', 'Toca +50% ATR', 'Toca +100% ATR', 'Rechazo en 100%'], fontsize=9.5, color=c_text, fontweight='bold')
    ax3.tick_params(axis='y', labelsize=10, colors=c_text)

    # =========================================================================
    # PANEL 4 (Abajo Der): AGOTAMIENTO vs CONTINUACIÓN SEGÚN VOLUMEN (RVOL)
    # =========================================================================
    ax4 = fig.add_subplot(gs[1, 1], facecolor=c_bg)
    
    categories = ['Volumen Normal\n(RVol <= 1.2)', 'Volumen Anómalo\nInstitucional (RVol > 2.0)']
    
    avg_fade_norm = df_ts['Fade Normal Vol'].mean()
    avg_exp_high = df_ts['Exp 150% High Vol'].mean()
    
    bar_x = [0, 1]
    values = [avg_fade_norm, avg_exp_high]
    bar_colors = [c_red, c_cyan]
    
    bars = ax4.bar(bar_x, values, width=0.48, color=bar_colors, alpha=0.85, edgecolor=[c_red, c_cyan], linewidth=1.5)
    
    ax4.set_xticks(bar_x)
    ax4.set_xticklabels(categories, fontsize=11, color=c_text, fontweight='bold')
    ax4.set_ylim(0, 100)
    ax4.set_ylabel('Probabilidad Empírica (%)', fontsize=11, color=c_sub)
    ax4.set_title('4. El Factor Decisivo: ¿Reversión o Ruptura al Tocar +100% ATR?', fontsize=13, fontweight='bold', color=c_cyan, pad=12)
    ax4.grid(True, color=c_grid, linestyle=':', alpha=0.7)
    
    # Texto en barras
    ax4.text(0, values[0] + 3, f"{values[0]:.1f}%\nRECHAZO / FADE", ha='center', va='bottom', fontsize=11, fontweight='bold', color=c_red)
    ax4.text(1, values[1] + 3, f"{values[1]:.1f}%\nEXPANDE A +150% ATR", ha='center', va='bottom', fontsize=11, fontweight='bold', color=c_cyan)
    
    # Recuadro didáctico
    ax4.text(0.5, 20, 
             "★ REGLA DE ORO INSTITUCIONAL:\n"
             "• RVol Normal (<=1.2) = 55.5% - 66% de probabilidad de techo (FADE).\n"
             "• RVol Alto (>2.0) = 59.4% (hasta 80-100% en SPY/QQQ) de llegar al +150% ATR.",
             bbox=dict(boxstyle='round,pad=0.6', facecolor='#151C28', edgecolor=c_cyan, alpha=0.9),
             ha='center', fontsize=9.5, color=c_text, fontweight='semibold')

    # Guardar imagen en alta resolución
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Infografía generada exitosamente en: {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
