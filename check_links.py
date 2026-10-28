import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\kim17\.gemini\antigravity\scratch\trading_screener\tradingvolt_weekend_review_latest.html", "r", encoding="utf-8") as f:
    html = f.read()

pos = html.find("function rrgRender")
if pos == -1:
    pos = html.find("function rrgDraw")
if pos == -1:
    pos = html.find("rrgQuad")

print("RRG JS function found at", pos)
print(html[pos:pos+3000])
