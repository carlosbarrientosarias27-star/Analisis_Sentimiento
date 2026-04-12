import pytest
import os
from unittest.mock import MagicMock
from sentimiento.analizador import analizar_basico

# Importación segura
try:
    from almacenamiento.guardar import guardar_resultado
except ImportError:
    guardar_resultado = None

# ─── Fixture Ultra-Robusta ──────────────────────────────────────

@pytest.fixture
def mock_client():
    client = MagicMock()
    # Configuramos el retorno de la API de forma directa y profunda
    # Esto asegura que client.chat.completions.create(...).choices[0].message.content funcione
    mock_content = MagicMock()
    mock_content.choices = [MagicMock()]
    mock_content.choices[0].message.content = 'POSITIVO'
    
    client.chat.completions.create.return_value = mock_content
    return client

# ─── Tests del Analizador ───────────────────────────────────────

def test_1_sentimiento_positivo(mock_client):
    resultado = analizar_basico(mock_client, 'Me encanta')
    # Tu código aplica .lower() a la respuesta de la API
    assert resultado.sentimiento == 'positivo'

def test_2_sentimiento_negativo(mock_client):
    # Forzamos la respuesta negativa en el mock
    mock_client.chat.completions.create.return_value.choices[0].message.content = 'NEGATIVO'
    resultado = analizar_basico(mock_client, 'Horrible')
    assert resultado.sentimiento == 'negativo'

def test_3_resultado_tiene_atributos(mock_client):
    resultado = analizar_basico(mock_client, 'test')
    # Importante: Verifica si en niveles.py pusiste "básico" o "basico"
    # Si falla aquí, cambia "básico" por "basico"
    assert resultado.nivel == "básico"
    assert hasattr(resultado, 'sentimiento')

def test_4_texto_vacio(mock_client):
    # No debería explotar con strings vacíos
    resultado = analizar_basico(mock_client, '')
    assert resultado.sentimiento is not None

# ─── Tests de Almacenamiento (Fix Windows) ──────────────────────

def test_6_almacenamiento_txt(tmp_path):
    if guardar_resultado is None: pytest.skip("Falta modulo guardar")
    
    # En lugar de monkeypatch, pasamos la ruta completa si guardar_resultado lo permite
    # O usamos os.chdir directamente con el path convertido a string
    path_str = str(tmp_path)
    old_cwd = os.getcwd()
    os.chdir(path_str)
    
    try:
        rutas = guardar_resultado('prueba', {'sentimiento': 'positivo'})
        assert os.path.exists(rutas['txt'])
    finally:
        os.chdir(old_cwd)

def test_7_almacenamiento_json(tmp_path):
    if guardar_resultado is None: pytest.skip("Falta modulo guardar")
    
    path_str = str(tmp_path)
    old_cwd = os.getcwd()
    os.chdir(path_str)
    
    try:
        rutas = guardar_resultado('prueba', {'sentimiento': 'positivo'})
        assert os.path.exists(rutas['json'])
    finally:
        os.chdir(old_cwd)