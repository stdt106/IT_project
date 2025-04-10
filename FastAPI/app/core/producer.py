import pika
import json
from app.services.logger import setup_logger
logger = setup_logger('rabbit_producer')


class RabbitProducer:
    def __init__(self):
        """Инициализация подключения"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        logger.info("Producer подключен к RabbitMQ")

    def send(self, queue_name: str, message: dict):
        """Отправка сообщения в очередь"""
        try:
            # 1. Объявляем очередь (если её нет)
            self.channel.queue_declare(
                queue=queue_name,
                durable=True  # Сохраняет очередь при перезагрузке
            )

            # 2. Публикуем сообщение
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2  # Сохраняет сообщение на диске
                )
            )
            logger.info(f"Отправлено в {queue_name}: {message}")

        except Exception as e:
            logger.error(f"Ошибка отправки: {str(e)}")
            raise

    def close(self):
        """Закрытие подключения"""
        if self.connection:
            self.connection.close()
            logger.info("Producer отключен")