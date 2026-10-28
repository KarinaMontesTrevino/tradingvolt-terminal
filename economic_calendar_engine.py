"""
TradingVolt • Dynamic Economic Calendar Engine
=============================================
Motor Dinámico de Calendario Económico & Macro Surprises.
Soporta:
- Eventos de Alto (High 🔴) y Medio (Medium 🟡) impacto para octubre y noviembre de 2026.
- Reunión de la Reserva Federal (FOMC Rate Decision & Press Conference de Jerome Powell).
- Cobertura completa: Jobless Claims, CPI, PPI, PCE, NFP, Decisión FOMC, PIB, Retail Sales, JOLTS,
  Ventas de Vivienda, Subastas del Tesoro, ISM Manufacturing/Services, Confianza del Consumidor.
- Filtros por Semana, Mes, Día, Nivel de Impacto (High & Medium / Solo High / All) y Región.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# ----------------- MASTER CALENDARIO MACROECONÓMICO (OCTUBRE & NOVIEMBRE 2026) -----------------
ECONOMIC_EVENTS_MASTER = [
    # Thu Oct 1
    {"date": "2026-10-01", "day_label": "Thu, Oct 1", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Continuing Jobless Claims (Sep 19)", "impact": "High", "actual": "1,701", "forecast": "1,730", "previous": "1,712", "status": "better"},
    {"date": "2026-10-01", "day_label": "Thu, Oct 1", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Initial Jobless Claims (Sep 26)", "impact": "High", "actual": "197K", "forecast": "200K", "previous": "198K", "status": "better"},
    {"date": "2026-10-01", "day_label": "Thu, Oct 1", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "ISM Manufacturing PMI (Sep)", "impact": "High", "actual": "54.5", "forecast": "55.0", "previous": "54.8", "status": "worse"},
    {"date": "2026-10-01", "day_label": "Thu, Oct 1", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Construction Spending (MoM Aug)", "impact": "Medium", "actual": "-0.1%", "forecast": "0.1%", "previous": "0.2%", "status": "worse"},

    # Fri Oct 2 (Jobs Day)
    {"date": "2026-10-02", "day_label": "Fri, Oct 2", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Nonfarm Payrolls (Sep)", "impact": "High", "actual": "165K", "forecast": "145K", "previous": "133K", "status": "better"},
    {"date": "2026-10-02", "day_label": "Fri, Oct 2", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Unemployment Rate (Sep)", "impact": "High", "actual": "4.1%", "forecast": "4.2%", "previous": "4.2%", "status": "better"},
    {"date": "2026-10-02", "day_label": "Fri, Oct 2", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Average Hourly Earnings (MoM Sep)", "impact": "High", "actual": "0.3%", "forecast": "0.3%", "previous": "0.4%", "status": "better"},
    {"date": "2026-10-02", "day_label": "Fri, Oct 2", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Factory Orders (MoM Aug)", "impact": "Medium", "actual": "-0.2%", "forecast": "0.0%", "previous": "4.9%", "status": "worse"},

    # Mon Oct 5
    {"date": "2026-10-05", "day_label": "Mon, Oct 5", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "ISM Services PMI (Sep)", "impact": "High", "actual": "54.9", "forecast": "55.0", "previous": "55.4", "status": "worse"},
    {"date": "2026-10-05", "day_label": "Mon, Oct 5", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Employment Trends Index (Sep)", "impact": "Medium", "actual": "108.9", "forecast": "109.2", "previous": "109.0", "status": "neutral"},

    # Tue Oct 6
    {"date": "2026-10-06", "day_label": "Tue, Oct 6", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Trade Balance (Aug)", "impact": "Medium", "actual": "-$70.4B", "forecast": "-$70.8B", "previous": "-$78.9B", "status": "better"},

    # Wed Oct 7
    {"date": "2026-10-07", "day_label": "Wed, Oct 7", "time": "1:00 PM", "country": "US", "flag": "🇺🇸", "event": "FOMC Meeting Minutes (Septiembre)", "impact": "High", "actual": "Published", "forecast": "—", "previous": "—", "status": "neutral"},
    {"date": "2026-10-07", "day_label": "Wed, Oct 7", "time": "2:00 PM", "country": "US", "flag": "🇺🇸", "event": "Consumer Credit (Aug)", "impact": "Medium", "actual": "$8.9B", "forecast": "$12.0B", "previous": "$25.5B", "status": "worse"},

    # Thu Oct 8
    {"date": "2026-10-08", "day_label": "Thu, Oct 8", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Initial Jobless Claims (Oct 03)", "impact": "High", "actual": "197K", "forecast": "200K", "previous": "199K", "status": "better"},
    {"date": "2026-10-08", "day_label": "Thu, Oct 8", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Wholesale Inventories (MoM Aug)", "impact": "Medium", "actual": "0.1%", "forecast": "0.2%", "previous": "0.2%", "status": "neutral"},

    # Fri Oct 9
    {"date": "2026-10-09", "day_label": "Fri, Oct 9", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Michigan Consumer Sentiment (Prelim Oct)", "impact": "Medium", "actual": "68.9", "forecast": "70.8", "previous": "70.1", "status": "worse"},
    {"date": "2026-10-09", "day_label": "Fri, Oct 9", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Michigan 5-Year Inflation Expectations", "impact": "Medium", "actual": "3.0%", "forecast": "3.1%", "previous": "3.1%", "status": "better"},

    # Tue Oct 13
    {"date": "2026-10-13", "day_label": "Tue, Oct 13", "time": "5:00 AM", "country": "US", "flag": "🇺🇸", "event": "NFIB Small Business Optimism (Sep)", "impact": "Medium", "actual": "91.5", "forecast": "91.9", "previous": "91.2", "status": "better"},
    {"date": "2026-10-13", "day_label": "Tue, Oct 13", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Existing Home Sales (Sep)", "impact": "High", "actual": "3.99M", "forecast": "3.95M", "previous": "3.93M", "status": "better"},

    # Wed Oct 14 (CPI Day)
    {"date": "2026-10-14", "day_label": "Wed, Oct 14", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Consumer Price Index (CPI YoY Sep)", "impact": "High", "actual": "2.4%", "forecast": "2.3%", "previous": "2.5%", "status": "worse"},
    {"date": "2026-10-14", "day_label": "Wed, Oct 14", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Core CPI (MoM Sep)", "impact": "High", "actual": "0.3%", "forecast": "0.2%", "previous": "0.3%", "status": "worse"},
    {"date": "2026-10-14", "day_label": "Wed, Oct 14", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Producer Price Index (PPI MoM Sep)", "impact": "High", "actual": "0.0%", "forecast": "0.1%", "previous": "0.2%", "status": "better"},

    # Thu Oct 15
    {"date": "2026-10-15", "day_label": "Thu, Oct 15", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Initial Jobless Claims (Oct 10)", "impact": "High", "actual": "199K", "forecast": "200K", "previous": "198K", "status": "better"},
    {"date": "2026-10-15", "day_label": "Thu, Oct 15", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Retail Sales (MoM Sep)", "impact": "High", "actual": "0.8%", "forecast": "0.3%", "previous": "0.4%", "status": "better"},
    {"date": "2026-10-15", "day_label": "Thu, Oct 15", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Philadelphia Fed Manufacturing Index", "impact": "Medium", "actual": "10.3", "forecast": "3.0", "previous": "1.7", "status": "better"},
    {"date": "2026-10-15", "day_label": "Thu, Oct 15", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "NY Empire State Manufacturing Index", "impact": "Medium", "actual": "-11.9", "forecast": "3.8", "previous": "11.5", "status": "worse"},

    # Fri Oct 16
    {"date": "2026-10-16", "day_label": "Fri, Oct 16", "time": "8:15 AM", "country": "US", "flag": "🇺🇸", "event": "Industrial Production (MoM Sep)", "impact": "Medium", "actual": "-0.3%", "forecast": "-0.2%", "previous": "0.8%", "status": "worse"},
    {"date": "2026-10-16", "day_label": "Fri, Oct 16", "time": "8:15 AM", "country": "US", "flag": "🇺🇸", "event": "Capacity Utilization Rate (Sep)", "impact": "Medium", "actual": "77.5%", "forecast": "77.8%", "previous": "78.0%", "status": "worse"},

    # Tue Oct 20
    {"date": "2026-10-20", "day_label": "Tue, Oct 20", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Building Permits (Sep)", "impact": "High", "actual": "1.40M", "forecast": "1.39M", "previous": "1.40M", "status": "better"},
    {"date": "2026-10-20", "day_label": "Tue, Oct 20", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Housing Starts (Sep)", "impact": "Medium", "actual": "1.35M", "forecast": "1.35M", "previous": "1.36M", "status": "neutral"},

    # Wed Oct 21
    {"date": "2026-10-21", "day_label": "Wed, Oct 21", "time": "1:00 PM", "country": "US", "flag": "🇺🇸", "event": "Federal Reserve Beige Book", "impact": "Medium", "actual": "Published", "forecast": "—", "previous": "—", "status": "neutral"},

    # Thu Oct 22
    {"date": "2026-10-22", "day_label": "Thu, Oct 22", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Initial Jobless Claims (Oct 17)", "impact": "High", "actual": "195K", "forecast": "202K", "previous": "199K", "status": "better"},
    {"date": "2026-10-22", "day_label": "Thu, Oct 22", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Existing Home Sales (Oct)", "impact": "High", "actual": "4.02M", "forecast": "3.98M", "previous": "3.99M", "status": "better"},
    {"date": "2026-10-22", "day_label": "Thu, Oct 22", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "CB Leading Economic Index (MoM Sep)", "impact": "Medium", "actual": "-0.5%", "forecast": "-0.3%", "previous": "-0.2%", "status": "worse"},

    # Fri Oct 23
    {"date": "2026-10-23", "day_label": "Fri, Oct 23", "time": "8:45 AM", "country": "US", "flag": "🇺🇸", "event": "S&P Global Flash Manufacturing PMI (Oct)", "impact": "High", "actual": "51.2", "forecast": "50.8", "previous": "50.5", "status": "better"},
    {"date": "2026-10-23", "day_label": "Fri, Oct 23", "time": "8:45 AM", "country": "US", "flag": "🇺🇸", "event": "S&P Global Flash Services PMI (Oct)", "impact": "High", "actual": "54.8", "forecast": "54.2", "previous": "54.0", "status": "better"},

    # =========================================================================
    # SEMANA PRÓXIMA (OCTUBRE 26 - 31, 2026): SEMANA CLAVE FOMC FED & PIB
    # =========================================================================
    # Mon Oct 26
    {"date": "2026-10-26", "day_label": "Mon, Oct 26", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Chicago Fed National Activity Index (Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.12", "previous": "0.15", "status": "pending"},
    {"date": "2026-10-26", "day_label": "Mon, Oct 26", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "New Home Sales (Sep)", "impact": "High", "actual": "Pendiente", "forecast": "710K", "previous": "716K", "status": "pending"},
    {"date": "2026-10-26", "day_label": "Mon, Oct 26", "time": "9:30 AM", "country": "US", "flag": "🇺🇸", "event": "Dallas Fed Manufacturing Index (Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "-8.5", "previous": "-9.0", "status": "pending"},
    {"date": "2026-10-26", "day_label": "Mon, Oct 26", "time": "10:30 AM", "country": "US", "flag": "🇺🇸", "event": "2-Year Treasury Note Auction", "impact": "Medium", "actual": "Pendiente", "forecast": "4.05%", "previous": "4.12%", "status": "pending"},
    {"date": "2026-10-26", "day_label": "Mon, Oct 26", "time": "12:00 PM", "country": "US", "flag": "🇺🇸", "event": "5-Year Treasury Note Auction", "impact": "Medium", "actual": "Pendiente", "forecast": "4.10%", "previous": "4.18%", "status": "pending"},

    # Tue Oct 27
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Durable Goods Orders (Sep)", "impact": "High", "actual": "Pendiente", "forecast": "-0.2%", "previous": "0.0%", "status": "pending"},
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "8:00 AM", "country": "US", "flag": "🇺🇸", "event": "S&P/Case-Shiller Home Price Index (YoY Aug)", "impact": "Medium", "actual": "Pendiente", "forecast": "5.6%", "previous": "5.9%", "status": "pending"},
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "8:00 AM", "country": "US", "flag": "🇺🇸", "event": "FHFA House Price Index (MoM Aug)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.2%", "previous": "0.1%", "status": "pending"},
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "CB Consumer Confidence (Oct)", "impact": "High", "actual": "Pendiente", "forecast": "100.5", "previous": "98.7", "status": "pending"},
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Richmond Fed Manufacturing Index (Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "-15", "previous": "-17", "status": "pending"},
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "12:00 PM", "country": "US", "flag": "🇺🇸", "event": "7-Year Treasury Note Auction", "impact": "Medium", "actual": "Pendiente", "forecast": "4.20%", "previous": "4.25%", "status": "pending"},
    {"date": "2026-10-27", "day_label": "Tue, Oct 27", "time": "All Day", "country": "US", "flag": "🏛️", "event": "FOMC 2-Day Policy Meeting Begins (Day 1)", "impact": "High", "actual": "En Curso", "forecast": "—", "previous": "—", "status": "pending"},

    # Wed Oct 28 (FED INTEREST RATE DECISION & POWELL PRESS CONFERENCE)
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Goods Trade Balance (Sep Adv)", "impact": "Medium", "actual": "Pendiente", "forecast": "-$96.0B", "previous": "-$94.3B", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Wholesale Inventories (MoM Sep Adv)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.1%", "previous": "0.2%", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Retail Inventories Ex Auto (Sep Adv)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.3%", "previous": "0.5%", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "JOLTs Job Openings (Sep)", "impact": "High", "actual": "Pendiente", "forecast": "7.95M", "previous": "8.04M", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "9:30 AM", "country": "US", "flag": "🇺🇸", "event": "EIA Crude Oil Inventories", "impact": "High", "actual": "Pendiente", "forecast": "+1.2M", "previous": "+2.1M", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "9:30 AM", "country": "US", "flag": "🇺🇸", "event": "EIA Gasoline & Distillates Stocks", "impact": "Medium", "actual": "Pendiente", "forecast": "-1.5M", "previous": "-2.2M", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "1:00 PM", "country": "US", "flag": "🏛️", "event": "Fed Interest Rate Decision (FOMC Policy)", "impact": "High", "actual": "Pendiente", "forecast": "4.50%", "previous": "4.75%", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "1:00 PM", "country": "US", "flag": "🏛️", "event": "FOMC Statement & Policy Statement", "impact": "High", "actual": "Pendiente", "forecast": "Policy Statement", "previous": "—", "status": "pending"},
    {"date": "2026-10-28", "day_label": "Wed, Oct 28", "time": "1:30 PM", "country": "US", "flag": "🏛️", "event": "FOMC Press Conference (Jerome Powell)", "impact": "High", "actual": "Pendiente", "forecast": "Live Video", "previous": "—", "status": "pending"},

    # Thu Oct 29 (GDP Day)
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "GDP Growth Rate (Q3 Advance)", "impact": "High", "actual": "Pendiente", "forecast": "3.1%", "previous": "3.0%", "status": "pending"},
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Core PCE QoQ (Q3 Advance)", "impact": "High", "actual": "Pendiente", "forecast": "2.1%", "previous": "2.8%", "status": "pending"},
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Initial Jobless Claims (Oct 24)", "impact": "High", "actual": "Pendiente", "forecast": "205K", "previous": "195K", "status": "pending"},
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Continuing Jobless Claims (Oct 17)", "impact": "Medium", "actual": "Pendiente", "forecast": "1,875K", "previous": "1,865K", "status": "pending"},
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Pending Home Sales (MoM Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.9%", "previous": "0.6%", "status": "pending"},
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "9:30 AM", "country": "US", "flag": "🇺🇸", "event": "EIA Natural Gas Storage", "impact": "Medium", "actual": "Pendiente", "forecast": "+75B", "previous": "+80B", "status": "pending"},
    {"date": "2026-10-29", "day_label": "Thu, Oct 29", "time": "10:00 AM", "country": "US", "flag": "🇺🇸", "event": "Kansas City Fed Manufacturing Activity (Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "-5", "previous": "-8", "status": "pending"},

    # Fri Oct 30 (PCE Day)
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Core PCE Price Index (MoM Sep)", "impact": "High", "actual": "Pendiente", "forecast": "0.2%", "previous": "0.1%", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Core PCE Price Index (YoY Sep)", "impact": "High", "actual": "Pendiente", "forecast": "2.6%", "previous": "2.7%", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Employment Cost Index (Q3)", "impact": "High", "actual": "Pendiente", "forecast": "0.9%", "previous": "0.9%", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Personal Income (MoM Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.3%", "previous": "0.2%", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Personal Spending (MoM Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.4%", "previous": "0.2%", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "8:45 AM", "country": "US", "flag": "🇺🇸", "event": "Chicago PMI (Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "47.0", "previous": "46.6", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Michigan Consumer Sentiment (Final Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "69.0", "previous": "68.9", "status": "pending"},
    {"date": "2026-10-30", "day_label": "Fri, Oct 30", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Michigan 5-Year Inflation Expectations (Final)", "impact": "Medium", "actual": "Pendiente", "forecast": "3.0%", "previous": "3.0%", "status": "pending"},

    # =========================================================================
    # SEMANA NOVIEMBRE 2 - 8 (NFP & ACTIVIDAD)
    # =========================================================================
    # Mon Nov 2
    {"date": "2026-11-02", "day_label": "Mon, Nov 2", "time": "8:45 AM", "country": "US", "flag": "🇺🇸", "event": "S&P Global Manufacturing PMI (Final Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "51.5", "previous": "51.2", "status": "pending"},
    {"date": "2026-11-02", "day_label": "Mon, Nov 2", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "ISM Manufacturing PMI (Oct)", "impact": "High", "actual": "Pendiente", "forecast": "49.5", "previous": "48.9", "status": "pending"},
    {"date": "2026-11-02", "day_label": "Mon, Nov 2", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Construction Spending (MoM Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.1%", "previous": "-0.1%", "status": "pending"},

    # Tue Nov 3
    {"date": "2026-11-03", "day_label": "Tue, Nov 3", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "Factory Orders (MoM Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "0.1%", "previous": "-0.2%", "status": "pending"},
    {"date": "2026-11-03", "day_label": "Tue, Nov 3", "time": "All Day", "country": "US", "flag": "🇺🇸", "event": "Total Vehicle Sales (Oct)", "impact": "Medium", "actual": "Pendiente", "forecast": "15.9M", "previous": "15.8M", "status": "pending"},

    # Wed Nov 4
    {"date": "2026-11-04", "day_label": "Wed, Nov 4", "time": "7:15 AM", "country": "US", "flag": "🇺🇸", "event": "ADP Nonfarm Employment Change (Oct)", "impact": "High", "actual": "Pendiente", "forecast": "135K", "previous": "143K", "status": "pending"},
    {"date": "2026-11-04", "day_label": "Wed, Nov 4", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Trade Balance (Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "-$69.5B", "previous": "-$70.4B", "status": "pending"},
    {"date": "2026-11-04", "day_label": "Wed, Nov 4", "time": "9:00 AM", "country": "US", "flag": "🇺🇸", "event": "ISM Services PMI (Oct)", "impact": "High", "actual": "Pendiente", "forecast": "53.8", "previous": "54.9", "status": "pending"},

    # Thu Nov 5
    {"date": "2026-11-05", "day_label": "Thu, Nov 5", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Initial Jobless Claims (Oct 31)", "impact": "High", "actual": "Pendiente", "forecast": "208K", "previous": "205K", "status": "pending"},
    {"date": "2026-11-05", "day_label": "Thu, Nov 5", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Nonfarm Productivity (Prelim Q3)", "impact": "Medium", "actual": "Pendiente", "forecast": "2.2%", "previous": "2.5%", "status": "pending"},
    {"date": "2026-11-05", "day_label": "Thu, Nov 5", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Unit Labor Costs (Prelim Q3)", "impact": "Medium", "actual": "Pendiente", "forecast": "1.8%", "previous": "0.9%", "status": "pending"},

    # Fri Nov 6 (Nonfarm Payrolls)
    {"date": "2026-11-06", "day_label": "Fri, Nov 6", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Nonfarm Payrolls (Oct)", "impact": "High", "actual": "Pendiente", "forecast": "140K", "previous": "165K", "status": "pending"},
    {"date": "2026-11-06", "day_label": "Fri, Nov 6", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Unemployment Rate (Oct)", "impact": "High", "actual": "Pendiente", "forecast": "4.1%", "previous": "4.1%", "status": "pending"},
    {"date": "2026-11-06", "day_label": "Fri, Nov 6", "time": "7:30 AM", "country": "US", "flag": "🇺🇸", "event": "Average Hourly Earnings (MoM Oct)", "impact": "High", "actual": "Pendiente", "forecast": "0.3%", "previous": "0.4%", "status": "pending"},
    {"date": "2026-11-06", "day_label": "Fri, Nov 6", "time": "2:00 PM", "country": "US", "flag": "🇺🇸", "event": "Consumer Credit (Sep)", "impact": "Medium", "actual": "Pendiente", "forecast": "$10.5B", "previous": "$8.9B", "status": "pending"}
]


def get_filtered_economic_calendar(
    view_mode: str = "Month",
    impact_filter: str = "High & Medium (Recomendado)",
    country_filter: str = "US",
    selected_period: str = "Próxima Semana (Oct 26 - 31) • SEMANA FOMC FED"
) -> pd.DataFrame:
    """
    Filtra y devuelve eventos macro según la semana, mes, día, impacto y región.
    Soporta eventos High (🔴) y Medium (🟡).
    """
    df = pd.DataFrame(ECONOMIC_EVENTS_MASTER)
    
    # 1. Filtro de Impacto
    if "Solo High" in impact_filter or impact_filter == "High":
        df = df[df["impact"] == "High"]
    elif "High & Medium" in impact_filter:
        df = df[df["impact"].isin(["High", "Medium"])]
    # Si es "All" o "Todos", no filtra por impacto
        
    # 2. Filtro de País / Región
    if country_filter != "Global":
        df = df[df["country"] == country_filter]

    # 3. Filtro de Período Temporal
    if "Oct 26" in selected_period or "Próxima Semana" in selected_period:
        df = df[(df["date"] >= "2026-10-26") & (df["date"] <= "2026-10-31")]
    elif "Oct 19" in selected_period or "Esta Semana" in selected_period:
        df = df[(df["date"] >= "2026-10-19") & (df["date"] <= "2026-10-25")]
    elif "Nov 2" in selected_period or "Semana NFP" in selected_period or "Semana de Empleo" in selected_period:
        df = df[(df["date"] >= "2026-11-01") & (df["date"] <= "2026-11-07")]
    elif "Noviembre" in selected_period:
        df = df[df["date"] >= "2026-11-01"]
    elif "Octubre" in selected_period or view_mode == "Month":
        df = df[(df["date"] >= "2026-10-01") & (df["date"] <= "2026-10-31")]
        
    if view_mode == "Day":
        today_str = datetime.now().strftime("%Y-%m-%d")
        day_match = df[df["date"] == today_str]
        if day_match.empty:
            df = df.iloc[-8:]
        else:
            df = day_match

    return df.sort_values(["date", "time"]).reset_index(drop=True)
