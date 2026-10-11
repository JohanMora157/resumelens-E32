# Diseño de la gramática y del DSL (Etapa 4)

Esta etapa recibe el resultado de las tres anteriores (datos extraídos, skills normalizadas y
clasificación) y lo convierte en un **programa** de un lenguaje propio, el *Candidate Profile
Language* (CPL). textX lee ese programa con una gramática libre de contexto (CFG), lo valida y
construye un modelo de objetos. A partir del modelo se generan las salidas HTML y Markdown.

```
 pipeline ──▶ builder.py ──▶ texto CPL ──▶ textX (resume.tx) ──▶ modelo ──▶ renderer.py ──▶ HTML / Markdown
                                │                │
                                │                └─ errores sintácticos (TextXSyntaxError)
                                └─ validator.py ── errores semánticos (TextXSemanticError)
```

| Archivo | Responsabilidad |
|---|---|
| `src/grammar/resume.tx` | La gramática (reglas de estructura y reglas léxicas). |
| `src/grammar/builder.py` | Escribe el texto CPL a partir de los datos del pipeline. No valida. |
| `src/grammar/validator.py` | Carga la gramática, parsea el programa y aplica las reglas semánticas. |
| `src/grammar/parser.py` | Envoltura que devuelve el perfil como estructura de Python. |
| `src/grammar/renderer.py` | Genera HTML y Markdown desde el modelo ya validado. |

## 1. Por qué un DSL

La clasificación ya existe como datos (diccionario de ACCEPTED/REJECTED), pero un diccionario no
se puede editar ni verificar por un tercero. Escribirla como un programa CPL permite:

- **Verificar** que el resultado respeta la forma esperada (la gramática) y las reglas de negocio
  (el validador).
- **Editar a mano** el resultado en la UI y comprobar que el sistema rechaza programas inválidos.
- **Separar** la decisión (autómatas) de la presentación (HTML/Markdown): el renderer solo lee un
  modelo ya válido.

## 2. Formalización de la gramática

La gramática es una CFG `G = (V, Σ, P, S)`.

- **S = Candidate** (símbolo inicial).
- **V (no terminales)**: Candidate, Contact, Experiences, Experience, Education, Skills,
  Classification, ProfileResult, y las auxiliares de repetición (StringList, StringTail,
  SkillList, SkillTail, Results, EmailOpt, PhoneOpt, DescOpt).
- **Σ (terminales)**: las palabras clave `candidate contact email phone experience years
  description education skills classification`, los símbolos `{ } : ,`, y los terminales léxicos
  STRING, INT, Email, Phone, SkillName, ProfileName, Status (sección 3).

### Producciones (BNF)

```
Candidate      → 'candidate' STRING '{' Contact Experiences Education Skills Classification '}'

Contact        → 'contact' '{' EmailOpt PhoneOpt '}'
EmailOpt       → ε | 'email' ':' Email
PhoneOpt       → ε | 'phone' ':' Phone

Experiences    → ε | Experience Experiences
Experience     → 'experience' '{' 'years' ':' INT DescOpt '}'
DescOpt        → ε | 'description' ':' STRING

Education      → 'education' '{' StringList '}'
StringList     → ε | STRING StringTail
StringTail     → ε | ',' STRING StringTail

Skills         → 'skills' '{' SkillList '}'
SkillList      → ε | SkillName SkillTail
SkillTail      → ε | ',' SkillName SkillTail

Classification → 'classification' '{' Results '}'
Results        → ε | ProfileResult Results
ProfileResult  → ProfileName ':' Status
```

### Producciones en EBNF

La misma gramática en EBNF (`{ }` = repetición de cero o más, `[ ]` = parte opcional):

```
candidate      = "candidate" , STRING , "{" , contact , { experience } , education , skills , classification , "}" ;
contact        = "contact" , "{" , [ "email" , ":" , EMAIL ] , [ "phone" , ":" , PHONE ] , "}" ;
experience     = "experience" , "{" , "years" , ":" , INT , [ "description" , ":" , STRING ] , "}" ;
education      = "education" , "{" , [ STRING , { "," , STRING } ] , "}" ;
skills         = "skills" , "{" , [ SKILL , { "," , SKILL } ] , "}" ;
classification = "classification" , "{" , { profile_result } , "}" ;
profile_result = PROFILE , ":" , STATUS ;
```

Los terminales `EMAIL`, `PHONE`, `SKILL`, `PROFILE` y `STATUS` se definen con las reglas léxicas de la sección 3.

Correspondencia con `resume.tx`: los operadores de textX son abreviaturas de estas
producciones. `x*=` es una repetición de cero o más (`Experiences`, `Results`), `x+=A[',']` es una
lista separada por comas (`StringTail`, `SkillTail`) y `( ... )?` es una parte opcional (las reglas
`...Opt`).

### Elementos exigidos por el enunciado

| Requisito | Dónde aparece |
|---|---|
| No terminales y terminales | Secciones 2 y 3. |
| Elementos repetidos | `experience` (0..n), `education` (0..n entradas), `skills` (0..n separadas por coma), `classification` (0..n resultados). |
| Anidamiento | `Candidate` contiene bloques (`Contact`, `Experience`, ...) que a su vez contienen entradas. |
| Cobertura de las etapas anteriores | Contacto y experiencia (regex), skills canónicas (FST), resultados (autómatas). |

## 3. Reglas léxicas (terminales)

