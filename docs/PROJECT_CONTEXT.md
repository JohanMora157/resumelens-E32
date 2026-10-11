# ResumeLens --- Project Context and Team/Agent Working Guide

> **Purpose of this document:** Shared context for the three team
> members and their coding agents.\
> Read this before modifying the project. It defines the agreed
> architecture, responsibilities, testing conventions, documentation
> expectations, and Git safety rules.

> **Estado final del proyecto (nota añadida al entregar).** Esta guía se escribió al inicio como plan de
> trabajo y se conserva por referencia. Donde difiera de lo siguiente, **prevalece lo siguiente**:
>
> - Los dos perfiles adicionales son **QA Engineer** (ingeniería de software) y **Data Analyst** (IA/datos).
>   Los cuatro perfiles están en [`profile-definitions.md`](profile-definitions.md).
> - El paquete `src/models/` se eliminó: las etapas se comunican con estructuras simples y con `PipelineResult`
>   (`src/pipeline.py`).
> - Los autómatas están en `src/classification/` (`full_stack_developer.py`, `machine_learning_engineer.py`,
>   `qa_engineer.py`, `data_analyst.py`) sobre la construcción común de `profile_dfa.py`.
> - La documentación final está en `dfa-design.md`, `data-analyst.md`, `fst-design.md`, `regex-design.md`,
>   `grammar-design.md`, `test-design.md`, `architecture.md` y `ai-usage.md`.
> - El reparto de perfiles por persona de las secciones 12 y 13 fue el plan inicial; la contribución real de cada
>   integrante está en el historial de commits.

------------------------------------------------------------------------

## 1. Project identity

**Project:** ResumeLens --- Formal Language-Based Resume Screening\
**Course:** Computación y Estructuras Discretas III --- 2026-2\
**Team members:** Juan David Fajardo, Johan Mora, Joshua Sayur

ResumeLens is an application that receives textual résumés and
determines whether the qualifications explicitly identified in a
candidate's résumé satisfy formally defined qualification patterns for
professional profiles.

The project is **not** a candidate ranking system and does **not** make
hiring decisions. It evaluates whether explicitly identified
qualifications satisfy formal patterns.

The official assignment states that ResumeLens must use:

1.  **Regular expressions** for résumé information extraction.
2.  **Finite-state transducers (FSTs)** for qualification normalization.
3.  **Finite automata** for professional-profile qualification-pattern
    recognition.
4.  **Context-free grammars + textX** for a structured candidate-profile
    language and validation.

The four profiles must be processed through **one general software
solution**, not four independent applications.

------------------------------------------------------------------------

# 2. The complete pipeline

The mental model for the whole project is:

``` text
Resume text
    |
    v
[1] REGEX / EXTRACTION
    |
    | Relevant candidate information
    v
[2] FST / NORMALIZATION
    |
    | Canonical qualification names
    v
[Canonical ordering]
    |
    v
[3] FINITE AUTOMATA / CLASSIFICATION
    |
    | Accepted / Rejected for each profile
    v
[4] CFG + textX / CANDIDATE PROFILE DSL
    |
    | Structured and validated candidate profile
    v
[HTML or Markdown visualization]
```

Important: these stages are connected. Do not build four unrelated
mini-projects.

------------------------------------------------------------------------

# 3. Professional profiles

The final system supports four profiles.

## 3.1 Full Stack Developer

This profile is predefined by the assignment.

Possible qualifications given by the assignment include:

-   JavaScript or TypeScript
-   React, Angular, or Vue
-   Node.js, Django, Spring Boot, or a similar backend technology
-   SQL or NoSQL databases
-   REST APIs
-   Git

The exact accepted pattern must be defined by the team and documented.
Do not silently assume that every listed qualification must always be
mandatory unless the team explicitly defines that rule.

Example from the assignment:

``` text
JS, React.js, NodeJS, Postgres, Git.
```

After normalization and canonical ordering:

``` text
JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
```

------------------------------------------------------------------------

## 3.2 Machine Learning Engineer

This profile is predefined by the assignment.

Possible qualifications given by the assignment include:

