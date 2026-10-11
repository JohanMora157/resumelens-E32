# Literature Review

ResumeLens screens textual résumés with four formal-language tools, one per pipeline stage: regular
expressions (extraction), finite-state transducers (normalization), finite automata (classification)
and a context-free grammar implemented with textX (structured profile and validation). This review
summarizes the sources behind each choice and explains where ResumeLens sits among related work.

## 1. Extracting information from résumés

Résumé extraction has been studied as an information-extraction problem since the mid-2000s. Yu,
Guan and Zhou (2005) propose a *cascaded hybrid model* for extracting information from résumés,
which is representative of the statistical approach: the text is segmented and labeled by models
trained on annotated data. Such systems handle free-form text well, but their decisions depend on
training data and are hard to inspect.

ResumeLens takes the opposite, rule-based route for Stage 1. Regular expressions describe regular
languages, which are exactly the languages recognized by finite automata (Hopcroft, Motwani &
Ullman, 2006), so each extraction pattern (e-mail, phone number, years of experience, education,
skills list) has a precise definition of what it accepts and what it rejects. The trade-off is
coverage: a pattern only recognizes the formats it was designed for. ResumeLens accepts this limit
on purpose, because every extraction can be explained and tested.

## 2. Normalization with finite-state transducers

The same skill appears in many surface forms (`JS`, `Javascript`, `ECMAScript`). Mapping them to one
canonical token is a string-to-string translation, which is the problem finite-state transducers
solve. Mohri (1997) presents transducers as a unifying tool for language and speech processing,
including their composition and determinization, and shows why they are efficient. Beesley and
Karttunen (2003) apply the same machinery to morphology, where surface forms must be related to a
canonical form, the closest classical use case to skill-name normalization.

ResumeLens builds one transducer per technology family. Each alias is an independent path from the
initial state that reads one letter per transition and emits the canonical token on the last one,
which avoids the duplicated output that a shared-prefix design would produce for pairs such as
`Node` and `NodeJS`. The transducers are built and run with Pyformlang (Romero, 2021), a Python
library for formal languages designed for teaching, which implements transducers, automata and
grammars behind a simple interface.

## 3. Classification with finite automata

Deciding whether a candidate fits a profile is a recognition problem: does the set of canonical
skills belong to the language of the profile? Deterministic finite automata are the standard model
for this kind of decision (Hopcroft et al., 2006). In ResumeLens each state records which mandatory
categories have been covered, so the automaton has `2^k` states for `k` categories and accepts when
all of them are covered, in any order. This construction also makes the result independent of the
order in which the candidate wrote the skills.

## 4. A grammar for the candidate profile

The result of the previous stages is written as a program in a small domain-specific language and
checked with a context-free grammar. textX (Dejanović et al., 2017) is a Python tool that builds a
parser and a meta-model from a single grammar and converts programs into Python object graphs; it is
built on a parsing-expression-grammar parser. Parsing expression grammars (Ford, 2004) define a
language through ordered choice, which removes the ambiguity that context-free grammars can have
and makes the parser deterministic. ResumeLens uses textX for syntactic validation and adds semantic
checks (valid ranges, no duplicates) on top of the parsed model before generating HTML and Markdown.

## 5. Automated screening and its limits

Automated screening raises concerns about validity and bias. Raghavan, Barocas, Kleinberg and Levy
(2019) review vendors of algorithmic pre-employment screening tools and find that little is
publicly known about how the tools are built, validated and checked for bias, and they identify the
lack of information about validity as the main gap. This motivates a transparent design: in
ResumeLens every decision comes from an explicit rule that can be read and tested, and the system
does not rank or score candidates. It only reports, for each profile, whether the explicitly stated
qualifications satisfy a formally defined pattern.

## 6. Positioning ResumeLens

| Aspect | Statistical approach (e.g., Yu et al., 2005) | ResumeLens |
|---|---|---|
| Extraction | Learned models trained on annotated résumés | Regular expressions with documented patterns |
| Normalization | Learned or dictionary-based | Finite-state transducers, one per technology family |
| Decision | Model prediction or score | Finite automaton per profile: accepted or rejected |
| Explainability | Limited | Every step is a formal definition |
| Main limit | Needs data; hard to audit | Recognizes only what the rules define |

The main limitation of ResumeLens follows from this choice. Skills that are not in the alias
vocabulary are reported as unknown, the extractor recognizes only the formats it was written for, and
the system evaluates explicit qualifications only. It does not infer skills from context or assess
their quality.

## References

Beesley, K. R., & Karttunen, L. (2003). *Finite State Morphology*. CSLI Publications.
https://web.stanford.edu/group/cslipublications/cslipublications/site/1575864347.shtml

Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž. (2017). TextX: A Python tool for
Domain-Specific Languages implementation. *Knowledge-Based Systems, 115*, 1–4.
https://doi.org/10.1016/j.knosys.2016.10.023

Ford, B. (2004). Parsing expression grammars: A recognition-based syntactic foundation. *Symposium on
Principles of Programming Languages (POPL)*, Venice, Italy. https://bford.info/pub/lang/peg/

Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and
Computation* (3rd ed.). Pearson/Addison-Wesley.

Mohri, M. (1997). Finite-state transducers in language and speech processing. *Computational
Linguistics, 23*(2), 269–311. https://aclanthology.org/J97-2003/

Raghavan, M., Barocas, S., Kleinberg, J., & Levy, K. (2019). *Mitigating bias in algorithmic hiring:
Evaluating claims and practices* (arXiv:1906.09208). https://arxiv.org/abs/1906.09208

Romero, J. (2021). Pyformlang: An educational library for formal language manipulation. In
*Proceedings of the 52nd ACM Technical Symposium on Computer Science Education (SIGCSE '21)* (pp.
576–582). ACM. https://doi.org/10.1145/3408877.3432464

Yu, K., Guan, G., & Zhou, M. (2005). Resume information extraction with cascaded hybrid model. In
*Proceedings of the 43rd Annual Meeting of the Association for Computational Linguistics (ACL '05)*
(pp. 499–506). Association for Computational Linguistics. https://aclanthology.org/P05-1062/