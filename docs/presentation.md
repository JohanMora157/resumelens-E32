# ResumeLens — Diapositivas de Presentación

**Proyecto Integrador CyED3 (2026-2)**  
**Autores:** Johan Mora · Juan David Fajardo · Joshua Sayur  
**Archivo PDF:** [`ResumeLens Presentation.pdf`](ResumeLens%20Presentation.pdf) / [`presentation.pdf`](presentation.pdf)

---

## Diapositiva 1: Portada
### ResumeLens
**¿Las calificaciones explícitas de una hoja de vida cumplen el patrón formal de un perfil profesional?**
* **Herramientas formales:** Expresiones regulares · Transductores (FST) · Autómatas finitos deterministas (DFA) · Gramáticas libres de contexto (CFG + textX)
* **Equipo:** Johan Mora · Juan David Fajardo · Joshua Sayur

---

## Diapositiva 2: El Problema
### Una habilidad, múltiples formas de escribirla
* `JS` · `Javascript` · `ECMAScript` $\rightarrow$ `JAVASCRIPT`
* `Postgres` · `Postgre SQL` $\rightarrow$ `POSTGRESQL`
* `React.js` · `ReactJS` $\rightarrow$ `REACT`

### Nuestro Objetivo
* Decidir, para cuatro perfiles profesionales, si las cualificaciones declaradas explícitamente en el CV satisfacen un patrón formal.
* **Sin ranking ni puntajes subjetivos:** cada decisión es explícita, determinista y verificable.

---

## Diapositiva 3: Arquitectura
### Un pipeline, cuatro herramientas formales

| Etapa | Herramienta Formal | Responsabilidad | Ejemplo / Salida |
| :--- | :--- | :--- | :--- |
| **1. Extracción** | Expresiones regulares | Identifica texto relevante | Nombre, contacto, experiencia, educación y skills crudas |
| **2. Normalización** | Transductores de estados finitos (FST) | Mapea variantes a un token canónico | `"Postgres"` $\rightarrow$ `POSTGRESQL` |
| **3. Clasificación** | Autómatas finitos deterministas (DFA) | Verifica cobertura de categorías obligatorias | `ACCEPTED` / `REJECTED` por perfil |
| **4. Lenguaje de perfil** | Gramática libre de contexto (CFG + textX) | Validación sintáctica/semántica | Programa estructurado, HTML y Markdown |

> Una solución general para los cuatro perfiles. Cada etapa tiene una sola responsabilidad; el pipeline únicamente orquesta.

---

