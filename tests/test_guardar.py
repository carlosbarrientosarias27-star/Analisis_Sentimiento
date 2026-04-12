import json
import pytest
from unittest.mock import patch
from datetime import datetime, timezone

# Importamos las funciones y las rutas de carpetas para validación
from almacenamiento.guardar import guardar_resultado, CARPETA_TXT, CARPETA_JSON

# --- FIXTURES ---

@pytest.fixture
def datos_ia():
    """Simula la respuesta JSON de un modelo de IA."""
    return {
        "sentimiento": "positivo",
        "confianza": 0.98,
        "detalles": {"emocion": "alegría"}
    }

@pytest.fixture
def mock_now():
    """Mock robusto para fijar la fecha/hora y predecir nombres de archivos."""
    fixed_now = datetime(2026, 4, 12, 16, 30, 0, tzinfo=timezone.utc)
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    with patch('almacenamiento.guardar.datetime', MockDatetime):
        yield fixed_now

# --- CASOS FELICES ---

def test_guardar_resultado_crea_archivos_correctos(mock_now, datos_ia):
    """Verifica que se generen tanto el TXT como el JSON con el formato esperado."""
    texto = "Excelente servicio al cliente"
    
    rutas = guardar_resultado(texto, datos_ia)
    
    # Validar que el diccionario de retorno tiene las llaves correctas
    assert 'txt' in rutas
    assert 'json' in rutas
    
    # Validar nombres de archivos basados en el mock_now (2026-04-12_163000)
    assert "analisis_2026-04-12_163000.txt" in rutas['txt']
    assert "analisis_2026-04-12_163000.json" in rutas['json']

def test_contenido_persistido_correctamente(datos_ia):
    """Verifica que el contenido guardado en los archivos sea íntegro."""
    texto_input = "Prueba de integridad de datos"
    rutas = guardar_resultado(texto_input, datos_ia)
    
    # Verificar TXT
    with open(rutas['txt'], 'r', encoding='utf-8') as f:
        assert f.read() == texto_input
        
    # Verificar JSON
    with open(rutas['json'], 'r', encoding='utf-8') as f:
        contenido_json = json.load(f)
        assert contenido_json["sentimiento"] == "positivo"

def test_creacion_de_carpetas_automatica():
    """Asegura que las carpetas 'txt' y 'json' se creen si no existen."""
    # Forzamos la ejecución de la lógica de creación
    guardar_resultado("test", {"res": "ok"})
    
    assert CARPETA_TXT.exists()
    assert CARPETA_JSON.exists()

# --- CASOS BORDE ---

def test_guardar_texto_muy_largo(datos_ia):
    """Prueba el comportamiento con un volumen de texto considerable."""
    texto_largo = "IA " * 10000
    rutas = guardar_resultado(texto_largo, datos_ia)
    
    with open(rutas['txt'], 'r', encoding='utf-8') as f:
        assert len(f.read()) == len(texto_largo)

def test_guardar_con_caracteres_especiales():
    """Verifica que UTF-8 maneje correctamente emojis y tildes."""
    texto = "Mañana será un gran día 🌟"
    datos = {"status": "confirmado ✅"}
    
    rutas = guardar_resultado(texto, datos)
    
    with open(rutas['json'], 'r', encoding='utf-8') as f:
        contenido = json.load(f)
        assert "✅" in contenido["status"]

# --- CASOS DE ERROR ---

def test_error_serializacion_json():
    """Debe lanzar TypeError si el diccionario contiene objetos no serializables."""
    datos_invalidos = {"fecha": datetime.now()} # datetime no es serializable directamente
    
    with pytest.raises(TypeError) as excinfo:
        guardar_resultado("texto", datos_invalidos)
    
    assert "Error al serializar JSON" in str(excinfo.value)

def test_error_permisos_sistema(datos_ia):
    """Simula un error de escritura en disco para verificar la robustez."""
    with patch("pathlib.Path.write_text", side_effect=OSError("Disco lleno")):
        with pytest.raises(OSError) as excinfo:
            guardar_resultado("test", datos_ia)
        
        assert "Disco lleno" in str(excinfo.value)