# ============================================
# sentimiento/niveles.py
# Responsabilidad única: procesar los resultados de la pipeline local
# y estructurarlos en los modelos de datos (TypedDict).
# ============================================

from typing import TypedDict

# --- CONFIGURACIÓN ---
MODELO_DEFAULT = "finiteautomata/beto-sentiment-analysis"
PROMPT_BASICO = "Clasifica el sentimiento: positivo, negativo o neutro."
PROMPT_INTERMEDIO = "Responde en JSON con: polaridad (float), emociones (lista), intensidad (str)."
PROMPT_AVANZADO = "Responde en JSON con: fragmentos (lista), justificacion (str), tonalidad (str), recomendacion (str)."

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

# ── Funciones de Análisis ─────────────────────────────────────────────────────

# Mapeo interno para traducir las etiquetas del modelo RoBERTuito
MAPPING_SENTIMIENTO = {"POS": "positivo", "NEG": "negativo", "NEU": "neutral"}

def basico(texto: str, client) -> ResultadoBasico:
    """
    Usa la pipeline local para un análisis rápido.
    client: objeto pipeline de Transformers devuelto por crear_cliente()
    """
    resultado = client(texto)[0]
    sentimiento = MAPPING_SENTIMIENTO.get(resultado['label'], "neutral")
    
    return {
        "nivel": "básico",
        "sentimiento": sentimiento,
        "texto_original": texto
    }

def intermedio(texto: str, client) -> ResultadoIntermedio:
    """
    Extrae la confianza del modelo como polaridad y define intensidad.
    """
    resultado = client(texto)[0]
    sentimiento = MAPPING_SENTIMIENTO.get(resultado['label'], "neutral")
    
    # Calculamos polaridad: POS es positivo, NEG es negativo
    score = resultado['score']
    polaridad = round(score if resultado['label'] == "POS" else -score, 2)
    
    return {
        "nivel": "intermedio",
        "sentimiento": sentimiento,
        "polaridad": polaridad,
        "emociones": {"alegria": 0.0, "tristeza": 0.0, "enojo": 0.0, "sorpresa": 0.0, "miedo": 0.0},
        "intensidad": "alta" if score > 0.8 else "media",
        "texto_original": texto
    }

def avanzado(texto: str, client) -> ResultadoAvanzado:
    """
    Versión avanzada adaptada a modelos de clasificación local.
    Nota: Los modelos locales no generan texto (justificaciones), solo clasifican.
    """
    res_int = intermedio(texto, client)
    
    return {
        "nivel": "avanzado",
        "sentimiento_global": res_int["sentimiento"],
        "polaridad": res_int["polaridad"],
        "fragmentos": [],
        "justificacion": f"Análisis de confianza ({res_int['polaridad']}) mediante RoBERTuito.",
        "tonalidad": "No disponible (Modelo Local)",
        "recomendacion": "N/A",
        "texto_original": texto
    }
