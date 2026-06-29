import requests
from telegram import Bot
import os

SEARCHES = [
    ("TOOM", "https://toom.de/s/midea%20portasplit%2012000"),
    ("OBI", "https://www.obi.de/search/midea%20portasplit%2012000/"),
    ("BAUHAUS", "https://www.bauhaus.info/suche/produkte?query=midea%20portasplit"),
    ("HORNBACH", "https://www.hornbach.de/suche/midea%20portasplit/")
]

KEYWORDS = ["midea", "12000"]

AVAILABILITY = [
    "abholung",
    "verfügbar",
    "lieferbar",
    "im markt",
    "auf lager"
]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def check_shop(name, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)

    text = r.text.lower()

    if all(k in text for k in KEYWORDS):
        if any(a in text for a in AVAILABILITY):
            return f"✅ {name}: möglicherweise verfügbar!\n{url}"

    return None


def send(msg):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=msg)


def main():
    results = []

    for name, url in SEARCHES:
        try:
            res = check_shop(name, url)
            if res:
                results.append(res)
        except Exception as e:
            print(name, "Fehler:", e)

    if results:
        send("\n\n".join(results))


if __name__ == "__main__":
    main()
