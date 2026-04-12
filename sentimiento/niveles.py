# ============================================
# sentimiento/niveles.py
# Responsabilidad única: definir los prompts de sistema y los modelos
# de datos (TypedDict) para los tres niveles de análisis.
# No contiene lógica de red ni de I/O.
# ============================================


import json
from typing import TypedDict


# ── Modelos de datos ──────────────────────────────────────────────────────────

class ResultadoBasico(TypedDict):
    """Resultado del análisis básico: solo la categoría de sentimiento."""
    nivel: str
    sentimiento: str          # "positivo" | "negativo" | "neutral"
    texto_original: str


class Emociones(TypedDict):
    """Puntuaciones por emoción (0-1)."""
    alegria: float
    tristeza: float
    enojo: float
    sorpresa: float
    miedo: float


class ResultadoIntermedio(TypedDict, total=False):
    """Resultado del análisis intermedio: polaridad, emociones e intensidad."""
    nivel: str
    sentimiento: str
    polaridad: float          # -1.0 .. +1.0
    emociones: Emociones
    intensidad: str           # "baja" | "media" | "alta"
    texto_original: str
    error: str
    respuesta_raw: str


class Fragmento(TypedDict):
    """Un fragmento de texto con su sentimiento individual."""
    texto: str
    sentimiento_individual: str


class ResultadoAvanzado(TypedDict, total=False):
    """Resultado del análisis avanzado: justificación, tonalidad y recomendación."""
    nivel: str
    sentimiento_global: str
    polaridad: float
    fragmentos: list[Fragmento]
    justificacion: str
    tonalidad: str
    recomendacion: str
    texto_original: str
    error: str
    respuesta_raw: str


# ── Prompts de sistema ────────────────────────────────────────────────────────

# Se definen como constantes de módulo (sin estado, sin efectos secundarios).

PROMPT_BASICO: str = (
    "Analiza el sentimiento del texto. "
    "Responde SOLO con una palabra: positivo, negativo o neutral."
)

PROMPT_INTERMEDIO: str = """
Analiza el sentimiento del texto.
Responde ÚNICAMENTE en formato JSON válido con estas claves:
- sentimiento: "positivo", "negativo" o "neutral"
- polaridad: número entre -1 (muy negativo) y +1 (muy positivo)
- emociones: objeto con puntuaciones 0-1 para alegria, tristeza, enojo, sorpresa, miedo
- intensidad: "baja", "media" o "alta"
No incluyas texto adicional fuera del JSON.
""".strip()

PROMPT_AVANZADO: str = """
Analiza el sentimiento del texto en profundidad.
Responde ÚNICAMENTE en formato JSON válido con estas claves:
- sentimiento_global: "positivo", "negativo" o "neutral"
- polaridad: número entre -1 y +1
- fragmentos: lista de objetos {"texto": "...", "sentimiento_individual": "..."}
- justificacion: explicación del análisis
- tonalidad: "formal", "coloquial", "agresivo", "entusiasta", etc.
- recomendacion: qué acción tomar según el sentimiento detectado
No incluyas texto adicional fuera del JSON.
""".strip()


# ── Constante de modelo ───────────────────────────────────────────────────────

MODELO_DEFAULT: str = "gpt-4o-mini"

# ── Funciones de Análisis ─────────────────────────────────────────────────────

def basico(texto: str, client) -> ResultadoBasico:
    respuesta = client.chat.completions.create(
        model=MODELO_DEFAULT,
        messages=[
            {"role": "system", "content": PROMPT_BASICO},
            {"role": "user", "content": texto}
        ]
    )
    sentimiento = respuesta.choices[0].message.content.strip().lower()
    return {
        "nivel": "básico",
        "sentimiento": sentimiento,
        "texto_original": texto
    }

def intermedio(texto: str, client) -> ResultadoIntermedio:
    respuesta = client.chat.completions.create(
        model=MODELO_DEFAULT,
        messages=[
            {"role": "system", "content": PROMPT_INTERMEDIO},
            {"role": "user", "content": texto}
        ],
        response_format={"type": "json_object"}
    )
    datos = json.loads(respuesta.choices[0].message.content)
    datos.update({"nivel": "intermedio", "texto_original": texto})
    return datos

def avanzado(texto: str, client) -> ResultadoAvanzado:
    respuesta = client.chat.completions.create(
        model=MODELO_DEFAULT,
        messages=[
            {"role": "system", "content": PROMPT_AVANZADO},
            {"role": "user", "content": texto}
        ],
        response_format={"type": "json_object"}
    )
    datos = json.loads(respuesta.choices[0].message.content)
    datos.update({"nivel": "avanzado", "texto_original": texto})
    return datos
