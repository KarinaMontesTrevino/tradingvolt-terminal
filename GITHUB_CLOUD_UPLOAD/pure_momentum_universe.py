"""
TradingVolt • Pure Momentum Official 231-Ticker Universe
Reverse engineered directly from Deepvue Pure Momentum Screener.
Filters for common stocks with 20-day Average Dollar Volume > $7M and 10-day ADR > 3%.
Absolute Strength (AS) > 95 at 1-month or > 93 at 3-months.
"""

PURE_MOMENTUM_231_TICKERS = ['ABCL', 'ACN', 'AGYS', 'AI', 'AMLX', 'AMN', 'AMPL', 'ANDG', 'ANF', 'APA', 'APOG', 'APPN', 'ARCT', 'ARHS', 'ASAN', 'ASO', 'ASST', 'ATRC', 'AUGO', 'AVPT', 'AZTA', 'BBD', 'BBWI', 'BETR', 'BHC', 'BKYI', 'BL', 'BLKB', 'BMBL', 'BRBR', 'BRZE', 'BSP', 'BSY', 'BTE', 'BXC', 'CAI', 'CART', 'CBLL', 'CBOE', 'CBRL', 'CCI', 'CCL', 'CDNA', 'CERT', 'CHPT', 'CHYM', 'CNXC', 'COTY', 'CRAI', 'CRGY', 'CRL', 'CRM', 'CRWD', 'CSGP', 'CSTL', 'CTSH', 'CVI', 'CXM', 'CXT', 'DFDV', 'DHT', 'DINO', 'DNA', 'DOCS', 'DOCU', 'DT', 'DXC', 'ECO', 'EFOR', 'EFX', 'ELF', 'ELMT', 'ENGS', 'EPAM', 'ESRT', 'ESTC', 'ETSY', 'EVER', 'EVH', 'FDS', 'FET', 'FIGS', 'FIVN', 'FIZZ', 'FRO', 'FRSH', 'G', 'GCT', 'GLND', 'GLOB', 'GMAB', 'GO', 'GRAL', 'GTLB', 'GTM', 'GWRE', 'HAFN', 'HALO', 'HAS', 'HCSG', 'HELP', 'HNGE', 'HTFL', 'HUBS', 'HURN', 'IBTA', 'ILMN', 'INN', 'INSP', 'INTA', 'INTR', 'INTU', 'IOVA', 'IT', 'KD', 'KOD', 'KSS', 'KVYO', 'LIFE', 'LIND', 'LW', 'LZ', 'MANE', 'MANH', 'MAX', 'MLAB', 'MNDY', 'MPC', 'MRNA', 'MSTR', 'MTW', 'MYGN', 'NAUT', 'NAVN', 'NIQ', 'NOG', 'NOW', 'NSIT', 'NTRA', 'NTSK', 'NUTX', 'ODD', 'OKTA', 'OMER', 'OSPN', 'OTEX', 'P', 'PAGS', 'PAR', 'PAYS', 'PCOR', 'PD', 'PFAI', 'PICS', 'PLNT', 'PLSE', 'PLTR', 'POOL', 'PRCH', 'PRGO', 'PSIX', 'PSX', 'PUBM', 'PURR', 'QDEL', 'QLYS', 'QMCO', 'QTWO', 'RBRK', 'REAL', 'REPX', 'RGEN', 'RHI', 'RNG', 'RPD', 'RSKD', 'RVTY', 'S', 'SAIL', 'SAM', 'SDGR', 'SEZL', 'SG', 'SHOP', 'SITC', 'SKYD', 'SLDE', 'SLN', 'SM', 'SNAP', 'SPSC', 'SPT', 'STNE', 'SVRN', 'SWKS', 'TBCH', 'TEAM', 'TEM', 'TENB', 'TIC', 'TRAX', 'TRI', 'TRMD', 'TRU', 'TRUP', 'TTAN', 'TWLO', 'TWST', 'TXG', 'U', 'USDE', 'UTHR', 'VEEA', 'VEEV', 'VEON', 'VERX', 'VET', 'VFC', 'VIA', 'VLO', 'VSTM', 'WDAY', 'WING', 'WIX', 'WK', 'XHG', 'XLAB', 'XP', 'XRPN', 'ZETA', 'ZS']

# Backward compatibility alias
PURE_MOMENTUM_205_TICKERS = PURE_MOMENTUM_231_TICKERS
