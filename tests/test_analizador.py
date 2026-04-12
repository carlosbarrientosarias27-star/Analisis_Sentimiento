# ============================================
# tests/test_analizador.py
#
# Suite de tests unitarios para:
#   - sentimiento/analizador.py
#   - almacenamiento/guardar.py
#
# Ejecutar con:
#   pytest tests/test_analizador.py -v
# ============================================

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, mock_open

import pytest

# ---------------------------------------------------------------------------
# Stub de los módulos que no están en el repositorio de tests
# (niveles.py, openai) para que los imports de analizador.py no fallen.
# ---------------------------------------------------------------------------

# ── Stub de sentimiento.niveles ──────────────────────────────────────────────

from dataclasses import dataclass, field
from typing import Optional

MODELO_DEFAULT = "gpt-4o-mini"
PROMPT_BASICO = "Devuelve solo: positivo, negativo o neutro."
PROMPT_INTERMEDIO = "Devuelve JSON con campos: polaridad, emociones, intensidad."
PROMPT_AVANZADO = "Devuelve JSON con campos: fragmentos, justificacion, tonalidad, recomendacion."


@dataclass
class ResultadoBasico:
    nivel: str = ""
    sentimiento: str = ""
    texto_original: str = ""
    error: Optional[str] = None


@dataclass
class ResultadoIntermedio:
    nivel: str = ""
    texto_original: str = ""
    polaridad: Optional[str] = None
    emociones: Optional[list] = field(default_factory=list)
    intensidad: Optional[float] = None
    error: Optional[str] = None
    respuesta_raw: Optional[str] = None


@dataclass
class ResultadoAvanzado:
    nivel: str = ""
    texto_original: str = ""
    fragmentos: Optional[list] = field(default_factory=list)
    justificacion: Optional[str] = None
    tonalidad: Optional[str] = None
    recomendacion: Optional[str] = None
    error: Optional[str] = None
    respuesta_raw: Optional[str] = None


# Registrar el paquete stub antes de importar analizador
niveles_stub = SimpleNamespace(
    MODELO_DEFAULT=MODELO_DEFAULT,
    PROMPT_BASICO=PROMPT_BASICO,
    PROMPT_INTERMEDIO=PROMPT_INTERMEDIO,
    PROMPT_AVANZADO=PROMPT_AVANZADO,
    ResultadoBasico=ResultadoBasico,
    ResultadoIntermedio=ResultadoIntermedio,
    ResultadoAvanzado=ResultadoAvanzado,
)
sys.modules.setdefault("sentimiento", MagicMock())
sys.modules["sentimiento.niveles"] = niveles_stub  # type: ignore

# Stub de openai para que el import no falle si no está instalado
if "openai" not in sys.modules:
    openai_stub = MagicMock()
    openai_stub.OpenAI = MagicMock
    sys.modules["openai"] = openai_stub

# Añadir la raíz del proyecto al path si es necesario
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar los módulos bajo prueba
# Nota: ajusta los imports si tu estructura de paquetes difiere
import importlib, types

# Cargamos analizador dinámicamente para reutilizar el código fuente real
_analizador_path = Path(__file__).parent.parent / "sentimiento" / "analizador.py"
if _analizador_path.exists():
    spec = importlib.util.spec_from_file_location("sentimiento.analizador", _analizador_path)
    analizador_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analizador_mod)
else:
    # Si el archivo no existe en la ruta estándar, importamos directamente
    from sentimiento import analizador as analizador_mod  # type: ignore

analizar_basico = analizador_mod.analizar_basico
analizar_intermedio = analizador_mod.analizar_intermedio
analizar_avanzado = analizador_mod.analizar_avanzado
_llamar_api = analizador_mod._llamar_api
_truncar = analizador_mod._truncar

# Cargamos guardar dinámicamente
_guardar_path = Path(__file__).parent.parent / "almacenamiento" / "guardar.py"
if _guardar_path.exists():
    spec_g = importlib.util.spec_from_file_location("almacenamiento.guardar", _guardar_path)
    guardar_mod = importlib.util.module_from_spec(spec_g)
    spec_g.loader.exec_module(guardar_mod)
else:
    from almacenamiento import guardar as guardar_mod  # type: ignore

guardar_resultado = guardar_mod.guardar_resultado
guardar_multiples = guardar_mod.guardar_multiples


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def mock_cliente():
    """Cliente OpenAI completamente mockeado. Reutilizable en todos los tests."""
    cliente = MagicMock()
    return cliente


