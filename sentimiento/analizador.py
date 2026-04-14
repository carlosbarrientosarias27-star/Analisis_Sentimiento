# ============================================
# sentimiento/analizador.py
# Responsabilidad única: ejecutar las llamadas a la API de OpenAI
# y mapear la respuesta a los modelos de datos definidos en niveles.py.
# Recibe el cliente como dependencia inyectada (no lo crea).
# ============================================

import json
from transformers import pipeline

from sentimiento.niveles import (
    MODELO_DEFAULT,
    PROMPT_BASICO,
    PROMPT_INTERMEDIO,
    PROMPT_AVANZADO,
    ResultadoBasico,
    ResultadoIntermedio,
    ResultadoAvanzado,
)


def _truncar(texto: str, limite: int = 100) -> str:
    """
    Trunca el texto al límite indicado y añade '...' si fue recortado.

    Args:
        texto: cadena original.
        limite: número máximo de caracteres.

    Returns:
        Cadena truncada.
    """
    return texto[:limite] + "..." if len(texto) > limite else texto


def _llamar_api(
    cliente,
    prompt_sistema: str,
    texto_usuario: str,
    modelo: str = MODELO_DEFAULT,
) -> str:
    """
    Realiza una llamada al modelo local (Transformers) y devuelve el texto.
    """
    try:
        # Combinamos las instrucciones y el texto para el modelo local
        prompt_completo = f"{prompt_sistema}\n\nTexto: {texto_usuario}"
        
        # El pipeline de transformers se llama como una función directamente
        # max_new_tokens controla el largo de la respuesta
        resultado = cliente(prompt_completo, max_new_tokens=256, truncation=True)
        
        # Extraemos el texto de la estructura [{'generated_text': '...'}]
        return resultado[0]['generated_text'].strip()
        
    except Exception as exc:
        raise RuntimeError(f"Error en la ejecución del modelo local: {exc}") from exc

# ── Análisis básico ───────────────────────────────────────────────────────────

def analizar_basico(cliente, texto: str) -> ResultadoBasico:
    """
    Analiza el sentimiento del texto a nivel básico (solo categoría).

    Args:
        cliente: instancia de OpenAI.
        texto: texto a analizar.

    Returns:
        ResultadoBasico con la categoría de sentimiento.
    """
    respuesta = _llamar_api(cliente, PROMPT_BASICO, texto)

    return ResultadoBasico(
        nivel="básico",
        sentimiento=respuesta.lower(),
        texto_original=_truncar(texto),
    )


# ── Análisis intermedio ───────────────────────────────────────────────────────

def analizar_intermedio(cliente, texto: str) -> ResultadoIntermedio:
    """
    Analiza el sentimiento del texto a nivel intermedio:
    polaridad, emociones e intensidad.

    Args:
        cliente: instancia de OpenAI.
        texto: texto a analizar.

    Returns:
        ResultadoIntermedio con los campos enriquecidos,
        o un dict de error si la respuesta no es JSON válido.
    """
    respuesta_raw = _llamar_api(cliente, PROMPT_INTERMEDIO, texto)

    try:
        datos: dict = json.loads(respuesta_raw)
        datos["nivel"] = "intermedio"  # <--- AQUÍ VA PARA EL ÉXITO
        datos["texto_original"] = _truncar(texto)
        return ResultadoIntermedio(**datos)  # type: ignore[arg-type]
    except (json.JSONDecodeError, TypeError) as exc:
        return ResultadoIntermedio(
            nivel="intermedio",
            error=f"No se pudo parsear la respuesta JSON: {exc}",
            respuesta_raw=respuesta_raw,
        )


# ── Análisis avanzado ─────────────────────────────────────────────────────────

def analizar_avanzado(cliente, texto: str) -> ResultadoAvanzado:
    """
    Analiza el sentimiento del texto a nivel avanzado:
    fragmentos, justificación, tonalidad y recomendación.

    Args:
        cliente: instancia de OpenAI.
        texto: texto a analizar.

    Returns:
        ResultadoAvanzado con el análisis en profundidad,
        o un dict de error si la respuesta no es JSON válido.
    """
    respuesta_raw = _llamar_api(cliente, PROMPT_AVANZADO, texto)

    try:
        datos: dict = json.loads(respuesta_raw)
        datos["nivel"] = "avanzado"  # <--- CRÍTICO
        datos["texto_original"] = _truncar(texto)
        return ResultadoAvanzado(**datos)  # type: ignore[arg-type]
    except (json.JSONDecodeError, TypeError) as exc:
        return ResultadoAvanzado(
            nivel="avanzado",
            error=f"No se pudo parsear la respuesta JSON: {exc}",
            respuesta_raw=respuesta_raw,
        )
