from fastapi import FastAPI, Request
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

@app.post("/")
async def alice_chatgpt(req: Request):
    body = await req.json()
    user_text = body["request"]["original_utterance"]

    if not user_text:
        return {
            "response": {
                "text": "Привет! Что хочешь узнать?",
                "end_session": False
            },
            "version": body["version"]
        }

    response = client.chat.completions.create(
        model="gpt-4o",  # или "gpt-3.5-turbo"
        messages=[{"role": "user", "content": user_text}]
    )

    answer = response.choices[0].message.content.strip()

    return {
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": body["version"]
    }