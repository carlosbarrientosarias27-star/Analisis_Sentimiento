# Sistema de Almacenamiento
El módulo almacenamiento/ gestiona la persistencia de los análisis en dos formatos complementarios: JSON (para consumo programático) y TXT (para lectura humana).

## 1. Estructura de Directorios
```
almacenamiento/
├── __init__.py
├── guardar.py          # escritura de resultados
├── leer.py             # lectura de resultados
└── resultados/
    ├── json/           # archivos .json
    │   └── .gitkeep
    └── txt/            # archivos .txt
        └── .gitkeep
```

## 2. Convención de Nombres
Patrón:   analisis_YYYY-MM-DD_HHmmss.{json|txt}
Ejemplo:  analisis_2026-04-14_130903.json
          analisis_2026-04-14_131023.txt

Los archivos JSON y TXT de un mismo análisis comparten exactamente
el mismo sufijo de fecha/hora, lo que los vincula sin metadatos extra.

## 3. Formato JSON
Cada archivo JSON contiene un objeto con los campos:
{
  "timestamp": "2026-04-14T13:09:03",
  "texto_original": "El producto es fantástico y muy útil.",
  "score": 0.82,
  "nivel": "POSITIVO",
  "detalles": {
    "positivo": 0.82,
    "neutral":  0.14,
    "negativo": 0.04
  }
}

### Descripción de cada campo:

| Parámetro | Descripción / Tipo |
| :--- | :--- |
|**timestamp**|	Fecha y hora ISO 8601 del momento del análisis. |
|**texto_original**|	Cadena de texto enviada por el usuario sin modificar.|
|**score**|	Puntuación compuesta en el rango [-1.0, 1.0] o [0.0, 1.0]. |
|**nivel**|	Etiqueta cualitativa: POSITIVO, NEUTRAL o NEGATIVO. |
|**detalles**|	Desglose de probabilidades por categoría (suma = 1.0). | 

## 4. Formato TXT
El archivo TXT es una representación legible del mismo análisis:
========================================
ANÁLISIS DE SENTIMIENTO
Fecha: 2026-04-14 13:09:03
========================================
Texto: El producto es fantástico y muy útil.
----------------------------------------
Nivel:      POSITIVO
Score:      0.82
Positivo:   82%
Neutral:    14%
Negativo:    4%
========================================

## 5. guardar.py — API de escritura
La función principal es guardar_resultado(resultado). Recibe el diccionario de resultado, genera la marca de tiempo, y escribe ambos formatos de forma atómica.

from almacenamiento.guardar import guardar_resultado

resultado = {
    "texto_original": "Texto a analizar.",
    "score": 0.75,
    "nivel": "POSITIVO",
    "detalles": {"positivo":0.75,"neutral":0.20,"negativo":0.05}
}

rutas = guardar_resultado(resultado)
# rutas["json"] -> "almacenamiento/resultados/json/analisis_2026-04-14_XXXXXX.json"
# rutas["txt"]  -> "almacenamiento/resultados/txt/analisis_2026-04-14_XXXXXX.txt"

## 6. leer.py — API de lectura
Permite recuperar análisis guardados anteriormente. Devuelve el mismo diccionario que se pasó a guardar_resultado.

from almacenamiento.leer import leer_resultado, listar_resultados

# Listar todos los análisis disponibles (orden cronológico inverso)
archivos = listar_resultados()   # lista de rutas JSON

# Leer un análisis concreto
datos = leer_resultado(archivos[0])
print(datos["nivel"])   # "POSITIVO"

## 7. Notas de Implementación
•	Los directorios resultados/json/ y resultados/txt/ se crean automáticamente si no existen.
•	La marca de tiempo usa la hora local del sistema en formato strftime('%Y-%m-%d_%H%M%S').
•	Los .gitkeep en cada directorio garantizan que las carpetas vacías se versionan en Git.
•	Codificación de escritura: UTF-8 con BOM desactivado para máxima compatibilidad.
