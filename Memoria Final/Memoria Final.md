# Memoria Final — Refactorización del Análisis de Sentimiento
 
## 1. ¿Por qué el código original estaba mal configurado?
 
El código InicioSentimiento.py presentaba los siguientes problemas críticos:
 
### Problema 1: Código monolítico sin modularización
Todo el proyecto estaba en un único archivo. Esto viola el Principio
de Responsabilidad Única (SRP). Cuando el proyecto crece, se vuelve
imposible de mantener porque cualquier cambio afecta a todo.
 
### Problema 2: Cliente global creado al importar
La línea `client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))` se
ejecutaba al importar el módulo. Esto causa dos problemas:
  - Si no existe la variable de entorno, el import falla.
  - Es imposible hacer tests sin una clave API real.
 
### Problema 3: Ejecución directa mezclada con la lógica
Las líneas `print(analizar_sentimiento_basico(texto_prueba))` estaban
al nivel del módulo. Al importar el archivo en otro script, estas
líneas se ejecutaban automáticamente. Efecto secundario no controlado.
 
### Problema 4: Sin persistencia de datos
Los resultados se imprimían por consola y se perdían. No había forma
de recuperar análisis anteriores ni de auditar el sistema.
 
### Problema 5: Sin manejo de errores
No había ningún try/except. Si la API de OpenAI fallaba, el programa
crasheaba con un error no informativo para el usuario.
 
### Problema 6: Sin tests
No había forma de verificar que el código funcionaba correctamente.
Cualquier cambio podía romper el sistema sin aviso.
 
---
 
## 2. Cambios realizados
 
| Cambio | Archivo creado | Motivo |
|--------|---------------|--------|
| Extraer cliente OpenAI | sentimiento/cliente.py | Testeable, lazy init |
| Separar niveles de análisis | sentimiento/niveles.py | SRP, un nivel por función |
| Coordinar análisis | sentimiento/analizador.py | Punto único de entrada |
| Guardar resultados | almacenamiento/guardar.py | Persistencia y trazabilidad |
| Leer historial | almacenamiento/leer.py | Recuperación de análisis |
| Tests unitarios | tests/test_analizador.py | Verificación automática |
| Pipeline CI/CD | .github/workflows/ci.yml | Validación en cada push |
| Interfaz gráfica | InicioSentimiento.py | GUI profesional con Tkinter |
 
---
 
## 3. Decisiones de diseño
 
- Usé `pathlib.Path` en lugar de `os.path` por ser más moderno y legible.
- Los archivos se nombran con timestamp para no sobreescribir análisis anteriores.
- Los mocks en los tests evitan consumir créditos de la API en cada test run.
- El ci.yml incluye bandit para detectar vulnerabilidades de seguridad.
 
---
 
## 4. Conclusión
 
El código original funcionaba, pero no era profesional. La diferencia entre
código funcional y código profesional es exactamente este ejercicio:
modularización, tests, CI/CD, persistencia y documentación.
Cada bloque añade una capa de calidad que protege el proyecto a largo plazo.