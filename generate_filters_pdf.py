"""
Generador del Documento PDF Vectorial Institucional (100% Nativo, Sin Recortes):
TradingVolt • Catálogo Maestro de Filtros Cuantitativos (Reverse Engineering)
"""
import os
import shutil
import textwrap

WORKSPACE_DIR = r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener"
ARTIFACT_DIR = r"C:\Users\kim17\.gemini\antigravity\brain\c5eba840-a175-4523-8ad5-46a40732b62e"

PDF_OUT = os.path.join(WORKSPACE_DIR, "TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.pdf")
PDF_ARTIFACT = os.path.join(ARTIFACT_DIR, "TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.pdf")

SECTIONS = [
    {
        "title": "1. UNIVERSOS MAESTROS & LIDERES INSTITUCIONALES (DEEPVUE CORE)",
        "filters": [
            ("01", "Deepvue Universe", "Deepvue (752)", "Piscina maestra institucional de alta liquidez en los grupos de industria lideres a 1, 3 y 12M.",
             ["* $Vol Promedio 20d >= $20M diarios (o Volumen >= 200,000 acciones)",
              "* Precio de Cierre >= $10.00 (elimina penny stocks e iliquidas)",
              "* Fuerza Relativa RS 1M > 45, Dist Max 52s >= -30% y Close >= 0.90 * SMA 200"]),
            ("02", "Liquid Leaders", "Deepvue (187)", "Acciones ultra-liquidas en Etapa 2 con Fuerza Relativa superior para absorcion institucional.",
             ["* $Vol Promedio 20d >= $15M - $20M diarios (o Volumen >= 200,000)",
              "* Estructura Alcista: Close >= 0.95 * SMA 50 o Close >= 0.95 * SMA 200",
              "* Dist Max 52s >= -25% y ROC 3M >= +3.0% (o ROC 1M >= 0.0%)"]),
            ("03", "Pure Momentum", "TradingVolt (231)", "Acciones de alta velocidad diaria (ADR elevado) y gran liquidez para swing agil.",
             ["* $Vol Promedio 20d >= $7.0M diarios (tolerancia operativa >= $5.0M)",
              "* Rango Diario Promedio ADR(10d) > 3.0% (tolerancia >= 2.8%)",
              "* Fuerza Absoluta: AS 1M > 95 o AS 3M > 93 (ROC 1M >= +10% o ROC 3M >= +20%)"]),
            ("04", "Sustained Momentum", "Deepvue (186)", "Lideres liquidos con persistencia de tendencia en 3 y 6 meses sobre medias clave.",
             ["* $Vol Promedio 20d >= $8M - $10M diarios (o Volumen >= 100,000)",
              "* Momentum Sostenido: ROC 3M >= +5.0% o ROC 6M >= +10.0% (RS Rating > 90)",
              "* Estructura: Close >= 0.95 * SMA 50/200 y Dist Max 52s >= -20%"]),
            ("05", "Weekly Strength", "Deepvue (399)", "Acumulacion institucional sostenida de viernes a viernes cerrando en maximos semanales.",
             ["* Posicion Rango Semanal (5d) >= 65% - 70% (o a <= 3.5% del maximo semanal)",
              "* Sostenida sobre EMA 21 (>= 0.97 * EMA 21) y sobre SMA 50 / SMA 200",
              "* Liquidez $Vol 20d >= $5M, Dist Max 52s >= -25% y ROC 3M >= +2.0%"]),
            ("06", "Power 21", "Deepvue (69)", "Lideres realizando pullback ordenado o consolidando pegados a la media exponencial 21 EMA.",
             ["* Proximidad a 21-Day EMA: Distancia entre -3.5% y +4.0%",
              "* Fuerza Absoluta Previa: ROC 3M >= +3.0%, Close >= 0.95*SMA50 y Dist Max 52s >= -25%",
              "* Liquidez Institucional: $Vol 20d >= $5M - $10M diarios"]),
        ]
    },
    {
        "title": "2. SUITE INSTITUCIONAL DE AMEET RAI (RUTINAS DIARIAS & FIN DE SEMANA)",
        "filters": [
            ("07", "Ameet Rai: IPO 1 Yr", "Ameet Rai (189)", "Barometro macro Risk-On / Risk-Off sobre todas las empresas salidas a bolsa en el ultimo ano.",
             ["* Antiguedad de Cotizacion <= 260 sesiones bursatiles (<= 1 ano desde debut IPO)",
              "* Soporte Institucional (Risk-On): Close >= 0.95*EMA21 o SMA20 (Dist Max 52s >= -25%)",
              "* Filtro Base: Precio >= $1.00 y Liquidez $Vol 20d >= $0.5M"]),
            ("08", "Ameet Rai: HV Edge", "Ameet Rai (45)", "Detecta el dia exacto de acumulacion institucional masiva bajo 3 hitos de volumen record.",
             ["* Firma HV Edge (Cumplir 1 de 3): 1) Vol Hoy >= Maximo Volumen en 1 Ano (252 sesiones)",
              "* 2) Vol Hoy >= Max Vol desde IPO  |  3) Vol Hoy >= Max Vol desde Earnings (63 sesiones)",
              "* Filtro Base: Precio >= $1.00 y Liquidez $Vol 20d >= $1.0M"]),
            ("09", "Ameet Rai: HTF Flags", "Ameet Rai (12)", "El patron mas explosivo: duplicacion rapida de precio seguida de bandera estrecha y alta.",
             ["* Mastil Explosivo (20 sesiones): Subida ((Max20 - Min20) / Min20) >= +80% a +100%",
              "* Consolidacion de Bandera (Flag Depth): Retroceso desde el pico <= 25% - 30%",
              "* Filtro Base: Precio >= $1.00 y Liquidez $Vol 20d >= $1.0M"]),
            ("10", "Ameet Rai: Daily Liq.", "Ameet Rai (296)", "Radar diario de ultra-liquidez para rastrear flujos de fondos pesados y rotacion temprana.",
             ["* Volumen Fisico de la Sesion >= 8,000,000 de acciones (o Media 20d >= 8,000,000)",
              "* Flujo Institucional en Dolares: $Vol >= $15,000,000 diarios",
              "* Filtro de Precio Base: Close >= $2.00"]),
            ("11", "Ameet Rai: 62.5% RS", "Ameet Rai (191)", "Lideres resilientes que acumulan sesiones positivas mientras el mercado general corrige.",
             ["* Ratio Sesiones Positivas (RS Days) >= 62.5% en ventanas de 5, 8, 10, 15, 20, 30, 40 o 60d",
              "* En Fase de Fuerza Relativa: Close >= 0.95 * SMA 50/200 o Dist Max 52s >= -25%",
              "* Filtro Base: Precio >= $3.00 y Liquidez $Vol 20d >= $3.0M"]),
            ("12", "Highest Volume IPO", "Deepvue (7)", "Nuevas emisiones que rompen record absoluto de volumen desde su debut con cierre fuerte.",
             ["* Volumen Hoy >= Maximo Volumen historico desde el dia posterior al estreno IPO",
              "* Daily Closing Range (DCR) > 40% con variacion diaria positiva (Chg Today > 0%)",
              "* Liquidez Promedio: $Vol 20d > $3,000,000 diarios"]),
        ]
    },
    {
        "title": "3. COMPRESION DE VOLATILIDAD, VCP & SECADO DE VOLUMEN (MINERVINI / DEEPVUE)",
        "filters": [
            ("13", "Minervini VCP Pattern", "M. Minervini (43)", "Contraccion progresiva de volatilidad (VCP) en el lado derecho de la base con secado de oferta.",
             ["* Secado de Volumen en consolidacion: Media Vol(5d) / Media Vol(50d) <= 1.35x",
              "* Estructura Etapa 2: Close >= 0.95 * SMA 50/200 y Dist Max 52s >= -20%",
              "* Liquidez Institucional: $Vol 20d >= $10,000,000 diarios (o Vol >= 100k)"]),
            ("14", "Minervini Stage 2", "M. Minervini", "Plantilla clasica Trend Template de Mark Minervini en Etapa 2 de aceleracion alcista.",
             ["* Alineacion Estructural de Medias: Close > SMA 50 > SMA 200",
              "* Proximidad a Techo y Suelo Anual: Dist Max 52s >= -20% y Dist Min 52s >= +20%",
              "* Momentum Controlado sin Agotamiento: 50 <= RSI(14) <= 78"]),
            ("15", "Volume Dry Up (VDU)", "Deepvue (160)", "Agotamiento de presion vendedora sobre la SMA 50 con compresion en el indicador RMV.",
             ["* Soporte Institucional: Close >= 0.98 * SMA 50",
              "* Secado de Volumen: RVOL 20d <= 0.85x (o Vol 5d / Vol 50d <= 0.75x)",
              "* Indicador RMV(15d) <= 15.0% (<= 10.0% = Tight Verde) y Liquidez $Vol 20d >= $3.0M"]),
            ("16", "Tight Range (Coiling)", "Deepvue (26)", "Compresion extrema de precio y volatilidad a 15 dias o patron Double Inside Days.",
             ["* Volatilidad de Rango 15d: RMV(15) = ((High15 - Low15) / Low15) * 100 <= 10.0%",
              "* Cambio 5d |Chg 5d| <= 4.0% O patron Double Inside Days (H0<=H1<=H2 y L0>=L1>=L2)",
              "* Proximidad a Medias: Dist SMA50 <= 10%, Dist SMA200 <= 20% y $Vol 20d >= $3.0M"]),
        ]
    },
    {
        "title": "4. METODOLOGIA CANSLIM, STAN WEINSTEIN & ACUMULACION TEMPRANA",
        "filters": [
            ("17", "CANSLIM Official", "W. O'Neil (36)", "Verdaderos lideres de mercado combinando fortaleza en maximos y patrocinio institucional.",
             ["* Precio >= $10.00 y Liquidez Institucional $Vol 20d >= $5,000,000",
              "* Nuevos Maximos & Liderazgo (N / L): Dist Max 52s >= -15% a -20% y ROC 3M > 0%",
              "* Direccion de Mercado (M): Etapa 2 Alcista (Close >= SMA 50 > SMA 200)"]),
            ("18", "CANSLIM High RS", "W. O'Neil (137)", "Lideres de Tecnologia y Consumo Discrecional con maxima Fuerza Relativa IBD ponderada.",
             ["* Fuerza Relativa IBD Ponderada: 0.40*(3M) + 0.20*(6M) + 0.20*(9M) + 0.20*(12M) -> RS > 85",
              "* Liquidez Institucional: $Vol 20d >= $15,000,000 y Precio >= $10.00",
              "* Estructura Alcista sostenida sobre SMA 50 y SMA 200"]),
            ("19", "True Market Leaders", "TML / BO60 (331)", "Universo TML y detector de rupturas de bases de 60 dias (BO60) en zona de compra O'Neil.",
             ["* Pivote BO60: Superacion del maximo de 60 sesiones con volumen RVOL >= 1.25x",
              "* Zona de Compra O'Neil: Entre 0.0% y +5.0% sobre el pivote (> +5% = Extendida)",
              "* Rating Acumulacion/Distribucion Chaikin (13 semanas): Ratio Pos/Neg >= 1.45 = A+"]),
            ("20", "Weinstein Stage 2/2A", "S. Weinstein (417)", "Acciones saliendo de Etapa 1 (Base) hacia Etapa 2A (Early Markup) y Etapa 2 alcista.",
             ["* Regla Weinstein: Close >= 0.97 * SMA 50 y >= 0.96 * SMA 200 con pendiente positiva",
              "* Sub-etapa: Dist Max 52s >= -15% = Etapa 2A (Early Markup); hasta -30% = Etapa 2",
              "* Liquidez Institucional: $Vol 20d >= $15M - $20M y Fuerza Relativa RS > 85"]),
            ("21", "Pocket Pivots", "Morales/Kacher (45)", "Compra institucional encubierta dentro de la base antes del breakout convencional.",
             ["* Dia Alcista (Up Day): Close Hoy > Close Ayer",
              "* Regla Pocket Pivot: Vol Hoy > Max(Volumen de cualquier dia bajista en las 10 sesiones previas)",
              "* Contexto Constructivo: Sobre/cerca de SMA 20/50, Dist Max 52s >= -35% y $Vol >= $2.0M"]),
            ("22", "David Ryan: Ants", "David Ryan (3+)", "Acumulacion institucional persistente durante 3 semanas consecutivas (15 barras).",
             ["* Frecuencia Acumulacion: >= 4 a 5 dias alcistas en 15 sesiones con Vol > Vol Previo o > SMA20/50",
              "* Ubicacion de Precio: A menos de 5% del maximo de 20d o dentro del 25% del maximo anual"]),
        ]
    },
    {
        "title": "5. CATALIZADORES EXPLOSIVOS, INTRADIA, PRE/POST-MARKET & SWING TACTICO",
        "filters": [
            ("23", "Episodic Pivot (EP)", "Qullamaggie (18)", "Reacciones explosivas a earnings/catalizadores que inician una nueva tendencia institucional.",
             ["* Salto en Ventana de 10 Sesiones: Ganancia Diaria >= +7.5% (+8%) O Gap Apertura >= +4% (+5%)",
              "* Explosion de Volumen: RVOL 20d >= 1.05x - 1.2x o Volumen >= 400k - 500k (o $Vol >= $2M)",
              "* Confirmacion de Vela: Close > High Previo o Daily Closing Range (DCR) >= 40%"]),
            ("24", "Up on Volume", "Deepvue (64)", "Sesiones de expansion alcista con volumen institucional y cierre en la mitad superior.",
             ["* Avance Diario: Chg Today >= +1.0% (o >= +1.5% en la sesion previa)",
              "* Calidad de Cierre (DCR): Posicion en Rango Diario >= 45% - 50%",
              "* Participacion Institucional: RVOL 20d >= 0.95x - 1.0x"]),
            ("25", "Pre-Market & Gap Ups", "TradingVolt Live", "Acciones en juego antes de la apertura con gap alcista y liquidez para operativa ORB.",
             ["* Precio >= $3.00 - $5.00 con Gap Apertura >= +0.5% a +2.0% (o Chg Today >= +1.0%)",
              "* Actividad Relativa: RVOL >= 1.1x o Posicion en Rango >= 30%",
              "* Liquidez Institucional: $Vol 20d > $10M (tolerancia >= $1.5M) o Market Cap > $500M"]),
            ("26", "Post-Market Movers", "Deepvue (21)", "Reacciones inmediatas after-hours (16:00-20:00 ET) a reportes de Earnings o noticias.",
             ["* Precio de Cierre >= $5.00",
              "* Magnitud After-Hours: |Movimiento| >= 2.0% en cualquier direccion (>= +2% o <= -2%)",
              "* Liquidez Institucional: $Vol 20d >= $10,000,000 diarios o Market Cap > $500M"]),
            ("27", "Pullback & Breakout 20d", "TradingVolt Core", "Configuraciones clasicas de rebote en media movil (SMA 20/50) y ruptura de 20 sesiones.",
             ["* Pullback SMA 20/50: SMA50 > SMA200, distancia a SMA20 <= 2.0% (o SMA50 <= 2.5%) y RSI 40-60",
              "* Breakout 20d: Close Hoy >= Max(High ultimas 20 sesiones) confirmado con RVOL >= 1.2x"]),
            ("28", "Top Gappers & Maximos", "DayTrade 5-Min", "Escaneres intradia sobre velas de 5 minutos para capturar momentum direccional en vivo.",
             ["* Top Gappers & RVOL: Precio >= $5.00, |Gap| >= 2.0% y RVOL(5m vs 30 barras) >= 1.5x",
              "* Impulso en Maximos: Gap > 0%, RVOL >= 1.2x-1.5x y en el Top 15% del rango intradia (>= 85%)"]),
            ("29", "Daily Pivot Breakout", "Pivot Strategy (42)", "Breakouts de pivotes confirmados (5L/5R, Lookback 100) con ROC, RVOL y pendiente EMA 100.",
             ["* Pivote Confirmado: Left Strength = 5, Right Strength = 5 en Pivot Lookback = 100 velas",
              "* Momentum & Volumen: ROC(100d) >= +30% y RVOL(20d) > 1.0x (Volumen > Promedio 20d)",
              "* Tendencia: EMA(100) con EMA Slope Lookback(100d, Smooth=1) >= +20% + Momentum Candle Colors"]),
        ]
    }
]

