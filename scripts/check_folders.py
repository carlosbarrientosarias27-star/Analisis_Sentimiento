# scripts/check_folders.py
import json
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
RAIZ = Path(__file__).parent.parent  

# Carpetas críticas que deben existir tras la ejecución
CARPETAS_REQUERIDAS = [
    RAIZ / "almacenamiento" / "resultados" / "json",
    RAIZ / "almacenamiento" / "resultados" / "txt",
]

CARPETA_JSON_RESULTADOS = RAIZ / "almacenamiento" / "resultados" / "json"
MIN_ARCHIVOS_JSON = 1  

# ── Helpers ───────────────────────────────────────────────────────────────────
def ok(mensaje: str) -> None:
    print(f"  [OK] {mensaje}")

def error(mensaje: str) -> None:
    print(f"  [X] {mensaje}", file=sys.stderr)

# ── Verificaciones ────────────────────────────────────────────────────────────
def verificar_carpetas_existen() -> bool:
    """Comprueba que las subcarpetas json/ y txt/ existen."""
    print("\n[1] Comprobando existencia de subcarpetas de resultados...")
    todo_ok = True
    for carpeta in CARPETAS_REQUERIDAS:
        if carpeta.is_dir():
            ok(f"Carpeta activa: {carpeta.relative_to(RAIZ)}")
        else:
            error(f"Falta carpeta crítica: {carpeta.relative_to(RAIZ)}")
            todo_ok = False
    return todo_ok

def verificar_archivos_json() -> bool:
    """Verifica la presencia de al menos un análisis generado."""
    print(f"\n[2] Buscando archivos en {CARPETA_JSON_RESULTADOS.relative_to(RAIZ)}...")
    
    if not CARPETA_JSON_RESULTADOS.is_dir():
        return False

    # Buscamos archivos .json reales (omitimos .gitkeep)
    jsons = [f for f in CARPETA_JSON_RESULTADOS.glob("*.json") if f.name != ".gitkeep"]

    if len(jsons) >= MIN_ARCHIVOS_JSON:
        ok(f"Encontrados {len(jsons)} resultados de análisis.")
        return True
    else:
        error(f"No se detectaron archivos JSON (se requiere al menos {MIN_ARCHIVOS_JSON}).")
        return False

def verificar_json_validos() -> bool:
    """Valida que los JSON generados no estén corruptos."""
    print("\n[3] Validando integridad de los archivos JSON...")
    jsons = [f for f in CARPETA_JSON_RESULTADOS.glob("*.json") if f.name != ".gitkeep"]
    todo_ok = True

    for ruta in jsons:
        try:
            contenido = json.loads(ruta.read_text(encoding="utf-8"))
            # El archivo debe ser un diccionario (objeto) para ser válido en nuestra app
            if isinstance(contenido, dict):
                ok(f"{ruta.name}: Estructura válida.")
            else:
                error(f"{ruta.name}: Contenido no es un objeto JSON.")
                todo_ok = False
        except json.JSONDecodeError as exc:
            error(f"{ruta.name}: Error de formato — {exc}")
            todo_ok = False
    return todo_ok

# ── Punto de entrada ──────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  CHECK_FOLDERS: VALIDACIÓN DE PIPELINE DE SENTIMIENTO")
    print("=" * 60)

    checks = [
        verificar_carpetas_existen(),
        verificar_archivos_json(),
        verificar_json_validos(),
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("  ESTADO GLOBAL: PASADO [OK]")
        sys.exit(0)
    else:
        print(f"  ESTADO GLOBAL: FALLIDO [{checks.count(False)} error(es)]")
        sys.exit(1)

if __name__ == "__main__":
    main()