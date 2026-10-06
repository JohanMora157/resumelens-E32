# ResumeLens — Stage 1: Regex Extraction Design

## 1. Purpose of the Regex Stage

The extraction stage is the first component of the ResumeLens pipeline. Its goal is to analyze raw textual résumés and identify relevant textual segments using formal regular expressions.

In formal language theory terms, regular expressions operate at the **lexical analysis** level:
- They scan the unstructured text.
- They identify tokens and segments that match defined patterns.
- They preserve the exact textual representations found in the input.

```text
Raw Resume Text ──[ Regular Expressions ]──> Extracted Resume Tokens
```

---

## 2. Information Extracted

The extractor categorizes detected information into four distinct fields:

1. **Contact Information**: Email addresses and phone numbers.
2. **Professional Experience**: Explicit quantitative experience statements (e.g., years of experience).
3. **Education**: Recognized academic degrees and computer science/software engineering fields of study.
4. **Technical Skills**: Technology and skill tokens listed under recognized section headers.

---

## 3. Regular Expressions and Patterns

### 3.1 Email Pattern (`EMAIL_PATTERN`)

- **Regular Expression**:
  ```python
  r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
  ```
- **What it recognizes**: Standard RFC-compliant email addresses, supporting subdomains, dots, underscores, hyphens, and plus-addressing (e.g., `user.name+tag@sub.domain.co.uk`).
- **Input example**: `Contact: candidate@domain.com`
- **Extracted output**: `"candidate@domain.com"`

### 3.2 Phone Pattern (`PHONE_PATTERN`)

- **Regular Expression**:
  ```python
  r"(?:(?:\b(?:Phone|Tel|Telephone|Mobile|Celular|Cel|Teléfono)\b\s*[:\s]+(?:\+?\d{1,3}[\s.-]?)?\d{7,12}\b)|"
  r"(?:(?:\b(?:Phone|Tel|Telephone|Mobile|Celular|Cel|Teléfono)\b\s*[:\s]*)?(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)|\b\d{2,4}\b)[\s.-]?\d{3,4}(?:[\s.-]?\d{3,4})?\b))"
  ```
- **What it recognizes**:
  - International phone numbers with country codes (e.g., `+1`, `+57`).
  - Numbers with area codes enclosed in parentheses (e.g., `(555) 123-4567`).
  - Delimiters such as hyphens, periods, or spaces.
  - Labeled plain-digit numbers (e.g., `Celular: 3001234567`).
- **What it excludes**: Year ranges (`2018 - 2022`), postal codes, and version numbers.
- **Input example**: `Mobile: +57 300 123 4567`
- **Extracted output**: `"+57 300 123 4567"`

### 3.3 Professional Experience Pattern (`EXPERIENCE_PATTERN`)

- **Regular Expression**:
  ```python
  r"\b(?:\d+\+?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*"
  r"(?:years?|yrs?|a[ñn]os?)\s*"
  r"(?:(?:of|de)\s*)?"
  r"(?:(?:professional|work|hands-on|laboral)\s*)?"
  r"(?:experience|experiencia)\b"
  ```
  *(with `re.IGNORECASE`)*
- **What it recognizes**: Explicit phrases stating duration of experience in English and Spanish.
  - Examples: `3 years of experience`, `2 years experience`, `5+ years of experience`, `4 years of professional experience`, `3 años de experiencia`.
- **What it excludes**: Generic uses of the word "experience" without quantitative duration (e.g., `"user experience design"`, `"life experience"`).

### 3.4 Education Pattern (`EDUCATION_PATTERN`)

- **Regular Expression**:
  Combines two sub-patterns:
  1. `ACADEMIC_DEGREES_PATTERN`: Matches recognized academic titles (e.g., `Bachelor's degree`, `Master's degree`, `Ph.D.`, `Doctorate`, `Associate degree`, `Licenciatura`).
  2. `ACADEMIC_FIELDS_PATTERN`: Matches recognized software and computing disciplines (e.g., `Computer Science`, `Software Engineering`, `Data Science`, `Artificial Intelligence`, `Ingeniería de Sistemas`).
- **What it recognizes**: Degrees and computing disciplines in their original text.
- **Input example**: `Bachelor's degree in Computer Science`
- **Extracted output**: `["Bachelor's degree", "Computer Science"]`

### 3.5 Skills Section and Delimiter Patterns