-   Python
-   Pandas or NumPy
-   Scikit-learn
-   TensorFlow or PyTorch
-   Machine-learning model development
-   SQL
-   Git

Again, the team must formally define the accepted pattern.

Example from the assignment:

``` text
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.
```

------------------------------------------------------------------------

## 3.3 Additional Software Engineering profile

The team must choose one additional profile related to **software
engineering**.

Before implementing it, document:

-   profile name
-   purpose
-   qualification categories
-   canonical qualification names
-   accepted pattern
-   rationale for choosing the pattern
-   automaton design

Do not choose a profile only because it is easy to code. It should have
a meaningful qualification pattern that can be represented using a
finite automaton.

------------------------------------------------------------------------

## 3.4 Additional AI/Data profile

The team must choose one additional profile related to **AI/data**.

Before implementing it, document:

-   profile name
-   purpose
-   qualification categories
-   canonical qualification names
-   accepted pattern
-   rationale for choosing the pattern
-   automaton design

------------------------------------------------------------------------

# 4. Architecture and folder responsibilities

Current intended structure:

``` text
ResumeLens/
|
├── src/
│   ├── extraction/
│   ├── normalization/
│   ├── classification/
│   ├── grammar/
│   ├── models/
│   └── main.py
|
├── tests/
│   ├── extraction/
│   ├── normalization/
│   ├── classification/
│   └── grammar/
|
├── docs/
|
├── data/
│   ├── resumes/
│   └── examples/
|
├── output/
|
├── README.md
├── requirements.txt
└── .gitignore
```

## `src/extraction/`

Responsible for Stage 1: résumé information extraction.

Expected responsibility:

``` text
raw résumé text
        ↓
relevant textual information
```

Use Python's `re` module.

This module should NOT:

-   normalize equivalent names;
-   decide that JS and JavaScript are equivalent;
-   classify the candidate;
-   decide whether a profile is accepted.

------------------------------------------------------------------------

## `src/normalization/`

Responsible for Stage 2: FST-based normalization.

Expected responsibility:

``` text
JS       → JAVASCRIPT
React.js → REACT
NodeJS   → NODE_JS
Postgres → POSTGRESQL
```

Use `pyformlang`.

This module should NOT decide whether the candidate is Full Stack, ML,
etc.

------------------------------------------------------------------------

## `src/classification/`

Responsible for Stage 3: finite automata.

Recommended organization:

``` text
classification/
├── full_stack.py
├── machine_learning.py
├── software_engineering.py
├── ai_data.py
└── classifier.py
```

Each profile has its own automaton, but all automata are used through
the same general classification mechanism.

The module should receive normalized/canonically ordered qualifications
and determine whether each profile pattern is satisfied.

------------------------------------------------------------------------

## `src/grammar/`

Responsible for Stage 4:

-   CFG/DSL design
-   EBNF documentation
-   textX implementation
-   candidate-profile validation
-   visualization generation

The grammar is not another classifier.

Its purpose is to define how the **resulting candidate information** is
structurally represented.

------------------------------------------------------------------------

## `src/models/`

Contains shared data structures exchanged between stages.

Examples of conceptual data objects:

``` text
ResumeData
NormalizedResume
ClassificationResult
CandidateProfile
```

The exact classes/fields are to be designed by the team.

The goal is to keep modules decoupled.

A module should consume a clearly defined object/interface instead of
knowing the internal implementation of another module.

------------------------------------------------------------------------

## `tests/`

Tests are organized by module:

``` text
tests/
├── extraction/
├── normalization/
├── classification/
└── grammar/
```

Integration tests can be added later when the full pipeline exists.

------------------------------------------------------------------------

## `docs/`

Contains design and formalization documents.

Examples:

``` text
docs/
├── architecture.md
├── regex-design.md
├── fst-design.md
├── automata-design.md
├── grammar-design.md
├── profile-definitions.md
├── test-plan.md
└── ai-usage.md
```

The assignment explicitly requires a `docs/` directory and Markdown
documents.

------------------------------------------------------------------------

## `data/resumes/`

Contains résumé input examples used for testing.

Use synthetic or assignment-provided examples. Do not introduce
unnecessary personal data.

