# 🧠 ANALISIS_SENTIMIENTO

![CI Pipeline](https://github.com/TU_USUARIO/ANALISIS_SENTIMIENTO/actions/workflows/pipeline.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![pytest](https://img.shields.io/badge/tests-pytest-red?logo=pytest)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Sistema modular de **análisis de sentimiento** en Python que clasifica textos en tres niveles cualitativos (POSITIVO, NEUTRAL, NEGATIVO) con soporte para análisis en batch, persistencia automática de resultados e interfaz gráfica de usuario.

---

# 📋 Descripción

El proyecto recibe texto libre, lo analiza usando un motor NLP configurable y devuelve:

- **Nivel cualitativo:** POSITIVO / NEUTRAL / NEGATIVO
- **Score numérico:** polaridad en el rango `[-1.0, 1.0]`
- **Desglose de emociones:** porcentaje de positividad, neutralidad y negatividad
- **Persistencia automática:** cada análisis se guarda en `almacenamiento/resultados/` en formato JSON y TXT

---

# ⚙️ Instalación

## Requisitos previos

- Python 3.11 o superior
- `pip`

## Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/ANALISIS_SENTIMIENTO.git
cd ANALISIS_SENTIMIENTO

# 2. Crear y activar entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env y añade tu clave: OPENAI_API_KEY=sk-...
```

---

# 🚀 Uso

## Interfaz gráfica

```bash
python main.py
```

Se abrirá la ventana de `InterfazEmpresaGUI`. Escribe o pega un texto y pulsa **Analizar**.

## Uso programático

```python
from sentimiento.cliente import ClienteSentimiento

cliente = ClienteSentimiento()

# Análisis simple
resultado = cliente.analizar_texto("El producto es fantástico.", guardar=True)
print(resultado["nivel"])   # POSITIVO
print(resultado["score"])   # 0.87

# Análisis en batch
textos = ["Excelente servicio", "Normal, sin más", "Pésima experiencia"]
resultados = cliente.analizar_multiples(textos, guardar=False)
for r in resultados:
    print(r["nivel"], r["score"])
```

### Leer análisis guardados

```python
from almacenamiento.leer import listar_resultados, leer_resultado

archivos = listar_resultados()          # lista ordenada, más reciente primero
datos = leer_resultado(archivos[0])
print(datos["nivel"], datos["timestamp"])
```

---

# 📁 Estructura de carpetas

```
ANALISIS_SENTIMIENTO/
│
├── .github/
│   └── workflows/
│       └── pipeline.yml           # CI: ejecuta pytest en cada push/PR
│
├── almacenamiento/
│   ├── __init__.py
│   ├── guardar.py                 # Escribe JSON + TXT con marca de tiempo
│   ├── leer.py                    # Lee y lista análisis guardados
│   └── resultados/
│       ├── json/                  # analisis_YYYY-MM-DD_HHmmss.json
│       │   └── .gitkeep
│       └── txt/                   # analisis_YYYY-MM-DD_HHmmss.txt
│           └── .gitkeep
│
├── Heredado/
│   └── InicioSentimiento.py       # Código original (solo referencia)
│
├── scripts/
│   └── check_folders.py           # Verifica que los directorios existen
│
├── sentimiento/
│   ├── __init__.py
│   ├── analizador.py              # Motor NLP; abstrae la API externa
│   ├── cliente.py                 # Orquestador del paquete
│   ├── multitexto.py              # Procesamiento en batch
│   └── niveles.py                 # Score → POSITIVO / NEUTRAL / NEGATIVO
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures compartidas (cliente, resultado_ejemplo)
│   ├── test_analizador.py         # Tests del motor NLP
│   └── test_guardar.py            # Tests del sistema de almacenamiento
│
├── .gitignore
├── conftest.py
├── InterfazEmpresaGUI.py          # Interfaz gráfica (Tkinter)
├── LICENSE
├── main.py                        # Punto de entrada
├── pytest.ini
├── README.md
├── requirements.txt
└── setup.cfg
```

### Formato de los archivos en `resultados/`

Cada análisis genera dos archivos con el mismo sufijo de fecha/hora:

**JSON** (`analisis_2026-04-14_130903.json`):
```json
{
  "timestamp": "2026-04-14T13:09:03",
  "texto_original": "El producto es fantástico.",
  "score": 0.87,
  "nivel": "POSITIVO",
  "detalles": {
    "positivo": 0.87,
    "neutral":  0.10,
    "negativo": 0.03
  }
}
```

**TXT** (`analisis_2026-04-14_130903.txt`):
```
========================================
ANÁLISIS DE SENTIMIENTO
Fecha: 2026-04-14 13:09:03
========================================
Texto:      El producto es fantástico.
----------------------------------------
Nivel:      POSITIVO
Score:      0.87
Positivo:   87%
Neutral:    10%
Negativo:    3%
========================================
```

---

## 🧪 Ejecutar los tests

```bash
# Todos los tests
pytest

# Con salida detallada
pytest -v

# Con reporte de cobertura
pytest --cov=sentimiento --cov=almacenamiento --cov-report=term-missing

# Un archivo concreto
pytest tests/test_analizador.py -v

# Un test específico
pytest tests/test_analizador.py::test_sentimiento_positivo -v
```

Los tests **no realizan llamadas reales a la API** — todas las respuestas externas están mockeadas mediante `unittest.mock.patch` en `conftest.py`.

---

## 🔁 Pipeline CI

El workflow `.github/workflows/pipeline.yml` se ejecuta automáticamente en cada **push** y **pull request** sobre cualquier rama:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest --cov=sentimiento --cov=almacenamiento
```

El badge en la cabecera de este README refleja el estado del último pipeline.

> **Nota:** sustituye `TU_USUARIO` en la URL del badge y del clone por tu nombre de usuario de GitHub.

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE MIT) para más detalles.