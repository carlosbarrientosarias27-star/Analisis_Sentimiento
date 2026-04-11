# ============================================
# almacenamiento/guardar.py
# Responsabilidad única: serializar y persistir resultados en disco.
# Usa pathlib para todas las rutas; nunca asume un directorio de trabajo.
# ============================================

import json
from datetime import datetime, timezone
from pathlib import Path


# Directorio de resultados relativo al paquete de almacenamiento
_DIRECTORIO_RESULTADOS: Path = Path(__file__).parent / "resultados"


def _asegurar_directorio(directorio: Path) -> None:
    """
    Crea el directorio si no existe (incluyendo padres).

    Args:
        directorio: ruta del directorio a verificar/crear.
    """
    directorio.mkdir(parents=True, exist_ok=True)


def _nombre_archivo_timestamp(prefijo: str) -> str:
    """
    Genera un nombre de archivo único basado en el prefijo y la fecha/hora UTC.

    Args:
        prefijo: etiqueta descriptiva (p. ej. 'basico', 'multiple').

    Returns:
        Nombre de archivo con formato '<prefijo>_YYYYMMDD_HHMMSS.json'.
    """
    marca = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefijo}_{marca}.json"


def guardar_resultado(
    resultado: dict,
    prefijo: str = "resultado",
    directorio: Path | None = None,
) -> Path:
    """
    Serializa un resultado de análisis en un archivo JSON con marca de tiempo.

    Args:
        resultado: diccionario con los datos a persistir.
        prefijo: etiqueta para el nombre del archivo.
        directorio: ruta opcional donde guardar; usa el directorio por defecto si es None.

    Returns:
        Path del archivo creado.

    Raises:
        OSError: si no se puede escribir el archivo.
        TypeError: si el resultado contiene tipos no serializables.
    """
    destino: Path = directorio or _DIRECTORIO_RESULTADOS
    _asegurar_directorio(destino)

    nombre = _nombre_archivo_timestamp(prefijo)
    ruta_archivo: Path = destino / nombre

    try:
        ruta_archivo.write_text(
            json.dumps(resultado, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except TypeError as exc:
        raise TypeError(
            f"El resultado contiene tipos no serializables a JSON: {exc}"
        ) from exc

    return ruta_archivo


def guardar_multiples(
    resultados: list[dict],
    prefijo: str = "multiple",
    directorio: Path | None = None,
) -> Path:
    """
    Serializa una lista de resultados en un único archivo JSON.

    Args:
        resultados: lista de diccionarios a persistir.
        prefijo: etiqueta para el nombre del archivo.
        directorio: ruta opcional donde guardar.

    Returns:
        Path del archivo creado.
    """
    return guardar_resultado(
        resultado={"resultados": resultados},
        prefijo=prefijo,
        directorio=directorio,
    )