@pytest.fixture
def respuesta_api_factory(mock_cliente):
    """
    Factoría que configura mock_cliente para devolver un texto específico
    como respuesta de la API.

    Uso:
        respuesta_api_factory("positivo")
    """
    def _configurar(texto_respuesta: str):
        mensaje = MagicMock()
        mensaje.content = texto_respuesta
        choice = MagicMock()
        choice.message = mensaje
        mock_cliente.chat.completions.create.return_value.choices = [choice]
        return mock_cliente

    return _configurar


@pytest.fixture
def cliente_api_caida(mock_cliente):
    """Cliente que lanza RuntimeError en cualquier llamada a la API."""
    mock_cliente.chat.completions.create.side_effect = Exception("Connection refused")
    return mock_cliente


@pytest.fixture
def tmp_dir(tmp_path):
    """Directorio temporal de pytest para almacenar JSONs de prueba."""
    return tmp_path


# ===========================================================================
# HELPERS
# ===========================================================================

TEXTO_CORTO = "Me encanta este producto, es fantástico."
TEXTO_NEGATIVO = "Estoy muy decepcionado, no funciona para nada."
TEXTO_NEUTRO = "El paquete llegó en tres días."
TEXTO_LARGO = "A " * 200  # 400 caracteres → supera el límite de 100


# ===========================================================================
# TESTS – _truncar (función auxiliar)
# ===========================================================================

class TestTruncar:
    def test_texto_corto_no_se_trunca(self):
        assert _truncar("Hola mundo", 100) == "Hola mundo"

    def test_texto_exactamente_en_limite_no_se_trunca(self):
        texto = "x" * 100
        assert _truncar(texto, 100) == texto

    def test_texto_largo_se_trunca_con_puntos(self):
        texto = "x" * 200
        resultado = _truncar(texto, 100)
        assert resultado.endswith("...")
        assert len(resultado) == 103  # 100 chars + "..."

    def test_limite_personalizado(self):
        resultado = _truncar("abcdef", limite=3)
        assert resultado == "abc..."


# ===========================================================================
# TESTS – analizar_basico
# ===========================================================================

class TestAnalizarBasico:

    # ── Casos felices ────────────────────────────────────────────────────────

    def test_sentimiento_positivo(self, respuesta_api_factory):
        """CF1: la API devuelve 'positivo' → ResultadoBasico correcto."""
        cliente = respuesta_api_factory("positivo")
        resultado = analizar_basico(cliente, TEXTO_CORTO)

        assert resultado.nivel == "básico"
        assert resultado.sentimiento == "positivo"
        assert TEXTO_CORTO[:100] in resultado.texto_original

    def test_sentimiento_negativo(self, respuesta_api_factory):
        """CF2: la API devuelve 'negativo' → sentimiento en minúsculas."""
        cliente = respuesta_api_factory("NEGATIVO")
        resultado = analizar_basico(cliente, TEXTO_NEGATIVO)

        assert resultado.sentimiento == "negativo"

    def test_sentimiento_neutro(self, respuesta_api_factory):
        """CF3: la API devuelve 'neutro' para texto sin carga emocional."""
        cliente = respuesta_api_factory("neutro")
        resultado = analizar_basico(cliente, TEXTO_NEUTRO)

        assert resultado.sentimiento == "neutro"
        assert resultado.nivel == "básico"

    # ── Casos borde ──────────────────────────────────────────────────────────

    def test_texto_vacio(self, respuesta_api_factory):
        """CB1: texto vacío → se llama igualmente a la API y devuelve resultado."""
        cliente = respuesta_api_factory("neutro")
        resultado = analizar_basico(cliente, "")

        assert resultado.nivel == "básico"
        assert resultado.texto_original == ""
        cliente.chat.completions.create.assert_called_once()

    def test_texto_muy_largo(self, respuesta_api_factory):
        """CB2: texto muy largo → texto_original queda truncado a 103 chars."""
        cliente = respuesta_api_factory("positivo")
        resultado = analizar_basico(cliente, TEXTO_LARGO)

        assert len(resultado.texto_original) == 103
        assert resultado.texto_original.endswith("...")

    # ── Casos de error ───────────────────────────────────────────────────────

    def test_api_no_disponible(self, cliente_api_caida):
        """CE1: la API lanza excepción → se propaga como RuntimeError."""
        with pytest.raises(RuntimeError, match="Error en la llamada a la API"):
            analizar_basico(cliente_api_caida, TEXTO_CORTO)


# ===========================================================================
# TESTS – analizar_intermedio
# ===========================================================================

