"""
TradingVolt • Script de Integración de la Vista Intraday Strength Watch
Agrega intraday_strength_engine a app.py con el gráfico interactivo, tabla con pre/post market y bubble map multidimensional.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_PATH = r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\app.py"

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. IMPORTAR INTRADAY_STRENGTH_ENGINE
import_hook = """try:
    import industry_ranks_engine as ire
    importlib.reload(ire)
except ImportError:
    ire = None"""

import_new = """try:
    import industry_ranks_engine as ire
    importlib.reload(ire)
except ImportError:
    ire = None
try:
    import intraday_strength_engine as ise
    importlib.reload(ise)
except ImportError:
    ise = None"""

if import_hook in code and "intraday_strength_engine" not in code:
    code = code.replace(import_hook, import_new, 1)
    print("✅ intraday_strength_engine importado.")

# 2. AGREGAR A LA NAVEGACIÓN EN SIDEBAR
nav_target = """            "🏆 Industry Rank Tables (Sectores & Grupos)"
        ],"""

nav_repl = """            "🏆 Industry Rank Tables (Sectores & Grupos)",
            "⚡ Intraday Strength Watch (Bubble Map)"
        ],"""

if "Intraday Strength Watch" not in code:
    if nav_target in code:
        code = code.replace(nav_target, nav_repl, 1)
    else:
        nav_target_crlf = nav_target.replace("\n", "\r\n")
        nav_repl_crlf = nav_repl.replace("\n", "\r\n")
        code = code.replace(nav_target_crlf, nav_repl_crlf, 1)
    print("✅ Opción Intraday Strength Watch agregada al menú.")

# 3. CÓDIGO DE LA VISTA INTRADAY STRENGTH WATCH
intraday_view_code = '''

# =========================================================================
# VISTA: INTRADAY STRENGTH WATCH (BUBBLE MAP & TABLA PRE/POST MARKET)
# =========================================================================
elif "Intraday Strength" in nav_view:
    st.markdown('<div class="brand-title">⚡ Intraday Strength Watch &amp; Bubble Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">FUERZA INTRADÍA • BUBBLE MAP MULTIDIMENSIONAL • PRE/POST MARKET FLOW • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "intra_tf" not in st.session_state:
        st.session_state["intra_tf"] = "1D"
    if "intra_active_ticker" not in st.session_state:
        st.session_state["intra_active_ticker"] = "AAUC"
    if "intra_active_name" not in st.session_state:
        st.session_state["intra_active_name"] = "Allied Gold Corporation"
    if "intra_active_sector" not in st.session_state:
        st.session_state["intra_active_sector"] = "Materials • Gold Mining"

    col_intra_left, col_intra_right = st.columns([1.1, 1.25], gap="medium")

    # ----------------- PANEL IZQUIERDO: GRÁFICO SUPERIOR + TABLA INFERIOR -----------------
    with col_intra_left:
        # 1. Gráfico Multi-Temporalidad del activo activo
        cur_t = st.session_state["intra_active_ticker"]
        cur_n = st.session_state["intra_active_name"]
        cur_s = st.session_state["intra_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_intra_tf_{tf}", use_container_width=True):
                    st.session_state["intra_tf"] = tf
                    st.rerun()

        fig_intra = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["intra_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_intra, use_container_width=True, config={"displayModeBar": True})

        st.markdown("<hr style='margin:10px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        # 2. Filtros y Organización de la Tabla Inferior
        tf1, tf2, tf3 = st.columns([1.5, 1.3, 1.3])
        with tf1:
            q_search = st.text_input("🔍 Buscar activo:", placeholder="Ej: RHI, CART, ZS...", label_visibility="collapsed")
        with tf2:
            sec_opts = ["All", "Energy", "Information Technology", "Financials", "Industrials", "Health Care", "Real Estate", "Consumer Discretionary", "Consumer Staples", "Materials"]
            sel_sec_filt = st.selectbox("Sector:", sec_opts, index=0, label_visibility="collapsed")
        with tf3:
            metric_sort_opts = {
                "chg_today": "Price % Change Today",
                "chg_from_open": "Price % Change from Open",
                "rvol_20d": "Relative Volume - 20 Day",
                "run_rate_20d": "Run Rate 20d (%)",
                "pre_mkt_gap": "Pre Market Gap %",
                "dollar_vol_m": "Volume in Dollars ($M)"
            }
            sel_sort = st.selectbox("Ordenar:", list(metric_sort_opts.keys()), format_func=lambda x: metric_sort_opts[x], index=0, label_visibility="collapsed")

        df_intra = ise.get_intraday_dataframe(
            sector_filter=sel_sec_filt,
            search_query=q_search,
            sort_by=sel_sort,
            ascending=False
        )

        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:12px; font-weight:bold; color:#F8FAFC;">Deepvue Universe ({len(df_intra)} activos encontrados)</span>
                <span style="font-size:11px; color:#94A3B8;">Haz clic en un ticker para seleccionarlo</span>
            </div>
        """, unsafe_allow_html=True)

        # Encabezados de la tabla con pre/post market stats
        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 10px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:1.2;">SYMBOL</span>
                <span style="flex:2.0;">INDUSTRY</span>
                <span style="flex:1.0; text-align:right;">CHG HOY</span>
                <span style="flex:1.0; text-align:right;">VS OPEN</span>
                <span style="flex:0.9; text-align:right;">RVOL</span>
                <span style="flex:1.1; text-align:right;">RUN RATE</span>
                <span style="flex:1.0; text-align:right;">PRE GAP</span>
            </div>
        """, unsafe_allow_html=True)

        # Filas de la tabla
        for _, row in df_intra.iterrows():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 2.0, 1.0, 1.0, 0.9, 1.1, 1.0])
            with c1:
                is_active = (st.session_state["intra_active_ticker"] == row["symbol"])
                btn_txt = f"👉 **{row['symbol']}**" if is_active else row["symbol"]
                if st.button(btn_txt, key=f"intra_row_{row['symbol']}", use_container_width=True):
                    st.session_state["intra_active_ticker"] = row["symbol"]
                    st.session_state["intra_active_name"] = row["name"]
                    st.session_state["intra_active_sector"] = f"{row['sector']} • {row['industry']}"
                    st.rerun()
            with c2:
                st.markdown(f"<div style='font-size:11px; color:#E2E8F0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{row['industry']}</div>", unsafe_allow_html=True)
            with c3:
                ct_col = "#10B981" if row["chg_today"] >= 0 else "#EF4444"
                st.markdown(f"<div style='font-size:11px; font-weight:bold; color:{ct_col}; text-align:right;'>{row['chg_today']:+.2f}%</div>", unsafe_allow_html=True)
            with c4:
                co_col = "#10B981" if row["chg_from_open"] >= 0 else "#EF4444"
                st.markdown(f"<div style='font-size:11px; color:{co_col}; text-align:right;'>{row['chg_from_open']:+.2f}%</div>", unsafe_allow_html=True)
            with c5:
                st.markdown(f"<div style='font-size:11px; color:#38BDF8; font-weight:bold; text-align:right;'>{row['rvol_20d']:.1f}x</div>", unsafe_allow_html=True)
            with c6:
                st.markdown(f"<div style='font-size:11px; color:#94A3B8; text-align:right;'>{row['run_rate_20d']:.1f}%</div>", unsafe_allow_html=True)
            with c7:
                pg_col = "#10B981" if row["pre_mkt_gap"] >= 0 else "#EF4444"
                st.markdown(f"<div style='font-size:11px; color:{pg_col}; text-align:right;'>{row['pre_mkt_gap']:+.2f}%</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:1px 0 2px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    # ----------------- PANEL DERECHO: BUBBLE MAP MULTIDIMENSIONAL -----------------
    with col_intra_right:
        # Selector de Ejes y Tamaño idéntico a Deepvue
        st.markdown("<div style='font-size:14px; font-weight:bold; color:#F8FAFC; margin-bottom:8px;'>🌐 Bubble Map Cuantitativo</div>", unsafe_allow_html=True)
        
        bc1, bc2, bc3 = st.columns([1.3, 1.3, 1.3])
        with bc1:
            x_axis_choice = st.selectbox(
                "Eje X (Horizontal):",
                ["chg_from_open", "chg_today", "pct_from_vwap", "pre_mkt_gap", "rs_1m"],
                format_func=lambda x: ise.METRIC_LABELS.get(x, x),
                index=0
            )
        with bc2:
            y_axis_choice = st.selectbox(
                "Eje Y (Vertical):",
                ["chg_today", "chg_from_open", "pct_from_vwap", "pre_mkt_gap", "rs_1m", "rs_3m"],
                format_func=lambda x: ise.METRIC_LABELS.get(x, x),
                index=0
            )
        with bc3:
            size_choice = st.selectbox(
                "Tamaño de Burbuja:",
                ["rvol_20d", "run_rate_20d", "dollar_vol_m"],
                format_func=lambda x: ise.METRIC_LABELS.get(x, x),
                index=0
            )

        # Renderizar Bubble Map
        fig_bubble = ise.render_intraday_bubble_map(
            df_intra,
            x_metric=x_axis_choice,
            y_metric=y_axis_choice,
            size_metric=size_choice
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": True})

        # Leyenda Cuantitativa de los Cuadrantes
        st.markdown("""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:11px; line-height:1.6; color:#94A3B8;">
                <strong style="color:#38BDF8;">Cómo leer los 4 Cuadrantes:</strong><br>
                ● <strong style="color:#60A5FA;">Superior Derecho (Líderes Intradía):</strong> Apertura positiva y empuje alcista sostenido por encima del precio de apertura.<br>
                ● <strong style="color:#93C5FD;">Superior Izquierdo (Reversión Alcista):</strong> Abrió negativo / gap bajista pero los compradores institucionales absorbieron el float.<br>
                ● <strong style="color:#F472B6;">Inferior Izquierdo (Debilidad Severa):</strong> Apertura en rojo y continuación vendedora a la baja (evitar largos).<br>
                ● <strong style="color:#FB7185;">Inferior Derecho (Fading Gappers):</strong> Subió en pre-mercado pero se desplomó por debajo de la apertura (típica trampa de toros).
            </div>
        """, unsafe_allow_html=True)
'''

if "VISTA: INTRADAY STRENGTH WATCH" not in code:
    code = code + intraday_view_code
    print("✅ Código de Intraday Strength Watch agregado.")

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("🎯 Integración de Intraday Strength Watch completada con éxito.")