------------------------------------------------------------------------

## `data/examples/`

Contains small examples of inputs/outputs or sample DSL representations.

------------------------------------------------------------------------

## `output/`

Contains generated HTML/Markdown results when appropriate.

Do not treat generated output as source code.

------------------------------------------------------------------------

# 5. Stage 1 --- Regular Expressions

## Required work

For each relevant information type:

1.  Define the regular expression.
2.  Explain what textual language/pattern it recognizes.
3.  Implement it using Python's `re`.
4.  Store the extracted information in a data structure or file.

Relevant information may include:

-   contact information
-   programming languages
-   frameworks/libraries
-   databases
-   academic qualifications
-   professional experience
-   tools/technologies
-   other qualifications relevant to the supported profiles

## Important boundary

Regex answers:

> "What information appears in this résumé?"

Regex does NOT answer:

> "Are JS and JavaScript equivalent?"

and does NOT answer:

> "Is this candidate a Full Stack Developer?"

Those decisions belong to later stages.

------------------------------------------------------------------------

# 6. Stage 2 --- Finite-State Transducers

## Required work

FSTs transform equivalent textual representations into a canonical
representation.

Examples given by the assignment include:

``` text
JS             → JAVASCRIPT
Javascript     → JAVASCRIPT
React.js       → REACT
ReactJS        → REACT
NodeJS         → NODE_JS
Node.js        → NODE_JS
Postgres       → POSTGRESQL
PostgreSQL     → POSTGRESQL
pandas         → PANDAS
sklearn        → SCIKIT_LEARN
scikit learn   → SCIKIT_LEARN
Scikit-learn   → SCIKIT_LEARN
Tensor Flow    → TENSORFLOW
TensorFlow     → TENSORFLOW
Py Torch       → PYTORCH
PyTorch        → PYTORCH
```

These are examples from the assignment. The assignment explicitly says
the team must propose its own transformations as well.

## Formal requirement

For each transducer, provide the complete 7-tuple:

``` text
M = (Q, Σ, Γ, δ, ω, q0, F)
```

Clearly document:

-   Q --- states
-   Σ --- input alphabet
-   Γ --- output alphabet
-   δ --- transition relation
-   ω --- output relation
-   q0 --- initial state
-   F --- accepting states

Also provide:

-   graphical representation
-   `pyformlang` implementation
-   tests

## Canonical ordering

After normalization, qualifications may be sorted into a canonical order
defined for the selected profile.

Example given by the assignment:

``` text
Frontend
Backend
Database
Version control
```

Thus:

``` text
Git, NodeJS, JS, Postgres, React.js
```

can become:

``` text
JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
```

The purpose is to prevent classification from depending on the order in
which a candidate wrote skills in the résumé.

------------------------------------------------------------------------

# 7. Stage 3 --- Finite Automata

The system must classify the résumé among the four supported profiles.

Allowed automaton types:

-   DFA
-   NFA
-   ε-NFA

For each profile automaton, document the complete 5-tuple:

``` text
M = (Q, Σ, δ, q0, F)
```

Clearly define:

-   Q --- states
-   Σ --- alphabet
-   δ --- transition function/relation
-   q0 --- initial state
-   F --- accepting states

Also document:

-   automaton type;
-   why that type is appropriate;
-   transition diagram;
-   profile pattern represented;
-   `pyformlang` implementation.

## Important design rule

The automaton should receive the **normalized/canonically ordered
qualification sequence**, not raw résumé text.

Conceptually:

``` text
CV
 ↓
Regex
 ↓
raw qualifications
 ↓
FST
 ↓
normalized qualifications
 ↓
canonical ordering
 ↓
automaton
 ↓
ACCEPTED / REJECTED
```

------------------------------------------------------------------------

# 8. Designing automata correctly

Before writing Python, define the language/pattern on paper.

For example, if a profile requires a sequence of categories:

``` text
LANGUAGE
→ FRONTEND
→ BACKEND
→ DATABASE
→ VERSION_CONTROL
```

then states can represent progress:

``` text
q0 → q1 → q2 → q3 → q4
```

But do not blindly copy this structure for every profile.

