"""
TradingVolt • Script de Integración de la Vista Industry Rank Tables
Agrega industry_ranks_engine a app.py con tablas dobles de sectores (11) y grupos (25),
drill-down interactivo y sincronización con gráfico multi-temporalidad.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_PATH = r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\app.py"

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. IMPORTAR INDUSTRY_RANKS_ENGINE
import_hook = """try:
    import stage_analysis_engine as sae
    importlib.reload(sae)
except ImportError:
    sae = None"""

import_new = """try:
    import stage_analysis_engine as sae
    importlib.reload(sae)
except ImportError:
    sae = None
try:
    import industry_ranks_engine as ire
    importlib.reload(ire)
except ImportError:
    ire = None"""

if import_hook in code and "industry_ranks_engine" not in code:
    code = code.replace(import_hook, import_new, 1)
    print("✅ industry_ranks_engine importado.")

# 2. AGREGAR A LA NAVEGACIÓN EN SIDEBAR
nav_target = """            "📊 Stage Analysis (Sectores & Activos)"
        ],"""

nav_repl = """            "📊 Stage Analysis (Sectores & Activos)",
            "🏆 Industry Rank Tables (Sectores & Grupos)"
        ],"""

if "Industry Rank Tables" not in code:
    if nav_target in code:
        code = code.replace(nav_target, nav_repl, 1)
    else:
        # Intento con CRLF
        nav_target_crlf = nav_target.replace("\n", "\r\n")
        nav_repl_crlf = nav_repl.replace("\n", "\r\n")
        code = code.replace(nav_target_crlf, nav_repl_crlf, 1)
    print("✅ Opción Industry Rank Tables agregada al menú.")

# 3. CÓDIGO DE LA VISTA INDUSTRY RANK TABLES
ranks_view_code = '''

# =========================================================================
# VISTA: INDUSTRY RANK TABLES (11 SECTORES & 25 GRUPOS + DRILL-DOWN)
# =========================================================================
elif "Industry Rank" in nav_view:
    st.markdown('<div class="brand-title">🏆 Industry Rank Tables & Momentum Leaders</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">ROTACIÓN DE FUERZA RELATIVA • 1M VS 3M VS 6M VS 12M • DRILL-DOWN DE ACTIVOS • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "industry_tf" not in st.session_state:
        st.session_state["industry_tf"] = "1D"
    if "industry_active_ticker" not in st.session_state:
        st.session_state["industry_active_ticker"] = "CDZI"
    if "industry_active_name" not in st.session_state:
        st.session_state["industry_active_name"] = "Cadiz Inc."
    if "industry_active_sector" not in st.session_state:
        st.session_state["industry_active_sector"] = "Utilities • Water Utilities"
    if "industry_selected_sector" not in st.session_state:
        st.session_state["industry_selected_sector"] = None

    col_rank_left, col_rank_right = st.columns([1.15, 1.25], gap="medium")

    with col_rank_left:
        # ----------------- PARTE 1 SUPERIOR: SECTORS (11) O DRILL-DOWN -----------------
        sel_ind_sec = st.session_state["industry_selected_sector"]

        if sel_ind_sec is None:
            # TABLA DE 11 SECTORES
            top_h1, top_h2 = st.columns([2.5, 2.5])
            with top_h1:
                st.markdown("<div style='font-size:14px; font-weight:bold; color:#F8FAFC; padding-top:4px;'>📊 Industry Ranks • Sectores (11)</div>", unsafe_allow_html=True)
            with top_h2:
                sort_sec = st.selectbox(
                    "Ordenar por:",
                    ["Rank Change - 1M vs 3M", "1M Rank", "3M Rank", "Stocks"],
                    index=0,
                    label_visibility="collapsed",
                    key="sort_sec_rank"
                )

            df_sec = ire.get_sector_ranks(sort_sec)

            st.markdown("""
                <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                    <span style="flex:2.8;">NAME</span>
                    <span style="flex:1.2; text-align:center;">1M</span>
                    <span style="flex:0.8; text-align:center;">3M</span>
                    <span style="flex:0.8; text-align:center;">6M</span>
                    <span style="flex:0.8; text-align:center;">12M</span>
                    <span style="flex:0.8; text-align:right;">STOCKS</span>
                </div>
            """, unsafe_allow_html=True)

            for _, row in df_sec.iterrows():
                sc1, sc2, sc3, sc4, sc5, sc6 = st.columns([2.8, 1.2, 0.8, 0.8, 0.8, 0.8])
                with sc1:
                    if st.button(f"📁 {row['name']}", key=f"btn_sec_rank_{row['name']}", use_container_width=True):
                        st.session_state["industry_selected_sector"] = row["name"]
                        st.rerun()
                with sc2:
                    chg = row["chg_1m_3m"]
                    if chg > 0:
                        badge = f"<span style='color:#10B981; font-weight:bold;'>{row['rank_1m']}<sup>+{chg}</sup></span>"
                    elif chg < 0:
                        badge = f"<span style='color:#EF4444; font-weight:bold;'>{row['rank_1m']}<sup>{chg}</sup></span>"
                    else:
                        badge = f"<span>{row['rank_1m']}</span>"
                    st.markdown(f"<div style='text-align:center; font-size:12px; padding-top:4px;'>{badge}</div>", unsafe_allow_html=True)
                with sc3:
                    st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_3m']}</div>", unsafe_allow_html=True)
                with sc4:
                    st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_6m']}</div>", unsafe_allow_html=True)
                with sc5:
                    st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_12m']}</div>", unsafe_allow_html=True)
                with sc6:
                    st.markdown(f"<div style='text-align:right; font-size:12px; font-weight:bold; color:#E2E8F0; padding-top:4px;'>{row['stocks']}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:1px 0 4px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        else:
            # DRILL-DOWN DEL SECTOR CLICADO CON BARRAS HORIZONTALES
            b1, b2 = st.columns([1.5, 3])
            with b1:
                if st.button("⬅️ Volver a Sectores", key="btn_back_rank_sec", use_container_width=True):
                    st.session_state["industry_selected_sector"] = None
                    st.rerun()
            with b2:
                st.markdown(f"<div style='font-size:15px; font-weight:bold; color:#38BDF8; padding-top:4px;'>📁 {sel_ind_sec} • Activos Líderes</div>", unsafe_allow_html=True)

            st.markdown("""
                <div style="background:rgba(15, 23, 42, 0.7); border:1px solid #1E293B; border-radius:6px; padding:6px 12px; margin:4px 0 10px 0; font-size:11px; color:#94A3B8; display:flex; justify-content:space-between;">
                    <span>Ordenado por: <strong style="color:#38BDF8;">Change vs yesterday's close</strong></span>
                    <span>Mostrando principales líderes del sector</span>
                </div>
            """, unsafe_allow_html=True)

            constituents = ire.INDUSTRY_CONSTITUENTS.get(sel_ind_sec, ire.INDUSTRY_CONSTITUENTS["Utilities"])
            for item in constituents:
                ic1, ic2, ic3, ic4 = st.columns([1.2, 2.2, 3.4, 1.2])
                with ic1:
                    is_active = (st.session_state["industry_active_ticker"] == item["symbol"])
                    btn_label = f"👉 **{item['symbol']}**" if is_active else item["symbol"]
                    if st.button(btn_label, key=f"ind_btn_{item['symbol']}", use_container_width=True):
                        st.session_state["industry_active_ticker"] = item["symbol"]
                        st.session_state["industry_active_name"] = item["name"]
                        st.session_state["industry_active_sector"] = f"{sel_ind_sec} • {item['sub']}"
                        st.rerun()
                with ic2:
                    st.markdown(f"<div style='font-size:11px; color:#E2E8F0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{item['name']}<br><span style='color:#64748B; font-size:10px;'>{item['sub']}</span></div>", unsafe_allow_html=True)
                with ic3:
                    max_g = 8.0
                    bar_w = min(100, int((item["change_pct"] / max_g) * 100))
                    st.markdown(f"""
                        <div style="width:100%; height:14px; background:#1E293B; border-radius:3px; overflow:hidden; margin-top:6px;">
                            <div style="width:{bar_w}%; height:100%; background:#3B82F6;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with ic4:
                    st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#3B82F6; text-align:right; padding-top:5px;'>+{item['change_pct']:.2f}%</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:1px 0 3px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # ----------------- PARTE 2 INFERIOR: INDUSTRY GROUPS (25) -----------------
        grp_h1, grp_h2 = st.columns([2.5, 2.5])
        with grp_h1:
            st.markdown("<div style='font-size:14px; font-weight:bold; color:#F8FAFC; padding-top:4px;'>📊 Industry Ranks • Groups (25)</div>", unsafe_allow_html=True)
        with grp_h2:
            sort_grp = st.selectbox(
                "Ordenar Grupos por:",
                ["Rank", "Rank Change", "Stocks"],
                index=0,
                label_visibility="collapsed",
                key="sort_grp_rank"
            )

        df_grp = ire.get_industry_groups(sort_grp)

        st.markdown("""
            <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                <span style="flex:2.8;">NAME</span>
                <span style="flex:1.2; text-align:center;">1M</span>
                <span style="flex:0.8; text-align:center;">3M</span>
                <span style="flex:0.8; text-align:center;">6M</span>
                <span style="flex:0.8; text-align:center;">12M</span>
                <span style="flex:0.8; text-align:right;">STOCKS</span>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df_grp.iterrows():
            gc1, gc2, gc3, gc4, gc5, gc6 = st.columns([2.8, 1.2, 0.8, 0.8, 0.8, 0.8])
            with gc1:
                if st.button(f"📑 {row['name']}", key=f"btn_grp_rank_{row['name']}", use_container_width=True):
                    # Si el grupo tiene activos registrados, abrirlo directamente
                    if row['name'] in ire.INDUSTRY_CONSTITUENTS:
                        st.session_state["industry_selected_sector"] = row['name']
                        st.rerun()
                    else:
                        st.session_state["industry_selected_sector"] = "Utilities"
                        st.rerun()
            with gc2:
                chg = row["chg_1m"]
                if chg > 0:
                    badge = f"<span style='color:#10B981; font-weight:bold;'>{row['rank_1m']}<sup>+{chg}</sup></span>"
                elif chg < 0:
                    badge = f"<span style='color:#EF4444; font-weight:bold;'>{row['rank_1m']}<sup>{chg}</sup></span>"
                else:
                    badge = f"<span>{row['rank_1m']}</span>"
                st.markdown(f"<div style='text-align:center; font-size:12px; padding-top:4px;'>{badge}</div>", unsafe_allow_html=True)
            with gc3:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_3m']}</div>", unsafe_allow_html=True)
            with gc4:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_6m']}</div>", unsafe_allow_html=True)
            with gc5:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#94A3B8; padding-top:4px;'>{row['rank_12m']}</div>", unsafe_allow_html=True)
            with gc6:
                st.markdown(f"<div style='text-align:right; font-size:12px; font-weight:bold; color:#E2E8F0; padding-top:4px;'>{row['stocks']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:1px 0 4px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    with col_rank_right:
        cur_t = st.session_state["industry_active_ticker"]
        cur_n = st.session_state["industry_active_name"]
        cur_s = st.session_state["industry_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_ind_tf_{tf}", use_container_width=True):
                    st.session_state["industry_tf"] = tf
                    st.rerun()

        fig_ind = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["industry_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_ind, use_container_width=True, config={"displayModeBar": True})

        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(59, 130, 246, 0.15); color:#60A5FA; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Industry Rank Leader</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
'''

if "VISTA: INDUSTRY RANK TABLES" not in code:
    code = code + ranks_view_code
    print("✅ Código de Industry Rank Tables agregado.")

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("🎯 Integración de Industry Rank Tables completada con éxito.")
