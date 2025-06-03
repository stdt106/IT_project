from pydantic import BaseModel


class Message(BaseModel):
    title: str
    summary: str
    full_text: str
    data: str = ""