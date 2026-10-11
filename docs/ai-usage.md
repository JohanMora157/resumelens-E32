# AI Usage

This document records how generative AI was used in ResumeLens, in line with the course policy
(**level 3**: prompts are logged, and every team member must be able to explain and modify the
code that was produced).

## 1. Tool

| Item | Detail |
|---|---|
| Assistant | Claude (Anthropic), used through Claude Code / the Claude app |
| Used by | Joshua Sayur (main interaction); outputs were shared with Johan Mora and Juan David Fajardo |
| Language of the prompts | Spanish (summarized in English below) |
| Period | October 2026 (project work leading up to the 11 October deadline) |

## 2. Summary of who did what

Being explicit: **the AI generated a large share of the first versions of the code and
documentation.** The team defined the requirements and domain decisions, contributed their own
modules, and verified, ran, debugged and integrated everything.

| Area | Written by the AI (first version) | Written / decided by the team |
|---|---|---|
| Stage 1, Regex extraction | Name extractor (`extraction/name_extractor.py`) and its tests | Regex extractor and its tests (Johan Mora) |
| Stage 2, FST | `transducers.py`, `normalizer.py`, `sorter.py`, `visualize.py`, `data/aliases.json` structure, tests | Requirements, alias vocabulary review, the four profile definitions (canonical order) |
| Stage 3, DFA | `profile_dfa.py`, Full Stack / ML / QA automata, `classifier.py`, tests | Data Analyst automaton and its tests (Juan David Fajardo); profile categories |
| Stage 4, Grammar | `resume.tx`, `builder.py`, `validator.py`, `renderer.py` | `parser.py` and integration tests (Juan David Fajardo); integration into the repo |
| Pipeline, UI, CLI | `pipeline.py`, Streamlit app, `main.py` | Running, manual testing, repository structure and Git workflow |
| Documentation | Drafts of `dfa-design.md`, `grammar-design.md`, `test-design.md`, `profile-definitions.md`, README, corrections to the other design documents, diagram generator script | Review, corrections, final content |

## 3. Log of interactions

Each row summarizes a prompt or group of prompts and the context provided by the student. The AI was used as a support tool throughout the development process, while the team made implementation decisions, adapted suggestions to the existing codebase, and tested and validated the results.

| # | Student prompt (summary) | Context given | AI assistance | What the team did with it |
|---|---|---|---|---|
| 1 | Divide the work among three people and clarify the integrative task | Assignment statement | Helped organize the assignment requirements and outline a possible division of work by module | Agreed on the division of work, prioritizing individual code contributions because the code is graded individually |
| 2 | Suggest a repository structure and clarify the QA and Data Analyst profiles | Assignment requirements and team members | Suggested a folder structure and initial descriptions of the two profiles | Refined the structure based on a classmate's feedback and created the directories on macOS |
| 3 | Support the FST implementation and define the four profiles and their categories | Canonical profile order, existing regex extractor, and classification `__init__` | Provided suggestions for the FST, normalization, sorting, and related tests | Integrated and adapted the suggestions to the existing project, ran the tests, resolved import and path errors, and committed the work in separate commits |
| 4 | Clarify the relationship between classification files and automata, and determine how many were needed | Repository structure | Explained the distinction between profile classification and automata and suggested a DFA module and profile-specific implementations | Coordinated the Data Analyst implementation with Fajardo and retained a separate version of `data_analyst.py` for comparison and integration |
| 5 | Develop the grammar and connect it to the pipeline and UI | Existing pipeline stages | Assisted with grammar syntax and discussed possible implementations for the builder, validator, renderer, pipeline, and Streamlit interface | Integrated the relevant components into the repository, ran Streamlit, and tested the application with sample CVs |
| 6 | Identify cleanup opportunities in the repository | Outputs from `tree`, `grep`, and `git status` | Helped identify potentially unused files, duplicated tests, and opportunities to simplify the CLI and classifier tests | Reviewed and performed the cleanup, then ran the test suite and confirmed that 345 tests passed |
| 7 | Expand validation cases and customize the UI appearance | Screenshots of the UI | Suggested additional CV test scenarios and explained Streamlit theme configuration options | Created sample files in `data/examples/`, ran them through the application, checked the outputs, and adjusted the UI as needed |
| 8 | Improve documentation of the grammar, tests, and README | Contents of `resume.tx` and test counts by file | Helped structure the documentation and suggested content for `grammar-design.md`, `test-design.md`, and the README | Checked the documentation against the actual implementation and repository, and added the relevant project and development environment details |
| 9 | Review the FST documentation and diagrams | Existing `fst-design.md` | Assisted in checking documented figures against the transducers and preparing FST and category-level DFA diagrams, including a generation script | Regenerated the diagrams locally, checked them against the implementation, and committed the resulting files |
| 10 | Check the consistency of the documentation with the implementation | Design documents covering architecture, regex, FST, the Data Analyst automaton, and project context | Helped identify possible inconsistencies and suggested revisions, a `profile-definitions.md` document, and an `architecture.md` code map | Reviewed the proposed changes against the actual code and repository, adjusted the documentation where necessary, and committed the verified changes |

## 4. Errors in the AI output that the team found or fixed

The output was not accepted as-is. Examples of problems found and corrected during the work:

- A shell command appended a dependency that was already in `requirements.txt` (duplicate line);
  fixed by restoring the file, and `streamlit` was later deduplicated by hand.
- textX did not accept `obj_processors` in `metamodel_from_file`; replaced by
  `register_obj_processors`.
- Backslash escaping in the DSL builder did not match what textX unescapes; the builder now strips
  backslashes.
- The name extractor accepted a lowercase phrase as a name; it now requires capitalized words.
- A test expected the wrong sorted list for Data Analyst (PostgreSQL also counts as a query
  language); the expectation was corrected.
- The AI wrongly assumed that some grammar files were written by a teammate; the team clarified
  their origin.
- The first DFA diagrams were unreadable (hundreds of transitions); replaced by category-level
  diagrams.
- A markdown table in the FST design document broke because of `|` characters in math headers.

## 5. Verification

- Automated: `pytest -q` runs **345 tests**, all passing (see `docs/test-design.md`).
- Manual: the Streamlit UI and the CLI were run with sample CVs in `data/examples/`
  (full stack, QA with unknown skills, empty CV, among others), and results were compared with the
  expected profile.
- The numbers in the FST design document (states, transitions, final states per family) were
  checked by building the transducers and counting.

## 6. Understanding of the code

Each member is responsible for being able to explain and modify the modules below:

| Member | Modules they must be able to explain |
|---|---|
| Johan Mora | Regex extraction, `regex_extractor.py` and its tests |
| Juan David Fajardo | Data Analyst DFA, `parser.py`, grammar integration tests |
| Joshua Sayur | FST normalization, DFA construction (`profile_dfa.py`), pipeline and UI |
