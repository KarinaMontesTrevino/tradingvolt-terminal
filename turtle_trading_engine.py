"""
turtle_trading_engine.py
========================
Motor cuantitativo canónico de la Estrategia de las Tortugas (Richard Dennis & William Eckhardt).
Implementa con exactitud matemática:
1. Volatilidad N (Wilder's ATR 20).
2. Canales Donchian sin lookahead bias (20/10 para S1, 55/20 para S2).
3. Dimensionamiento por Volatilidad: 1 Unidad = (1% Equity) / N.
4. Piramidación estricta: +1 unidad cada +0.5N (máx 4 unidades).
5. Stop Loss de 2N desde la última entrada para TODAS las unidades.
6. Salidas Donchian (10 días para S1, 20 días para S2) o ejecución de Stop Loss.
7. Gráficos interactivos en Plotly con marcas explícitas de entrada, piramidación, stops y salidas.
"""

import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

STUDIES_DIR = os.path.dirname(os.path.abspath(__file__))
STUDY_DB_PATH = os.path.join(STUDIES_DIR, "turtle_backtest_summary.json")

def load_market_ohlcv(symbol: str, period: str = "5y") -> pd.DataFrame:
    """Descarga cotizaciones históricas limpias para el backtest."""
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period=period, interval="1d", auto_adjust=True)
    except Exception:
        df = pd.DataFrame()

    if df is None or df.empty:
        try:
            df = yf.download(symbol, period=period, interval="1d", progress=False, threads=False, auto_adjust=True)
        except Exception:
            df = pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna(subset=['Close'])
    df = df[df['Close'] > 0]
    return df