Each profile needs a justified pattern.

For every profile ask:

1.  What qualifications are required?
2.  Which qualifications are alternatives?
3.  Which are optional?
4.  Which combinations are accepted?
5.  What is the canonical order?
6.  What should happen if something is missing?
7.  What should happen if an irrelevant qualification appears?
8.  What sequence(s) should be accepted?
9.  What sequence(s) should be rejected?

The answer to these questions determines the automaton.

------------------------------------------------------------------------

# 9. Stage 4 --- CFG + textX

The final language is a DSL for representing the structured candidate
profile.

The input to this stage comes from previous stages:

-   candidate information
-   normalized qualifications
-   profile-classification results

The DSL should support information such as:

-   personal information
-   contact information
-   professional experience
-   skills
-   classification results

It should support repeated structured elements where appropriate, such
as:

-   multiple professional experiences
-   education records
-   skills

## Required work

1.  Define the grammar using EBNF.
2.  Identify terminals and non-terminals.
3.  Explain the structural characteristics of the language.
4.  Implement it using textX.
5.  Validate valid candidate profiles.
6.  Reject invalid lexical/syntactic representations.
7.  Generate a short HTML or Markdown visualization after successful
    validation.

## Important boundary

textX is not responsible for discovering skills in the CV.

It receives structured information produced by the previous stages.

------------------------------------------------------------------------

# 10. Testing strategy

Tests must be meaningful and tied to the formal model.

Use `pytest` unless the team explicitly decides otherwise.

## 10.1 Extraction tests

Each regex should have at least:

### Positive case

Input contains the expected information.

``` text
"Technical Skills: JavaScript, React, Git"
```

Expected:

``` text
JavaScript
React
Git
```

### Variation case

Test formatting variations that the regex is supposed to recognize.

### Negative case

Input should not produce a false positive.

### Edge case

Test punctuation, capitalization, spacing, line breaks, etc., when
relevant.

Do not test things the regex was never designed to recognize.

------------------------------------------------------------------------

## 10.2 FST tests

For every normalization rule, test:

``` text
input → expected canonical output
```

Example:

``` text
JS → JAVASCRIPT
```

Also include:

-   different capitalization where supported;
-   punctuation/spacing variants where supported;
-   unknown qualifications that should remain unchanged or be handled
    according to the team's defined policy;
-   canonical ordering.

The test should verify the actual transformation, not just that the code
runs.

------------------------------------------------------------------------

## 10.3 Automata tests

Each profile should have at least:

### Accepted scenario

A qualification sequence that clearly satisfies the profile pattern.

### Rejected --- missing requirement

A sequence missing a required qualification/category.

### Rejected --- invalid pattern

A sequence that contains qualifications but violates the defined
pattern.

### Alternative-path scenario

If the automaton supports alternatives such as:

``` text
React | Angular | Vue
```

test at least two alternatives.

### Boundary/edge scenario

Test the shortest accepted sequence and an important nearby rejected
sequence, when applicable.

The tests must match the formal definition of the automaton.

------------------------------------------------------------------------

## 10.4 Grammar/textX tests

At minimum:

### Valid candidate

A DSL instance that follows the grammar.

### Invalid syntax

A malformed DSL instance that should be rejected.

### Repeated elements

A candidate with multiple experiences, skills, education records, etc.,
if the grammar supports them.

### Classification result

A valid candidate containing the output of the classification stage.

------------------------------------------------------------------------

## 10.5 Integration tests

Once the pipeline is integrated, test complete flows:

``` text
CV → Regex → FST → Sorting → Automaton → textX → Output
```

At minimum include:

-   a Full Stack accepted example;
-   a Machine Learning accepted example;
-   an accepted example for each additional profile;
-   rejected examples;
-   normalization variants;
-   invalid DSL output.

The goal is to prove that the components work together, not only
independently.

------------------------------------------------------------------------

# 11. Shared interfaces between modules

To avoid conflicts between team members, modules should communicate
through clear data structures.

Do not make one module reach into another module's internal variables.

Conceptually:

``` text
ExtractionResult
        ↓
NormalizationResult
        ↓
ClassificationResult
        ↓
CandidateProfile
```

