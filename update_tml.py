user_str = '''AEO, AMG, ONC, AAMI, CCC, CVS, ELAN, ANDG, HAS, AS, ITUB, LQDA, PRVA, FIVE, TLN, KD, AUGO, PAYC, PRCH, ILMN, NEO, SBUX, BKH, CACI, CCL, CRL, HALO, NWE, PBR, PSX, TXG, ABBV, SKYD, CTSH, DRH, EXEL, REGN, FTRE, VFC, DINO, HAE, HUM, OLLI, SMG, TX, UTHR, ARXS, XP, ZG, AEM, CGAU, IOVA, MAT, WSM, JBS, SLDE, BLLN, ERO, CHYM, Z, CAI, HPE, BZ, COKE, CMBT, FIGS, GRMN, MANH, TRU, ABNB, AMN, MIAX, CART, MEDP, MPC, SHAK, SIG, ACN, ECO, CBRL, DOCS, NRIX, VCYT, WING, BTSG, PVH, TNK, CDNS, SEZL, LIND, SPCX, BJ, CHH, IAG, ARIS, XPO, OCTV, ALMR, CE, ELF, IMAX, TWST, UNH, WPM, NAVN, ULS, MNDY, MRNA, RVTY, TREX, KRMN, EBAY, GO, HRB, NHC, NTRA, ONON, QDEL, STLD, TRMD, ASO, DHT, ETSY, CAKE, CNK, LPG, PACS, WAT, BBWI, CBOE, CHRD, DKS, LIFE, LLY, BSP, RGEN, RGLD, TNET, GWRE, NUE, PINS, P, URBN, BSY, CAVA, ESI, IQV, MEOH, MGNI, AZTA, GMAB, RELY, DK, MSM, SARO, STOK, APPN, CVI, GCT, KSS, NTAP, CRCL, FRO, PRGO, TEM, VEEV, VSXY, BOX, BRZE, FRSH, VLO, AVTR, CORT, NEM, ATRC, EPAM, SHOP, AYA, QMCO, TTAN, TPB, CDNA, HCI, BIO, CNC, W, PLNT, WAY, NTSK, SDGR, SM, BMNR, KVYO, NSIT, PK, BROS, OMER, GTLB, KNSA, WRBY, VAC, BAX, GME, CHEF, DXC, CRWD, DOCU, SN, ZETA, A, TENB, VVV, TEAM, MNST, HTFL, CVSA, FLYW, S, AR, GRAL, MTDR, CON, DT, PR, SAIL, CRGY, OKTA, SSL, YOU, APA, XNCR, MUR, CVE, TBBB, PEB, BH, NTNX, PBF, QLYS, AVPT, PLTR, SNOW, DDOG, RBRK, CXT, ANAB, NUTX, PD, FROG, RIG, VAL, BH.A, TWLO, AMPL, IOT, RNG, HNGE, KMPR, FIVN, NOG, ESTC, TALO, AGIO, ALKS, ANF, ARQT, CLF, CLMT, DNOW, INSW, RGR, SLGN, BLSH, MDLN'''

tickers = [t.strip().upper().replace('.', '-') for t in user_str.split(',') if t.strip()]
unique_tickers = sorted(list(set(tickers)))

print(f"Total tickers: {len(unique_tickers)}")

# Formatear lista en líneas de 10
lines = []
for i in range(0, len(unique_tickers), 10):
    chunk = unique_tickers[i:i+10]
    lines.append("    " + ", ".join([f'"{t}"' for t in chunk]) + ",")

code = f'''# Lista Oficial True Market Leaders (TML) - Actualizada Semana en Curso ({len(unique_tickers)} acciones)
TML_CURRENT_{len(unique_tickers)}_TICKERS = [
''' + "\n".join(lines) + f'''
]

# Alias compatible con todo el motor TradingVolt
TML_331_TICKERS = TML_CURRENT_{len(unique_tickers)}_TICKERS
TML_OFFICIAL_TICKERS = TML_CURRENT_{len(unique_tickers)}_TICKERS
'''

with open('C:/Users/kim17/.gemini/antigravity/scratch/trading_screener/leaders_universe.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("leaders_universe.py actualizado con éxito.")
