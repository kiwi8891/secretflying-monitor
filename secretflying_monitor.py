import os
import json
import requests
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CITIES = ["barcelona", "valencia", "madrid"]
URL = "https://www.secretflying.com/europe-flight-deals/"
SEEN_FILE = Path(__file__).parent / "seen.json"
DAYS_BACK = 3


def load_seen():
    if not SEEN_FILE.exists():
        return {}
    data = json.loads(SEEN_FILE.read_text())
    if isinstance(data, list):
        return {url: "1970-01-01" for url in data}
    return data


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(seen, indent=2))


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }, timeout=10)


def fetch_deals():
    scraper = cloudscraper.create_scraper()
    resp = scraper.get(URL, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cutoff = datetime.now() - timedelta(days=DAYS_BACK)
    deals = []

    for article in soup.select("article"):
        time_tag = article.find("time")
        if not time_tag:
            continue
        try:
            pub_date = datetime.strptime(time_tag.text.strip(), "%B %d, %Y")
        except ValueError:
            continue
        if pub_date < cutoff:
            continue

        heading = article.find("h2")
        link_tag = article.find("a", href=lambda h: h and "/posts/" in h)
        if not heading or not link_tag:
            continue

        title = heading.get_text(strip=True)
        link = link_tag["href"]

        if any(city in title.lower() for city in CITIES):
            deals.append({
                "title": title,
                "link": link,
                "date": pub_date.strftime("%d %b %Y"),
                "pub_iso": pub_date.strftime("%Y-%m-%d"),
            })

    return deals


def main():
    seen = load_seen()
    deals = fetch_deals()
    new_deals = [d for d in deals if d["pub_iso"] > seen.get(d["link"], "")]

    for deal in new_deals:
        msg = f"✈️ <b>Nueva oferta desde España</b>\n\n{deal['title']}\n📅 {deal['date']}\n🔗 {deal['link']}"
        send_telegram(msg)
        seen[deal["link"]] = deal["pub_iso"]
        print(f"Enviado: {deal['title']}")

    save_seen(seen)

    if not new_deals:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Sin novedades desde Barcelona, Valencia o Madrid.")


if __name__ == "__main__":
    main()
