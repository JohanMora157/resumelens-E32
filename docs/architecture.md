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
2. **Regex Extraction**: Extrae texto relevante del CV (datos personales, experiencia y tokens brutos de cualificaciones) utilizando expresiones regulares.
3. **FST Normalization**: Transforma las diferentes representaciones textuales y abreviaciones de una misma cualificación a su forma canónica estándar mediante transductores de estados finitos.
4. **Canonical Ordering**: Organiza las cualificaciones normalizadas en un orden canónico predefinido por perfil para independizar la evaluación del orden en el que fueron redactadas.
5. **Finite Automata Classification**: Evalúa las secuencias de cualificaciones reconocidas frente a los autómatas de cada perfil para determinar la aceptación o rechazo formal del candidato.
6. **CFG/textX Validation**: Valida y estructura formalmente la información del perfil del candidato mediante una gramática libre de contexto procesada con textX.
7. **HTML/Markdown Output**: Genera la representación y visualización final formateada del perfil estructurado y los resultados de evaluación.
