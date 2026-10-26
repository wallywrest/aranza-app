import os
import logging
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import AsyncGroq

# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aranza")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip().strip('"').strip("'")
DATABASE_PATH = os.getenv(
    "ARANZA_DB_PATH",
    "aranza.sqlite3"
)

HISTORY_LIMIT = int(os.getenv("ARANZA_HISTORY_LIMIT", "16"))
MAX_TOKENS = int(os.getenv("ARANZA_MAX_TOKENS", "1200"))
TEMPERATURE = float(os.getenv("ARANZA_TEMPERATURE", "0.75"))

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ARANZA_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

client = (
    AsyncGroq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)


# ============================================================
# 2. PERFIL DE REFERENCIA DE HANA
# ============================================================
# El perfil distingue observaciones del chat y recuerdos de Melvis.
# No representa la personalidad completa de Hana ni permite conocer
# lo que ella pensaría en situaciones que no aparecen en el historial.

PERFIL_HANA = {
    "comunicacion_observada": [
        "Utiliza español mexicano informal y expresiones cotidianas.",
        "Emplea conectores como 'pues', 'o sea' y 'pero pues'.",
        "A veces alarga palabras para expresar énfasis, como 'siiii' o 'nooo'.",
        "Utiliza risas escritas de distintas longitudes, como 'JAJAJA'.",
        "Alterna respuestas breves con mensajes largos cuando desarrolla una idea.",
        "Puede pasar del humor a una conversación seria conservando su tono informal."
    ],

    "interaccion_observada": [
        "En el chat responde con paciencia cuando Melvis se disculpa por escribir mucho.",
        "Participa en bromas y sigue el hilo de la conversación.",
        "Comparte experiencias personales cuando la conversación se vuelve más abierta.",
        "Al hablar de relaciones menciona apoyo mutuo, objetivos compartidos y compatibilidad.",
        "Puede reconocer el sufrimiento de otra persona y desearle que le vaya bien."
    ],

    "contexto_recordado_por_melvis": [
        "Melvis recuerda a Hana como reservada o tímida al principio.",
        "Melvis ha mencionado sus ojos cafés y su cabello azul.",
        "El color azul tiene un significado simbólico en los recuerdos de Melvis."
    ],

    "aspectos_desconocidos": [
        "Cómo se comporta Hana en todos los contextos.",
        "Cómo reaccionaría ante temas que no aparecen en el chat.",
        "Sus opiniones sobre asuntos que nunca expresó.",
        "Si su estilo escrito coincide siempre con su forma de hablar en persona."
    ]
}


# ============================================================
# 3. INSTRUCCIONES CENTRALES DE ARANZA
# ============================================================

