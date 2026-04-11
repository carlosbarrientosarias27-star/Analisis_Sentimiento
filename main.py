import json
from sentimiento.cliente import obtener_cliente
from sentimiento.analizador import ejecutar_analisis
from sentimiento.multitexto import analizar_lote
from almacenamiento.guardar import guardar_json

def main():
    try:
        # 1. Inicialización
        cliente = obtener_cliente()
        texto_prueba = "El producto es aceptable, pero el soporte técnico fue lento."
        
        # 2. Análisis Individual (Avanzado)
        print("--- Analizando texto individual ---")
        resultado_adv = ejecutar_analisis(cliente, texto_prueba, nivel="avanzado")
        print(f"Sentimiento: {resultado_adv.get('sentimiento_global')}")
        
        # 3. Análisis por lotes
        print("\n--- Analizando lote de reseñas ---")
        reseñas = [
            "Excelente servicio",
            "No me gustó nada",
            "Es normalito"
        ]
        lote_resultado = analizar_lote(cliente, reseñas)
        
        # 4. Persistencia
        ruta = guardar_json(lote_resultado, "resultado_analisis.json")
        print(f"\n✅ Proceso completado. Datos guardados en: {ruta}")
        print(f"Polaridad promedio: {lote_resultado['estadisticas']['polaridad_promedio']:.2f}")

    except Exception as e:
        print(f"❌ Error crítico en la aplicación: {e}")

if __name__ == "__main__":
    main()