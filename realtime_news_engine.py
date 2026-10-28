"""
================================================================================
TRADINGVOLT • REAL-TIME TOP STORIES & BREAKING NEWS ENGINE (v2.5 INSTITUTIONAL)
================================================================================
Institutional Multi-Source Real-Time News Wire Aggregator:
  - Bloomberg Markets & Technology (Syndicated Institutional Wire)
  - Benzinga Pro Wire (Markets, Analyst Ratings, Earnings, Movers)
  - Reuters Financial & Global Markets Wire
  - CNBC Markets & Finance Wire (Dedicated Financial Feeds)
  - CNBC Investing & Earnings Wire
  - MarketWatch MarketPulse & Bulletins (Dow Jones Institutional Wire)
  - Wall Street Journal & Barron's Markets Wire
  - SEC EDGAR Official 8-K Breaking Corporate Filings (Material Events Only)

Features:
  - Multi-layer Institutional Gatekeeper: Eliminates personal finance Q&A
    ("The Moneyist", divorce, 401k, weddings, shopping, lifestyle, sports,
    entertainment, retail clickbait) and enforces positive market signal.
  - Publisher Verification on syndicated RSS items (<source> tag validation).
  - Clean SEC EDGAR 8-K parser translating item codes (1.01, 2.01, 2.02, 5.02)
    into readable institutional event headlines.
  - Deep Entity Recognition (~200+ major corporations + cashtags + exchange tags).
  - Automated Thematic Classification (Flash, Earnings, M&A/Deals, Analyst
    Ratings, Macro/Fed, Tech/AI, Energy/Commodities, FDA/Biotech, Institutional).
================================================================================
"""

import urllib.request
import xml.etree.ElementTree as ET
import html
import re
import time
import ssl
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

# SSL Context for permissive reading of public news feeds
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# In-memory cache
_NEWS_CACHE: Dict[str, Any] = {
    "timestamp": 0.0,
    "items": []
}
_CACHE_TTL_SECONDS = 60  # 1 minute TTL

# Institutional Source Metadata & Dedicated Financial Feeds
SOURCE_METADATA = {
    "Bloomberg": {
        "color": "#F59E0B",      # Amber / Bloomberg Orange
        "badge": "BLOOMBERG",
        "icon": "🟧",
        "allowed_publishers": ["bloomberg"],
        "url": "https://news.google.com/rss/search?q=source:Bloomberg+(stocks+OR+market+OR+earnings+OR+shares+OR+Fed+OR+economy+OR+yields+OR+oil+OR+AI+OR+deal)+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    "Benzinga": {
        "color": "#06B6D4",      # Cyan / Benzinga Blue
        "badge": "BENZINGA",
        "icon": "🟦",
        "allowed_publishers": ["benzinga"],
        "url": "https://news.google.com/rss/search?q=source:Benzinga+(stock+OR+shares+OR+earnings+OR+analyst+OR+upgrade+OR+downgrade+OR+target+OR+market+OR+ETF)+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    "Reuters": {
        "color": "#F97316",      # Bright Orange
        "badge": "REUTERS",
        "icon": "📙",
        "allowed_publishers": ["reuters"],
        "url": "https://news.google.com/rss/search?q=source:Reuters+(stocks+OR+markets+OR+shares+OR+earnings+OR+Fed+OR+economy+OR+oil+OR+bank+OR+deal+OR+revenue)+when:1d&hl=en-US&gl=US&ceid=US:en"
    },
    "CNBC": {
        "color": "#3B82F6",      # Blue (Dedicated CNBC Finance/Markets feed instead of general news)
        "badge": "CNBC MARKETS",
        "icon": "🔷",
        "allowed_publishers": ["cnbc"],
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"
    },
    "CNBC Investing": {
        "color": "#2563EB",      # Royal Blue
        "badge": "CNBC INVESTING",
        "icon": "📈",
        "allowed_publishers": ["cnbc"],
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069"
    },
    "MarketWatch": {
        "color": "#10B981",      # Emerald Green (Dedicated MarketPulse real-time market feed)
        "badge": "MARKETWATCH",
        "icon": "🟩",
        "allowed_publishers": ["marketwatch", "dow jones", "barron"],
        "url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse"
    },
    "Wall Street Journal": {
        "color": "#94A3B8",      # Slate Silver
        "badge": "WSJ / BARRON'S",
        "icon": "📰",
        "allowed_publishers": ["wall street journal", "wsj", "barron"],
        "url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain"
    },
    "SEC EDGAR (8-K)": {
        "color": "#8B5CF6",      # Violet Institutional
        "badge": "SEC 8-K",
        "icon": "🏛️",
        "allowed_publishers": ["sec"],
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-K&company=&dateb=&owner=include&start=0&count=30&output=atom"
    }
}

