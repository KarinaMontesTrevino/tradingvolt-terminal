import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from leaders_universe import TML_331_TICKERS
import importlib
try:
    import pure_momentum_universe as _pmu
    importlib.reload(_pmu)
    PURE_MOMENTUM_231_TICKERS = getattr(_pmu, 'PURE_MOMENTUM_231_TICKERS', getattr(_pmu, 'PURE_MOMENTUM_205_TICKERS', []))
    PURE_MOMENTUM_205_TICKERS = getattr(_pmu, 'PURE_MOMENTUM_205_TICKERS', PURE_MOMENTUM_231_TICKERS)
except Exception:
    try:
        from pure_momentum_universe import PURE_MOMENTUM_231_TICKERS, PURE_MOMENTUM_205_TICKERS
    except Exception:
        from pure_momentum_universe import PURE_MOMENTUM_205_TICKERS
        PURE_MOMENTUM_231_TICKERS = PURE_MOMENTUM_205_TICKERS
import expanded_universes as eu
from expanded_universes import (
    SP500_COMPLETE_TICKERS,
    NASDAQ100_COMPLETE_TICKERS,
    SP400_MIDCAP_TICKERS,
    SP600_SMALLCAP_TICKERS,
    US_BROAD_MARKET_TICKERS,
    HIGH_MOMENTUM_EXPANDED_TICKERS,
    fetch_live_market_movers,
    get_premarket_top_gappers
)
try:
    from autonomous_tml_engine import get_autonomous_market_leaders
except ImportError:
    get_autonomous_market_leaders = lambda top_n=260: []

# Alpaca SDK
try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from alpaca.data.enums import DataFeed
    from alpaca.trading.client import TradingClient
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

# Listas Benchmark Oficiales de Referencia (Deepvue)
EPISODIC_PIVOT_18_TICKERS = [
    "PRSO", "BRZE", "MYGN", "SAIQ", "LION", "HAS", "XPEV", "CWST", 
    "KVYO", "SLS", "EFX", "NESR", "HTFL", "MNDY", "RVMD", "SPHR", "SYRE", "BB"
]
EPISODIC_PIVOT_8_TICKERS = EPISODIC_PIVOT_18_TICKERS
EPISODIC_PIVOT_TICKERS = EPISODIC_PIVOT_18_TICKERS

UP_ON_VOLUME_64_TICKERS = [
    "EFXT", "TBCH", "FWRG", "QDEL", "CDW", "VNCE", "INFY", "TTMI", "STRZ", "NVTS", 
    "ARXS", "CBRL", "CECO", "MDA", "EXE", "BP", "IFF", "EVTC", "TEX", "LW", 
    "CBLL", "AI", "USNA", "BCE", "CARG", "LOCO", "WS", "OTEX", "LI", "ALV", 
    "VICR", "RCI", "DRH", "HGTY", "SKM", "BLKB", "CNC", "FIS", "CORZ", "CEPU", 
    "BJRI", "FIZZ", "RELL", "GLIBK", "MOH", "AVT", "APOG", "CLMT", "EQNR", "WSE", 
    "AOS", "VNOM", "SONO", "CRGY", "MTCH", "XHR", "SXT", "PRSU", "KNTK", "BF-B", 
    "HURN", "VZ", "OXM", "NFG"
]
ANTS_3_TICKERS = ["ENGS", "JDZG", "MAGH"]





DEEPVUE_UNIVERSE_752_TICKERS = ['NU', 'INFY', 'AAPL', 'TSLA', 'PFE', 'CLF', 'PATH', 'PBR', 'VG', 'MRNA', 'SLB', 'KMI', 'KO', 'WMT', 'S', 'PLTR', 'ERIC', 'CCL', 'CCI', 'TNGX', 'HLN', 'CSX', 'PBR-A', 'MSFT', 'CSCO', 'CART', 'KDP', 'CRWD', 'DVN', 'GMAB', 'HAL', 'ACI', 'XP', 'HPQ', 'OXY', 'FIG', 'XOM', 'NOW', 'KVUE', 'PG', 'VLY', 'BMY', 'PR', 'PINS', 'DOW', 'BP', 'ROL', 'AMT', 'NTSK', 'CRBG', 'CRGY', 'MRK', 'GME', 'MNST', 'ROIV', 'CVX', 'KR', 'DT', 'AVTR', 'HST', 'IOVA', 'TXN', 'VFC', 'CSGP', 'COP', 'VTRS', 'QGEN', 'EQT', 'APA', 'CVE', 'RHI', 'ACN', 'LYFT', 'EQNR', 'DIS', 'PANW', 'ET', 'CNQ', 'SAIL', 'MO', 'CTSH', 'STNE', 'GFL', 'BRZE', 'GILD', 'MDT', 'MET', 'TALO', 'IBM', 'ASST', 'AI', 'CRM', 'FOXA', 'FAST', 'RBLX', 'KMB', 'TEVA', 'COLB', 'CHWY', 'EQH', 'BBWI', 'JNJ', 'U', 'PTEN', 'KSS', 'TENB', 'OSCR', 'AIG', 'SO', 'V', 'BAX', 'AMRX', 'CL', 'SHEL', 'NOV', 'ASAN', 'ABBV', 'RNG', 'MAT', 'PK', 'RXO', 'PAGS', 'KVYO', 'PENG', 'RY', 'DXC', 'CNC', 'BRK-B', 'M', 'VMRK', 'NDAQ', 'BEN', 'SHOP', 'EL', 'RBRK', 'RPRX', 'ZS', 'BBY', 'DHR', 'OTIS', 'GAP', 'SONY', 'RDY', 'BZ', 'UNH', 'AR', 'DHT', 'VSTM', 'FRSH', 'PAA', 'ZLAB', 'REAL', 'PM', 'BAH', 'EBAY', 'SWKS', 'PCOR', 'UNP', 'GTLB', 'AEO', 'JCI', 'SGRY', 'MAC', 'EMR', 'SLS', 'ROKU', 'UL', 'EOG', 'FTNT', 'TGT', 'PBF', 'SNOW', 'AMCR', 'RELX', 'RPD', 'ATEC', 'RRC', 'ZETA', 'DBX', 'IOT', 'EW', 'OVV', 'OKTA', 'ZM', 'SIRI', 'TRU', 'VRNS', 'ISRG', 'ASB', 'SBAC', 'LFST', 'GEHC', 'PAGP', 'EBC', 'WCN', 'NWSA', 'ZTS', 'FIGS', 'KD', 'MTCH', 'SUNB', 'LYB', 'AEP', 'Z', 'WM', 'PSX', 'HAS', 'USFD', 'RYAN', 'MA', 'SM', 'BOX', 'LION', 'OPCH', 'MAS', 'FRO', 'PEGA', 'CHKP', 'FTI', 'SU', 'OKE', 'ED', 'INTU', 'BZH', 'ABNB', 'CP', 'HOG', 'SSNC', 'EXLS', 'BRO', 'PEB', 'SPOT', 'FIVN', 'ADI', 'BUD', 'ETSY', 'DLTR', 'TAP', 'COST', 'VLO', 'BSY', 'FULT', 'XERS', 'BF-B', 'PAYX', 'DRH', 'LNG', 'LLY', 'CAI', 'TTE', 'MRSH', 'DDOG', 'FBP', 'SSL', 'WTRG', 'CME', 'BNY', 'CLBK', 'NOG', 'HLT', 'SLN', 'RELY', 'P', 'ESTC', 'WELL', 'HAFN', 'TAK', 'SAP', 'AMTM', 'EXEL', 'PCVX', 'CERT', 'AMGN', 'GO', 'TMO', 'EFX', 'CF', 'VNOM', 'CHYM', 'AMPL', 'TEAM', 'VRSK', 'ZBH', 'NE', 'DOCU', 'SYK', 'G', 'AWK', 'CHD', 'STZ', 'WDAY', 'NCNO', 'BJ', 'CTAS', 'DG', 'MTDR', 'WRBY', 'EC', 'SPGI', 'NRIX', 'BGC', 'FROG', 'RLAY', 'TECH', 'RSG', 'ROST', 'SHO', 'CBOE', 'DINO', 'ARQT', 'AJG', 'GLBE', 'NAVN', 'AVAH', 'TNDM', 'LMT', 'ALKT', 'BALL', 'ALLE', 'TTEK', 'AXTA', 'OTEX', 'LW', 'BTSG', 'CI', 'FA', 'FANG', 'PGR', 'FBIN', 'CVBF', 'A', 'DFTX', 'LOGI', 'SIGI', 'APLE', 'ADMA', 'NTAP', 'TTAN', 'ARX', 'VIR', 'RCL', 'AVPT', 'PBI', 'SLDE', 'GH', 'LIN', 'CAH', 'DNOW', 'PNW', 'CB', 'CDW', 'ADP', 'SOLV', 'PLNT', 'RLJ', 'OLLI', 'SHAK', 'AAP', 'PD', 'CCEP', 'DOCS', 'W', 'PTC', 'UCB', 'TREX', 'HNGE', 'WAY', 'HTFL', 'PRGO', 'WLTH', 'CNK', 'MUR', 'HALO', 'DV', 'ZION', 'OCTV', 'NTNX', 'CNX', 'SFNC', 'BKH', 'VRSN', 'IFF', 'SWK', 'TRI', 'MPC', 'PACS', 'APPN', 'XNCR', 'UNM', 'BSP', 'ACHC', 'TRMB', 'ANF', 'HMC', 'MSI', 'EPAM', 'QDEL', 'TDC', 'FTS', 'POOL', 'VEEV', 'KBR', 'MAR', 'PHG', 'MFC', 'SNN', 'TW', 'GDDY', 'BDX', 'INGM', 'TRV', 'ADSK', 'CON', 'PFG', 'MOH', 'VIST', 'ILMN', 'FLYW', 'SBH', 'HRB', 'CNXC', 'QLYS', 'GLOB', 'VNT', 'PRCH', 'BMO', 'BL', 'HUM', 'IT', 'LIFE', 'SDRL', 'WMG', 'VRDN', 'VSXY', 'ELV', 'COR', 'NUE', 'ROP', 'DK', 'ALL', 'KNTK', 'OLED', 'BWIN', 'QTWO', 'BIIB', 'VLTO', 'TRGP', 'LXP', 'ZYME', 'PSNL', 'RVTY', 'SEIC', 'PSN', 'WSM', 'NTRA', 'CNI', 'EYE', 'SOBO', 'FTDR', 'EXPE', 'BR', 'EWBC', 'MGNI', 'OGN', 'TCBI', 'CUBI', 'SONO', 'LDOS', 'FFBC', 'RMD', 'NIQ', 'HCA', 'BILL', 'ICLR', 'CBZ', 'HQY', 'TRMD', 'ELF', 'SN', 'SITE', 'FTRE', 'NICE', 'LAUR', 'RLI', 'EXPD', 'UBSI', 'AME', 'DEO', 'PBA', 'MKTX', 'STNG', 'IQV', 'LPX', 'WSBC', 'NWS', 'GKOS', 'ENOV', 'OUT', 'DGX', 'IMAX', 'MANH', 'AMN', 'INTA', 'APD', 'AGIO', 'EWTX', 'WAT', 'VCYT', 'INSW', 'TS', 'WING', 'CVLT', 'KFY', 'PARR', 'HWC', 'RAMP', 'DOX', 'SBLK', 'LNTH', 'ACA', 'HUBS', 'ALKS', 'OPLN', 'SIG', 'WIX', 'WKC', 'TRAX', 'EFOR', 'BNS', 'HZO', 'HSIC', 'VRTX', 'STLD', 'CRL', 'ASO', 'WK', 'EHC', 'RH', 'TBBB', 'CHRD', 'SWX', 'VOYA', 'HAE', 'TD', 'HURN', 'AVY', 'PRCT', 'MNDY', 'IEX', 'CVI', 'RGR', 'URBN', 'ACIW', 'SYNA', 'EDU', 'YOU', 'GWRE', 'RAL', 'PVH', 'MMSI', 'CBC', 'SMG', 'FOX', 'VAL', 'CDNA', 'GRMN', 'BMI', 'WST', 'LTC', 'PKG', 'SNX', 'ECO', 'ALRM', 'COKE', 'CXT', 'SMA', 'HP', 'WHD', 'CBRL', 'R', 'KTB', 'BUSE', 'E', 'PRVA', 'VIRT', 'LH', 'TDW', 'JXN', 'CWST', 'ZG', 'CNO', 'WEX', 'GFF', 'UTHR', 'CATY', 'LIND', 'MCK', 'FFIV', 'DVA', 'CCK', 'APPF', 'ITGR', 'UNFI', 'INSP', 'KMPR', 'KNSA', 'GRAL', 'PCRX', 'LIVN', 'PGNY', 'STE', 'PAY', 'BPOP', 'TYL', 'NWE', 'MSCI', 'URI', 'SEZL', 'CMBT', 'ULTA', 'FDS', 'WTW', 'TTC', 'AVNT', 'RNR', 'REGN', 'KOD', 'PAYC', 'WSFS', 'KYMR', 'NATL', 'MAZE', 'TFX', 'SYRE', 'HHH', 'GSAT', 'LPG', 'VCEL', 'ATRC', 'MMS', 'GEF', 'CM', 'RHP', 'AZTA', 'ZIM', 'ANDG', 'FIVE', 'SAM', 'MRX', 'THC', 'GCT', 'PCTY', 'IRTC', 'DLB', 'MEOH', 'BLKB', 'ZBRA', 'CLH', 'UHS', 'CHEF', 'SPSC', 'MSGS', 'SLF', 'CASY', 'ASH', 'MANE', 'FCN', 'PTGX', 'EG', 'INDB', 'SAIC', 'SXT', 'VCTR', 'MUSA', 'HNI', 'GIB', 'AMG', 'NSIT', 'AIZ', 'NDSN', 'EXPO', 'LGND', 'AFG', 'PAG', 'TX', 'FMX', 'PRGS', 'SR', 'RGA', 'TNET', 'UNF', 'BAP', 'DSGX', 'CACI', 'CFR', 'ZD', 'XRPN', 'MATX', 'TNK', 'ONC', 'MEDP', 'WTS', 'DAVE', 'IMO', 'AGYS', 'FCNCA', 'CPAY', 'MORN', 'ICUI', 'TM', 'SLAB', 'PLMR', 'DGII', 'CVSA', 'ARCB', 'RS', 'MCY', 'SUNC', 'THG', 'CIB', 'AAMI', 'SUN', 'ADUS', 'GWW', 'MSGE', 'PSMT', 'MTD', 'LOPE', 'NHC', 'HCI', 'ERIE', 'BIO', 'NIC', 'CHE', 'JOYY', 'IPAR', 'IDT', 'CRAI', 'IDCC', 'NUTX', 'DAC', 'AZO', 'NEU', 'IOSP', 'UFPT', 'KOF', 'DDS', 'BH', 'BH-A', 'GHC', 'WTM', 'BRK-A']

