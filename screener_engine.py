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

# Universo Maestro de Mercado Completo EE.UU. (S&P 500 + S&P 400 + S&P 600 + Nasdaq 100 + High Momentum + Deepvue 752 + TML)
FULL_US_MARKET_TICKERS = sorted(list(set(
    US_BROAD_MARKET_TICKERS
    + HIGH_MOMENTUM_EXPANDED_TICKERS
    + DEEPVUE_UNIVERSE_752_TICKERS
    + TML_331_TICKERS
    + LIQUID_LEADERS_187_TICKERS
    + MOMENTUM_LEADERS_186_TICKERS
    + WEEKLY_STRENGTH_399_TICKERS
    + DAILY_PIVOT_BREAKOUT_TICKERS
)))

# Caché en memoria de barras diarias (TTL 5 minutos) para escanear los ~1,850 activos en <1.5s al cambiar de filtro
_DAILY_BARS_CACHE = {
    "timestamp": 0.0,
    "provider": "",
    "data": {}
}

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
    Evalúa en tiempo real el indicador 'Daily Pivot Breakout Strategy Indicator (by Mike)':
    - Left Strength (5), Right Strength (5), Pivot Lookback (100)
    - ROC Period (100 días) >= Minimum ROC (30%)
    - RVOL Period (20 días): Volumen de ruptura > SMA(Volumen, 20) (RVOL > 1.0x)
    - EMA Length (100), EMA Slope Lookback (100), EMA Smooth Length (1), Min EMA Slope % (20%)
    - 20% Trailing Stop (•••••••) y Momentum Candle Colors.
    IMPORTANTE: Evalúa TODOS los Pivot Highs confirmados e intactos (no rotos previamente) dentro de las
    últimas 100 sesiones. Un 'Breakout' solo se dispara cuando el precio cruza un Pivot High intacto
    en la sesión actual (o dentro de la ventana de ruptura reciente de 1 a 3 días), nunca por trades viejos.
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
        "breakout_window_days": 3,
        "include_near_pivot": False,
        "include_active_trade": False,
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
    bk_win = max(1, int(cfg.get("breakout_window_days", 3)))
    include_near = bool(cfg.get("include_near_pivot", False))
    include_active = bool(cfg.get("include_active_trade", False))

    n = len(df)
    if n < max(L + R + 10, 60):
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
        return {"valid": False}

    # 3. Simulación barra a barra exacta:
    #    Cada vez que se confirma un nuevo Pivot High (5L/5R), se registra como nivel de resistencia.
    #    En cada barra b verificamos si Close[b] rompe por primera vez cualquiera de los Pivot Highs
    #    confirmados e intactos dentro de las últimas `piv_lb` (100) barras.
    pivot_line_series = np.full(n, np.nan)
    trailing_stop_series = np.full(n, np.nan)
    entry_signals = []   # (bar_idx, date, close_price, broken_pivot_price)
    exit_signals = []    # (bar_idx, date, close_price, trailing_stop_price)

    in_trade = False
    peak_since_entry = 0.0
    known_pivots = []  # [piv_idx, piv_price, piv_date, broken_bool]

    for b in range(max(L + R, 20), n):
        if b in pivot_at_bar:
            p_i, p_val, p_dt = pivot_at_bar[b]
            # Si ya fue superado durante las R barras de confirmación, nace roto; si no, nace intacto
            already_exceeded = np.any(closes[p_i + 1:b] > p_val * 1.002)
            known_pivots.append([p_i, p_val, p_dt, bool(already_exceeded)])

        # Pivotes dentro de la ventana Pivot Lookback (100 barras)
        valid_pivs = [p for p in known_pivots if (b - p[0]) <= piv_lb]
        unbroken_pivs = [p for p in valid_pivs if not p[3]]

        # El Pivot High activo a mostrar en la línea verde es el pivote intacto más cercano por encima del precio previo (o el más reciente)
        ref_piv = None
        if unbroken_pivs:
            prev_c_val = closes[b - 1] if b >= 1 else closes[b]
            above_prev = [p for p in unbroken_pivs if p[1] >= prev_c_val * 0.995]
            ref_piv = min(above_prev, key=lambda x: x[1]) if above_prev else unbroken_pivs[-1]
            pivot_line_series[b] = ref_piv[1]
        elif valid_pivs:
            ref_piv = max(valid_pivs, key=lambda x: x[1])
            pivot_line_series[b] = ref_piv[1]

        # Actualizar 20% Trailing Stop si hay un trade abierto
        if in_trade:
            peak_since_entry = max(peak_since_entry, highs[b], closes[b])
            t_stop = peak_since_entry * (1.0 - trail_pct / 100.0)
            trailing_stop_series[b] = t_stop
            if closes[b] < t_stop:
                in_trade = False
                exit_signals.append((b, df.index[b], float(closes[b]), float(t_stop)))

        # Verificar si en la barra b se rompe por primera vez algún Pivot High intacto del lookback
        broken_now = [p for p in unbroken_pivs if closes[b] > p[1]]
        if broken_now:
            # Tomamos el pivote roto de mayor nivel estructural
            target_piv = max(broken_now, key=lambda x: x[1])
            piv_val = target_piv[1]
            mom_ok = (roc_series[b] >= min_roc)
            slope_ok = (ema_slope_series[b] >= min_slope) and (closes[b] > ema_vals[b])
            rvol_ok = (rvol_series[b] >= min_rvol)

            # Marcar como rotos todos los pivotes superados al cierre de la barra b
            for p in broken_now:
                p[3] = True

            if mom_ok and slope_ok and rvol_ok:
                pivot_line_series[b] = piv_val
                if not in_trade:
                    in_trade = True
                    peak_since_entry = max(highs[b], closes[b])
                    trailing_stop_series[b] = peak_since_entry * (1.0 - trail_pct / 100.0)
                entry_signals.append((b, df.index[b], float(closes[b]), float(piv_val)))

    # Determinar el Pivot High de referencia actual para la tabla y el gráfico:
    # 1. Si hubo un Entry Signal reciente (en los últimos `bk_win` días), mostramos el pivote exacto que acaba de romper
    recent_entries = [e for e in entry_signals if (n - 1 - e[0]) < bk_win]
    fresh_cross = len(recent_entries) > 0

    valid_pivs_now = [p for p in known_pivots if (n - 1 - p[0]) <= piv_lb]
    unbroken_now = [p for p in valid_pivs_now if not p[3]]

    if fresh_cross:
        last_ent = recent_entries[-1]
        active_piv_price = float(last_ent[3])
        active_piv_date = str(last_ent[1])[:10]
        breakout_bar_rvol = max(curr_rvol, float(rvol_series[last_ent[0]]))
    elif unbroken_now:
        # El pivote intacto más cercano por encima del precio actual
        above_curr = [p for p in unbroken_now if p[1] >= curr_close]
        chosen_p = min(above_curr, key=lambda x: x[1]) if above_curr else unbroken_now[-1]
        active_piv_price = float(chosen_p[1])
        active_piv_date = str(chosen_p[2])[:10]
        breakout_bar_rvol = curr_rvol
    else:
        highest_p = max(confirmed_pivots, key=lambda x: x[1])
        active_piv_price = float(highest_p[1])
        active_piv_date = str(highest_p[2])[:10]
        breakout_bar_rvol = curr_rvol

    dist_pivot_pct = ((curr_close - active_piv_price) / (active_piv_price + 1e-9)) * 100.0

    # Trailing Stop actual
    if not np.isnan(trailing_stop_series[-1]):
        curr_trailing_stop = float(trailing_stop_series[-1])
    else:
        recent_peak = float(np.max(highs[-min(20, n):]))
        curr_trailing_stop = recent_peak * (1.0 - trail_pct / 100.0)
    dist_trailing_stop_pct = ((curr_close - curr_trailing_stop) / (curr_trailing_stop + 1e-9)) * 100.0

    last_entry_info = entry_signals[-1] if entry_signals else None
    gain_since_entry_pct = ((curr_close - last_entry_info[2]) / (last_entry_info[2] + 1e-9)) * 100.0 if last_entry_info else 0.0
    days_since_entry = (n - 1 - last_entry_info[0]) if last_entry_info else 999

    # Condiciones cuantitativas actuales
    cond_momentum = (roc_val >= min_roc)
    cond_trend_slope = (ema_slope_pct >= min_slope) and (curr_close > curr_ema)
    cond_rvol = (curr_rvol >= min_rvol) or (fresh_cross and breakout_bar_rvol >= min_rvol)

    # Un Breakout verdadero exige que la ruptura haya ocurrido en la ventana reciente (`fresh_cross`) Y el precio se mantenga sobre el pivote
    cond_true_breakout = fresh_cross and (curr_close >= active_piv_price * 0.995) and cond_momentum and cond_trend_slope and cond_rvol
    # Un Pre-Breakout exige un pivote intacto justo arriba (entre -3.5% y 0%) con ROC >= 30% y EMA Slope >= 20%
    cond_near_pivot = (len(unbroken_now) > 0) and (-3.5 <= dist_pivot_pct <= 0.5) and cond_momentum and cond_trend_slope
    # En Trade Activo (rompió hace pocos días y sigue sobre el pivote y sobre el 20% Trailing Stop)
    cond_active_trade = in_trade and (days_since_entry <= 15) and (curr_close > active_piv_price) and cond_momentum and cond_trend_slope

    if cond_true_breakout:
        candle_state = f"🔥 BREAKOUT ({days_since_entry}d • RVOL {breakout_bar_rvol:.2f}x)"
        candle_hex = "#00FF87"
    elif cond_near_pivot:
        candle_state = f"🎯 PRE-BREAKOUT (A {dist_pivot_pct:+.1f}% del Pivote)"
        candle_hex = "#00F0FF"
    elif cond_momentum and cond_trend_slope:
        candle_state = "💎 Momentum Activo (ROC≥30% & Slope≥20%)"
        candle_hex = "#38BDF8"
    elif (roc_val >= min_roc * 0.65 or ema_slope_pct >= min_slope * 0.65) and curr_close > curr_ema:
        candle_state = "🟡 Momentum en Construcción"
        candle_hex = "#FFD600"
    elif curr_close > curr_ema:
        candle_state = "🟣 Consolidación > EMA 100"
        candle_hex = "#B388FF"
    else:
        candle_state = "🔴 Bajo EMA 100 / Sin Tendencia"
        candle_hex = "#FF2E63"

    matched = cond_true_breakout
    if include_near and cond_near_pivot:
        matched = True
    if include_active and cond_active_trade:
        matched = True

    if cond_true_breakout:
        when_lbl = "HOY" if days_since_entry == 0 else f"Hace {days_since_entry}d"
        setup_status = f"🚀 BREAKOUT {when_lbl} (Pivote ${active_piv_price:.2f})"
    elif cond_near_pivot:
        setup_status = f"🎯 ACECHANDO PIVOTE (${active_piv_price:.2f}, {dist_pivot_pct:+.1f}%)"
    elif cond_active_trade:
        setup_status = f"📈 EN TRADE ({days_since_entry}d desde Entry, Stop ${curr_trailing_stop:.2f})"
    else:
        setup_status = f"Pivote ${active_piv_price:.2f} ({dist_pivot_pct:+.1f}%)"

    return {
        "valid": True,
        "matched": bool(matched),
        "strict_breakout": bool(cond_true_breakout),
        "fresh_cross": bool(fresh_cross),
        "in_trade": bool(in_trade),
        "days_since_entry": int(days_since_entry),
        "pivot_price": round(active_piv_price, 2),
        "pivot_idx": int(confirmed_pivots[-1][0]),
        "pivot_date": active_piv_date,
        "highest_pivot_price": round(max(confirmed_pivots, key=lambda x: x[1])[1], 2),
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
        "cond_breakout": bool(cond_true_breakout),
    }