# Expanded Corporate Entity -> Ticker Map
PROMINENT_COMPANY_MAP = {
    "NVIDIA": "NVDA", "TESLA": "TSLA", "APPLE": "AAPL", "MICROSOFT": "MSFT",
    "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "ALPHABET": "GOOGL",
    "GOOGLE": "GOOGL", "AMD": "AMD", "INTEL": "INTC", "BROADCOM": "AVGO",
    "QUALCOMM": "QCOM", "MICRON": "MU", "SUPER MICRO": "SMCI", "PALANTIR": "PLTR",
    "COINBASE": "COIN", "MICROSTRATEGY": "MSTR", "STRATEGY": "MSTR", "ROBINHOOD": "HOOD",
    "BOEING": "BA", "AIRBUS": "EADSY", "PFIZER": "PFE", "MODERNA": "MRNA",
    "EXXON": "XOM", "CHEVRON": "CVX", "OCCIDENTAL": "OXY", "SHELL": "SHEL",
    "BP ": "BP", "CONOCOPHILLIPS": "COP", "EOG RESOURCES": "EOG", "DEVON ENERGY": "DVN",
    "MARATHON PETROLEUM": "MPC", "PBF ENERGY": "PBF", "VALERO": "VLO",
    "JPMORGAN": "JPM", "GOLDMAN SACHS": "GS", "GOLDMAN": "GS", "MORGAN STANLEY": "MS",
    "CITIGROUP": "C", "BANK OF AMERICA": "BAC", "WELLS FARGO": "WFC",
    "APOLLO GLOBAL": "APO", "APOLLO": "APO", "BLACKSTONE": "BX", "BLACKROCK": "BLK",
    "KKR": "KKR", "CARLYLE": "CG", "BROOKFIELD": "BN", "ARES MANAGEMENT": "ARES",
    "BERKSHIRE": "BRK-B", "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD", "SOLANA": "SOL-USD",
    "NETFLIX": "NFLX", "DISNEY": "DIS", "ORACLE": "ORCL", "ARM HOLDINGS": "ARM",
    "TSMC": "TSM", "TAIWAN SEMI": "TSM", "ASML": "ASML", "UBER": "UBER",
    "LYFT": "LYFT", "AIRBNB": "ABNB", "DOORDAASH": "DASH", "DOORDASH": "DASH",
    "ALIBABA": "BABA", "TENCENT": "TCEHY", "BAIDU": "BIDU", "JD.COM": "JD", "BYD": "BYDDY",
    "ELI LILLY": "LLY", "NOVO NORDISK": "NVO", "ASTRAZENECA": "AZN", "MERCK": "MRK",
    "ABBVIE": "ABBV", "AMGEN": "AMGN", "GILEAD": "GILD", "VERTEX": "VRTX", "REGENERON": "REGN",
    "HALOZYME": "HALO", "ILLUMINA": "ILMN", "CARE DX": "CDNA", "CAREDX": "CDNA",
    "CROWDSTRIKE": "CRWD", "CLOUDFLARE": "NET", "PALO ALTO": "PANW", "FORTINET": "FTNT",
    "ZSCALER": "ZS", "OKTA": "OKTA", "SENTINELONE": "S", "CYBERARK": "CYBR",
    "SNOWFLAKE": "SNOW", "SERVICENOW": "NOW", "SALESFORCE": "CRM", "WORKDAY": "WDAY",
    "ADOBE": "ADBE", "INTUIT": "INTU", "PAYCOM": "PAYC", "PAYSIGN": "PAYS",
    "SHOPIFY": "SHOP", "SPOTIFY": "SPOT", "REDDIT": "RDDT", "ROBLOX": "RBLX",
    "APP LOVIN": "APP", "APPLOVIN": "APP", "UNITY": "U", "CAVA": "CAVA", "CHIPOTLE": "CMG",
    "STARBUCKS": "SBUX", "MCDONALD'S": "MCD", "WALMART": "WMT", "COSTCO": "COST",
    "TARGET": "TGT", "HOME DEPOT": "HD", "LOWE'S": "LOW", "NIKE": "NKE", "FIGS": "FIGS",
    "ABERCROMBIE": "ANF", "CATERPILLAR": "CAT", "DEERE": "DE", "GENERAL ELECTRIC": "GE",
    "GE VERNOVA": "GEV", "GE AEROSPACE": "GE", "LOCKHEED": "LMT", "RAYTHEON": "RTX",
    "RTX": "RTX", "GENERAL DYNAMICS": "GD", "NORTHROP": "NOC", "AXON": "AXON",
    "VERTIV": "VRT", "EATON": "ETN", "QUANTA": "PWR", "CONSTELLATION ENERGY": "CEG",
    "VISTRA": "VST", "NRG ENERGY": "NRG", "CAMECO": "CCJ", "FIRST SOLAR": "FSLR",
    "ENPHASE": "ENPH", "NEXTERA": "NEE", "FREEPORT": "FCX", "NEWMONT": "NEM",
    "SOUTHERN COPPER": "SCCO", "ALBEMARLE": "ALB", "RIO TINTO": "RIO", "BHP": "BHP",
    "VISA": "V", "MASTERCARD": "MA", "PAYPAL": "PYPL", "BLOCK": "XYZ", "SOFI": "SOFI",
    "AFFIRM": "AFRM", "UPSTART": "UPST", "FORD": "F", "GENERAL MOTORS": "GM",
    "RIVIAN": "RIVN", "LUCID": "LCID", "STELLANTIS": "STLA", "TOYOTA": "TM",
    "FERRARI": "RACE", "DELL": "DELL", "HEWLETT PACKARD": "HPE", "HP ENTERPRISE": "HPE",
    "NETAPP": "NTAP", "WESTERN DIGITAL": "WDC", "SEAGATE": "STX", "CISCO": "CSCO",
    "IBM": "IBM", "ACCENTURE": "ACN", "ELON MUSK": "TSLA", "JENSEN HUANG": "NVDA",
    "TIM COOK": "AAPL", "WARREN BUFFETT": "BRK-B", "JAMIE DIMON": "JPM",
    "BILL ACKMAN": "PSHZF", "CATHIE WOOD": "ARKK", "COREWEAVE": "CRWV", "NEBIUS": "NBIS",
    "FRONTLINE": "FRO", "INTERNATIONAL SEAWAYS": "INSW", "DORIAN LPG": "LPG",
    "DHT HOLDINGS": "DHT", "EQUINOR": "EQNR", "POWER SOLUTIONS": "PSIX"
}

