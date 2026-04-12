import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Asumiendo que la estructura de carpetas es:
# proyecto/
# ├── almacenamiento/
# │   └── guardar.py
# └── tests/
#     └── test_guardar.py
from almacenamiento.guardar import guardar_resultado, guardar_multiples

# --- FIXTURES ---

@pytest.fixture
def datos_validos():
    """Retorna un diccionario de ejemplo similar a una respuesta de IA."""
    return {
        "id": "chatcmpl-123",
        "model": "gpt-4",
        "choices": [{"text": "Respuesta de prueba"}]
    }

@pytest.fixture
def mock_now():
    """Mock robusto para fijar la fecha y hora."""
    fixed_now = datetime(2026, 4, 12, 16, 30, 0, tzinfo=timezone.utc)
    
    # Creamos una subclase de datetime para evitar problemas de inmutabilidad
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    with patch('almacenamiento.guardar.datetime', MockDatetime):
        yield fixed_now

# --- CASOS FELICES ---

def test_guardar_resultado_exitoso(tmp_path, datos_validos, mock_now):
    """Verifica que un archivo JSON se guarde correctamente en un directorio específico."""
    prefijo = "test_ia"
    ruta_generada = guardar_resultado(datos_validos, prefijo=prefijo, directorio=tmp_path)
    
    assert ruta_generada.exists()
    assert ruta_generada.name == "test_ia_20260412_163000.json"
    
    # Validar contenido
    contenido = json.loads(ruta_generada.read_text(encoding="utf-8"))
    assert contenido["id"] == "chatcmpl-123"

def test_guardar_multiples_exitoso(tmp_path, datos_validos, mock_now):
    """Verifica la persistencia de una lista de resultados bajo una llave contenedora."""
    lista_resultados = [datos_validos, datos_validos]
    ruta_generada = guardar_multiples(lista_resultados, prefijo="batch", directorio=tmp_path)
    
    contenido = json.loads(ruta_generada.read_text(encoding="utf-8"))
    assert "resultados" in contenido
    assert len(contenido["resultados"]) == 2
    assert contenido["resultados"][0]["model"] == "gpt-4"

def test_creacion_automatica_directorio(tmp_path, datos_validos):
    """Verifica que el script crea subdirectorios si estos no existen previamente."""
    sub_dir = tmp_path / "nueva_carpeta" / "logs"
    ruta_generada = guardar_resultado(datos_validos, directorio=sub_dir)
    
    assert sub_dir.exists()
    assert ruta_generada.parent == sub_dir

# --- CASOS BORDE ---

def test_guardar_resultado_con_caracteres_especiales(tmp_path):
    """Prueba la correcta codificación UTF-8 con emojis y acentos."""
    datos = {"texto": "Acción confirmada 🚀", "idioma": "Español"}
    ruta = guardar_resultado(datos, directorio=tmp_path)
    
    contenido_raw = ruta.read_text(encoding="utf-8")
    assert "🚀" in contenido_raw
    assert "Acción" in contenido_raw

def test_guardar_diccionario_vacio(tmp_path):
    """Verifica que el sistema maneja correctamente estructuras de datos vacías."""
    ruta = guardar_resultado({}, prefijo="vacio", directorio=tmp_path)
    contenido = json.loads(ruta.read_text(encoding="utf-8"))
    assert contenido == {}

# --- CASOS DE ERROR ---

def test_error_tipo_no_serializable(tmp_path):
    """Debe lanzar TypeError si intentamos guardar objetos que JSON no soporta (ej. sets)."""
    datos_invalidos = {
        "timestamp": datetime.now(), # datetime directo no es serializable por defecto
        "valores": {1, 2, 3}        # sets no son serializables
    }
    
    with pytest.raises(TypeError) as excinfo:
        guardar_resultado(datos_invalidos, directorio=tmp_path)
    
    assert "no serializables" in str(excinfo.value)

def test_error_permisos_escritura(tmp_path, datos_validos):
    """Verifica el comportamiento cuando no hay permisos de escritura (Simulado)."""
    # Usamos mock para simular una falla de sistema (OSError) al escribir
    with patch("pathlib.Path.write_text", side_effect=OSError("No hay espacio o permiso")):
        with pytest.raises(OSError) as excinfo:
            guardar_resultado(datos_validos, directorio=tmp_path)
        
        assert "No hay espacio o permiso" in str(excinfo.value)