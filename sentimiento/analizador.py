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
    cliente: OpenAI,
    prompt_sistema: str,
    texto_usuario: str,
    modelo: str = MODELO_DEFAULT,
) -> str:
    """
    Realiza una llamada a la API de chat completions y devuelve el contenido
    de la respuesta como cadena de texto.

    Args:
        cliente: instancia de OpenAI ya configurada.
        prompt_sistema: instrucción de sistema para el modelo.
        texto_usuario: texto que el usuario quiere analizar.
        modelo: identificador del modelo a usar.

    Returns:
        Contenido textual de la respuesta del modelo.

    Raises:
        RuntimeError: si la llamada a la API falla.
    """
    try:
        response = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_usuario},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        raise RuntimeError(f"Error en la llamada a la API de OpenAI: {exc}") from exc


# ── Análisis básico ───────────────────────────────────────────────────────────

def analizar_basico(cliente: OpenAI, texto: str) -> ResultadoBasico:
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

def analizar_intermedio(cliente: OpenAI, texto: str) -> ResultadoIntermedio:
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

def analizar_avanzado(cliente: OpenAI, texto: str) -> ResultadoAvanzado:
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
