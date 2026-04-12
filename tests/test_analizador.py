import pytest
import json
from unittest.mock import MagicMock
from sentimiento.analizador import analizar_basico, analizar_intermedio, analizar_avanzado

# --- Fixtures ---

@pytest.fixture
def mock_openai_client():
    """
    Configura el mock para que responda a la cadena:
    cliente.chat.completions.create(...)
    """
    mock_client = MagicMock()
    # Creamos la cadena de mocks
    mock_chat = MagicMock()
    mock_completions = MagicMock()
    
    mock_client.chat = mock_chat
    mock_chat.completions = mock_completions
    # El método .create es el que devolverá nuestra respuesta simulada
    return mock_client

@pytest.fixture
def mock_response_factory():
    """
    Genera la estructura de objeto que la SDK de OpenAI devuelve:
    objeto.choices[0].message.content
    """
    def _crear_respuesta(content: str):
        mock_res = MagicMock()
        mock_message = MagicMock()
        mock_message.content = content
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_res.choices = [mock_choice]
        return mock_res
    return _crear_respuesta

# --- Casos Felices ---

def test_analizar_basico_exito(mock_openai_client, mock_response_factory):
    # Setup: Ahora accedemos a la profundidad correcta del mock
    respuesta_ia = mock_response_factory("Positivo")
    mock_openai_client.chat.completions.create.return_value = respuesta_ia
    
    resultado = analizar_basico(mock_openai_client, "Hoy es un día maravilloso")
    
    assert resultado["sentimiento"] == "positivo"
    assert resultado["nivel"] == "básico"

def test_analizar_intermedio_exito(mock_openai_client, mock_response_factory):
    json_resp = json.dumps({
        "polaridad": 0.8,
        "emociones": ["alegría"],
        "intensidad": "alta"
    })
    mock_openai_client.chat.completions.create.return_value = mock_response_factory(json_resp)
    
    resultado = analizar_intermedio(mock_openai_client, "¡Excelente!")
    
    assert resultado["polaridad"] == 0.8
    assert resultado.get("error") is None

def test_analizar_avanzado_exito(mock_openai_client, mock_response_factory):
    json_resp = json.dumps({
        "fragmentos": [{"texto": "bueno", "sentimiento": "positivo"}],
        "justificacion": "Test",
        "tonalidad": "formal",
        "recomendacion": "Ninguna"
    })
    mock_openai_client.chat.completions.create.return_value = mock_response_factory(json_resp)
    
    resultado = analizar_avanzado(mock_openai_client, "Texto de prueba")
    
    assert resultado["nivel"] == "avanzado"
    assert resultado["tonalidad"] == "formal"

# --- Casos Borde ---

def test_analizar_texto_vacio(mock_openai_client, mock_response_factory):
    mock_openai_client.chat.completions.create.return_value = mock_response_factory("Neutro")
    resultado = analizar_basico(mock_openai_client, "")
    assert resultado["sentimiento"] == "neutro"

def test_analizar_texto_muy_largo(mock_openai_client, mock_response_factory):
    texto_largo = "A" * 200
    mock_openai_client.chat.completions.create.return_value = mock_response_factory("Positivo")
    
    resultado = analizar_basico(mock_openai_client, texto_largo)
    
    assert "..." in resultado["texto_original"]
    assert len(resultado["texto_original"]) > 100

# --- Casos de Error ---

def test_error_api_no_disponible(mock_openai_client):
    # Forzamos la excepción en el método create
    mock_openai_client.chat.completions.create.side_effect = Exception("API Down")
    
    with pytest.raises(RuntimeError) as exc:
        analizar_basico(mock_openai_client, "Hola")
    assert "Error en la llamada a la API" in str(exc.value)

def test_error_json_malformado(mock_openai_client, mock_response_factory):
    # Enviamos algo que json.loads() no pueda procesar
    mock_openai_client.chat.completions.create.return_value = mock_response_factory("No soy un JSON")
    
    resultado = analizar_intermedio(mock_openai_client, "Error test")
    
    assert resultado["error"] is not None
    assert "No se pudo parsear" in resultado["error"]