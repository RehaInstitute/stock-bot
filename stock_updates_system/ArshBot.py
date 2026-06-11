import requests
import time
from datetime import datetime
import pytz

# ==========================
# CONFIG
# ==========================

BOT_TOKEN = "8959605541:AAEI2TA4khZXlIO1MviuXa5dkjTpjdfGqso"
CHAT_ID = 1162324485
API_URL = "https://api.sharenox.com/api/dashboard/data"

# ==========================
# TIME
# ==========================

def get_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S")

# ==========================
# SAFE API FETCH
# ==========================

def fetch_api():
    for _ in range(3):
        try:
            r = requests.get(API_URL, timeout=20)
            if r.status_code == 200:
                return r.json()
        except:
            time.sleep(2)
    return None

# ==========================
# TELEGRAM
# ==========================

def send_telegram(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except:
        pass

# ==========================
# MARKET ENGINE
# ==========================

def analyze_market(data):

    data = data or {}
    ind = data.get("indian_indices", {}) or {}

    nifty = float(ind.get("nifty", {}).get("percent", 0) or 0)
    bank = float(ind.get("banknifty", {}).get("percent", 0) or 0)
    sensex = float(ind.get("sensex", {}).get("percent", 0) or 0)
    vix = float(ind.get("vix", {}).get("ltp", 0) or 0)

    score = 50
    score += nifty * 2
    score += bank * 2
    score += sensex

    if vix > 18:
        score -= 10
    elif vix < 15:
        score += 5

    score = max(0, min(100, score))

    if score >= 65:
        return score, "🟢 BULLISH", "BUY ON DIP"
    elif score <= 40:
        return score, "🔴 BEARISH", "SELL ON RISE"
    else:
        return score, "🟡 SIDEWAYS", "NO TRADE"

# ==========================
# HEATMAP STYLE
# ==========================

def heatmap(name, pct):

    try:
        pct = float(pct or 0)
    except:
        pct = 0

    if pct >= 1:
        return f"🟢🟢 {name} → {pct}% 🔥 STRONG"
    elif pct >= 0:
        return f"🟢 {name} → {pct}% 📈 POSITIVE"
    elif pct > -1:
        return f"🔴 {name} → {pct}% 📉 WEAK"
    else:
        return f"🔴🔴 {name} → {pct}% 💥 VERY WEAK"

# ==========================
# MESSAGE BUILDER (AI STYLE UI)
# ==========================

def create_message(data):

    data = data or {}
    ind = data.get("indian_indices", {}) or {}
    fii_dii = data.get("fii_dii", {}) or {}
    movers = data.get("movers", {}) or {}

    nifty = ind.get("nifty", {}) or {}
    banknifty = ind.get("banknifty", {}) or {}
    sensex = ind.get("sensex", {}) or {}
    vix = ind.get("vix", {}) or {}

    sectors = ind.get("extra", []) or []

    score, trend, bias = analyze_market(data)

    msg = "╔════════════════════════════╗\n"
    msg +="        ║ 🤖  AI MARKET DASHBOARD     ║\n"
    msg +="        ║   By Reha Trading Institute           ║\n"
    msg +="╚════════════════════════════╝\n\n"

    msg += f"⏰ 𝗧𝗜𝗠𝗘 (IST): {get_ist_time()}\n\n"

    # ================= MARKET =================
    msg += "📊 𝗠𝗔𝗥𝗞𝗘𝗧 𝗦𝗧𝗥𝗨𝗖𝗧𝗨𝗥𝗘\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🧭 Trend   : {trend}\n"
    msg += f"📈 Score   : {score}/100\n"
    msg += f"🎯 Bias    : {bias}\n\n"

    # ================= INDICES =================
    msg += "📈 𝗜𝗡𝗗𝗜𝗖𝗘𝗦\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"Nifty     : {nifty.get('ltp', 0)} ({nifty.get('percent', 0)}%)\n"
    msg += f"BankNifty : {banknifty.get('ltp', 0)} ({banknifty.get('percent', 0)}%)\n"
    msg += f"Sensex    : {sensex.get('ltp', 0)} ({sensex.get('percent', 0)}%)\n"
    msg += f"VIX       : {vix.get('ltp', 0)}\n\n"

    # ================= SECTOR HEATMAP =================
    msg += "🔥 𝗦𝗘𝗖𝗧𝗢𝗥 𝗛𝗘𝗔𝗧𝗠𝗔𝗣\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━\n"

    if sectors:
        for s in sectors:
            msg += heatmap(s.get("name"), s.get("percent")) + "\n"
    else:
        msg += "No sector data\n"

    # ================= FII / DII =================
    fii = fii_dii.get("fii", {}).get("net", 0) or 0
    dii = fii_dii.get("dii", {}).get("net", 0) or 0

    msg += f"\n💰 𝗙𝗜𝗜: ₹{fii} Cr | 🏦 𝗗𝗜𝗜: ₹{dii} Cr\n"

    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━\n"

    # ================= TOP GAINERS =================
    msg += "📈 𝗧𝗢𝗣 𝗚𝗔𝗜𝗡𝗘𝗥𝗦\n"
    for s in movers.get("gainers", [])[:5]:
        msg += f"🟢 {s.get('symbol')} → {s.get('change_pct')}%\n"

    # ================= TOP LOSERS =================
    msg += "\n🔴 𝗧𝗢𝗣 𝗟𝗢𝗦𝗘𝗥𝗦\n"
    for s in movers.get("losers", [])[:5]:
        msg += f"🔴 {s.get('symbol')} → {s.get('change_pct')}%\n"

    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📌 AI STATUS: LIVE MARKET TRACKING ACTIVE"

    return msg

# ==========================
# MAIN LOOP
# ==========================

last_update = None

while True:
    try:
        data = fetch_api()

        if not data:
            print("API Failed")
            time.sleep(30)
            continue

        current_update = data.get("updated_at")

        if current_update and current_update != last_update:

            msg = create_message(data)
            send_telegram(msg)

            print("✅ Sent")
            last_update = current_update

        else:
            print("No Update")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)