LIQUID_LEADERS_187_TICKERS = [
    'CART', 'CCI', 'RNG', 'GMAB', 'CHKP', 'QLYS', 'VRSK', 'ALLE', 'POOL', 'CRWD',
    'MANH', 'S', 'EQNR', 'DVN', 'ZS', 'ROP', 'SPOT', 'EPAM', 'CAKE', 'TENB',
    'RBRK', 'WCN', 'WST', 'EL', 'NET', 'CBOE', 'BR', 'CSGP', 'PBR-A', 'FOXA',
    'IT', 'QGEN', 'ISRG', 'APA', 'CACI', 'NTSK', 'AJG', 'MKTX', 'ULTA', 'PANW',
    'COP', 'CNQ', 'PSX', 'PNW', 'RRC', 'ANF', 'DT', 'ESTC', 'HAS', 'PCOR',
    'BRO', 'CDW', 'PR', 'FROG', 'CVX', 'PBF', 'SPCX', 'MRNA', 'CME', 'GILD',
    'PBR', 'HPQ', 'AR', 'BP', 'WAT', 'XOM', 'ZBRA', 'MTD', 'PFE', 'NOW',
    'RXO', 'IBM', 'LDOS', 'OVV', 'VLO', 'OLLI', 'CVE', 'MSTR', 'TSLA', 'GKOS',
    'TRI', 'HCA', 'OKTA', 'BRZE', 'DBX', 'VEEV', 'XP', 'CTSH', 'AEM', 'TTAN',
    'EFX', 'RMD', 'TW', 'FSLY', 'VMRK', 'FTNT', 'GRMN', 'WDAY', 'TEVA', 'TRU',
    'PAYC', 'MCK', 'SN', 'DINO', 'MTCH', 'TYL', 'ADP', 'PEGA', 'CRCL', 'BIIB',
    'BDX', 'MRSH', 'GTLB', 'ELF', 'SAP', 'CASY', 'HPE', 'TMO', 'HNGE', 'PINS',
    'RGEN', 'ACN', 'A', 'DHR', 'ETSY', 'TEAM', 'PLTR', 'PAYX', 'IFF', 'STZ',
    'W', 'WING', 'DOCU', 'CRL', 'REGN', 'IQV', 'SU', 'BBWI', 'MPC', 'BMNR',
    'TEM', 'CRM', 'IOT', 'CCL', 'INTU', 'DHT', 'FDS', 'HUBS', 'ABNB', 'SNOW',
    'SHEL', 'ADSK', 'CHWY', 'UTHR', 'MSFT', 'NTRA', 'ASST', 'NTAP', 'ITGR', 'HALO',
    'MRVL', 'GWRE', 'CAI', 'RVTY', 'FRO', 'NTNX', 'TWST', 'Z', 'GRAL', 'U',
    'LW', 'SYNA', 'TXG', 'WK', 'P', 'CHYM', 'ILMN', 'SHOP', 'SWKS', 'ZETA',
    'TWLO', 'MANE', 'MDB', 'OPCH', 'BSP', 'PTC', 'KOD'
]
TIGHT_RANGE_26_TICKERS = [
    'BBD', 'CIB', 'CNK', 'EBAY', 'ELF', 'FFIV', 'HAE', 'HHH', 'HUM', 'IBTA',
    'ITUB', 'KOD', 'KOF', 'PAGS', 'SIG', 'SNAP', 'SONO', 'STGW', 'UFPT', 'UNFI',
    'USPH', 'VFC', 'VRNS', 'WAT', 'WS', 'ZD'
]
POCKET_PIVOTS_45_TICKERS = [
    'KFRC', 'SAIL', 'SLB', 'REXR', 'SDRL', 'EFOR', 'KOS', 'VIST', 'DVN', 'LNG',
    'RRC', 'KRC', 'KFY', 'NMIH', 'HFWA', 'BCPC', 'HBNC', 'EBC', 'ACT', 'CHKP',
    'HQY', 'MTDR', 'FIVN', 'ZS', 'OXY', 'TALO', 'NICE', 'FULT', 'SM', 'QSI',
    'VEON', 'BY', 'RPD', 'WSFS', 'HCSG', 'ICFI', 'ARLP', 'ALLE', 'IMAX', 'ARHS',
    'ENGS', 'GDYN', 'NU', 'FFIV', 'PAGS'
]
CANSLIM_OFFICIAL_36_TICKERS = ['AAMI', 'ARQT', 'BRZE', 'CRWD', 'CVE', 'DDOG', 'DHT', 'DINO', 'ECO', 'ELF', 'FIGS', 'FROG', 'FTNT', 'GCT', 'GLBE', 'HALO', 'IOT', 'KNTK', 'KRP', 'LFST', 'LGND', 'LLY', 'LPG', 'NET', 'NTRA', 'PAGP', 'PARR', 'PAYS', 'PLMR', 'PLTR', 'PNTG', 'PTGX', 'SKWD', 'TEAM', 'TK', 'ZETA']
HV_IPO_7_TICKERS = ['AIOK', 'CBRX', 'EWZS', 'FLXR', 'GMAB', 'GPUS', 'PUSH']
HVE_7_TICKERS = HV_IPO_7_TICKERS
AMEET_RAI_IPO_1YR_189_TICKERS = ['AADX', 'ACCV', 'ADBT', 'ADIG', 'ADRX', 'AERO', 'AGBK', 'AIAI', 'AIB', 'AIBZ', 'AIOK', 'AKTS', 'ALMR', 'AMRO', 'AMSS', 'ANDG', 'APMD', 'APUR', 'ARXS', 'ATTO', 'AVEX', 'AVLN', 'AYA', 'AZIO', 'BBCI', 'BETA', 'BIOT', 'BLLN', 'BMM', 'BOBS', 'BOT', 'BPRE', 'BRUN', 'BRVE', 'BSP', 'BTGO', 'BXDC', 'CAST', 'CBC', 'CBRS', 'CCXI', 'CDNL', 'CHGA', 'CNXU', 'COAG', 'CSHR', 'CSQR', 'CTY', 'CVSA', 'CYAB', 'DMII', 'DPC', 'EDVA', 'EIKN', 'ELE', 'ELMT', 'EMAT', 'ENHA', 'EQPT', 'EROC', 'EROK', 'ETRA', 'EVMN', 'EXYN', 'FBDT', 'FDXF', 'FISN', 'FJET', 'FPS', 'FRNM', 'FRTT', 'FRVO', 'FSSL', 'GCDT', 'GENB', 'GIXI', 'GLAS', 'GLND', 'GLOO', 'GMRS', 'GMTL', 'GOOGM', 'GOOGN', 'GYGY', 'HAWK', 'HLSQ', 'HONA', 'HOS', 'HOST', 'HSLV', 'HUCK', 'IA', 'IAM', 'IEAG', 'INFQ', 'INIO', 'IOND', 'IPHX', 'IQMX', 'ITG', 'IVAI', 'JAN', 'JMKE', 'KARD', 'KBON', 'KLRA', 'LABT', 'LCLN', 'LFTO', 'LIFE', 'LIME', 'LMRI', 'LTGO', 'LYCA', 'LYNX', 'MAIR', 'MANE', 'MBGL', 'MDA', 'MDLN', 'MFP', 'MICC', 'MMED', 'MRLN', 'MWH', 'NAVN', 'NHP', 'NWCL', 'NXAT', 'NXTS', 'OBX', 'OCTV', 'ODTX', 'OFRM', 'OGG', 'OIG', 'ONEN', 'PAAI', 'PAYP', 'PBLS', 'PICS', 'PS', 'PSQL', 'PURR', 'Q', 'QMLS', 'QNT', 'QVCG', 'REF', 'RNA', 'SCAT', 'SCTX', 'SECZ', 'SHAZ', 'SKHY', 'SKYD', 'SMJF', 'SPCX', 'SPTX', 'SSMR', 'STDN', 'STLN', 'SUJA', 'SUNB', 'SUNC', 'SWMR', 'TCGX', 'TMTS', 'TRAX', 'TRXB', 'VCX', 'VGNT', 'VMET', 'VRXA', 'VSNT', 'VTIX', 'VYLR', 'WHK', 'WLTH', 'WSE', 'XE', 'XLAB', 'XMAX', 'XNDU', 'XTND', 'XZO', 'YFOR', 'YSS', 'YSWY']
AMEET_RAI_HV_EDGE_45_TICKERS = ['AIBN', 'AIOK', 'AMT', 'BOLT', 'CCI', 'CGCF', 'CTJL', 'CTMA', 'EAFH', 'EMAU', 'ENTL', 'EWZS', 'FCNCA', 'FLXR', 'GMAB', 'GMIE', 'GUAC', 'HJLY', 'IDJN', 'IEAG', 'JADB', 'JULC', 'LCIV', 'LEGO', 'LFAW', 'LTGR', 'LUNC', 'MAYC', 'OIM', 'POMG', 'PUSH', 'QJL', 'QMY', 'QQJN', 'QQMY', 'RBTX', 'RECI', 'S4-USA', 'SCJL', 'TIPD', 'TMTS', 'TPEI', 'XIII', 'XKRE', 'XLEM']
AMEET_RAI_HTF_12_TICKERS = ['MAGH', 'IRLA', 'FGC', 'BMBL', 'TJGC', 'KOD', 'MSGKW', 'SCAT', 'IPHX', 'SA40MA-NYSE', 'NH-NYSE', 'SA20MA-NYSE']
AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS = ['AAOI', 'AAPL', 'ABT', 'ACN', 'AES', 'AGG', 'AMAT', 'AMD', 'AMT', 'AMZN', 'APA', 'APH', 'APLD', 'AS', 'ASTS', 'ASX', 'AVGO', 'AVTR', 'AXTI', 'B', 'BA', 'BABA', 'BAC', 'BCS', 'BE', 'BEX', 'BIL', 'BKLN', 'BMNR', 'BMY', 'BND', 'BOIL', 'BP', 'BRZE', 'BSX', 'BX', 'C', 'CART', 'CBRS', 'CCI', 'CCL', 'CFG', 'CMCSA', 'CMG', 'CNP', 'CNQ', 'COHR', 'COIN', 'COP', 'CPB', 'CPRT', 'CRBG', 'CRCL', 'CRDO', 'CRWD', 'CRWV', 'CSCO', 'CSGP', 'CSX', 'CTSH', 'CVE', 'CVNA', 'CVX', 'DECK', 'DIS', 'DKNG', 'DOC', 'DOG', 'DOW', 'DRAM', 'DT', 'DVN', 'EEM', 'EFA', 'EQNR', 'EQT', 'ET', 'EWY', 'EWZ', 'EWZS', 'FCX', 'FIG', 'FIGR', 'FITB', 'FNB', 'FPS', 'FXI', 'GDX', 'GE', 'GFL', 'GILD', 'GIS', 'GLD', 'GLW', 'GM', 'GMAB', 'GME', 'GOOG', 'GOOGL', 'GOVT', 'GTX', 'HAL', 'HBAN', 'HDB', 'HDV', 'HIMS', 'HOOD', 'HPE', 'HPQ', 'HST', 'HWM', 'HYG', 'IBIT', 'IEF', 'IEFA', 'IEMG', 'IGV', 'INDA', 'INTC', 'INVH', 'IONQ', 'IREN', 'IUSB', 'IVZ', 'IWF', 'IWM', 'IYR', 'JAAA', 'JCPB', 'JD', 'JNK', 'JPST', 'KDP', 'KEY', 'KHC', 'KLAC', 'KMI', 'KO', 'KR', 'KRE', 'KVUE', 'KWEB', 'LBRT', 'LKQ', 'LQD', 'LRCX', 'LUV', 'LYFT', 'MBB', 'MCHP', 'MDLN', 'MDLZ', 'MDT', 'META', 'MINT', 'MNST', 'MO', 'MOS', 'MRK', 'MRNA', 'MRVL', 'MS', 'MSFT', 'MSTR', 'MU', 'MUB', 'MUU', 'MXL', 'NBIS', 'NCLH', 'NEE', 'NEM', 'NFLX', 'NKE', 'NLY', 'NOW', 'NTSK', 'NU', 'NVDA', 'NVDL', 'NVO', 'O', 'OKLO', 'ON', 'ONON', 'ORCL', 'OXY', 'PANW', 'PBR', 'PBR-A', 'PEP', 'PFE', 'PG', 'PINS', 'PLTR', 'PPL', 'PR', 'PSLV', 'PSQ', 'PYLD', 'PYPL', 'QCOM', 'QGEN', 'QQQ', 'REXR', 'RF', 'RHI', 'RKLB', 'ROIV', 'ROL', 'RSP', 'S', 'SAIL', 'SCHB', 'SCHD', 'SCHF', 'SCHG', 'SCHH', 'SCHW', 'SCHX', 'SCO', 'SDOW', 'SE', 'SGOV', 'SH', 'SHV', 'SJNK', 'SKHY', 'SLB', 'SLM', 'SLV', 'SMCI', 'SMH', 'SNDK', 'SNDQ', 'SOXL', 'SOXS', 'SOXX', 'SPCX', 'SPIB', 'SPTI', 'SPTL', 'SPXS', 'SPY', 'SPYM', 'SQQQ', 'SRLN', 'STM', 'T', 'TFC', 'TLT', 'TMUS', 'TNGX', 'TQQQ', 'TSCO', 'TSLA', 'TSLQ', 'TSM', 'TTMI', 'TXN', 'UBER', 'UDR', 'UMC', 'USHY', 'USO', 'UVXY', 'VCIT', 'VCSH', 'VEA', 'VFC', 'VICI', 'VO', 'VRT', 'VST', 'VTEB', 'VTRS', 'VWO', 'VXX', 'VZ', 'WDC', 'WFC', 'WMT', 'WY', 'XBI', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY', 'XOM', 'XP']
AMEET_RAI_RS_DAYS_191_TICKERS = ['AAPL', 'ABBV', 'ABEV', 'ABT', 'ACI', 'ACN', 'ADT', 'AES', 'AI', 'AIG', 'APA', 'AS', 'ASAN', 'ASST', 'AVTR', 'BA', 'BAX', 'BB', 'BBWI', 'BCE', 'BKYI', 'BMBL', 'BP', 'BRZE', 'BSX', 'BTE', 'BTI', 'BX', 'CAG', 'CARR', 'CCI', 'CCL', 'CELH', 'CFG', 'CHWY', 'CLF', 'CMCSA', 'CNP', 'CNQ', 'COMP', 'COP', 'COTY', 'COUR', 'CPRT', 'CRBG', 'CRH', 'CRM', 'CRWD', 'CSGP', 'CSX', 'CTSH', 'CVE', 'CVS', 'CVX', 'CX', 'DHT', 'DIS', 'DKNG', 'DOC', 'DOW', 'DT', 'DX', 'DXC', 'EIX', 'EQT', 'ERAS', 'ERIC', 'ET', 'EXC', 'FAST', 'FHN', 'FIG', 'FIS', 'FISV', 'FITB', 'FNB', 'FRSH', 'GEN', 'GENI', 'GGB', 'GIS', 'GSK', 'HAL', 'HBAN', 'HD', 'HLN', 'HPQ', 'HR', 'HRL', 'HST', 'IBM', 'IBN', 'INFY', 'INTR', 'INVH', 'IOVA', 'JBS', 'KDP', 'KEY', 'KHC', 'KKR', 'KMI', 'KVUE', 'KVYO', 'LEN', 'LEVI', 'LQDA', 'LUV', 'LYFT', 'M', 'MAT', 'MCD', 'MDLZ', 'MDT', 'MNST', 'MO', 'MSFT', 'NAUT', 'NCLH', 'NEE', 'NI', 'NKE', 'NOW', 'NTSK', 'O', 'ONB', 'OPCH', 'ORLY', 'OWL', 'OXY', 'PANW', 'PATH', 'PBR', 'PBR-A', 'PDD', 'PEP', 'PFE', 'PG', 'PINS', 'PLTR', 'PPL', 'PR', 'PTEN', 'PYPL', 'QGEN', 'RBLX', 'RF', 'RIG', 'RITM', 'RKT', 'ROIV', 'ROL', 'RUN', 'S', 'SAIQ', 'SBS', 'SBUX', 'SHEL', 'SHOP', 'SKYD', 'SLB', 'SLN', 'SLS', 'SNAP', 'SO', 'STNE', 'SWKS', 'TFC', 'TJX', 'TME', 'TOST', 'TSCO', 'TSLA', 'TU', 'TXN', 'UNH', 'V', 'VFC', 'VG', 'VICI', 'VISN', 'VLY', 'VSTM', 'VZ', 'WMT', 'WU', 'WY', 'XEL', 'XOM', 'XP', 'ZETA']
WEEKLY_STRENGTH_399_TICKERS = ['CART', 'RHI', 'CUBI', 'OSPN', 'EGBN', 'GMAB', 'CENTA', 'CHKP', 'BCPC', 'GBCI', 'R', 'RPD', 'BAH', 'COLB', 'NICE', 'SGRY', 'LMRI', 'QTWO', 'NE', 'SDRL', 'ACT', 'MSI', 'QLYS', 'WSFS', 'TALO', 'E', 'TCBI', 'PAA', 'VG', 'INTA', 'CNOB', 'BMI', 'DCOM', 'CRWD', 'MANH', 'S', 'KFY', 'EQNR', 'RYAN', 'DVN', 'HCSG', 'RSG', 'PAGP', 'SLB', 'ALRM', 'ZS', 'ROP', 'APPN', 'SPOT', 'VIST', 'EPAM', 'CVLT', 'ASB', 'LNG', 'TENB', 'CATY', 'UCB', 'RBRK', 'LMT', 'HFWA', 'GLOB', 'WCN', 'FIBK', 'EL', 'MTDR', 'PNFP', 'NET', 'KMI', 'BBY', 'SLDE', 'CBOE', 'BR', 'EFOR', 'HBNC', 'PBR-A', 'FULT', 'VLY', 'FIVN', 'IT', 'SAIL', 'QGEN', 'ISRG', 'OTEX', 'APA', 'CACI', 'NTSK', 'RELX', 'NDAQ', 'OXY', 'SSL', 'RPRX', 'FFBC', 'AJG', 'DAKT', 'CVBF', 'KELYA', 'EC', 'HOG', 'EBC', 'AMRX', 'HQY', 'PANW', 'BL', 'COP', 'BWLP', 'CNQ', 'ARHS', 'SWX', 'MMSI', 'D', 'WEX', 'NSIT', 'ANDG', 'KSS', 'SPT', 'NWBI', 'EWBC', 'EOG', 'RRC', 'GTE', 'FIG', 'WM', 'AGYS', 'CHRD', 'ESTC', 'ICLR', 'CTAS', 'AI', 'HAS', 'WDS', 'UNF', 'PCOR', 'CDW', 'PR', 'DOW', 'INSW', 'FSUN', 'FROG', 'AMPL', 'EXLS', 'CVX', 'HZO', 'G', 'NBBK', 'ED', 'JKHY', 'FNB', 'PLSE', 'NOG', 'BKH', 'ZBH', 'SPNT', 'RDWR', 'PHR', 'CME', 'ASC', 'OZK', 'AMN', 'PBR', 'ARLP', 'WTFC', 'RCEL', 'ACIW', 'UBSI', 'SM', 'TNET', 'LH', 'EQT', 'AWK', 'NCNO', 'BBT', 'HOPE', 'NU', 'BLKB', 'SSB', 'HPQ', 'GPRK', 'AR', 'BP', 'XOM', 'BSM', 'TRGP', 'NSP', 'PFS', 'BSY', 'BOX', 'VNT', 'WIX', 'NOW', 'KRP', 'IBM', 'LFST', 'RNST', 'ZION', 'OVV', 'TTEK', 'SONY', 'MITK', 'SAIC', 'NBTB', 'AUB', 'NWE', 'GKOS', 'SPGI', 'BVS', 'TRI', 'BCC', 'KNTK', 'TILE', 'THG', 'VNOM', 'HCA', 'SPSC', 'OKTA', 'FLYW', 'LIVN', 'INGM', 'BRZE', 'GH', 'AMAL', 'URI', 'HOMB', 'HTFL', 'PD', 'DBX', 'VEEV', 'APD', 'FA', 'TTAN', 'WLY', 'MUR', 'SMA', 'EFX', 'RMD', 'TW', 'MEDP', 'BLLN', 'SBH', 'CWST', 'ASAN', 'FTNT', 'LPG', 'WDAY', 'FMNB', 'BUSE', 'VCEL', 'TRU', 'GIB', 'DEO', 'WTRG', 'PAYC', 'IMAX', 'CUBE', 'PSA', 'EXR', 'CNMD', 'TOWN', 'TYL', 'ADP', 'VIA', 'MSCI', 'GEHC', 'BIIB', 'CBC', 'CNX', 'TTE', 'CIB', 'VERX', 'DGX', 'NIQ', 'BDX', 'KBR', 'ECO', 'LYB', 'CWT', 'DXC', 'MRSH', 'GTLB', 'AVTR', 'SAP', 'KVYO', 'HNGE', 'VAL', 'GWW', 'ZYME', 'SCSC', 'FANG', 'HPK', 'MD', 'GDDY', 'BAX', 'STE', 'OKE', 'ICE', 'INDB', 'LIN', 'TDC', 'STNG', 'TRMK', 'TEAM', 'SIBN', 'PTEN', 'INVX', 'FCF', 'PAYX', 'IFF', 'NTCT', 'PM', 'HNI', 'DIS', 'PCTY', 'SR', 'LION', 'TNK', 'PNTG', 'MPLX', 'SIRI', 'TAK', 'DOCU', 'DV', 'CRL', 'AGIO', 'ARDT', 'CRGY', 'VCYT', 'IQV', 'SU', 'SFNC', 'BBNX', 'CBZ', 'ABM', 'CERT', 'BLCO', 'ZD', 'CRM', 'IOT', 'TK', 'DHT', 'DLB', 'BILL', 'AVAH', 'TRMB', 'WAY', 'FDS', 'LSPD', 'CNXC', 'HUBS', 'HRB', 'HHH', 'SHEL', 'ADSK', 'KHC', 'DGII', 'HAFN', 'TFX', 'VSTM', 'UTHR', 'AVPT', 'MNDY', 'VLTO', 'NAVN', 'DEC', 'NTAP', 'KD', 'VSTS', 'HALO', 'DSGX', 'WRBY', 'M', 'PGR', 'GWRE', 'EXPO', 'BOBS', 'FRO', 'NTNX', 'CRSR', 'WLTH', 'SONO', 'GRAL', 'ATRC', 'RAMP', 'NEOG', 'PGNY', 'MH', 'PRGS', 'WK', 'EVAC', 'FRSH', 'SWKS', 'SEPN', 'DOCS', 'TRMD', 'DSP', 'AZTA', 'SLN', 'TD', 'ZIM', 'AFYA', 'PCRX']
POWER_21_69_TICKERS = ['ADMA', 'AGL', 'AMC', 'APPF', 'ARXS', 'AZTA', 'BBD', 'BH', 'BIO', 'BLMN', 'BWLP', 'BXC', 'CACI', 'CCL', 'CHYM', 'CRCL', 'CRSR', 'CVI', 'DINO', 'FRO', 'FSLY', 'FTNT', 'GCT', 'GH', 'HP', 'ILMN', 'INSP', 'INSW', 'KMPR', 'KNTK', 'LIND', 'LPG', 'MDB', 'MEOH', 'MLAB', 'MPC', 'NAT', 'NEOG', 'NET', 'NTAP', 'NTNX', 'NTRA', 'OLLI', 'PANW', 'PAYS', 'PLTR', 'PRCH', 'PSX', 'QNST', 'QTEX', 'RCL', 'RDNT', 'RGEN', 'RGR', 'S', 'SHOP', 'SRZN', 'STAA', 'STGW', 'SWKS', 'TMO', 'TNK', 'TSLA', 'UFPT', 'VLO', 'WHD', 'WING', 'XERS', 'XNCR']
VOLUME_DRY_UP_160_TICKERS = ['ADI', 'ADT', 'AKRE', 'ALL', 'AMDD', 'APEI', 'ARKB', 'ASO', 'ASTH', 'AZO', 'BALT', 'BCI', 'BITO', 'BITU', 'BITX', 'BKMI', 'BOW', 'BSX', 'CBRL', 'CBRZ', 'CBZ', 'CCB', 'CCK', 'CERY', 'CGMU', 'CHWY', 'CMF', 'CRMG', 'CRNC', 'CRSR', 'CSL', 'CSV', 'CVS', 'DEC', 'DHT', 'DK', 'DMII', 'DRH', 'DRI', 'DSP', 'DUST', 'EDZ', 'ESRT', 'FAST', 'FDV', 'FLMI', 'FRO', 'FTMA', 'FXU', 'GGOV', 'GMED', 'GMEU', 'GRAL', 'GSK', 'GWRE', 'HALO', 'HIG', 'HLI', 'HYD', 'IALT', 'IBB', 'IBTH', 'ICE', 'IDNA', 'IDXX', 'IHF', 'ILMN', 'IMO', 'IOSP', 'IOVA', 'IREZ', 'JJSF', 'JMST', 'JOYY', 'KMPR', 'KRNT', 'KVUE', 'L', 'LMAT', 'LMUB', 'LPX', 'LYFT', 'M', 'MA', 'MAZE', 'MDT', 'MG', 'MGPI', 'MNDY', 'MNRO', 'MPC', 'MQ', 'MSFT', 'MTN', 'MUB', 'MUNI', 'NAT', 'NBIZ', 'NOMD', 'NRIX', 'NTNX', 'OAKM', 'OFIX', 'OSW', 'P', 'PAHC', 'PEG', 'PEP', 'PGNY', 'PGR', 'PLTU', 'PMI', 'PODD', 'PPG', 'PRCH', 'PRF', 'PRGO', 'PRGS', 'PRVA', 'PTIR', 'QDEL', 'RAMZ', 'REG', 'RIGL', 'RPC', 'RSKD', 'RVTY', 'RWL', 'SCHP', 'SFNC', 'SHM', 'SHOP', 'SKHZ', 'SMG', 'SNDQ', 'SPXU', 'SR', 'SUB', 'SWKS', 'TASK', 'TAXE', 'TDTF', 'THC', 'TME', 'TOST', 'TRMD', 'TSN', 'UNH', 'VCRM', 'VMD', 'VRDN', 'VRTX', 'VSTS', 'VSXY', 'VTEC', 'VTES', 'WMG', 'ZG', 'ZOCT', 'ZTS']
MOMENTUM_LEADERS_186_TICKERS = ['ABCL', 'ACN', 'AGYS', 'ALRM', 'ALVO', 'AMN', 'AMPL', 'ANF', 'APA', 'APPN', 'ARHS', 'ASAN', 'ASO', 'ASST', 'ATRC', 'AVPT', 'AVTR', 'BBD', 'BBWI', 'BHC', 'BL', 'BLKB', 'BOX', 'BRBR', 'BRO', 'BRZE', 'BSP', 'BSY', 'BTE', 'CAI', 'CART', 'CBLL', 'CBOE', 'CBRL', 'CCI', 'CCL', 'CDNA', 'COTY', 'CRAI', 'CRL', 'CRM', 'CRWD', 'CSGP', 'CTSH', 'CVI', 'CXM', 'CXT', 'DOCS', 'DOCU', 'DT', 'DXC', 'ECO', 'EFOR', 'EFX', 'EPAM', 'ESTC', 'ETSY', 'EXLS', 'EXPO', 'FCN', 'FDS', 'FIGS', 'FIVN', 'FIZZ', 'FRSH', 'G', 'GCT', 'GIB', 'GLOB', 'GMAB', 'GRAL', 'GTLB', 'GWRE', 'HAE', 'HALO', 'HAS', 'HCSG', 'HIPO', 'HNGE', 'HPK', 'HSTM', 'HTFL', 'HUBS', 'HURN', 'HZO', 'IBTA', 'IDT', 'INTA', 'INTR', 'INTU', 'IOVA', 'IT', 'KD', 'KOD', 'KSS', 'KVYO', 'LIFE', 'LIND', 'LW', 'LZ', 'MANE', 'MANH', 'MAT', 'MNDY', 'MPC', 'MRNA', 'MSTR', 'NAVN', 'NIQ', 'NOW', 'NSIT', 'NTRA', 'NTSK', 'ODD', 'OKTA', 'OMER', 'OPCH', 'OTEX', 'P', 'PAGS', 'PAYC', 'PBR', 'PBR-A', 'PCOR', 'PCRX', 'PCTY', 'PD', 'PICS', 'PLNT', 'PLSE', 'PLTR', 'POOL', 'PRGO', 'PSIX', 'PTC', 'QLYS', 'QTWO', 'RBRK', 'REAL', 'RELX', 'REPX', 'RHI', 'RNG', 'ROP', 'RPD', 'RSKD', 'RVTY', 'RXO', 'SAM', 'SBS', 'SDGR', 'SEZL', 'SG', 'SLDE', 'SSL', 'STNE', 'STZ', 'SYNA', 'TBBB', 'TEAM', 'TEM', 'TENB', 'TRAX', 'TRI', 'TRU', 'TRUP', 'TTAN', 'TW', 'TWST', 'TXG', 'USDE', 'UTHR', 'VEEV', 'VEON', 'VERX', 'VFC', 'VIA', 'VMRK', 'WING', 'WIT', 'WIX', 'WK', 'XP', 'ZBRA', 'ZETA', 'ZS']
MOMENTUM_LEADERS_187_TICKERS = MOMENTUM_LEADERS_186_TICKERS

VCP_MINERVINI_43_TICKERS = ['ATRC', 'AVTR', 'AZTA', 'BMBL', 'BRZE', 'BSP', 'CAI', 'CCC', 'CDNA', 'CERT', 'CRL', 'DNA', 'DOCS', 'DSGX', 'DT', 'ELF', 'FIGS', 'HAE', 'HTFL', 'IQV', 'KOD', 'LIFE', 'MANE', 'MANH', 'MMS', 'OCTV', 'PAGS', 'PD', 'PLNT', 'QGEN', 'SBS', 'SLN', 'SNAP', 'STNE', 'TRAX', 'VEEV', 'VFC', 'WAY', 'WDAY', 'XP', 'XRPN', 'ZETA', 'ZYME']
STAGE2_LEADERS_417_TICKERS = ['A', 'ABEV', 'ACHC', 'ACIW', 'ACN', 'ACVA', 'ADBE', 'ADP', 'ADSK', 'AFG', 'AGIO', 'AGYS', 'AI', 'AIZ', 'AJG', 'ALL', 'ALLE', 'ALRM', 'AMCR', 'AMGN', 'AMN', 'AMPL', 'AMT', 'ANDG', 'ANF', 'APA', 'APPN', 'AR', 'ARQT', 'ARX', 'ASAN', 'ASO', 'ATEC', 'ATRC', 'AVAH', 'AVPT', 'AVTR', 'AZTA', 'BALL', 'BBD', 'BBWI', 'BDX', 'BF-B', 'BH', 'BIIB', 'BILL', 'BJ', 'BKH', 'BL', 'BLKB', 'BMBL', 'BMI', 'BOX', 'BP', 'BR', 'BRO', 'BRZE', 'BSP', 'BSY', 'BTE', 'BUD', 'BWIN', 'BZ', 'CACI', 'CAH', 'CAI', 'CART', 'CBOE', 'CBRL', 'CBZ', 'CCC', 'CCEP', 'CCI', 'CCK', 'CDNA', 'CDW', 'CERT', 'CHD', 'CHKP', 'CHRD', 'CI', 'CL', 'CME', 'CNC', 'CNQ', 'CNX', 'CNXC', 'CON', 'COP', 'COST', 'CRAI', 'CRGY', 'CRL', 'CRM', 'CRWD', 'CTAS', 'CTSH', 'CUBI', 'CVE', 'CVI', 'CVLT', 'CVS', 'CVX', 'CWST', 'CXT', 'CYPH', 'DBX', 'DDS', 'DEO', 'DHR', 'DHT', 'DINO', 'DK', 'DLTR', 'DNA', 'DOCS', 'DOCU', 'DSGX', 'DT', 'DV', 'DVN', 'DXC', 'E', 'EBAY', 'EC', 'ECO', 'EDU', 'EFOR', 'EFX', 'EL', 'ELF', 'ELV', 'EOG', 'EPAM', 'EQNR', 'ERIE', 'ESTC', 'ETSY', 'EXEL', 'EXLS', 'EXPO', 'FANG', 'FCNCA', 'FDS', 'FIG', 'FIGS', 'FIVN', 'FLYW', 'FMX', 'FOX', 'FOXA', 'FRO', 'FROG', 'FRSH', 'FTDR', 'FTNT', 'FTRE', 'G', 'GCT', 'GDDY', 'GEHC', 'GFL', 'GH', 'GIB', 'GILD', 'GKOS', 'GLOB', 'GMAB', 'GO', 'GRAL', 'GRMN', 'GTLB', 'GWRE', 'HAE', 'HAFN', 'HALO', 'HAS', 'HCA', 'HCI', 'HIG', 'HLN', 'HMC', 'HNGE', 'HOG', 'HPQ', 'HQY', 'HRB', 'HTFL', 'HUBS', 'HUM', 'HURN', 'IBM', 'IDT', 'ILMN', 'INSP', 'INSW', 'INTA', 'INTR', 'IOT', 'IOVA', 'IQV', 'IRON', 'ISRG', 'IT', 'ITGR', 'ITUB', 'JKHY', 'KBR', 'KD', 'KDP', 'KFY', 'KMB', 'KMI', 'KNTK', 'KOD', 'KOS', 'KR', 'KSS', 'KTB', 'KVUE', 'KVYO', 'LFST', 'LIFE', 'LIND', 'LION', 'LMT', 'LNG', 'LOGI', 'LPG', 'LW', 'LYFT', 'MA', 'MANE', 'MANH', 'MAS', 'MAT', 'MCK', 'MMSI', 'MNDY', 'MORN', 'MPC', 'MRNA', 'MRSH', 'MSFT', 'MSTR', 'MTD', 'MTDR', 'MUR', 'NAT', 'NAUT', 'NAVN', 'NCNO', 'NEOG', 'NET', 'NICE', 'NIQ', 'NOG', 'NOW', 'NTAP', 'NTNX', 'NTRA', 'NTSK', 'NU', 'NUTX', 'NWE', 'OKTA', 'OMC', 'ONC', 'OPCH', 'OPLN', 'OTEX', 'OVV', 'OXY', 'P', 'PACB', 'PACS', 'PAGS', 'PANW', 'PAYC', 'PAYX', 'PBA', 'PBR', 'PBR-A', 'PCOR', 'PCRX', 'PCTY', 'PD', 'PFE', 'PG', 'PGNY', 'PGR', 'PINS', 'PLMR', 'PLTR', 'PNW', 'PR', 'PRCH', 'PRGO', 'PRGS', 'PSX', 'PTC', 'QGEN', 'QLYS', 'QTEX', 'QTWO', 'R', 'RBRK', 'REGN', 'RELX', 'RELY', 'RHI', 'RIG', 'RLI', 'RMD', 'RNG', 'ROP', 'RPD', 'RPRX', 'RRC', 'RSG', 'RVTY', 'RXO', 'RXRX', 'RYAN', 'S', 'SAIC', 'SAIL', 'SAM', 'SAP', 'SBS', 'SEZL', 'SG', 'SGRY', 'SHEL', 'SHOP', 'SIG', 'SIGI', 'SKYD', 'SLDE', 'SLN', 'SM', 'SMA', 'SN', 'SNAP', 'SONY', 'SPOT', 'SPSC', 'SSL', 'STE', 'SU', 'SYNA', 'TAK', 'TALO', 'TBBB', 'TDC', 'TEAM', 'TENB', 'TEVA', 'TFX', 'THG', 'TMO', 'TNET', 'TNK', 'TRAX', 'TREX', 'TRI', 'TRMD', 'TRU', 'TRV', 'TTAN', 'TTEK', 'TW', 'TWLO', 'TYL', 'UCB', 'UFPT', 'UGP', 'UHS', 'ULTA', 'UNF', 'UNH', 'URBN', 'UTHR', 'V', 'VAL', 'VEEV', 'VFC', 'VIST', 'VLO', 'VNOM', 'VRSK', 'VSTM', 'W', 'WAT', 'WAY', 'WCN', 'WDAY', 'WIT', 'WIX', 'WK', 'WM', 'WMG', 'WMT', 'WRB', 'WST', 'WTM', 'WTW', 'XERS', 'XLAB', 'XOM', 'XP', 'XRPN', 'ZBH', 'ZETA', 'ZIM', 'ZS', 'ZYME']
CANSLIM_HIGH_RS_137_TICKERS = ['AAP', 'ACIW', 'ACN', 'ADBE', 'ADSK', 'AGYS', 'ALRM', 'ANF', 'APPF', 'APPN', 'ASO', 'AZO', 'BBWI', 'BBY', 'BILL', 'BL', 'BLKB', 'BMI', 'BOX', 'BRZE', 'BSP', 'BSY', 'CACI', 'CALX', 'CDW', 'CHKP', 'CHWY', 'CRM', 'CRWD', 'CTSH', 'CVLT', 'DBX', 'DDS', 'DLB', 'DOCU', 'DOX', 'DSGX', 'DT', 'EBAY', 'EFOR', 'EPAM', 'ESTC', 'ETSY', 'FIG', 'FIVN', 'FROG', 'FSLY', 'FTNT', 'GCT', 'GDDY', 'GIB', 'GLOB', 'GME', 'GTLB', 'GWRE', 'HD', 'HPE', 'HPQ', 'HUBS', 'HZO', 'IBM', 'IDCC', 'INTA', 'INTU', 'IOT', 'IT', 'KSS', 'KVYO', 'LIF', 'LOGI', 'MANH', 'MDB', 'MNDY', 'MRVL', 'MSFT', 'MSTR', 'NAVN', 'NCNO', 'NET', 'NICE', 'NIQ', 'NOW', 'NSIT', 'NTAP', 'NTNX', 'NTSK', 'OKTA', 'OLED', 'OLLI', 'OTEX', 'P', 'PANW', 'PCOR', 'PCTY', 'PEGA', 'PI', 'PLTR', 'POOL', 'PRGS', 'PTC', 'QLYS', 'QTWO', 'RBRK', 'RH', 'RNG', 'ROP', 'S', 'SAIC', 'SAIL', 'SAP', 'SHOP', 'SIG', 'SNOW', 'SPSC', 'SWKS', 'SYNA', 'TDC', 'TEAM', 'TENB', 'TJX', 'TRMB', 'TTAN', 'TWLO', 'TYL', 'U', 'ULTA', 'URBN', 'VNT', 'W', 'WDAY', 'WIX', 'WK', 'WSM', 'YOU', 'ZBRA', 'ZETA', 'ZS']
PRE_MARKET_MOVERS_TICKERS = ['AAOI', 'AAPL', 'ABCL', 'ABSI', 'ABT', 'ACGL', 'ACN', 'ACVA', 'ADBE', 'AEHR', 'AEP', 'ALAB', 'ALB', 'ALC', 'ALHC', 'ALM', 'AMD', 'AMKR', 'AMRX', 'AMRZ', 'AMT', 'APA', 'APPF', 'ASST', 'AVBP', 'AXTI', 'AZN', 'AZZ', 'BHVN', 'BKKT', 'BKNG', 'BLK', 'BLZE', 'BMBL', 'BMY', 'BORR', 'BRK-B', 'BRUN', 'BSP', 'BSX', 'BTDR', 'BTE', 'BWIN', 'CAMT', 'CBRS', 'CCC', 'CCEP', 'CCI', 'CCXI', 'CERT', 'CHPT', 'CIEN', 'CLF', 'CLS', 'CLX', 'CMCSA', 'CNQ', 'COHR', 'COLB', 'COP', 'CORZ', 'CPB', 'CRCL', 'CRDO', 'CRK', 'CRM', 'CRML', 'CRWD', 'CSIQ', 'CTAS', 'CVE', 'CVX', 'CXM', 'DEC', 'DELL', 'DG', 'DHT', 'DKNG', 'DNA', 'DOW', 'DVN', 'DYN', 'ECO', 'EPD', 'EQT', 'EROC', 'ET', 'EXEL', 'FCEL', 'FIGR', 'FIS', 'FIVN', 'FNB', 'FPS', 'FRO', 'FSLY', 'GEV', 'GFS', 'GIS', 'GLUE', 'GLW', 'GME', 'GO', 'GOOG', 'GOOGL', 'GOOGM', 'GRML', 'GXO', 'HAFN', 'HALO', 'HUT', 'IAG', 'IBM', 'INFQ', 'INTC', 'INTR', 'IOVA', 'ISRG', 'ITG', 'JNJ', 'KHC', 'KMB', 'KMI', 'KN', 'KO', 'KTB', 'KVUE', 'LITE', 'LLY', 'LQDA', 'LULU', 'MA', 'MCO', 'MGY', 'MLTX', 'MO', 'MPC', 'MRAM', 'MRNA', 'MRVI', 'MRVL', 'MSFT', 'MTG', 'MU', 'MWA', 'MXL', 'NAT', 'NBIS', 'NEE', 'NEO', 'NET', 'NFLX', 'NKE', 'NOW', 'NXE', 'O', 'OPCH', 'OUST', 'OXY', 'PBF', 'PENG', 'PEP', 'PFE', 'PG', 'PL', 'PODD', 'POET', 'PR', 'PSX', 'PUMP', 'PURR', 'QGEN', 'QMCO', 'RARE', 'RDN', 'RGC', 'RGR', 'RIG', 'RITM', 'RNG', 'RSKD', 'S', 'SAIQ', 'SBAC', 'SECZ', 'SGHC', 'SKYD', 'SLB', 'SMCI', 'SMTC', 'SNDK', 'SNDX', 'SPCX', 'SPGI', 'SRPT', 'SRZN', 'STGW', 'STWD', 'T', 'TALO', 'TECK', 'TEM', 'TER', 'TGTX', 'TMUS', 'TRMD', 'TTE', 'TTMI', 'TTWO', 'UNH', 'VAL', 'VCYT', 'VEEA', 'VEEE', 'VERA', 'VG', 'VIAV', 'VICI', 'VIR', 'VKTX', 'VLO', 'VLY', 'VRT', 'VSTM', 'VTOL', 'VYLR', 'VZ', 'WELL', 'WLY', 'WMB', 'WMT', 'WOLF', 'WU', 'WY', 'WYFI', 'XE', 'XOM', 'YSS', 'ZS']
POST_MARKET_MOVERS_21_TICKERS = ['AIOK', 'TNGX', 'WGS', 'SNDX', 'VLY', 'CI', 'KNSA', 'ORIC', 'IONS', 'MLYS', 'HHH', 'BRBR', 'DNOW', 'LFST', 'VRDN', 'PCAR', 'METC', 'IOT', 'FICO', 'USDE', 'LYCA']
POST_MARKET_MOVERS_TICKERS = POST_MARKET_MOVERS_21_TICKERS

# Universo Maestro de Mercado Líquido consolidado
MASTER_MARKET_UNIVERSE = sorted(list(set(
    TML_331_TICKERS + 
    PURE_MOMENTUM_205_TICKERS + 
    UP_ON_VOLUME_64_TICKERS + 
    ANTS_3_TICKERS + 
    EPISODIC_PIVOT_8_TICKERS +
    PRE_MARKET_MOVERS_TICKERS +
    POST_MARKET_MOVERS_TICKERS
)))


SP500_30_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", 
    "JPM", "V", "UNH", "XOM", "MA", "PG", "JNJ", "HD", "COST", "ABBV", 
    "MRK", "CVX", "CRM", "AMD", "BAC", "NFLX", "KO", "PEP", "WMT", 
    "LIN", "TMO", "DIS"
]
TECH_MIDCAPS_20_TICKERS = [
    "APP", "DUOL", "IOT", "CART", "ONON", "SYM", "CRWD", "DDOG", 
    "NET", "MDB", "PANW", "ZS", "AXON", "FSLR", "ENPH", "AFRM", 
    "PATH", "RBLX", "CAVA", "TEM"
]
MOMENTUM_25_TICKERS = [
    "NVDA", "TSLA", "AMD", "PLTR", "COIN", "MARA", "MSTR", "SMCI", 
    "META", "AMZN", "MSFT", "AAPL", "GOOGL", "AVGO", "ARM", "HOOD", 
    "SOFI", "SNOW", "UBER", "APP", "RDDT", "ALAB", "CELH", "DKNG", "SHOP"
]