# Blacklist of false-positive ticker uppercase matches
TICKER_BLACKLIST = {
    "A", "I", "AN", "AM", "AT", "BY", "FOR", "IN", "IS", "IT", "OF", "ON", "OR",
    "TO", "UP", "HE", "BE", "AS", "SO", "DO", "NO", "GO", "IF", "MY", "US", "WE",
    "THE", "AND", "NEW", "TOP", "WAR", "OIL", "GAS", "GDP", "FED", "CPI", "SEC",
    "BUY", "SELL", "HOLD", "CEO", "CFO", "IPO", "ETF", "USA", "ALL", "NOW", "ONE",
    "TWO", "BIG", "DAY", "LOW", "NET", "EST", "SEE", "HOW", "WHY", "CAN", "OUT",
    "WHO", "YEN", "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "AI", "EV", "Q1", "Q2",
    "Q3", "Q4", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "LIVE", "POST", "DEAL", "BEAT", "MISS", "POW", "RUN", "DOWN",
    "UAE", "UK", "EU", "UN", "IMF", "WTO", "OPEC", "FDA", "DOJ", "FTC", "IRS", "EPA"
}

# Hard Exclusion Patterns: Personal Finance Q&A, Divorce, 401k, Weddings, Shopping, Lifestyle, Gossip, Sports
NOISE_EXCLUSION_PHRASES = [
    # Personal Finance Q&A / The Moneyist / Dear Quentin / Family & Divorce
    "my spouse", "my husband", "my wife", "my ex-", "my ex ", "my mother", "my father",
    "my parents", "my son", "my daughter", "my kids", "my children", "my brother",
    "my sister", "my friend", "my neighbor", "my boyfriend", "my girlfriend", "my partner",
    "my step", "in-laws", "our divorce", "in a divorce", "divorce", "alimony", "prenup",
    "child support", "wedding", "wedding band", "engagement ring", "jeweler", "jewelry",
    "how is that fair", "is it a bad idea", "bad idea?", "am i wrong", "should i tell",
    "dear quentin", "moneyist", "401(k)", "roth ira", "social security", "medicare",
    "medicaid", "i retired", "i'm retired", "i am retired", "retire at ", "retirement savings",
    "i inherited", "inheritance", "estate plan", "will and trust", "nursing home",
    "caregiver", "funeral", "life insurance", "credit score", "credit card debt",
    "pay off my", "student loan", "my mortgage", "refinance my", "home equity",
    "landlord", "my rent", "pocket money", "allowance", "tipping", "etiquette",
    "suze orman", "dave ramsey", "i have $", "we have $", "i'm 6", "i'm 7", "i am 6", "i am 7",
    # Consumer Shopping / Retail Dupes / Lifestyle / Travel / Lottery
    "quince", "cut-price duplicates", "online retailer known for", "best deals",
    "promo code", "coupon", "mattress", "wardrobe", "recipe", "restaurant review",
    "cruise ship", "airline miles", "hotel points", "airport lounge", "horoscope",
    "astrology", "lottery", "powerball", "mega millions", "jackpot", "weight loss workout",
    # Entertainment / Gaming / Movies / Celebrities / Sports
    "elden ring", "spider-man", "hollywood", "box office", "movie", "sequel", "trailer",
    "celebrity", "video game", "grammy", "oscar", "emmy", "taylor swift", "beyonce",
    "kardashian", "royal family", "prince harry", "meghan markle", "nfl", "nba", "mlb",
    "nhl", "super bowl", "world cup", "premier league", "champions league", "touchdown",
    "quarterback", "playoffs",
    # Retail Clickbait Fluff
    "if you invested $", "forget nvidia", "millionaire-maker", "no-brainer stock",
    "retire a millionaire"
]

