# Guía de Tests
El proyecto usa pytest como framework de testing. Los tests se encuentran en la carpeta tests/ en la raíz del proyecto.

## 1. Estructura de Tests
tests/
├── __init__.py
├── conftest.py          # fixtures compartidas
├── test_analizador.py   # tests del motor NLP
└── test_guardar.py      # tests del sistema de almacenamiento

## 2. Ejecutar los Tests
Todos los tests
# Desde la raíz del proyecto
pytest

# Con salida detallada
pytest -v

# Con reporte de cobertura
pytest --cov=sentimiento --cov=almacenamiento --cov-report=term-missing

Un archivo o test concreto
# Sólo los tests del analizador
pytest tests/test_analizador.py -v

# Un test específico por nombre
pytest tests/test_analizador.py::test_sentimiento_positivo -v

# Tests que coincidan con un patrón
pytest -k "positivo or negativo" -v

## 3. Cobertura de Cada Archivo
test_analizador.py
▸	test_sentimiento_positivo: Verifica que un texto claramente positivo obtenga nivel POSITIVO y score > 0.
▸	test_sentimiento_negativo: Verifica que un texto negativo obtenga nivel NEGATIVO y score < 0.
▸	test_sentimiento_neutral: Verifica que un texto ambiguo obtenga nivel NEUTRAL con score cercano a 0.
▸	test_texto_vacio: Comprueba que un string vacío no lanza excepción y devuelve un diccionario válido.
▸	test_texto_largo: Texto de más de 512 caracteres; verifica que se trunque o se maneje sin error.
▸	test_tipos_retorno: Comprueba que score sea float y nivel sea str.

test_guardar.py
▸	test_guardar_crea_json: Llama a guardar_resultado y verifica que el archivo .json existe en disco.
▸	test_guardar_crea_txt: Ídem para el archivo .txt.
▸	test_formato_nombre_archivo: Comprueba que el nombre sigue el patrón analisis_YYYY-MM-DD_HHmmss.
▸	test_contenido_json_valido: Parsea el JSON creado y verifica que todos los campos obligatorios están presentes.
▸	test_leer_resultado: Guarda y luego lee; verifica que los datos son idénticos.
▸	test_listar_resultados: Verifica que listar_resultados devuelve los archivos en orden cronológico inverso.

## 4. Fixtures (conftest.py)
conftest.py define fixtures reutilizables disponibles automáticamente para todos los archivos de test:
# conftest.py
import pytest
from sentimiento.cliente import ClienteSentimiento

@pytest.fixture
def cliente():
    """Instancia de ClienteSentimiento lista para usar."""
    return ClienteSentimiento()

@pytest.fixture
def resultado_ejemplo():
    """Diccionario de resultado para tests de almacenamiento."""
    return {
        "texto_original": "Texto de prueba",
        "score": 0.65,
        "nivel": "POSITIVO",
        "detalles": {"positivo":0.65,"neutral":0.30,"negativo":0.05}
    }

@pytest.fixture(autouse=True)
def limpiar_resultados(tmp_path, monkeypatch):
    """Redirige escrituras a tmp_path para no contaminar resultados/."""
    monkeypatch.chdir(tmp_path)
    yield

## 5. Cómo Añadir Nuevos Tests
Paso 1 — Crear el archivo
Crea tests/test_<modulo>.py. pytest descubrirá automáticamente cualquier archivo que empiece por test_.

Paso 2 — Escribir el test
# tests/test_niveles.py
from sentimiento.niveles import clasificar_nivel

def test_umbral_positivo():
    assert clasificar_nivel(0.06) == "POSITIVO"

def test_umbral_neutral_positivo():
    assert clasificar_nivel(0.05) == "NEUTRAL"

def test_umbral_negativo():
    assert clasificar_nivel(-0.50) == "NEGATIVO"

Paso 3 — Usar fixtures existentes
def test_analizar_con_cliente(cliente):
    res = cliente.analizar_texto("Fantástico")
    assert res["nivel"] == "POSITIVO"

## 6. Configuración de pytest
El archivo pytest.ini en la raíz controla el comportamiento global:
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -ra -q
filterwarnings = ignore::DeprecationWarning

## 7. Pipeline CI
El workflow .github/workflows/pipeline.yml ejecuta los tests automáticamente en cada push y pull request:
# .github/workflows/pipeline.yml (resumen)
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest --cov=sentimiento --cov=almacenamiento
Consejo: los tests deben ser independientes del sistema de archivos real.
Usa la fixture limpiar_resultados (o tmp_path de pytest) para que
cada test trabaje en un directorio temporal limpio.
