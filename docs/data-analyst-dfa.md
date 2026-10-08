# Autómata Finito Determinista (DFA) — Data Analyst

Documento de formalización del autómata correspondiente al perfil **Data Analyst** en ResumeLens (Etapa 3 del pipeline).

---

## 1. Propósito del DFA

El autómata evalúa una secuencia de cualificaciones canónicas (obtenidas tras la etapa de normalización FST) y determina si el candidato cumple con el perfil profesional de **Data Analyst**. 

El criterio de aceptación exige demostrar competencias en cuatro áreas obligatorias de análisis de datos, independientemente del orden en que aparezcan en la hoja de vida.

---

## 2. Categorías y Alfabeto de Entrada ($\Sigma$)

El alfabeto $\Sigma$ está formado por los 11 tokens canónicos asignados al perfil en `src/classification/profiles.py`:

| Categoría | Condición | Tokens Canónicos ($\Sigma$) |
|---|---|---|
| **QUERY_LANGUAGE** | Obligatoria | `SQL`, `POSTGRESQL`, `MYSQL` |
| **ANALYSIS_LANGUAGE** | Obligatoria | `PYTHON`, `R` |
| **DATA_PROCESSING** | Obligatoria | `PANDAS`, `NUMPY` |
| **VISUALIZATION** | Obligatoria | `POWER_BI`, `TABLEAU`, `MATPLOTLIB` |
| **SPREADSHEET** | Opcional | `EXCEL` |

Total de símbolos en el alfabeto: $|\Sigma| = 11$.

---

## 3. Definición Formal (5-tupla)

El autómata es un DFA definido por:

$$M = (Q, \Sigma, \delta, q_0, F)$$

### 3.1 Conjunto de Estados ($Q$)

Dado que hay 4 categorías obligatorias y cada una puede estar satisfecha o no, el conjunto de estados corresponde al conjunto potencia de las categorías obligatorias:

$$Q = \mathcal{P}(\{\text{QUERY}, \text{ANALYSIS}, \text{PROCESSING}, \text{VISUALIZATION}\})$$

Esto produce exactamente $2^4 = 16$ estados:

1. **`q_empty`**: Ninguna categoría obligatoria satisfecha (estado inicial).
2. **`q_query`**: Satisfecha únicamente `QUERY_LANGUAGE`.
3. **`q_analysis`**: Satisfecha únicamente `ANALYSIS_LANGUAGE`.
4. **`q_processing`**: Satisfecha únicamente `DATA_PROCESSING`.
5. **`q_visualization`**: Satisfecha únicamente `VISUALIZATION`.
6. **`q_query_analysis`**: Satisfechas `QUERY` y `ANALYSIS`.
7. **`q_query_processing`**: Satisfechas `QUERY` y `PROCESSING`.
8. **`q_query_visualization`**: Satisfechas `QUERY` y `VISUALIZATION`.
9. **`q_analysis_processing`**: Satisfechas `ANALYSIS` y `PROCESSING`.
10. **`q_analysis_visualization`**: Satisfechas `ANALYSIS` y `VISUALIZATION`.
11. **`q_processing_visualization`**: Satisfechas `PROCESSING` y `VISUALIZATION`.
12. **`q_query_analysis_processing`**: Satisfechas `QUERY`, `ANALYSIS` y `PROCESSING`.
13. **`q_query_analysis_visualization`**: Satisfechas `QUERY`, `ANALYSIS` y `VISUALIZATION`.
14. **`q_query_processing_visualization`**: Satisfechas `QUERY`, `PROCESSING` y `VISUALIZATION`.
15. **`q_analysis_processing_visualization`**: Satisfechas `ANALYSIS`, `PROCESSING` y `VISUALIZATION`.
16. **`q_all_mandatory`**: Satisfechas las 4 categorías obligatorias (estado de aceptación).

### 3.2 Estado Inicial ($q_0$)

$$q_0 = \text{q\_empty}$$

### 3.3 Estados Finales ($F$)

$$F = \{\text{q\_all\_mandatory}\}$$

Solo se acepta si el candidato alcanza el estado donde las 4 categorías obligatorias han sido vistas al menos una vez.

### 3.4 Función de Transición ($\delta$)

Sea $q_S \in Q$ un estado que representa el conjunto $S$ de categorías obligatorias satisfechas:

1. **Para un token $\sigma$ de categoría obligatoria $C$:**
   $$\delta(q_S, \sigma) = q_{S \cup \{C\}}$$
   - Si la categoría $C$ no estaba en $S$, avanza al estado que incluye $C$.
   - Si la categoría $C$ ya estaba en $S$, produce un auto-bucle ($S \cup \{C\} = S$).

2. **Para el token opcional `EXCEL`:**
   $$\delta(q_S, \text{EXCEL}) = q_S$$
   Produce un auto-bucle en los 16 estados, preservando el progreso actual sin alterar las categorías obligatorias.

3. **Para un símbolo ajeno ($\sigma \notin \Sigma$):**
   La transición $\delta(q_S, \sigma)$ es indefinida. En consecuencia, el autómata se detiene de inmediato y rechaza la entrada.

---

## 4. Propiedades del Diseño

### 4.1 Independencia del Orden
En un currículum vitae, un candidato puede listar sus habilidades en cualquier secuencia. Como la unión de conjuntos es conmutativa y asociativa ($S \cup \{A\} \cup \{B\} = S \cup \{B\} \cup \{A\}$), cualquier orden de lectura que contenga las 4 categorías obligatorias llega inevitablemente al estado final `q_all_mandatory`.

### 4.2 Papel Opcional de EXCEL
`EXCEL` forma parte válida del alfabeto $\Sigma$, pero no es requisito para la aceptación. Al funcionar como auto-bucle en cada estado, puede aparecer al inicio, en medio, al final, repetirse o estar ausente sin impedir la aceptación.

### 4.3 Símbolos fuera del Alfabeto
Si la lista contiene tecnologías ajenas al perfil (por ejemplo `GIT` o `REACT`), el DFA no posee transición para dicho símbolo, lo que garantiza el rechazo formal sin necesidad de filtros ad-hoc.

---

## 5. Ejemplos de Evaluación

### Ejemplo 1: Candidato Aceptado
- **Entrada:** `["PYTHON", "SQL", "POWER_BI", "PANDAS"]`
- **Recorrido:**
  1. Inicio en `q_empty`.
  2. Lee `PYTHON` $\to$ `q_analysis`.
  3. Lee `SQL` $\to$ `q_query_analysis`.
  4. Lee `POWER_BI` $\to$ `q_query_analysis_visualization`.
  5. Lee `PANDAS` $\to$ `q_all_mandatory`.
- **Fin de cadena en `q_all_mandatory` $\in F \implies$ ACEPTADO (`True`).**

*(Nota: Si se añade `EXCEL` en cualquier posición, ej. `["EXCEL", "PYTHON", "SQL", "POWER_BI", "PANDAS"]`, el recorrido pasa por `q_empty --EXCEL--> q_empty` y concluye igualmente en `q_all_mandatory`).*

### Ejemplo 2: Candidato Rechazado
- **Entrada:** `["SQL", "PYTHON", "PANDAS"]`
- **Recorrido:**
  1. Inicio en `q_empty`.
  2. Lee `SQL` $\to$ `q_query`.
  3. Lee `PYTHON` $\to$ `q_query_analysis`.
  4. Lee `PANDAS` $\to$ `q_query_analysis_processing`.
- **Fin de cadena en `q_query_analysis_processing` $\notin F \implies$ RECHAZADO (`False`).**
- **Causa:** Falta al menos una habilidad de `VISUALIZATION`.