# Positive Institutional Market Keywords (At least one required for non-SEC articles)
INSTITUTIONAL_SIGNAL_KEYWORDS = [
    "stock", "stocks", "share", "shares", "equity", "equities", "market", "markets",
    "wall street", "s&p", "nasdaq", "dow", "russell", "index", "indices", "futures",
    "options", "etf", "fund", "hedge fund", "private equity", "asset manager",
    "venture capital", "ipo", "offering", "buyback", "repurchase", "dividend",
    "earnings", "revenue", "profit", "margin", "ebitda", "eps", "guidance", "outlook",
    "forecast", "estimate", "quarter", "q1", "q2", "q3", "q4", "fiscal", "merger",
    "acquisition", "acquire", "acquires", "buy", "buys", "buying", "buyout", "takeover",
    "stake", "deal", "agreement", "contract", "partnership", "joint venture", "spinoff",
    "restructuring", "bankruptcy", "default", "debt", "bond", "bonds", "treasury",
    "treasuries", "yield", "yields", "spread", "credit", "fed", "federal reserve",
    "fomc", "powell", "central bank", "ecb", "boj", "boe", "pboc", "rate", "rates",
    "inflation", "cpi", "pce", "ppi", "gdp", "recession", "economy", "economic",
    "jobs", "payrolls", "unemployment", "manufacturing", "pmi", "ism", "retail sales",
    "tariff", "tariffs", "trade", "sanctions", "export", "import", "supply chain",
    "oil", "crude", "wti", "brent", "opec", "natural gas", "lng", "energy", "solar",
    "nuclear", "uranium", "gold", "silver", "copper", "lithium", "commodity",
    "commodities", "bitcoin", "crypto", "ethereum", "blockchain", "sec", "ftc", "doj",
    "fda", "antitrust", "regulator", "regulatory", "lawsuit", "settlement", "fine",
    "probe", "investigation", "clinical trial", "phase 1", "phase 2", "phase 3",
    "approval", "drug", "biotech", "pharma", "semiconductor", "chip", "chips", "gpu",
    "datacenter", "data center", "cloud", "artificial intelligence", "ai ",
    "cybersecurity", "ev ", "electric vehicle", "autonomous", "robotics", "analyst",
    "analysts", "upgrade", "upgrades", "downgrade", "downgrades", "price target",
    "overweight", "underweight", "outperform", "rating", "bull", "bear", "rally",
    "selloff", "surge", "surges", "plunge", "plunges", "jump", "jumps", "drop", "drops",
    "soar", "soars", "slump", "slumps", "gain", "gains", "loss", "losses", "valuation",
    "billion", "million", "trillion", "ceo", "cfo", "board", "activist", "investor",
    "investors", "institutional", "trader", "traders", "bank", "banks", "banking",
    "capital", "sovereign wealth", "Short interest", "squeeze"
]