- **Section Header Pattern (`SKILLS_SECTION_PATTERN`)**:
  Identifies recognized skill headers in English and Spanish, with or without a trailing colon:
  - English: `Technical Skills:`, `Skills:`, `Technologies:`, `Programming Languages:`, `Frameworks:`, `Databases:`, `Tools & Technologies:`, `Tech Stack:`
  - Spanish: `Habilidades Técnicas:`, `Habilidades:`, `Tecnologías:`, `Lenguajes de Programación:`, `Bases de Datos:`, `Herramientas:`
  It captures content until the next major section heading (`Education`, `Experience`, `Projects`, `Certifications`, `Contact`, `Summary`) or two consecutive newlines.
- **Delimiter Pattern (`SKILL_DELIMITERS_PATTERN`)**:
  ```python
  r"[,;|\n]+"
  ```
  Splits items listed within the captured content using commas, semicolons, vertical bars, or line breaks/bullets, while cleanly stripping sentence-ending punctuation (like a trailing period in `Git.`) and preserving token extensions (like `.js` in `React.js` or `.net` in `ASP.NET`).

---

## 4. Input and Output Examples

### Example 1: Full Stack Developer Reference (Wednesday Addams)

**Input text:**
```text
Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
```

**Extracted dictionary output:**
```python
{
    "contact": {
        "email": None,
        "phone": None,
        "emails": [],
        "phones": [],
    },
    "experience": ["3 years of experience"],
    "education": [],
    "technical_skills": ["JS", "React.js", "NodeJS", "Postgres", "Git"],
}
```

### Example 2: Machine Learning Reference (Mary Jane Watson)

**Input text:**
```text
Mary Jane Watson
2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.
```

**Extracted dictionary output:**
```python
{
    "contact": {
        "email": None,
        "phone": None,
        "emails": [],
        "phones": [],
    },
    "experience": ["2 years of experience"],
    "education": [],
    "technical_skills": [
        "Python",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "SQL",
        "Git",
    ],
}
```

### Example 3: Full Bilingual Resume with All Sections

**Input text:**
```text
Johan Mora
Email: johan.mora@example.com | Teléfono: +57 300 123 4567
Profesional con 3 años de experiencia en desarrollo de software.

Educación:
Ingeniería de Sistemas

Habilidades Técnicas:
Python, Django, PostgreSQL, Git.
```

**Extracted dictionary output:**
```python
{
    "contact": {
        "email": "johan.mora@example.com",
        "phone": "+57 300 123 4567",
        "emails": ["johan.mora@example.com"],
        "phones": ["+57 300 123 4567"],
    },
    "experience": ["3 años de experiencia"],
    "education": ["Ingeniería de Sistemas"],
    "technical_skills": ["Python", "Django", "PostgreSQL", "Git"],
}
```

---

## 5. What Regex Deliberately Does NOT Do

To maintain a clean formal separation of responsibilities between stages, the Regex stage explicitly avoids:

1. **No canonical name mapping**: Regex does **not** map `JS` to `JAVASCRIPT` or `React.js` to `REACT`.
2. **No equivalence resolution**: Regex does **not** decide whether `Postgres` and `PostgreSQL` mean the same database.
3. **No profile classification**: Regex does **not** evaluate whether a candidate satisfies the Full Stack Developer or Machine Learning Engineer profile.
4. **No hiring decisions**: Regex does not rank, score, or filter candidates.
5. **No hardcoded dictionary of skills**: Regex detects structured lists under skill headings, rather than relying on a hardcoded dictionary of every existing library in the world.

---

## 6. Why Normalization Belongs to FST (Finite-State Transducers)

In formal language and automata theory:

- **Regular Expressions (Type 3 in the Chomsky hierarchy)** are language recognizers: they decide whether an input string belongs to a regular language, or extract matching substrings from a larger text.
- **Finite-State Transducers (FSTs)** are rational relations / string-to-string translators: given an input string over alphabet $\Sigma$, they emit an output string over alphabet $\Gamma$:
  $$T: \Sigma^* \to \Gamma^*$$

Normalization requires mapping many equivalent surface representations to a single canonical standard:
- `JS` $\to$ `JAVASCRIPT`
- `Javascript` $\to$ `JAVASCRIPT`
- `React.js` $\to$ `REACT`
- `NodeJS` $\to$ `NODE_JS`
- `Postgres` $\to$ `POSTGRESQL`

Mixing normalization into the Regex phase would violate the single-responsibility principle of the pipeline and defeat the academic objective of applying Finite-State Transducers. Leaving normalization to Stage 2 guarantees that:
1. Stage 1 focuses strictly on **textual extraction**.
2. Stage 2 models the **formal transformation** via an explicit 7-tuple transducer $M = (Q, \Sigma, \Gamma, \delta, \omega, q_0, F)$.
3. The pipeline remains decoupled, testable, and theoretically sound.
