import requests
import os
import asyncio
import datetime
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

POSITIVE_HINTS = [
    "abholung",
    "verfügbar",
    "lieferbar",
    "im markt",
    "auf lager",
    "sofort lieferbar",
    "bestellbar"
]

NEGATIVE_HINTS = [
    "nicht verfügbar",
    "nicht lieferbar",
    "derzeit nicht",
    "ausverkauft",
    "kein bestand"
]

# Freiburg Umgebung (PLZ Trick)
PLZ_LIST = ["79098", "79100", "79106", "79206", "79312", "77652"]

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ==========================
# TELEGRAM SEND
# ==========================

async def send_message(msg):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)


# ==========================
# STATUSMELDUNG
# ==========================

def should_send_status():
    now = datetime.datetime.now()
    # jeden Tag zwischen 09:00 und 09:05
    return now.hour == 9


# ==========================
# SHOP CHECK
# ==========================

def check_shop(name, url):
    results = []

    for plz in PLZ_LIST:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "de-DE,de;q=0.9",
                "X-Forwarded-For": f"79.{plz[:2]}.1.1"
            }

            r = requests.get(url, headers=headers, timeout=10)
            text = r.text.lower()

            keyword_hit = all(k in text for k in KEYWORDS)
            positive = any(p in text for p in POSITIVE_HINTS)
            negative = any(n in text for n in NEGATIVE_HINTS)

            if keyword_hit and positive and not negative:
                result = f"✅ {name} (PLZ {plz}) → wahrscheinlich verfügbar\n{url}"
                results.append(result)

        except Exception as e:
            print(f"{name} Fehler:", e)

    return results


# ==========================
# MAIN
# ==========================

async def main():
    try:
        print("🔍 Prüfe Baumärkte...")

        all_results = []

        for name, url in SEARCHES:
            results = check_shop(name, url)
            all_results.extend(results)

        # ✅ Treffer gefunden
        if all_results:
            message = "🚨 PortaSplit möglicherweise verfügbar!\n\n"
            message += "\n\n".join(all_results)

            await send_message(message)
            print("✅ Treffer gesendet")

        # ✅ tägliche Statusmeldung
        elif should_send_status():
            now = datetime.datetime.now().strftime("%H:%M")
            msg = f"✅ Status: Bot läuft ({now}), kein Treffer aktuell."
            await send_message(msg)
            print("ℹ️ Status gesendet")

        else:
            print("❌ Kein Treffer")

    except Exception as e:
        # ✅ Fehlerüberwachung
        error_msg = f"❌ BOT FEHLER:\n{str(e)}"
        print(error_msg)

        try:
            await send_message(error_msg)
        except:
            print("⚠️ Telegram Fehler konnte nicht gesendet werden")


# ==========================
# START
# ==========================

if __name__ == "__main__":
    asyncio.run(main())
