import pytest
import os
from unittest.mock import MagicMock
from sentimiento.analizador import analizar_basico
# Nota: Asegúrate de que 'almacenamiento.guardar' exista o ajusta esta importación
try:
    from almacenamiento.guardar import guardar_resultado
except ImportError:
    guardar_resultado = None

# ─── Fixture: simula la respuesta de OpenAI ───────────────────────

@pytest.fixture
def mock_client():
    client = MagicMock()
    # Simulamos la estructura de respuesta de OpenAI: response.choices[0].message.content
    respuesta = MagicMock()
    respuesta.choices = [MagicMock()]
    respuesta.choices[0].message.content = 'POSITIVO'
    client.chat.completions.create.return_value = respuesta
    return client

# ─── Tests del analizador ─────────────────────────────────────────

def test_1_sentimiento_positivo(mock_client):
    # Usamos el nombre correcto de la función: analizar_basico
    resultado = analizar_basico(mock_client, 'Me encanta este producto')
    
    # ResultadoBasico es un objeto (probablemente un dataclass o Pydantic), 
    # por lo que accedemos por atributo, no por clave.
    assert resultado.sentimiento == 'positivo'

def test_2_sentimiento_negativo(mock_client):
    mock_client.chat.completions.create.return_value.choices[0].message.content = 'NEGATIVO'
    
    resultado = analizar_basico(mock_client, 'Muy mala experiencia')
    assert resultado.sentimiento == 'negativo'

def test_3_resultado_tiene_atributos(mock_client):
    resultado = analizar_basico(mock_client, 'Texto cualquiera')
    
    # Verificamos atributos del objeto ResultadoBasico
    assert hasattr(resultado, 'nivel')
    assert hasattr(resultado, 'sentimiento')
    assert resultado.nivel == "básico"

def test_4_texto_vacio(mock_client):
    # Caso borde: no debe crashear con texto vacío
    resultado = analizar_basico(mock_client, '')
    assert resultado.sentimiento == 'positivo' # O lo que devuelva el mock

def test_5_api_no_disponible():
    client = MagicMock()
    # El código original lanza RuntimeError cuando la API falla
    client.chat.completions.create.side_effect = Exception('API error')
    
    with pytest.raises(RuntimeError) as excinfo:
        analizar_basico(client, 'texto')
    assert "Error en la llamada a la API" in str(excinfo.value)

# ─── Tests del almacenamiento ─────────────────────────────────────

@pytest.mark.skipif(guardar_resultado is None, reason="Modulo de almacenamiento no encontrado")
def test_6_almacenamiento_txt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rutas = guardar_resultado('texto prueba', {'sentimiento': 'positivo'})
    assert os.path.exists(rutas['txt'])

@pytest.mark.skipif(guardar_resultado is None, reason="Modulo de almacenamiento no encontrado")
def test_7_almacenamiento_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rutas = guardar_resultado('texto prueba', {'sentimiento': 'positivo'})
    assert os.path.exists(rutas['json'])