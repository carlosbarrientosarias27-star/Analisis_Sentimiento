# almacenamiento/leer.py
import json
from pathlib import Path

# Definimos las rutas de forma independiente para evitar acoplamiento circular
_BASE_DIR = Path(__file__).parent / "resultados"
CARPETA_TXT = _BASE_DIR / "txt"
CARPETA_JSON = _BASE_DIR / "json"

def listar_analisis() -> list[str]:
    """
    Lista los nombres (stem) de todos los análisis guardados en JSON,
    ordenados del más reciente al más antiguo.
    """
    if not CARPETA_JSON.exists():
        return []

    # Buscamos archivos .json y los ordenamos por fecha de modificación (mtime)
    archivos = sorted(
        CARPETA_JSON.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Devolvemos solo el nombre sin la extensión .json
    return [f.stem for f in archivos]

def leer_json(nombre: str) -> dict:
    """
    Lee un análisis guardado y lo devuelve como diccionario.
    
    Args:
        nombre: El nombre base del archivo (ej: 'analisis_2024-05-20_120000')
    """
    ruta = CARPETA_JSON / f"{nombre}.json"
    
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el análisis JSON: {nombre}")

    contenido = ruta.read_text(encoding="utf-8")
    return json.loads(contenido)

def leer_txt(nombre: str) -> str:
    """
    Lee el informe original o texto de entrada guardado en TXT.
    
    Args:
        nombre: El nombre base del archivo.
    """
    ruta = CARPETA_TXT / f"{nombre}.txt"
    
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el informe TXT: {nombre}")

    return ruta.read_text(encoding="utf-8")

def leer_par_completo(nombre: str) -> tuple[str, dict]:
    """
    Utilidad para recuperar ambos archivos (TXT y JSON) de una sola vez.
    """
    return leer_txt(nombre), leer_json(nombre)