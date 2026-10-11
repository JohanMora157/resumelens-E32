# Definición de los perfiles profesionales

ResumeLens evalúa si las cualificaciones explícitas de un CV cumplen el patrón formal de cuatro
perfiles. Este documento define cada perfil: su propósito, sus categorías, el patrón que se acepta y
por qué se eligió así. Los autómatas que reconocen estos patrones están formalizados en
[`dfa-design.md`](dfa-design.md).

La definición vive en `src/classification/profiles.py` (categorías y orden canónico). El sistema no
clasifica ni ordena candidatos: solo decide, para cada perfil, si el patrón se cumple.

## 1. Cómo se define un patrón

Cada perfil tiene **categorías** (por ejemplo `FRONTEND`) y cada categoría agrupa skills canónicas
equivalentes para el perfil (por ejemplo `REACT`, `ANGULAR`, `VUE`).

- Una categoría **obligatoria** debe estar cubierta por **al menos una** de sus skills.
- Una categoría **opcional** se acepta pero no se exige.
- Una skill de una categoría ya cubierta no cambia el resultado.
- El orden en que aparecen las skills no importa.
- Una skill que no pertenece al perfil se ignora al evaluarlo (el ordenador canónico la descarta).

Un candidato es **ACCEPTED** para un perfil cuando cubre todas sus categorías obligatorias. Un mismo
candidato puede cumplir varios perfiles, y se evalúa cada uno por separado.

## 2. Full Stack Developer

**Propósito.** Desarrollo de aplicaciones web de punta a punta.

| Categoría | Condición | Skills canónicas |
|---|---|---|
| `LANGUAGE` | Obligatoria | `JAVASCRIPT`, `TYPESCRIPT` |
| `FRONTEND` | Obligatoria | `REACT`, `ANGULAR`, `VUE` |
| `BACKEND` | Obligatoria | `NODE_JS`, `DJANGO`, `SPRING_BOOT` |
| `DATABASE` | Obligatoria | `SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB` |
| `API` | Opcional | `REST_API` |
| `VERSION_CONTROL` | Obligatoria | `GIT` |

**Orden canónico.** `LANGUAGE → FRONTEND → BACKEND → DATABASE → API → VERSION_CONTROL`.

**Justificación.** Es un perfil predefinido por el enunciado. `REST_API` es opcional porque muchos
perfiles full stack reales no la declaran de forma explícita, y exigirla rechazaría candidatos
razonables.

| Secuencia | Resultado |
|---|---|
| `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` | ACCEPTED |
| `TYPESCRIPT, VUE, DJANGO, MONGODB, REST_API, GIT` | ACCEPTED (otras alternativas y API opcional) |
| `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL` | REJECTED (falta `VERSION_CONTROL`) |

## 3. Machine Learning Engineer

**Propósito.** Desarrollo y entrenamiento de modelos de aprendizaje automático.

| Categoría | Condición | Skills canónicas |
|---|---|---|
| `LANGUAGE` | Obligatoria | `PYTHON` |
| `DATA_PROCESSING` | Obligatoria | `PANDAS`, `NUMPY` |
| `ML_LIBRARY` | Obligatoria | `SCIKIT_LEARN` |
| `MODEL_FRAMEWORK` | Obligatoria | `TENSORFLOW`, `PYTORCH` |
| `DATABASE` | Obligatoria | `SQL`, `POSTGRESQL`, `MYSQL` |
| `VERSION_CONTROL` | Obligatoria | `GIT` |

**Orden canónico.** `LANGUAGE → DATA_PROCESSING → ML_LIBRARY → MODEL_FRAMEWORK → DATABASE → VERSION_CONTROL`.

**Justificación.** Es un perfil predefinido por el enunciado. Se separan `ML_LIBRARY` (modelos
clásicos) y `MODEL_FRAMEWORK` (aprendizaje profundo) para exigir ambos tipos de conocimiento.

| Secuencia | Resultado |
|---|---|
| `PYTHON, PANDAS, SCIKIT_LEARN, TENSORFLOW, SQL, GIT` | ACCEPTED |
| `PYTHON, PANDAS, TENSORFLOW, SQL, GIT` | REJECTED (falta `ML_LIBRARY`) |

