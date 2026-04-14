# 🧠 Memoria Final del Proyecto — ANALISIS_SENTIMIENTO

---

## 1. Contexto del código heredado

**Descripción del problema inicial:**

El archivo original `InicioSentimiento.py` (guardado en `Heredado/`) concentraba **todo el sistema de análisis de sentimiento en un único script monolítico**. Usaba la API de OpenAI (`gpt-4o-mini`) directamente desde cada función, sin abstracción alguna, y mezclaba en el mismo fichero la lógica de análisis, el parseo de respuestas, el cálculo de estadísticas y el código de demostración (`print` al nivel de módulo). Al importarse, el script se ejecutaba de inmediato produciendo llamadas reales a la API y salida en consola no controlada.

**Principales deficiencias detectadas:**

- **Ejecución involuntaria al importar:** el bloque de demostración (`print`, llamadas a funciones) estaba al nivel de módulo sin estar protegido por `if __name__ == "__main__":`, por lo que cualquier `import` del archivo disparaba llamadas reales a la API de OpenAI.
- **Acoplamiento directo a OpenAI:** las tres funciones de análisis (`básico`, `intermedio`, `avanzado`) instanciaban y llamaban al cliente de OpenAI directamente, haciendo imposible cambiar de proveedor o hacer pruebas sin coste real.
- **Estructura monolítica:** lógica de análisis, clasificación por niveles, procesamiento multi-texto y presentación de resultados convivían en el mismo archivo, violando el principio de responsabilidad única.
- **Gestión de errores incompleta:** el bloque `except (json.JSONDecodeError, Exception)` capturaba cualquier excepción silenciosamente y devolvía un diccionario con `"error"` sin registrar nada, dificultando el diagnóstico.
- **Sin persistencia:** los resultados solo se imprimían por consola; no existía ningún mecanismo para guardarlos ni recuperarlos.
- **Sin tests:** no había ningún archivo de pruebas, lo que impedía verificar el comportamiento de forma automatizada.
- **Credenciales sin validar:** la clave API se cargaba con `os.getenv` pero no se comprobaba si era `None` antes de instanciar el cliente, provocando un error críptico en tiempo de ejecución si el `.env` no existía.

**Esquema del flujo original:**

```text
InicioSentimiento.py
  │
  ├─ analizar_sentimiento_basico(texto)   ──► OpenAI API ──► print()
  ├─ analizar_sentimiento_intermedio(texto) ──► OpenAI API ──► print()
  ├─ analizar_sentimiento_avanzado(texto)  ──► OpenAI API ──► print()
  └─ analizar_sentimiento_multitexto(textos) ──► bucle intermedio ──► print()

[Todo ejecutado al importar, sin tests, sin almacenamiento]
```

---

## 2. Análisis y planificación

**Objetivos de la refactorización:**

- Eliminar la ejecución involuntaria al importar protegiendo el código de demostración con `if __name__ == "__main__":`.
- Desacoplar la lógica de análisis de la API concreta mediante una capa de abstracción (`analizador.py`).
- Separar responsabilidades en módulos independientes y cohesionados.
- Añadir persistencia de resultados en JSON y TXT con nombre basado en marca de tiempo.
- Introducir una suite de tests automatizados con `pytest`.
- Proporcionar una interfaz gráfica sencilla que sustituya a los `print` de demostración.

**Plan de trabajo:**

1. **Análisis del código heredado** — lectura crítica de `InicioSentimiento.py` e identificación de todos los problemas.
2. **Diseño de la nueva arquitectura** — definición de módulos, interfaces y dependencias antes de escribir código.
3. **Implementación del paquete `sentimiento/`** — `analizador.py`, `niveles.py`, `multitexto.py` y `cliente.py` como orquestador.
4. **Implementación del paquete `almacenamiento/`** — `guardar.py` y `leer.py` con soporte JSON y TXT.
5. **Interfaz gráfica** — `InterfazEmpresaGUI.py` con Tkinter, desacoplada de la lógica.
6. **Tests** — `test_analizador.py` y `test_guardar.py` con fixtures en `conftest.py`.
7. **CI/CD** — pipeline en `.github/workflows/pipeline.yml` que ejecuta `pytest` en cada push.

---

## 3. Modularización del código

**Nueva estructura del proyecto:**

```bash
ANALISIS_SENTIMIENTO/
│
├── main.py                        # Punto de entrada; lanza la GUI
├── InterfazEmpresaGUI.py          # Capa de presentación (Tkinter)
│
├── sentimiento/
│   ├── __init__.py
│   ├── analizador.py              # Motor NLP; abstrae la API externa
│   ├── niveles.py                 # Clasifica score → POSITIVO/NEUTRAL/NEGATIVO
│   ├── multitexto.py              # Procesamiento en batch
│   └── cliente.py                 # Orquestador del paquete
│
├── almacenamiento/
│   ├── __init__.py
│   ├── guardar.py                 # Escribe JSON y TXT con marca de tiempo
│   ├── leer.py                    # Lee y lista análisis guardados
│   └── resultados/
│       ├── json/
│       └── txt/
│
├── Heredado/
│   └── InicioSentimiento.py       # Código original (solo referencia)
│
├── scripts/
│   └── check_folders.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_analizador.py
    └── test_guardar.py
```

**Justificación de la nueva estructura:**

La separación en dos paquetes (`sentimiento/` y `almacenamiento/`) permite modificar el motor de análisis o el formato de persistencia de forma totalmente independiente. El módulo `niveles.py` se puede ajustar sin tocar el motor NLP; `guardar.py` se puede extender con nuevos formatos (CSV, base de datos) sin afectar a la lógica de negocio. Esta organización reduce el acoplamiento y hace que el proyecto sea escalable para incorporar nuevos proveedores de NLP o nuevas interfaces de usuario.

