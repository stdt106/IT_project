import pika
import json
import os
from dotenv import load_dotenv
from FastAPI.app.services.logger import setup_logger

logger = setup_logger('rabbit_producer')

load_dotenv()

class RabbitProducer:
    def __init__(self):

        try:
            credentials = pika.PlainCredentials(
                os.getenv("RABBITMQ_USER"),
                os.getenv("RABBITMQ_PASS")
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST"),
                port=int(os.getenv("RABBITMQ_PORT")),
                credentials=credentials
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Producer подключен к RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к RabbitMQ: {e}")
            raise

    def send(self, queue_name: str, message: dict):

        try:
            self.channel.queue_declare(
                queue=queue_name,
                durable=True
            )

            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )
            logger.info(f"📰 Отправлено в {queue_name}: {' '.join(message['full_text'].split()[:5])}...")

        except Exception as e:
            logger.error(f"Ошибка отправки: {str(e)}")
            raise

    def close(self):

        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Producer отключен")
