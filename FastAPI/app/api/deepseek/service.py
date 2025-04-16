from pprint import pprint
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import requests
import feedparser

import feedparser
import requests
from bs4 import BeautifulSoup

def fetch_lenta_article_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Не удалось получить статью."

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find("div", class_="topic-body__content")
    if not body:
        return "Не удалось найти текст статьи."

    paragraphs = body.find_all("p")
    return "\n\n".join(p.get_text(" ", strip=True) for p in paragraphs)

def main():
    rss_url = "https://lenta.ru/rss/news"
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        print("Новостей нет.")
        return

    first_entry = feed.entries[0]
    link = first_entry.link
    print(f"\n📰 Ссылка на статью: {link}")

    text = fetch_lenta_article_text(link)
    print(f"\n📝 Текст статьи:\n{text}")

if __name__ == "__main__":
    main()

'''
# Парсим RSS-ленту
feed = feedparser.parse(rss_url)

# Получаем полную новость (в виде строки) из первого элемента в ленте
if feed.entries:
    first_entry = feed.entries[0]
    #full_news = first_entry.title + "\n" + first_entry.summary + "\n" + first_entry.link

    # Выводим полную новость
    #print(full_news)
    print(first_entry)
else:
    print("Нет новостей для отображения.")

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
TSS = os.getenv("TSS")

JSON_PATH = Path(__file__).parent / "neww.json"

#rss_url = "https://feeds.bbci.co.uk/news/world/rss.xml"
#feed = feedparser.parse(rss_url)
#news = ('Российские военные нанесли удар по месту проведения совещания командования Вооруженных сил Украины (ВСУ) в Сумах, сообщили в Минобороны России. "Нанесен удар двумя оперативно-тактическими ракетами "Искандер-М" по месту проведения совещания командного состава оперативно-тактической группы "Северск", – говорится в сообщении. Цель была поражена, были ликвидированы более 60 боевиков ВСУ. В оборонном ведомстве подчеркнули, что киевский режим продолжает использовать мирное население в качестве живого щита, а также размещать военные объекты и проводить мероприятия с участием боевиков в центре густонаселенного города. Ранее мэр украинского Конотопа Артем Семенихин сообщил о том, что на Украине возбудили уголовное дело в отношении организаторов собрания боевиков Вооруженных сил Украины в городе Сумы. По его словам, инициатором сбора украинских боевиков из 117-й бригады выступил глава Сумской областной военной администрации Владимир Артюх.')

url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": TSS,
}

data = {
    "model": "deepseek-ai/DeepSeek-R1",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": f"Тебе на вход подаётся новость, тебе её надо озаглавить (ограничься 50 символами), потом написать эту же новость, но кратко. Пиши без слов 'заголовок' и 'название', и 'краткий пересказ'. Замечание: если новость иностранная, то ты всё не забываешь переводить на русский язык. Вот новость в оригинале: {news}"
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
data = response.json()
#pprint(data)

text = data['choices'][0]['message']['content']
pprint(text.split('</think>\n\n')[1])

api_data = response.json()
processed_text = api_data['choices'][0]['message']['content']
brief_text = processed_text.split('</think>\n\n')[1]

result = {
        "full_text": news,          # Исходная новость
        "title": brief_text.split('\n')[0],  # Первая строка — заголовок
        "anons": '\n'.join(brief_text.split('\n')[1:]),  # Остальное — краткий пересказ
        "data": ""
    }

# Сохраняем в JSON
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
print(f"Данные сохранены в {JSON_PATH}")
'''