For example:

``` python
class ExtractionResult:
    candidate_name: str
    contact: ...
    qualifications: list[str]
    experience: ...
```

The exact design will be decided by the team.

Before changing a shared model, coordinate with the other members
because a change can affect multiple modules.

------------------------------------------------------------------------

# 12. Team division

Everyone should understand the common pipeline.

The work can be divided mainly by profile for the automata stage:

-   **Johan:** Full Stack Developer
-   **Juan:** Machine Learning Engineer
-   **Jhosua:** additional Software Engineering profile

The additional AI/Data profile and shared components should be assigned
explicitly before implementation.

Important:

> A person owning a profile does not own the entire application.

Everyone is responsible for understanding the common Regex/FST pipeline
and how their automaton integrates into the shared classifier.

Shared components such as:

-   models/interfaces;
-   integration;
-   textX grammar;
-   UI;
-   final tests;

must be coordinated rather than duplicated.

------------------------------------------------------------------------

# 13. Working isolation rules

To minimize merge conflicts:

## Prefer

``` text
Juan → classification/machine_learning.py
Johan → classification/full_stack.py
Jhosua → classification/software_engineering.py
```

and similar isolated files.

## Avoid

Three people simultaneously modifying:

``` text
src/main.py
src/models/...
README.md
requirements.txt
```

unless coordinated.

If a change requires modifying a shared file:

1.  Check whether another member is currently working on it.
2.  Keep the change minimal.
3.  Explain the change in the task/commit description.
4.  Do not rewrite unrelated code.
5.  Do not reformat entire files unnecessarily.

------------------------------------------------------------------------

# 14. Git workflow --- IMPORTANT

## Official assignment requirements

The assignment requires:

-   a GitHub repository created by the team;
-   the repository link registered in the team form;
-   at least **10 commits**;
-   at least **2 hours between each commit**;
-   meaningful commits;
-   a `docs/` directory;
-   project documents written in Markdown;
-   the README must contain necessary project clarifications;
-   individual contributions are evaluated through commits.

The 10 commits are a **minimum**, not a target.

We should NOT artificially stop at 10 commits.

We should NOT create fake commits just to satisfy the number.

A meaningful project may naturally have more than 10 commits.

## Team Git convention

Recommended branch structure:

``` text
main
  |
  └── develop
       |
       ├── feature/...
       ├── chore/...
       ├── docs/...
       └── test/...
```

Use descriptive branch names.

Examples:

``` text
feature/regex-extraction
feature/fst-normalization
feature/full-stack-automaton
feature/ml-automaton
feature/textx-grammar
test/regex-cases
docs/automata-formalization
chore/test-setup
```

Do not create every branch in advance. Create them when the
corresponding work actually begins.

------------------------------------------------------------------------

# 15. CRITICAL RULE FOR AI/CODING AGENTS

Agents must **NOT perform Git operations**.

The human team members control Git.

### Agents must NOT:

``` text
git init
git add
git commit
git push
git merge
git rebase
git reset
git checkout
git switch
git branch
git cherry-pick
```

Do not create or modify branches.

Do not create commits.

Do not push.

Do not rewrite Git history.

### Allowed only when explicitly requested by the human:

Read-only commands such as:

``` text
git status
git log
git diff
```

A `git pull` may be performed only if the human explicitly requests it.

If the agent believes a Git operation is necessary, it must STOP and
tell the human what should be done instead.

The human will handle:

-   branch creation;
-   staging;
-   commits;
-   pushes;
-   merges;
-   pull requests.

------------------------------------------------------------------------

# 16. Commit conventions

Commits should represent real units of work.

Good:

``` text
feat: implement resume skill extraction
feat: add JavaScript normalization transducer
test: add FST normalization cases
feat: implement Full Stack qualification automaton
docs: formalize Full Stack automaton
test: add Full Stack acceptance scenarios
feat: implement candidate profile grammar
```

Bad:

``` text
fix stuff
changes
update
final
final2
test
asdf
```

Also bad:

``` text
feat: implement everything
```

if the commit actually contains unrelated stages.

A commit should ideally answer:

