from fastapi import FastAPI, Request
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

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

    chatgpt_resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": user_text}
        ]
    )

    answer = chatgpt_resp.choices[0].message.content.strip()

    return {
        "response": {
            "text": answer,
            "end_session": False
        },
        "version": body["version"]
    }