## Diapositiva 4: Etapa 1 · Expresiones Regulares
### Las regex encuentran texto; nunca toman decisiones
* **Nombre y contacto:** Línea inicial en mayúsculas / formato de nombre · correo electrónico · teléfono.
* **Experiencia:** `3 years of experience` · `3 años de experiencia`.
* **Educación:** Grados académicos y áreas de estudio (`Bachelor's degree`, `Computer Science`).
* **Skills:** Elementos separados por comas, saltos o viñetas bajo encabezados reconocidos.
* **Patrón de correo:** `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
* **Principio de diseño:** La salida conserva la escritura original. Decidir que `"JS"` significa `JavaScript` es trabajo de la siguiente etapa.

---

## Diapositiva 5: Etapa 2 · Transductores de Estados Finitos (FST)
### Múltiples escrituras entran, un token canónico sale
* **Nueve transductores:** Uno por familia de alias (Node, React, Version Control, etc.).
* **Un camino por alias:** Emisión de $\epsilon$ en las letras intermedias y el token canónico en la transición final.
* **Insensible a mayúsculas:** Dos transiciones por letra integradas directamente en $\delta$.
* **Idempotente:** Normalizar un token ya canónico devuelve el mismo token.
* **Formalización:** $M = (Q, \Sigma, \Gamma, \delta, \omega, q_0, F)$
* **Dimensiones del conjunto completo:**
  * **791** estados
  * **1,511** transiciones
  * **35** skills canónicas reconocidas

---

## Diapositiva 6: Etapa 2 · Ejemplo FST
### `Node` y `NodeJS` emiten `NODE_JS` una sola vez
* Dos caminos independientes que comparten su prefijo común:
  * Camino 1: $q_0 \xrightarrow{N/\epsilon} a_1 \xrightarrow{o/\epsilon} a_2 \xrightarrow{d/\epsilon} a_3 \xrightarrow{e/\text{NODE\_JS}} a_4$ (estado final)
  * Camino 2: $q_0 \xrightarrow{N/\epsilon} b_1 \xrightarrow{o/\epsilon} b_2 \xrightarrow{d/\epsilon} b_3 \xrightarrow{e/\epsilon} b_4 \xrightarrow{J/\epsilon} b_5 \xrightarrow{S/\text{NODE\_JS}} b_6$ (estado final)
* El token se emite únicamente al final de un alias completo, evitando que un prefijo incompleto genere salida por error.

---

## Diapositiva 7: Etapa 3 · Autómatas Finitos (DFA)
### El estado recuerda qué categorías se han cubierto
* **Estado = subconjunto de categorías obligatorias cubiertas:** Con $k$ categorías obligatorias existen $2^k$ estados.
* **Estado de aceptación = todas cubiertas:** $q_{\text{all}} = F$.
* **Categorías opcionales:** Modeladas como *self-loops* (no bloquean la aceptación).
* **DFA parcial y minimal:** La ausencia de una transición ante un token ajeno representa el rechazo inmediato; ningún autómata equivalente puede tener menos estados.

---

## Diapositiva 8: Etapa 3 · Los Cuatro Perfiles
### Mismo método formal, cuatro patrones distintos

| Perfil | Estados ($2^k$) | Alfabeto ($\Sigma$) | Categorías Obligatorias |
| :--- | :---: | :---: | :--- |
| **Full Stack Developer** | 32 | 14 | Language, Frontend, Backend, Database, Version Control *(API opcional)* |
| **Machine Learning Engineer** | 64 | 10 | Language, Data Processing, ML Library, Model Framework, Database, Version Control |
| **QA Engineer** | 64 | 13 | Testing, Test Automation, API Testing, Programming, Issue Tracking, Version Control |
| **Data Analyst** | 16 | 11 | Query Language, Spreadsheet, Analysis Language, Visualization *(Data Processing opcional)* |

* **El contexto importa:** `SQL` es una skill de categoría `DATABASE` para Full Stack y ML, pero es de categoría `QUERY_LANGUAGE` para Data Analyst.
* Los tokens ajenos a un perfil son descartados por el ordenador canónico antes de evaluar el autómata.

---

## Diapositiva 9: Etapa 4 · Gramática Libre de Contexto y textX
### El resultado es un programa validado
* **Lenguaje DSL del candidato:**
  ```textx
  candidate "Wednesday Addams" {
    experience { years: 3 }
    skills { JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT }
    classification {
      FULL_STACK_DEVELOPER: ACCEPTED
      QA_ENGINEER: REJECTED
    }
  }
  ```
* **Sintaxis con textX:** Gramática libre de contexto formal definida en [`src/grammar/resume.tx`](../src/grammar/resume.tx).
* **Validaciones semánticas:**
  * Nombre no vacío ni con solo espacios.
  * Años de experiencia en rango válido ($0 \le \text{years} \le 60$).
  * Sin duplicados en las habilidades.
  * Exactamente un resultado por perfil evaluado en la clasificación.
* **Renderizado final:** Generación automática de fichas estructuradas en HTML y Markdown.

---

## Diapositiva 10: Demostración en Vivo
### De texto pegado a un programa validado
1. **Pegar el CV:** Pegar texto o subir archivo `.txt` y presionar *"Analizar"*.
2. **Seguir las etapas:** Visualizar extracción, normalización FST y las cuatro clasificaciones DFA.
3. **Editar el programa DSL:** Cambiar `years: 99` o introducir duplicados para comprobar el rechazo sintáctico/semántico en vivo.
4. **Casos borde:** Evaluar CVs vacíos o cualificaciones con tecnologías desconocidas (ej. COBOL).
* **Comando:** `streamlit run src/ui/app.py`

---

## Diapositiva 11: Validación y Pruebas
### 345 pruebas automatizadas, 100% pasando

| Módulo | Cantidad de Pruebas | Alcance |
| :--- | :---: | :--- |
| **Normalización (FST)** | 114 | Traducción exacta, insensibilidad a mayúsculas, idempotencia |
| **Clasificación (DFA)** | 93 | Aceptación/rechazo de perfiles, todas las 24 permutaciones en Data Analyst |
| **Gramática (textX)** | 83 | Validador sintáctico, reglas léxicas y chequeos semánticos |
| **Extracción (Regex)** | 35 | Expresiones regulares de contacto, experiencia, educación y nombre |
| **Pipeline (Integración)** | 20 | Orquestación completa de extremo a extremo y CLI |
| **Total** | **345** | Ejecución en ~0.64 segundos |

---

## Diapositiva 12: Conclusiones
### Alcances y límites del sistema

* **Fortalezas:**
  * Cada decisión es explícita, determinista y matemáticamente testeable.
  * Arquitectura desacoplada: cada etapa tiene una única responsabilidad formal.
  * Constructor unificado de autómatas para los cuatro perfiles.
* **Límites:**
  * Solo se reconocen las habilidades catalogadas en el vocabulario del sistema.
  * Verifica cualificaciones declaradas textualmente, no habilidades prácticas reales.
  * Diseñado como soporte para la revisión humana; no la reemplaza.

> **Uso de IA:** El uso de herramientas de IA generativa está documentado y auditado en [`docs/ai-usage.md`](ai-usage.md).
