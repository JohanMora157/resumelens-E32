# ResumeLens

Sistema que analiza una hoja de vida en texto y determina si sus calificaciones explícitas cumplen
el patrón formal de un perfil profesional. Proyecto integrador de **Computación y Estructuras Discretas III (CyED3)**.

Perfiles evaluados: **Full Stack Developer**, **Machine Learning Engineer**, **QA Engineer** y
**Data Analyst**.

## Integrantes

| Nombre | Usuario de GitHub |
|---|---|
| Joshua Sayur | joshsg9 |
| Juan David Fajardo | F4F4F |
| Johan Mora | JohanMora157 |

**IDE utilizado:** Visual Studio Code.

## Cómo funciona

El texto del CV pasa por cuatro etapas, cada una con una herramienta de teoría de la computación:

```
CV (.txt)
   │
   ▼  1. Extracción        Expresiones regulares: nombre, contacto, experiencia, educación, skills
   │
   ▼  2. Normalización     Transductores de estados finitos (FST): "Postgres" → POSTGRESQL
   │
   ▼  3. Clasificación     Autómatas finitos deterministas (DFA), uno por perfil: ACCEPTED / REJECTED
   │
   ▼  4. Gramática y DSL   Gramática libre de contexto (textX): validación y salida HTML / Markdown
```

Un perfil se **acepta** cuando el candidato cubre todas las categorías obligatorias de ese perfil
(por ejemplo, Full Stack exige lenguaje, frontend, backend, base de datos y control de versiones).
El orden en que aparecen las skills no importa.

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone https://github.com/<organizacion>/resumelens-E32.git
cd resumelens-E32
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

**Interfaz gráfica (Streamlit):**

```bash
streamlit run src/ui/app.py
```

Pega el texto de un CV o sube un `.txt` y pulsa **Analizar**. La interfaz muestra la extracción, la
normalización, la clasificación, el programa DSL (editable y validado por textX) y las salidas HTML
y Markdown.

**Consola:**

```bash
python -m src.main data/examples/sample_resume.txt
python -m src.main cv.txt --html salida.html
python -m src.main cv.txt --markdown
```

**Pruebas:**

```bash
pytest -q
```

## Estructura del repositorio

```
resumelens-E32/
├── data/
│   ├── aliases.json          Alias de skills por familia tecnológica (entrada de los FST)
│   ├── examples/             CVs de muestra
│   └── resumes/              CVs de prueba
├── docs/                     Documentos de diseño (ver más abajo)
├── scripts/                  Generador de diagramas de los autómatas
├── src/
│   ├── extraction/           Etapa 1: expresiones regulares
│   ├── normalization/        Etapa 2: transductores (FST), normalizador y ordenador
│   ├── classification/       Etapa 3: perfiles y autómatas (DFA)
│   ├── grammar/              Etapa 4: gramática textX, constructor, validador y renderizador
│   ├── ui/app.py             Interfaz Streamlit
│   ├── pipeline.py           Orquesta las cuatro etapas
│   └── main.py               Entrada por consola
├── tests/                    345 pruebas automáticas (misma estructura que src/)
├── output/                   Salidas generadas
├── pytest.ini
└── requirements.txt
```

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Arquitectura general y módulo de cada etapa. |
| [`docs/profile-definitions.md`](docs/profile-definitions.md) | Los cuatro perfiles: categorías, patrón aceptado y justificación. |
| [`docs/regex-design.md`](docs/regex-design.md) | Diseño de las expresiones regulares (Etapa 1). |
| [`docs/fst-design.md`](docs/fst-design.md) | Diseño y formalización de los transductores (Etapa 2). |
| [`docs/dfa-design.md`](docs/dfa-design.md) | Formalización de los cuatro autómatas (Etapa 3). |
| [`docs/data-analyst.md`](docs/data-analyst.md) | Autómata de Data Analyst: tabla de transiciones y diagrama. |
| [`docs/data-analyst-dfa.md`](docs/data-analyst-dfa.md) | Resumen en español del autómata de Data Analyst. |
| [`docs/grammar-design.md`](docs/grammar-design.md) | Gramática libre de contexto y DSL (Etapa 4). |
| [`docs/test-design.md`](docs/test-design.md) | Diseño de pruebas. |
| [`docs/ai-usage.md`](docs/ai-usage.md) | Registro del uso de herramientas de IA. |
| [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) | Guía de trabajo del equipo (plan inicial, con nota de estado final). |

Los diagramas están en [`docs/diagrams/`](docs/diagrams/) y el script que genera los de los
autómatas, en [`scripts/`](scripts/).

## Uso de inteligencia artificial

Se usó IA generativa como apoyo, con registro de los prompts y revisión del código por el equipo.
El detalle está en [`docs/ai-usage.md`](docs/ai-usage.md).
