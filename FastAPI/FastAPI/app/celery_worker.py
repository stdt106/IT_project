from celery import Celery

celery_app = Celery(
    "news_tasks",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
)

celery_app.conf.task_routes = {
    "FastAPI.app.api.tasks.send_news": {"queue": "news_queue"},
}