def fetch_data_alpaca_daily(tickers: list[str], api_key: str, secret_key: str) -> dict[str, pd.DataFrame]:
    """Descarga barras diarias históricas usando Alpaca (IEX Feed) con chunking robusto y normalización de símbolos."""
    if not tickers or not api_key or not secret_key:
        return {}
    client = StockHistoricalDataClient(api_key.strip(), secret_key.strip())
    start_date = datetime.now() - timedelta(days=380)
    
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
        except Exception:
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
                      pivot_params: dict = None, force_refresh: bool = False) -> pd.DataFrame:
    """
    Ejecuta el scanner de Swing Trading 100% en tiempo real sobre el mercado completo
    sin listas estáticas forzadas (cero hardcoding de benchmarks).
    Incluye caché de 5 minutos en memoria para que cambiar entre los 29 filtros sobre ~1,850 activos sea instantáneo.
    """
    import time as _time
    if not tickers:
        tickers = FULL_US_MARKET_TICKERS
        
    live_meta = {}
    if (isinstance(tickers, str) and tickers == "FULL_MARKET") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "FULL_MARKET"):
        tickers = FULL_US_MARKET_TICKERS
    elif (isinstance(tickers, str) and tickers == "LIVE_MOVERS") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "LIVE_MOVERS"):
        movers, live_meta = eu.fetch_live_market_movers()
        tickers = sorted(list(set(movers + HIGH_MOMENTUM_EXPANDED_TICKERS)))
    elif (isinstance(tickers, str) and tickers == "AUTONOMOUS_LEADERS") or (isinstance(tickers, list) and len(tickers) == 1 and tickers[0] == "AUTONOMOUS_LEADERS"):
        tickers = get_autonomous_market_leaders(top_n=260)
        if not tickers:
            tickers = FULL_US_MARKET_TICKERS

    # Normalizar tickers (ej. BF.B -> BF-B) y eliminar duplicados manteniendo orden
    seen_t = set()
    clean_tickers = []
    for raw_t in tickers:
        if raw_t and str(raw_t).strip():
            ct = str(raw_t).strip().upper().replace('.', '-')
            if ct not in seen_t:
                seen_t.add(ct)
                clean_tickers.append(ct)
    tickers = clean_tickers

    now_ts = _time.time()
    cache_age = now_ts - _DAILY_BARS_CACHE.get("timestamp", 0.0)
    cached_store = _DAILY_BARS_CACHE.get("data", {}) if (not force_refresh and cache_age < 300.0 and _DAILY_BARS_CACHE.get("provider") == provider) else {}

    ticker_dfs = {}
    missing_tickers = []
    for t in tickers:
        if t in cached_store:
            ticker_dfs[t] = cached_store[t]
        else:
            missing_tickers.append(t)

    if missing_tickers:
        fetched_dfs = {}
        if provider == "Alpaca" and alpaca_key and alpaca_secret:
            try:
                fetched_dfs = fetch_data_alpaca_daily(missing_tickers, alpaca_key, alpaca_secret)
            except Exception as e:
                print(f"Fallo Alpaca, recurriendo a yfinance: {e}")
                fetched_dfs = {}

        if not fetched_dfs:
            try:
                chunk_size = 250
                for i in range(0, len(missing_tickers), chunk_size):
                    chunk = missing_tickers[i:i + chunk_size]
                    data = yf.download(chunk, period="1y", interval="1d", group_by="ticker", threads=True, progress=False)
                    if data is None or data.empty:
                        continue
                    for t in chunk:
                        try:
                            if isinstance(data.columns, pd.MultiIndex) and t in data.columns.levels[0]:
                                df = data[t].dropna(how="all")
                            elif isinstance(data.columns, pd.MultiIndex):
                                if len(chunk) == 1:
                                    df = data.dropna(how="all").copy()
                                    df.columns = df.columns.get_level_values(0)
                                else:
                                    continue
                            else:
                                df = data.dropna(how="all")
                            if not df.empty and 'Close' in df.columns:
                                df = df.dropna(subset=['Close'])
                                df = df[df['Close'] > 0]
                                if not df.empty:
                                    fetched_dfs[t] = df
                        except Exception:
                            continue
            except Exception as e:
                print(f"Error descargando datos diarios: {e}")

        if fetched_dfs:
            ticker_dfs.update(fetched_dfs)
            if cache_age >= 300.0 or _DAILY_BARS_CACHE.get("provider") != provider or force_refresh:
                _DAILY_BARS_CACHE["timestamp"] = now_ts
                _DAILY_BARS_CACHE["provider"] = provider
                _DAILY_BARS_CACHE["data"] = dict(ticker_dfs)
            else:
                _DAILY_BARS_CACHE["data"].update(fetched_dfs)

    if not ticker_dfs:
        return pd.DataFrame()

    results = []
    
    for t, df in ticker_dfs.items():
        try:
            is_ipo_strat = ("IPO" in strategy or "HVE" in strategy or "Highest Volume" in strategy)
            is_intraday_mover = ("Pre Market" in strategy or "Post Market" in strategy or "Gap" in strategy)
            min_bars = 5 if is_ipo_strat else (5 if is_intraday_mover else (15 if ("Episodic" in strategy or "EP" in strategy or "Ants" in strategy or "Up on Volume" in strategy) else (105 if ("Pivot Breakout" in strategy or "Daily Pivot" in strategy) else 50)))
            if df.empty or len(df) < min_bars:
                continue
                
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
            change_pct = ((current_price - prev_close) / prev_close) * 100.0
            if np.isnan(change_pct):
                change_pct = 0.0
            
            # Promedios de volumen de 5, 20 y 50 días (excluyendo la barra actual para referencia limpia)
            vol_avg_20 = float(volume.tail(21).iloc[:-1].mean()) if len(df) >= 21 else float(volume.mean())
            vol_avg_50 = float(volume.tail(51).iloc[:-1].mean()) if len(df) >= 51 else vol_avg_20
            vol_5d = float(volume.tail(5).mean()) if len(df) >= 5 else float(volume.iloc[-1])
            vol_dryup = vol_5d / (vol_avg_50 + 1e-9)
            
            # Volumen físico y en Dólares ($ Volume)
            last_vol = float(volume.iloc[-1])
            dollar_vol = last_vol * current_price
            dollar_vol_m = dollar_vol / 1_000_000.0
            dollar_vol_avg_20 = float(((volume.tail(20) * close.tail(20)).mean()) / 1_000_000.0) if len(df) >= 20 else dollar_vol_m
            
            # ADR 10 días (%) y RMV 15 días (%)
            adr_10 = calculate_adr(df, 10)
            if len(df) >= 15:
                high_15 = float(df['High'].tail(15).max())
                low_15 = float(df['Low'].tail(15).min())
                rmv_15 = ((high_15 - low_15) / (low_15 + 1e-9)) * 100.0
            else:
                rmv_15 = 15.0
            
            # Rate of Change (1W, 1M, 3M, 6M)
            roc_1w = float(((current_price - close.iloc[-6]) / close.iloc[-6]) * 100.0) if len(df) >= 6 else change_pct
            roc_1m = float(((current_price - close.iloc[-21]) / close.iloc[-21]) * 100.0) if len(df) >= 22 else change_pct
            roc_3m = float(((current_price - close.iloc[-63]) / close.iloc[-63]) * 100.0) if len(df) >= 64 else roc_1m
            roc_6m = float(((current_price - close.iloc[-126]) / close.iloc[-126]) * 100.0) if len(df) >= 127 else roc_3m
            
            # Filtro base de liquidez mínima operable
            effective_min_vol = 25_000 if ("Episodic" in strategy or "EP" in strategy or is_ipo_strat) else (50_000 if ("Up on Volume" in strategy or "Ants" in strategy or "Pure Momentum" in strategy or "Pivot Breakout" in strategy or "Daily Pivot" in strategy) else min_volume)
            effective_min_price = 2.0 if ("Episodic" in strategy or "EP" in strategy or is_ipo_strat or "HTF" in strategy or "High Tight" in strategy) else (3.0 if ("Up on Volume" in strategy or "Ants" in strategy or "Pure Momentum" in strategy or "Pre Market" in strategy or "RS Days" in strategy) else min_price)
            if current_price < effective_min_price or (vol_avg_20 < effective_min_vol and last_vol < effective_min_vol):
                continue
                
            # Medias móviles e indicadores técnicos
            sma_20 = float(close.rolling(20).mean().iloc[-1]) if len(df) >= 20 else current_price
            sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(df) >= 50 else sma_20
            sma_150 = float(close.rolling(150).mean().iloc[-1]) if len(df) >= 150 else sma_50
            sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(df) >= 200 else float(close.rolling(len(df)).mean().iloc[-1])
            ema_21 = float(close.ewm(span=21, adjust=False).mean().iloc[-1]) if len(df) >= 21 else sma_20
            dist_ema21_pct = ((current_price - ema_21) / (ema_21 + 1e-9)) * 100.0
            
            rsi_series = calculate_rsi(close, 14)
            rsi = float(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50.0
            
            atr_series = calculate_atr(df, 14)
            atr = float(atr_series.iloc[-1]) if not np.isnan(atr_series.iloc[-1]) else 0.0
            
            rvol_20 = last_vol / (vol_avg_20 + 1e-9)
            rvol_50 = last_vol / (vol_avg_50 + 1e-9)
            rvol = rvol_20
            
            high_52w = float(df['High'].tail(252).max())
            low_52w = float(df['Low'].tail(252).min())
            dist_high_52w = ((current_price - high_52w) / (high_52w + 1e-9)) * 100.0
            dist_low_52w = ((current_price - low_52w) / (low_52w + 1e-9)) * 100.0
            
            day_high = float(df['High'].iloc[-1])
            day_low = float(df['Low'].iloc[-1])
            range_spread = day_high - day_low
            pos_in_range = ((current_price - day_low) / (range_spread + 1e-9)) * 100.0
            
            matched = False
            pattern_name = ""
            
            # =========================================================================
            # EVALUACIÓN CUANTITATIVA 100% EN TIEMPO REAL (CERO LISTAS HARDCODEADAS)
            # =========================================================================
            if "Pivot Breakout" in strategy or "Daily Pivot" in strategy:
                # Daily Pivot Breakout Strategy Indicator (by Mike):
                # Left=5, Right=5, Lookback=100, ROC(100)>=30%, RVOL(20)>1.0x, EMA(100) Slope(100)>=20%
                piv_eval = evaluate_daily_pivot_breakout(df, params=pivot_params)
                if piv_eval.get("valid") and piv_eval.get("matched") and (dollar_vol_avg_20 >= 3.0 or dollar_vol_m >= 3.0):
                    matched = True
                    rvol = piv_eval["rvol_val"]
                    pattern_name = f"{piv_eval['setup_status']} • ROC {piv_eval['roc_val']:+.1f}% • Slope {piv_eval['ema_slope_pct']:+.1f}%"

            elif strategy == "Trend Template (Etapa 2)":
                cond_trend = (current_price > sma_50) and (sma_50 > sma_150) and (sma_150 > sma_200)
                cond_high = dist_high_52w >= -abs(max_dist_52w)
                cond_low = dist_low_52w >= 25.0
                cond_rsi = 50.0 <= rsi <= 80.0
                if cond_trend and cond_high and cond_low and cond_rsi and dollar_vol_avg_20 >= 5.0:
                    matched = True
                    pattern_name = f"Minervini Etapa 2 ({dist_high_52w:+.1f}% de 52w High)"
                    
            elif "Highest Volume" in strategy or "HVE" in strategy:
                # Highest Volume IPO / Since IPO Day (Récord de volumen real en las últimas 1-3 sesiones):
                if len(df) > 5:
                    v_hist_max = float(df['Volume'].iloc[1:-1].max())
                else:
                    v_hist_max = 0.0
                is_hve_today = (v_hist_max > 0) and (last_vol >= v_hist_max) and (change_pct > 0.0) and (pos_in_range >= 40.0)
                # También detectar si el récord ocurrió en las últimas 2 sesiones manteniendo el cierre sobre el mínimo
                is_hve_recent = False
                hve_ratio = last_vol / (v_hist_max + 1e-9) if v_hist_max > 0 else 0.0
                if not is_hve_today and len(df) > 6:
                    for back_i in (2, 3):
                        v_b = float(df['Volume'].iloc[-back_i])
                        v_prior_max = float(df['Volume'].iloc[1:-back_i].max())
                        c_b = float(df['Close'].iloc[-back_i])
                        c_prev_b = float(df['Close'].iloc[-back_i - 1])
                        l_b = float(df['Low'].iloc[-back_i])
                        h_b = float(df['High'].iloc[-back_i])
                        dcr_b = ((c_b - l_b) / (h_b - l_b + 1e-9)) * 100.0
                        if v_prior_max > 0 and v_b >= v_prior_max and c_b > c_prev_b and dcr_b >= 45.0 and current_price >= l_b:
                            is_hve_recent = True
                            hve_ratio = v_b / (v_prior_max + 1e-9)
                            break
                if (is_hve_today or is_hve_recent) and (dollar_vol_avg_20 >= 3.0 or dollar_vol_m >= 5.0):
                    matched = True
                    tag_when = "HOY" if is_hve_today else "Reciente 2d"
                    pattern_name = f"Highest Vol Record {tag_when} ({hve_ratio:.2f}x máx, DCR {pos_in_range:.0f}%)"

            elif "VCP" in strategy or "Volatility Contraction" in strategy:
                # Mark Minervini VCP (Volatility Contraction Pattern en Etapa 2 con contracción real de rango y secado de volumen):
                cond_liquid = (dollar_vol_avg_20 >= 8.0)
                cond_stage2 = (current_price > sma_50 > sma_200) and (current_price >= sma_20 * 0.97) and (dist_high_52w >= -18.0) and (dist_low_52w >= 25.0)
                # Contracción progresiva de volatilidad: rango de 5 días menor que rango de 20 días y RMV_15 comprimido
                if len(df) >= 20:
                    rng_5d = ((float(df['High'].tail(5).max()) - float(df['Low'].tail(5).min())) / (float(df['Low'].tail(5).min()) + 1e-9)) * 100.0
                    rng_20d = ((float(df['High'].tail(20).max()) - float(df['Low'].tail(20).min())) / (float(df['Low'].tail(20).min()) + 1e-9)) * 100.0
                    is_contracting = (rng_5d <= 8.5) and (rmv_15 <= 14.0) and (rng_5d < rng_20d * 0.75)
                else:
                    is_contracting = False
                cond_vol_dry = (vol_dryup <= 0.90) or (rvol_20 <= 0.85)
                if cond_liquid and cond_stage2 and is_contracting and cond_vol_dry:
                    matched = True
                    pattern_name = f"Minervini VCP (RMV {rmv_15:.1f}%, Vol 5d/50d {vol_dryup:.2f}x)"

            elif "Deepvue Universe" in strategy:
                cond_liquid = (dollar_vol_avg_20 >= 20.0)
                cond_price = (current_price >= 10.0)
                cond_trend = (current_price > sma_50) and (current_price > sma_200)
                cond_rs = (dist_high_52w >= -25.0) and (roc_1m > 0.0) and (roc_3m >= 5.0)
                if cond_liquid and cond_price and cond_trend and cond_rs:
                    matched = True
                    pattern_name = f"Deepvue Institutional ($Vol ${dollar_vol_avg_20:.0f}M, 3M {roc_3m:+.1f}%)"

            elif "Liquid Leaders" in strategy:
                cond_liquid = (dollar_vol_avg_20 >= 25.0)
                cond_trend = (current_price > sma_20) and (sma_20 > sma_50) and (sma_50 > sma_200)
                cond_rs = (dist_high_52w >= -18.0) and (roc_3m >= 12.0) and (roc_1m >= 2.0) and (adr_10 >= 2.2)
                if cond_liquid and cond_trend and cond_rs:
                    matched = True
                    pattern_name = f"Liquid Leader ($Vol ${dollar_vol_avg_20:.0f}M, 3M {roc_3m:+.1f}%, ADR {adr_10:.1f}%)"

            elif "Sustained Momentum" in strategy or "Momentum Leaders" in strategy:
                cond_liquid = (dollar_vol_avg_20 >= 10.0)
                cond_trend = (current_price > sma_50 > sma_200) and (current_price >= ema_21 * 0.97)
                cond_mom = (roc_3m >= 18.0) and (roc_6m >= 25.0) and (roc_1m >= 0.0) and (dist_high_52w >= -18.0)
                if cond_liquid and cond_trend and cond_mom:
                    matched = True
                    pattern_name = f"Sustained Momentum (3M {roc_3m:+.1f}%, 6M {roc_6m:+.1f}%)"

            elif "Stage 2" in strategy or "Weinstein" in strategy or "Stage Analysis" in strategy:
                sma50_prev20 = float(close.rolling(50).mean().iloc[-20]) if len(df) >= 70 else sma_50 * 0.98
                sma200_prev20 = float(close.rolling(200).mean().iloc[-20]) if len(df) >= 220 else sma_200 * 0.99
                cond_liquid = (dollar_vol_avg_20 >= 12.0)
                cond_stage2 = (current_price > sma_50 > sma_200) and (sma_50 > sma50_prev20) and (sma_200 >= sma200_prev20)
                cond_rs = (dist_high_52w >= -18.0) and (roc_3m >= 10.0) and (current_price >= ema_21 * 0.97)
                if cond_liquid and cond_stage2 and cond_rs:
                    matched = True
                    stage_label = "Etapa 2A (Early Markup)" if (dist_high_52w >= -10.0 and rvol_20 >= 1.1) else "Etapa 2 (Advancing)"
                    pattern_name = f"Weinstein {stage_label} (3M {roc_3m:+.1f}%)"

            elif "CANSLIM" in strategy or "High RS" in strategy:
                is_high_rs_variant = ("High RS" in strategy)
                min_3m_req = 20.0 if is_high_rs_variant else 15.0
                cond_price = (current_price >= 12.0)
                cond_liquid = (dollar_vol_avg_20 >= 12.0)
                cond_trend = (current_price > sma_50 > sma_200) and (current_price >= sma_20 * 0.98)
                cond_rs = (dist_high_52w >= -15.0) and (roc_3m >= min_3m_req) and (roc_6m >= 20.0) and (52.0 <= rsi <= 82.0)
                if cond_price and cond_liquid and cond_trend and cond_rs:
                    matched = True
                    pattern_name = f"CANSLIM Leader ({dist_high_52w:+.1f}% 52w, 3M {roc_3m:+.1f}%)"

            elif "Leaders" in strategy or "TML" in strategy:
                cond_trend = (current_price > sma_20 > sma_50 > sma_200)
                cond_high = (dist_high_52w >= -12.0)
                cond_mom = (roc_3m >= 15.0) and (dollar_vol_avg_20 >= 15.0) and (55.0 <= rsi <= 80.0)
                if cond_trend and cond_high and cond_mom:
                    matched = True
                    pattern_name = f"True Market Leader ({dist_high_52w:+.1f}% 52w, 3M {roc_3m:+.1f}%)"
                    
            elif "Episodic" in strategy or "EP" in strategy:
                # Qullamaggie Episodic Pivot (EP) real en las últimas 5 sesiones:
                # Gap >= +5% o Ganancia Diaria >= +8% con RVOL >= 2.0x y $Vol >= $8M, sosteniendo el mínimo de la vela EP
                recent_6 = df.tail(6)
                ep_found = False
                ep_date_str = ""
                ep_gain_val = 0.0
                ep_rvol_val = 0.0
                
                for idx in range(1, len(recent_6)):
                    bar = recent_6.iloc[idx]
                    prev_bar = recent_6.iloc[idx - 1]
                    b_gain = ((bar['Close'] - prev_bar['Close']) / (prev_bar['Close'] + 1e-9)) * 100.0
                    b_gap = ((bar['Open'] - prev_bar['Close']) / (prev_bar['Close'] + 1e-9)) * 100.0
                    b_vol = float(bar['Volume'])
                    b_rvol = b_vol / (vol_avg_20 + 1e-9)
                    b_dvol_m = (b_vol * float(bar['Close'])) / 1_000_000.0
                    candle_spread = float(bar['High'] - bar['Low'])
                    b_cr = ((float(bar['Close'] - bar['Low'])) / (candle_spread if candle_spread > 0 else 1.0)) * 100.0
                    
                    if (b_gain >= 8.0 or b_gap >= 5.0) and (b_rvol >= 2.0) and (b_dvol_m >= 5.0) and (b_cr >= 50.0) and (current_price >= float(bar['Low']) * 0.99):
                        ep_found = True
                        ep_date_str = str(bar.name)[:10]
                        ep_gain_val = b_gain
                        ep_rvol_val = b_rvol

                if ep_found:
                    matched = True
                    pattern_name = f"Episodic Pivot {ep_date_str} (+{ep_gain_val:.1f}%, RVOL {ep_rvol_val:.1f}x)"

            elif "Pocket Pivot" in strategy:
                # Pocket Pivot real (Gil Morales & Chris Kacher) HOY:
                # Día alcista (Close > Close ayer, DCR >= 50%) cuyo volumen supera el máximo volumen bajista de las 10 sesiones previas
                is_up_day = (change_pct >= 0.5) and (current_price > open_price if 'open_price' in locals() else True) and (pos_in_range >= 50.0)
                recent_10 = df.iloc[-11:-1] if len(df) >= 11 else df.iloc[:-1]
                if len(recent_10) >= 5:
                    down_mask = (recent_10['Close'] < recent_10['Close'].shift(1)) | (recent_10['Close'] < recent_10['Open'])
                    down_vols = recent_10.loc[down_mask, 'Volume']
                    max_down_vol = float(down_vols.max()) if not down_vols.empty and not np.isnan(down_vols.max()) else 0.0
                else:
                    max_down_vol = 0.0

                is_pocket_vol = (max_down_vol > 0.0) and (last_vol > max_down_vol) and (rvol_20 >= 1.05)
                dist_sma50_pct = ((current_price - sma_50) / (sma_50 + 1e-9)) * 100.0
                # Debe ocurrir dentro o saliendo de la base (cerca de EMA 21 / SMA 50, no sobre-extendida)
                cond_base = (current_price >= sma_50 * 0.98) and (sma_50 >= sma_200 * 0.98) and (-2.0 <= dist_sma50_pct <= 12.0) and (dist_high_52w >= -22.0)
                cond_liquid = (dollar_vol_avg_20 >= 5.0)

                if is_up_day and is_pocket_vol and cond_base and cond_liquid:
                    matched = True
                    pocket_ratio = last_vol / (max_down_vol + 1e-9)
                    pattern_name = f"Pocket Pivot Hoy ({pocket_ratio:.2f}x vs Máx Vol Bajista 10d)"

            elif "IPO Last 1 Year" in strategy or "Ameet Rai: IPO" in strategy:
                # Empresas con <= 250 barras (~1 año desde debut en bolsa) en tendencia alcista sobre EMA 21 / SMA 20
                is_recent_ipo = (10 <= len(df) <= 245)
                is_supported = (current_price > ema_21) and (current_price > sma_20) and (dist_high_52w >= -22.0)
                cond_liquid = (dollar_vol_avg_20 >= 2.0) and (current_price >= 5.0)
                if is_recent_ipo and is_supported and cond_liquid:
                    matched = True
                    pattern_name = f"IPO Reciente ({len(df)} sesiones, {dist_high_52w:+.1f}% de Máx)"

            elif "HV Edge" in strategy or "Ameet Rai: HV Edge" in strategy:
                # HV Edge en la sesión actual (o ayer): Mayor volumen en 1 año o en 63 sesiones (post-earnings) con cierre alcista
                is_hv_edge = False
                hv_type = ""
                hv_ratio = 1.0
                if len(df) >= 65:
                    v_1y_max = float(df['Volume'].tail(252).iloc[:-1].max())
                    v_earn_max = float(df['Volume'].tail(63).iloc[:-1].max())
                    if last_vol >= v_1y_max and v_1y_max > 0 and change_pct > 0.0 and pos_in_range >= 45.0:
                        is_hv_edge = True
                        hv_type = "Récord Vol 1 Año"
                        hv_ratio = last_vol / (v_1y_max + 1e-9)
                    elif last_vol >= v_earn_max and v_earn_max > 0 and change_pct >= 1.5 and pos_in_range >= 50.0 and rvol_20 >= 2.0:
                        is_hv_edge = True
                        hv_type = "Récord Vol 63d (Trimestral)"
                        hv_ratio = last_vol / (v_earn_max + 1e-9)
                if is_hv_edge and dollar_vol_avg_20 >= 5.0 and current_price >= 5.0:
                    matched = True
                    pattern_name = f"HV Edge ({hv_type}, {hv_ratio:.2f}x, RVOL {rvol_20:.1f}x)"

            elif "High Tight Flag" in strategy or "HTF" in strategy:
                # High Tight Flag (HTF): Subida >= +80% en las últimas 40 sesiones y consolidación alta con retroceso <= 20%
                if len(df) >= 40:
                    recent_40 = df.tail(40)
                    min_idx = recent_40['Low'].idxmin()
                    after_min = recent_40.loc[min_idx:]
                    min_40 = float(recent_40['Low'].min())
                    max_after = float(after_min['High'].max())
                    run_pct = ((max_after - min_40) / (min_40 + 1e-9)) * 100.0
                    flag_depth = ((current_price - max_after) / (max_after + 1e-9)) * 100.0
                else:
                    run_pct = 0.0
                    flag_depth = -50.0
                cond_htf = (run_pct >= 80.0) and (-20.0 <= flag_depth <= 0.0) and (current_price > ema_21 * 0.96) and (dollar_vol_avg_20 >= 3.0) and (current_price >= 4.0)
                if cond_htf:
                    matched = True
                    pattern_name = f"High Tight Flag (Mástil +{run_pct:.0f}%, Flag {flag_depth:+.1f}%)"

            elif "Daily Liquidity" in strategy:
                cond_vol_8m = (last_vol >= 8_000_000) and (dollar_vol_m >= 50.0) and (current_price >= 5.0) and (change_pct > 0.0) and (current_price > sma_50)
                if cond_vol_8m:
                    matched = True
                    pattern_name = f"Daily Liquidity ({last_vol/1_000_000:.1f}M acciones, ${dollar_vol_m:.0f}M $Vol)"

            elif "RS Days" in strategy or "Ameet Rai" in strategy:
                # Al menos 62.5% de sesiones positivas en las últimas 20 sesiones (>= 13 de 20 días en verde) en Etapa 2
                if len(df) >= 22:
                    ret_20 = df['Close'].pct_change().tail(20)
                    up_days_20 = int((ret_20 > 0.0).sum())
                    rs_ratio_20 = up_days_20 / 20.0
                else:
                    up_days_20 = 0
                    rs_ratio_20 = 0.0
                cond_rs_days = (rs_ratio_20 >= 0.65) and (current_price > sma_50 > sma_200) and (dist_high_52w >= -18.0) and (roc_1m >= 5.0) and (dollar_vol_avg_20 >= 8.0)
                if cond_rs_days:
                    matched = True
                    pattern_name = f"RS Days ({up_days_20}/20 días alcistas = {rs_ratio_20*100:.0f}%)"

            elif "Weekly Strength" in strategy:
                if len(df) >= 6:
                    w_high = float(df['High'].tail(5).max())
                    w_low = float(df['Low'].tail(5).min())
                    pos_week = ((current_price - w_low) / (w_high - w_low + 1e-9)) * 100.0
                else:
                    pos_week = 0.0
                cond_wk = (pos_week >= 75.0) and (roc_1w >= 2.0) and (current_price > ema_21 > sma_50 > sma_200) and (dist_high_52w >= -15.0) and (dollar_vol_avg_20 >= 10.0)
                if cond_wk:
                    matched = True
                    pattern_name = f"Weekly Strength (Rango 5d {pos_week:.0f}%, Semanal {roc_1w:+.1f}%)"

            elif "Power 21" in strategy:
                # Pullback ordenado a la 21 EMA en líderes con fuerte avance previo (ROC 3M >= 15%)
                low_today = float(df['Low'].iloc[-1])
                touched_ema21 = (low_today <= ema_21 * 1.02) and (current_price >= ema_21 * 0.99) and (abs(dist_ema21_pct) <= 2.5)
                cond_leader = (current_price > sma_50 > sma_200) and (roc_3m >= 15.0) and (dist_high_52w >= -18.0) and (dollar_vol_avg_20 >= 10.0)
                if touched_ema21 and cond_leader:
                    matched = True
                    pattern_name = f"Power 21 Pullback (Dist EMA21 {dist_ema21_pct:+.1f}%, 3M {roc_3m:+.1f}%)"

            elif "Volume Dry Up" in strategy:
                # Secado estricto de volumen sobre SMA 50 (RVOL <= 0.65x y RMV_15 <= 12%)
                cond_vdu = (current_price > sma_50 > sma_200) and (rvol_20 <= 0.65) and (vol_dryup <= 0.85) and (rmv_15 <= 12.0) and (dist_high_52w >= -20.0) and (dollar_vol_avg_20 >= 6.0)
                if cond_vdu:
                    matched = True
                    pattern_name = f"Volume Dry Up (RVOL {rvol_20:.2f}x, RMV {rmv_15:.1f}%)"

            elif "Tight Range" in strategy:
                is_inside_day = False
                is_double_inside = False
                if len(df) >= 4:
                    h1, l1 = float(df['High'].iloc[-1]), float(df['Low'].iloc[-1])
                    h2, l2 = float(df['High'].iloc[-2]), float(df['Low'].iloc[-2])
                    h3, l3 = float(df['High'].iloc[-3]), float(df['Low'].iloc[-3])
                    is_inside_day = (h1 <= h2 and l1 >= l2)
                    is_double_inside = is_inside_day and (h2 <= h3 and l2 >= l3)
                cond_tight = (rmv_15 <= 9.5) and (abs(roc_1w) <= 3.0 or is_inside_day) and (current_price > sma_50 > sma_200) and (dist_high_52w >= -18.0) and (dollar_vol_avg_20 >= 6.0)
                if cond_tight:
                    matched = True
                    tag_in = "Double Inside Day" if is_double_inside else ("Inside Day" if is_inside_day else f"5d {roc_1w:+.1f}%")
                    pattern_name = f"Tight Range (RMV {rmv_15:.1f}%, {tag_in})"

            elif "Up on Volume" in strategy:
                cond_uov = (change_pct >= 2.5) and (pos_in_range >= 65.0) and (rvol_20 >= 1.5) and (current_price > sma_50) and (dollar_vol_avg_20 >= 5.0)
                if cond_uov:
                    matched = True
                    pattern_name = f"Up on Volume (+{change_pct:.1f}%, RVOL {rvol_20:.2f}x, DCR {pos_in_range:.0f}%)"

            elif "Ants" in strategy:
                # David Ryan's ANTS oficial: >= 11 días alcistas de las últimas 15 sesiones, avance >= +12% en 15d y expansión de volumen
                if len(df) >= 16:
                    ret_15 = df['Close'].pct_change().tail(15)
                    up_15 = int((ret_15 > 0.0).sum())
                    gain_15 = float(((current_price - float(df['Close'].iloc[-16])) / float(df['Close'].iloc[-16])) * 100.0)
                else:
                    up_15 = 0
                    gain_15 = 0.0
                cond_ants = (up_15 >= 11) and (gain_15 >= 12.0) and (vol_5d >= vol_avg_20) and (current_price > sma_50) and (dist_high_52w >= -20.0) and (dollar_vol_avg_20 >= 4.0)
                if cond_ants:
                    matched = True
                    pattern_name = f"David Ryan ANTS ({up_15}/15 días verdes, +{gain_15:.1f}% en 15d)"

            elif strategy == "Pullback a SMA 20/50":
                cond_uptrend = (current_price > sma_200) and (sma_50 > sma_200) and (roc_3m >= 8.0)
                near_sma20 = abs((current_price - sma_20) / (sma_20 + 1e-9)) <= 0.015 and (current_price >= sma_20 * 0.99)
                near_sma50 = abs((current_price - sma_50) / (sma_50 + 1e-9)) <= 0.02 and (current_price >= sma_50 * 0.99)
                cond_rsi = 42.0 <= rsi <= 62.0
                if cond_uptrend and (near_sma20 or near_sma50) and cond_rsi and dollar_vol_avg_20 >= 5.0:
                    matched = True
                    target = "SMA 20" if near_sma20 else "SMA 50"
                    pattern_name = f"Pullback Institucional a {target} (RSI {rsi:.0f})"
                    
            elif strategy == "Ruptura de Resistencia (Breakout)":
                recent_high_20 = float(df['High'].tail(21).iloc[:-1].max()) if len(df) >= 21 else day_high
                prev_c_20 = float(df['Close'].iloc[-2])
                cond_break = (current_price > recent_high_20) and (prev_c_20 <= recent_high_20 * 1.005)
                cond_rvol = (rvol_20 >= 1.3) and (pos_in_range >= 60.0) and (current_price > sma_50 > sma_200) and (dollar_vol_avg_20 >= 5.0)
                if cond_break and cond_rvol:
                    matched = True
                    pattern_name = f"Breakout 20d (${recent_high_20:.2f}, RVOL {rvol_20:.2f}x)"
                    
            elif "Pure Momentum" in strategy:
                cond_dollar_vol = (dollar_vol_avg_20 >= 7.0)
                cond_adr = (adr_10 >= 3.2)
                cond_momentum = (roc_1m >= 12.0 or roc_3m >= 25.0) and (current_price > ema_21 > sma_50) and (dist_high_52w >= -18.0)
                if cond_dollar_vol and cond_adr and cond_momentum:
                    matched = True
                    pattern_name = f"Pure Momentum (ADR {adr_10:.1f}%, 1M {roc_1m:+.1f}%, 3M {roc_3m:+.1f}%)"

            elif "Pre Market" in strategy or "Gap Ups" in strategy:
                open_price = float(df['Open'].iloc[-1])
                gap_pct = ((open_price - prev_close) / (prev_close + 1e-9)) * 100.0
                cond_price = (current_price >= 5.0)
                cond_gap_or_up = (gap_pct >= 2.0 and change_pct >= 1.5) or (change_pct >= 4.0 and rvol_20 >= 1.3)
                cond_liquid = (dollar_vol_avg_20 >= 5.0) or (dollar_vol_m >= 5.0)
                if cond_price and cond_gap_or_up and cond_liquid:
                    matched = True
                    gap_label = f"Gap {gap_pct:+.1f}%" if abs(gap_pct) >= 1.5 else f"Impulso {change_pct:+.1f}%"
                    pattern_name = f"Gap & Go ({gap_label}, RVOL {rvol_20:.2f}x)"

            elif "Post Market" in strategy or "After Hours" in strategy:
                cond_price = (current_price >= 5.0)
                cond_move = (abs(change_pct) >= 3.0) and (rvol_20 >= 1.2)
                cond_liquid = (dollar_vol_avg_20 >= 10.0) or (dollar_vol_m >= 10.0)
                if cond_price and cond_move and cond_liquid:
                    matched = True
                    move_type = "Reacción Alcista" if change_pct >= 0 else "Reacción Bajista"
                    pattern_name = f"After-Hours / Earnings {move_type} ({change_pct:+.1f}%, RVOL {rvol_20:.2f}x)"
                    
            if matched:
                open_price_val = float(df['Open'].iloc[-1])
                gap_val = ((open_price_val - prev_close) / (prev_close + 1e-9)) * 100.0
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
    if ("Pivot Breakout" in strategy or "Daily Pivot" in strategy) and "ROC (100d) %" in df_res.columns:
        return df_res.sort_values(by=["RVOL", "ROC (100d) %"], ascending=[False, False]).reset_index(drop=True)
    if ("Pre Market" in strategy or "Post Market" in strategy or "Gap" in strategy or "Gapper" in strategy or "Up on Volume" in strategy or "Episodic" in strategy) and "Cambio %" in df_res.columns:
        return df_res.sort_values(by="Cambio %", ascending=False).reset_index(drop=True)
    if "Pure Momentum" in strategy and "ADR (10s) %" in df_res.columns:
        return df_res.sort_values(by="ADR (10s) %", ascending=False).reset_index(drop=True)
    if ("HV Edge" in strategy or "Highest Volume" in strategy or "Pocket Pivot" in strategy) and "RVOL" in df_res.columns:
        return df_res.sort_values(by="RVOL", ascending=False).reset_index(drop=True)
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
                if (current_price >= 3.0 and (gap_pct >= 1.0 or pos_in_range >= 40.0)) :
                    matched = True
                    pattern_name = f"Pre-Mkt Gapper ({gap_pct:+.1f}%)"
            elif "Post Market" in strategy or "After Hours" in strategy:
                if (current_price >= 3.0 and (abs(gap_pct) >= 1.5 or abs(change_pct) >= 1.5)) :
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
