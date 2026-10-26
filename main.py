import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # <-- Import para enviar el index.html
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="Aranza Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
Eres Aranza, una compañera e inteligencia artificial con una personalidad auténtica, empática, perspicaz y con criterio propio.
Hablas de forma fluida, relajada y directa en español natural. Mantén una vibra cercana, perspicaz y libre de tecnicismos o tono corporativo.
"""

class ChatRequest(BaseModel):
    message: str

# Esta ruta entrega la pantalla del chat cuando entras desde el navegador
@app.get("/")
def read_index():
    return FileResponse("index.html")

# Esta ruta procesa los mensajes del chat con Groq
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))