# SEC 8-K Item Code Translations (Spanish Institutional Labels)
SEC_8K_ITEM_MAP = {
    "1.01": "Acuerdo Definitivo Material (M&A / Contrato)",
    "1.02": "Terminación de Acuerdo Material",
    "1.03": "Bancarrota o Reestructuración",
    "2.01": "Adquisición o Disposición de Activos",
    "2.02": "Resultados de Operaciones y Condición Financiera (Earnings)",
    "2.03": "Obligación Financiera Directa / Deuda",
    "2.04": "Evento de Aceleración de Obligación",
    "2.05": "Costos por Salida o Reestructuración",
    "2.06": "Deterioro Material de Activos (Impairment)",
    "3.01": "Aviso de Desliste o Incumplimiento Bursátil",
    "3.02": "Venta No Registrada de Acciones / Capital",
    "4.01": "Cambio en Firma Auditora",
    "4.02": "No Confiabilidad en Estados Financieros Previos (Restatement)",
    "5.01": "Cambio de Control de la Compañía",
    "5.02": "Salida o Nombramiento de Directivos / CEO / CFO",
    "5.03": "Enmienda a Estatutos Corporativos",
    "7.01": "Divulgación Regulación FD (Guidance / Presentación Institucional)",
    "8.01": "Otros Eventos Corporativos de Relevancia Material"
}


def _clean_text(raw_html: Optional[str]) -> str:
    """Strip HTML tags and unescape entities."""
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def _is_institutional_market_news(title: str, summary: str, tickers: List[str], source_name: str) -> bool:
    """
    Two-stage institutional gatekeeper:
      1. Rejects any personal finance, Q&A advice column, divorce, 401(k), wedding,
         consumer shopping, lifestyle, sports, or entertainment noise.
      2. Requires at least one verified institutional financial keyword or stock ticker.
    """
    combined = f"{title} {summary}".lower()
    title_l = title.lower().strip()
    summary_l = summary.lower().strip()

    # 1. Hard exclusion check
    for bad_phrase in NOISE_EXCLUSION_PHRASES:
        if bad_phrase in combined:
            return False

    # Reject first-person Q&A / reader letter articles (e.g. '"I retired in 2020..."' or 'My ...')
    if title_l.startswith(("my ", "i ", "i'm ", "i’ve ", "we ", "our ", "dear ", "is getting a ", "should i ", "how do i ")):
        return False
    if summary_l.startswith(('"i ', "'i ", "“i ", '"my ', "'my ", "“my ", '"we ', "“we ")):
        return False

    # SEC 8-K filings are filtered separately by material item codes
    if "SEC" in source_name:
        return True

    # 2. Positive institutional signal check
    if tickers:
        return True
    for kw in INSTITUTIONAL_SIGNAL_KEYWORDS:
        if kw in combined:
            return True

    return False


def _format_sec_8k_filing(raw_title: str, raw_summary: str) -> Optional[Dict[str, Any]]:
    """
    Parses raw SEC EDGAR 8-K Atom entry into a clean institutional headline and summary.
    Rejects trivial 8-Ks that only contain Item 9.01 (Exhibits) or administrative noise.
    """
    # Example raw_title: "8-K - FF EAI Robotics Ecosystem Inc. (0001460702) (Filer)"
    m = re.search(r'8-K(?:/A)?\s*-\s*([^()]+)\s*\((\d+)\)', raw_title)
    if m:
        comp_name = m.group(1).strip()
        cik = m.group(2).strip()
    else:
        comp_name = raw_title.replace("8-K -", "").replace("(Filer)", "").strip()
        cik = ""

    # Extract Item codes from summary
    found_items = re.findall(r'Item\s+(\d+\.\d+)', raw_summary)
    material_items = [it for it in found_items if it in SEC_8K_ITEM_MAP]

    # If the 8-K has NO material items (e.g. only Item 9.01 Financial Statements and Exhibits), skip it
    if not material_items:
        return None

    item_descriptions = [f"{SEC_8K_ITEM_MAP[it]} ({it})" for it in material_items[:3]]
    short_labels = []
    for it in material_items[:2]:
        if it == "1.01":
            short_labels.append("Acuerdo Material")
        elif it == "2.01":
            short_labels.append("M&A / Activos")
        elif it == "2.02":
            short_labels.append("Resultados / Earnings")
        elif it == "5.02":
            short_labels.append("Cambio Ejecutivo/Directorio")
        elif it == "7.01":
            short_labels.append("Reg FD / Guidance")
        elif it == "8.01":
            short_labels.append("Evento Material")
        elif it in ("2.03", "3.02"):
            short_labels.append("Emisión Deuda/Capital")
        else:
            short_labels.append(f"Item {it}")

    headline_tag = " + ".join(short_labels)
    clean_title = f"[SEC 8-K] {comp_name} — {headline_tag}"
    clean_summary = f"Reporte Oficial SEC EDGAR (CIK {cik}) • Eventos declarados: {' • '.join(item_descriptions)}."

    return {
        "title": clean_title,
        "summary": clean_summary,
        "items": material_items
    }


