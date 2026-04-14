# ============================================
# sentimiento/multitexto.py
# Responsabilidad única: orquestar el análisis de listas de textos
# y calcular estadísticas agregadas sobre los resultados.
# ============================================

from typing import TypedDict
from transformers import pipeline

from sentimiento.analizador import analizar_intermedio
from sentimiento.niveles import ResultadoIntermedio


# ── Modelos de datos ──────────────────────────────────────────────────────────

class Estadisticas(TypedDict):
    """Métricas agregadas sobre un conjunto de resultados de sentimiento."""
    total: int
    positivos: int
    negativos: int
    neutrales: int
    polaridad_promedio: float


class ResultadoMultiple(TypedDict):
    """Contenedor del análisis múltiple: resultados individuales + estadísticas."""
    resultados_individuales: list[ResultadoIntermedio]
    estadisticas: Estadisticas


# ── Función principal ─────────────────────────────────────────────────────────

def analizar_multitexto(cliente, textos: list[str]) -> ResultadoMultiple:
    """
    Analiza una lista de textos en nivel intermedio.
    
    Args:
        cliente: instancia del modelo local (pipeline de transformers).
        textos: lista de cadenas a analizar.
    """
    if not textos:
        raise ValueError("La lista de textos no puede estar vacía.")

    resultados: list[ResultadoIntermedio] = []

    for texto in textos:
        # Aquí se inyecta el cliente local
        resultado = analizar_intermedio(cliente, texto)
        resultados.append(resultado)

    estadisticas = _calcular_estadisticas(resultados)

    return ResultadoMultiple(
        resultados_individuales=resultados,
        estadisticas=estadisticas,
    )


# ── Función auxiliar privada ──────────────────────────────────────────────────

def _calcular_estadisticas(resultados: list[ResultadoIntermedio]) -> Estadisticas:
    """
    Calcula métricas agregadas a partir de una lista de resultados intermedios.

    Args:
        resultados: lista de ResultadoIntermedio.

    Returns:
        Estadisticas con conteos y polaridad promedio.
    """
    polaridades: list[float] = [
        r["polaridad"]
        for r in resultados
        if isinstance(r.get("polaridad"), (int, float))
    ]

    return Estadisticas(
        total=len(resultados),
        positivos=sum(1 for r in resultados if r.get("sentimiento") == "positivo"),
        negativos=sum(1 for r in resultados if r.get("sentimiento") == "negativo"),
        neutrales=sum(1 for r in resultados if r.get("sentimiento") == "neutral"),
        polaridad_promedio=round(sum(polaridades) / len(polaridades), 4)
        if polaridades
        else 0.0,
    )
