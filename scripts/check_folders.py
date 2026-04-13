# ============================================
# scripts/check_folders.py
# Verifica que las carpetas y archivos de resultados
# existen y son válidos tras ejecutar el pipeline.
# Usado en GitHub Actions — sale con código 1 si algo falla.
# ============================================

import json
import sys
from pathlib import Path


# ── Configuración ─────────────────────────────────────────────────────────────

RAIZ = Path(__file__).parent.parent  # raíz del proyecto

CARPETAS_REQUERIDAS = [
    RAIZ / "almacenamiento",
    RAIZ / "almacenamiento" / "resultados",
]

CARPETA_RESULTADOS = RAIZ / "almacenamiento" / "resultados"

MIN_ARCHIVOS_JSON = 1  # al menos un resultado debe haberse generado


# ── Helpers ───────────────────────────────────────────────────────────────────

def ok(mensaje: str) -> None:
    print(f"  [OK] {mensaje}")


def error(mensaje: str) -> None:
    print(f"  [X] {mensaje}", file=sys.stderr)


# ── Verificaciones ────────────────────────────────────────────────────────────

def verificar_carpetas_existen() -> bool:
    """Comprueba que todas las carpetas requeridas existen."""
    print("\n[1] Comprobando existencia de carpetas...")
    todo_ok = True
    for carpeta in CARPETAS_REQUERIDAS:
        if carpeta.is_dir():
            ok(f"{carpeta.relative_to(RAIZ)}")
        else:
            error(f"Carpeta no encontrada: {carpeta.relative_to(RAIZ)}")
            todo_ok = False
    return todo_ok


def verificar_archivos_json() -> bool:
    """Comprueba archivos .json buscando ahora en la subcarpeta correcta."""
    print("\n[2] Comprobando archivos JSON en almacenamiento/resultados/json/...")

    # Apuntamos a la nueva subcarpeta de JSONs
    carpeta_json = CARPETA_RESULTADOS / "json"
    
    if not carpeta_json.is_dir():
        error(f"La carpeta {carpeta_json.relative_to(RAIZ)} no existe.")
        return False

    # Buscamos archivos .json (excluyendo el .gitkeep)
    jsons = [f for f in carpeta_json.glob("*.json") if f.name != ".gitkeep"]

    if len(jsons) >= MIN_ARCHIVOS_JSON:
        ok(f"Se encontraron {len(jsons)} archivo(s) JSON")
        return True
    else:
        error(f"Se esperaba al menos {MIN_ARCHIVOS_JSON} JSONs pero se encontraron {len(jsons)}")
        return False

def verificar_json_validos() -> bool:
    """Valida el contenido buscando en la subcarpeta json/."""
    print("\n[3] Validando contenido de los archivos JSON...")
    
    carpeta_json = CARPETA_RESULTADOS / "json"
    jsons = [f for f in carpeta_json.glob("*.json") if f.name != ".gitkeep"]
    todo_ok = True

    for ruta in jsons:
        try:
            contenido = json.loads(ruta.read_text(encoding="utf-8"))

            # Soporte para archivos de múltiples resultados (guardar_multiples)
            entradas = (
                contenido.get("resultados", [contenido])
                if isinstance(contenido, dict)
                else [contenido]
            )

            for entrada in entradas:
                if not isinstance(entrada, dict):
                    error(f"{ruta.name}: entrada no es un objeto JSON válido")
                    todo_ok = False
                    continue
                if "nivel" not in entrada:
                    error(f"{ruta.name}: falta el campo 'nivel'")
                    todo_ok = False
                else:
                    ok(f"{ruta.name} -> nivel={entrada['nivel']}")

        except json.JSONDecodeError as exc:
            error(f"{ruta.name}: JSON malformado — {exc}")
            todo_ok = False

    return todo_ok


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 55)
    print("  check_folders.py - verificacion de resultados")
    print("=" * 55)

    checks = [
        verificar_carpetas_existen(),
        verificar_archivos_json(),
        verificar_json_validos(),
    ]

    print("\n" + "=" * 55)
    if all(checks):
        print("  RESULTADO: todas las verificaciones pasaron [OK]")
        print("=" * 55)
        sys.exit(0)
    else:
        fallos = checks.count(False)
        print(f"  RESULTADO: {fallos} verificación(es) fallaron [X]")
        print("=" * 55)
        sys.exit(1)


if __name__ == "__main__":
    main()