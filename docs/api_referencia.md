# Referencia de API
Documentación de todas las funciones y clases públicas del proyecto ANALISIS_SENTIMIENTO.

## sentimiento.analizador
Analizador.analizar(texto)
Analiza el sentimiento de una cadena de texto y devuelve un diccionario con el score y el desglose por categorías.
Parámetro	Descripción / Tipo
texto	str — Texto en lenguaje natural a analizar. Longitud máxima recomendada: 512 tokens.
Retorna	dict — { 'score': float, 'positivo': float, 'neutral': float, 'negativo': float }

from sentimiento.analizador import Analizador

a = Analizador()
res = a.analizar("Me encanta este producto")
# {"score": 0.88, "positivo": 0.88, "neutral": 0.09, "negativo": 0.03}

## sentimiento.niveles
clasificar_nivel(score)
Convierte un score numérico en una etiqueta cualitativa.
Parámetro	Descripción / Tipo
score	float — Puntuación de sentimiento. Rango esperado: [-1.0, 1.0].
Retorna	str — "POSITIVO", "NEUTRAL" o "NEGATIVO".

Umbrales por defecto:
Parámetro	Descripción / Tipo
score > 0.05	"POSITIVO"
-0.05 ≤ score ≤ 0.05	"NEUTRAL"
score < -0.05	"NEGATIVO"

from sentimiento.niveles import clasificar_nivel

print(clasificar_nivel(0.88))   # "POSITIVO"
print(clasificar_nivel(0.00))   # "NEUTRAL"
print(clasificar_nivel(-0.50))  # "NEGATIVO"

## sentimiento.cliente
ClienteSentimiento.analizar_texto(texto, guardar=False)
Método principal del orquestador. Ejecuta el pipeline completo: análisis → nivel → (opcional) guardado.
Parámetro	Descripción / Tipo
texto	str — Texto a analizar.
guardar	bool — Si True, persiste el resultado en disco. Por defecto: False.
Retorna	dict — Objeto resultado completo con campos: texto_original, score, nivel, detalles, timestamp.

from sentimiento.cliente import ClienteSentimiento

cliente = ClienteSentimiento()
resultado = cliente.analizar_texto("Servicio pésimo.", guardar=True)
print(resultado["nivel"])   # "NEGATIVO"
print(resultado["score"])   # -0.71

ClienteSentimiento.analizar_multiples(textos, guardar=False)
Delega en multitexto.py para procesar una lista de textos en batch.
Parámetro	Descripción / Tipo
textos	list[str] — Lista de textos a analizar.
guardar	bool — Guarda cada resultado individualmente si es True.
Retorna	list[dict] — Lista de objetos resultado, en el mismo orden que la entrada.

textos = ["Excelente", "Regular", "Malísimo"]
resultados = cliente.analizar_multiples(textos)
for r in resultados:
    print(r["nivel"], r["score"])

## almacenamiento.guardar
guardar_resultado(resultado)
Parámetro	Descripción / Tipo
resultado	dict — Objeto resultado devuelto por ClienteSentimiento.analizar_texto().
Retorna	dict — { "json": str, "txt": str } con las rutas absolutas de los archivos creados.

from almacenamiento.guardar import guardar_resultado

rutas = guardar_resultado(resultado)
print(rutas["json"])  # ".../resultados/json/analisis_2026-04-14_130903.json"

## almacenamiento.leer
listar_resultados(formato='json')
Parámetro	Descripción / Tipo
formato	"json" | "txt" — Subcarpeta a listar. Por defecto: "json".
Retorna	list[str] — Rutas de los archivos ordenadas de más reciente a más antiguo.

## leer_resultado(ruta)
Parámetro	Descripción / Tipo
ruta	str | Path — Ruta al archivo JSON a leer.
Retorna	dict — Objeto resultado deserializado (misma estructura que guardar_resultado).

from almacenamiento.leer import listar_resultados, leer_resultado

archivos = listar_resultados()
ultimo = leer_resultado(archivos[0])
print(ultimo["nivel"])  # "POSITIVO"

## Heredado.InicioSentimiento
Módulo legacy incluido por compatibilidad retroactiva.
No usar en código nuevo; está siendo reemplazado por sentimiento/cliente.py.
InicioSentimiento.iniciar(texto)
Parámetro	Descripción / Tipo
texto	str — Texto a analizar (API legacy).
Retorna	tuple — (nivel: str, score: float)
