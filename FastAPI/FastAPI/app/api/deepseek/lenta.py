import feedparser
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from FastAPI.app.api.deepseek.service import generate_summary
from FastAPI.app.services.logger import setup_logger

logger = setup_logger('lenta_parser')

def fetch_lenta_article_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find("div", class_="topic-body__content")
    if not body:
        return ""
    paragraphs = body.find_all("p")
    return "\n\n".join(p.get_text(" ", strip=True) for p in paragraphs)

def run_lenta_parser():
    logger.info("🔍 Запуск парсера LENTA")
    rss_url = "https://lenta.ru/rss/news"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except requests.RequestException as e:
        logger.error(f"❌ Ошибка при загрузке RSS: {e}")
        return

    logger.info(f"📥 RSS получен. Найдено {len(feed.entries)} записей.")

    if not feed.entries:
        logger.warning("❗ RSS пустой — новостей нет.")
        return

    link = feed.entries[0].link
    txt = fetch_lenta_article_text(link)

    if not txt:
        logger.warning("❗ Пустой текст статьи.")
        return

    base = Path(__file__).parent
    save_path = base / "neww.json"
    sent_path = base / "sent_news.json"

    generate_summary(txt, save_path, sent_path)


if __name__ == "__main__":
    run_lenta_parser()
