import pika
import json
from FastAPI.app.services.logger import setup_logger


logger = setup_logger('rabbit_producer')


class RabbitProducer:

    def __init__(self):
        self._connect()

    def _connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='127.0.0.1', port=5672)
            )
            self.channel = self.connection.channel()
            logger.info("Producer подключен к RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к RabbitMQ: {e}")
            raise

    def send(self, queue_name: str, message: dict):
        try:
            if self.connection.is_closed or self.channel.is_closed:
                logger.warning("🔁 Переподключение к RabbitMQ...")
                self._connect()

            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info(f"📤 Отправлено в очередь {queue_name}")
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
            raise

    def close(self):
        try:
            if self.channel.is_open:
                self.channel.close()
            if self.connection.is_open:
                self.connection.close()
            logger.info("Producer отключен")
        except Exception as e:
            logger.error(f"Ошибка при закрытии Producer: {e}")