class TestAnalizarIntermedio:

    _RESPUESTA_VALIDA = json.dumps({
        "polaridad": "positiva",
        "emociones": ["alegría", "satisfacción"],
        "intensidad": 0.85,
    })

    # ── Casos felices ────────────────────────────────────────────────────────

    def test_parse_correcto(self, respuesta_api_factory):
        """CF4: JSON válido de la API → ResultadoIntermedio completo."""
        cliente = respuesta_api_factory(self._RESPUESTA_VALIDA)
        resultado = analizar_intermedio(cliente, TEXTO_CORTO)

        assert resultado.nivel == "intermedio"
        assert resultado.polaridad == "positiva"
        assert "alegría" in resultado.emociones
        assert resultado.intensidad == pytest.approx(0.85)

    def test_nivel_siempre_intermedio(self, respuesta_api_factory):
        """CF5: el campo 'nivel' se sobreescribe a 'intermedio' siempre."""
        respuesta = json.dumps({"polaridad": "negativa", "emociones": [], "intensidad": 0.2, "nivel": "otro"})
        cliente = respuesta_api_factory(respuesta)
        resultado = analizar_intermedio(cliente, TEXTO_NEGATIVO)

        assert resultado.nivel == "intermedio"

    def test_texto_original_truncado(self, respuesta_api_factory):
        """CF6: texto_original se trunca a 103 chars en textos largos."""
        cliente = respuesta_api_factory(self._RESPUESTA_VALIDA)
        resultado = analizar_intermedio(cliente, TEXTO_LARGO)

        assert resultado.texto_original.endswith("...")

    # ── Casos borde ──────────────────────────────────────────────────────────

    def test_texto_vacio(self, respuesta_api_factory):
        """CB3: texto vacío no interrumpe el flujo."""
        cliente = respuesta_api_factory(self._RESPUESTA_VALIDA)
        resultado = analizar_intermedio(cliente, "")

        assert resultado.texto_original == ""
        assert resultado.nivel == "intermedio"

    def test_respuesta_unicode_emociones(self, respuesta_api_factory):
        """CB4: emociones con caracteres Unicode/emoji no provocan errores."""
        respuesta = json.dumps({
            "polaridad": "positiva",
            "emociones": ["alegría 😊", "emoción ✨"],
            "intensidad": 1.0,
        })
        cliente = respuesta_api_factory(respuesta)
        resultado = analizar_intermedio(cliente, "Qué día tan bonito 😊")

        assert "alegría 😊" in resultado.emociones

    # ── Casos de error ───────────────────────────────────────────────────────

    def test_json_malformado(self, respuesta_api_factory):
        """CE2: JSON malformado → devuelve ResultadoIntermedio con campo error."""
        cliente = respuesta_api_factory("esto no es json {{{{")
        resultado = analizar_intermedio(cliente, TEXTO_CORTO)

        assert resultado.error is not None
        assert "parsear" in resultado.error.lower() or "json" in resultado.error.lower()
        assert resultado.respuesta_raw == "esto no es json {{{{"

    def test_api_no_disponible(self, cliente_api_caida):
        """CE3: API caída → RuntimeError."""
        with pytest.raises(RuntimeError):
            analizar_intermedio(cliente_api_caida, TEXTO_CORTO)


# ===========================================================================
# TESTS – analizar_avanzado
# ===========================================================================