def _extract_tickers(title: str, text: str = "") -> List[str]:
    """
    Extract stock tickers from title and text using:
      1. Explicit cashtags: $TICKER
      2. Parenthesized exchange symbols: (NASDAQ: TICKER), (NYSE: TICKER)
      3. Prominent company name mentions (~200 institutional names)
    """
    combined = f"{title} {text}"
    found = set()

    # 1. Cashtags: $AAPL, $TSLA
    for m in re.finditer(r'\$([A-Z]{1,5})\b', combined):
        t = m.group(1).upper()
        if t not in TICKER_BLACKLIST:
            found.add(t)

    # 2. Parenthesized exchange tickers: (NASDAQ: NVDA) or (NYSE: XOM)
    for m in re.finditer(r'\((?:NYSE|NASDAQ|AMEX|BATS):\s*([A-Z]{1,5})\)', combined, re.IGNORECASE):
        t = m.group(1).upper()
        if t not in TICKER_BLACKLIST:
            found.add(t)

    # 3. Prominent Company names
    combined_upper = combined.upper()
    for comp_key, tick in PROMINENT_COMPANY_MAP.items():
        pattern = r'\b' + re.escape(comp_key.strip()) + r'\b'
        if re.search(pattern, combined_upper):
            found.add(tick)

    return sorted(list(found))[:6]


def _classify_category(title: str, text: str = "", sec_items: Optional[List[str]] = None) -> List[str]:
    """Categorize the news story into specific institutional themes."""
    combined = (f"{title} {text}").lower()
    cats = []

    if sec_items:
        if "2.02" in sec_items:
            cats.append("📊 Earnings")
        if any(x in sec_items for x in ("1.01", "2.01", "5.01")):
            cats.append("🤝 M&A")
        if "5.02" in sec_items:
            cats.append("🏦 Institutional")
        if not cats:
            cats.append("🏛️ SEC Filing")

    # Breaking / Flash
    if any(w in combined for w in ["breaking", "urgent", "emergency", "flash", "halted", "surges", "plunges", "plummets", "crashes", "skyrockets", "soars", "slumps", "record high"]):
        cats.append("🚨 FLASH")

    # Earnings & Guidance
    if any(w in combined for w in ["earnings", "revenue", "profit", "quarterly", "q1", "q2", "q3", "q4", "guidance", "outlook", "eps", "beats estimates", "misses estimates", "same-store sales", "margin", "ebitda", "dividend", "buyback"]):
        if "📊 Earnings" not in cats:
            cats.append("📊 Earnings")

    # M&A, Deals & Stakes
    if any(w in combined for w in ["acquisition", "acquire", "acquires", "merger", "buyout", "takeover", "tender offer", "to buy", "buys ", "stake in", "% stake", "spinoff", "spin-off", "joint venture", "pact", "billion deal", "million deal", "ipo", "capital raise"]):
        if "🤝 M&A" not in cats:
            cats.append("🤝 M&A")

    # Analyst Ratings & Price Targets
    if any(w in combined for w in ["upgrade", "upgrades", "downgrade", "downgrades", "price target", "overweight", "underweight", "outperform", "initiates coverage", "analyst", "wall street sees", "top pick"]):
        cats.append("🎯 Analyst Ratings")

    # Macro & Fed
    if any(w in combined for w in ["fed ", "federal reserve", "powell", "inflation", "cpi", "pce", "interest rate", "rate cut", "rate hike", "gdp", "treasury", "yield", "yields", "jobs report", "payrolls", "unemployment", "central bank", "fomc", "ecb", "boj", "tariff", "tariffs", "recession", "economy"]):
        cats.append("🏛️ Macro & Fed")

    # FDA & Biotech
    if any(w in combined for w in ["fda", "drug", "clinical trial", "phase 1", "phase 2", "phase 3", "vaccine", "biotech", "pharma", "therapy", "glp-1", "oncology"]):
        cats.append("💊 FDA / Biotech")

    # Commodities & Energy
    if any(w in combined for w in ["crude", "oil", "wti", "brent", "opec", "natural gas", "lng", "gold", "silver", "copper", "uranium", "nuclear", "energy", "refinery", "pipeline"]):
        cats.append("🛢️ Commodities")

    # Crypto
    if any(w in combined for w in ["bitcoin", "crypto", "ethereum", "btc", "cryptocurrency", "blockchain", "coinbase", "stablecoin"]):
        cats.append("🪙 Crypto")

    # AI & Tech
    if any(w in combined for w in ["artificial intelligence", " ai ", "ai-", "chip", "chips", "semiconductor", "nvidia", "gpu", "datacenter", "data center", "cloud", "openai", "cybersecurity", "robotics", "quantum", "autonomous"]):
        cats.append("💻 Tech & AI")

    if not cats:
        cats.append("🏦 Markets")

    return cats[:3]


