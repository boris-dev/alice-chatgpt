from fastapi import FastAPI, Request
import os
import time
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

user_sessions = {}
SESSION_TIMEOUT = 1200  # 20 минут
REQUEST_INTERVAL = 4  # 4 секунды

@app.post("/")
async def alice_chatgpt(req: Request):
    body = await req.json()
    user_text = body["request"].get("original_utterance", "")
    user_id = body["session"]["user_id"]
    current_time = time.time()

    session = user_sessions.get(user_id)

    # Проверка частоты запросов
    if session and current_time - session['last_request'] < REQUEST_INTERVAL:
        return {
            "response": {"text": "Подожди немного, ты отправляешь запросы слишком быстро!", "end_session": False},
            "version": body.get("version", "1.0")
        }

    # Создание новой сессии или очистка по таймауту
    if not session or current_time - session['last_interaction'] > SESSION_TIMEOUT:
        user_sessions[user_id] = {'history': [], 'last_interaction': current_time, 'last_request': current_time}
    else:
        user_sessions[user_id]['last_interaction'] = current_time
        user_sessions[user_id]['last_request'] = current_time

    # Команда очистки истории
    if "сотри историю" in user_text.lower():
        user_sessions[user_id]['history'] = []
        return {
            "response": {"text": "История очищена!", "end_session": False},
            "version": body.get("version", "1.0")
        }

    # Команда показа контекста
    if "контекст" in user_text.lower():
        user_messages = [msg['content'] for msg in user_sessions[user_id]['history'] if msg['role'] == 'user']
        if not user_messages:
            context_text = "Контекст пуст."
        else:
            context_text = "Ты спрашивал: " + "; ".join(user_messages)
        return {
            "response": {"text": context_text, "end_session": False},
            "version": body.get("version", "1.0")
        }

    user_sessions[user_id]['history'].append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Ты помощник Алисы, отвечай коротко и понятно."}] + user_sessions[user_id]['history']
        )
        answer = response.choices[0].message.content.strip()
        user_sessions[user_id]['history'].append({"role": "assistant", "content": answer})
    except Exception as e:
        answer = "Произошла ошибка при обращении к ChatGPT."

    return {
        "response": {"text": answer, "end_session": False},
        "version": body.get("version", "1.0")
    }