def calculate_n(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Calcula N (Wilder's ATR 20) según las reglas canónicas de las Tortugas."""
    high = df['High']
    low = df['Low']
    prev_close = df['Close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Wilder's smoothing
    n = tr.ewm(alpha=1.0/period, adjust=False).mean()
    return n

def simulate_turtle_trades(
    df: pd.DataFrame, 
    system: int = 2,
    mode: str = "LONG_AND_SHORT",
    risk_pct_per_unit: float = 0.01,
    max_units: int = 4,
    initial_equity: float = 100000.0,
    pyramid_step: float = 0.5
):
    """
    Ejecuta la simulación barra a barra con registro completo de eventos
    (entradas, piramidación, stops y salidas).
    """
    if len(df) < 65:
        return None, None, None, {}

    entry_window = 20 if system == 1 else 55
    exit_window = 10 if system == 1 else 20
    allow_short = (mode == "LONG_AND_SHORT")

    df = df.copy()
    df['N'] = calculate_n(df, 20)
    df['Upper_Entry'] = df['High'].shift(1).rolling(entry_window).max()
    df['Lower_Entry'] = df['Low'].shift(1).rolling(entry_window).min()
    df['Upper_Exit'] = df['High'].shift(1).rolling(exit_window).max()
    df['Lower_Exit'] = df['Low'].shift(1).rolling(exit_window).min()

    equity = initial_equity
    equity_curve = []
    trades = []
    actions = [] # Registra eventos visuales para el gráfico

    pos_dir = 0
    units = []

    dates = df.index
    opens = df['Open'].values
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values
    upper_e = df['Upper_Entry'].values
    lower_e = df['Lower_Entry'].values
    upper_x = df['Upper_Exit'].values
    lower_x = df['Lower_Exit'].values
    n_vals = df['N'].values

    # Series para registrar trazas en el gráfico
    stop_lines = [np.nan] * len(df)
    unit_counts = [0] * len(df)

    for i in range(entry_window + 1, len(df)):
        dt = dates[i]
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        n_val = n_vals[i-1]
        if np.isnan(n_val) or n_val <= 0:
            equity_curve.append({'Date': dt, 'Equity': equity, 'Pos': 0})
            continue

        # 1. Gestionar posición abierta existente
        if pos_dir != 0:
            total_shares = sum(u['shares'] for u in units)
            last_entry_p = units[-1]['price']
            stop_price = units[-1]['stop']
            stopped_out = False
            exit_reason = ""
            exit_price = 0.0

            if pos_dir == 1: # Long
                if l <= stop_price:
                    stopped_out = True
                    exit_price = min(o, stop_price)
                    exit_reason = "STOP_LOSS_2N"
                elif l <= lower_x[i]:
                    stopped_out = True
                    exit_price = min(o, lower_x[i])
                    exit_reason = "DONCHIAN_EXIT"
            elif pos_dir == -1: # Short
                if h >= stop_price:
                    stopped_out = True
                    exit_price = max(o, stop_price)
                    exit_reason = "STOP_LOSS_2N"
                elif h >= upper_x[i]:
                    stopped_out = True
                    exit_price = max(o, upper_x[i])
                    exit_reason = "DONCHIAN_EXIT"

            if stopped_out:
                pnl = sum((exit_price - u['price']) * u['shares'] if pos_dir == 1 else (u['price'] - exit_price) * u['shares'] for u in units)
                ret_pct = pnl / equity
                trades.append({
                    'Entry_Date': str(units[0]['date'])[:10],
                    'Exit_Date': str(dt)[:10],
                    'Direction': 'LONG' if pos_dir == 1 else 'SHORT',
                    'Units': len(units),
                    'Avg_Entry': round(sum(u['price'] * u['shares'] for u in units) / total_shares, 2),
                    'Exit_Price': round(exit_price, 2),
                    'PnL': round(pnl, 2),
                    'Return_Pct': round(ret_pct * 100.0, 2),
                    'Exit_Reason': exit_reason
                })
                actions.append({
                    'date': dt,
                    'type': 'EXIT',
                    'reason': exit_reason,
                    'price': exit_price,
                    'direction': 'LONG' if pos_dir == 1 else 'SHORT',
                    'pnl': pnl
                })
                equity += pnl
                pos_dir = 0
                units = []
            else:
                # 2. Piramidación: ¿Añadir unidades cada +0.5N?
                if len(units) < max_units:
                    if pos_dir == 1 and h >= last_entry_p + pyramid_step * n_val:
                        add_price = max(o, last_entry_p + pyramid_step * n_val)
                        unit_risk = risk_pct_per_unit * equity
                        shares = max(int(unit_risk / (n_val + 1e-9)), 1)
                        new_stop = add_price - 2.0 * n_val
                        for u in units:
                            u['stop'] = new_stop
                        unit_num = len(units) + 1
                        units.append({'date': dt, 'price': add_price, 'shares': shares, 'stop': new_stop})
                        actions.append({
                            'date': dt,
                            'type': f'PYRAMID_U{unit_num}',
                            'price': add_price,
                            'direction': 'LONG',
                            'stop': new_stop
                        })
                    elif pos_dir == -1 and l <= last_entry_p - pyramid_step * n_val:
                        add_price = min(o, last_entry_p - pyramid_step * n_val)
                        unit_risk = risk_pct_per_unit * equity
                        shares = max(int(unit_risk / (n_val + 1e-9)), 1)
                        new_stop = add_price + 2.0 * n_val
                        for u in units:
                            u['stop'] = new_stop
                        unit_num = len(units) + 1
                        units.append({'date': dt, 'price': add_price, 'shares': shares, 'stop': new_stop})
                        actions.append({
                            'date': dt,
                            'type': f'PYRAMID_U{unit_num}',
                            'price': add_price,
                            'direction': 'SHORT',
                            'stop': new_stop
                        })

        # 3. Nueva entrada si estamos Flat
        if pos_dir == 0:
            if h > upper_e[i]:
                entry_p = max(o, upper_e[i])
                unit_risk = risk_pct_per_unit * equity
                shares = max(int(unit_risk / (n_val + 1e-9)), 1)
                stop_p = entry_p - 2.0 * n_val
                pos_dir = 1
                units = [{'date': dt, 'price': entry_p, 'shares': shares, 'stop': stop_p}]
                actions.append({
                    'date': dt,
                    'type': 'ENTRY_U1',
                    'price': entry_p,
                    'direction': 'LONG',
                    'stop': stop_p
                })
            elif allow_short and l < lower_e[i]:
                entry_p = min(o, lower_e[i])
                unit_risk = risk_pct_per_unit * equity
                shares = max(int(unit_risk / (n_val + 1e-9)), 1)
                stop_p = entry_p + 2.0 * n_val
                pos_dir = -1
                units = [{'date': dt, 'price': entry_p, 'shares': shares, 'stop': stop_p}]
                actions.append({
                    'date': dt,
                    'type': 'ENTRY_U1',
                    'price': entry_p,
                    'direction': 'SHORT',
                    'stop': stop_p
                })

        if units:
            stop_lines[i] = units[-1]['stop']
            unit_counts[i] = len(units) * pos_dir

        # Mark-to-market equity
        unrealized = 0.0
        if pos_dir != 0:
            unrealized = sum((c - u['price']) * u['shares'] if pos_dir == 1 else (u['price'] - c) * u['shares'] for u in units)

        equity_curve.append({
            'Date': dt,
            'Equity': equity + unrealized,
            'Units': len(units) * pos_dir
        })

    df['Stop_Line'] = stop_lines
    df['Unit_Count'] = unit_counts

    eq_df = pd.DataFrame(equity_curve).set_index('Date')
    trades_df = pd.DataFrame(trades)
    metrics = compute_metrics(eq_df, trades_df)

    return df, eq_df, trades_df, actions, metrics

def compute_metrics(eq_df: pd.DataFrame, trades_df: pd.DataFrame):
    if eq_df is None or eq_df.empty:
        return {}

    equity = eq_df['Equity']
    total_days = (equity.index[-1] - equity.index[0]).days
    years = max(total_days / 365.25, 0.1)

    initial_eq = equity.iloc[0]
    final_eq = equity.iloc[-1]
    total_ret = (final_eq / initial_eq) - 1.0
    cagr = ((final_eq / initial_eq) ** (1.0 / years)) - 1.0

    daily_rets = equity.pct_change().dropna()
    mean_ret = daily_rets.mean() * 252
    vol = daily_rets.std() * np.sqrt(252)
    sharpe = (mean_ret - 0.02) / (vol + 1e-9) if vol > 0 else 0.0

    cummax = equity.cummax()
    drawdown = (equity - cummax) / cummax
    max_dd = drawdown.min()
    calmar = cagr / abs(max_dd) if abs(max_dd) > 0 else 0.0

    win_rate = 0.0
    profit_factor = 0.0
    total_trades = 0
    win_loss_ratio = 0.0
    avg_win = 0.0
    avg_loss = 0.0

    if trades_df is not None and not trades_df.empty:
        total_trades = len(trades_df)
        wins = trades_df[trades_df['PnL'] > 0]
        losses = trades_df[trades_df['PnL'] < 0]
        win_rate = (len(wins) / total_trades) * 100.0 if total_trades > 0 else 0.0
        gross_profit = wins['PnL'].sum()
        gross_loss = abs(losses['PnL'].sum())
        profit_factor = gross_profit / (gross_loss + 1e-9) if gross_loss > 0 else 999.0
        avg_win = wins['PnL'].mean() if len(wins) > 0 else 0.0
        avg_loss = abs(losses['PnL'].mean()) if len(losses) > 0 else 0.0
        win_loss_ratio = avg_win / (avg_loss + 1e-9) if avg_loss > 0 else 0.0

    return {
        'Total_Return_Pct': round(total_ret * 100.0, 2),
        'CAGR_Pct': round(cagr * 100.0, 2),
        'Annualized_Vol_Pct': round(vol * 100.0, 2),
        'Sharpe_Ratio': round(sharpe, 2),
        'Max_Drawdown_Pct': round(max_dd * 100.0, 2),
        'Calmar_Ratio': round(calmar, 2),
        'Total_Trades': total_trades,
        'Win_Rate_Pct': round(win_rate, 2),
        'Profit_Factor': round(profit_factor, 2),
        'Avg_Win': round(avg_win, 2),
        'Avg_Loss': round(avg_loss, 2),
        'Win_Loss_Ratio': round(win_loss_ratio, 2)
    }

def build_turtle_chart(df: pd.DataFrame, actions: list, symbol: str = "GC=F", title_extra: str = "") -> go.Figure:
    """Construye el gráfico interactivo de alta precisión con entradas, pirámide y stops."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.68, 0.16, 0.16],
        subplot_titles=None
    )

    x_dates = df.index

    # 1. Velas Japonesas
    fig.add_trace(go.Candlestick(
        x=x_dates,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Precio",
        increasing_line_color='#00FF87',
        decreasing_line_color='#FF2E63',
        increasing_fillcolor='#00FF87',
        decreasing_fillcolor='#FF2E63'
    ), row=1, col=1)

    # 2. Canales Donchian de Entrada y Salida
    fig.add_trace(go.Scatter(
        x=x_dates, y=df['Upper_Entry'],
        line=dict(color='#00F0FF', width=1.4, dash='dash'),
        name="Donchian Breakout Alto (Entrada Long)"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x_dates, y=df['Lower_Entry'],
        line=dict(color='#F43F5E', width=1.4, dash='dash'),
        name="Donchian Breakout Bajo (Entrada Short)"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x_dates, y=df['Lower_Exit'],
        line=dict(color='#EAB308', width=1.0, dash='dot'),
        name="Canal Salida Long"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x_dates, y=df['Upper_Exit'],
        line=dict(color='#A855F7', width=1.0, dash='dot'),
        name="Canal Salida Short"
    ), row=1, col=1)

    # 3. Línea Dinámica de Stop Loss (2N)
    fig.add_trace(go.Scatter(
        x=x_dates, y=df['Stop_Line'],
        mode='lines',
        line=dict(color='#EF4444', width=2.0),
        name="🛑 Stop Loss (2N)",
        connectgaps=False
    ), row=1, col=1)

    # 4. Marcadores de Eventos (Entrada U1, Piramidación U2/U3/U4, Salidas)
    entry_dates, entry_prices, entry_texts = [], [], []
    pyramid_dates, pyramid_prices, pyramid_texts = [], [], []
    exit_dates, exit_prices, exit_texts, exit_colors = [], [], [], []

    for act in actions:
        dt = act['date']
        px = act['price']
        atype = act['type']
        
        if atype == 'ENTRY_U1':
            entry_dates.append(dt)
            entry_prices.append(px)
            entry_texts.append(f"🟢 ENTRY U1 ({act['direction']})<br>${px:.2f}")
        elif 'PYRAMID' in atype:
            pyramid_dates.append(dt)
            pyramid_prices.append(px)
            pyramid_texts.append(f"🔵 +{atype[-2:]} (+0.5N)<br>${px:.2f}")
        elif atype == 'EXIT':
            exit_dates.append(dt)
            exit_prices.append(px)
            pnl_c = "#00FF87" if act['pnl'] >= 0 else "#FF2E63"
            exit_colors.append(pnl_c)
            exit_texts.append(f"🔻 EXIT: {act['reason']}<br>${px:.2f} ({'+' if act['pnl']>=0 else ''}${act['pnl']:,.0f})")

    if entry_dates:
        fig.add_trace(go.Scatter(
            x=entry_dates, y=entry_prices,
            mode='markers+text',
            marker=dict(symbol='triangle-up', size=13, color='#00FF87', line=dict(color='#FFFFFF', width=1)),
            text=[t.split('<br>')[0] for t in entry_texts],
            textposition='top center',
            textfont=dict(size=10, color='#00FF87'),
            name="🟢 Entrada Unidad 1 (Breakout)",
            hovertext=entry_texts,
            hoverinfo='text'
        ), row=1, col=1)

    if pyramid_dates:
        fig.add_trace(go.Scatter(
            x=pyramid_dates, y=pyramid_prices,
            mode='markers+text',
            marker=dict(symbol='diamond', size=11, color='#38BDF8', line=dict(color='#FFFFFF', width=1)),
            text=[t.split('<br>')[0] for t in pyramid_texts],
            textposition='top center',
            textfont=dict(size=9, color='#38BDF8'),
            name="🔵 Piramidación (+0.5N)",
            hovertext=pyramid_texts,
            hoverinfo='text'
        ), row=1, col=1)

    if exit_dates:
        fig.add_trace(go.Scatter(
            x=exit_dates, y=exit_prices,
            mode='markers+text',
            marker=dict(symbol='x', size=12, color=exit_colors, line=dict(width=2)),
            text=["EXIT" for _ in exit_texts],
            textposition='bottom center',
            textfont=dict(size=9, color='#F8FAFC'),
            name="🔻 Salida (Stop 2N o Donchian)",
            hovertext=exit_texts,
            hoverinfo='text'
        ), row=1, col=1)

    # Panel 2: Volatilidad N (Wilder ATR 20)
    fig.add_trace(go.Scatter(
        x=x_dates, y=df['N'],
        line=dict(color='#A855F7', width=1.5),
        name="Volatilidad N (ATR 20)"
    ), row=2, col=1)

    # Panel 3: Número de Unidades en Posición (0 a 4)
    bar_cols = ['#00FF87' if u > 0 else ('#FF2E63' if u < 0 else '#64748B') for u in df['Unit_Count']]
    fig.add_trace(go.Bar(
        x=x_dates, y=df['Unit_Count'],
        marker_color=bar_cols,
        name="Unidades en Cartera (Max 4)"
    ), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=720,
        margin=dict(l=10, r=45, t=35, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
        title=dict(text=f"<b>🐢 SISTEMA DE LAS TORTUGAS • {symbol}</b> {title_extra}", font=dict(size=14, color="#E2E8F0"))
    )

    fig.update_xaxes(showgrid=True, gridcolor="#1A2234", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#1A2234", zeroline=False, side="right")

    return fig

def get_study_database() -> dict:
    """Carga la base de datos de estudios precompilados de las Tortugas."""
    if os.path.exists(STUDY_DB_PATH):
        try:
            with open(STUDY_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}
