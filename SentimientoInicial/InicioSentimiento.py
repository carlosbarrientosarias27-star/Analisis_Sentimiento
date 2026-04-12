# ============================================
# ANÁLISIS DE SENTIMIENTO AVANZADO
# ============================================
import os
import json  # Se añadió el import de json que faltaba
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analizar_sentimiento_basico(texto: str) -> dict:
    """Nivel básico: solo categoría"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            Analiza el sentimiento del texto. Responde SOLO con una palabra: positivo, negativo o neutral.
            """},
            {"role": "user", "content": texto}
        ],
        temperature=0.0
    )
    
    return {
        "nivel": "básico",
        "sentimiento": response.choices[0].message.content.strip(),
        "texto_original": texto[:100] + "..."
    }

def analizar_sentimiento_intermedio(texto: str) -> dict:
    """Nivel intermedio: polaridad, puntuación, emociones"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            Analiza el sentimiento del texto. Responde ÚNICAMENTE en formato JSON con:
            - sentimiento: positivo, negativo o neutral
            - polaridad: número entre -1 (muy negativo) y +1 (muy positivo)
            - emociones: objeto con puntuaciones para alegria, tristeza, enojo, sorpresa, miedo
            - intensidad: baja, media, alta
            """},
            {"role": "user", "content": texto}
        ],
        temperature=0.0
    )
    
    try:
        resultado = json.loads(response.choices[0].message.content)
        resultado["nivel"] = "intermedio"
        resultado["texto_original"] = texto[:100] + "..."
        return resultado
    except Exception: # Se cambió 'except:' por 'except Exception:' (E722)
        return {
            "nivel": "intermedio",
            "error": "No se pudo parsear respuesta",
            "respuesta_raw": response.choices[0].message.content
        }

def analizar_sentimiento_avanzado(texto: str) -> dict:
    """Nivel avanzado: con justificación y fragmentos relevantes"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            Analiza el sentimiento del texto en profundidad. Responde ÚNICAMENTE en formato JSON con:
            - sentimiento_global: positivo, negativo o neutral
            - polaridad: número entre -1 y +1
            - fragmentos: lista de objetos con "texto" y "sentimiento_individual"
            - justificacion: explicación del análisis
            - tonalidad: formal, coloquial, agresivo, entusiasta, etc.
            - recomendacion: qué acción tomar según el sentimiento
            """},
            {"role": "user", "content": texto}
        ],
        temperature=0.0
    )
    
    try:
        resultado = json.loads(response.choices[0].message.content)
        resultado["nivel"] = "avanzado"
        resultado["texto_original"] = texto[:100] + "..."
        return resultado
    except Exception: # Se cambió 'except:' por 'except Exception:' (E722)
        return {
            "nivel": "avanzado",
            "error": "No se pudo parsear respuesta",
            "respuesta_raw": response.choices[0].message.content
        }

def analizar_sentimiento_multitexto(textos: list) -> dict: # Se cambió type hint de list a dict para el retorno
    """Analiza sentimiento de múltiples textos y calcula estadísticas"""
    
    resultados = []
    for texto in textos:
        resultado = analizar_sentimiento_intermedio(texto)
        resultados.append(resultado)
    
    # Calcular estadísticas agregadas
    polaridades = [r.get("polaridad", 0) for r in resultados if isinstance(r.get("polaridad"), (int, float))]
    
    estadisticas = {
        "total": len(resultados),
        "positivos": sum(1 for r in resultados if r.get("sentimiento") == "positivo"),
        "negativos": sum(1 for r in resultados if r.get("sentimiento") == "negativo"),
        "neutrales": sum(1 for r in resultados if r.get("sentimiento") == "neutral"),
        "polaridad_promedio": sum(polaridades) / len(polaridades) if polaridades else 0
    }
    
    return {
        "resultados_individuales": resultados,
        "estadisticas": estadisticas
    }

# ========== BLOQUE DE EJECUCIÓN Y PERSISTENCIA ==========
if __name__ == "__main__":
    # Importación local para evitar dependencias circulares
    from almacenamiento.guardar import guardar_resultado, guardar_multiples

    print("=" * 70)
    print("📊 ANÁLISIS Y PERSISTENCIA DE RESULTADOS")
    print("=" * 70)

    texto_prueba = "El producto llegó rápido, pero la calidad no es lo que esperaba."

    # 1. Analizar
    print("\n[1] Analizando sentimiento...")
    resultado_avanzado = analizar_sentimiento_avanzado(texto_prueba)

    # 2. Guardar (Esto genera los archivos que el script de verificación busca)
    print("[2] Guardando resultado en disco...")
    ruta = guardar_resultado(resultado_avanzado, prefijo="demo_avanzado")
    print(f"✅ Archivo creado en: {ruta}")

    # 3. Ejemplo múltiple
    reseñas_batch = ["Excelente", "Pésimo servicio"]
    print("\n[3] Procesando lote de reseñas...")
    resultado_batch = analizar_sentimiento_multitexto(reseñas_batch)
    
    # Guardamos los resultados individuales en un solo archivo JSON
    ruta_batch = guardar_multiples(
        resultado_batch["resultados_individuales"], 
        prefijo="batch_reseñas"
    )
    print(f"✅ Archivo batch creado en: {ruta_batch}")

# Análisis de múltiples textos (ejemplo de reseñas)
print("\n" + "=" * 70)
print("📊 ANÁLISIS DE MÚLTIPLES RESEÑAS")
print("=" * 70)

reseñas = [
    "Me encantó este producto, súper recomendado",
    "Regular, cumple pero no es nada del otro mundo",
    "Horrible, no compren esto, es una estafa",
    "Buen producto, buen precio, envío rápido",
    "No me gustó, la calidad es mala"
]

resultado_multiple = analizar_sentimiento_multitexto(reseñas)

print("\n📈 ESTADÍSTICAS AGREGADAS:")
print(f"   Total de reseñas: {resultado_multiple['estadisticas']['total']}")
print(f"   Positivas: {resultado_multiple['estadisticas']['positivos']}")
print(f"   Negativas: {resultado_multiple['estadisticas']['negativos']}")
print(f"   Neutrales: {resultado_multiple['estadisticas']['neutrales']}")
print(f"   Polaridad promedio: {resultado_multiple['estadisticas']['polaridad_promedio']:.2f}")

print("\n📋 RESEÑAS INDIVIDUALES:")
for i, res in enumerate(resultado_multiple['resultados_individuales']):
    print(f"\n   Reseña {i+1}: {reseñas[i]}")
    print(f"   → Sentimiento: {res.get('sentimiento')} (polaridad: {res.get('polaridad', 'N/A')})")
    if res.get('emociones'):
        emocion_principal = max(res['emociones'].items(), key=lambda x: x[1]) if res['emociones'] else ("ninguna", 0)
        print(f"   → Emoción principal: {emocion_principal[0]}")