import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from FastAPI.app.services.logger import setup_logger
from FastAPI.app.core.producer_singleton import producer_instance as producer

logger = setup_logger('file_watcher_tass')

NEW_PATH = Path(__file__).parent / "neww_tass.json"
SENT_PATH = Path(__file__).parent / "sent_news_tass.json"

class NewwTassHandler(FileSystemEventHandler):
    def __init__(self, producer):
        self.producer = producer

    def on_modified(self, event):
        # Проверка на изменение нужного файла
        if Path(event.src_path).resolve() != NEW_PATH.resolve():
            return

        logger.info("🟢 Обнаружено изменение neww_tass.json")

        try:
            with open(NEW_PATH, 'r', encoding='utf-8') as f:
                new_data = json.load(f)

            # Если новость уже была отправлена — не дублируем
            if SENT_PATH.exists():
                with open(SENT_PATH, 'r', encoding='utf-8') as f:
                    sent_data = json.load(f)
                if sent_data.get("full_text") == new_data.get("full_text"):
                    logger.warning("🟡 Новость уже отправлялась, пропускаем.")
                    return

            # Отправляем в очередь
            try:
                self.producer.send("news_queue", new_data)
                logger.info("✅ Новость отправлена в RabbitMQ")
            except Exception as e:
                logger.error(f"❌ Ошибка отправки: {e}")
                return

            # Обновляем sent_news_tass.json
            with open(SENT_PATH, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            logger.error(f"❌ Ошибка при обработке neww_tass.json: {e}")

def start_watching(producer):
    observer = Observer()
    event_handler = NewwTassHandler(producer)
    observer.schedule(event_handler, path=NEW_PATH.parent, recursive=False)
    observer.start()
    logger.info("👀 Слежение за neww_tass.json запущено")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