class TestAnalizarAvanzado:

    _RESPUESTA_VALIDA = json.dumps({
        "fragmentos": ["Me encanta", "es fantástico"],
        "justificacion": "El texto contiene múltiples expresiones positivas.",
        "tonalidad": "entusiasta",
        "recomendacion": "Adecuado para testimonios de producto.",
    })

    # ── Casos felices ────────────────────────────────────────────────────────

    def test_parse_correcto(self, respuesta_api_factory):
        """CF7: JSON válido → ResultadoAvanzado con todos los campos."""
        cliente = respuesta_api_factory(self._RESPUESTA_VALIDA)
        resultado = analizar_avanzado(cliente, TEXTO_CORTO)

        assert resultado.nivel == "avanzado"
        assert resultado.tonalidad == "entusiasta"
        assert len(resultado.fragmentos) == 2
        assert resultado.justificacion is not None
        assert resultado.recomendacion is not None

    def test_nivel_siempre_avanzado(self, respuesta_api_factory):
        """CF8: el nivel siempre es 'avanzado' independientemente de la respuesta."""
        datos = json.loads(self._RESPUESTA_VALIDA)
        datos["nivel"] = "basico"  # intento de sobreescritura desde la API
        cliente = respuesta_api_factory(json.dumps(datos))
        resultado = analizar_avanzado(cliente, TEXTO_CORTO)

        assert resultado.nivel == "avanzado"

    # ── Casos borde ──────────────────────────────────────────────────────────

    def test_texto_muy_largo_truncado(self, respuesta_api_factory):
        """CB5: texto largo → texto_original truncado correctamente."""
        cliente = respuesta_api_factory(self._RESPUESTA_VALIDA)
        resultado = analizar_avanzado(cliente, TEXTO_LARGO)

        assert len(resultado.texto_original) <= 103

    def test_fragmentos_lista_vacia(self, respuesta_api_factory):
        """CB6: la API puede devolver 'fragmentos' como lista vacía."""
        respuesta = json.dumps({
            "fragmentos": [],
            "justificacion": "Sin fragmentos destacables.",
            "tonalidad": "neutro",
            "recomendacion": "N/A",
        })
        cliente = respuesta_api_factory(respuesta)
        resultado = analizar_avanzado(cliente, TEXTO_NEUTRO)

        assert resultado.fragmentos == []

    # ── Casos de error ───────────────────────────────────────────────────────

    def test_json_malformado(self, respuesta_api_factory):
        """CE4: JSON inválido → error capturado en campo error."""
        cliente = respuesta_api_factory("<respuesta inesperada>")
        resultado = analizar_avanzado(cliente, TEXTO_CORTO)

        assert resultado.error is not None
        assert resultado.respuesta_raw == "<respuesta inesperada>"

    def test_api_no_disponible(self, cliente_api_caida):
        """CE5: API no disponible → RuntimeError propagado."""
        with pytest.raises(RuntimeError, match="Error en la llamada a la API"):
            analizar_avanzado(cliente_api_caida, TEXTO_CORTO)


# ===========================================================================
# TESTS – _llamar_api (función interna)
# ===========================================================================

class TestLlamarApi:

    def test_devuelve_contenido_limpio(self, mock_cliente):
        """Verifica que strip() se aplica al contenido retornado."""
        mensaje = MagicMock()
        mensaje.content = "  positivo  \n"
        mock_cliente.chat.completions.create.return_value.choices = [
            MagicMock(message=mensaje)
        ]
        resultado = _llamar_api(mock_cliente, "sistema", "usuario")
        assert resultado == "positivo"

    def test_pasa_temperatura_cero(self, mock_cliente):
        """Garantiza que temperature=0.0 se envía siempre para reproducibilidad."""
        mensaje = MagicMock()
        mensaje.content = "ok"
        mock_cliente.chat.completions.create.return_value.choices = [
            MagicMock(message=mensaje)
        ]
        _llamar_api(mock_cliente, "s", "u")
        call_kwargs = mock_cliente.chat.completions.create.call_args
        assert call_kwargs.kwargs.get("temperature", None) == 0.0

    def test_excepcion_se_convierte_en_runtime_error(self, mock_cliente):
        """Cualquier excepción de la API se re-lanza como RuntimeError."""
        mock_cliente.chat.completions.create.side_effect = ValueError("bad request")
        with pytest.raises(RuntimeError, match="Error en la llamada a la API"):
            _llamar_api(mock_cliente, "s", "u")


# ===========================================================================
# TESTS – guardar_resultado y guardar_multiples
# ===========================================================================

