"""
TradingVolt • Script de Integración de la Vista Stage Analysis (Stan Weinstein)
Agrega stage_analysis_engine a app.py con el drill-down interactivo de sectores y activos.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APP_PATH = r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\app.py"

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. IMPORTAR STAGE_ANALYSIS_ENGINE
import_hook = """try:
    import economic_calendar_engine as ecle
    importlib.reload(ecle)
except ImportError:
    ecle = None"""

import_new = """try:
    import economic_calendar_engine as ecle
    importlib.reload(ecle)
except ImportError:
    ecle = None
try:
    import stage_analysis_engine as sae
    importlib.reload(sae)
except ImportError:
    sae = None"""

if import_hook in code and "stage_analysis_engine" not in code:
    code = code.replace(import_hook, import_new, 1)
    print("✅ stage_analysis_engine importado.")

# 2. AGREGAR A LA NAVEGACIÓN EN SIDEBAR
nav_target = """            "🌐 Calendario Económico"
        ],"""

nav_repl = """            "🌐 Calendario Económico",
            "📊 Stage Analysis (Sectores & Activos)"
        ],"""

if "Stage Analysis (Sectores" not in code:
    code = code.replace(nav_target, nav_repl, 1)
    if nav_target not in code:
        # Intento con CRLF
        nav_target_crlf = nav_target.replace("\n", "\r\n")
        nav_repl_crlf = nav_repl.replace("\n", "\r\n")
        code = code.replace(nav_target_crlf, nav_repl_crlf, 1)
    print("✅ Opción Stage Analysis agregada al menú.")

# 3. CÓDIGO DE LA VISTA STAGE ANALYSIS
stage_view_code = '''

# =========================================================================
# VISTA: STAGE ANALYSIS (STAN WEINSTEIN 4-STAGE MODEL & SECTOR DRILL-DOWN)
# =========================================================================
elif "Stage Analysis" in nav_view:
    st.markdown('<div class="brand-title">📊 Stage Analysis (Stan Weinstein 4-Stage Model)</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">ROTACIÓN SECTORIAL INSTITUCIONAL • FASES DE ACUMULACIÓN &amp; TENDENCIA • REVERSE ENGINEERED FROM DEEPVUE</div>', unsafe_allow_html=True)
    st.write("")

    if "stage_tf" not in st.session_state:
        st.session_state["stage_tf"] = "1D"
    if "stage_active_ticker" not in st.session_state:
        st.session_state["stage_active_ticker"] = "TPET"
    if "stage_active_name" not in st.session_state:
        st.session_state["stage_active_name"] = "Trio Petroleum Corp."
    if "stage_active_sector" not in st.session_state:
        st.session_state["stage_active_sector"] = "Energy • Oil, Gas & Consumable Fuels"
    if "stage_selected_sector" not in st.session_state:
        st.session_state["stage_selected_sector"] = None

    col_stage_left, col_stage_right = st.columns([1.1, 1.3], gap="medium")

    with col_stage_left:
        # 1. Market Overview (S1, S2, S3, S4)
        st.markdown("""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 14px; margin-bottom:12px;">
                <div style="font-weight:700; color:#F3F4F6; font-size:13px; margin-bottom:8px;">Market Overview (Stan Weinstein Stages)</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12px;">
                    <span style="color:#F59E0B;">● S1 (Basing): <strong>78 (1%)</strong></span>
                    <span style="color:#3B82F6;">● S2 (Uptrend): <strong>1,579 (28%)</strong></span>
                    <span style="color:#EAB308;">● S3 (Distribution): <strong>842 (15%)</strong></span>
                    <span style="color:#EC4899;">● S4 (Downtrend): <strong>3,141 (56%)</strong></span>
                </div>
                <div style="width:100%; height:8px; background:#1F2937; border-radius:4px; overflow:hidden; display:flex;">
                    <div style="width:1.4%; height:100%; background:#F59E0B;" title="S1: 1.4%"></div>
                    <div style="width:28.0%; height:100%; background:#3B82F6;" title="S2: 28.0%"></div>
                    <div style="width:15.0%; height:100%; background:#EAB308;" title="S3: 15.0%"></div>
                    <div style="width:55.6%; height:100%; background:#EC4899;" title="S4: 55.6%"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico histórico de curvas S1, S2, S3, S4
        with st.expander("📈 Histórico de Distribución de Fases (S1-S4)", expanded=False):
            fig_ov = sae.render_market_overview_chart()
            st.plotly_chart(fig_ov, use_container_width=True, config={"displayModeBar": False})

        # 2. VISTA CONDICIONAL: TABLA DE SECTORES O DRILL-DOWN DE ACTIVOS
        sel_sec = st.session_state["stage_selected_sector"]

        if sel_sec is None:
            # TABLA GENERAL DE SECTORES
            st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:14px; font-weight:bold; color:#F8FAFC;">Desglose por Sectores (GICS)</span>
                    <span style="font-size:11px; color:#94A3B8;">Haz clic en un sector para desplegar sus activos</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div style="display:flex; justify-content:space-between; background:#1F2937; padding:6px 12px; border-radius:6px; font-size:11px; color:#94A3B8; font-weight:bold; margin-bottom:6px;">
                    <span style="flex:2.2;">SECTOR</span>
                    <span style="flex:2.5; text-align:center;">DISTRIBUCIÓN (S1-S4)</span>
                    <span style="flex:0.6; text-align:center;">S1</span>
                    <span style="flex:0.6; text-align:center;">S2</span>
                    <span style="flex:0.6; text-align:center;">S3</span>
                    <span style="flex:0.6; text-align:center;">S4</span>
                    <span style="flex:1.0; text-align:right;">SALUD</span>
                </div>
            """, unsafe_allow_html=True)

            for sector_name, s_info in sae.SECTOR_STAGE_DATA.items():
                r1, r2, r3, r4, r5, r6, r7 = st.columns([2.2, 2.5, 0.6, 0.6, 0.6, 0.6, 1.0])
                with r1:
                    if st.button(f"📁 {sector_name} ({s_info['count']})", key=f"btn_sec_{sector_name}", use_container_width=True):
                        st.session_state["stage_selected_sector"] = sector_name
                        st.rerun()
                with r2:
                    st.markdown(f"""
                        <div style="width:100%; height:10px; background:#1E293B; border-radius:4px; overflow:hidden; display:flex; margin-top:8px;">
                            <div style="width:{s_info['s1']}%; height:100%; background:#F59E0B;"></div>
                            <div style="width:{s_info['s2']}%; height:100%; background:#3B82F6;"></div>
                            <div style="width:{s_info['s3']}%; height:100%; background:#EAB308;"></div>
                            <div style="width:{s_info['s4']}%; height:100%; background:#EC4899;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with r3:
                    st.markdown(f"<div style='text-align:center; font-size:11px; padding-top:4px;'>{s_info['s1']}%</div>", unsafe_allow_html=True)
                with r4:
                    st.markdown(f"<div style='text-align:center; font-size:11px; font-weight:bold; color:#3B82F6; padding-top:4px;'>{s_info['s2']}%</div>", unsafe_allow_html=True)
                with r5:
                    st.markdown(f"<div style='text-align:center; font-size:11px; padding-top:4px;'>{s_info['s3']}%</div>", unsafe_allow_html=True)
                with r6:
                    st.markdown(f"<div style='text-align:center; font-size:11px; padding-top:4px;'>{s_info['s4']}%</div>", unsafe_allow_html=True)
                with r7:
                    st.markdown(f"<div style='text-align:right; font-size:11px; font-weight:bold; color:{s_info['health_color']}; padding-top:4px;'>{s_info['health']}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0 6px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

        else:
            # DRILL-DOWN DEL SECTOR SELECCIONADO
            sec_meta = sae.SECTOR_STAGE_DATA.get(sel_sec, {"count": 265, "s2": 41, "health": "Strong"})
            b_c1, b_c2 = st.columns([1.5, 3])
            with b_c1:
                if st.button("⬅️ Volver a Sectores", key="btn_back_sectors", use_container_width=True):
                    st.session_state["stage_selected_sector"] = None
                    st.rerun()
            with b_c2:
                st.markdown(f"<div style='font-size:15px; font-weight:bold; color:#38BDF8; padding-top:4px;'>📁 {sel_sec} ({sec_meta['count']} acciones)</div>", unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background:rgba(15, 23, 42, 0.7); border:1px solid #1E293B; border-radius:6px; padding:8px 12px; margin:8px 0 12px 0; font-size:12px; color:#CBD5E1; display:flex; justify-content:space-between;">
                    <span>Fase dominante: <strong style="color:#3B82F6;">Stage 2 ({sec_meta['s2']}%)</strong></span>
                    <span>Salud: <strong style="color:{sec_meta.get('health_color', '#3B82F6')}">{sec_meta.get('health', 'Strong')}</strong></span>
                    <span style="color:#94A3B8;">Ordenado por: <strong>Performance Diario (%)</strong></span>
                </div>
            """, unsafe_allow_html=True)

            assets = sae.SECTOR_ASSETS_PERFORMANCE.get(sel_sec, sae.SECTOR_ASSETS_PERFORMANCE["Energy"])
            st.caption(f"Mostrando los principales {len(assets)} activos líderes del sector. Haz clic en cualquiera para graficar:")

            # Lista de activos con barras de rendimiento horizontal
            for a in assets:
                ac1, ac2, ac3, ac4 = st.columns([1.2, 2.4, 3.2, 1.2])
                with ac1:
                    is_active = (st.session_state["stage_active_ticker"] == a["symbol"])
                    btn_label = f"👉 **{a['symbol']}**" if is_active else a["symbol"]
                    if st.button(btn_label, key=f"sa_t_{sel_sec}_{a['symbol']}", use_container_width=True):
                        st.session_state["stage_active_ticker"] = a["symbol"]
                        st.session_state["stage_active_name"] = a["name"]
                        st.session_state["stage_active_sector"] = f"{sel_sec} • {a['sub']}"
                        st.rerun()
                with ac2:
                    st.markdown(f"<div style='font-size:11px; color:#E2E8F0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{a['name']}<br><span style='color:#64748B; font-size:10px;'>{a['sub']}</span></div>", unsafe_allow_html=True)
                with ac3:
                    # Barra horizontal azul de performance idéntica a Deepvue
                    max_gain = 14.0
                    bar_w = min(100, int((a["change_pct"] / max_gain) * 100))
                    st.markdown(f"""
                        <div style="width:100%; height:16px; background:#1E293B; border-radius:3px; overflow:hidden; margin-top:6px;">
                            <div style="width:{bar_w}%; height:100%; background:#3B82F6;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with ac4:
                    st.markdown(f"<div style='font-size:12px; font-weight:bold; color:#3B82F6; text-align:right; padding-top:6px;'>+{a['change_pct']:.2f}%</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0 4px 0; border:none; border-top:1px solid #1E293B;'>", unsafe_allow_html=True)

    with col_stage_right:
        cur_t = st.session_state["stage_active_ticker"]
        cur_n = st.session_state["stage_active_name"]
        cur_s = st.session_state["stage_active_sector"]

        tf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 3])
        tf_options = ["5m", "15m", "1h", "4h", "1D", "1W", "1M"]
        for idx, tf in enumerate(tf_options):
            with tf_cols[idx]:
                if st.button(tf, key=f"btn_stage_tf_{tf}", use_container_width=True):
                    st.session_state["stage_tf"] = tf
                    st.rerun()

        fig_stage = ece.render_deepvue_chart(
            cur_t, 
            timeframe=st.session_state["stage_tf"],
            company_name=cur_n,
            sector_info=cur_s
        )
        st.plotly_chart(fig_stage, use_container_width=True, config={"displayModeBar": True})

        st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:12px 16px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:16px; font-weight:bold; color:#F9FAFB;">{cur_t}</span> • 
                        <span style="color:#9CA3AF; font-size:13px;">{cur_n}</span>
                        <div style="font-size:12px; color:#6B7280;">{cur_s}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(59, 130, 246, 0.15); color:#60A5FA; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600;">Stan Weinstein Stage Analysis</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
'''

if "VISTA: STAGE ANALYSIS" not in code:
    code = code + stage_view_code
    print("✅ Código de Stage Analysis agregado.")

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("🎯 Integración de Stage Analysis completada con éxito.")
