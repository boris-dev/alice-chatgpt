from fastapi import FastAPI, Request
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

@app.post("/")
async def alice_chatgpt(req: Request):
    body = await req.json()
    user_text = body["request"].get("original_utterance", "")

    if not user_text.strip():
        return {
            "response": {
                "text": "Чем могу помочь?",
                "end_session": False
            },
            "version": body.get("version", "1.0")
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Отвечай коротко и понятно"},
                {"role": "user", "content": user_text}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = "Произошла ошибка при обращении к ChatGPT."

    return {
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": body.get("version", "1.0")
    }
