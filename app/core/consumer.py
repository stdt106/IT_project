import pika
import json
from app.services.logger import setup_logger
logger = setup_logger('rabbit_producer')


class RabbitConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        """Подключение к RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        logger.info("Consumer подключен")

    def start_consuming(self, queue_name: str):
        """Слушаем указанную очередь"""
        # 1. Объявляем очередь (такая же, как у Producer)
        self.channel.queue_declare(
            queue=queue_name,
            durable=True
        )

        # 2. Настройка Fair Dispatch
        self.channel.basic_qos(prefetch_count=1)

        # 3. Подписка на очередь
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._process_message,
            auto_ack=False
        )

        logger.info(f"Ожидаем сообщения в {queue_name}...")
        self.channel.start_consuming()

    def _process_message(self, ch, method, properties, body):
        """Обработка полученного сообщения"""
        try:
            message = json.loads(body)
            logger.info(f"Получено: {message}")

            # Здесь будет логика обработки (пока просто подтверждаем)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Ошибка обработки: {str(e)}")
            # Можно добавить повторную попытку или dead-letter очередь

    def close(self):
        """Корректное отключение"""
        if self.connection:
            self.connection.close()
            logger.info("Consumer отключен")