FORMULAS = [
    ("ADR 10d (Average Daily Range %)", "ADR_10 = ( Mean_10d( High / Low ) - 1.0 ) * 100", "Umbral Pure Momentum: > 3.0% (ideal 3.5% a 8.0%)"),
    ("RMV 15d (Range Volatility Deepvue)", "RMV_15 = ( (Max(High,15) - Min(Low,15)) / Min(Low,15) ) * 100", "Zonas: <= 10% (Tight Verde / Compresion) | 10%-15% (Nivel 1)"),
    ("DCR (Daily Closing Range %)", "DCR = ( (Close - Low) / (High - Low) ) * 100", "Mide la fortaleza del cierre dentro de la vela diaria (0% a 100%)"),
    ("RVOL Intradia Ajustado por Sesion", "RVOL_Proj = ( Vol_Hoy / Fraccion_Sesion ) / SMA(Vol, 20d)", "Ajusta el volumen acumulado segun los minutos transcurridos (9:30-16:00 ET)"),
    ("IBD Relative Strength Ponderado", "RS_Raw = 0.40*(3M) + 0.20*(6M) + 0.20*(9M) + 0.20*(12M)", "Escala percentil 1 a 99; lideres institucionales operan con RS >= 85"),
    ("Dealer Gamma Exposure (GEX CBOE)", "GEX_$M = Sign * Gamma_BS * OI * 100 * Spot^2 * 0.01 / 1e6", "Net GEX > 0: Long Gamma (Rango) | Net GEX < 0: Short Gamma (Volatilidad)"),
]


