from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from app.core.producer import RabbitProducer

# Создаем основной экземпляр FastAPI
app = FastAPI(title="RabbitMQ Manager", docs_url="/docs")

# Создаем роутер
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>FastAPI + RabbitMQ</title></head>
        <body>
            <h1>Сервер работает!</h1>
            <p>Доступные эндпоинты:</p>
            <ul>
                <li><a href="/docs">/docs</a> - Swagger UI</li>
                <li>POST <a href="/send">/send</a> - Отправка сообщений</li>
            </ul>
        </body>
    </html>
    """

@router.post("/send")
async def send_message(message: dict):
    producer = RabbitProducer()
    try:
        producer.send(queue_name="to_db", message=message)
        return {"status": "Сообщение отправлено"}
    finally:
        producer.close()

# Подключаем роутер к приложению
app.include_router(router)