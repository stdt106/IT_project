import pika
import json
import os
import django
from datetime import datetime


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django.settings')
django.setup()

from news.models import Articles


def save_article(data):
    try:
        title = data.get('title')
        anons = data.get('anons')
        full_text = data.get('full_text')
        date_str = data.get('date')

        if not (title and anons and full_text):
            print("⚠️ Пропущены обязательные поля! Пропускаем.")
            return

        date = datetime.fromisoformat(date_str) if date_str else datetime.now()

        article = Articles(
            title=title,
            anons=anons,
            full_text=full_text,
            date=date
        )
        article.save()
        print(f"✅ Новость добавлена: \n{title}\n{anons}\n{full_text}\n{date}")
    except Exception as e:
        print("❌ Ошибка при сохранении новости:", e)


def callback(ch, method, properties, body):
    print("📥 Получено сообщение")
    try:
        data = json.loads(body)
        save_article(data)
    except json.JSONDecodeError:
        print("❌ Невозможно декодировать JSON:", body)
    except Exception as e:
        print("❌ Ошибка при обработке сообщения:", e)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():

    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )

    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='news_queue', durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='news_queue', on_message_callback=callback)

        print("🎧 Ожидание новостей из RabbitMQ...")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("❌ Не удалось подключиться к RabbitMQ:", e)
    except KeyboardInterrupt:
        print("⛔ Остановлено пользователем")
    except Exception as e:
        print("❌ Общая ошибка:", e)


if __name__ == '__main__':
    main()