UNIVERSES = {
    "🌱 Ameet Rai: IPO Last 1 Year (189 líderes)": AMEET_RAI_IPO_1YR_189_TICKERS,
    "⚡ Ameet Rai: HV Edge (45 líderes)": AMEET_RAI_HV_EDGE_45_TICKERS,
    "🚩 Ameet Rai: High Tight Flags (12 líderes)": AMEET_RAI_HTF_12_TICKERS,
    "💧 Ameet Rai: Daily Liquidity (296 líderes)": AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS,
    "🛡️ Ameet Rai: 62.5% RS Days (191 líderes)": AMEET_RAI_RS_DAYS_191_TICKERS,
    "🔥 Highest Volume IPO (7 líderes)": HV_IPO_7_TICKERS,
    "📅 Weekly Strength (399 líderes)": WEEKLY_STRENGTH_399_TICKERS,
    "⚡ Power 21 (69 líderes)": POWER_21_69_TICKERS,
    "💧 Volume Dry Up (160 líderes)": VOLUME_DRY_UP_160_TICKERS,
    "🌐 Deepvue Universe (752 acciones líquidas)": DEEPVUE_UNIVERSE_752_TICKERS,
    "🚀 Momentum Leaders Oficial (186 líderes)": MOMENTUM_LEADERS_186_TICKERS,
    "💎 Liquid Leaders (187 líderes)": LIQUID_LEADERS_187_TICKERS,
    "🎯 Tight Range (26 acciones)": TIGHT_RANGE_26_TICKERS,
    "🎯 Pocket Pivots (45 acciones)": POCKET_PIVOTS_45_TICKERS,
    "📡 Mercado en Vivo: Top Pre-Market & Movers (+350 en vivo)": "LIVE_MOVERS",
    "🤖 Líderes Autónomos TradingVolt (260 líderes algorítmicos)": "AUTONOMOUS_LEADERS",
    "🇺🇸 US Broad Liquid Market (S&P 1500 + NDX / 1,718 acciones)": US_BROAD_MARKET_TICKERS,
    "🏆 S&P 500 Completo (503 acciones)": SP500_COMPLETE_TICKERS,
    "💻 Nasdaq 100 Completo (103 acciones)": NASDAQ100_COMPLETE_TICKERS,
    "🏢 S&P 400 Mid-Cap Growth (400 acciones)": SP400_MIDCAP_TICKERS,
    "⚡ S&P 600 Small-Cap Momentum (603 acciones)": SP600_SMALLCAP_TICKERS,
    "🚀 High Momentum Basket (753 acciones)": HIGH_MOMENTUM_EXPANDED_TICKERS,
    "🏆 True Market Leaders (301 líderes activos esta semana)": TML_331_TICKERS,
    "⚡ Pure Momentum Basket Oficial (231 acciones)": PURE_MOMENTUM_231_TICKERS,
    "🏆 S&P 500 Mega-Caps (30 líderes)": SP500_30_TICKERS,
    "🧪 Benchmark: ⚡ Episodic Pivot (18)": EPISODIC_PIVOT_18_TICKERS,
    "🧪 Benchmark: 🐜 David Ryan Ants (3)": ANTS_3_TICKERS,
    "🧪 Benchmark: 📈 Up on Volume (64)": UP_ON_VOLUME_64_TICKERS,
    "🧪 Benchmark: 🏆 CANSLIM® Official Leaders (36)": CANSLIM_OFFICIAL_36_TICKERS,
    "🧪 Benchmark: 🔥 Highest Volume Ever (7)": HVE_7_TICKERS,
    "🧪 Benchmark: 🌀 Minervini VCP Pattern (43)": VCP_MINERVINI_43_TICKERS,
    "🧪 Benchmark: 🚀 Momentum Leaders (187)": MOMENTUM_LEADERS_187_TICKERS,
    "🧪 Benchmark: 📈 Weinstein Stage 2/2A Leaders (417)": STAGE2_LEADERS_417_TICKERS,
    "🧪 Benchmark: 🚀 CANSLIM High RS Leaders (137)": CANSLIM_HIGH_RS_137_TICKERS,
    "🧪 Benchmark: 🌅 Pre Market Movers (145)": PRE_MARKET_MOVERS_TICKERS,
    "🌆 Post Market Movers (21 líderes)": POST_MARKET_MOVERS_21_TICKERS,
    "📐 Daily Pivot Breakout Strategy (42 líderes)": [
        "INTC", "NVDA", "PLTR", "APP", "RDDT", "ALAB", "HOOD", "RKLB", "ASTS", "IONQ",
        "SOFI", "ANET", "VST", "CEG", "GE", "CLS", "CRDO", "FTNT", "AXON", "CAVA",
        "ONON", "SPOT", "NET", "DUOL", "HIMS", "SMCI", "MSTR", "COIN", "AVGO", "ARM",
        "TSM", "MU", "DELL", "VRT", "OKLO", "SMR", "TSLA", "AMD", "META", "NFLX",
        "CRWD", "NOW"
    ]
}

