# almacenamiento/guardar.py
import json
from datetime import datetime, timezone
from pathlib import Path

# Configuración de rutas relativas al archivo actual
_BASE_DIR = Path(__file__).parent / "resultados"
CARPETA_TXT = _BASE_DIR / "txt"
CARPETA_JSON = _BASE_DIR / "json"

def _crear_carpetas():
    """Asegura que existan las subcarpetas de resultados."""
    CARPETA_TXT.mkdir(parents=True, exist_ok=True)
    CARPETA_JSON.mkdir(parents=True, exist_ok=True)

def guardar_resultado(texto_entrada: str, resultados: dict) -> dict:
    """
    Guarda el texto original en TXT y el análisis en JSON.
    Devuelve un diccionario con las rutas de los archivos creados.
    """
    _crear_carpetas()
    
    # Usamos UTC para evitar problemas de zona horaria
    timestamp = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d_%H%M%S')
    nombre_base = f'analisis_{timestamp}'
    
    ruta_txt = CARPETA_TXT / f"{nombre_base}.txt"
    ruta_json = CARPETA_JSON / f"{nombre_base}.json"

    # 1. Guardar el texto de entrada
    ruta_txt.write_text(texto_entrada, encoding="utf-8")

    # 2. Guardar los resultados en JSON
    try:
        ruta_json.write_text(
            json.dumps(resultados, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except TypeError as exc:
        raise TypeError(f"Error al serializar JSON: {exc}")

    return {
        'txt': str(ruta_txt),
        'json': str(ruta_json)
    }