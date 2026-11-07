# ⚡ Catálogo Maestro de Filtros Cuantitativos • Deepvue & TradingVolt

Documento técnico y operativo que recopila la arquitectura matemática, criterios lógicos y lectura de acción del precio de los filtros oficiales de **Deepvue** y la suite institucional **TradingVolt**.

---

## 📌 Nuevos Filtros Documentados (Deepvue Rule Builder)

### 30. Donchian (3,13) Momentum Breakout & Higher Low
* **Plataforma / Origen:** Deepvue Visual Rule Builder
* **Tipo de Setup:** Swing Trading / Breakout de Consolidación Corta
* **Timeframe:** Diario (`D`)

```text
Estructura en Deepvue:
All of the following happened:
  [D] Donchian (3, 0), Low (last)  Greater than  [D] Donchian (13, 0), Low (last)
  [D] Donchian (3, 0), Up (last)   Greater than  [D] Donchian (13, 0), Up 1 cdl. ago
```

#### A. En palabras sencillas
> *"Búscame acciones que hoy estén rompiendo el techo de las últimas dos semanas y media, pero cuyos mínimos recientes demuestren que los compradores ya están defendiendo el precio cada vez más arriba."*

#### B. Desglose Matemático y de Acción del Precio
1. **Línea 1 (`Low(3d) > Low(13d)`): Piso Ascendente (*Higher Low*)**
   * El mínimo de las últimas 3 sesiones está claramente despegado del mínimo de las últimas 13 sesiones.
   * **Objetivo:** Garantiza que el activo ya construyó un suelo superior y no viene cayendo hacia el fondo de su rango. Elimina falsos rebotes que vienen de un desplome reciente.
2. **Línea 2 (`High(3d) > High(13d, t-1)`): Rotura de Resistencia (*New 13-Day High*)**
   * El máximo más alto de las últimas 3 sesiones acaba de superar el techo previo de 13 días (hasta la vela de ayer).
   * **Objetivo:** Confirma que la ruptura es **fresca** (ocurrida en la ventana actual) y que el precio está expandiendo el rango al alza.

#### C. Diagrama de la Vela y los Canales
```text
Precio
  ▲                                     [Máximo Hoy] ◄── Supera techo Donchian 13d
  │                                         /
  │              ── Techo Donchian 13d ── ┌/┐
  │           ┌─┐                       ┌─┤ │
  │          ┌┤ │ ┌─┐       ┌─┐        ┌┤ │ │
  │          ││ ├─┤ ├─┐   ┌─┤ │       ┌┤│ │ │
  │          └┴─┘ └─┘ └─┤ ├─┤ │ ┌─┐  ┌┤│ │ │
  │                     └─┘ └─┘ └─┤ ├─┘└┴─┘ │
  │                               └─┘       └── Suelo Donchian 3d (Mínimo más alto)
  │        ──────────────────────────────────── Suelo Donchian 13d (Protegido abajo)
  └────────────────────────────────────────────────────────► Tiempo (13 sesiones / ~2.5 semanas)
```

---

### 31. Gap & Go Bullish Ignition
* **Plataforma / Origen:** Deepvue Visual Rule Builder
* **Tipo de Setup:** Catalizador de Impulso / Day Trading & Early Swing
* **Timeframe:** Diario (`D`)

```text
Estructura en Deepvue:
All of the following happened:
  [D] Price.Open (last)        Greater than  [D] Price.High 1 cdl. ago
  [D] Rvol (20, SMA, 1) (last) Greater than  Constant value 0.5
  [D] Price.Close (last)       Greater than  [D] Price.Open (last)
```

#### A. En palabras sencillas
> *"Búscame acciones que hoy hayan abierto con un salto alcista limpio por encima de todo el día de ayer, y que además sigan subiendo en verde por encima de su precio de apertura con volumen activo (un patrón clásico de Gap & Go)."*

#### B. Desglose Matemático y de Acción del Precio
1. **Línea 1 (`Open > High[1]`): Gap Alcista Puro (*True Gap Up*)**
   * El precio abre por encima del máximo absoluto de la sesión anterior.
   * **Objetivo:** Denota sorpresa institucional, desequilibrio oferta/demanda o noticias de fuerte impacto (*Earnings beat*, catalizadores, contratos).
