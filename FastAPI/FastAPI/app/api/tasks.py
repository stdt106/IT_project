from FastAPI.app.celery_worker import celery_app
from FastAPI.app.core.producer_singleton import producer_instance as producer
import logging


logger = logging.getLogger(__name__)

@celery_app.task(name="FastAPI.app.api.tasks.send_news")
def send_news(message: dict):
    try:
        logger.info(f"✅ [TASK] Получена новость: {message['title']}")
        producer.send("news_queue", message)
        logger.info("📤 Новость отправлена в очередь RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Ошибка в задаче Celery: {e}")