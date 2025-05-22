import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path
from FastAPI.app.services.logger import setup_logger

logger = setup_logger('deepseek_service')

def generate_summary(txt: str, save_path: Path, sent_path: Path):
    """Отправляет текст новости в GPT и сохраняет результат"""

    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))
    TSS = os.getenv("TSS")

    if sent_path.exists():
        with open(sent_path, "r", encoding="utf-8") as f:
            last = json.load(f)
        if last.get("full_text", "").strip() == txt.strip():
            logger.info("🟡 Эта новость уже обрабатывалась.")
            return

    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": TSS,
    }

    data = {
        "model": "deepseek-ai/DeepSeek-R1",
        "messages": [
            {"role": "system",
             "content": "You are a helpful assistant."
             },
            {"role": "user",
             "content": f"Тебе на вход подаётся новость, тебе её надо озаглавить (ограничься 50 символами) и помести его строго в первую строку, потом написать эту же новость, но кратко (постарайся ограничиться 150 символами). Пиши без слов 'заголовок' и 'название', и 'краткий пересказ'. Замечание: если новость иностранная, то ты всё не забываешь переводить на русский язык. Вот новость в оригинале: {txt}"
             }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=(5, 60))
        response.raise_for_status()
        gpt_data = response.json()
        content = gpt_data['choices'][0]['message']['content']
        brief_text = content.split('</think>\n\n')[1]
    except Exception as e:
        logger.error(f"❌ Ошибка GPT: {e}")
        return

    result = {
        "full_text": txt,
        "title": brief_text.split('\n')[0],
        "anons": '\n'.join(brief_text.split('\n')[1:]),
        "data": ""
    }

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    #with open(sent_path, 'w', encoding='utf-8') as f:
    #    json.dump(result, f, ensure_ascii=False, indent=4)

    logger.info(f"✅ Новость обработана и сохранена: {save_path}")




#from dotenv import load_dotenv
#import os
#import requests
#from pprint import pprint
#
#
#load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))
#TSS = os.getenv("TSS")
#
#url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
#headers = {
#    "Content-Type": "application/json",
#    "Authorization": TSS,
#}
#
#data = {
#    "model": "deepseek-ai/DeepSeek-R1",
#    "messages": [
#        {
#            "role": "system",
#            "content": "You are a very helpful assistant.",
#        },
#        {
#            "role": "user",
#            "content": input("Введите промпт:\n"),
#        }
#    ]
#}
#
#response = requests.post(url, headers=headers, json=data, timeout=(15, 120))
#response.raise_for_status()
#data = response.json()
#text = data['choices'][0]['message']['content']
#pprint(text.split('</think>\n\n')[1])
#
#processed_text = data['choices'][0]['message']['content']
#brief_text = processed_text.split('</think>\n\n')[1]
#choices = data.get("choices")