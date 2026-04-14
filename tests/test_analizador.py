import pytest
import json
from unittest.mock import MagicMock
from sentimiento.analizador import analizar_basico, analizar_intermedio, analizar_avanzado

# --- Fixtures ---

@pytest.fixture
def mock_pipeline():
    """
    Simula el pipeline de transformers.
    Se comporta como una función: cliente(texto)
    """
    return MagicMock()

@pytest.fixture
def mock_response():
    """
    Simula la respuesta estándar de Hugging Face: [{'generated_text': '...'}]
    """
    def _crear(contenido):
        return [{"generated_text": contenido}]
    return _crear

# --- Casos Felices ---

def test_analizar_basico_exito(mock_pipeline, mock_response):
    # Setup: el "cliente" devuelve la respuesta directamente al ser llamado
    mock_pipeline.return_value = mock_response("Positivo")
    
    resultado = analizar_basico(mock_pipeline, "Hoy es un gran día")
    
    assert resultado["sentimiento"] == "positivo"
    assert resultado["nivel"] == "básico"

def test_analizar_intermedio_exito(mock_pipeline, mock_response):
    json_resp = json.dumps({
        "polaridad": 0.5,
        "emociones": ["alegría"],
        "intensidad": "media"
    })
    mock_pipeline.return_value = mock_response(json_resp)
    
    resultado = analizar_intermedio(mock_pipeline, "Texto de prueba")
    
    assert resultado["polaridad"] == 0.5
    assert resultado["nivel"] == "intermedio"

def test_analizar_avanzado_exito(mock_pipeline, mock_response):
    json_resp = json.dumps({
        "fragmentos": [{"texto": "bueno", "sentimiento": "positivo"}],
        "justificacion": "Test",
        "tonalidad": "formal",
        "recomendacion": "Ninguna"
    })
    mock_pipeline.return_value = mock_response(json_resp)
    
    resultado = analizar_avanzado(mock_pipeline, "Prueba avanzada")
    
    assert resultado["nivel"] == "avanzado"
    assert resultado["tonalidad"] == "formal"

# --- Casos Borde ---

def test_analizar_texto_vacio(mock_pipeline, mock_response):
    mock_pipeline.return_value = mock_response("Neutro")
    resultado = analizar_basico(mock_pipeline, "")
    assert resultado["sentimiento"] == "neutro"

# --- Casos de Error ---

def test_error_modelo_local(mock_pipeline):
    # Forzamos error en la "llamada" al modelo
    mock_pipeline.side_effect = Exception("Modelo no cargado")
    
    with pytest.raises(RuntimeError) as exc:
        analizar_basico(mock_pipeline, "Hola")
    assert "Error en la ejecución del modelo local" in str(exc.value)

def test_error_json_malformado(mock_pipeline, mock_response):
    # El modelo devuelve texto plano cuando se esperaba JSON
    mock_pipeline.return_value = mock_response("No soy un JSON")
    
    resultado = analizar_intermedio(mock_pipeline, "Error test")
    
    assert resultado["error"] is not None
    assert "No se pudo parsear" in resultado["error"]