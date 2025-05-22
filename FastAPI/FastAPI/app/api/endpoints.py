from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from pydantic import BaseModel

from FastAPI.app.api.deepseek.tass import run_tass_parser
from FastAPI.app.core.producer import RabbitProducer
from pathlib import Path
import json
import logging
import asyncio
import sys
import importlib.util
from FastAPI.app.api.deepseek.file_watcher_lenta import start_watching
import threading

from FastAPI.app.api.deepseek.lenta import run_lenta_parser
from FastAPI.app.api.deepseek.tass import run_tass_parser
from FastAPI.app.api.deepseek.file_watcher_tass import start_watching as start_watching_tass


# Импортируем service.py как модуль
service_path = Path(__file__).parent / "deepseek" / "service.py"
spec = importlib.util.spec_from_file_location("news_service", service_path)
news_service = importlib.util.module_from_spec(spec)
sys.modules["news_service"] = news_service
spec.loader.exec_module(news_service)

#app = FastAPI()
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JSON_PATH = Path(__file__).parent / "deepseek" / "neww.json"

# Добавляем модель для валидации
class Message(BaseModel):
    title: str
    summary: str
    full_text: str
    data: str = ""


def send_to_rabbitmq():
    """Проверяет новость и отправляет в RabbitMQ, если это новая новость."""
    neww_path = Path(__file__).parent / "deepseek" / "neww.json"
    sent_path = Path(__file__).parent / "deepseek" / "sent_news.json"

    try:
        with open(neww_path, 'r', encoding='utf-8') as f:
            new_news = json.load(f)

        # Если есть файл с отправленной новостью, сравниваем
        if sent_path.exists():
            with open(sent_path, 'r', encoding='utf-8') as f:
                sent_news = json.load(f)
            if new_news['full_text'] == sent_news.get('full_text'):
                logger.info("Такая новость уже отправлялась. Пропускаем.")
                return

        # Отправка в RabbitMQ
        producer = RabbitProducer()
        producer.send(queue_name="news_queue", message=new_news)
        producer.close()
        logger.info("Данные из neww.json отправлены в RabbitMQ")

        # Только после успешной отправки — сохраняем в sent_news.json
        with open(sent_path, 'w', encoding='utf-8') as f:
            json.dump(new_news, f, ensure_ascii=False, indent=4)
        logger.info("Новость сохранена в sent_news.json")

    except Exception as e:
        logger.error(f"Ошибка при отправке в RabbitMQ: {e}")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем watcher в отдельном потоке
    threading.Thread(target=start_watching, daemon=True).start()
    threading.Thread(target=start_watching_tass, daemon=True).start()

    # Запускаем парсер
    async def background_loop():
        while True:
            run_lenta_parser()
            run_tass_parser()
            await asyncio.sleep(15)

    asyncio.create_task(background_loop())
    send_to_rabbitmq()
    #asyncio.create_task(background_loop())
    yield

app = FastAPI(lifespan=lifespan)  # Передаем lifespan в конструктор

@router.post("/send")
async def send_message(message: Message):  # Используем модель
    producer = RabbitProducer()
    try:
        # Преобразуем Pydantic-модель в dict
        producer.send(queue_name="news_queue", message=message.model_dump())
        return {"status": "Сообщение отправлено"}
    finally:
        producer.close()

app.include_router(router)