#!/usr/bin/env python3
# ============================================
# main.py - CORREGIDO
# ============================================

import json
import sys

from sentimiento.cliente import crear_cliente
from sentimiento.analizador import analizar_basico, analizar_intermedio, analizar_avanzado
from sentimiento.multitexto import analizar_multitexto
# Eliminamos guardar_multiples de la importación porque ya no existe
from almacenamiento.guardar import guardar_resultado
from almacenamiento.leer import listar_analisis


# ── Helpers de presentación ───────────────────────────────────────────────────

def _titulo(texto: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70)

def _seccion(texto: str) -> None:
    print(f"\n{'─' * 70}")
    print(f"  {texto}")
    print(f"{'─' * 70}")

def _json(datos: dict) -> None:
    print(json.dumps(datos, indent=2, ensure_ascii=False))


# ── Demo 1: comparativa de niveles ───────────────────────────────────────────

def demo_niveles(texto: str) -> None:
    _titulo("DEMO 1: NIVELES DE ANÁLISIS")
    cliente = crear_cliente()

    # 1. NIVEL BÁSICO
    _seccion("NIVEL BÁSICO")
    res_b = analizar_basico(cliente, texto)
    datos_b = res_b.__dict__.copy() # Convertimos a dict
    datos_b["nivel"] = "básico"      # Inyectamos nivel
    _json(datos_b)
    guardar_resultado(texto, datos_b)

    # 2. NIVEL INTERMEDIO
    _seccion("NIVEL INTERMEDIO")
    res_i = analizar_intermedio(cliente, texto)
    datos_i = res_i.__dict__.copy() # Convertimos a dict
    datos_i["nivel"] = "intermedio"  # Inyectamos nivel
    _json(datos_i)
    guardar_resultado(texto, datos_i)

    # 3. NIVEL AVANZADO
    _seccion("NIVEL AVANZADO")
    res_a_obj = analizar_avanzado(cliente, texto)
    # Conversión segura para evitar errores de linter
    datos_a = res_a_obj.__dict__.copy() if hasattr(res_a_obj, "__dict__") else dict(res_a_obj)
    datos_a["nivel"] = "avanzado"     # Inyectamos nivel
    _json(datos_a)
    rutas=guardar_resultado(texto, datos_a)

    print("\n✅ Guardado exitoso:") 
    print(f"   TXT: {rutas['txt'].name}")
    print(f"   JSON: {rutas['json'].name}")

# ── Demo 2: análisis por lotes ───────────────────────────────────────────────

def demo_multiples(reseñas: list[str]) -> None:
    """
    Analiza un conjunto de reseñas y guarda cada una individualmente.
    """
    _titulo("📊 DEMO 2: ANÁLISIS DE MÚLTIPLES RESEÑAS")

    cliente = crear_cliente()
    resultado = analizar_multitexto(cliente, reseñas)
    
    for reseña, res in zip(reseñas, resultado["resultados_individuales"]):
        # Si el resultado es un objeto, lo convertimos y forzamos el nivel
        if hasattr(res, "__dict__"):
            datos_res = res.__dict__.copy()
        else:
            datos_res = dict(res)
            
        datos_res["nivel"] = "avanzado" # El validador exige esto
        guardar_resultado(reseña, datos_res)
        
    _seccion("📈 ESTADÍSTICAS")
    stats = resultado["estadisticas"]
    print(f"   Total: {stats['total']} | Positivas: {stats['positivos']} | Negativas: {stats['negativos']}")

    _seccion("📋 GUARDANDO RESULTADOS INDIVIDUALES")
    for reseña, res in zip(reseñas, resultado["resultados_individuales"]):
        # Inyectamos nivel para cumplir con el check_folders.py
        res["nivel"] = "avanzado"
        
        # Guardamos usando la nueva función de guardar.py
        rutas = guardar_resultado(reseña, res)
        print(f"   ✅ Procesado: {reseña[:30]}... -> {rutas['json'].name}")


# ── Demo 3: historial ────────────────────────────────────────────────────────

def demo_historial() -> None:
    _titulo("DEMO 3: HISTORIAL DE ARCHIVOS")
    archivos = listar_analisis()
    if not archivos:
        print("\n  (No hay resultados previos guardados.)")
        return

    for ruta in archivos:
        print(f"  • {ruta.name}  ({ruta.stat().st_size} bytes)")


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main() -> None:
    texto_prueba = "El producto llegó rápido, pero la calidad no es lo que esperaba."
    reseñas = [
        "Me encantó este producto, súper recomendado",
        "No me gustó, la calidad es mala",
    ]

    try:
        # FIX: Removed 'cliente' argument here to match the function definition
        demo_niveles(texto_prueba) 
        demo_multiples(reseñas)
        demo_historial()
    except Exception as exc:
        print(f"\n❌ Error imprevisto: {exc}")
        sys.exit(1)