> What meaningful project capability or documentation change was added?

------------------------------------------------------------------------

# 17. Commit timing

The assignment requires at least two hours between commits.

Therefore:

-   do not create artificial commits every few minutes;
-   do not batch an entire week of unrelated work into one huge commit;
-   keep meaningful work units;
-   record when commits are made;
-   if a change is small but not meaningful by itself, combine it with
    the next related meaningful change rather than creating a fake
    commit.

The project can and probably should exceed 10 commits.

------------------------------------------------------------------------

# 18. Documentation conventions

Project documentation inside the repository must be Markdown.

When documenting a formal model, use a consistent structure.

## For an FST document

``` text
# FST — Qualification Normalization

## Purpose

## Transformation

## Formal Definition
### Q
### Σ
### Γ
### δ
### ω
### q0
### F

## Diagram

## Example

## Implementation

## Tests
```

## For an automaton

``` text
# Automaton — Full Stack Developer

## Profile

## Accepted Pattern

## Formal Definition
### Q
### Σ
### δ
### q0
### F

## Automaton Type

## Why this type?

## Diagram

## Examples Accepted

## Examples Rejected

## Implementation

## Tests
```

## For Regex

``` text
# Regex — Skill Extraction

## Purpose

## Pattern

## What language does it recognize?

## Examples

## Implementation

## Tests
```

## For textX

``` text
# Candidate Profile Grammar

## Purpose

## EBNF

## Terminals

## Non-terminals

## Structural Rules

## Valid Examples

## Invalid Examples

## textX Implementation

## Visualization
```

------------------------------------------------------------------------

# 19. Naming conventions

Use clear, consistent names.

Python files:

``` text
snake_case.py
```

Classes:

``` text
PascalCase
```

Functions/variables:

``` text
snake_case
```

Canonical qualifications should have one representation.

For example:

``` text
JAVASCRIPT
REACT
NODE_JS
POSTGRESQL
SCIKIT_LEARN
TENSORFLOW
PYTORCH
```

Do not create multiple canonical names for the same technology.

If a new canonical name is proposed, document it before using it across
modules.

------------------------------------------------------------------------

# 20. Dependencies

The currently known core dependencies are:

``` text
pyformlang
textX
pytest
```

Do not add frameworks or libraries without a concrete reason.

In particular, do not independently introduce:

-   Django
-   Flask
-   FastAPI
-   React
-   database systems
-   unrelated NLP libraries

unless the team explicitly agrees that they are needed.

The assignment requires a Python implementation, but it does not
prescribe a particular web framework.

------------------------------------------------------------------------

# 21. UI rule

The final system needs a UI as part of the complete Python
implementation.

The UI should eventually allow the user to:

1.  provide/select a résumé;
2.  run the ResumeLens pipeline;
3.  see extracted/normalized information where useful;
4.  see classification results;
5.  see the validated structured candidate representation;
6.  see the final HTML/Markdown visualization.

Do not build a complex UI before the formal pipeline is stable.

The UI is not the main academic contribution. The important part is
demonstrating the formal models and their integration.

------------------------------------------------------------------------

# 22. Important conceptual restrictions

These rules must not be violated:

### ResumeLens does NOT rank candidates.

No:

``` text
candidate score = 87%
candidate A is better than candidate B
```

unless explicitly required later by the team and assignment.

The official purpose is qualification-pattern evaluation.

### Regex does NOT normalize.

Regex extracts.

### FST does NOT classify.

FST normalizes equivalent representations.

### Automata do NOT parse the entire résumé.

They recognize qualification patterns after extraction and
normalization.

### textX does NOT replace the automata.

textX structures and validates the candidate profile representation.

### The four profiles are not four independent applications.

They are processed through the same general solution.

------------------------------------------------------------------------

# 23. AI usage requirement

The assignment explicitly allows collaboration with AI but requires a
record of AI interactions.

The team must keep track of:

-   prompts used;
-   relevant student-provided context;
-   AI-generated suggestions that influenced the project;
-   modifications made by the students.

Keep this information in:

``` text
docs/ai-usage.md
```

Do not blindly copy AI output.

