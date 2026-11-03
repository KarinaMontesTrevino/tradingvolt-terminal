"""
TradingVolt - Monte Carlo Simulation Engine
Simulación estocástica institucional de trayectorias (Geometric Brownian Motion & Portafolios Correlacionados)
Especializado en Las 7 Magníficas, Líderes de Semiconductores e Infraestructura de IA.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Canasta de activos líderes solicitados
DEFAULT_TICKERS = {
    "Las 7 Magníficas": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
    "Semis & AI Hardware": ["NVDA", "TSM", "ASML", "AMD", "MRVL", "ALAB", "LITE", "SKHY"],
    "AI Neocloud & Hyperscalers": ["CRWV", "NBIS", "MSFT", "AMZN", "GOOGL", "META"],
    "Todos los 18 Líderes": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "AMD", "MRVL", "TSM", "ASML", "ALAB", "LITE",
        "SKHY", "CRWV", "NBIS", "SPCX", "BRKR"
    ]
}

TICKER_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc.",
    "TSLA": "Tesla, Inc.",
    "AMD": "Advanced Micro Devices",
    "MRVL": "Marvell Technology",
    "TSM": "Taiwan Semiconductor",
    "ASML": "ASML Holding N.V.",
    "ALAB": "Astera Labs, Inc.",
    "LITE": "Lumentum Holdings",
    "SKHY": "SK hynix Inc.",
    "CRWV": "CoreWeave, Inc.",
    "NBIS": "Nebius Group N.V.",
    "SPCX": "Space Exploration ETF",
    "BRKR": "Bruker Corporation"
}


def fetch_historical_prices(tickers: list, period: str = "1y") -> pd.DataFrame:
    """
    Descarga histórico de precios de cierre ajustados para los tickers seleccionados.
    """
    clean_tickers = [t.strip().upper() for t in tickers if t.strip()]
    if not clean_tickers:
        return pd.DataFrame()

    try:
        data = yf.download(clean_tickers, period=period, progress=False, threads=False)
        if data.empty:
            return pd.DataFrame()
        
        if "Close" in data.columns:
            closes = data["Close"]
        else:
            closes = data

        if isinstance(closes, pd.Series):
            closes = closes.to_frame(name=clean_tickers[0])
            
        # Limpiar columnas vacías
        closes = closes.dropna(how="all", axis=1)
        closes = closes.ffill().bfill()
        return closes
    except Exception as e:
        print(f"Error descargando datos para Monte Carlo: {e}")
        return pd.DataFrame()


def run_single_asset_monte_carlo(
    s0: float,
    mu: float,
    sigma: float,
    days: int = 60,
    n_sims: int = 5000,
    drift_mode: str = "historical", # "historical", "risk_free", "neutral"
    risk_free_rate: float = 0.045
) -> dict:
    """
    Simulación Geometric Brownian Motion (GBM) para un activo individual.
    dS_t = mu * S_t * dt + sigma * S_t * dW_t
    Solución exacta: S_t = S_0 * exp((drift) * t + sigma * sqrt(t) * Z)
    """
    dt = 1.0 / 252.0  # Paso diario
    
    if drift_mode == "risk_free":
        daily_drift = (risk_free_rate - 0.5 * (sigma ** 2)) * dt
    elif drift_mode == "neutral":
        daily_drift = (-0.5 * (sigma ** 2)) * dt  # Drift cero
    else:
        # Drift empírico
        daily_drift = (mu - 0.5 * (sigma ** 2)) * dt

    daily_vol = sigma * np.sqrt(dt)

    # Matriz completa de simulación: (días + 1, n_sims)
    # Para visualización de trayectorias (spaghetti)
    random_shocks = np.random.standard_normal((days, n_sims))
    price_paths = np.zeros((days + 1, n_sims))
    price_paths[0] = s0

    for t in range(1, days + 1):
        price_paths[t] = price_paths[t - 1] * np.exp(daily_drift + daily_vol * random_shocks[t - 1])

    final_prices = price_paths[-1]
    returns = (final_prices - s0) / s0

    # Percentiles
    p5 = float(np.percentile(final_prices, 5))
    p10 = float(np.percentile(final_prices, 10))
    p25 = float(np.percentile(final_prices, 25))
    p50 = float(np.percentile(final_prices, 50))
    p75 = float(np.percentile(final_prices, 75))
    p90 = float(np.percentile(final_prices, 90))
    p95 = float(np.percentile(final_prices, 95))

    # Métricas de Riesgo
    var_95_pct = float((s0 - p5) / s0 * 100.0)
    var_99_val = float(np.percentile(final_prices, 1))
    var_99_pct = float((s0 - var_99_val) / s0 * 100.0)
    
    # Conditional VaR (Expected Shortfall) debajo del percentil 5
    tail_losses = returns[returns <= (p5 - s0) / s0]
    cvar_95_pct = float(np.abs(np.mean(tail_losses)) * 100.0) if len(tail_losses) > 0 else var_95_pct

    prob_profit = float(np.mean(returns > 0) * 100.0)
    prob_gain_20 = float(np.mean(returns > 0.20) * 100.0)
    prob_drop_20 = float(np.mean(returns < -0.20) * 100.0)

    return {
        "s0": s0,
        "days": days,
        "n_sims": n_sims,
        "mu_annual": mu,
        "sigma_annual": sigma,
        "price_paths": price_paths,
        "final_prices": final_prices,
        "returns": returns,
        "p5": p5,
        "p10": p10,
        "p25": p25,
        "p50": p50,
        "p75": p75,
        "p90": p90,
        "p95": p95,
        "median_return": float((p50 - s0) / s0 * 100.0),
        "mean_return": float(np.mean(returns) * 100.0),
        "var_95_pct": var_95_pct,
        "var_99_pct": var_99_pct,
        "cvar_95_pct": cvar_95_pct,
        "prob_profit": prob_profit,
        "prob_gain_20": prob_gain_20,
        "prob_drop_20": prob_drop_20
    }


def run_batch_monte_carlo(
    prices_df: pd.DataFrame,
    days: int = 60,
    n_sims: int = 5000,
    drift_mode: str = "historical",
    risk_free_rate: float = 0.045
) -> dict:
    """
    Ejecuta simulaciones para todos los activos y calcula además la matriz de correlación.
    """
    if prices_df.empty:
        return {}

    returns_df = prices_df.pct_change().dropna()
    results = {}
    summary_rows = []

    corr_matrix = returns_df.corr()

    for ticker in prices_df.columns:
        series = prices_df[ticker].dropna()
        if len(series) < 20:
            continue
        
        s0 = float(series.iloc[-1])
        ret_series = returns_df[ticker].dropna()
        
        daily_mu = float(ret_series.mean())
        daily_sigma = float(ret_series.std())
        
        ann_mu = float(daily_mu * 252.0)
        ann_sigma = float(daily_sigma * np.sqrt(252.0))

        sim = run_single_asset_monte_carlo(
            s0=s0,
            mu=ann_mu,
            sigma=ann_sigma,
            days=days,
            n_sims=n_sims,
            drift_mode=drift_mode,
            risk_free_rate=risk_free_rate
        )
        sim["ticker"] = ticker
        sim["name"] = TICKER_NAMES.get(ticker, ticker)
        results[ticker] = sim

        summary_rows.append({
            "Ticker": ticker,
            "Empresa": TICKER_NAMES.get(ticker, ticker),
            "Precio Actual": s0,
            "Volatilidad Anual": ann_sigma * 100.0,
            "Retorno Esperado (P50)": sim["median_return"],
            "Rango P5 (Crash 5%)": sim["p5"],
            "P50 (Mediana)": sim["p50"],
            "Rango P95 (Euforia)": sim["p95"],
            "VaR 95%": sim["var_95_pct"],
            "CVaR 95% (Tail Risk)": sim["cvar_95_pct"],
            "Prob. Ganancia": sim["prob_profit"],
            "Prob. Caída >20%": sim["prob_drop_20"]
        })

    summary_df = pd.DataFrame(summary_rows)
    return {
        "results": results,
        "summary_df": summary_df,
        "corr_matrix": corr_matrix,
        "days": days,
        "n_sims": n_sims,
        "drift_mode": drift_mode
    }


def create_spaghetti_fan_chart(sim_result: dict, ticker: str) -> go.Figure:
    """
    Crea gráfico de abanico con 80 trayectorias aleatorias transparentes
    más los conos de percentiles P5, P25, P50 (Mediana), P75 y P95.
    """
    paths = sim_result["price_paths"]
    days = sim_result["days"]
    s0 = sim_result["s0"]
    name = TICKER_NAMES.get(ticker, ticker)
    x_axis = np.arange(days + 1)

    fig = go.Figure()

    # 1. 80 trayectorias aleatorias finas de fondo
    sample_paths = np.random.choice(paths.shape[1], size=min(80, paths.shape[1]), replace=False)
    for idx in sample_paths:
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=paths[:, idx],
            mode="lines",
            line=dict(color="rgba(100, 116, 139, 0.12)", width=1),
            showlegend=False,
            hoverinfo="skip"
        ))

    # 2. Cono P5 - P95 (Banda de probabilidad del 90%)
    p5_line = np.percentile(paths, 5, axis=1)
    p25_line = np.percentile(paths, 25, axis=1)
    p50_line = np.percentile(paths, 50, axis=1)
    p75_line = np.percentile(paths, 75, axis=1)
    p95_line = np.percentile(paths, 95, axis=1)

    # Banda externa P5 a P95
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=p95_line,
        mode="lines",
        line=dict(color="rgba(0, 240, 255, 0.4)", width=1.5, dash="dash"),
        name="Percentil 95% (Alcista)",
        hoverinfo="y+name"
    ))
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=p5_line,
        mode="lines",
        line=dict(color="rgba(255, 75, 75, 0.4)", width=1.5, dash="dash"),
        name="Percentil 5% (VaR 95%)",
        fill="tonexty",
        fillcolor="rgba(0, 240, 255, 0.05)",
        hoverinfo="y+name"
    ))

    # Banda interna P25 a P75
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=p75_line,
        mode="lines",
        line=dict(color="rgba(0, 255, 135, 0.7)", width=1.5),
        name="Percentil 75%",
        hoverinfo="y+name"
    ))
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=p25_line,
        mode="lines",
        line=dict(color="rgba(255, 170, 0, 0.7)", width=1.5),
        name="Percentil 25%",
        fill="tonexty",
        fillcolor="rgba(0, 255, 135, 0.08)",
        hoverinfo="y+name"
    ))

    # Mediana P50
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=p50_line,
        mode="lines",
        line=dict(color="#00F0FF", width=3),
        name=f"Mediana P50: ${p50_line[-1]:.2f} ({sim_result['median_return']:+.1f}%)"
    ))

    # Línea base de precio inicial S0
    fig.add_hline(
        y=s0,
        line=dict(color="#FFFFFF", width=1.2, dash="dot"),
        annotation_text=f"Precio Inicial: ${s0:.2f}",
        annotation_position="top left",
        annotation_font=dict(color="#CBD5E1", size=11)
    )

    fig.update_layout(
        title=f"🎲 Cono de Dispersión Monte Carlo ({sim_result['n_sims']:,} sims, {days} días) • {ticker} ({name})",
        xaxis_title="Días de Proyección Hacia Adelante",
        yaxis_title="Precio Simulado (USD)",
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=480,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def create_distribution_histogram(sim_result: dict, ticker: str) -> go.Figure:
    """
    Histograma de densidad de rendimientos finales con VaR 95% y Median Return.
    """
    returns_pct = sim_result["returns"] * 100.0
    s0 = sim_result["s0"]
    name = TICKER_NAMES.get(ticker, ticker)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=returns_pct,
        nbinsx=80,
        histnorm="probability density",
        marker=dict(
            color="rgba(0, 240, 255, 0.65)",
            line=dict(color="#00F0FF", width=1)
        ),
        name="Distribución Rendimiento"
    ))

    # Línea de retorno 0%
    fig.add_vline(x=0.0, line=dict(color="#FFFFFF", width=1.5, dash="dash"), annotation_text="Breakeven 0%")

    # Línea de VaR 95%
    var_x = -sim_result["var_95_pct"]
    fig.add_vline(
        x=var_x,
        line=dict(color="#FF4B4B", width=2.5),
        annotation_text=f"VaR 95%: {var_x:.1f}%",
        annotation_position="top left",
        annotation_font=dict(color="#FF4B4B", size=12, family="JetBrains Mono")
    )

    # Línea de Mediana P50
    med_x = sim_result["median_return"]
    fig.add_vline(
        x=med_x,
        line=dict(color="#00FF87", width=2.5),
        annotation_text=f"Mediana: {med_x:+.1f}%",
        annotation_position="top right",
        annotation_font=dict(color="#00FF87", size=12, family="JetBrains Mono")
    )

    fig.update_layout(
        title=f"📊 Distribución de Probabilidad de Rendimiento Final • {ticker} ({sim_result['days']} días)",
        xaxis_title="Retorno Proyectado (%)",
        yaxis_title="Densidad",
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def create_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """
    Heatmap de correlación cruzada interactivo.
    """
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.index,
        colorscale=[
            [0.0, "#0B111E"],
            [0.3, "#1E293B"],
            [0.6, "#00A3FF"],
            [1.0, "#00FF87"]
        ],
        zmin=-0.2,
        zmax=1.0,
        text=np.round(corr_df.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=10, family="JetBrains Mono")
    ))

    fig.update_layout(
        title="🧬 Matriz de Correlación Cruzada Diaria (1 Año)",
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=520,
        margin=dict(l=60, r=40, t=50, b=50)
    )
    return fig
