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
    print(f"  ✓  {mensaje}")


def error(mensaje: str) -> None:
    print(f"  ✗  {mensaje}", file=sys.stderr)


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
    """Comprueba que hay al menos MIN_ARCHIVOS_JSON archivos .json en resultados/."""
    print("\n[2] Comprobando archivos JSON en almacenamiento/resultados/...")

    if not CARPETA_RESULTADOS.is_dir():
        error("La carpeta de resultados no existe, no se pueden comprobar archivos.")
        return False

    jsons = sorted(CARPETA_RESULTADOS.glob("*.json"))

    if len(jsons) >= MIN_ARCHIVOS_JSON:
        ok(f"Se encontraron {len(jsons)} archivo(s) JSON")
        for f in jsons:
            ok(f"  → {f.name}")
    else:
        error(
            f"Se esperaba al menos {MIN_ARCHIVOS_JSON} archivo(s) JSON "
            f"pero se encontraron {len(jsons)}"
        )
        return False

    return True


def verificar_json_validos() -> bool:
    """Comprueba que cada archivo .json es JSON válido y tiene la clave 'nivel'."""
    print("\n[3] Validando contenido de los archivos JSON...")

    if not CARPETA_RESULTADOS.is_dir():
        return False

    jsons = sorted(CARPETA_RESULTADOS.glob("*.json"))
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
                    ok(f"{ruta.name} → nivel={entrada['nivel']}")

        except json.JSONDecodeError as exc:
            error(f"{ruta.name}: JSON malformado — {exc}")
            todo_ok = False

    return todo_ok


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 55)
    print("  check_folders.py — verificación de resultados")
    print("=" * 55)

    checks = [
        verificar_carpetas_existen(),
        verificar_archivos_json(),
        verificar_json_validos(),
    ]

    print("\n" + "=" * 55)
    if all(checks):
        print("  RESULTADO: todas las verificaciones pasaron ✓")
        print("=" * 55)
        sys.exit(0)
    else:
        fallos = checks.count(False)
        print(f"  RESULTADO: {fallos} verificación(es) fallaron ✗")
        print("=" * 55)
        sys.exit(1)


if __name__ == "__main__":
    main()