2. **Línea 2 (`RVOL(20) > 0.50`): Filtro de Actividad Institucional**
   * El volumen relativo de hoy ya supera al menos la mitad del volumen de un día promedio completo.
   * **Objetivo:** Elimina acciones congeladas o ilíquidas donde un salto de precio ocurre por micro-transacciones sin demanda institucional.
3. **Línea 3 (`Close > Open`): Vela Verde en Expansión (*No Fade*)**
   * El precio actual cotiza por encima del precio de apertura.
   * **Objetivo:** Elimina la trampa institucional clásica de *Fade* (donde abren arriba para distribuir y vender a los novatos). Aquí la demanda sostiene y compra más arriba.

#### C. Diagrama de la Vela
```text
           [Día Hoy]
             │ High
           ┌─┴─┐
           │   │ ◄── Close (Por encima de Open: Vela Verde)
           │   │
           └─┬─┘ ◄── Open
             │ Low
        ═══════════════ [ESPACIO DE GAP LIMPIO]
             │ High
           ┌─┴─┐
           │   │
           └─┬─┘
             │ Low
          [Ayer]
```

---

## 🏛️ Resumen del Catálogo Maestro de Filtros Cuantitativos

| # | Filtro Cuantitativo | Origen / Enfoque | Criterio Matemático Clave |
| :-: | :--- | :--- | :--- |
| **01** | **Deepvue Universe** | Deepvue Core (752) | $\text{\$Vol}_{20d} \ge \$20\text{M}$, $\text{Precio} \ge \$10$, $\text{RS} > 45$, $\text{Dist}_{52w} \ge -30\%$ |
| **02** | **Liquid Leaders** | Deepvue Core (187) | $\text{\$Vol}_{20d} \ge \$15\text{M}$, $\text{Close} \ge 0.95 \times \text{SMA}_{50/200}$, $\text{ROC}_{3M} \ge +3\%$ |
| **03** | **Pure Momentum** | TradingVolt (231) | $\text{\$Vol}_{20d} \ge \$7\text{M}$, $\text{ADR}_{10d} > 3.0\%$, $\text{AS}_{1M} > 95$ o $\text{AS}_{3M} > 93$ |
| **04** | **Sustained Momentum** | Deepvue (186) | $\text{\$Vol} \ge \$10\text{M}$, $\text{ROC}_{3M} \ge +5\%$, $\text{RS} > 90$, $\text{Dist}_{52w} \ge -20\%$ |
| **05** | **Weekly Strength** | Deepvue (399) | Cierre en top 30% semanal ($\text{DCR}_{sem} \ge 70\%$), sobre $\text{EMA}_{21} / \text{SMA}_{50}$ |
| **06** | **Power 21** | Deepvue (69) | Pullback a $\text{EMA}_{21}$ ($-3.5\%$ a $+4.0\%$), $\text{ROC}_{3M} \ge +3\%$, $\text{\$Vol} \ge \$5\text{M}$ |
| **07** | **Ameet Rai: IPO 1 Yr** | Deepvue (189) | Cotización $\le 260$ días, soporte sobre $\text{EMA}_{21} / \text{SMA}_{20}$ |
| **08** | **Ameet Rai: HV Edge** | Deepvue (45) | Vol Hoy $\ge$ Máx Vol en 1 año (252d) o desde IPO o desde Earnings (63d) |
| **09** | **Ameet Rai: HTF Flags** | Deepvue (12) | Mástil $\ge +80\%$ en 20 sesiones con retroceso de bandera $\le 25\%$ |
| **10** | **Ameet Rai: Daily Liquidity** | Deepvue (296) | Volumen $\ge 8,000,000$ acciones y $\text{\$Vol} \ge \$15\text{M}$ |
| **11** | **Ameet Rai: 62.5% RS Days** | Deepvue (191) | Días verdes $\ge 62.5\%$ en ventanas de 5 a 60 días |
| **12** | **Highest Volume IPO** | Deepvue (7) | Récord de volumen desde IPO con $\text{DCR} > 40\%$ y cambio $> 0\%$ |
| **13** | **Minervini VCP Pattern** | Minervini (43) | Contracción $\text{RMV}_{15d} \le 14\%$, secado de volumen, a $\le 20\%$ de máximos |
| **14** | **Minervini Stage 2** | Minervini Trend | $\text{Close} > \text{SMA}_{50} > \text{SMA}_{150} > \text{SMA}_{200}$, a $\le 20\%$ de máximos anuales |
| **15** | **Volume Dry Up (VDU)** | Deepvue (160) | $\text{RVOL} \le 0.75\text{x}$, $\text{RMV}_{15d} \le 15\%$, soporte sobre $\text{SMA}_{50}$ |
| **16** | **Tight Range (Coiling)** | Deepvue (26) | $\text{RMV}_{15d} \le 10\%$, variación 5d $\le 4\%$ o Double Inside Day |
| **17** | **CANSLIM Official** | W. O'Neil (36) | Ventas/EPS acelerados, Etapa 2, a $\le 15\%$ de máximos, $\text{\$Vol} \ge \$5\text{M}$ |
| **18** | **CANSLIM High RS** | W. O'Neil (137) | IBD Relative Strength ponderado $> 85$, Etapa 2 sobre $\text{SMA}_{50/200}$ |
| **19** | **True Market Leaders (TML)** | BO60 Breakout (331) | Ruptura de base de 60 días ($\text{BO60}$) en zona de compra ($0.0\%$ a $+5.0\%$) |
| **20** | **Weinstein Stage 2/2A** | S. Weinstein (417) | Salida de Etapa 1 a 2A/2 con medias de 150d y 200d en pendiente alcista |
| **21** | **Pocket Pivots** | Morales & Kacher (45)| Día alcista con $\text{Vol} > \text{Máx Vol Bajista de las últimas 10 sesiones}$ |
| **22** | **David Ryan: Ants** | David Ryan Official | $\ge 11$ de 15 sesiones alcistas, avance $\ge +12\%$, liquidez institucional |
| **23** | **Episodic Pivot (EP)** | K. Qullamaggie (18) | Salto $\ge +8\%$ o Gap $\ge +5\%$ con $\text{RVOL} \ge 1.4\text{x}$ en últimas 10 sesiones |
| **24** | **Up on Volume** | Deepvue (64) | Cierre alcista, $\text{DCR} \ge 50\%$, $\text{RVOL} \ge 1.2\text{x}$ sobre $\text{SMA}_{50}$ |
| **25** | **Pre Market Movers** | TradingVolt Live | $\text{Gap} \ge +0.5\%$ a $+2.0\%$, $\text{RVOL} \ge 1.1\text{x}$, precio $\ge \$3.00$ |
| **26** | **Post Market Movers** | Deepvue (21) | $|\text{Movimiento}| \ge 2.0\%$ en after-hours con $\text{\$Vol} \ge \$10\text{M}$ |
| **27** | **Pullback SMA 20/50 & Breakout 20d** | TradingVolt Core | Rebote en media móvil corta y ruptura de máximos de 20 días con volumen |
| **28** | **Top Gappers & Intraday Highs** | Day Trading 5m | $|\text{Gap}| \ge 2.0\%$, $\text{RVOL}_{5m} \ge 1.5\text{x}$ y cotizando en top 15% del día |
| **29** | **Daily Pivot Breakout** | Mike 5L/5R (42) | Ruptura fractal ($5L/5R$, lookback 100) con $\text{ROC}_{100d} \ge +30\%$, $\text{Slope} \ge +20\%$ |
| **30** | **Donchian (3,13) Breakout** | Deepvue Visual | $\text{Low}_{3d} > \text{Low}_{13d}$ y $\text{High}_{3d} > \text{High}_{13d}[1]$ (Rotura de 2.5 semanas) |
| **31** | **Gap & Go Bullish Ignition** | Deepvue Visual | $\text{Open} > \text{High}[1]$, $\text{Close} > \text{Open}$ y $\text{RVOL}_{20d} > 0.50\text{x}$ |

---

## 🗂️ Archivos Actualizados y Disponibles

1. **Documento PDF Vectorial Oficial**:
   [`TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.pdf`](file:///C:/Users/kim17/.gemini/antigravity/scratch/trading_screener/TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.pdf)
2. **Catálogo HTML Interactivo**:
   [`TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.html`](file:///C:/Users/kim17/.gemini/antigravity/scratch/trading_screener/TradingVolt_Catalogo_Maestro_Filtros_Cuantitativos.html)
3. **Documento Markdown en Repositorio**:
   [`FILTROS_CUANTITATIVOS_DEEPVUE_TRADINGVOLT.md`](file:///C:/Users/kim17/.gemini/antigravity/scratch/trading_screener/FILTROS_CUANTITATIVOS_DEEPVUE_TRADINGVOLT.md)
