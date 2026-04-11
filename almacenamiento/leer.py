# ============================================
# almacenamiento/leer.py
# Responsabilidad única: leer y listar resultados previamente guardados.
# Complementa a guardar.py sin acoplamiento directo con él.
# ============================================

import json
from pathlib import Path


# Mismo directorio por defecto que guardar.py; se define de forma independiente
# para evitar importar guardar.py y crear acoplamiento circular.
_DIRECTORIO_RESULTADOS: Path = Path(__file__).parent / "resultados"


def listar_archivos(directorio: Path | None = None) -> list[Path]:
    """
    Devuelve la lista de archivos JSON en el directorio de resultados,
    ordenados del más reciente al más antiguo.

    Args:
        directorio: ruta opcional; usa el directorio por defecto si es None.

    Returns:
        Lista de Path ordenada por fecha de modificación descendente.
        Lista vacía si el directorio no existe.
    """
    destino: Path = directorio or _DIRECTORIO_RESULTADOS

    if not destino.exists():
        return []

    return sorted(
        destino.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def leer_resultado(ruta: Path) -> dict:
    """
    Lee y deserializa un archivo JSON de resultado.

    Args:
        ruta: Path del archivo a leer.

    Returns:
        Diccionario con los datos del resultado.

    Raises:
        FileNotFoundError: si el archivo no existe.
        json.JSONDecodeError: si el contenido no es JSON válido.
    """
    if not ruta.exists():
        raise FileNotFoundError(f"El archivo no existe: {ruta}")

    contenido = ruta.read_text(encoding="utf-8")
    return json.loads(contenido)


def leer_ultimo(directorio: Path | None = None) -> dict | None:
    """
    Lee el resultado más reciente del directorio.

    Args:
        directorio: ruta opcional; usa el directorio por defecto si es None.

    Returns:
        Diccionario con los datos del resultado más reciente,
        o None si no hay archivos.
    """
    archivos = listar_archivos(directorio)
    if not archivos:
        return None

    return leer_resultado(archivos[0])


def leer_todos(directorio: Path | None = None) -> list[dict]:
    """
    Lee todos los resultados del directorio, del más reciente al más antiguo.

    Args:
        directorio: ruta opcional.

    Returns:
        Lista de diccionarios con todos los resultados.
        Lista vacía si no hay archivos.
    """
    archivos = listar_archivos(directorio)

    resultados: list[dict] = []
    for ruta in archivos:
        try:
            resultados.append(leer_resultado(ruta))
        except (json.JSONDecodeError, OSError):
            # Archivo corrupto o sin permisos: se omite sin detener la ejecución
            continue

    return resultados