def _pdf_escape(s: str) -> str:
    b = s.encode("cp1252", errors="replace").decode("cp1252")
    return b.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class VectorPDFBuilder:
    def __init__(self, width=841.89, height=595.28):
        self.w = width
        self.h = height
        self.pages = []
        self.cur = []

    def new_page(self):
        if self.cur:
            self.pages.append("\n".join(self.cur))
        self.cur = []
        self.rect(0, 0, self.w, self.h, fill=(0.043, 0.059, 0.098))

    def rect(self, x, y_top, w, h, fill=None, stroke=None, line_w=0.6):
        y_pdf = self.h - y_top - h
        cmds = [f"{line_w:.2f} w"]
        if fill:
            cmds.append(f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg")
        if stroke:
            cmds.append(f"{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG")
        op = "B" if (fill and stroke) else ("f" if fill else "S")
        cmds.append(f"{x:.2f} {y_pdf:.2f} {w:.2f} {h:.2f} re {op}")
        self.cur.append(" ".join(cmds))

    def text(self, x, y_top, txt, font="F1", size=9.0, color=(0.97, 0.98, 0.99)):
        y_pdf = self.h - y_top
        esc = _pdf_escape(txt)
        self.cur.append(
            f"BT /{font} {size:.1f} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg {x:.2f} {y_pdf:.2f} Td ({esc}) Tj ET"
        )

    def draw_header(self, page_num, total_pages):
        self.rect(24, 18, self.w - 48, 44, fill=(0.059, 0.090, 0.165), stroke=(0.196, 0.255, 0.333), line_w=0.8)
        self.rect(24, 18, 5, 44, fill=(0.0, 0.94, 1.0))
        self.text(38, 33, "TRADINGVOLT INSTITUTIONAL QUANT DESK  |  DOCUMENTACION TECNICA OFICIAL", font="F2", size=8.5, color=(0.22, 0.74, 0.97))
        self.text(38, 49, "Catalogo Maestro de los 28 Filtros Cuantitativos (Reverse Engineering & Parametros Exactos)", font="F2", size=14.0, color=(1.0, 1.0, 1.0))
        self.text(self.w - 175, 35, "VERSION: v2.5 Quant Pipeline", font="F3", size=8.5, color=(0.58, 0.64, 0.72))
        self.text(self.w - 175, 49, f"PAGINA {page_num} DE {total_pages}  |  OCT 2026", font="F3", size=8.5, color=(0.0, 1.0, 0.53))

    def draw_footer(self, page_num, total_pages):
        self.rect(24, self.h - 24, self.w - 48, 0.6, fill=(0.12, 0.16, 0.23))
        self.text(24, self.h - 12, "TradingVolt Institutional Terminal & Market Desk  •  Especificacion Matematica de Escaneres y Motores Cuantitativos", font="F1", size=7.5, color=(0.40, 0.45, 0.53))
        self.text(self.w - 130, self.h - 12, f"Pagina {page_num} / {total_pages}", font="F3", size=7.5, color=(0.22, 0.74, 0.97))

    def draw_table_header(self, y):
        self.rect(24, y, self.w - 48, 16, fill=(0.118, 0.161, 0.231), stroke=(0.20, 0.25, 0.33), line_w=0.5)
        self.text(29, y + 11.5, "#", font="F2", size=8.0, color=(0.22, 0.74, 0.97))
        self.text(48, y + 11.5, "FILTRO CUANTITATIVO", font="F2", size=8.0, color=(0.22, 0.74, 0.97))
        self.text(162, y + 11.5, "ORIGEN / POOL", font="F2", size=8.0, color=(0.22, 0.74, 0.97))
        self.text(252, y + 11.5, "OBJETIVO ESTRATEGICO / QUE BUSCA", font="F2", size=8.0, color=(0.22, 0.74, 0.97))
        self.text(446, y + 11.5, "METRICAS, PARAMETROS & REGLAS EXACTAS DE FILTRADO", font="F2", size=8.0, color=(0.22, 0.74, 0.97))
        return y + 16

    def save(self, out_path):
        if self.cur:
            self.pages.append("\n".join(self.cur))
            self.cur = []

        objects = []
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        page_count = len(self.pages)
        kids_refs = " ".join([f"{6 + i*2} 0 R" for i in range(page_count)])
        objects.append(f"<< /Type /Pages /Kids [{kids_refs}] /Count {page_count} >>".encode("ascii"))
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>")

        for i, p_stream in enumerate(self.pages):
            page_obj_id = 6 + i * 2
            content_obj_id = page_obj_id + 1
            p_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.w:.2f} {self.h:.2f}] "
                f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> "
                f"/Contents {content_obj_id} 0 R >>"
            ).encode("ascii")
            stream_bytes = p_stream.encode("cp1252", errors="replace")
            c_dict = f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii") + stream_bytes + b"\nendstream"
            objects.append(p_dict)
            objects.append(c_dict)

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for idx, obj_bytes in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f"{idx} 0 obj\n".encode("ascii"))
            out.extend(obj_bytes)
            out.extend(b"\nendobj\n")

        xref_pos = len(out)
        out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

        out.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
        )
        with open(out_path, "wb") as f:
            f.write(out)


