# ============================================
# sentimiento/cliente.py
# Responsabilidad única: construir y exponer el cliente OpenAI.
# Nunca instanciar el cliente fuera de este módulo.
# ============================================

from transformers import pipeline

def crear_cliente():
    """
    Carga un modelo de análisis de sentimiento local usando Transformers.
    
    Returns:
        pipeline: Una tubería de Hugging Face lista para procesar texto.
    """
    # Puedes elegir un modelo específico. 
    # Si no pones nada, usará 'distilbert-base-uncased-finetuned-sst-2-english' por defecto.
    # Para español, te recomiendo: "pysentimiento/robertuito-sentiment-analysis"
    nombre_modelo = "pysentimiento/robertuito-sentiment-analysis"
    
    print(f"Cargando modelo local: {nombre_modelo}...")
    
    # La pipeline se encarga de descargar el modelo (solo la primera vez) 
    # y de gestionar el tokenizador y el modelo automáticamente.
    analizador = pipeline(
        "sentiment-analysis", 
        model=nombre_modelo
    )
    
    return analizador
