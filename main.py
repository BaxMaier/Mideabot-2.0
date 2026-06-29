import requests
import os
import asyncio
import json
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

AVAILABILITY_HINTS = [
    "abholung",
    "verfügbar",
    "lieferbar",
    "im markt",
    "auf lager",
    "sofort lieferbar",
    "bestellbar"
]

# 👉 Freiburg + Umgebung (PLZ Trick)
PLZ_LIST = ["79098", "79100", "79106", "79206", "79312", "77652"]

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STATE_FILE = "seen.json"


# ==========================
# SPAM SCHUTZ (Speicher)
# ==========================

def load_seen():
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen), f)


# ==========================
# SHOP CHECK mit PLZ Trick
# ==========================

def check_shop(name, url):
    results = []

    for plz in PLZ_LIST:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "X-Forwarded-For": f"79.{plz[:2]}.1.1",  # Fake Region
                "Accept-Language": "de-DE,de;q=0.9"
            }

            r = requests.get(url, headers=headers, timeout=10)
            text = r.text.lower()

            if all(k in text for k in KEYWORDS):
                if any(a in text for a in AVAILABILITY_HINTS):

                    result = f"{name} (PLZ {plz}) → evtl. verfügbar\n{url}"
                    results.append(result)

        except Exception as e:
            print(name, "Fehler:", e)

    return results


# ==========================
# TELEGRAM SEND
# ==========================

async def send_message(msg):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)


# ==========================
# MAIN LOGIK
# ==========================

async def main():
    print("🔍 Prüfe Baumärkte + PLZ...")

    seen = load_seen()
    new_hits = set()

    for name, url in SEARCHES:
        results = check_shop(name, url)

        for r in results:
            if r not in seen:
                new_hits.add(r)

    if new_hits:
        msg = "🚨 PortaSplit gefunden!\n\n" + "\n\n".join(new_hits)
        await send_message(msg)

        seen.update(new_hits)
        save_seen(seen)

        print("✅ Neue Treffer gesendet!")
    else:
        print("❌ Keine neuen Treffer")


# ==========================
# START
# ==========================

if __name__ == "__main__":
    asyncio.run(main())

