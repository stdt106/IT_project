from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from pydantic import BaseModel
from pathlib import Path
import json
import logging
import asyncio
import sys
import importlib.util
import threading

from FastAPI.app.api.deepseek.tass import run_tass_parser
from FastAPI.app.api.deepseek.lenta import run_lenta_parser
from FastAPI.app.api.deepseek.file_watcher_lenta import start_watching as start_watching_lenta
from FastAPI.app.api.deepseek.file_watcher_tass import start_watching as start_watching_tass
from FastAPI.app.core.producer_singleton import producer_instance as producer
from FastAPI.app.api.schemas import Message

# Celery задача
from FastAPI.app.api.tasks import send_news

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Импортируем service.py как модуль
service_path = Path(__file__).parent / "deepseek" / "service.py"
spec = importlib.util.spec_from_file_location("news_service", service_path)
news_service = importlib.util.module_from_spec(spec)
sys.modules["news_service"] = news_service
spec.loader.exec_module(news_service)


def send_to_rabbitmq():
    """Проверяет новость и отправляет в RabbitMQ через Celery, если это новая новость."""
    neww_path = Path(__file__).parent / "deepseek" / "neww.json"
    sent_path = Path(__file__).parent / "deepseek" / "sent_news.json"

    try:
        with open(neww_path, 'r', encoding='utf-8') as f:
            new_news = json.load(f)

        if sent_path.exists():
            with open(sent_path, 'r', encoding='utf-8') as f:
                sent_news = json.load(f)
            if new_news['full_text'] == sent_news.get('full_text'):
                logger.info("Такая новость уже отправлялась. Пропускаем.")
                return

        # Отправляем через Celery
        send_news.delay(new_news)
        logger.info("📤 Задача отправлена через Celery")

        with open(sent_path, 'w', encoding='utf-8') as f:
            json.dump(new_news, f, ensure_ascii=False, indent=4)
        logger.info("💾 Новость сохранена в sent_news.json")

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке в Celery: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("♻️ Цикл запуска парсеров...")

    # watcher'ы
    threading.Thread(target=start_watching_lenta, args=(producer,), daemon=True).start()
    threading.Thread(target=start_watching_tass, args=(producer,), daemon=True).start()

    async def background_loop():
        logger.info("🔁 background_loop запущен")
        while True:
            run_lenta_parser()
            run_tass_parser()
            await asyncio.sleep(15)

    asyncio.create_task(background_loop())
    send_to_rabbitmq()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@router.post("/send")
async def send_message(message: Message):
    try:
        send_news.delay(message.model_dump())
        return {"status": "Задача отправлена через Celery"}
    except Exception as e:
        return {"status": f"Ошибка при отправке: {e}"}
