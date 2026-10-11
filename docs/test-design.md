# Diseño de pruebas

El proyecto tiene **345 pruebas automáticas** con `pytest` que cubren las cuatro etapas del
pipeline y su integración. Se ejecutan con:

```bash
pytest -q
```

Configuración en `pytest.ini`: `pythonpath = .` (para importar `src`) y `testpaths = tests`.

## 1. Estrategia

Cada etapa se prueba de forma aislada y después todas juntas:

1. **Pruebas unitarias por etapa**: cada módulo se verifica con entradas controladas.
2. **Casos negativos y de borde** en cada etapa, no solo el camino feliz.
3. **Pruebas parametrizadas** donde el mismo comportamiento se repite sobre muchos datos
   (por ejemplo, todos los alias de las familias del FST, o todas las combinaciones de skills de un
   perfil).
4. **Pruebas de integración** que recorren el pipeline completo, del texto del CV al DSL, HTML y
   Markdown.

La estructura de `tests/` replica la de `src/`, de modo que cada módulo tiene su archivo de pruebas.

## 2. Cobertura por módulo

| Etapa | Archivo | Pruebas | Qué verifica |
|---|---|---:|---|
| 1. Extracción | `tests/extraction/test_regex_extractor.py` | 20 | Correo, teléfono, años de experiencia, educación y skills crudas; ausencia de cada dato; formatos distintos. |
| 1. Extracción | `tests/extraction/test_name_extractor.py` | 15 | Detección del nombre; rechazo de líneas que no son un nombre (minúsculas, encabezados). |
| 2. Normalización | `tests/normalization/test_transducers.py` | 10 | Construcción de los FST: un transductor por familia, detección de alias ambiguos. |
| 2. Normalización | `tests/normalization/test_normalizer.py` | 77 | Alias → token canónico, insensibilidad a mayúsculas, idempotencia, limpieza de ruido (`Git.`, viñetas), desconocidas, trazabilidad. |
| 2. Normalización | `tests/normalization/test_sorter.py` | 27 | Orden canónico por perfil, descarte de skills ajenas, agrupación y categorías faltantes. |
| 3. Clasificación | `tests/classification/test_profile_dfa.py` | 49 | Construcción de los DFA de Full Stack, ML y QA; aceptación y rechazo por categorías; independencia del orden. |
| 3. Clasificación | `tests/classification/test_data_analyst.py` | 19 | El DFA de Data Analyst, incluido su caso de categoría opcional. |
| 3. Clasificación | `tests/classification/test_classifier.py` | 25 | `classify_profile`, `classify_candidate` y `accepted_profiles` sobre los cuatro perfiles. |
| 4. Gramática | `tests/grammar/test_builder.py` | 12 | Texto del DSL, escape de comillas, omisión de valores inválidos, `parse_years`. |
| 4. Gramática | `tests/grammar/test_validator.py` | 36 | Programas válidos e inválidos, errores sintácticos y reglas semánticas. |
| 4. Gramática | `tests/grammar/test_resume_integration.py` | 35 | Parseo completo del DSL y modelo resultante. |
| Integración | `tests/pipeline/test_pipeline.py` | 20 | CV de texto a clasificación, DSL, HTML y Markdown; CV vacío; candidatos de cada perfil. |
| | **Total** | **345** | |

## 3. Casos negativos y de borde considerados

| Etapa | Casos |
|---|---|
| Extracción | CV sin correo o sin teléfono; sin años de experiencia; texto vacío; nombre en minúsculas. |
| FST | Alias en distintas mayúsculas (`react`, `REACT`, `React`); variantes con punto (`Node.js`); skill con puntuación final (`Git.`); skill desconocida; cadena vacía. |
| Orden | Skills que no pertenecen al perfil (se descartan); skills en desorden. |
| Autómatas | Falta una categoría obligatoria (rechazo); skills repetidas; orden distinto de entrada (mismo resultado); categoría opcional presente o ausente; lista vacía. |
| Gramática | Llaves sin cerrar; bloques faltantes o desordenados; correo o teléfono mal formados; años fuera de rango (0–60); skills duplicadas; perfil repetido en la clasificación; nombre vacío. |
| Pipeline | CV vacío; CV con skills desconocidas; candidato que no cumple ningún perfil; candidato aceptado por un perfil. |

## 4. Ejemplos de evidencia manual

Además de las pruebas automáticas, la carpeta `data/examples/` contiene CVs de muestra que se
pueden cargar en la UI o pasar por la consola:

```bash
python -m src.main data/examples/sample_resume.txt
```

| Caso | Resultado esperado |
|---|---|
| Full Stack completo | `FULL_STACK_DEVELOPER: ACCEPTED`, los demás `REJECTED`. |
| Perfil de QA (con skills ajenas como COBOL) | `QA_ENGINEER: ACCEPTED`; `COBOL` y `Fortran` quedan como desconocidas. |
| CV sin skills | Los cuatro perfiles `REJECTED`; el DSL se genera con `skills { }` y es válido. |

## 5. Cómo se ejecutan

```bash
pytest -q                                   # toda la suite
pytest tests/normalization -q               # una etapa
pytest tests/classification/test_classifier.py -q   # un archivo
pytest -k "full_stack" -q                   # por nombre
```

## 6. Resultado

```
345 passed
```
