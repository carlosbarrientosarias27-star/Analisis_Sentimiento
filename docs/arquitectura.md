# Arquitectura del Sistema
ANALISIS_SENTIMIENTO es un sistema modular de análisis de sentimiento en Python. Los módulos se organizan en capas bien definidas con responsabilidades separadas.

## 1. Diagrama de Módulos
```
main.py  (punto de entrada)
    └── InterfazEmpresaGUI.py  (interfaz gráfica)
         └── sentimiento/cliente.py  (orquestador)
              ├── sentimiento/analizador.py  (motor NLP)
              ├── sentimiento/niveles.py  (clasificador)
              ├── sentimiento/multitexto.py  (batch)
              └── almacenamiento/guardar.py  (persistencia)
                   └── almacenamiento/leer.py  (lectura)
```

## 2. Descripción de Módulos

| Módulo / Archivo | Responsabilidad Principal | Descripción Detallada |
| :--- | :--- | :--- |
| **`main.py`** | Punto de entrada | Inicializa la aplicación y lanza la interfaz gráfica. Gestiona la configuración global y el ciclo de vida del proceso. |
| **`InterfazEmpresaGUI.py`** | Interfaz Gráfica | Capa de presentación (Tkinter). Captura el texto de entrada del usuario y delega el análisis a `cliente.py`. |
| **`sentimiento/cliente.py`** | Orquestador | Punto de entrada de la capa de negocio. Coordina al analizador, clasifica niveles y gestiona la persistencia. |
| **`sentimiento/analizador.py`** | Motor NLP | Encapsula la librería de análisis (VADER, TextBlob, etc.). Expone una API uniforme para el orquestador. |
| **`sentimiento/niveles.py`** | Clasificador | Traduce puntuaciones numéricas a etiquetas cualitativas (POSITIVO / NEUTRAL / NEGATIVO) según umbrales. |
| **`sentimiento/multitexto.py`** | Procesamiento Batch | Permite analizar listas de textos en una sola llamada, delegando el procesamiento individual al motor NLP. |
| **`almacenamiento/guardar.py`** | Persistencia | Escribe los resultados en disco (JSON/TXT) con marcas de tiempo, desacoplando la serialización. |
| **`almacenamiento/leer.py`** | Lectura | Lee y deserializa los archivos generados para recuperar análisis anteriores y mostrarlos en la interfaz. |

## 3. Flujo de Datos

| Paso | Descripción |
| :--- | :--- |
| **1 — Entrada** | El usuario escribe texto en `InterfazEmpresaGUI.py` y pulsa 'Analizar'. |
| **2 — Delegación** | La GUI llama a `cliente.py` con el texto en bruto. |
| **3 — Análisis** | `cliente.py` pasa el texto a `analizador.py`; éste devuelve score y metadatos. |
| **4 — Nivel** | `cliente.py` pasa el score a `niveles.py`; recibe la etiqueta (POSITIVO, etc.). |
| **5 — Resultado** | `cliente.py` ensambla el objeto resultado y lo devuelve a la GUI. |
| **6 — Guardado** | Opcionalmente, `cliente.py` llama a `guardar.py` para persistir en disco. |
| **7 — Presentación** | La GUI muestra nivel, score y detalles al usuario. |

## 4. Principios de Diseño
•	Separación de responsabilidades: cada módulo tiene una única razón para cambiar.
•	Inyección implícita de dependencias: cliente.py importa directamente los módulos; para tests se pueden parchear con unittest.mock.
•	Sin estado global: los resultados se pasan como valores de retorno, no como variables globales.
•	Almacenamiento desacoplado: la capa de negocio no sabe nada del formato de archivo.