def build_master_filters_pdf():
    pdf = VectorPDFBuilder()
    total_pages = 3
    page_plan = [
        [SECTIONS[0], SECTIONS[1]],
        [SECTIONS[2], SECTIONS[3]],
        [SECTIONS[4]]
    ]

    for p_idx, sec_list in enumerate(page_plan, start=1):
        pdf.new_page()
        pdf.draw_header(p_idx, total_pages)
        y = 68.0

        for sec in sec_list:
            pdf.rect(24, y, pdf.w - 48, 17, fill=(0.067, 0.094, 0.153), stroke=(0.12, 0.16, 0.23), line_w=0.6)
            pdf.rect(24, y, 4, 17, fill=(0.063, 0.725, 0.506))
            pdf.text(34, y + 12, sec["title"], font="F2", size=9.2, color=(0.97, 0.98, 0.99))
            y += 19.0

            y = pdf.draw_table_header(y)

            for r_idx, (num, name, origin, desc, rules) in enumerate(sec["filters"]):
                row_h = 33.5
                bg = (0.059, 0.090, 0.165) if r_idx % 2 == 0 else (0.047, 0.071, 0.125)
                pdf.rect(24, y, pdf.w - 48, row_h, fill=bg, stroke=(0.118, 0.161, 0.231), line_w=0.4)

                pdf.text(29, y + 14, num, font="F3", size=8.8, color=(0.22, 0.74, 0.97))
                pdf.text(48, y + 14, name, font="F2", size=8.6, color=(1.0, 1.0, 1.0))
                pdf.text(162, y + 14, origin, font="F3", size=7.6, color=(0.98, 0.75, 0.14))

                wrapped_desc = textwrap.wrap(desc, width=36)[:3]
                for l_i, line_txt in enumerate(wrapped_desc):
                    pdf.text(252, y + 10.5 + l_i * 9.5, line_txt, font="F1", size=7.5, color=(0.88, 0.91, 0.94))

                for r_i, rule_txt in enumerate(rules[:3]):
                    col_r = (0.0, 1.0, 0.53) if r_i == 0 else (0.94, 0.96, 0.98)
                    pdf.text(446, y + 10.5 + r_i * 9.5, rule_txt, font="F1", size=7.4, color=col_r)

                y += row_h

            y += 6.0

        if p_idx == 3:
            pdf.rect(24, y, pdf.w - 48, 17, fill=(0.067, 0.094, 0.153), stroke=(0.12, 0.16, 0.23), line_w=0.6)
            pdf.rect(24, y, 4, 17, fill=(0.22, 0.74, 0.97))
            pdf.text(34, y + 12, "6. FORMULARIO MATEMATICO DE INDICADORES BASE DEL MOTOR", font="F2", size=9.2, color=(0.97, 0.98, 0.99))
            y += 22.0

            card_w = (pdf.w - 60) / 2.0
            card_h = 46.0
            for f_idx, (f_title, f_eq, f_note) in enumerate(FORMULAS):
                col_idx = f_idx % 2
                row_idx = f_idx // 2
                cx = 24 + col_idx * (card_w + 12)
                cy = y + row_idx * (card_h + 7)
                pdf.rect(cx, cy, card_w, card_h, fill=(0.059, 0.090, 0.165), stroke=(0.15, 0.22, 0.32), line_w=0.5)
                pdf.rect(cx, cy, 3, card_h, fill=(0.22, 0.74, 0.97))
                pdf.text(cx + 10, cy + 12, f_title, font="F2", size=8.5, color=(0.22, 0.74, 0.97))
                pdf.rect(cx + 10, cy + 16, card_w - 20, 14, fill=(0.03, 0.05, 0.08), stroke=(0.12, 0.18, 0.26), line_w=0.4)
                pdf.text(cx + 15, cy + 26, f_eq, font="F3", size=8.0, color=(0.0, 1.0, 0.53))
                pdf.text(cx + 10, cy + 40, f_note, font="F1", size=7.6, color=(0.80, 0.84, 0.90))

        pdf.draw_footer(p_idx, total_pages)

    pdf.save(PDF_OUT)
    shutil.copy2(PDF_OUT, PDF_ARTIFACT)
    print(f"Vector PDF generated successfully: {PDF_OUT} ({os.path.getsize(PDF_OUT)} bytes)")


if __name__ == "__main__":
    build_master_filters_pdf()
