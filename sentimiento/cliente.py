# sentimiento/cliente.py
# Responsabilidad única: inicializar el cliente OpenAI de forma segura
 
import os
from dotenv import load_dotenv
from openai import OpenAI
 
def get_client() -> OpenAI:
    """Crea y devuelve el cliente OpenAI usando la variable de entorno."""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError('OPENAI_API_KEY no encontrada en el fichero .env')
    return OpenAI(api_key=api_key)
