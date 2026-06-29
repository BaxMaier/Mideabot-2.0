import requests
import os
import asyncio
from telegram import Bot

# ==========================
# KONFIG
# ==========================

SEARCHES = [
    ("TOOM", "https://toom.de/s/midea%20portasplit%2012000"),
    ("OBI", "https://www.obi.de/search/midea%20portasplit%2012000/"),
    ("BAUHAUS", "https://www.bauhaus.info/suche/produkte?query=midea%20portasplit"),
    ("HORNBACH", "https://www.hornbach.de/suche/midea%20portasplit/")
]

KEYWORDS = ["midea", "12000", "portasplit"]

# Hinweise auf echte Verfügbarkeit
AVAILABILITY_HINTS = [
    "abholung",
    "verfügbar",
    "lieferbar",
    "im markt",
    "auf lager",
    "sofort lieferbar",
    "bestellbar"
]

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ==========================
# SHOP CHECK
# ==========================

def check_shop(name, url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=10)
        text = r.text.lower()

        keyword_hit = all(k in text for k in KEYWORDS)
        availability_hit = any(h in text for h in AVAILABILITY_HINTS)

        if keyword_hit and availability_hit:
            return f"✅ {name}: Midea PortaSplit evtl. verfügbar!\n{url}"

    except Exception as e:
        print(name, "Fehler:", e)

    return None


# ==========================
# TELEGRAM SEND (async!)
# ==========================

async def send_message(msg):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)


# ==========================
# MAIN LOGIK
# ==========================

async def main():
    print("🔍 Prüfe Baumärkte...")

    results = []

    for name, url in SEARCHES:
        result = check_shop(name, url)
        if result:
            results.append(result)

    if results:
        msg = "🚨 PortaSplit gefunden!\n\n" + "\n\n".join(results)
        await send_message(msg)
        print("✅ Treffer gesendet!")
    else:
        print("❌ Kein Treffer")


# ==========================
# START
# ==========================

if __name__ == "__main__":
    asyncio.run(main())
