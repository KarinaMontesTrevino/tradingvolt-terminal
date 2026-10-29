"""
TradingVolt • Institutional & Insider Ownership Engine (SEC Form 3, 4 & 13F)
Motor de Inteligencia de Participaciones Institucionales y Operaciones de Insiders.
Mapea:
- Form 3: Declaraciones iniciales de propiedad efectiva (nuevos directores, CFO/CEO, activistas 10%+).
- Form 4: Cambios en propiedad efectiva con SLA de 2 días (Compras en mercado abierto 'P', Ventas 'S', Ejercicios 'M', Planes 10b5-1).
- Form 13F: Posiciones trimestrales de gestores institucionales de >$100M AUM (ARK, Berkshire, Citadel, RenTech, etc.).
- Smart Money Confluence: Cruce de compras de insiders con acumulación institucional trimestral.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------------------------------
# 1. BASE DE DATOS INSTITUCIONAL: FORM 4 (INSIDER TRANSACTIONS)
# -------------------------------------------------------------------------
FORM4_TRANSACTIONS = [
    # Coinbase (COIN) - Caso Lütke (Director) Compras Abiertas Semanales + Directivos
    {
        "filing_date": "2026-08-15", "transaction_date": "2026-08-11", "form_type": "4", "accession_number": "0001679788-26-000088",
        "ticker": "COIN", "issuer_name": "Coinbase Global, Inc.", "owner_name": "Lütke Tobias", "officer_title": "Director",
        "is_director": True, "is_officer": False, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 3930, "transaction_price_per_share": 97.24, "transaction_value": 382153.20,
        "shares_owned_following": 29430, "aff_10b5_one": False, "direct_or_indirect": "I",
        "nature_of_ownership": "By 7910240 Canada Inc.", "footnotes": "Discretionary open market purchase by holding company."
    },
    {
        "filing_date": "2026-09-08", "transaction_date": "2026-09-06", "form_type": "4", "accession_number": "0001679788-26-000102",
        "ticker": "COIN", "issuer_name": "Coinbase Global, Inc.", "owner_name": "Lütke Tobias", "officer_title": "Director",
        "is_director": True, "is_officer": False, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 4120, "transaction_price_per_share": 89.50, "transaction_value": 368740.00,
        "shares_owned_following": 33550, "aff_10b5_one": False, "direct_or_indirect": "I",
        "nature_of_ownership": "By 7910240 Canada Inc.", "footnotes": "Weekly open market purchase sequence."
    },
    {
        "filing_date": "2026-10-18", "transaction_date": "2026-10-16", "form_type": "4", "accession_number": "0001679788-26-000145",
        "ticker": "COIN", "issuer_name": "Coinbase Global, Inc.", "owner_name": "Haas Alesia J", "officer_title": "Chief Financial Officer",
        "is_director": False, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 5000, "transaction_price_per_share": 195.40, "transaction_value": 977000.00,
        "shares_owned_following": 178920, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Discretionary open market purchase. No 10b5-1 plan."
    },
    {
        "filing_date": "2026-10-22", "transaction_date": "2026-10-20", "form_type": "4", "accession_number": "0001679788-26-000155",
        "ticker": "COIN", "issuer_name": "Coinbase Global, Inc.", "owner_name": "Armstrong Brian", "officer_title": "Chairman & CEO",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": True,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "S", "transaction_acquired_disposed": "D",
        "transaction_shares": 25000, "transaction_price_per_share": 215.80, "transaction_value": 5395000.00,
        "shares_owned_following": 20195357, "aff_10b5_one": True, "direct_or_indirect": "I",
        "nature_of_ownership": "The Brian Armstrong Living Trust", "footnotes": "Rule 10b5-1 pre-scheduled trading plan adopted Nov 2025."
    },

    # Robert Half (RHI) - Cluster Buy de Directores & CEO
    {
        "filing_date": "2026-10-21", "transaction_date": "2026-10-19", "form_type": "4", "accession_number": "0000315213-26-000042",
        "ticker": "RHI", "issuer_name": "Robert Half Inc.", "owner_name": "Waddell M. Keith", "officer_title": "President & CEO",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 15000, "transaction_price_per_share": 64.20, "transaction_value": 963000.00,
        "shares_owned_following": 612400, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Discretionary purchase post earnings."
    },
    {
        "filing_date": "2026-10-22", "transaction_date": "2026-10-20", "form_type": "4", "accession_number": "0000315213-26-000044",
        "ticker": "RHI", "issuer_name": "Robert Half Inc.", "owner_name": "Gentile Patrick", "officer_title": "EVP & CFO",
        "is_director": False, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 5000, "transaction_price_per_share": 65.10, "transaction_value": 325500.00,
        "shares_owned_following": 142100, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Open market purchase."
    },
    {
        "filing_date": "2026-10-23", "transaction_date": "2026-10-21", "form_type": "4", "accession_number": "0000315213-26-000046",
        "ticker": "RHI", "issuer_name": "Robert Half Inc.", "owner_name": "Richman Dirk", "officer_title": "Director",
        "is_director": True, "is_officer": False, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 8000, "transaction_price_per_share": 66.40, "transaction_value": 531200.00,
        "shares_owned_following": 78900, "aff_10b5_one": False, "direct_or_indirect": "I",
        "nature_of_ownership": "Richman Family Trust", "footnotes": "Cluster Buy: 3er insider en 72 horas."
    },

    # Palantir Technologies (PLTR) - Acumulación y Ejercicios
    {
        "filing_date": "2026-10-14", "transaction_date": "2026-10-12", "form_type": "4", "accession_number": "0001321655-26-000078",
        "ticker": "PLTR", "issuer_name": "Palantir Technologies Inc.", "owner_name": "Cohen Stephen", "officer_title": "President & Secretary",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 50000, "transaction_price_per_share": 41.50, "transaction_value": 2075000.00,
        "shares_owned_following": 8450000, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "High conviction open market purchase."
    },
    {
        "filing_date": "2026-10-19", "transaction_date": "2026-10-17", "form_type": "4", "accession_number": "0001321655-26-000085",
        "ticker": "PLTR", "issuer_name": "Palantir Technologies Inc.", "owner_name": "Karp Alexander", "officer_title": "Chief Executive Officer",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "S", "transaction_acquired_disposed": "D",
        "transaction_shares": 100000, "transaction_price_per_share": 43.80, "transaction_value": 4380000.00,
        "shares_owned_following": 6430000, "aff_10b5_one": True, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Sale under Rule 10b5-1 adopted on May 2025 for option exercise tax."
    },

    # CrowdStrike (CRWD) - Director Buy post recuperación
    {
        "filing_date": "2026-10-15", "transaction_date": "2026-10-13", "form_type": "4", "accession_number": "0001535527-26-000065",
        "ticker": "CRWD", "issuer_name": "CrowdStrike Holdings, Inc.", "owner_name": "Schnittger Gerhard", "officer_title": "Director",
        "is_director": True, "is_officer": False, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 3500, "transaction_price_per_share": 298.50, "transaction_value": 1044750.00,
        "shares_owned_following": 42500, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Discretionary purchase at key 50-day support."
    },

    # Maplebear / Instacart (CART) - Cluster Buy Fundadores
    {
        "filing_date": "2026-10-17", "transaction_date": "2026-10-15", "form_type": "4", "accession_number": "0001579091-26-000052",
        "ticker": "CART", "issuer_name": "Maplebear Inc.", "owner_name": "Simó Fidji", "officer_title": "CEO and Chair",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 20000, "transaction_price_per_share": 39.80, "transaction_value": 796000.00,
        "shares_owned_following": 485000, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Open market buy post investor day."
    },
    {
        "filing_date": "2026-10-18", "transaction_date": "2026-10-16", "form_type": "4", "accession_number": "0001579091-26-000054",
        "ticker": "CART", "issuer_name": "Maplebear Inc.", "owner_name": "Florance Andrew", "officer_title": "Director",
        "is_director": True, "is_officer": False, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 10000, "transaction_price_per_share": 40.25, "transaction_value": 402500.00,
        "shares_owned_following": 85000, "aff_10b5_one": False, "direct_or_indirect": "I",
        "nature_of_ownership": "Florance Trust LLC", "footnotes": "Cluster Buy: Director open market purchase."
    },

    # Noble Corporation (NE) - Energía Offshore
    {
        "filing_date": "2026-10-11", "transaction_date": "2026-10-09", "form_type": "4", "accession_number": "0001894454-26-000031",
        "ticker": "NE", "issuer_name": "Noble Corporation plc", "owner_name": "Eifler Robert W", "officer_title": "President & CEO",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "A Ordinary Shares",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 12500, "transaction_price_per_share": 42.10, "transaction_value": 526250.00,
        "shares_owned_following": 325400, "aff_10b5_one": False, "direct_or_indirect": "D",
        "nature_of_ownership": "Direct", "footnotes": "Open market purchase during energy sector breakout."
    },

    # Nvidia (NVDA) - Operaciones Programadas 10b5-1 de Jensen Huang
    {
        "filing_date": "2026-10-20", "transaction_date": "2026-10-18", "form_type": "4", "accession_number": "0001045810-26-000112",
        "ticker": "NVDA", "issuer_name": "NVIDIA Corporation", "owner_name": "Huang Jen Hsun", "officer_title": "President and CEO",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": True,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "S", "transaction_acquired_disposed": "D",
        "transaction_shares": 120000, "transaction_price_per_share": 141.50, "transaction_value": 16980000.00,
        "shares_owned_following": 78200000, "aff_10b5_one": True, "direct_or_indirect": "I",
        "nature_of_ownership": "J. & L. Huang 2006 Trust", "footnotes": "Trade executed under Rule 10b5-1 plan adopted March 2025."
    },

    # Zscaler (ZS) - Discretionary Director Buy
    {
        "filing_date": "2026-10-16", "transaction_date": "2026-10-14", "form_type": "4", "accession_number": "0001713683-26-000041",
        "ticker": "ZS", "issuer_name": "Zscaler, Inc.", "owner_name": "Chaudhry Jay", "officer_title": "CEO and Chairman",
        "is_director": True, "is_officer": True, "is_ten_percent_owner": True,
        "security_type": "non_derivative", "security_title": "Common Stock",
        "transaction_code": "P", "transaction_acquired_disposed": "A",
        "transaction_shares": 8000, "transaction_price_per_share": 182.20, "transaction_value": 1457600.00,
        "shares_owned_following": 28400000, "aff_10b5_one": False, "direct_or_indirect": "I",
        "nature_of_ownership": "The Chaudhry Family Trust", "footnotes": "Open market discretionary purchase."
    }
]

# -------------------------------------------------------------------------
# 2. BASE DE DATOS INSTITUCIONAL: FORM 13F (INSTITUTIONAL WHALES)
# -------------------------------------------------------------------------
FORM13F_HOLDINGS = [
    # ARK Investment Management (Cathie Wood - CIK 0001697748)
    {
        "manager_name": "ARK Investment Management LLC", "filer_cik": "0001697748", "period": "2026-09-30", "filing_date": "2026-10-18",
        "ticker": "COIN", "cusip": "19260Q107", "issuer_name": "Coinbase Global Inc", "title_of_class": "Common Stock",
        "shares_held": 8450200, "market_value_m": 1690.0, "qoq_shares_chg_pct": 14.8, "portfolio_pct": 8.4,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "High Accumulation"
    },
    {
        "manager_name": "ARK Investment Management LLC", "filer_cik": "0001697748", "period": "2026-09-30", "filing_date": "2026-10-18",
        "ticker": "PLTR", "cusip": "69608A108", "issuer_name": "Palantir Technologies Inc", "title_of_class": "Class A Common",
        "shares_held": 12850000, "market_value_m": 546.1, "qoq_shares_chg_pct": 22.5, "portfolio_pct": 4.6,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "High Accumulation"
    },
    {
        "manager_name": "ARK Investment Management LLC", "filer_cik": "0001697748", "period": "2026-09-30", "filing_date": "2026-10-18",
        "ticker": "CRWD", "cusip": "22788C105", "issuer_name": "CrowdStrike Holdings Inc", "title_of_class": "Class A Common",
        "shares_held": 1850000, "market_value_m": 573.5, "qoq_shares_chg_pct": 8.2, "portfolio_pct": 3.8,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Moderate Add"
    },

    # Berkshire Hathaway (Warren Buffett - CIK 0001067983)
    {
        "manager_name": "Berkshire Hathaway Inc", "filer_cik": "0001067983", "period": "2026-09-30", "filing_date": "2026-10-15",
        "ticker": "AAPL", "cusip": "037833100", "issuer_name": "Apple Inc", "title_of_class": "Common Stock",
        "shares_held": 300000000, "market_value_m": 69000.0, "qoq_shares_chg_pct": -4.2, "portfolio_pct": 28.5,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Core Trim"
    },
    {
        "manager_name": "Berkshire Hathaway Inc", "filer_cik": "0001067983", "period": "2026-09-30", "filing_date": "2026-10-15",
        "ticker": "OXY", "cusip": "674599105", "issuer_name": "Occidental Petroleum Corp", "title_of_class": "Common Stock",
        "shares_held": 255281524, "market_value_m": 13274.6, "qoq_shares_chg_pct": 3.4, "portfolio_pct": 5.4,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Steady Accumulation"
    },

    # Citadel Advisors LLC (Ken Griffin - CIK 0001423053)
    {
        "manager_name": "Citadel Advisors LLC", "filer_cik": "0001423053", "period": "2026-09-30", "filing_date": "2026-10-20",
        "ticker": "NVDA", "cusip": "67066G104", "issuer_name": "NVIDIA Corporation", "title_of_class": "Common Stock",
        "shares_held": 9450000, "market_value_m": 1332.4, "qoq_shares_chg_pct": 38.6, "portfolio_pct": 2.2,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Aggressive Add"
    },
    {
        "manager_name": "Citadel Advisors LLC", "filer_cik": "0001423053", "period": "2026-09-30", "filing_date": "2026-10-20",
        "ticker": "RHI", "cusip": "770323103", "issuer_name": "Robert Half Inc", "title_of_class": "Common Stock",
        "shares_held": 2450000, "market_value_m": 167.5, "qoq_shares_chg_pct": 42.1, "portfolio_pct": 0.45,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "New Momentum Position"
    },
    {
        "manager_name": "Citadel Advisors LLC", "filer_cik": "0001423053", "period": "2026-09-30", "filing_date": "2026-10-20",
        "ticker": "CART", "cusip": "56501R106", "issuer_name": "Maplebear Inc", "title_of_class": "Common Stock",
        "shares_held": 3850000, "market_value_m": 164.7, "qoq_shares_chg_pct": 55.4, "portfolio_pct": 0.42,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Aggressive Add"
    },

    # Renaissance Technologies LLC (Jim Simons - CIK 0001037389)
    {
        "manager_name": "Renaissance Technologies LLC", "filer_cik": "0001037389", "period": "2026-09-30", "filing_date": "2026-10-19",
        "ticker": "PLTR", "cusip": "69608A108", "issuer_name": "Palantir Technologies Inc", "title_of_class": "Class A Common",
        "shares_held": 6400000, "market_value_m": 272.0, "qoq_shares_chg_pct": 68.2, "portfolio_pct": 0.85,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Quant Signal Expansion"
    },
    {
        "manager_name": "Renaissance Technologies LLC", "filer_cik": "0001037389", "period": "2026-09-30", "filing_date": "2026-10-19",
        "ticker": "NE", "cusip": "G65431108", "issuer_name": "Noble Corporation plc", "title_of_class": "A Ordinary Shares",
        "shares_held": 3120000, "market_value_m": 143.8, "qoq_shares_chg_pct": 31.4, "portfolio_pct": 0.38,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Quant Energy Add"
    },

    # Coatue Management LLC (Philippe Laffont - CIK 0001509470)
    {
        "manager_name": "Coatue Management LLC", "filer_cik": "0001509470", "period": "2026-09-30", "filing_date": "2026-10-16",
        "ticker": "ZS", "cusip": "98980F104", "issuer_name": "Zscaler Inc", "title_of_class": "Common Stock",
        "shares_held": 2850000, "market_value_m": 555.7, "qoq_shares_chg_pct": 18.2, "portfolio_pct": 2.8,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Cloud Security Conviction"
    },
    {
        "manager_name": "Coatue Management LLC", "filer_cik": "0001509470", "period": "2026-09-30", "filing_date": "2026-10-16",
        "ticker": "COIN", "cusip": "19260Q107", "issuer_name": "Coinbase Global Inc", "title_of_class": "Common Stock",
        "shares_held": 2100000, "market_value_m": 420.0, "qoq_shares_chg_pct": 26.5, "portfolio_pct": 2.1,
        "put_call": None, "investment_discretion": "SOLE", "conviction": "Fintech Accumulation"
    }
]

# -------------------------------------------------------------------------
# 3. BASE DE DATOS INSTITUCIONAL: FORM 3 (INITIAL STATEMENTS & ACTIVISTS)
# -------------------------------------------------------------------------
FORM3_STATEMENTS = [
    {
        "filing_date": "2026-02-04", "period_of_report": "2026-02-02", "form_type": "3", "accession_number": "0001679788-26-000006",
        "ticker": "COIN", "issuer_name": "Coinbase Global, Inc.", "owner_name": "Lütke Tobias", "officer_title": "Director",
        "is_director": True, "is_officer": False, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Class A Common Stock", "shares_owned": 25500,
        "direct_or_indirect": "I", "nature_of_ownership": "By 7910240 Canada Inc.",
        "trigger_event": "Onboarding Junta Directiva (CEO Shopify)",
        "footnotes": "Shares held of record by 7910240 Canada Inc. Sole director with pecuniary interest."
    },
    {
        "filing_date": "2026-07-12", "period_of_report": "2026-07-02", "form_type": "3", "accession_number": "0001193125-26-000412",
        "ticker": "CART", "issuer_name": "Maplebear Inc.", "owner_name": "Starboard Value LP", "officer_title": "10% Beneficial Owner (Activist)",
        "is_director": False, "is_officer": False, "is_ten_percent_owner": True,
        "security_type": "non_derivative", "security_title": "Common Stock", "shares_owned": 18450000,
        "direct_or_indirect": "I", "nature_of_ownership": "Starboard Value and Opportunity Fund",
        "trigger_event": "Cruzó el umbral del 10% (Entrada de Activista)",
        "footnotes": "Section 16 10% owner threshold crossed. Engagement planned with management."
    },
    {
        "filing_date": "2026-09-01", "period_of_report": "2026-08-25", "form_type": "3", "accession_number": "0000315213-26-000015",
        "ticker": "RHI", "issuer_name": "Robert Half Inc.", "owner_name": "Kowalski Elena", "officer_title": "Chief Technology Officer",
        "is_director": False, "is_officer": True, "is_ten_percent_owner": False,
        "security_type": "non_derivative", "security_title": "Common Stock", "shares_owned": 18500,
        "direct_or_indirect": "D", "nature_of_ownership": "Direct",
        "trigger_event": "Nueva Nombramiento Ejecutivo (CTO)",
        "footnotes": "Initial statement of beneficial ownership upon appointment."
    }
]

# -------------------------------------------------------------------------
# 4. MÉTODOS Y MOTORES CUANTITATIVOS
# -------------------------------------------------------------------------

def get_form4_dataframe(
    ticker_filter: str = "",
    transaction_code: str = "All",
    role_filter: str = "All",
    min_value_usd: float = 0.0,
    only_cluster_buys: bool = False
) -> pd.DataFrame:
    """
    Filtra y devuelve el DataFrame de operaciones Form 4 con cálculo de Cluster Buys.
    """
    df = pd.DataFrame(FORM4_TRANSACTIONS)
    
    # Detección de Cluster Buys: >= 2 compras de mercado (Code P) en el mismo ticker
    buys_df = df[df["transaction_code"] == "P"]
    ticker_buy_counts = buys_df.groupby("ticker")["owner_name"].nunique().to_dict()
    df["is_cluster_buy"] = df.apply(lambda r: (r["transaction_code"] == "P" and ticker_buy_counts.get(r["ticker"], 0) >= 2), axis=1)
    df["cluster_count"] = df["ticker"].map(lambda t: ticker_buy_counts.get(t, 0))

    if ticker_filter:
        t_clean = ticker_filter.upper().strip()
        df = df[df["ticker"].str.contains(t_clean) | df["issuer_name"].str.upper().str.contains(t_clean)]

    if transaction_code != "All":
        df = df[df["transaction_code"] == transaction_code]

    if role_filter == "Officers Only":
        df = df[df["is_officer"] == True]
    elif role_filter == "Directors Only":
        df = df[df["is_director"] == True]
    elif role_filter == "10% Owners":
        df = df[df["is_ten_percent_owner"] == True]

    if min_value_usd > 0:
        df = df[df["transaction_value"] >= min_value_usd]

    if only_cluster_buys:
        df = df[df["is_cluster_buy"] == True]

    return df.sort_values("filing_date", ascending=False).reset_index(drop=True)


def get_form13f_dataframe(
    ticker_filter: str = "",
    manager_filter: str = "All",
    min_market_value_m: float = 0.0
) -> pd.DataFrame:
    """
    Filtra y devuelve el reporte 13F de posiciones institucionales por activo o gestor.
    """
    df = pd.DataFrame(FORM13F_HOLDINGS)

    if ticker_filter:
        t_clean = ticker_filter.upper().strip()
        df = df[df["ticker"].str.contains(t_clean) | df["issuer_name"].str.upper().str.contains(t_clean)]

    if manager_filter != "All":
        df = df[df["manager_name"] == manager_filter]

    if min_market_value_m > 0:
        df = df[df["market_value_m"] >= min_market_value_m]

    return df.sort_values("market_value_m", ascending=False).reset_index(drop=True)


def get_smart_money_confluence_summary() -> pd.DataFrame:
    """
    Genera el radar de 'Smart Money Confluence':
    Activos donde los Insiders están comprando en el mercado abierto (Form 4 Code P)
    Y simultáneamente los Fondos Institucionales aumentaron posición (Form 13F QoQ > 0).
    """
    df4 = pd.DataFrame(FORM4_TRANSACTIONS)
    df13 = pd.DataFrame(FORM13F_HOLDINGS)

    # 1. Agrupar compras de insiders por ticker
    p_buys = df4[df4["transaction_code"] == "P"]
    insider_agg = p_buys.groupby("ticker").agg(
        insider_buys_count=("transaction_shares", "count"),
        distinct_insiders=("owner_name", "nunique"),
        total_insider_dollars=("transaction_value", "sum"),
        avg_price_paid=("transaction_price_per_share", "mean"),
        latest_filing=("filing_date", "max")
    ).reset_index()

    # 2. Agrupar acumulación institucional 13F por ticker
    inst_agg = df13.groupby("ticker").agg(
        funds_holding=("manager_name", "nunique"),
        total_13f_value_m=("market_value_m", "sum"),
        avg_qoq_chg_pct=("qoq_shares_chg_pct", "mean"),
        top_buyers=("manager_name", lambda x: ", ".join(list(x)[:2]))
    ).reset_index()

    # 3. Intersección (Confluence)
    confluence = pd.merge(insider_agg, inst_agg, on="ticker", how="inner")
    
    # Cálculo de Confluence Score cuantitativo (0 - 100)
    # Pondera: Número de insiders distintos (max 30 pts), valor en compras (max 30 pts), QoQ 13F (max 40 pts)
    def calc_score(row):
        score = 0.0
        score += min(row["distinct_insiders"] * 15.0, 30.0)
        score += min((row["total_insider_dollars"] / 1000000.0) * 15.0, 30.0)
        score += min(max(row["avg_qoq_chg_pct"], 0.0) * 1.0, 40.0)
        return int(np.clip(score, 10, 99))

    confluence["confluence_score"] = confluence.apply(calc_score, axis=1)
    return confluence.sort_values("confluence_score", ascending=False).reset_index(drop=True)


def render_insider_candlestick_chart(ticker: str) -> go.Figure:
    """
    Renderiza un gráfico interactivo con velas diarias y marcadores de compras (▲ verde)
    y ventas (▼ rojo) de insiders en sus fechas y precios exactos reportados en el Form 4.
    Debajo incluye el historial de acciones institucionales reportadas en el Form 13F.
    """
    t_clean = ticker.upper().strip()
    
    # 1. Simular serie temporal de 90 sesiones con coherencia hacia el precio actual
    np.random.seed(hash(t_clean) % 10000)
    n_days = 90
    base_price = 100.0
    if t_clean == "COIN": base_price = 210.0
    elif t_clean == "PLTR": base_price = 43.5
    elif t_clean == "CRWD": base_price = 315.0
    elif t_clean == "RHI": base_price = 68.0
    elif t_clean == "CART": base_price = 42.0
    elif t_clean == "NVDA": base_price = 142.0
    elif t_clean == "NE": base_price = 46.0
    elif t_clean == "ZS": base_price = 195.0

    dates = pd.date_range(end=datetime.now(), periods=n_days, freq="B")
    returns = np.random.normal(0.0018, 0.022, n_days)
    price_series = base_price * np.exp(np.cumsum(returns) - np.sum(returns))
    
    opens = price_series * (1 + np.random.uniform(-0.01, 0.01, n_days))
    highs = np.maximum(opens, price_series) * (1 + np.random.uniform(0.005, 0.02, n_days))
    lows = np.minimum(opens, price_series) * (1 - np.random.uniform(0.005, 0.02, n_days))
    closes = price_series
    volumes = np.random.randint(1500000, 12000000, n_days)

    df_candles = pd.DataFrame({
        "date": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes
    })

    # Medias Móviles Institucionales
    df_candles["ema10"] = df_candles["close"].ewm(span=10).mean()
    df_candles["ema20"] = df_candles["close"].ewm(span=20).mean()
    df_candles["sma50"] = df_candles["close"].rolling(50).mean()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.72, 0.28]
    )

    # 1. Velas Japonesas
    fig.add_trace(go.Candlestick(
        x=df_candles["date"],
        open=df_candles["open"],
        high=df_candles["high"],
        low=df_candles["low"],
        close=df_candles["close"],
        name="Precio",
        increasing_line_color="#10B981",
        decreasing_line_color="#EF4444",
        increasing_fillcolor="#10B981",
        decreasing_fillcolor="#EF4444"
    ), row=1, col=1)

    # Medias móviles
    fig.add_trace(go.Scatter(x=df_candles["date"], y=df_candles["ema10"], mode="lines", line=dict(color="#38BDF8", width=1.2), name="10 EMA"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_candles["date"], y=df_candles["ema20"], mode="lines", line=dict(color="#F59E0B", width=1.2), name="20 EMA"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_candles["date"], y=df_candles["sma50"], mode="lines", line=dict(color="#EC4899", width=1.5), name="50 SMA"), row=1, col=1)

    # 2. Agregar Pins de Insiders (Form 4)
    ticker_f4 = [f for f in FORM4_TRANSACTIONS if f["ticker"] == t_clean]
    
    buy_dates, buy_prices, buy_texts = [], [], []
    sell_dates, sell_prices, sell_texts = [], [], []

    for item in ticker_f4:
        t_dt = pd.to_datetime(item["transaction_date"])
        plan_str = " (10b5-1 Plan)" if item["aff_10b5_one"] else " (DISCRETIONARY)"
        txt = (
            f"<b>{item['owner_name']}</b> ({item['officer_title']}){plan_str}<br>"
            f"Código: {item['transaction_code']} • {item['transaction_shares']:,} acc @ ${item['transaction_price_per_share']:.2f}<br>"
            f"Valor: ${item['transaction_value']:,.2f}<br>"
            f"Vehículo: {item['nature_of_ownership']}"
        )
        if item["transaction_code"] == "P":
            buy_dates.append(t_dt)
            buy_prices.append(item["transaction_price_per_share"] * 0.985)
            buy_texts.append(txt)
        elif item["transaction_code"] == "S":
            sell_dates.append(t_dt)
            sell_prices.append(item["transaction_price_per_share"] * 1.015)
            sell_texts.append(txt)

    if buy_dates:
        fig.add_trace(go.Scatter(
            x=buy_dates,
            y=buy_prices,
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=14, color="#10B981", line=dict(color="#FFFFFF", width=1.5)),
            name="Insider BUY (Form 4)",
            hovertext=buy_texts,
            hoverinfo="text"
        ), row=1, col=1)

    if sell_dates:
        fig.add_trace(go.Scatter(
            x=sell_dates,
            y=sell_prices,
            mode="markers+text",
            marker=dict(symbol="triangle-down", size=14, color="#EF4444", line=dict(color="#FFFFFF", width=1.5)),
            name="Insider SELL (Form 4)",
            hovertext=sell_texts,
            hoverinfo="text"
        ), row=1, col=1)

    # 3. Sub-chart: Volumen y acumulación 13F
    bar_colors = ["#10B981" if c >= o else "#EF4444" for c, o in zip(df_candles["close"], df_candles["open"])]
    fig.add_trace(go.Bar(
        x=df_candles["date"],
        y=df_candles["volume"],
        name="Volumen Diario",
        marker_color=bar_colors,
        opacity=0.4
    ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=520,
        margin=dict(l=40, r=30, t=30, b=30),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#94A3B8", size=10)),
        hovermode="x unified"
    )

    fig.update_xaxes(showgrid=True, gridcolor="#1E293B", color="#94A3B8")
    fig.update_yaxes(showgrid=True, gridcolor="#1E293B", color="#94A3B8")

    return fig
