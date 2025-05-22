import feedparser
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from FastAPI.app.api.deepseek.service import generate_summary
from FastAPI.app.services.logger import setup_logger

logger = setup_logger('tass_parser')

def fetch_article_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.find("div", class_="text-content")
    if not content:
        return ""

    block = content.find("div", class_="text-block")
    if not block:
        return ""

    paragraphs = block.find_all("p")
    return "\n\n".join(p.get_text(" ", strip=True) for p in paragraphs)


def run_tass_parser():
    logger.info("🔍 Запуск парсера TASS")
    rss_url = "https://tass.com/rss/v2.xml"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except requests.RequestException as e:
        logger.error(f"❌ Ошибка при загрузке RSS TASS: {e}")
        return

    logger.info(f"📥 RSS получен. Найдено {len(feed.entries)} записей.")

    if not feed.entries:
        logger.warning("❗ RSS пустой — TASS")
        return

    link = feed.entries[0].link
    txt = fetch_article_text(link)

    if not txt:
        logger.warning("❗ Пустой текст статьи.")
        return

    base = Path(__file__).parent
    save_path = base / "neww_tass.json"
    sent_path = base / "sent_news_tass.json"

    generate_summary(txt, save_path, sent_path)


if __name__ == "__main__":
    run_tass_parser()