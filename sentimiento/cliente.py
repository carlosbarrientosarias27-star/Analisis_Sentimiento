# ============================================
# sentimiento/cliente.py
# Responsabilidad única: construir y exponer el cliente OpenAI.
# Nunca instanciar el cliente fuera de este módulo.
# ============================================

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Esto carga las variables del .env
api_key = os.getenv("OPENAI_API_KEY")


def crear_cliente() -> OpenAI:
    """
    Carga las variables de entorno y devuelve un cliente OpenAI configurado.

    Returns:
        OpenAI: instancia lista para hacer llamadas a la API.

    Raises:
        EnvironmentError: si la variable OPENAI_API_KEY no está definida.
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "La variable de entorno OPENAI_API_KEY no está definida. "
            "Comprueba tu archivo .env o las variables del sistema."
        )

    return OpenAI(api_key=api_key)