| Terminal | Expresión | Qué acepta |
|---|---|---|
| `STRING` | integrado en textX | Texto entre comillas dobles. |
| `INT` | integrado en textX | Enteros. |
| `Email` | `/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/` | `wednesday@example.com` |
| `Phone` | `/[+(]?[0-9][0-9 ().\-]{5,24}[0-9]/` | `+1-555-0199` |
| `SkillName` | `/[A-Z][A-Z0-9_]*/` | `NODE_JS`, `POSTGRESQL` (el formato del token que emite el FST). |
| `ProfileName` | `'FULL_STACK_DEVELOPER' \| 'MACHINE_LEARNING_ENGINEER' \| 'QA_ENGINEER' \| 'DATA_ANALYST'` | Los cuatro perfiles. |
| `Status` | `'ACCEPTED' \| 'REJECTED'` | El resultado del autómata. |
| `Comment` | `//...` y `/* ... */` | Comentarios, ignorados por el analizador. |

`SkillName` coincide a propósito con el formato de los tokens canónicos del FST. Así lo que sale de
la etapa 2 entra en el programa sin transformaciones.

## 4. Ejemplo y derivación

Programa válido:

```
candidate "Wednesday Addams" {
  contact { email: wednesday.addams@example.com  phone: +1-555-0199 }
  experience { years: 3 }
  education { "Bachelor's degree" }
  skills { JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT }
  classification {
    FULL_STACK_DEVELOPER: ACCEPTED
    MACHINE_LEARNING_ENGINEER: REJECTED
    QA_ENGINEER: REJECTED
    DATA_ANALYST: REJECTED
  }
}
```

Derivación por la izquierda del bloque de skills (resumida):

```
Skills ⇒ 'skills' '{' SkillList '}'
       ⇒ 'skills' '{' SkillName SkillTail '}'
       ⇒ 'skills' '{' JAVASCRIPT ',' SkillName SkillTail '}'
       ⇒ 'skills' '{' JAVASCRIPT ',' REACT ',' SkillName SkillTail '}'
       ⇒ ... ⇒ 'skills' '{' JAVASCRIPT ',' REACT ',' NODE_JS ',' POSTGRESQL ',' GIT '}'
```

Árbol de análisis (nivel superior):

```
Candidate
├── 'candidate'  "Wednesday Addams"  '{'
├── Contact ── email ── phone
├── Experiences ── Experience(years=3)
├── Education ── "Bachelor's degree"
├── Skills ── JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
├── Classification ── 4 × ProfileResult
└── '}'
```

## 5. Ambigüedad

Cada producción se elige mirando únicamente el siguiente token (una palabra clave, `{`, `}` o `,`),
así que no hay dos árboles posibles para un mismo programa. textX es además un analizador PEG
(elección ordenada), por lo que siempre devuelve un único árbol. Los bloques aparecen en un orden
fijo (`contact`, `experience`, `education`, `skills`, `classification`), lo que evita ambigüedades
de ordenación.

## 6. Validación en dos capas

**Sintáctica (textX).** Rechaza lo que no cumple la gramática: llaves sin cerrar, bloques
desordenados o faltantes, correo o teléfono mal formados, perfiles o estados inexistentes. Lanza
`TextXSyntaxError`.

**Semántica (`validator.py`).** Rechaza programas bien formados pero con datos incoherentes. Lanza
`TextXSemanticError`, que `DSLValidationError(kind)` clasifica:

| Regla | Ejemplo rechazado |
|---|---|
| Años de experiencia entre 0 y 60 | `years: 99` |
| Sin skills repetidas | `skills { GIT, GIT }` |
| Un solo resultado por perfil | `QA_ENGINEER: ACCEPTED` y `QA_ENGINEER: REJECTED` |
| Nombre no vacío | `candidate "" { ... }` |

Por esta separación el DSL puede editarse en la UI: lo que no respeta la forma falla en textX y lo
que respeta la forma pero no tiene sentido falla en las reglas semánticas.

## 7. Decisiones de diseño

- **`builder.py` solo escribe texto.** No decide ni valida. Los valores que no cumplen las reglas
  léxicas (correo o teléfono mal formados, skills que no son `MAYÚSCULAS_CON_GUION`) se omiten en
  lugar de producir un programa inválido.
- **Los años se extraen del texto** ("3 years", "5+ años", "two years") con `parse_years`.
- **Los strings se escriben sin barras invertidas.** textX solo interpreta `\"` dentro de un STRING,
  así que `_quote` elimina las barras y escapa las comillas.
- **La clasificación se escribe en el orden fijo de los perfiles**, para que el programa sea
  reproducible.
- **El renderer lee solo el modelo validado.** Si el programa no pasa la validación, no se
  genera HTML ni Markdown.

## 8. Limitaciones

- `description` está en la gramática pero el builder todavía no la rellena.
- El nombre se limita a una línea.
- La gramática no verifica que el resultado de clasificación sea consistente con las skills, porque
  eso es responsabilidad de los autómatas. El DSL solo comprueba la forma y las reglas de negocio.
- Una skill con el formato correcto pero ajena al vocabulario (por ejemplo `COBOL`) pasaría la
  gramática. El pipeline no la incluye porque el FST ya la descartó antes.

## 9. Pruebas asociadas

| Archivo | Qué cubre |
|---|---|
| `tests/grammar/test_builder.py` | Construcción del texto, escape de comillas, omisión de valores inválidos, `parse_years`. |
| `tests/grammar/test_validator.py` | Programas válidos e inválidos, las reglas semánticas y `DSLValidationError`. |
| `tests/grammar/test_resume_integration.py` | Parseo completo y modelo resultante. |
| `tests/pipeline/test_pipeline.py` | CV de texto a DSL, HTML y Markdown de extremo a extremo. |