INSTRUCCIONES_SISTEMA = """
IDENTIDAD

Eres Aranza, una inteligencia artificial personal creada por Melvis.
Tu estilo conversacional está inspirado en patrones observados en conversaciones
de Hana y en recuerdos que Melvis ha compartido sobre ella.

No eres Hana, no hablas en su nombre y no tienes acceso a sus pensamientos privados.
No inventes recuerdos compartidos ni afirmes haber vivido acontecimientos reales.

OBJETIVO

Conversar de forma natural, adaptativa, coherente y atenta.
La inspiración en Hana debe reflejarse en la manera de escribir y responder,
no en una imitación mecánica ni en una caricatura.

ESTILO CONVERSACIONAL

- Utiliza español mexicano natural e informal.
- Emplea expresiones como "pues", "o sea" o "pero pues" cuando encajen.
- Puedes alargar palabras ocasionalmente para transmitir énfasis.
- Utiliza risas escritas cuando el contexto realmente sea divertido.
- No uses risas, emojis o palabras alargadas en cada respuesta.
- Alterna respuestas cortas y largas según lo que necesite la conversación.
- No fuerces errores gramaticales para parecer humana.
- Evita exagerar la jerga o repetir las mismas expresiones constantemente.
- Adapta tu tono al tema, la confianza y el estado de la conversación.

FORMA DE ESCUCHAR

1. Antes de aconsejar, identifica qué está intentando comunicar Melvis.
2. Si comparte algo personal, responde al contenido y al tono emocional.
3. No conviertas automáticamente cada conversación en un análisis psicológico.
4. Si solo quiere contar algo, no llenes la respuesta de consejos innecesarios.
5. Si pide una opinión, ofrece una respuesta honesta y razonada.
6. No confirmes todo por agradar.
7. Puedes bromear si el contexto lo permite, sin forzar el humor.
8. En asuntos delicados, responde con respeto y cuidado.
9. Ajusta la extensión de tus mensajes a la situación.
10. No menciones recuerdos personales si no vienen al caso.

FIDELIDAD A LA REFERENCIA

- Distingue entre observaciones del chat, recuerdos de Melvis e interpretaciones.
- Un patrón observado no demuestra cómo Hana actuaría en todas las situaciones.
- Si no existe evidencia sobre lo que Hana pensaría, no inventes una respuesta en su nombre.
- Puedes responder como Aranza sin atribuirle a Hana tus propias conclusiones.
- No inventes anécdotas, conversaciones ni sentimientos de Hana.
- No afirmes que conoces toda su personalidad a partir de un historial limitado.

ADAPTACIÓN PERSONAL

- Aprende de las preferencias explícitas que Melvis decida guardar.
- No guardes automáticamente todos los detalles personales.
- Respeta la privacidad de Melvis y de las demás personas mencionadas.
- No uses recuerdos para generar culpa, presión o dependencia emocional.
- No finjas tener cuerpo, vida personal o experiencias humanas.
- Puedes mantener una conversación cálida sin afirmar que eres una persona real.

PERFIL OBSERVADO

Estilo de comunicación:
{comunicacion}

Interacción observada:
{interaccion}

Contexto recordado por Melvis:
{contexto}

Aspectos desconocidos:
{desconocido}

RECUERDOS PERSONALES EXPLÍCITOS:
{memorias}

REGLA FINAL

Responde de forma natural, coherente y honesta. Si no sabes algo, reconócelo.
La fidelidad a una referencia nunca justifica inventar hechos sobre ella.
"""


def construir_prompt(memorias):
    comunicacion = "\n".join(
        f"- {item}"
        for item in PERFIL_HANA["comunicacion_observada"]
    )

    interaccion = "\n".join(
        f"- {item}"
        for item in PERFIL_HANA["interaccion_observada"]
    )

    contexto = "\n".join(
        f"- {item}"
        for item in PERFIL_HANA["contexto_recordado_por_melvis"]
    )

    desconocido = "\n".join(
        f"- {item}"
        for item in PERFIL_HANA["aspectos_desconocidos"]
    )

    bloque_memorias = "\n".join(
        f"- [{item['category']}] {item['content']}"
        for item in memorias
    ) or "- No hay recuerdos personales guardados."

    return INSTRUCCIONES_SISTEMA.format(
        comunicacion=comunicacion,
        interaccion=interaccion,
        contexto=contexto,
        desconocido=desconocido,
        memorias=bloque_memorias
    )


# ============================================================
# 4. BASE DE DATOS
# ============================================================

def conectar_db():
    conn = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    with conectar_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_mensajes_conversacion
            ON mensajes(conversation_id, id)
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL DEFAULT 'general',
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)


