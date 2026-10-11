# ResumeLens Architecture

ResumeLens implementa un pipeline secuencial basado en modelos de la teoría de lenguajes formales para procesar hojas de vida textuales y evaluar su concordancia con perfiles profesionales definidos.

## End-to-End Pipeline

```text
Resume Text
    │
    ▼
Regex Extraction
    │
    ▼
FST Normalization
    │
    ▼
Canonical Ordering
    │
    ▼
Finite Automata Classification
    │
    ▼
CFG/textX Validation
    │
    ▼
HTML/Markdown Output
```

## Etapas del Pipeline y Responsabilidades

1. **Resume**: Texto plano de entrada correspondiente al currículum vitae del candidato.
2. **Regex Extraction**: Extrae texto relevante del CV (nombre, datos de contacto, experiencia, educación y tokens brutos de cualificaciones) utilizando expresiones regulares.
3. **FST Normalization**: Transforma las diferentes representaciones textuales y abreviaciones de una misma cualificación a su forma canónica estándar mediante transductores de estados finitos.
4. **Canonical Ordering**: Organiza las cualificaciones normalizadas en un orden canónico predefinido por perfil para independizar la evaluación del orden en el que fueron redactadas, y descarta las que no pertenecen al perfil evaluado.
5. **Finite Automata Classification**: Evalúa las secuencias de cualificaciones reconocidas frente a los autómatas de cada perfil para determinar la aceptación o rechazo formal del candidato.
6. **CFG/textX Validation**: Valida y estructura formalmente la información del perfil del candidato mediante una gramática libre de contexto procesada con textX.
7. **HTML/Markdown Output**: Genera la representación y visualización final formateada del perfil estructurado y los resultados de evaluación.

## Correspondencia entre etapas y código

| Etapa | Módulo | Archivos principales | Documento de diseño |
|---|---|---|---|
| 1. Extracción | `src/extraction/` | `regex_extractor.py`, `name_extractor.py` | [`regex-design.md`](regex-design.md) |
| 2. Normalización (FST) | `src/normalization/` | `transducers.py`, `normalizer.py` | [`fst-design.md`](fst-design.md) |
| Orden canónico | `src/normalization/` | `sorter.py` | [`fst-design.md`](fst-design.md), sección 6 |
| 3. Clasificación (autómatas) | `src/classification/` | `profiles.py`, `profile_dfa.py`, un archivo por perfil, `classifier.py` | [`dfa-design.md`](dfa-design.md), [`profile-definitions.md`](profile-definitions.md) |
| 4. Gramática y DSL | `src/grammar/` | `resume.tx`, `builder.py`, `validator.py`, `parser.py`, `renderer.py` | [`grammar-design.md`](grammar-design.md) |
| Orquestación | `src/` | `pipeline.py` | Este documento |
| Interfaz gráfica | `src/ui/` | `app.py` (Streamlit) | README |
| Línea de comandos | `src/` | `main.py` | README |

El vocabulario de alias que alimenta a los transductores está en `data/aliases.json`.

## Flujo de datos

```text
texto del CV
   │  extraction            → nombre, contacto, experiencia, educación, skills crudas
   ▼
skills crudas
   │  normalization (FST)   → skills canónicas (p. ej. "Postgres" → POSTGRESQL) y desconocidas
   ▼
skills canónicas
   │  sort_for_profile      → una secuencia ordenada por cada perfil (descarta las ajenas al perfil)
   ▼
secuencias por perfil
   │  classification (DFA)  → ACCEPTED / REJECTED por perfil
   ▼
resultados
   │  builder               → programa en el DSL (texto)
   ▼
programa DSL
   │  textX + validator     → modelo validado (o error sintáctico / semántico)
   ▼
modelo
   │  renderer              → HTML y Markdown
```

`src/pipeline.py` solo orquesta: llama a cada etapa y reúne los resultados en un `PipelineResult`. Las
decisiones de cada etapa viven en su propio módulo. La interfaz gráfica y la línea de comandos usan el
mismo pipeline, por lo que producen los mismos resultados.

## Principios de diseño

- **Una responsabilidad por etapa.** La extracción no normaliza, los transductores no clasifican, los
  autómatas no leen el texto del CV y la gramática no decide la clasificación.
- **Una sola solución general.** Los cuatro perfiles pasan por el mismo pipeline y por la misma
  construcción de autómatas; agregar un perfil es agregar sus datos en `profiles.py`.
- **Independencia del orden.** El resultado no depende del orden en que el candidato escribió sus skills.
- **Sin atajos.** La normalización se hace con transductores y la clasificación con autómatas, no con
  diccionarios de traducción ni con comparaciones de listas.
