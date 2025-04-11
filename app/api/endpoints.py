from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from app.core.producer import RabbitProducer

app = FastAPI()
router = APIRouter()

# Добавляем модель для валидации
class Message(BaseModel):
    title: str  # Обязательное поле
    anons: str = "Trump do smth, definitely"  # Необязательное поле со значением по умолчанию
    full_text: str = "Nema"

@router.post("/send")
async def send_message(message: Message):  # Используем модель
    producer = RabbitProducer()
    try:
        # Преобразуем Pydantic-модель в dict
        producer.send(queue_name="news_queue", message=message.dict())
        return {"status": "Сообщение отправлено"}
    finally:
        producer.close()

app.include_router(router)