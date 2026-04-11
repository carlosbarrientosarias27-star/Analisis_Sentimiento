#!/usr/bin/env python3
# ============================================
# main.py
# Punto de entrada único de la aplicación.
# Responsabilidad: orquestar los módulos, mostrar resultados
# y persistirlos. Sin lógica de negocio propia.
# ============================================

import json
import sys
from pathlib import Path

from sentimiento.cliente import crear_cliente
from sentimiento.analizador import analizar_basico, analizar_intermedio, analizar_avanzado
from sentimiento.multitexto import analizar_multitexto
from almacenamiento.guardar import guardar_resultado, guardar_multiples
from almacenamiento.leer import listar_archivos


# ── Helpers de presentación ───────────────────────────────────────────────────

def _titulo(texto: str) -> None:
    """Imprime un título delimitado por líneas."""
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70)


def _seccion(texto: str) -> None:
    """Imprime un separador de sección."""
    print(f"\n{'─' * 70}")
    print(f"  {texto}")
    print(f"{'─' * 70}")


def _json(datos: dict) -> None:
    """Imprime un diccionario formateado como JSON legible."""
    print(json.dumps(datos, indent=2, ensure_ascii=False))


# ── Demo 1: comparativa de niveles ───────────────────────────────────────────

def demo_niveles(texto: str) -> None:
    """
    Ejecuta los tres niveles de análisis sobre un único texto,
    imprime los resultados y los persiste individualmente.

    Args:
        texto: cadena a analizar.
    """
    _titulo("📊 ANÁLISIS DE SENTIMIENTO — COMPARATIVA DE NIVELES")
    print(f"\n📝 Texto: {texto}\n")

    # Creamos el cliente UNA sola vez y lo pasamos como dependencia
    cliente = crear_cliente()

    # Básico
    _seccion("🔵 NIVEL BÁSICO")
    res_basico = analizar_basico(cliente, texto)
    _json(res_basico)
    ruta = guardar_resultado(res_basico, prefijo="basico")  # type: ignore[arg-type]
    print(f"\n  💾 Guardado en: {ruta}")

    # Intermedio
    _seccion("🟡 NIVEL INTERMEDIO")
    res_intermedio = analizar_intermedio(cliente, texto)
    _json(res_intermedio)  # type: ignore[arg-type]
    ruta = guardar_resultado(res_intermedio, prefijo="intermedio")  # type: ignore[arg-type]
    print(f"\n  💾 Guardado en: {ruta}")

    # Avanzado
    _seccion("🟢 NIVEL AVANZADO")
    res_avanzado = analizar_avanzado(cliente, texto)
    _json(res_avanzado)  # type: ignore[arg-type]
    ruta = guardar_resultado(res_avanzado, prefijo="avanzado")  # type: ignore[arg-type]
    print(f"\n  💾 Guardado en: {ruta}")


# ── Demo 2: análisis de múltiples reseñas ────────────────────────────────────

def demo_multiples(reseñas: list[str]) -> None:
    """
    Analiza un conjunto de reseñas, muestra estadísticas y persiste el resultado.

    Args:
        reseñas: lista de textos a analizar.
    """
    _titulo("📊 ANÁLISIS DE MÚLTIPLES RESEÑAS")

    cliente = crear_cliente()
    resultado = analizar_multitexto(cliente, reseñas)

    stats = resultado["estadisticas"]
    _seccion("📈 ESTADÍSTICAS AGREGADAS")
    print(f"   Total de reseñas : {stats['total']}")
    print(f"   Positivas        : {stats['positivos']}")
    print(f"   Negativas        : {stats['negativos']}")
    print(f"   Neutrales        : {stats['neutrales']}")
    print(f"   Polaridad media  : {stats['polaridad_promedio']:.2f}")

    _seccion("📋 RESEÑAS INDIVIDUALES")
    for i, (reseña, res) in enumerate(
        zip(reseñas, resultado["resultados_individuales"]), start=1
    ):
        sentimiento = res.get("sentimiento", "N/A")
        polaridad = res.get("polaridad", "N/A")
        print(f"\n   [{i}] {reseña}")
        print(f"       → Sentimiento: {sentimiento}  |  Polaridad: {polaridad}")

        emociones = res.get("emociones")
        if emociones:
            emocion_max = max(emociones.items(), key=lambda x: x[1])
            print(f"       → Emoción principal: {emocion_max[0]} ({emocion_max[1]:.2f})")

    ruta = guardar_multiples(resultado["resultados_individuales"], prefijo="multiples")  # type: ignore[arg-type]
    print(f"\n  💾 Guardado en: {ruta}")


# ── Demo 3: lectura de archivos previos ───────────────────────────────────────

def demo_historial() -> None:
    """Muestra los archivos de resultados existentes en el directorio de almacenamiento."""
    _titulo("🗂  HISTORIAL DE RESULTADOS GUARDADOS")

    archivos = listar_archivos()
    if not archivos:
        print("\n  (No hay resultados previos guardados.)")
        return

    for ruta in archivos:
        print(f"  • {ruta.name}  ({ruta.stat().st_size} bytes)")


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main() -> None:
    """
    Función principal: configura los datos de ejemplo y ejecuta las demos.
    Captura errores críticos para proporcionar mensajes claros al usuario.
    """
    texto_prueba = (
        "El producto llegó rápido, pero la calidad no es lo que esperaba. "
        "La verdad, estoy un poco decepcionado."
    )

    reseñas = [
        "Me encantó este producto, súper recomendado",
        "Regular, cumple pero no es nada del otro mundo",
        "Horrible, no compren esto, es una estafa",
        "Buen producto, buen precio, envío rápido",
        "No me gustó, la calidad es mala",
    ]

    try:
        demo_niveles(texto_prueba)
        demo_multiples(reseñas)
        demo_historial()
    except EnvironmentError as exc:
        print(f"\n❌ Error de configuración: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"\n❌ Error de API: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución interrumpida por el usuario.")
        sys.exit(0)

    print("\n✅ Análisis completado.\n")


if __name__ == "__main__":
    main()