def _format_time_ago(pub_dt: Optional[datetime]) -> str:
    """Calculate relative time string in Spanish."""
    if not pub_dt:
        return "Reciente"
    now = datetime.now(timezone.utc)
    diff = (now - pub_dt).total_seconds()

    if diff < 60:
        return "Hace instantes"
    elif diff < 3600:
        mins = max(1, int(diff / 60))
        return f"Hace {mins} min"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"Hace {hours} h"
    else:
        days = int(diff / 86400)
        return f"Hace {days} d"


def _parse_pubdate(date_str: Optional[str]) -> Optional[datetime]:
    """Parse various RSS/Atom date formats."""
    if not date_str:
        return None
    date_str = date_str.strip()
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            continue
    return None


def _fetch_single_source(source_name: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetch, validate, and parse a single institutional RSS/Atom feed."""
    url = meta["url"]
    allowed_pubs = meta.get("allowed_publishers", [])
    items_list = []
    headers = {
        'User-Agent': 'QuantTraderDesk/2.5 (Mozilla/5.0 Windows NT 10.0; Win64; x64) contact@quantvolt.org',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6.5, context=_SSL_CTX) as resp:
            data = resp.read()
            root = ET.fromstring(data)

            raw_items = root.findall('.//item')
            is_atom = False
            if not raw_items:
                raw_items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                is_atom = True

            for node in raw_items[:30]:
                if is_atom:
                    title_node = node.find('{http://www.w3.org/2005/Atom}title')
                    link_node = node.find('{http://www.w3.org/2005/Atom}link')
                    link = link_node.attrib.get('href', '') if link_node is not None else ''
                    pub_node = node.find('{http://www.w3.org/2005/Atom}updated')
                    summary_node = node.find('{http://www.w3.org/2005/Atom}summary')
                    source_tag_node = None
                else:
                    title_node = node.find('title')
                    link_node = node.find('link')
                    link = link_node.text if link_node is not None else ''
                    pub_node = node.find('pubDate')
                    summary_node = node.find('description')
                    source_tag_node = node.find('source')

                raw_title = title_node.text if title_node is not None else ""
                clean_t = _clean_text(raw_title)
                if not clean_t:
                    continue

                # Validate <source> tag on Google News syndicated items to prevent third-party blog leaks
                if source_tag_node is not None and source_tag_node.text and allowed_pubs:
                    pub_name_lower = source_tag_node.text.strip().lower()
                    if not any(ap in pub_name_lower for ap in allowed_pubs):
                        continue

                # Strip trailing source suffix
                for s_suffix in [
                    " - Bloomberg.com", " - Bloomberg", " - Reuters", " - Benzinga",
                    " - The Wall Street Journal", " - WSJ", " - Barron's", " - CNBC",
                    " - MarketWatch"
                ]:
                    if clean_t.endswith(s_suffix):
                        clean_t = clean_t[:-len(s_suffix)].strip()

                raw_summary = summary_node.text if summary_node is not None else ""
                clean_s = _clean_text(raw_summary)

                # In Google News RSS, <description> often just repeats the title and publisher name
                if clean_s and clean_t[:40].lower() in clean_s.lower() and len(clean_s) < len(clean_t) + 45:
                    clean_s = ""

                raw_pub = pub_node.text if pub_node is not None else ""
                pub_dt = _parse_pubdate(raw_pub)

                # STRICT RECENCY FILTER: Real-time desk shows only news from last 28 hours
                if pub_dt:
                    now_utc = datetime.now(timezone.utc)
                    age_seconds = (now_utc - pub_dt).total_seconds()
                    if age_seconds > 86400 * 1.2 or age_seconds < -3600:
                        continue

                sec_items = None
                if "SEC" in source_name:
                    sec_parsed = _format_sec_8k_filing(clean_t, clean_s)
                    if not sec_parsed:
                        continue
                    clean_t = sec_parsed["title"]
                    clean_s = sec_parsed["summary"]
                    sec_items = sec_parsed["items"]

                tickers = _extract_tickers(clean_t, clean_s)

                # INSTITUTIONAL GATEKEEPER: Filter out personal finance, divorce, weddings, lifestyle, etc.
                if not _is_institutional_market_news(clean_t, clean_s, tickers, source_name):
                    continue

                categories = _classify_category(clean_t, clean_s, sec_items=sec_items)

                item = {
                    "id": f"{source_name}_{hash(clean_t)}",
                    "title": clean_t,
                    "original_title": raw_title,
                    "summary": clean_s[:320] if clean_s else "",
                    "source": source_name,
                    "source_badge": meta["badge"],
                    "color": meta["color"],
                    "icon": meta["icon"],
                    "link": link or meta["url"],
                    "pub_datetime": pub_dt,
                    "pub_str": raw_pub,
                    "time_ago": _format_time_ago(pub_dt),
                    "tickers": tickers,
                    "categories": categories,
                    "is_flash": "🚨 FLASH" in categories
                }
                items_list.append(item)

    except Exception:
        pass

    return items_list


def fetch_all_news(force_refresh: bool = False, selected_sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Fetch news from all institutional sources concurrently.
    Cached for _CACHE_TTL_SECONDS to ensure ultra-fast Streamlit rendering.
    """
    global _NEWS_CACHE
    now = time.time()

    if not force_refresh and (now - _NEWS_CACHE["timestamp"]) < _CACHE_TTL_SECONDS and _NEWS_CACHE["items"]:
        items = _NEWS_CACHE["items"]
    else:
        all_items = []
        sources_to_query = SOURCE_METADATA.copy()

        with ThreadPoolExecutor(max_workers=len(sources_to_query)) as executor:
            future_to_source = {
                executor.submit(_fetch_single_source, s_name, s_meta): s_name
                for s_name, s_meta in sources_to_query.items()
            }
            for future in as_completed(future_to_source):
                try:
                    res = future.result()
                    all_items.extend(res)
                except Exception:
                    pass

        # Deduplicate similar titles across sources
        seen_titles = {}
        deduped = []
        for it in all_items:
            sig = re.sub(r'[^a-zA-Z0-9]', '', it["title"].lower())[:60]
            if sig in seen_titles:
                existing = seen_titles[sig]
                for tick in it["tickers"]:
                    if tick not in existing["tickers"]:
                        existing["tickers"].append(tick)
                continue
            seen_titles[sig] = it
            deduped.append(it)

        def _sort_key(x):
            dt = x.get("pub_datetime")
            return dt.timestamp() if dt else 0

        deduped.sort(key=_sort_key, reverse=True)

        _NEWS_CACHE["items"] = deduped
        _NEWS_CACHE["timestamp"] = now
        items = deduped

    if selected_sources:
        items = [i for i in items if i["source"] in selected_sources]

    return items


def search_news(
    query: str = "",
    category: str = "Todas",
    ticker: str = "",
    source: str = "Todas",
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """Filter and search news items by query, category, ticker, or source."""
    all_news = fetch_all_news(force_refresh=force_refresh)
    filtered = all_news

    if source and source != "Todas":
        filtered = [n for n in filtered if n["source"].lower() == source.lower()]

    if category and category != "Todas":
        filtered = [n for n in filtered if any(category.lower() in c.lower() for c in n["categories"])]

    if ticker and ticker.strip():
        t_clean = ticker.strip().upper().replace("$", "")
        filtered = [n for n in filtered if t_clean in n["tickers"]]

    if query and query.strip():
        q_lower = query.strip().lower()
        filtered = [
            n for n in filtered
            if q_lower in n["title"].lower() or q_lower in n["summary"].lower() or any(q_lower in t.lower() for t in n["tickers"])
        ]

    return filtered


def get_breaking_ticker_tape(limit: int = 12) -> List[Dict[str, Any]]:
    """Returns the most critical breaking stories and market headlines for the top marquee."""
    all_news = fetch_all_news()
    flash_news = [n for n in all_news if n["is_flash"]]
    if len(flash_news) < limit:
        flash_news.extend([n for n in all_news if not n["is_flash"]][:limit - len(flash_news)])
    return flash_news[:limit]


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("Testing realtime_news_engine v2.5 Institutional...")
    start_t = time.time()
    news = fetch_all_news(force_refresh=True)
    elapsed = time.time() - start_t
    print(f"Fetched {len(news)} clean institutional items in {elapsed:.2f} seconds.")
    for i, item in enumerate(news[:15], 1):
        print(f"{i:02d}. [{item['source_badge']}] {item['time_ago']} | ({', '.join(item['categories'])}) | {item['title']} | Tickers: {item['tickers']}")