Every team member must understand the code and formal models they
submit.

If an AI proposes a formal definition, automaton, grammar, regex, test,
or architecture, the team must review and understand it before
incorporating it.

------------------------------------------------------------------------

# 24. Definition of done for a feature

Before considering a module finished, verify:

``` text
[ ] Code implemented
[ ] Unit tests implemented
[ ] Relevant edge cases tested
[ ] Documentation updated
[ ] Formal model documented if applicable
[ ] Diagram added if applicable
[ ] No unrelated files modified
[ ] Existing tests still pass
[ ] Integration contract is clear
```

For an automaton specifically:

``` text
[ ] 5-tuple complete
[ ] Type identified
[ ] Type justified
[ ] Diagram
[ ] Accepted examples
[ ] Rejected examples
[ ] pyformlang implementation
[ ] Tests
```

For an FST:

``` text
[ ] 7-tuple complete
[ ] Q
[ ] Σ
[ ] Γ
[ ] δ
[ ] ω
[ ] q0
[ ] F
[ ] Diagram
[ ] Transformations
[ ] pyformlang implementation
[ ] Tests
```

For Regex:

``` text
[ ] Pattern defined
[ ] Pattern explained
[ ] Python re implementation
[ ] Positive tests
[ ] Negative tests
[ ] Edge cases
[ ] Output stored in a shared structure
```

For textX:

``` text
[ ] EBNF
[ ] Terminals
[ ] Non-terminals
[ ] Structural explanation
[ ] textX implementation
[ ] Valid cases
[ ] Invalid cases
[ ] Repeated elements where required
[ ] HTML/Markdown visualization
```

------------------------------------------------------------------------

# 25. Before modifying someone else's work

If a task requires changing another person's module:

1.  Read the existing implementation.
2.  Understand its input/output contract.
3.  Avoid rewriting it unnecessarily.
4.  Preserve existing tests.
5.  If the change affects the shared interface, communicate it to the
    team.
6.  Add/update tests for the new behavior.

Never "clean up" another person's code just because you would write it
differently unless that cleanup is part of the agreed task.

------------------------------------------------------------------------

# 26. General rule for agents

When working on ResumeLens:

> Implement only the requested task, respect the existing architecture,
> do not invent requirements, do not replace formal-model decisions
> without justification, and do not perform Git operations.

If something is ambiguous:

> Prefer asking the human/team rather than silently changing the
> architecture.

If a requested change conflicts with the official assignment:

> Point out the conflict before implementing it.

If a solution requires changing another module:

> Explain which module is affected and why.

------------------------------------------------------------------------

# 27. Final system vision

The finished application should conceptually behave like:

``` text
                     USER
                      |
                      v
               +-------------+
               |   Resume    |
               +-------------+
                      |
                      v
               +-------------+
               |   REGEX     |
               |  Extraction |
               +-------------+
                      |
                      v
               +-------------+
               |     FST     |
               | Normalizer  |
               +-------------+
                      |
                      v
             Canonical ordering
                      |
                      v
          +-----------------------+
          |   Profile Automata    |
          |                       |
          | Full Stack            |
          | Machine Learning      |
          | Software Engineering  |
          | AI/Data               |
          +-----------------------+
                      |
                      v
             Classification result
                      |
                      v
               +-------------+
               |   textX /   |
               |  CFG / DSL  |
               +-------------+
                      |
                      v
               Valid candidate
                  profile
                      |
                      v
              HTML / Markdown
```

The important engineering idea is that every stage has **one clear
responsibility** and the stages communicate through well-defined data
structures.

------------------------------------------------------------------------

# 28. Quick checklist before coding

Before starting a task, the agent/member should be able to answer:

``` text
1. Which stage am I working on?
2. Which folder owns this functionality?
3. What is my input?
4. What is my output?
5. Which formal model is required?
6. What must be documented?
7. What tests prove that it works?
8. Am I modifying a shared file?
9. Could this change conflict with another member?
10. Am I accidentally changing a different stage?
11. Am I adding an unnecessary dependency?
12. Am I about to perform a Git operation?
```

If the answer to #12 is yes:

**STOP. The human handles Git.**