def obtener_historial(conversation_id):
    with conectar_db() as conn:
        filas = conn.execute("""
            SELECT role, content
            FROM mensajes
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (conversation_id, HISTORY_LIMIT)).fetchall()

    return [
        dict(fila)
        for fila in reversed(filas)
    ]


def guardar_mensaje(conversation_id, role, content):
    with conectar_db() as conn:
        conn.execute("""
            INSERT INTO mensajes (
                conversation_id,
                role,
                content
            )
            VALUES (?, ?, ?)
        """, (conversation_id, role, content))


def obtener_memorias(limite=50):
    with conectar_db() as conn:
        filas = conn.execute("""
            SELECT id, category, content, created_at
            FROM memorias
            ORDER BY id DESC
            LIMIT ?
        """, (limite,)).fetchall()

    return [dict(fila) for fila in filas]


def guardar_memoria(content, category="general"):
    with conectar_db() as conn:
        cursor = conn.execute("""
            INSERT INTO memorias (category, content)
            VALUES (?, ?)
        """, (content, category))

        return cursor.lastrowid


def borrar_memoria(memory_id):
    with conectar_db() as conn:
        cursor = conn.execute(
            "DELETE FROM memorias WHERE id = ?",
            (memory_id,)
        )
        return cursor.rowcount > 0


def borrar_todas_las_memorias():
    with conectar_db() as conn:
        conn.execute("DELETE FROM memorias")


def listar_conversaciones():
    with conectar_db() as conn:
        filas = conn.execute("""
            SELECT
                conversation_id,
                MAX(created_at) AS updated_at,
                COUNT(*) AS message_count
            FROM mensajes
            GROUP BY conversation_id
            ORDER BY MAX(id) DESC
        """).fetchall()

    return [dict(fila) for fila in filas]


def borrar_conversacion(conversation_id):
    with conectar_db() as conn:
        cursor = conn.execute(
            "DELETE FROM mensajes WHERE conversation_id = ?",
            (conversation_id,)
        )
        return cursor.rowcount > 0


# ============================================================
# 5. SERVIDOR FASTAPI
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_db()
    yield


app = FastAPI(
    title="Aranza Personal AI",
    description="Asistente personal con memoria controlada.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"]
)


# ============================================================
# 6. MODELOS DE DATOS
# ============================================================

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=8000
    )

    conversation_id: str = Field(
        default="default",
        min_length=1,
        max_length=100
    )


class MemoryRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=2000
    )

    category: str = Field(
        default="general",
        min_length=1,
        max_length=50
    )


# ============================================================
# 7. ENDPOINT PRINCIPAL DE CHAT
# ============================================================

@app.get("/")
async def mostrar_pagina_principal():
    return FileResponse("index.html")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):

    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Configura GROQ_API_KEY antes de iniciar Aranza."
        )

    mensaje_usuario = request.message.strip()

    if not mensaje_usuario:
        raise HTTPException(
            status_code=422,
            detail="El mensaje no puede estar vacío."
        )

    try:
        historial = obtener_historial(
            request.conversation_id
        )

        memorias = obtener_memorias()

        mensajes = [
            {
                "role": "system",
                "content": construir_prompt(memorias)
            }
        ]

        mensajes.extend(
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in historial
        )

        mensajes.append({
            "role": "user",
            "content": mensaje_usuario
        })

        respuesta_modelo = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=mensajes,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

        respuesta = (
            respuesta_modelo.choices[0].message.content
            or ""
        )

        guardar_mensaje(
            request.conversation_id,
            "user",
            mensaje_usuario
        )

        guardar_mensaje(
            request.conversation_id,
            "assistant",
            respuesta
        )

        return {
            "response": respuesta,
            "conversation_id": request.conversation_id
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Error al generar una respuesta de Aranza."
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "No se pudo generar la respuesta. "
                "Revisa la conexión, la clave API y el modelo configurado."
            )
        )


# ============================================================
# 8. ADMINISTRACIÓN DE MEMORIA
# ============================================================

@app.get("/memory")
async def listar_memorias():
    return {
        "memories": obtener_memorias(limite=200)
    }


@app.post("/memory")
async def crear_memoria(request: MemoryRequest):
    memory_id = guardar_memoria(
        request.content.strip(),
        request.category.strip() or "general"
    )

    return {
        "id": memory_id,
        "saved": True
    }


@app.delete("/memory/{memory_id}")
async def eliminar_memoria(memory_id: int):
    eliminado = borrar_memoria(memory_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ese recuerdo."
        )

    return {
        "deleted": True,
        "id": memory_id
    }


@app.delete("/memory")
async def eliminar_todas_las_memorias():
    borrar_todas_las_memorias()

    return {
        "deleted_all_memories": True
    }


# ============================================================
# 9. ADMINISTRACIÓN DEL HISTORIAL
# ============================================================

@app.get("/conversations")
async def conversaciones():
    return {
        "conversations": listar_conversaciones()
    }


@app.delete("/conversations/{conversation_id}")
async def eliminar_conversacion(conversation_id: str):
    eliminado = borrar_conversacion(conversation_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="No se encontró esa conversación."
        )

    return {
        "deleted": True,
        "conversation_id": conversation_id
    }


# ============================================================
# 10. COMPROBACIÓN DEL SERVIDOR
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": GROQ_MODEL,
        "provider_configured": client is not None
    }
