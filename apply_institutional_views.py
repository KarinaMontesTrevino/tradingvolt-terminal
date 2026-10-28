"""
TradingVolt • Script de Integración de las 5 Vistas Institucionales Deepvue
Parchea app.py de forma robusta e idempotente.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_PATH = r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\app.py"

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. ACTUALIZAR IMPORTACIONES
import_hook = """try:
    import unusual_options_engine as uoe
    importlib.reload(uoe)
except ImportError:
    uoe = None"""

import_new = """try:
    import unusual_options_engine as uoe
    importlib.reload(uoe)
except ImportError:
    uoe = None
try:
    import earnings_calendar_engine as ece
    importlib.reload(ece)
except ImportError:
    ece = None
try:
    import new_highs_lows_engine as nhle
    importlib.reload(nhle)
except ImportError:
    nhle = None
try:
    import cot_positioning_engine as cpe
    importlib.reload(cpe)
except ImportError:
    cpe = None
try:
    import sentiment_intelligence_engine as sie
    importlib.reload(sie)
except ImportError:
    sie = None
try:
    import economic_calendar_engine as ecle
    importlib.reload(ecle)
except ImportError:
    ecle = None"""

if import_hook in code and "earnings_calendar_engine" not in code:
    code = code.replace(import_hook, import_new, 1)
    print("✅ Importaciones de los 5 motores agregadas.")
else:
    print("ℹ️ Importaciones ya presentes o no requeridas.")

# 2. ACTUALIZAR MENÚ DE NAVEGACIÓN EN SIDEBAR
nav_target = """            "🚨 Monitor LULD & Halts en Vivo"
        ],"""

nav_repl = """            "🚨 Monitor LULD & Halts en Vivo",
            "📅 Calendario de Earnings (Split Chart)",
            "📈 New Highs & New Lows (Breadth)",
            "📊 COT Positioning (Futures)",
            "🧠 NAAIM / AAII Sentiment Desk",
            "🌐 Calendario Económico"
        ],"""

if nav_target in code and "Calendario de Earnings" not in code:
    code = code.replace(nav_target, nav_repl, 1)
    print("✅ Menú lateral de navegación expandido con las 5 opciones.")
else:
    print("ℹ️ Opciones de navegación ya presentes.")

# 3. AGREGAR CÓDIGO DE LAS 5 VISTAS AL FINAL DE APP.PY
views_code = '''

# =========================================================================
# VISTA 1: CALENDARIO DE EARNINGS (SPLIT-SCREEN CON GRÁFICO MULTI-TEMPORALIDAD)
# =========================================================================
elif "Earnings" in nav_view:
    st.markdown('<div class="brand-title">📅 Calendario de Earnings & Multi-Timeframe Chart</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">ANÁLISIS INSTITUCIONAL DE RESULTADOS • SEMANA EN CURSO • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "earnings_tf" not in st.session_state:
        st.session_state["earnings_tf"] = "1D"
    if "earnings_active_ticker" not in st.session_state:
        st.session_state["earnings_active_ticker"] = "ADSE"
    if "earnings_active_name" not in st.session_state:
        st.session_state["earnings_active_name"] = "ADS-TEC Energy PLC"
    if "earnings_active_sector" not in st.session_state:
        st.session_state["earnings_active_sector"] = "Industrials • Machinery"

    col_cal, col_chart = st.columns([1.05, 1.35], gap="medium")

    with col_cal:
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#111827; padding:10px 14px; border-radius:8px; border:1px solid #1F2937; margin-bottom:12px;">
                <div style="font-weight:700; color:#F3F4F6; font-size:14px;">📅 &lt; Oct 19 - 25, 2026 &gt;</div>
                <div style="font-size:12px; color:#9CA3AF;"><span style="color:#10B981; font-weight:600;">84% Beats</span> | 297 Reportes Totales</div>
            </div>
        """, unsafe_allow_html=True)

        days_list = list(ece.EARNINGS_WEEK_DATA.keys())
        selected_day = st.radio("Día de la semana:", days_list, horizontal=True, label_visibility="collapsed", index=2)
        
        day_info = ece.EARNINGS_WEEK_DATA[selected_day]
        st.markdown(f"""
            <div style="background:rgba(30, 41, 59, 0.7); border:1px solid #334155; border-radius:6px; padding:8px 12px; margin-bottom:12px; display:flex; justify-content:space-between; font-size:12px;">
                <span><strong>REPORTED:</strong> {day_info['reported']}</span>
                <span><strong>EPS:</strong> <span style="color:#10B981;">{day_info['eps_growth']}</span></span>
                <span><strong>Sales:</strong> <span style="color:#10B981;">{day_info['sales_growth']}</span></span>
                <span><strong>Surprise:</strong> <span style="color:#10B981;">{day_info['surprise_pct']}</span></span>
            </div>
        """, unsafe_allow_html=True)

        filter_txt = st.text_input("🔍 Filtrar ticker o empresa:", placeholder="Ej: META, TSLA, NFLX...", label_visibility="collapsed").upper()

        tickers = day_info["tickers"]
        if filter_txt:
            tickers = [t for t in tickers if filter_txt in t["symbol"] or filter_txt in t["name"].upper()]

        if not tickers:
            st.info(f"No hay empresas reportando en {day_info['date_str']}.")
        else:
            st.caption(f"Mostrando {len(tickers)} empresas. Haz clic en un ticker para sincronizar el gráfico:")
            for t in tickers:
                c1, c2, c3, c4 = st.columns([1.1, 1.8, 1.3, 1.1])
                with c1:
                    is_active = (st.session_state["earnings_active_ticker"] == t["symbol"])
                    btn_label = f"👉 **{t['symbol']}**" if is_active else t["symbol"]
                    if st.button(btn_label, key=f"btn_earn_{t['symbol']}_{selected_day}", use_container_width=True):
                        st.session_state["earnings_active_ticker"] = t["symbol"]
                        st.session_state["earnings_active_name"] = t["name"]
                        st.session_state["earnings_active_sector"] = f"{t['sector']} • {t['time']}"
                        st.rerun()
                with c2:
                    st.markdown(f"<div style='font-size:12px; color:#E5E7EB; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{t['name']}</div>", unsafe_allow_html=True)
                with c3:
                    b_color = "#10B981" if t["type"] == "beat" else "#EF4444"
                    st.markdown(f"<div style='color:{b_color}; font-weight:700; font-size:12px;'>{t['result']}</div>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div style='color:#9CA3AF; font-size:11px;'>{t['eps']} vs {t['est']}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0; border:none; border-top:1px solid #1F2937;'>", unsafe_allow_html=True)

    with col_chart:
        cur_t = st.session_state["earnings_active_ticker"]
        cur_n = st.session_state["earnings_active_name"]
        cur_s = st.session_state["earnings_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_tf_{tf}", use_container_width=True):
                    st.session_state["earnings_tf"] = tf
                    st.rerun()

        fig_stock = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["earnings_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_stock, use_container_width=True, config={"displayModeBar": True})
        
        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(16, 185, 129, 0.15); color:#10B981; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Sincronizado en Vivo</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 2: NEW HIGHS & NEW LOWS (BREADTH & MULTI-TIMEFRAME CHART)
# =========================================================================
elif "New Highs" in nav_view:
    st.markdown('<div class="brand-title">📈 New Highs / New Lows & Multi-Timeframe Chart</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">AMPLITUD DE MERCADO • LÍDERES VS REZAGADOS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "nhnl_tf" not in st.session_state:
        st.session_state["nhnl_tf"] = "1D"
    if "nhnl_active_ticker" not in st.session_state:
        st.session_state["nhnl_active_ticker"] = "MAGH"
    if "nhnl_active_name" not in st.session_state:
        st.session_state["nhnl_active_name"] = "Magnitude International Ltd"
    if "nhnl_active_sector" not in st.session_state:
        st.session_state["nhnl_active_sector"] = "Industrials • Construction & Engineering"

    col_nhnl, col_nhnl_chart = st.columns([1.1, 1.3], gap="medium")

    with col_nhnl:
        # Barra de Amplitud de Mercado New Highs vs New Lows (idéntica a Deepvue)
        total_hl = nhle.NEW_HIGHS_TOTAL + nhle.NEW_LOWS_TOTAL
        pct_highs = (nhle.NEW_HIGHS_TOTAL / total_hl) * 100
        pct_lows = (nhle.NEW_LOWS_TOTAL / total_hl) * 100
        net_hl = nhle.NEW_HIGHS_TOTAL - nhle.NEW_LOWS_TOTAL

        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:bold; margin-bottom:6px;">
                    <span style="color:#38BDF8;">New Highs: {nhle.NEW_HIGHS_TOTAL} ({pct_highs:.1f}%)</span>
                    <span style="color:#94A3B8;">Net: <strong style="color:{'#22C55E' if net_hl >= 0 else '#EF4444'}">{net_hl:+d}</strong></span>
                    <span style="color:#F43F5E;">{nhle.NEW_LOWS_TOTAL} New Lows ({pct_lows:.1f}%)</span>
                </div>
                <div style="width:100%; height:12px; background:#1F2937; border-radius:6px; overflow:hidden; display:flex;">
                    <div style="width:{pct_highs}%; height:100%; background:#3B82F6;"></div>
                    <div style="width:{pct_lows}%; height:100%; background:#F43F5E;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_nh, tab_groups = st.tabs(["🏛️ Desglose por Sectores", "📊 Grupos Líderes vs Rezagados"])

        with tab_nh:
            view_type = st.radio("Mostrar:", ["🟢 New Highs (Máximos de 52 Semanas)", "🔴 New Lows (Mínimos de 52 Semanas)"], horizontal=True)
            if "New Highs" in view_type:
                for sector, data in nhle.NEW_HIGHS_BY_SECTOR.items():
                    with st.expander(f"🟢 **{sector}** — {data['count']} Highs ({data['share']})", expanded=(sector == "Energy")):
                        st.caption("Haz clic en cualquier acción para graficar:")
                        cols = st.columns(4)
                        for i, sym in enumerate(data["tickers"]):
                            with cols[i % 4]:
                                if st.button(sym, key=f"nh_{sector}_{sym}", use_container_width=True):
                                    st.session_state["nhnl_active_ticker"] = sym
                                    st.session_state["nhnl_active_name"] = f"Stock ({sym})"
                                    st.session_state["nhnl_active_sector"] = f"{sector} • 52W High"
                                    st.rerun()
            else:
                for sector, data in nhle.NEW_LOWS_BY_SECTOR.items():
                    with st.expander(f"🔴 **{sector}** — {data['count']} Lows ({data['share']})", expanded=(sector == "Capital Goods")):
                        st.caption("Haz clic en cualquier acción para graficar:")
                        cols = st.columns(4)
                        for i, sym in enumerate(data["tickers"]):
                            with cols[i % 4]:
                                if st.button(sym, key=f"nl_{sector}_{sym}", use_container_width=True):
                                    st.session_state["nhnl_active_ticker"] = sym
                                    st.session_state["nhnl_active_name"] = f"Stock ({sym})"
                                    st.session_state["nhnl_active_sector"] = f"{sector} • 52W Low"
                                    st.rerun()

        with tab_groups:
            cg1, cg2 = st.columns(2)
            with cg1:
                st.markdown("<strong style='color:#38BDF8;'>Leading Groups (Top Alzas)</strong>", unsafe_allow_html=True)
                for g in nhle.LEADING_GROUPS:
                    st.markdown(f"<div style='font-size:12px; padding:4px 0; border-bottom:1px solid #1F2937; display:flex; justify-content:space-between;'><span>{g['name']}</span><span style='color:#38BDF8; font-weight:bold;'>{g['count']} ({g['pct']})</span></div>", unsafe_allow_html=True)
            with cg2:
                st.markdown("<strong style='color:#F43F5E;'>Lagging Groups (Top Bajas)</strong>", unsafe_allow_html=True)
                for g in nhle.LAGGING_GROUPS:
                    st.markdown(f"<div style='font-size:12px; padding:4px 0; border-bottom:1px solid #1F2937; display:flex; justify-content:space-between;'><span>{g['name']}</span><span style='color:#F43F5E; font-weight:bold;'>{g['count']} ({g['pct']})</span></div>", unsafe_allow_html=True)

    with col_nhnl_chart:
        cur_t = st.session_state["nhnl_active_ticker"]
        cur_n = st.session_state["nhnl_active_name"]
        cur_s = st.session_state["nhnl_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_nhnl_tf_{tf}", use_container_width=True):
                    st.session_state["nhnl_tf"] = tf
                    st.rerun()

        fig_nhnl = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["nhnl_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_nhnl, use_container_width=True, config={"displayModeBar": True})
        
        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(59, 130, 246, 0.15); color:#60A5FA; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Monitor de Amplitud</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 3: COT POSITIONING (COMMITMENTS OF TRADERS)
# =========================================================================
elif "COT" in nav_view:
    st.markdown('<div class="brand-title">📊 COT Positioning (Commitments of Traders)</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">CFTC INSTITUTIONAL POSITIONING • SMART MONEY VS SPECULATORS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    market_opts = list(cpe.COT_MARKETS.keys())
    m_col1, m_col2 = st.columns([1.5, 3.5])
    with m_col1:
        sel_market = st.selectbox(
            "Seleccionar Mercado de Futuros:", 
            market_opts, 
            format_func=lambda x: f"{x} - {cpe.COT_MARKETS[x]['name']} ({cpe.COT_MARKETS[x]['category']})"
        )
    with m_col2:
        m_info = cpe.COT_MARKETS[sel_market]
        reg_color = "#EAB308" if "STAND ASIDE" in m_info["regime"] else ("#10B981" if "BULLISH" in m_info["regime"] or "LONG" in m_info["regime"] else "#EF4444")
        st.markdown(f"""
            <div style="display:flex; gap:10px; align-items:center; height:100%; padding-top:14px;">
                <span style="background:{reg_color}22; color:{reg_color}; border:1px solid {reg_color}55; padding:6px 14px; border-radius:6px; font-weight:700; font-size:12px;">{m_info['regime']}</span>
                <span style="background:#1E293B; color:#CBD5E1; padding:6px 14px; border-radius:6px; font-size:12px;">{m_info['sentiment_label']}</span>
                <span style="background:#1E293B; color:#38BDF8; padding:6px 14px; border-radius:6px; font-size:12px;">Crowding score: <strong>{m_info['crowding_score']}</strong></span>
                <span style="color:#94A3B8; font-size:12px;">{m_info['bias']}</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background:rgba(15, 23, 42, 0.7); border:1px solid #1E293B; border-radius:8px; padding:12px 16px; margin:10px 0 16px 0;">
            <div style="font-size:13px; color:#E2E8F0; line-height:1.6;">
                <strong>Diagnóstico Cuantitativo:</strong> {m_info['description']}
            </div>
            <div style="font-size:11px; color:#64748B; margin-top:4px;">
                Fecha del informe CFTC: <strong>{m_info['as_of_date']}</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3 Tarjetas de posicionamiento neto
    nc = m_info["non_commercial"]
    co = m_info["commercial"]
    sm = m_info["small_trader"]
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])

    with c1:
        st.markdown(f"""
            <div style="background:#0F172A; border-top:3px solid #3378FF; border-radius:8px; padding:12px; border:1px solid #1E293B;">
                <div style="color:#94A3B8; font-size:12px; font-weight:600;">Non-commercial (Large Speculators)</div>
                <div style="font-size:20px; font-weight:bold; color:#F8FAFC; margin:4px 0;">{nc['net']/1e3:,.1f}K</div>
                <div style="font-size:12px; color:#64748B;">{nc['pct_oi']} OI &nbsp;|&nbsp; {nc['wow']} WoW</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div style="background:#0F172A; border-top:3px solid #E53935; border-radius:8px; padding:12px; border:1px solid #1E293B;">
                <div style="color:#94A3B8; font-size:12px; font-weight:600;">Commercial (Smart Money Hedgers)</div>
                <div style="font-size:20px; font-weight:bold; color:#F8FAFC; margin:4px 0;">{co['net']/1e3:+,.1f}K</div>
                <div style="font-size:12px; color:#64748B;">{co['pct_oi']} OI &nbsp;|&nbsp; {co['wow']} WoW</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div style="background:#0F172A; border-top:3px solid #FFA726; border-radius:8px; padding:12px; border:1px solid #1E293B;">
                <div style="color:#94A3B8; font-size:12px; font-weight:600;">Small trader (Retail Speculators)</div>
                <div style="font-size:20px; font-weight:bold; color:#F8FAFC; margin:4px 0;">{sm['net']/1e3:+,.1f}K</div>
                <div style="font-size:12px; color:#64748B;">{sm['pct_oi']} OI &nbsp;|&nbsp; {sm['wow']} WoW</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div style="background:#0F172A; border-top:3px solid #00E676; border-radius:8px; padding:12px; border:1px solid #1E293B;">
                <div style="color:#94A3B8; font-size:12px; font-weight:600;">Open Interest Total</div>
                <div style="font-size:20px; font-weight:bold; color:#00E676; margin:4px 0;">{m_info['open_interest']:,}</div>
                <div style="font-size:12px; color:#64748B;">Cambio semanal: <strong>{m_info['oi_wow']}</strong></div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    fig_cot = cpe.render_cot_chart(sel_market)
    st.plotly_chart(fig_cot, use_container_width=True, config={"displayModeBar": True})


# =========================================================================
# VISTA 4: NAAIM / AAII SENTIMENT DESK
# =========================================================================
elif "NAAIM" in nav_view or "AAII" in nav_view:
    st.markdown('<div class="brand-title">🧠 NAAIM / AAII Sentiment Intelligence Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">EXPOSICIÓN INSTITUCIONAL VS SENTIMIENTO MINORISTA • SEÑALES CONTRARIAS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    col_naaim, col_aaii = st.columns([1.2, 1.0], gap="large")

    with col_naaim:
        st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="display:flex; gap:10px; align-items:center;">
                    <span style="font-size:16px; font-weight:bold; color:#F8FAFC;">NAAIM Exposure</span>
                    <span style="background:rgba(56, 189, 248, 0.15); color:#38BDF8; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:600;">Neutral</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:20px; font-weight:bold; color:#38BDF8;">87.7</span>
                    <span style="font-size:12px; color:#64748B;">Exposure Index • Oct 21, 2026</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        fig_naaim = sie.render_naaim_chart()
        st.plotly_chart(fig_naaim, use_container_width=True, config={"displayModeBar": False})

        # 4 Chips de métricas de NAAIM
        nk1, nk2, nk3, nk4 = st.columns(4)
        with nk1:
            st.metric("Percentile", sie.NAAIM_DATA["percentile"])
        with nk2:
            st.metric("Z-Score", f"{sie.NAAIM_DATA['z_score']:+.2f}")
        with nk3:
            st.metric("4W Chg", f"{sie.NAAIM_DATA['change_4w']:+.1f}")
        with nk4:
            st.metric("Range", sie.NAAIM_DATA["historical_range"])

        st.info(f"💡 **Lectura Institucional:** {sie.NAAIM_DATA['interpretation']}")

    with col_aaii:
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:16px; font-weight:bold; color:#F8FAFC;">AAII Sentiment</span>
                <span style="font-size:12px; color:#64748B;">Updated {sie.AAII_DATA['last_update']}</span>
            </div>
        """, unsafe_allow_html=True)

        ak1, ak2, ak3 = st.columns(3)
        with ak1:
            st.metric("BULLISH", f"{sie.AAII_DATA['bullish']:.1f}%", f"{sie.AAII_DATA['bullish_1w_chg']:+.1f} pts 1W")
        with ak2:
            st.metric("BEARISH", f"{sie.AAII_DATA['bearish']:.1f}%", f"{sie.AAII_DATA['bearish_1w_chg']:+.1f} pts 1W")
        with ak3:
            st.metric("BULL - BEAR SPREAD", f"{sie.AAII_DATA['spread']:+.1f} pts", f"{sie.AAII_DATA['spread_4w_chg']:+.1f} pts 4W")

        st.caption("Últimas 4 encuestas semanales (Bullish verde, Neutral gris, Bearish rojo):")
        fig_aaii = sie.render_aaii_horizontal_bars()
        st.plotly_chart(fig_aaii, use_container_width=True, config={"displayModeBar": False})

        st.markdown(f"""
            <div style="background:#0F172A; border:1px solid #1E293B; border-radius:8px; padding:14px; margin-top:8px;">
                <div style="color:#38BDF8; font-weight:700; font-size:12px; margin-bottom:6px;">TRADER READ:</div>
                <div style="color:#CBD5E1; font-size:12px; line-height:1.6;">
                    {sie.AAII_DATA['trader_read']}
                </div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================================
# VISTA 5: CALENDARIO ECONÓMICO (MACRO & SURPRISES)
# =========================================================================
elif "Económico" in nav_view or "Economic" in nav_view:
    st.markdown('<div class="brand-title">🌐 Calendario Económico & Macro Surprises</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">RELEASES MACROECONÓMICOS DE ALTO IMPACTO • CONSENSO VS ACTUAL • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    f1, f2, f3, f4 = st.columns([1.5, 1.2, 1.2, 1.2])
    with f1:
        st.markdown("<div style='font-size:16px; font-weight:bold; color:#F8FAFC; padding-top:6px;'>📅 &lt; October 2026 &gt;</div>", unsafe_allow_html=True)
    with f2:
        v_mode = st.selectbox("Vista Temporal:", ["Month", "Week", "Day"], index=0)
    with f3:
        i_filter = st.selectbox("Nivel de Impacto:", ["High", "All"], index=0)
    with f4:
        c_filter = st.selectbox("País:", ["US", "Global"], index=0)

    df_eco = ecle.get_filtered_economic_calendar(view_mode=v_mode, impact_filter=i_filter, country_filter=c_filter)

    st.markdown("""
        <div style="display:flex; justify-content:space-between; background:#111827; padding:8px 14px; border-radius:6px; font-size:12px; color:#94A3B8; font-weight:bold; margin-bottom:8px;">
            <span style="flex:1;">HORA (LOCAL)</span>
            <span style="flex:3;">EVENTO MACRO</span>
            <span style="flex:1; text-align:right;">ACTUAL</span>
            <span style="flex:1; text-align:right;">FORECAST</span>
            <span style="flex:1; text-align:right;">PREVIO</span>
        </div>
    """, unsafe_allow_html=True)

    grouped_days = df_eco["day_label"].unique()

    for day in grouped_days:
        st.markdown(f"<div style='background:#1E293B; color:#F8FAFC; padding:6px 12px; border-radius:4px; font-weight:bold; font-size:12px; margin:10px 0 4px 0;'>{day}</div>", unsafe_allow_html=True)
        sub_df = df_eco[df_eco["day_label"] == day]
        for _, row in sub_df.iterrows():
            act_color = "#22C55E" if row["status"] == "better" else ("#EF4444" if row["status"] == "worse" else "#F8FAFC")
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 14px; border-bottom:1px solid #1E293B; font-size:12px;">
                    <span style="flex:1; color:#94A3B8;">{row['time']}</span>
                    <span style="flex:3; color:#E2E8F0;"><span style="color:#EF4444;">🔴</span> {row['flag']} <strong>{row['event']}</strong></span>
                    <span style="flex:1; text-align:right; font-weight:bold; color:{act_color};">{row['actual']}</span>
                    <span style="flex:1; text-align:right; color:#94A3B8;">{row['forecast']}</span>
                    <span style="flex:1; text-align:right; color:#64748B;">{row['previous']}</span>
                </div>
            """, unsafe_allow_html=True)
'''

if "VISTA 1: CALENDARIO DE EARNINGS" not in code:
    code = code + views_code
    print("✅ Código de las 5 vistas institucionales añadido al final de app.py.")
else:
    print("ℹ️ Código de las 5 vistas ya presente en app.py.")

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("🎯 Integración completada con éxito.")
