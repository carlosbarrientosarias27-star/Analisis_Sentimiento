# tests/test_analizador.py
import pytest
import os, json
from unittest.mock import MagicMock, patch
from sentimiento.analizador import analizar_sentimiento_basico
from almacenamiento.guardar import guardar_resultado
 
# ─── Fixture: simula la respuesta de OpenAI ───────────────────────
@pytest.fixture
def mock_client():
    client = MagicMock()
    respuesta = MagicMock()
    respuesta.choices[0].message.content = 'POSITIVO'
    client.chat.completions.create.return_value = respuesta
    return client
 
# ─── Tests del analizador ─────────────────────────────────────────
def test_1_sentimiento_positivo(mock_client):
    resultado = analizar_sentimiento_basico('Me encanta este producto', mock_client)
    assert resultado['sentimiento'] == 'POSITIVO'
 
def test_2_sentimiento_negativo(mock_client):
    mock_client.chat.completions.create.return_value.choices[0].message.content = 'NEGATIVO'
    resultado = analizar_sentimiento_basico('Muy mala experiencia', mock_client)
    assert resultado['sentimiento'] == 'NEGATIVO'
 
def test_3_resultado_tiene_claves(mock_client):
    resultado = analizar_sentimiento_basico('Texto cualquiera', mock_client)
    assert 'nivel' in resultado
    assert 'sentimiento' in resultado
 
def test_4_texto_vacio(mock_client):
    # Caso borde: no debe crashar con texto vacío
    resultado = analizar_sentimiento_basico('', mock_client)
    assert isinstance(resultado, dict)
 
def test_5_api_no_disponible():
    client = MagicMock()
    client.chat.completions.create.side_effect = Exception('API error')
    with pytest.raises(Exception):
        analizar_sentimiento_basico('texto', client)
 
# ─── Tests del almacenamiento ─────────────────────────────────────
def test_6_almacenamiento_txt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # carpeta temporal
    rutas = guardar_resultado('texto prueba', {'basico': 'POSITIVO'})
    assert os.path.exists(rutas['txt'])
 
def test_7_almacenamiento_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rutas = guardar_resultado('texto prueba', {'basico': 'POSITIVO'})
