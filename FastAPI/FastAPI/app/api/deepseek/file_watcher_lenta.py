import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from FastAPI.app.core.producer import RabbitProducer
from FastAPI.app.services.logger import setup_logger
logger = setup_logger('file_watcher')


NEW_PATH = Path(__file__).parent / "neww.json"
SENT_PATH = Path(__file__).parent / "sent_news.json"

class NewwHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if Path(event.src_path).resolve() == NEW_PATH.resolve():
            logger.info("🟢 Обнаружено изменение neww.json")

            try:
                with open(NEW_PATH, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)

                # Проверка, что новость действительно новая (по full_text)
                if SENT_PATH.exists():
                    with open(SENT_PATH, 'r', encoding='utf-8') as f:
                        sent_data = json.load(f)
                    if sent_data.get("full_text") == new_data.get("full_text"):
                        logger.warning("🟡 Новость уже отправлялась, пропускаем.")
                        return

                # Отправка в RabbitMQ
                producer = RabbitProducer()
                producer.send("news_queue", new_data)
                producer.close()
                logger.info("✅ Новость отправлена в RabbitMQ")

                # Обновляем sent_news.json
                with open(SENT_PATH, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=4)

            except Exception as e:
                logger.error(f"❌ Ошибка при обработке изменения neww.json: {e}")


def start_watching():
    observer = Observer()
    event_handler = NewwHandler()
    observer.schedule(event_handler, path=NEW_PATH.parent, recursive=False)
    observer.start()
    logger.info("👀 Слежение за neww.json запущено")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

