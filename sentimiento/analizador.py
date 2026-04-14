# ============================================
# sentimiento/analizador.py
# ============================================

import json
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
    return texto[:limite] + "..." if len(texto) > limite else texto


def _llamar_api(
    cliente,  # <-- QUITADO : OpenAI
    prompt_sistema: str,
    texto_usuario: str,
    modelo: str = MODELO_DEFAULT,
) -> str:
    """
    Realiza una llamada al modelo local (Transformers) y devuelve el texto.
    """
    try:
        # Combinamos las instrucciones y el texto para el modelo local
        prompt_completo = f"{prompt_sistema}\n{texto_usuario}"
        
        # El pipeline de transformers se llama como una función directamente
        resultado = cliente(prompt_completo, max_new_tokens=256, truncation=True)
        
        # Extraemos el texto de la estructura [{'generated_text': '...'}]
        return resultado[0]['generated_text'].strip()
        
    except Exception as exc:
        raise RuntimeError(f"Error en la ejecución del modelo local: {exc}") from exc


# ── Análisis básico ───────────────────────────────────────────────────────────

def analizar_basico(cliente, texto: str) -> ResultadoBasico:
    respuesta_raw = _llamar_api(cliente, PROMPT_BASICO, texto)
    sentimiento = respuesta_raw.lower()

    if "positivo" in sentimiento:
        return ResultadoBasico(nivel="básico", sentimiento="positivo", texto_original=_truncar(texto))
    if "negativo" in sentimiento:
        return ResultadoBasico(nivel="básico", sentimiento="negativo", texto_original=_truncar(texto))
    
    return ResultadoBasico(nivel="básico", sentimiento="neutro", texto_original=_truncar(texto))


# ── Análisis intermedio ───────────────────────────────────────────────────────

def analizar_intermedio(cliente, texto: str) -> ResultadoIntermedio: 
    respuesta_raw = _llamar_api(cliente, PROMPT_INTERMEDIO, texto)

    try:
        datos: dict = json.loads(respuesta_raw)
        datos["nivel"] = "intermedio"
        datos["texto_original"] = _truncar(texto)
        return ResultadoIntermedio(**datos)
    except (json.JSONDecodeError, TypeError) as exc:
        return ResultadoIntermedio(
            nivel="intermedio",
            error=f"No se pudo parsear la respuesta JSON: {exc}",
            respuesta_raw=respuesta_raw,
        )


# ── Análisis avanzado ─────────────────────────────────────────────────────────

def analizar_avanzado(cliente, texto: str) -> ResultadoAvanzado:
    respuesta_raw = _llamar_api(cliente, PROMPT_AVANZADO, texto)

    try:
        datos: dict = json.loads(respuesta_raw)
        datos["nivel"] = "avanzado"
        datos["texto_original"] = _truncar(texto)
        return ResultadoAvanzado(**datos)
    except (json.JSONDecodeError, TypeError) as exc:
        return ResultadoAvanzado(
            nivel="avanzado",
            error=f"No se pudo parsear la respuesta JSON: {exc}",
            respuesta_raw=respuesta_raw,
        )