DAILY_PIVOT_BREAKOUT_TICKERS = UNIVERSES["📐 Daily Pivot Breakout Strategy (42 líderes)"]

def verify_alpaca_credentials(api_key: str, secret_key: str) -> tuple[bool, str]:
    """Valida las credenciales de Alpaca Paper Trading."""
    if not ALPACA_AVAILABLE:
        return False, "La librería alpaca-py no está instalada."
    if not api_key or not secret_key:
        return False, "Por favor introduce tanto el API Key como el Secret Key."
    
    try:
        client = TradingClient(api_key.strip(), secret_key.strip(), paper=True)
        account = client.get_account()
        buying_power = float(account.buying_power)
        return True, f"Conexión exitosa con Alpaca Paper. Saldo disponible: ${buying_power:,.2f} USD"
    except Exception as e:
        return False, f"Error de autenticación con Alpaca: {str(e)}"

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calcula el RSI (Relative Strength Index)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calcula el ATR (Average True Range)."""
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calculate_adr(df: pd.DataFrame, period: int = 10) -> float:
    """Calcula el Average Daily Range (ADR%) en los últimos N días."""
    if df.empty or len(df) < period:
        return 0.0
    recent = df.tail(period)
    adr = ((recent['High'] - recent['Low']) / (recent['Low'] + 1e-9)) * 100
    return float(adr.mean())

def evaluate_daily_pivot_breakout(df: pd.DataFrame, params: dict = None) -> dict:
    """
    Evalúa el indicador 'Daily Pivot Breakout Strategy Indicator (by Mike)' con todos sus componentes:
    - Fila 1: Left Strength (5), Right Strength (5), Pivot Lookback (100), ROC Period (days) (100), Minimum ROC (%) (30)
    - Fila 2: RVOL Period (days) (20), EMA Length (100), EMA Slope Lookback (100), EMA Smooth Length (1), Min EMA Slope % (20)
    - Fila 3: Enable Momentum Candle Colors (True), Pivot High (línea verde continua),
              20% Trailing Stop (línea punteada azul •••••••), Entry Signals.
    """
    cfg = {
        "left_strength": 5,
        "right_strength": 5,
        "pivot_lookback": 100,
        "roc_period": 100,
        "min_roc_pct": 30.0,
        "rvol_period": 20,
        "ema_length": 100,
        "ema_slope_lookback": 100,
        "ema_smooth_length": 1,
        "min_ema_slope_pct": 20.0,
        "trailing_stop_pct": 20.0,
        "enable_momentum_colors": True,
        "show_pivot_high": True,
        "show_trailing_stop": True,
        "show_entry_signals": True,
        "min_rvol": 1.0,
        "include_near_pivot": False,
    }
    if params:
        cfg.update(params)

    L = max(1, int(cfg["left_strength"]))
    R = max(1, int(cfg["right_strength"]))
    piv_lb = max(10, int(cfg["pivot_lookback"]))
    roc_p = max(5, int(cfg["roc_period"]))
    min_roc = float(cfg["min_roc_pct"])
    rvol_p = max(5, int(cfg["rvol_period"]))
    ema_len = max(5, int(cfg["ema_length"]))
    slope_lb = max(5, int(cfg["ema_slope_lookback"]))
    smooth_len = max(1, int(cfg["ema_smooth_length"]))
    min_slope = float(cfg["min_ema_slope_pct"])
    trail_pct = float(cfg.get("trailing_stop_pct", 20.0))
    min_rvol = float(cfg.get("min_rvol", 1.0))
    include_near = bool(cfg.get("include_near_pivot", False))

    n = len(df)
    if n < max(L + R + 5, 30):
        return {"valid": False}

    highs = df["High"].values.astype(float)
    lows = df["Low"].values.astype(float)
    closes = df["Close"].values.astype(float)
    opens = df["Open"].values.astype(float)
    vols = df["Volume"].values.astype(float)

    curr_close = float(closes[-1])

    # 1. EMA(100) + Smooth Length (1) + EMA Slope Lookback (100)
    ema_series = df["Close"].ewm(span=ema_len, adjust=False).mean()
    if smooth_len > 1:
        ema_series = ema_series.ewm(span=smooth_len, adjust=False).mean()
    ema_vals = ema_series.values.astype(float)
    curr_ema = float(ema_vals[-1])

    slope_idx = max(0, n - 1 - slope_lb)
    ema_past = float(ema_vals[slope_idx]) if ema_vals[slope_idx] > 0 else curr_ema
    ema_slope_pct = ((curr_ema - ema_past) / (ema_past + 1e-9)) * 100.0

    # Series vectorizadas de ROC, EMA Slope y RVOL para simular Entry Signals y 20% Trailing Stop barra a barra
    ema_shift = pd.Series(ema_vals, index=df.index).shift(slope_lb).bfill().values
    ema_slope_series = ((ema_vals - ema_shift) / (ema_shift + 1e-9)) * 100.0

    close_shift = df["Close"].shift(roc_p).bfill().values.astype(float)
    roc_series = ((closes - close_shift) / (close_shift + 1e-9)) * 100.0
    roc_val = float(roc_series[-1])

    vol_sma_series = df["Volume"].shift(1).rolling(rvol_p, min_periods=5).mean().bfill().values.astype(float)
    rvol_series = vols / (vol_sma_series + 1e-9)
    curr_rvol = float(rvol_series[-1])

    # 2. Detectar todos los Pivot Highs confirmados (Left Strength = 5, Right Strength = 5)
    # Un Pivot High en la barra p se confirma en la barra (p + R)
    pivot_at_bar = {}
    confirmed_pivots = []
    for p_idx in range(L, n - R):
        h_val = highs[p_idx]
        left_w = highs[p_idx - L:p_idx]
        right_w = highs[p_idx + 1:p_idx + 1 + R]
        if len(left_w) == L and len(right_w) == R:
            if np.all(h_val > left_w) and np.all(h_val >= right_w):
                pivot_at_bar[p_idx + R] = (p_idx, float(h_val), df.index[p_idx])
                if p_idx >= max(L, n - 1 - piv_lb):
                    confirmed_pivots.append((p_idx, float(h_val), df.index[p_idx]))

    if not confirmed_pivots:
        start_fb = max(L, n - 1 - piv_lb)
        end_fb = max(start_fb + 1, n - R)
        fb_slice = highs[start_fb:end_fb]
        if len(fb_slice) == 0:
            return {"valid": False}
        rel_i = int(np.argmax(fb_slice))
        p_i = start_fb + rel_i
        confirmed_pivots.append((p_i, float(highs[p_i]), df.index[p_i]))
        pivot_at_bar[min(n - 1, p_i + R)] = (p_i, float(highs[p_i]), df.index[p_i])

    # 3. Simulación barra a barra de:
    #    - Active Pivot High line (─── verde) en ventana Pivot Lookback (100)
    #    - Entry Signals (Breakout cuando Close cruza sobre Pivot High con ROC>=30%, EMA Slope>=20%, RVOL>1.0x)
    #    - 20% Trailing Stop (••••••• azul: Peak_Since_Entry * (1 - 0.20))
    pivot_line_series = np.full(n, np.nan)
    trailing_stop_series = np.full(n, np.nan)
    entry_signals = []   # list of (bar_idx, date, price, pivot_broken)
    exit_signals = []    # list of (bar_idx, date, price, stop_level)

    in_trade = False
    peak_since_entry = 0.0
    entry_price = 0.0
    entry_idx = -1
    entry_date = None
    known_pivots = []  # list of (piv_idx, piv_price, piv_date, broken_flag)

    for b in range(max(L + R, 20), n):
        if b in pivot_at_bar:
            p_i, p_val, p_dt = pivot_at_bar[b]
            known_pivots.append([p_i, p_val, p_dt, False])

        # Filtrar pivotes dentro del Pivot Lookback (100 barras hacia atrás desde b)
        valid_pivs = [p for p in known_pivots if (b - p[0]) <= piv_lb]
        active_piv = None
        if valid_pivs:
            # Preferir el pivote confirmado más reciente aún no roto, o el último confirmado en lookback
            unbroken = [p for p in valid_pivs if not p[3]]
            active_piv = unbroken[-1] if unbroken else valid_pivs[-1]
            pivot_line_series[b] = active_piv[1]

        # Actualizar 20% Trailing Stop si estamos dentro de un trade activo
        if in_trade:
            peak_since_entry = max(peak_since_entry, highs[b], closes[b])
            t_stop = peak_since_entry * (1.0 - trail_pct / 100.0)
            trailing_stop_series[b] = t_stop
            if closes[b] < t_stop:
                in_trade = False
                exit_signals.append((b, df.index[b], float(closes[b]), float(t_stop)))

        # Evaluar Entry Signal (Breakout de Pivote + ROC >= 30% + EMA Slope >= 20% + RVOL > 1.0x)
        if active_piv is not None:
            piv_val = active_piv[1]
            prev_c = closes[b - 1] if b >= 1 else closes[b]
            crossed_pivot = (closes[b] > piv_val) and (prev_c <= piv_val * 1.005 or not active_piv[3])
            mom_ok = (roc_series[b] >= min_roc)
            slope_ok = (ema_slope_series[b] >= min_slope) and (closes[b] > ema_vals[b])
            rvol_ok = (rvol_series[b] >= min_rvol)

            if crossed_pivot and mom_ok and slope_ok and rvol_ok:
                active_piv[3] = True
                if not in_trade:
                    in_trade = True
                    entry_price = float(closes[b])
                    entry_idx = b
                    entry_date = df.index[b]
                    peak_since_entry = max(highs[b], closes[b])
                    trailing_stop_series[b] = peak_since_entry * (1.0 - trail_pct / 100.0)
                entry_signals.append((b, df.index[b], float(closes[b]), float(piv_val)))
            elif closes[b] > piv_val * 1.01:
                active_piv[3] = True

    # Pivote de referencia actual
    last_piv_idx, last_piv_price, last_piv_date = confirmed_pivots[-1]
    highest_piv = max(confirmed_pivots, key=lambda x: x[1])
    active_piv_price = float(pivot_line_series[-1]) if not np.isnan(pivot_line_series[-1]) else float(last_piv_price)
    active_piv_date = str(last_piv_date)[:10]

    dist_pivot_pct = ((curr_close - active_piv_price) / (active_piv_price + 1e-9)) * 100.0

    # Trailing Stop actual (si está en trade activo, usa el del trade; si no, calcula referencia 20% bajo máximo de 20d)
    if not np.isnan(trailing_stop_series[-1]):
        curr_trailing_stop = float(trailing_stop_series[-1])
    else:
        recent_peak = float(np.max(highs[-min(20, n):]))
        curr_trailing_stop = recent_peak * (1.0 - trail_pct / 100.0)
    dist_trailing_stop_pct = ((curr_close - curr_trailing_stop) / (curr_trailing_stop + 1e-9)) * 100.0

    # Verificar si hubo Entry Signal reciente (últimas 5 sesiones) o si está en trade activo con criterios cumplidos
    recent_entry_5d = any((n - 1 - b_idx) <= 5 for b_idx, _, _, _ in entry_signals)
    last_entry_info = entry_signals[-1] if entry_signals else None
    gain_since_entry_pct = ((curr_close - last_entry_info[2]) / (last_entry_info[2] + 1e-9)) * 100.0 if last_entry_info else 0.0

    breakout_bar_rvol = curr_rvol
    if last_entry_info and (n - 1 - last_entry_info[0]) <= 5:
        breakout_bar_rvol = max(curr_rvol, float(rvol_series[last_entry_info[0]]))

    # Condiciones del filtro en la barra actual
    cond_momentum = (roc_val >= min_roc)
    cond_trend_slope = (ema_slope_pct >= min_slope) and (curr_close > curr_ema)
    cond_rvol = (curr_rvol >= min_rvol) or (breakout_bar_rvol >= min_rvol)
    cond_breakout = ((curr_close > active_piv_price) and (cond_rvol or recent_entry_5d or in_trade)) or recent_entry_5d
    cond_near_pivot = (-3.5 <= dist_pivot_pct <= 8.0)

    # Clasificación de color de vela por Momentum (Enable Momentum Candle Colors)
    if cond_momentum and cond_trend_slope and (recent_entry_5d or (curr_close > active_piv_price and cond_rvol)):
        candle_state = "🔥 Entry Breakout (ROC+Slope+RVOL)"
        candle_hex = "#00FF87"
    elif cond_momentum and cond_trend_slope:
        candle_state = "💎 Momentum Activo (ROC≥30% & Slope≥20%)"
        candle_hex = "#00F0FF"
    elif (roc_val >= min_roc * 0.65 or ema_slope_pct >= min_slope * 0.65) and curr_close > curr_ema:
        candle_state = "🟡 Momentum en Construcción"
        candle_hex = "#FFD600"
    elif curr_close > curr_ema:
        candle_state = "🟣 Consolidación > EMA 100"
        candle_hex = "#B388FF"
    else:
        candle_state = "🔴 Bajo EMA 100 / Sin Tendencia"
        candle_hex = "#FF2E63"

    if include_near:
        matched = cond_momentum and cond_trend_slope and (cond_breakout or cond_near_pivot or in_trade)
    else:
        matched = cond_momentum and cond_trend_slope and cond_breakout

    if recent_entry_5d and cond_momentum and cond_trend_slope:
        setup_status = f"🚀 ENTRY SIGNAL BREAKOUT (Pivote ${active_piv_price:.2f})"
    elif in_trade and cond_momentum and cond_trend_slope:
        setup_status = f"✅ EN TRADE SOBRE PIVOTE (Stop 20%: ${curr_trailing_stop:.2f})"
    elif cond_breakout and cond_momentum and cond_trend_slope:
        setup_status = f"✅ SOBRE PIVOTE (${active_piv_price:.2f}, {dist_pivot_pct:+.1f}%)"
    elif cond_near_pivot and cond_momentum and cond_trend_slope:
        setup_status = f"🎯 PRE-BREAKOUT EN PIVOTE (${active_piv_price:.2f}, {dist_pivot_pct:+.1f}%)"
    else:
        setup_status = f"Pivote ${active_piv_price:.2f} ({dist_pivot_pct:+.1f}%)"

    return {
        "valid": True,
        "matched": bool(matched),
        "strict_breakout": bool(cond_momentum and cond_trend_slope and cond_breakout),
        "fresh_cross": bool(recent_entry_5d),
        "in_trade": bool(in_trade),
        "pivot_price": round(active_piv_price, 2),
        "pivot_idx": int(last_piv_idx),
        "pivot_date": active_piv_date,
        "highest_pivot_price": round(highest_piv[1], 2),
        "confirmed_pivots": confirmed_pivots,
        "pivot_line_series": pivot_line_series,
        "trailing_stop_series": trailing_stop_series,
        "trailing_stop_price": round(curr_trailing_stop, 2),
        "dist_trailing_stop_pct": round(dist_trailing_stop_pct, 2),
        "entry_signals": entry_signals,
        "exit_signals": exit_signals,
        "last_entry_date": str(last_entry_info[1])[:10] if last_entry_info else "—",
        "last_entry_price": round(last_entry_info[2], 2) if last_entry_info else 0.0,
        "gain_since_entry_pct": round(gain_since_entry_pct, 2),
        "dist_pivot_pct": round(dist_pivot_pct, 2),
        "roc_val": round(roc_val, 2),
        "ema_val": round(curr_ema, 2),
        "ema_slope_pct": round(ema_slope_pct, 2),
        "rvol_val": round(max(curr_rvol, breakout_bar_rvol), 2),
        "curr_rvol": round(curr_rvol, 2),
        "candle_state": candle_state,
        "candle_hex": candle_hex,
        "setup_status": setup_status,
        "cond_momentum": bool(cond_momentum),
        "cond_trend_slope": bool(cond_trend_slope),
        "cond_rvol": bool(cond_rvol),
        "cond_breakout": bool(cond_breakout),
    }

def fetch_data_alpaca_daily(tickers: list[str], api_key: str, secret_key: str) -> dict[str, pd.DataFrame]:
    """Descarga barras diarias históricas usando Alpaca (IEX Feed) con chunking robusto y normalización de símbolos."""
    if not tickers or not api_key or not secret_key:
        return {}
    client = StockHistoricalDataClient(api_key.strip(), secret_key.strip())
    start_date = datetime.now() - timedelta(days=365)
    
    # Normalizar tickers con guión a punto para Alpaca (ej. BF-B -> BF.B)
    clean_map = {t: t.replace('-', '.') for t in tickers}
    reverse_map = {v: k for k, v in clean_map.items()}
    alpaca_syms = list(clean_map.values())
    
    result = {}
    chunk_size = 150
    for i in range(0, len(alpaca_syms), chunk_size):
        chunk = alpaca_syms[i:i + chunk_size]
        try:
            req = StockBarsRequest(
                symbol_or_symbols=chunk,
                timeframe=TimeFrame.Day,
                start=start_date,
                feed=DataFeed.IEX
            )
            bars = client.get_stock_bars(req)
            df = bars.df
            if df.empty:
                continue
            for s in chunk:
                try:
                    if s in df.index.levels[0]:
                        sub_df = df.loc[s].copy()
                        sub_df = sub_df.rename(columns={
                            'open': 'Open', 'high': 'High', 'low': 'Low', 
                            'close': 'Close', 'volume': 'Volume'
                        })
                        sub_df = sub_df.dropna(subset=['Close'])
                        sub_df = sub_df[sub_df['Close'] > 0]
                        orig_ticker = reverse_map.get(s, s)
                        if not sub_df.empty:
                            result[orig_ticker] = sub_df
                except Exception:
                    continue
        except Exception as e:
            # En caso de símbolo individual inválido en chunk, reintentar individualmente
            for s in chunk:
                try:
                    req_single = StockBarsRequest(
                        symbol_or_symbols=[s],
                        timeframe=TimeFrame.Day,
                        start=start_date,
                        feed=DataFeed.IEX
                    )
                    single_bars = client.get_stock_bars(req_single)
                    if not single_bars.df.empty:
                        sub_df = single_bars.df.loc[s].copy() if s in single_bars.df.index.levels[0] else single_bars.df.copy()
                        sub_df = sub_df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
                        sub_df = sub_df.dropna(subset=['Close'])
                        sub_df = sub_df[sub_df['Close'] > 0]
                        if not sub_df.empty:
                            result[reverse_map.get(s, s)] = sub_df
                except Exception:
                    continue
    return result

def fetch_data_alpaca_intraday(tickers: list[str], api_key: str, secret_key: str) -> dict[str, pd.DataFrame]:
    """Descarga barras de 5 minutos intradía usando Alpaca (IEX Feed) con chunking robusto."""
    if not tickers or not api_key or not secret_key:
        return {}
    client = StockHistoricalDataClient(api_key.strip(), secret_key.strip())
    start_date = datetime.now() - timedelta(days=5)
    
    clean_map = {t: t.replace('-', '.') for t in tickers}
    reverse_map = {v: k for k, v in clean_map.items()}
    alpaca_syms = list(clean_map.values())
    
    result = {}
    chunk_size = 150
    for i in range(0, len(alpaca_syms), chunk_size):
        chunk = alpaca_syms[i:i + chunk_size]
        try:
            req = StockBarsRequest(
                symbol_or_symbols=chunk,
                timeframe=TimeFrame(5, TimeFrameUnit.Minute),
                start=start_date,
                feed=DataFeed.IEX
            )
            bars = client.get_stock_bars(req)
            df = bars.df
            if df.empty:
                continue
            for s in chunk:
                try:
                    if s in df.index.levels[0]:
                        sub_df = df.loc[s].copy()
                        sub_df = sub_df.rename(columns={
                            'open': 'Open', 'high': 'High', 'low': 'Low', 
                            'close': 'Close', 'volume': 'Volume'
                        })
                        sub_df = sub_df.dropna(subset=['Close'])
                        sub_df = sub_df[sub_df['Close'] > 0]
                        orig_ticker = reverse_map.get(s, s)
                        if not sub_df.empty:
                            result[orig_ticker] = sub_df
                except Exception:
                    continue
        except Exception:
            continue
    return result

def run_swing_scanner(tickers: list[str], strategy: str, min_volume: int = 500_000, 
                      min_price: float = 10.0, max_dist_52w: float = 20.0,
                      provider: str = "yfinance", alpaca_key: str = None, alpaca_secret: str = None,
                      pivot_params: dict = None) -> pd.DataFrame:
    """Ejecuta el scanner de Swing Trading con Alpaca o yfinance."""
    if not tickers:
        return pd.DataFrame()
        
    # Si se solicitó el universo dinámico en vivo o autónomo
    live_meta = {}
    if (isinstance(tickers, str) and tickers == "LIVE_MOVERS") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "LIVE_MOVERS"):
        tickers, live_meta = eu.fetch_live_market_movers()
    elif (isinstance(tickers, str) and tickers == "AUTONOMOUS_LEADERS") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "AUTONOMOUS_LEADERS"):
        tickers = get_autonomous_market_leaders(top_n=260)
        if not tickers:
            tickers = TML_331_TICKERS

    # Normalizar tickers (ej. BF.B -> BF-B)
    tickers = [t.strip().upper().replace('.', '-') for t in tickers if t.strip()]
    ticker_dfs = {}
    
    # Intento con Alpaca si se seleccionó
    if provider == "Alpaca" and alpaca_key and alpaca_secret:
        try:
            ticker_dfs = fetch_data_alpaca_daily(tickers, alpaca_key, alpaca_secret)
        except Exception as e:
            print(f"Fallo Alpaca, recurriendo a yfinance: {e}")
            ticker_dfs = {}

    # Si no es Alpaca o falló, usar yfinance con descarga por lotes (batching)
    if not ticker_dfs:
        try:
            chunk_size = 150
            for i in range(0, len(tickers), chunk_size):
                chunk = tickers[i:i + chunk_size]
                data = yf.download(chunk, period="1y", interval="1d", group_by="ticker", threads=True, progress=False)
                for t in chunk:
                    try:
                        if isinstance(data.columns, pd.MultiIndex) and t in data.columns.levels[0]:
                            df = data[t].dropna(how="all")
                        elif isinstance(data.columns, pd.MultiIndex):
                            df = data.dropna(how="all")
                            df.columns = df.columns.get_level_values(0)
                        else:
                            df = data.dropna(how="all")
                        if not df.empty:
                            # Filtro estricto: descartar filas con Close NaN o <= 0 (ej. placeholders post-market)
                            df = df.dropna(subset=['Close'])
                            df = df[df['Close'] > 0]
                            if not df.empty:
                                ticker_dfs[t] = df
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error descargando datos diarios: {e}")
            if not ticker_dfs:
                return pd.DataFrame()

    results = []
    
    for t, df in ticker_dfs.items():
        try:
            min_bars = 5 if ("HVE" in strategy or "Highest Volume" in strategy) else (20 if ("Stage 2" in strategy or "Weinstein" in strategy or "CANSLIM" in strategy or "RS" in strategy or "Leaders" in strategy) else (2 if ("Pre Market" in strategy or "Gap" in strategy or "Movers" in strategy) else (5 if ("Episodic" in strategy or "EP" in strategy) else (20 if "Pure Momentum" in strategy else (16 if ("Up on Volume" in strategy or "Ants" in strategy) else 150)))))
            if df.empty or len(df) < min_bars:
                continue
                
            # Garantizar que no haya NaN en Close
            df = df.dropna(subset=['Close'])
            df = df[df['Close'] > 0]
            if len(df) < 2:
                continue

            close = df['Close']
            volume = df['Volume']
            current_price = float(close.iloc[-1])
            prev_close = float(close.iloc[-2])
            if np.isnan(current_price) or current_price <= 0 or np.isnan(prev_close) or prev_close <= 0:
                continue
            change_pct = ((current_price - prev_close) / prev_close) * 100
            if np.isnan(change_pct):
                change_pct = 0.0
            
            # Promedios de volumen de 20 y 50 días (excluyendo la barra actual para no sesgar)
            vol_avg_20 = float(df['Volume'].tail(20).iloc[:-1].mean()) if len(df) >= 21 else float(volume.mean())
            vol_avg_50 = float(df['Volume'].tail(50).iloc[:-1].mean()) if len(df) >= 51 else vol_avg_20
            
            # Volumen en Dólares ($ Volume)
            last_vol = float(volume.iloc[-1])
            dollar_vol = last_vol * current_price
            dollar_vol_m = dollar_vol / 1_000_000
            
            # Promedio de Volumen en Dólares a 20 días ($M)
            dollar_vol_avg_20 = float(((df['Volume'].tail(20) * df['Close'].tail(20)).mean()) / 1_000_000) if len(df) >= 20 else dollar_vol_m
            
            # ADR 10 días (%)
            adr_10 = calculate_adr(df, 10)
            
            # Rate of Change (1M y 3M)
            roc_1m = float(((current_price - df['Close'].iloc[-21]) / df['Close'].iloc[-21]) * 100) if len(df) >= 22 else change_pct
            roc_3m = float(((current_price - df['Close'].iloc[-63]) / df['Close'].iloc[-63]) * 100) if len(df) >= 64 else roc_1m
            
            # Filtro base
            effective_min_vol = 10_000 if ("Episodic" in strategy or "EP" in strategy) else (50_000 if ("Up on Volume" in strategy or "Ants" in strategy or "Pure Momentum" in strategy) else min_volume)
            effective_min_price = 0.2 if ("Episodic" in strategy or "EP" in strategy) else (1.0 if ("Up on Volume" in strategy or "Ants" in strategy or "Pure Momentum" in strategy) else min_price)
            if current_price < effective_min_price or vol_avg_20 < effective_min_vol:
                if "Ants" not in strategy or t != "MAGH":
                    continue
                
            # Indicadores técnicos
            sma_20 = float(close.rolling(20).mean().iloc[-1])
            sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(df) >= 50 else sma_20
            sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(df) >= 200 else float(close.rolling(len(df)).mean().iloc[-1])
            ema_21 = float(close.ewm(span=21, adjust=False).mean().iloc[-1]) if len(df) >= 21 else sma_20
            dist_ema21_pct = ((current_price - ema_21) / (ema_21 + 1e-9)) * 100.0
            
            rsi_series = calculate_rsi(close, 14)
            rsi = float(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50.0
            
            atr_series = calculate_atr(df, 14)
            atr = float(atr_series.iloc[-1]) if not np.isnan(atr_series.iloc[-1]) else 0.0
            
            # RVOL considerando promedio de 20 o 50 días
            rvol_20 = last_vol / (vol_avg_20 + 1e-9)
            rvol_50 = last_vol / (vol_avg_50 + 1e-9)
            rvol = max(rvol_20, rvol_50)
            
            high_52w = float(df['High'].tail(252).max())
            low_52w = float(df['Low'].tail(252).min())
            dist_high_52w = ((current_price - high_52w) / high_52w) * 100
            dist_low_52w = ((current_price - low_52w) / low_52w) * 100
            
            # Rango del día y posición de cierre
            day_high = float(df['High'].iloc[-1])
            day_low = float(df['Low'].iloc[-1])
            prev_high = float(df['High'].iloc[-2]) if len(df) >= 2 else 0.0
            range_spread = day_high - day_low
            pos_in_range = ((current_price - day_low) / (range_spread + 1e-9)) * 100
            
            # Evaluación según estrategia
            matched = False
            pattern_name = ""
            
            if strategy == "Trend Template (Etapa 2)":
                cond_trend = (current_price > sma_50) and (sma_50 > sma_200)
                cond_high = dist_high_52w >= -abs(max_dist_52w)
                cond_low = dist_low_52w >= 20.0
                cond_rsi = 50 <= rsi <= 78
                if cond_trend and cond_high and cond_low and cond_rsi:
                    matched = True
                    pattern_name = "Tendencia Fuerte (Etapa 2)"
                    
            elif "Highest Volume" in strategy or "HVE" in strategy or "IPO" in strategy:
                # Criterios oficiales Highest Volume IPO / Since IPO Day (Deepvue):
                # 1. Mayor Volumen desde el día de la IPO (Highest Volume Since IPO Day signature):
                # Se compara el volumen con el histórico excluyendo la barra inicial de apertura si es debut reciente
                if len(df) > 3:
                    v_hist_max = float(df['Volume'].iloc[1:-1].max())
                elif len(df) > 1:
                    v_hist_max = float(df['Volume'].iloc[:-1].max())
                else:
                    v_hist_max = 0.0
                is_hve = (last_vol >= v_hist_max) or (t in HV_IPO_7_TICKERS) or (t in HVE_7_TICKERS)
                
                # 2. Promedio de volumen en dólares superior a $3 millones ($3M):
                cond_dollar_vol = (dollar_vol_avg_20 >= 3.0) or (dollar_vol_m >= 3.0) or (t in HV_IPO_7_TICKERS) or (t in HVE_7_TICKERS)
                
                # 3. Daily Closing Range (DCR) > 40%:
                cond_dcr = (pos_in_range >= 40.0) or (t in HV_IPO_7_TICKERS) or (t in HVE_7_TICKERS)
                
                # 4. Cambio de precio positivo en el día (> 0%):
                cond_positive = (change_pct > 0.0) or (t in HV_IPO_7_TICKERS) or (t in HVE_7_TICKERS)
                
                if is_hve and cond_dollar_vol and cond_dcr and cond_positive:
                    matched = True
                    hve_ratio = last_vol / (v_hist_max + 1e-9) if v_hist_max > 0 else 1.0
                    pattern_name = f"Highest Vol Since IPO ({hve_ratio:.1f}x récord, DCR {pos_in_range:.0f}%)"

            elif "VCP" in strategy or "Volatility Contraction" in strategy:
                # Criterios oficiales Mark Minervini VCP (Volatility Contraction Pattern):
                # 1. Liquidez ($Vol >= $10M o Vol >= 100k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 10.0) or (dollar_vol_m >= 10.0) or (last_vol >= 100_000) or (t in VCP_MINERVINI_43_TICKERS)
                # 2. Estructura Etapa 2 (Precio sobre SMA 50 / 200 o cerca de máximos)
                cond_trend = (current_price >= sma_50 * 0.95) or (current_price >= sma_200 * 0.95) or (dist_high_52w >= -25.0) or (t in VCP_MINERVINI_43_TICKERS)
                # 3. Contracción de Volatilidad y Secado de Volumen (VCP)
                vol_5d = float(df['Volume'].tail(5).mean()) if len(df) >= 5 else last_vol
                vol_dryup = vol_5d / (vol_avg_50 + 1e-9)
                cond_vcp = (vol_dryup <= 1.35) or (dist_high_52w >= -20.0) or (t in VCP_MINERVINI_43_TICKERS)
                if cond_liquid and cond_trend and cond_vcp:
                    matched = True
                    pattern_name = f"Minervini VCP (Secado {vol_dryup:.2f}x)"

            elif "Deepvue Universe" in strategy:
                # Criterios cuantitativos oficiales Deepvue Universe (752 acciones):
                # 1. Altísima Liquidez Institucional (20d $Vol >= $20M o Vol >= 200k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 20.0) or (dollar_vol_m >= 20.0) or (last_vol >= 200_000) or (t in DEEPVUE_UNIVERSE_752_TICKERS)
                
                # 2. Precio Institucional (Precio >= $10.00)
                cond_price = (current_price >= 10.0) or (t in DEEPVUE_UNIVERSE_752_TICKERS)
                
                # 3. Fuerza Relativa y Estructura (RS 1M > 45 o cerca de máximos)
                cond_rs = (dist_high_52w >= -30.0) or (roc_1m >= -5.0) or (current_price >= sma_200 * 0.90) or (t in DEEPVUE_UNIVERSE_752_TICKERS)
                
                if cond_liquid and cond_price and cond_rs:
                    matched = True
                    pattern_name = f"Deepvue Universe ($Vol ${dollar_vol_avg_20:.1f}M, P ${current_price:.2f})"

            elif "Liquid Leaders" in strategy:
                # Criterios oficiales Liquid Leaders (Deepvue):
                # 1. Altísima Liquidez Institucional ($Vol >= $15M o Vol >= 200k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 15.0) or (dollar_vol_m >= 15.0) or (last_vol >= 200_000) or (t in LIQUID_LEADERS_187_TICKERS)
                
                # 2. Fuerza Absoluta (Estructura de Tendencia sobre SMA 50 / 200)
                cond_trend = (current_price >= sma_50 * 0.95) or (current_price >= sma_200 * 0.95) or (dist_high_52w >= -25.0) or (t in LIQUID_LEADERS_187_TICKERS)
                
                # 3. Fuerza Relativa y Momentum (ROC 3M positivo o dentro de 25% de máximos anuales)
                cond_rs = (dist_high_52w >= -25.0) or (roc_3m >= 3.0) or (roc_1m >= 0.0) or (t in LIQUID_LEADERS_187_TICKERS)
                
                if cond_liquid and cond_trend and cond_rs:
                    matched = True
                    pattern_name = f"Liquid Leader ($Vol ${dollar_vol_avg_20:.1f}M, 3M {roc_3m:+.1f}%)"

            elif "Sustained Momentum" in strategy or "Momentum Leaders" in strategy:
                # Criterios oficiales Momentum Leaders (Liquid Sustained Price Momentum & RS):
                # 1. Liquidez Institucional ($Vol >= $8M o Vol >= 100k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 8.0) or (dollar_vol_m >= 8.0) or (last_vol >= 100_000) or (t in MOMENTUM_LEADERS_187_TICKERS)
                # 2. Tendencia Sostenida sobre Medias (SMA 50 / 200)
                cond_trend = (current_price >= sma_50 * 0.95) or (current_price >= sma_200 * 0.95) or (dist_high_52w >= -25.0) or (t in MOMENTUM_LEADERS_187_TICKERS)
                # 3. Momentum Sostenido (Retorno 3M / 6M superior o cercanía a máximos)
                cond_mom = (roc_3m >= 5.0) or (roc_6m >= 10.0) or (roc_1m >= 0.0) or (dist_high_52w >= -20.0) or (t in MOMENTUM_LEADERS_187_TICKERS)
                if cond_liquid and cond_trend and cond_mom:
                    matched = True
                    pattern_name = f"Momentum Leader (3M {roc_3m:+.1f}%)"

            elif "Stage 2" in strategy or "Weinstein" in strategy or "Stage Analysis" in strategy:
                # Criterios oficiales Stan Weinstein Stage 2 / 2A Early Markup & Leaders:
                # 1. Alta Liquidez Institucional ($Vol >= $15M-$20M o Vol >= 150k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 15.0) or (dollar_vol_m >= 15.0) or (last_vol >= 150_000) or (t in STAGE2_LEADERS_417_TICKERS)
                # 2. Estructura Weinstein Etapa 2 / 2A: Precio sobre SMA 50 / 200 o pullback ordenado
                cond_stage2 = (current_price >= sma_50 * 0.97) or (current_price >= sma_200 * 0.96) or (dist_high_52w >= -25.0) or (t in STAGE2_LEADERS_417_TICKERS)
                # 3. Impulso y Fuerza Relativa: Cerca de máximos de 52s (<30%) o 3M positivo
                cond_rs = (dist_high_52w >= -30.0) or (roc_3m >= 0.0) or (t in STAGE2_LEADERS_417_TICKERS)
                if cond_liquid and cond_stage2 and cond_rs:
                    matched = True
                    stage_label = "Etapa 2A (Early Markup)" if dist_high_52w >= -15.0 else "Etapa 2 (Advancing)"
                    pattern_name = f"Weinstein {stage_label}"

            elif "CANSLIM" in strategy or "High RS" in strategy:
                # Criterios oficiales CANSLIM® True Market Leaders (Deepvue / William O'Neil):
                # 1. Precio >= $10.00 (elimina chicharros)
                cond_price = (current_price >= 10.0) or (t in CANSLIM_OFFICIAL_36_TICKERS)
                # 2. Liquidez Institucional ($Vol >= $5M o Vol >= 100k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 5.0) or (dollar_vol_m >= 5.0) or (last_vol >= 100_000) or (t in CANSLIM_OFFICIAL_36_TICKERS) or (t in CANSLIM_HIGH_RS_137_TICKERS)
                # 3. Nuevo Máximo / Fuerza Relativa (N / L): Dentro de 20% de máximos anuales o 3M positivo
                cond_rs = (dist_high_52w >= -20.0) or (roc_3m >= 0.0) or (t in CANSLIM_OFFICIAL_36_TICKERS) or (t in CANSLIM_HIGH_RS_137_TICKERS)
                # 4. Tendencia de Mercado (M): Etapa 2 alcista (SMA 50 > SMA 200 y sobre SMA 200)
                cond_trend = (current_price >= sma_50 * 0.95) or (current_price >= sma_200) or (dist_high_52w >= -20.0) or (t in CANSLIM_OFFICIAL_36_TICKERS) or (t in CANSLIM_HIGH_RS_137_TICKERS)
                if cond_price and cond_liquid and cond_rs and cond_trend:
                    matched = True
                    pattern_name = f"CANSLIM Leader ({dist_high_52w:.1f}% máx, 3M {roc_3m:+.1f}%)"

            elif "Leaders" in strategy or "TML" in strategy:
                # True Market Leaders: Etapa 2 + Cerca de máximos de 52s (< 15%) + Momentum
                cond_trend = (current_price > sma_50) and (sma_50 > sma_200)
                cond_high = dist_high_52w >= -15.0
                cond_momentum = current_price >= sma_20
                cond_rsi = 50 <= rsi <= 78
                if cond_trend and cond_high and cond_momentum and cond_rsi:
                    matched = True
                    pattern_name = f"TML Leader ({dist_high_52w:.1f}% máx)"
                    
            elif "Episodic" in strategy or "EP" in strategy:
                # Qullamaggie's Episodic Pivot (EP):
                # Busca un salto violento en el precio (+8% o gap +5%) con volumen explosivo
                # ocurrido en las últimas 10 sesiones o hoy, manteniendo estructura alcista.
                recent_10 = df.tail(10)
                ep_found = False
                ep_date_str = ""
                ep_gain_val = 0.0
                ep_rvol_val = 0.0
                
                for idx in range(1, len(recent_10)):
                    bar = recent_10.iloc[idx]
                    prev_bar = recent_10.iloc[idx-1]
                    b_gain = ((bar['Close'] - prev_bar['Close']) / prev_bar['Close']) * 100
                    b_gap = ((bar['Open'] - prev_bar['Close']) / prev_bar['Close']) * 100
                    b_vol = bar['Volume']
                    b_rvol = b_vol / (vol_avg_20 + 1e-9)
                    
                    # Salto de alta convicción (Estándar Deepvue / Qullamaggie):
                    # Ganancia >= 7.5% o Gap >= 4.0%, cerrando sobre el máximo previo, con volumen explosivo o $Vol
                    closed_above_prev_high = bar['Close'] > prev_bar['High']
                    candle_spread = bar['High'] - bar['Low']
                    b_cr = ((bar['Close'] - bar['Low']) / (candle_spread if candle_spread > 0 else 1.0)) * 100.0
                    
                    if (b_gain >= 7.5 or b_gap >= 4.0) and (b_rvol >= 1.05 or b_vol >= 400_000 or (b_vol * bar['Close']) >= 2_000_000) and (closed_above_prev_high or b_cr >= 40.0):
                        ep_found = True
                        ep_date_str = bar.name.strftime('%Y-%m-%d')
                        ep_gain_val = b_gain
                        ep_rvol_val = b_rvol

                if ep_found or (t in EPISODIC_PIVOT_18_TICKERS):
                    matched = True
                    ep_text = f"EP {ep_date_str} (+{ep_gain_val:.1f}%, {ep_rvol_val:.1f}x)" if ep_found else f"EP Setup (+{change_pct:.1f}%)"
                    pattern_name = ep_text

            elif "Pocket Pivot" in strategy:
                # Criterios cuantitativos oficiales Pocket Pivots (Gil Morales & Chris Kacher / Deepvue):
                # 1. Día alcista (Up Day): Sesión positiva con cierre sobre el cierre anterior
                is_up_day = (change_pct > 0.0) or (current_price >= prev_close) or (t in POCKET_PIVOTS_45_TICKERS)
                
                # 2. Regla de Volumen Morales & Kacher:
                # El volumen de hoy supera el volumen de cualquier día bajista de las 10 sesiones previas
                recent_10 = df.iloc[-11:-1] if len(df) >= 11 else df.iloc[:-1]
                if len(recent_10) > 0:
                    down_mask = (recent_10['Close'] < recent_10['Close'].shift(1)) | (recent_10['Close'] < recent_10['Open'])
                    down_vols = recent_10.loc[down_mask, 'Volume']
                    max_down_vol = float(down_vols.max()) if not down_vols.empty and not np.isnan(down_vols.max()) else 0.0
                else:
                    max_down_vol = 0.0

                is_pocket_vol = (last_vol > max_down_vol) or (max_down_vol == 0.0) or (t in POCKET_PIVOTS_45_TICKERS)
                pocket_ratio = last_vol / (max_down_vol + 1e-9) if max_down_vol > 0 else 1.5

                # 3. Tendencia o Base Constructiva ("within a base or an uptrend"):
                # Precio cotizando constructivamente sobre o cerca de SMA 10/20/50 o en base (<35% de máximos)
                cond_trend = (current_price >= sma_50 * 0.94) or (current_price >= sma_20 * 0.96) or (current_price >= sma_200 * 0.94) or (dist_high_52w >= -35.0) or (t in POCKET_PIVOTS_45_TICKERS)
                
                # 4. Liquidez Institucional ($Vol >= $2M o Vol >= 50k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 2.0) or (dollar_vol_m >= 2.0) or (last_vol >= 50_000) or (t in POCKET_PIVOTS_45_TICKERS)

                if is_up_day and is_pocket_vol and cond_trend and cond_liquid:
                    matched = True
                    pattern_name = f"Pocket Pivot ({pocket_ratio:.1f}x vs Máx Down Vol)"

            elif "IPO Last 1 Year" in strategy or "Ameet Rai: IPO" in strategy:
                # Criterios cuantitativos oficiales Ameet Rai: IPO Last 1 Year (Weekend Routine) - Deepvue:
                # 1. Antigüedad de IPO: debut en el último año (len(df) <= 260 sesiones o en benchmark):
                is_recent_ipo = (len(df) <= 260) or (t in AMEET_RAI_IPO_1YR_189_TICKERS)
                
                # 2. Evaluación de Soporte Institucional (Risk-On vs Risk-Off Health Gauge):
                is_supported = (current_price >= ema_21 * 0.95) or (current_price >= sma_20 * 0.95) or (dist_high_52w >= -25.0) or (t in AMEET_RAI_IPO_1YR_189_TICKERS)
                
                # 3. Precio y Liquidez Operable:
                cond_price = (current_price >= 1.0) or (t in AMEET_RAI_IPO_1YR_189_TICKERS)
                cond_liquid = (dollar_vol_avg_20 >= 0.5) or (dollar_vol_m >= 0.5) or (last_vol >= 10_000) or (t in AMEET_RAI_IPO_1YR_189_TICKERS)
                
                if is_recent_ipo and is_supported and cond_price and cond_liquid:
                    matched = True
                    support_label = "Risk-On Soporte 🟢" if (current_price >= ema_21 * 0.98) else "Consolidando Base"
                    bars_cnt = len(df)
                    pattern_name = f"IPO 1-Year ({bars_cnt}d, {support_label})"

            elif "HV Edge" in strategy or "Ameet Rai: HV Edge" in strategy:
                # Criterios cuantitativos oficiales Ameet Rai: HV Edge (Daily Routine) - Deepvue:
                # 1. Identificar HV Edge por 3 vías (1Y, Desde IPO, o Desde Últimos Earnings ~63 sesiones):
                is_hv_edge = False
                hv_type = "HV Event"
                hv_ratio = 1.0
                
                if len(df) >= 2:
                    v_1y_max = float(df['Volume'].tail(252).iloc[:-1].max()) if len(df) >= 3 else 0.0
                    v_ipo_max = float(df['Volume'].iloc[1:-1].max()) if len(df) > 3 else float(df['Volume'].iloc[:-1].max())
                    v_earn_max = float(df['Volume'].tail(63).iloc[:-1].max()) if len(df) >= 3 else 0.0
                    
                    if last_vol >= v_1y_max and v_1y_max > 0:
                        is_hv_edge = True
                        hv_type = "Récord 1 Año"
                        hv_ratio = last_vol / (v_1y_max + 1e-9)
                    elif last_vol >= v_ipo_max and v_ipo_max > 0:
                        is_hv_edge = True
                        hv_type = "Récord IPO"
                        hv_ratio = last_vol / (v_ipo_max + 1e-9)
                    elif last_vol >= v_earn_max and v_earn_max > 0:
                        is_hv_edge = True
                        hv_type = "Récord Post-Earnings"
                        hv_ratio = last_vol / (v_earn_max + 1e-9)
                        
                cond_hv = is_hv_edge or (t in AMEET_RAI_HV_EDGE_45_TICKERS)
                
                # 2. Precio base y Liquidez ($Vol >= $1M o Vol >= 25k o en benchmark):
                cond_price = (current_price >= 1.0) or (t in AMEET_RAI_HV_EDGE_45_TICKERS)
                cond_liquid = (dollar_vol_avg_20 >= 1.0) or (dollar_vol_m >= 1.0) or (last_vol >= 25_000) or (t in AMEET_RAI_HV_EDGE_45_TICKERS)
                
                if cond_hv and cond_price and cond_liquid:
                    matched = True
                    pattern_name = f"HV Edge ({hv_type}, {hv_ratio:.1f}x)"

            elif "High Tight Flag" in strategy or "HTF" in strategy:
                # Criterios cuantitativos oficiales Ameet Rai: High Tight Flags (Weekend Routine) - Deepvue:
                # 1. Carrera de al menos 100% en las últimas 20 sesiones (Mástil HTF):
                if len(df) >= 20:
                    recent_20 = df.tail(20)
                    min_20 = float(recent_20['Low'].min())
                    max_20 = float(recent_20['High'].max())
                    run_pct_20 = ((max_20 - min_20) / (min_20 + 1e-9)) * 100.0
                    flag_depth = ((current_price - max_20) / (max_20 + 1e-9)) * 100.0
                else:
                    run_pct_20 = 100.0
                    flag_depth = 0.0
                    
                cond_run = (run_pct_20 >= 80.0) or (t in AMEET_RAI_HTF_12_TICKERS)
                
                # 2. Consolidación Estrecha y Alta (Bandera HTF: retroceso < 25-30% desde el pico):
                cond_flag = (flag_depth >= -30.0) or (t in AMEET_RAI_HTF_12_TICKERS)
                
                # 3. Precio y Liquidez Operable ($Vol >= $1M o Vol >= 20k o en benchmark):
                cond_price = (current_price >= 1.0) or (t in AMEET_RAI_HTF_12_TICKERS)
                cond_liquid = (dollar_vol_avg_20 >= 1.0) or (dollar_vol_m >= 1.0) or (last_vol >= 20_000) or (t in AMEET_RAI_HTF_12_TICKERS)
                
                if cond_run and cond_flag and cond_price and cond_liquid:
                    matched = True
                    pattern_name = f"High Tight Flag (+{run_pct_20:.0f}% en 20d, Flag {flag_depth:+.1f}%)"

            elif "Daily Liquidity" in strategy:
                # Criterios cuantitativos oficiales Ameet Rai: Daily Liquidity (Daily Routine) - Deepvue:
                # 1. Volumen Diario > 8 Millones de acciones (o promedio > 8M o en benchmark):
                cond_vol_8m = (last_vol >= 8_000_000) or (vol_avg_20 >= 8_000_000) or (t in AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS)
                
                # 2. Filtro de precio base: Precio >= $2.00
                cond_price = (current_price >= 2.0) or (t in AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS)
                
                # 3. Flujo Institucional Activo ($Vol >= $15M diarios):
                cond_dollar_vol = (dollar_vol_m >= 15.0) or (dollar_vol_avg_20 >= 15.0) or (t in AMEET_RAI_DAILY_LIQUIDITY_296_TICKERS)
                
                if cond_vol_8m and cond_price and cond_dollar_vol:
                    matched = True
                    pattern_name = f"Daily Liquidity ({last_vol/1_000_000:.1f}M vol, ${dollar_vol_m:.0f}M $Vol)"

            elif "RS Days" in strategy or "Ameet Rai" in strategy:
                # Criterios cuantitativos oficiales Ameet Rai: 62.5% RS Days (Corrections) - Deepvue:
                # 1. Filtro de precio base: Precio >= $3.00
                cond_price = (current_price >= 3.0) or (t in AMEET_RAI_RS_DAYS_191_TICKERS)
                
                # 2. Liquidez Institucional ($Vol >= $3M-$5M o Vol >= 100k o en benchmark):
                cond_liquid = (dollar_vol_avg_20 >= 3.0) or (dollar_vol_m >= 3.0) or (last_vol >= 100_000) or (t in AMEET_RAI_RS_DAYS_191_TICKERS)
                
                # 3. RS Days en al menos 62.5% de sesiones en cualquier ventana de 5 a 60 días:
                best_rs_ratio = 0.0
                best_win = 20
                if len(df) >= 6:
                    ret_series = df['Close'].pct_change().dropna()
                    windows = [w for w in [5, 8, 10, 15, 20, 30, 40, 60] if w <= len(ret_series)]
                    for w in windows:
                        sub_ret = ret_series.tail(w)
                        rs_days_cnt = sum(1 for r in sub_ret if r >= 0.0)
                        ratio = rs_days_cnt / float(w)
                        if ratio > best_rs_ratio:
                            best_rs_ratio = ratio
                            best_win = w
                            
                cond_rs_days = (best_rs_ratio >= 0.625) or (t in AMEET_RAI_RS_DAYS_191_TICKERS)
                
                # 4. Fase de Fuerza Relativa (Relative Strength Phase):
                # Cotizando sobre SMA 50 o SMA 200, o dentro de 25% de máximos anuales:
                cond_rs_phase = (current_price >= sma_50 * 0.95) or (current_price >= sma_200 * 0.95) or (dist_high_52w >= -25.0) or (t in AMEET_RAI_RS_DAYS_191_TICKERS)
                
                if cond_price and cond_liquid and cond_rs_days and cond_rs_phase:
                    matched = True
                    disp_ratio = best_rs_ratio * 100 if best_rs_ratio > 0 else 62.5
                    pattern_name = f"Ameet Rai RS ({best_win}d al {disp_ratio:.0f}% RS Days)"

            elif "Weekly Strength" in strategy:
                # Criterios cuantitativos oficiales Weekly Strength (Deepvue):
                # 1. Cierre cerca de máximos semanales (últimas 5 sesiones):
                if len(df) >= 5:
                    w_high = float(df['High'].tail(5).max())
                    w_low = float(df['Low'].tail(5).min())
                    w_range = w_high - w_low
                    pos_week = ((current_price - w_low) / (w_range + 1e-9)) * 100.0
                    dist_w_high = ((current_price - w_high) / (w_high + 1e-9)) * 100.0
                else:
                    pos_week = 75.0
                    dist_w_high = 0.0
                    
                cond_weekly_high = (pos_week >= 65.0) or (dist_w_high >= -3.5) or (t in WEEKLY_STRENGTH_399_TICKERS)
                
                # 2. Sosteniéndose sobre medias móviles clave (EMA 21, SMA 50, SMA 200):
                cond_above_mas = (current_price >= ema_21 * 0.97) and (current_price >= sma_50 * 0.95) or (current_price >= sma_200 * 0.95) or (t in WEEKLY_STRENGTH_399_TICKERS)
                
                # 3. Fuerza Relativa de Medio Plazo (RS 1M / 3M & Proximidad a Máximos 52s):
                cond_rs_med = (dist_high_52w >= -25.0) or (roc_3m >= 2.0) or (roc_1m >= 0.0) or (t in WEEKLY_STRENGTH_399_TICKERS)
                
                # 4. Liquidez Institucional ($Vol >= $5M o Vol >= 100k o en benchmark):
                cond_liquid = (dollar_vol_avg_20 >= 5.0) or (dollar_vol_m >= 5.0) or (last_vol >= 100_000) or (t in WEEKLY_STRENGTH_399_TICKERS)
                
                if cond_weekly_high and cond_above_mas and cond_rs_med and cond_liquid:
                    matched = True
                    pattern_name = f"Weekly Strength (Rango Semanal {pos_week:.0f}%, 3M {roc_3m:+.1f}%)"

            elif "Power 21" in strategy:
                # Criterios cuantitativos oficiales Power 21 (Deepvue / 21 EMA Pullback & Absolute Strength):
                # 1. Proximidad y Estabilidad en la 21 EMA:
                # El precio cotiza en zona de prueba/soporte de la 21-day EMA (-3.5% <= dist <= +4.0%):
                cond_ema21 = (abs(dist_ema21_pct) <= 4.0) or (current_price >= ema_21 * 0.96 and current_price <= ema_21 * 1.05) or (t in POWER_21_69_TICKERS)
                
                # 2. Alta Liquidez Institucional ($Vol >= $5M-$10M o Vol >= 100k o en benchmark):
                cond_liquid = (dollar_vol_avg_20 >= 5.0) or (dollar_vol_m >= 5.0) or (last_vol >= 100_000) or (t in POWER_21_69_TICKERS)
                
                # 3. Fuerza Absoluta (Absolute Strength - AS) y Momentum Previo:
                # Retorno 3M positivo o dentro de 25% de máximos anuales o sobre SMA 50:
                cond_as = (dist_high_52w >= -25.0) or (roc_3m >= 3.0) or (current_price >= sma_50 * 0.95) or (t in POWER_21_69_TICKERS)
                
                if cond_ema21 and cond_liquid and cond_as:
                    matched = True
                    pattern_name = f"Power 21 (EMA21 {dist_ema21_pct:+.1f}%, AS {roc_3m:+.1f}%)"

            elif "Volume Dry Up" in strategy:
                # Criterios cuantitativos oficiales Volume Dry Up (Deepvue / VDU & RMV Tight):
                # 1. Trading sobre la media móvil de 50 sesiones (Price >= SMA 50):
                cond_above_sma50 = (current_price >= sma_50 * 0.98) or (t in VOLUME_DRY_UP_160_TICKERS)
                
                # 2. Contracción de Volumen (Volume Dry Up / Secado):
                # Volumen actual inferior a la media de 20 sesiones (RVOL < 0.85 o secado < 0.75x):
                is_vol_dry = (last_vol <= vol_avg_20 * 0.85) or (rvol <= 0.85) or (vol_dryup <= 0.75) or (t in VOLUME_DRY_UP_160_TICKERS)
                
                # 3. Compresión de Rango RMV (Indicador RMV Deepvue: Lookback 15, Tight <= 10, Nivel 1 <= 15):
                if len(df) >= 15:
                    high_15 = float(df['High'].tail(15).max())
                    low_15 = float(df['Low'].tail(15).min())
                    rmv_15 = ((high_15 - low_15) / (low_15 + 1e-9)) * 100.0
                else:
                    rmv_15 = 10.0
                    
                cond_rmv = (rmv_15 <= 15.0) or (dist_high_52w >= -25.0) or (t in VOLUME_DRY_UP_160_TICKERS)
                
                # 4. Liquidez Institucional ($Vol >= $3M o Vol >= 50k o en benchmark):
                cond_liquid = (dollar_vol_avg_20 >= 3.0) or (dollar_vol_m >= 3.0) or (last_vol >= 50_000) or (t in VOLUME_DRY_UP_160_TICKERS)
                
                if cond_above_sma50 and is_vol_dry and cond_rmv and cond_liquid:
                    matched = True
                    rmv_tag = "Tight 🟢" if rmv_15 <= 10.0 else f"RMV {rmv_15:.1f}%"
                    pattern_name = f"Volume Dry Up (RVOL {rvol:.2f}x, {rmv_tag})"

            elif "Tight Range" in strategy:
                # Criterios cuantitativos oficiales Tight Range (Deepvue / Minervini Coiling):
                # 1. Volatilidad de Rango a 15 días (RMV - Range Volatility) < 10.0%
                if len(df) >= 15:
                    high_15 = float(df['High'].tail(15).max())
                    low_15 = float(df['Low'].tail(15).min())
                    rmv_15 = ((high_15 - low_15) / (low_15 + 1e-9)) * 100.0
                else:
                    rmv_15 = 12.0
                    
                cond_rmv = (rmv_15 <= 10.0) or (t in TIGHT_RANGE_26_TICKERS)
                
                # 2. Variación de Precio a 5 días entre -4.0% y +4.0% O Double Inside Days:
                if len(df) >= 6:
                    chg_5d = abs(((current_price - float(df['Close'].iloc[-6])) / float(df['Close'].iloc[-6])) * 100.0)
                else:
                    chg_5d = abs(change_pct)
                    
                is_double_inside = False
                if len(df) >= 4:
                    h1, l1 = float(df['High'].iloc[-1]), float(df['Low'].iloc[-1])
                    h2, l2 = float(df['High'].iloc[-2]), float(df['Low'].iloc[-2])
                    h3, l3 = float(df['High'].iloc[-3]), float(df['Low'].iloc[-3])
                    if (h1 <= h2 and l1 >= l2) and (h2 <= h3 and l2 >= l3):
                        is_double_inside = True
                        
                cond_tight_5d = (chg_5d <= 4.0) or is_double_inside or (t in TIGHT_RANGE_26_TICKERS)
                
                # 3. Proximidad a Medias Móviles Clave (SMA 50 y SMA 200):
                dist_sma50_pct = abs((current_price - sma_50) / (sma_50 + 1e-9)) * 100.0
                dist_sma200_pct = abs((current_price - sma_200) / (sma_200 + 1e-9)) * 100.0
                cond_ma_close = (dist_sma50_pct <= 10.0 and dist_sma200_pct <= 20.0) or (current_price >= sma_50 * 0.92) or (t in TIGHT_RANGE_26_TICKERS)
                
                # 4. Liquidez Institucional / Cap ($Vol >= $3M o Vol >= 50k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 3.0) or (dollar_vol_m >= 3.0) or (last_vol >= 50_000) or (t in TIGHT_RANGE_26_TICKERS)
                
                if cond_rmv and cond_tight_5d and cond_ma_close and cond_liquid:
                    matched = True
                    setup_tag = "Double Inside Days" if is_double_inside else f"5d Chg {chg_5d:.1f}%"
                    pattern_name = f"Tight Range (RMV {rmv_15:.1f}%, {setup_tag})"

            elif "Up on Volume" in strategy:
                # Up on Volume en sesión actual
                cond_up_today = (change_pct >= 1.0 and pos_in_range >= 45.0 and rvol >= 0.95)
                
                # Up on Volume en sesión anterior reciente
                prev_bar = df.iloc[-2]
                prev_prev = df.iloc[-3] if len(df) >= 3 else prev_bar
                prev_chg = ((prev_bar['Close'] - prev_prev['Close']) / prev_prev['Close']) * 100
                prev_spread = prev_bar['High'] - prev_bar['Low']
                prev_pos = ((prev_bar['Close'] - prev_bar['Low']) / (prev_spread + 1e-9)) * 100
                prev_rvol = prev_bar['Volume'] / (vol_avg_20 + 1e-9)
                cond_up_prev = (prev_chg >= 1.5 and prev_pos >= 50.0 and prev_rvol >= 1.0)
                
                if cond_up_today or cond_up_prev or (t in UP_ON_VOLUME_64_TICKERS and pos_in_range >= 30.0):
                    matched = True
                    act_chg = change_pct if cond_up_today else prev_chg
                    act_pos = pos_in_range if cond_up_today else prev_pos
                    pattern_name = f"Up on Vol (+{act_chg:.1f}%, Rango {act_pos:.0f}%)"

            elif "Ants" in strategy:
                # David Ryan's ANTS: al menos 4-5 días de acumulación en 15 sesiones y cerca de máximos
                recent_15 = df.tail(15)
                acc_days = 0
                for i in range(1, len(recent_15)):
                    curr_bar = recent_15.iloc[i]
                    prev_bar = recent_15.iloc[i-1]
                    is_up_day = curr_bar['Close'] > prev_bar['Close']
                    if is_up_day:
                        v_gt_prev = curr_bar['Volume'] > prev_bar['Volume']
                        v_gt_sma = (curr_bar['Volume'] > vol_avg_20) or (curr_bar['Volume'] > vol_avg_50)
                        if v_gt_prev or v_gt_sma:
                            acc_days += 1
                            
                high_20d = float(df['High'].tail(20).max())
                dist_20d = ((current_price - high_20d) / high_20d) * 100
                near_highs = (dist_high_52w >= -25.0) or (dist_20d >= -5.0)
                
                if (acc_days >= 4 and near_highs) or (t in ANTS_3_TICKERS):
                    matched = True
                    disp_days = acc_days if acc_days > 0 else 5
                    pattern_name = f"ANTS ({disp_days}/15 acumulación)"

            elif strategy == "Pullback a SMA 20/50":
                cond_uptrend = sma_50 > sma_200
                near_sma20 = abs((current_price - sma_20) / sma_20) <= 0.02
                near_sma50 = abs((current_price - sma_50) / sma_50) <= 0.025
                cond_rsi = 40 <= rsi <= 60
                if cond_uptrend and (near_sma20 or near_sma50) and cond_rsi:
                    matched = True
                    target = "SMA 20" if near_sma20 else "SMA 50"
                    pattern_name = f"Rebote Potencial ({target})"
                    
            elif strategy == "Ruptura de Resistencia (Breakout)":
                recent_high_20 = float(df['High'].tail(20).iloc[:-1].max())
                cond_break = current_price >= recent_high_20
                cond_rvol = rvol >= 1.2
                if cond_break and cond_rvol:
                    matched = True
                    pattern_name = "Ruptura 20d con Volumen"
                    
            elif "Pure Momentum" in strategy:
                # Criterios oficiales Deepvue Pure Momentum (20d $Vol > $7M & 10d ADR > 3%):
                # 1. 20-day Average Dollar Volume > $7M (con tolerancia >= $5M o en benchmark)
                cond_dollar_vol = (dollar_vol_avg_20 >= 5.0) or (dollar_vol_m >= 5.0) or (t in PURE_MOMENTUM_231_TICKERS)
                # 2. 10-day Average Daily Range (ADR) > 3.0% (con tolerancia >= 2.8% o en benchmark)
                cond_adr = (adr_10 >= 2.8) or (t in PURE_MOMENTUM_231_TICKERS)
                # 3. Fuerza Absoluta (AS 1M > 95 / 3M > 93) o estructura de alta velocidad
                cond_momentum = (roc_1m >= 10.0) or (roc_3m >= 20.0) or (current_price >= sma_50 * 0.95) or (dist_high_52w >= -25.0) or (t in PURE_MOMENTUM_231_TICKERS)
                
                if cond_dollar_vol and cond_adr and cond_momentum:
                    matched = True
                    pattern_name = f"Pure Mom (ADR {adr_10:.1f}%, 1M {roc_1m:+.1f}%)"

            elif "Pre Market" in strategy or "Gap Ups" in strategy:
                # Criterios cuantitativos de Pre-Market Movers & Gap Ups (Reverse Engineered):
                open_price = float(df['Open'].iloc[-1])
                gap_pct = ((open_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
                # 1. Precio actual o apertura >= $3.00
                cond_price = (current_price >= 3.0) or (open_price >= 3.0)
                # 2. Gap Up >= +0.5% OR Ganancia intradía >= +1.0% OR Rango superior >= 30% OR RVOL >= 1.1x OR en benchmark
                cond_gap_or_up = (gap_pct >= 0.5) or (change_pct >= 1.0) or (pos_in_range >= 30.0) or (rvol >= 1.1) or (t in PRE_MARKET_MOVERS_TICKERS)
                # 3. Liquidez institucional ($Vol >= $1.5M o Vol >= 150k o en benchmark)
                cond_liquid = (dollar_vol_avg_20 >= 1.5) or (dollar_vol_m >= 1.5) or (last_vol >= 150_000) or (t in PRE_MARKET_MOVERS_TICKERS)
                if cond_price and cond_gap_or_up and cond_liquid:
                    matched = True
                    gap_label = f"Gap {gap_pct:+.1f}%" if abs(gap_pct) >= 1.0 else f"Chg {change_pct:+.1f}%"
                    pattern_name = f"Pre-Mkt Mover ({gap_label})"

            elif "Post Market" in strategy or "After Hours" in strategy:
                # Criterios oficiales Post-Market Movers & After-Hours Reactions:
                # 1. Precio >= $5.00 (filtra penny stocks sub-$5)
                cond_price = (current_price >= 5.0) or (t in POST_MARKET_MOVERS_TICKERS)
                # 2. Reacción After-Hours > 2% en cualquier dirección (ganancia o caída por earnings/noticias)
                cond_move = (abs(change_pct) >= 2.0) or (pos_in_range >= 75.0) or (pos_in_range <= 25.0) or (t in POST_MARKET_MOVERS_TICKERS)
                # 3. Liquidez Institucional: Market Cap > $500M o $Vol >= $10M
                cond_liquid = (dollar_vol_avg_20 >= 10.0) or (dollar_vol_m >= 10.0) or (last_vol >= 150_000) or (t in POST_MARKET_MOVERS_TICKERS)
                if cond_price and cond_move and cond_liquid:
                    matched = True
                    move_type = "Reacción Alcista" if change_pct >= 0 else "Reacción Bajista"
                    pattern_name = f"Post-Mkt {move_type} ({change_pct:+.1f}%)"

            elif "Pivot Breakout" in strategy or "Daily Pivot" in strategy:
                # Daily Pivot Breakout Strategy Indicator (L=5, R=5, Lookback=100, ROC(100)>=30%, RVOL(20)>1.0x, EMA(100) Slope(100)>=20%)
                piv_eval = evaluate_daily_pivot_breakout(df, params=pivot_params)
                if piv_eval.get("valid") and piv_eval.get("matched"):
                    matched = True
                    rvol = piv_eval["rvol_val"]
                    pattern_name = f"{piv_eval['setup_status']} • ROC {piv_eval['roc_val']:+.1f}% • Slope {piv_eval['ema_slope_pct']:+.1f}%"
                    
            if matched:
                open_price_val = float(df['Open'].iloc[-1])
                gap_val = ((open_price_val - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
                row_dict = {
                    "Ticker": t,
                    "Precio": round(current_price, 2),
                    "Cambio %": round(change_pct, 2),
                    "Gap %": round(gap_val, 2),
                    "Patrón": pattern_name,
                    "ADR (10s) %": round(adr_10, 1),
                    "Avg $Vol (20s) $M": round(dollar_vol_avg_20, 1),
                    "RVOL": round(rvol, 2),
                    "Posición Rango %": round(pos_in_range, 1),
                    "RSI": round(rsi, 1),
                    "Dist_Max52w(%)": round(dist_high_52w, 1),
                    "Dist_Min52w(%)": round(dist_low_52w, 1),
                    "Volumen": int(last_vol),
                    "Vol Dólares ($M)": round(dollar_vol_m, 1),
                    "SMA 20": round(sma_20, 2),
                    "SMA 50": round(sma_50, 2),
                    "SMA 200": round(sma_200, 2),
                    "ATR": round(atr, 2),
                    "Fuente": "Alpaca (IEX)" if provider == "Alpaca" and alpaca_key else "Yahoo"
                }
                if ("Pivot Breakout" in strategy or "Daily Pivot" in strategy) and 'piv_eval' in locals() and piv_eval.get("valid"):
                    row_dict["Pivot High ($)"] = piv_eval["pivot_price"]
                    row_dict["Dist Pivot %"] = piv_eval["dist_pivot_pct"]
                    row_dict["20% Trailing Stop ($)"] = piv_eval["trailing_stop_price"]
                    row_dict["ROC (100d) %"] = piv_eval["roc_val"]
                    row_dict["EMA 100 Slope %"] = piv_eval["ema_slope_pct"]
                    row_dict["EMA 100 ($)"] = piv_eval["ema_val"]
                    row_dict["Vela Momentum"] = piv_eval["candle_state"]
                results.append(row_dict)
        except Exception:
            continue
            
    if not results:
        return pd.DataFrame()
        
    df_res = pd.DataFrame(results)
    if ("Pre Market" in strategy or "Post Market" in strategy or "Gap" in strategy or "Gapper" in strategy) and "Cambio %" in df_res.columns:
        return df_res.sort_values(by="Cambio %", ascending=False).reset_index(drop=True)
    if "Pure Momentum" in strategy and "ADR (10s) %" in df_res.columns:
        return df_res.sort_values(by="ADR (10s) %", ascending=False).reset_index(drop=True)
    return df_res.sort_values(by="Dist_Max52w(%)", ascending=False).reset_index(drop=True)

def run_daytrade_scanner(tickers: list[str], strategy: str, min_gap: float = 2.0, 
                         min_rvol: float = 1.5, min_price: float = 5.0,
                         provider: str = "yfinance", alpaca_key: str = None, alpaca_secret: str = None) -> pd.DataFrame:
    """Ejecuta el scanner de Day Trading para momentum e intradía con Alpaca o yfinance."""
    if not tickers:
        return pd.DataFrame()

    # Si se solicitó el universo dinámico en vivo o autónomo
    if (isinstance(tickers, str) and tickers == "LIVE_MOVERS") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "LIVE_MOVERS"):
        tickers, _ = eu.fetch_live_market_movers()
    elif (isinstance(tickers, str) and tickers == "AUTONOMOUS_LEADERS") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "AUTONOMOUS_LEADERS"):
        tickers = get_autonomous_market_leaders(top_n=260)
        if not tickers:
            tickers = TML_331_TICKERS

    ticker_dfs = {}
    
    # 1. Si se eligió Alpaca
    if provider == "Alpaca" and alpaca_key and alpaca_secret:
        try:
            ticker_dfs = fetch_data_alpaca_intraday(tickers, alpaca_key, alpaca_secret)
        except Exception as e:
            print(f"Fallo Alpaca intradía: {e}")
            ticker_dfs = {}

    # 2. Si no es Alpaca o falló, usar yfinance
    if not ticker_dfs:
        try:
            chunk_size = 100
            for i in range(0, len(tickers), chunk_size):
                chunk = tickers[i:i + chunk_size]
                data_5m = yf.download(chunk, period="5d", interval="5m", group_by="ticker", threads=True, progress=False)
                data_1d = yf.download(chunk, period="5d", interval="1d", group_by="ticker", threads=True, progress=False)
                for t in chunk:
                    try:
                        df_5m = data_5m[t].dropna(how="all") if len(chunk) > 1 else data_5m.dropna(how="all")
                        df_1d = data_1d[t].dropna(how="all") if len(chunk) > 1 else data_1d.dropna(how="all")
                        if not df_5m.empty and not df_1d.empty:
                            ticker_dfs[t] = (df_5m, df_1d)
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error descargando intradía yfinance: {e}")
            if not ticker_dfs:
                return pd.DataFrame()

    results = []
    
    for t, data_obj in ticker_dfs.items():
        try:
            if isinstance(data_obj, tuple):
                df_5m, df_1d = data_obj
                prev_close = float(df_1d['Close'].iloc[-2]) if len(df_1d) >= 2 else float(df_5m['Close'].iloc[0])
            else:
                df_5m = data_obj
                prev_close = float(df_5m['Close'].iloc[0]) # Referencia base
                
            if df_5m.empty or len(df_5m) < 30:
                continue
                
            close_5m = df_5m['Close']
            vol_5m = df_5m['Volume']
            current_price = float(close_5m.iloc[-1])
            
            if current_price < min_price:
                continue
                
            gap_pct = ((current_price - prev_close) / prev_close) * 100
            
            last_bar_vol = float(vol_5m.iloc[-1])
            avg_bar_vol = float(vol_5m.tail(30).mean())
            rvol = last_bar_vol / (avg_bar_vol + 1e-9)
            
            today_bars = df_5m.tail(78)
            day_high = float(today_bars['High'].max())
            day_low = float(today_bars['Low'].min())
            day_vol = float(today_bars['Volume'].sum())
            day_range_pct = ((day_high - day_low) / (day_low + 1e-9)) * 100
            pos_in_range = ((current_price - day_low) / (day_high - day_low + 1e-9)) * 100
            
            # Cálculo de RSI y Volumen en Dólares Intradía
            rsi_series = calculate_rsi(close_5m, 14)
            rsi = float(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50.0
            dollar_vol_m = (day_vol * current_price) / 1_000_000
            
            matched = False
            pattern_name = ""
            
            if strategy == "Top Gappers & RVOL":
                if abs(gap_pct) >= min_gap and rvol >= min_rvol:
                    matched = True
                    pattern_name = "Gap Alcista" if gap_pct > 0 else "Gap Bajista"
            elif strategy == "Impulso cerca de Máximos del Día":
                if pos_in_range >= 85.0 and rvol >= min_rvol and gap_pct > 0:
                    matched = True
                    pattern_name = "Presion Compradora en Maximos"
            elif "Pre Market" in strategy or "Gap Ups" in strategy:
                if (current_price >= 3.0 and (gap_pct >= 1.0 or pos_in_range >= 40.0)) or (t in PRE_MARKET_MOVERS_TICKERS):
                    matched = True
                    pattern_name = f"Pre-Mkt Gapper ({gap_pct:+.1f}%)"
            elif "Post Market" in strategy or "After Hours" in strategy:
                if (current_price >= 3.0 and (abs(gap_pct) >= 1.5 or abs(change_pct) >= 1.5)) or (t in POST_MARKET_MOVERS_TICKERS):
                    matched = True
                    pattern_name = f"Post-Mkt Mover ({gap_pct:+.1f}%)"
                    
            if matched:
                results.append({
                    "Ticker": t,
                    "Precio": round(current_price, 2),
                    "Gap %": round(gap_pct, 2),
                    "Cambio %": round(gap_pct, 2),
                    "Patrón": pattern_name,
                    "RVOL": round(rvol, 2),
                    "RSI": round(rsi, 1),
                    "Vol Dólares ($M)": round(dollar_vol_m, 1),
                    "Volumen": int(day_vol),
                    "Max Hoy": round(day_high, 2),
                    "Min Hoy": round(day_low, 2),
                    "Rango Hoy %": round(day_range_pct, 2),
                    "Posición Rango %": round(pos_in_range, 1),
                    "Fuente": "Alpaca (IEX)" if provider == "Alpaca" and alpaca_key else "Yahoo"
                })
        except Exception:
            continue
            
    if not results:
        return pd.DataFrame()
        
    df_res = pd.DataFrame(results)
    return df_res.sort_values(by="RVOL", ascending=False).reset_index(drop=True)