**Principales módulos y su función:**

- `sentimiento/analizador.py`: Encapsula la llamada a la API (OpenAI u otra) y devuelve siempre el mismo formato de diccionario, independientemente del proveedor.
- `sentimiento/niveles.py`: Traduce la puntuación numérica a una etiqueta cualitativa (POSITIVO / NEUTRAL / NEGATIVO) según umbrales configurables.
- `sentimiento/multitexto.py`: Itera sobre una lista de textos delegando en `analizador.py` y agrega estadísticas.
- `sentimiento/cliente.py`: Único punto de entrada de la capa de negocio; coordina análisis, clasificación y guardado opcional.
- `almacenamiento/guardar.py`: Serializa los resultados en JSON y TXT, nombrando los archivos con `analisis_YYYY-MM-DD_HHmmss`.
- `almacenamiento/leer.py`: Deserializa archivos guardados y los lista en orden cronológico inverso.

---

## 4. Implementación del Pipeline

**Descripción del flujo actual:**

```text
[Usuario - GUI]
      │  texto en bruto
      ▼
[InterfazEmpresaGUI.py]
      │  llamada a cliente.analizar_texto(texto, guardar=True)
      ▼
[sentimiento/cliente.py]  ◄── orquestador
      ├── sentimiento/analizador.py  →  score + detalles
      ├── sentimiento/niveles.py     →  etiqueta (POSITIVO/NEUTRAL/NEGATIVO)
      └── almacenamiento/guardar.py  →  JSON + TXT en disco  (opcional)
      │  resultado completo
      ▼
[InterfazEmpresaGUI.py]  →  muestra nivel, score y detalles al usuario
```

**Gestión de errores y excepciones:**

- La clave API se valida al inicio de `analizador.py`; si es `None` se lanza `EnvironmentError` con un mensaje claro antes de intentar cualquier llamada.
- Los errores de parseo JSON se registran con el módulo `logging` (nivel `WARNING`) y se propaga una excepción tipada (`ValueError`) en lugar de devolver un diccionario con `"error"`.
- Los errores de escritura en disco en `guardar.py` se capturan con `OSError` y se registran sin interrumpir la ejecución del análisis.
- Los tests usan `monkeypatch` para evitar llamadas reales a la API y `tmp_path` para no contaminar el directorio de resultados.

---

## 5. Cambios de código realizados

| Antes (`InicioSentimiento.py`) | Después | Motivo |
|---|---|---|
| Código de demostración al nivel de módulo | Protegido con `if __name__ == "__main__":` en `main.py` | Evita ejecución involuntaria al importar |
| `client = OpenAI(...)` dentro de cada función | Instancia única en `analizador.py`, inyectable en tests | Elimina acoplamiento y permite mocking |
| Tres funciones separadas: básico, intermedio, avanzado | Un único `Analizador.analizar(texto, nivel)` con parámetro de nivel | API uniforme y extensible |
| `except (json.JSONDecodeError, Exception)` silencioso | `except json.JSONDecodeError` con `logging.warning` y re-raise | Diagnóstico claro, sin enmascarar errores |
| Resultados solo por `print()` | `almacenamiento/guardar.py` escribe JSON + TXT en disco | Persistencia real y recuperable |
| Sin tests | `tests/test_analizador.py` + `tests/test_guardar.py` con pytest | Verificación automática en CI |
| Sin interfaz | `InterfazEmpresaGUI.py` con Tkinter | Experiencia de usuario real |
| Variables `r`, `res` en bucles | `resultado`, `resultado_individual` | Mayor claridad y mantenibilidad |

**Medidas de validación:**

- `pytest -v` con cobertura (`--cov=sentimiento --cov=almacenamiento`) ejecutado localmente y en el pipeline de CI.
- Comparación manual de resultados entre `InicioSentimiento.py` (original) y `cliente.py` (refactorizado) con los mismos textos de prueba.
- Verificación de que ningún test realiza llamadas reales a la API (mocking con `unittest.mock.patch`).

---

## 6. Evaluación final

**Resultados obtenidos:**

Tras la refactorización el proyecto presenta una arquitectura clara en capas: presentación (`InterfazEmpresaGUI.py`), negocio (`sentimiento/`) y persistencia (`almacenamiento/`). El código es ahora testeable sin coste de API, los errores son rastreables gracias al logging, y los resultados quedan guardados en disco con un nombre que facilita su recuperación. El pipeline de CI garantiza que ningún cambio futuro rompa el comportamiento esperado.

**Desafíos encontrados:**

- **Compatibilidad del formato de respuesta:** la API de OpenAI no siempre devuelve JSON válido aunque se le pida explícitamente; fue necesario añadir un mecanismo de reintento con temperatura 0 y un fallback de parseo robusto.
- **Aislamiento en tests:** replicar el comportamiento de la API sin llamadas reales requirió diseñar fixtures cuidadosas en `conftest.py` que devuelvan respuestas plausibles.
- **Nombres de archivo únicos:** garantizar que dos análisis ejecutados en el mismo segundo no sobreescriban el mismo archivo obligó a añadir un sufijo aleatorio de dos dígitos al final de la marca de tiempo.

---

## 7. Conclusión personal

Este proyecto ha demostrado que refactorizar código heredado no consiste solo en "limpiar" sino en **replantear el diseño desde los principios**. El mayor aprendizaje ha sido entender que un código que "funciona" puede seguir siendo problemático si no es testeable, si acopla responsabilidades o si se ejecuta de forma no controlada. La separación en módulos, la introducción de tests y la automatización del pipeline no solo mejoran la calidad del software, sino que reducen el miedo a hacer cambios futuros, que es en última instancia el valor más importante del buen diseño.