## 4. QA Engineer (perfil adicional de ingeniería de software)

**Propósito.** Aseguramiento de la calidad: pruebas, automatización y seguimiento de defectos.

| Categoría | Condición | Skills canónicas |
|---|---|---|
| `TESTING` | Obligatoria | `PYTEST`, `JUNIT`, `TESTNG` |
| `TEST_AUTOMATION` | Obligatoria | `SELENIUM`, `CYPRESS`, `PLAYWRIGHT` |
| `API_TESTING` | Obligatoria | `POSTMAN`, `REST_ASSURED` |
| `PROGRAMMING` | Obligatoria | `PYTHON`, `JAVA`, `JAVASCRIPT` |
| `ISSUE_TRACKING` | Obligatoria | `JIRA` |
| `VERSION_CONTROL` | Obligatoria | `GIT` |

**Orden canónico.** `TESTING → TEST_AUTOMATION → API_TESTING → PROGRAMMING → ISSUE_TRACKING → VERSION_CONTROL`.

**Justificación.** Se eligió porque es un perfil de ingeniería de software con un patrón claro y
distinto del de Full Stack: no se define por la tecnología de desarrollo sino por las prácticas de
prueba (unitaria, automatizada y de API), el seguimiento de defectos y la capacidad de programar.
Comparte con Full Stack las skills `JAVASCRIPT` y `GIT`, lo que muestra que una misma skill puede
pertenecer a perfiles distintos.

| Secuencia | Resultado |
|---|---|
| `PYTEST, SELENIUM, POSTMAN, PYTHON, JIRA, GIT` | ACCEPTED |
| `PYTEST, SELENIUM, POSTMAN, PYTHON, GIT` | REJECTED (falta `ISSUE_TRACKING`) |

## 5. Data Analyst (perfil adicional de IA y datos)

**Propósito.** Consulta, análisis y visualización de datos para apoyar decisiones.

| Categoría | Condición | Skills canónicas |
|---|---|---|
| `QUERY_LANGUAGE` | Obligatoria | `SQL`, `POSTGRESQL`, `MYSQL` |
| `SPREADSHEET` | Opcional | `EXCEL` |
| `ANALYSIS_LANGUAGE` | Obligatoria | `PYTHON`, `R` |
| `DATA_PROCESSING` | Obligatoria | `PANDAS`, `NUMPY` |
| `VISUALIZATION` | Obligatoria | `POWER_BI`, `TABLEAU`, `MATPLOTLIB` |

**Orden canónico.** `QUERY_LANGUAGE → SPREADSHEET → ANALYSIS_LANGUAGE → DATA_PROCESSING → VISUALIZATION`.

**Justificación.** Se eligió porque es un perfil de datos que se diferencia del de Machine Learning por
su énfasis en consulta y visualización en lugar de modelado. Muestra dos decisiones de diseño: la
misma skill `SQL` pertenece a `DATABASE` en Full Stack y ML pero a `QUERY_LANGUAGE` aquí, y `EXCEL` es
una categoría opcional que se acepta sin exigirse.

| Secuencia | Resultado |
|---|---|
| `SQL, PYTHON, PANDAS, TABLEAU` | ACCEPTED |
| `SQL, PYTHON, PANDAS, EXCEL` | REJECTED (falta `VISUALIZATION`) |

## 6. Skills compartidas entre perfiles

| Skill | Perfiles y categoría |
|---|---|
| `SQL`, `POSTGRESQL`, `MYSQL` | Full Stack (`DATABASE`), ML (`DATABASE`), Data Analyst (`QUERY_LANGUAGE`) |
| `PYTHON` | ML (`LANGUAGE`), QA (`PROGRAMMING`), Data Analyst (`ANALYSIS_LANGUAGE`) |
| `JAVASCRIPT` | Full Stack (`LANGUAGE`), QA (`PROGRAMMING`) |
| `PANDAS`, `NUMPY` | ML y Data Analyst (`DATA_PROCESSING`) |
| `GIT` | Full Stack, ML y QA (`VERSION_CONTROL`) |

Por eso la pertenencia de una skill a una categoría se define dentro de cada perfil y no en los
transductores. El transductor solo normaliza el nombre; el perfil decide qué significa.