class TestGuardarResultado:

    # ── Casos felices ────────────────────────────────────────────────────────

    def test_crea_archivo_json(self, tmp_dir):
        """CF9: guardar_resultado crea un archivo JSON en el directorio indicado."""
        datos = {"nivel": "básico", "sentimiento": "positivo"}
        ruta = guardar_resultado(datos, prefijo="test", directorio=tmp_dir)

        assert ruta.exists()
        assert ruta.suffix == ".json"

    def test_contenido_json_correcto(self, tmp_dir):
        """CF10: el JSON guardado se puede leer y coincide con el original."""
        datos = {"nivel": "avanzado", "tonalidad": "entusiasta"}
        ruta = guardar_resultado(datos, directorio=tmp_dir)

        cargado = json.loads(ruta.read_text(encoding="utf-8"))
        assert cargado["nivel"] == "avanzado"
        assert cargado["tonalidad"] == "entusiasta"

    def test_nombre_archivo_incluye_prefijo(self, tmp_dir):
        """CF11: el nombre del archivo comienza con el prefijo indicado."""
        ruta = guardar_resultado({"x": 1}, prefijo="mitest", directorio=tmp_dir)
        assert ruta.name.startswith("mitest_")

    def test_guardar_multiples(self, tmp_dir):
        """CF12: guardar_multiples envuelve la lista bajo la clave 'resultados'."""
        lista = [{"a": 1}, {"b": 2}]
        ruta = guardar_multiples(lista, prefijo="multi", directorio=tmp_dir)

        cargado = json.loads(ruta.read_text(encoding="utf-8"))
        assert "resultados" in cargado
        assert len(cargado["resultados"]) == 2

    # ── Casos borde ──────────────────────────────────────────────────────────

    def test_directorio_se_crea_si_no_existe(self, tmp_dir):
        """CB7: si el directorio no existe se crea automáticamente."""
        nuevo_dir = tmp_dir / "sub" / "directorio"
        assert not nuevo_dir.exists()

        ruta = guardar_resultado({"ok": True}, directorio=nuevo_dir)
        assert nuevo_dir.exists()
        assert ruta.exists()

    def test_resultado_vacio_es_valido(self, tmp_dir):
        """CB8: guardar un dict vacío produce un archivo JSON vacío '{}'."""
        ruta = guardar_resultado({}, directorio=tmp_dir)
        cargado = json.loads(ruta.read_text(encoding="utf-8"))
        assert cargado == {}

    # ── Casos de error ───────────────────────────────────────────────────────

    def test_tipo_no_serializable_lanza_type_error(self, tmp_dir):
        """CE6: un valor no serializable lanza TypeError con mensaje claro."""
        datos_invalidos = {"funcion": lambda x: x}
        with pytest.raises(TypeError, match="no serializables"):
            guardar_resultado(datos_invalidos, directorio=tmp_dir)

    def test_multiples_archivos_prefijos_distintos_no_colisionan(self, tmp_dir):
        """
        CE7: dos archivos con prefijos distintos no colisionan aunque se guarden
        en el mismo segundo (el prefijo diferencia los nombres).

        NOTA de diseño: _nombre_archivo_timestamp usa precisión de segundos.
        Si se necesita guardar varios resultados con el *mismo* prefijo en <1 s,
        la segunda escritura sobreescribe a la primera — comportamiento conocido.
        Para evitarlo, el orquestador debería usar prefijos únicos o añadir
        un sufijo aleatorio. Este test documenta el contrato actual.
        """
        ruta1 = guardar_resultado({"i": 1}, prefijo="alpha", directorio=tmp_dir)
        ruta2 = guardar_resultado({"i": 2}, prefijo="beta", directorio=tmp_dir)

        # Con prefijos distintos los nombres nunca colisionan
        assert ruta1 != ruta2
        assert json.loads(ruta1.read_text())["i"] == 1
        assert json.loads(ruta2.read_text())["i"] == 2


# ===========================================================================
# TESTS DE INTEGRACIÓN LIGERA
# (analizador + guardar, sin tocar disco real de producción)
# ===========================================================================

class TestIntegracionAnalizadorGuardar:

    def test_resultado_basico_se_persiste(self, respuesta_api_factory, tmp_dir):
        """
        Flujo completo: análisis básico → serialización del dataclass → JSON.
        """
        cliente = respuesta_api_factory("positivo")
        resultado = analizar_basico(cliente, TEXTO_CORTO)

        # Convertimos el dataclass a dict manualmente (como haría el orquestador)
        import dataclasses
        datos = dataclasses.asdict(resultado)
        ruta = guardar_resultado(datos, prefijo="basico", directorio=tmp_dir)

        cargado = json.loads(ruta.read_text(encoding="utf-8"))
        assert cargado["sentimiento"] == "positivo"
        assert cargado["nivel"] == "básico"

    def test_resultado_avanzado_se_persiste(self, respuesta_api_factory, tmp_dir):
        """
        Flujo completo: análisis avanzado → serialización → JSON verificable.
        """
        respuesta = json.dumps({
            "fragmentos": ["fantástico"],
            "justificacion": "Tono muy positivo.",
            "tonalidad": "entusiasta",
            "recomendacion": "Usar en marketing.",
        })
        cliente = respuesta_api_factory(respuesta)
        resultado = analizar_avanzado(cliente, TEXTO_CORTO)

        import dataclasses
        datos = dataclasses.asdict(resultado)
        ruta = guardar_resultado(datos, prefijo="avanzado", directorio=tmp_dir)

        cargado = json.loads(ruta.read_text(encoding="utf-8"))
        assert cargado["tonalidad"] == "entusiasta"
        assert cargado["nivel"] == "avanzado"