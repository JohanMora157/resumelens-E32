"""UI de ResumeLens (Streamlit). Ejecutar desde la raíz del repo:

    streamlit run src/ui/app.py

Entrada: texto de una hoja de vida (pegado o archivo .txt).
Salida: lo extraído, las skills normalizadas, ACCEPTED/REJECTED por perfil, el DSL
generado, su validación con textX y la ficha final en HTML.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # raíz del repo en el path

import streamlit as st
import streamlit.components.v1 as components

from src.grammar.renderer import LABELS, render_html, render_markdown
from src.grammar.validator import DSLValidationError, validate_dsl
from src.normalization.normalizer import normalize_skill
from src.pipeline import run_pipeline

EXAMPLE = """Wednesday Addams
Email: wednesday.addams@example.com | Phone: +1-555-0199
3 years of experience developing web applications.
Education:
Bachelor's degree in Computer Science
Technical Skills:
JS, React.js, NodeJS, Postgres, Git."""


def show_html(html: str, height: int = 520) -> None:
    """Muestra la ficha HTML (ya escapada por el renderizador) según la versión de Streamlit."""
    try:
        components.html(html, height=height, scrolling=True)
    except Exception:  # versiones nuevas sin components.html
        st.iframe(html, height=height)


st.set_page_config(page_title="ResumeLens", layout="wide")
st.title("ResumeLens")
st.caption("¿Las calificaciones explícitas del CV cumplen el patrón formal de un perfil profesional?")

uploaded = st.file_uploader("Sube un CV en .txt (opcional)", type=["txt"])
default = uploaded.read().decode("utf-8", errors="replace") if uploaded else EXAMPLE
cv_text = st.text_area("Texto de la hoja de vida", value=default, height=260)

if st.button("Analizar", type="primary"):
    st.session_state["result"] = run_pipeline(cv_text)

result = st.session_state.get("result")
if result is not None:
    st.header("1. Extracción (expresiones regulares)")
    left, right = st.columns(2)
    contact = result.extracted["contact"]
    left.write({"nombre": result.name, "email": contact["email"], "teléfono": contact["phone"],
                "experiencia": result.extracted["experience"], "educación": result.extracted["education"]})
    right.write({"skills crudas": result.extracted["technical_skills"]})

    st.header("2. Normalización (transductores) y orden por perfil")
    st.table([{"texto del CV": raw, "forma canónica": normalize_skill(raw) or "— (desconocida)"}
              for raw in result.extracted["technical_skills"]])
    for profile, skills in result.sorted_by_profile.items():
        st.write(f"**{LABELS[profile]}** → {', '.join(skills) if skills else '(ninguna skill del perfil)'}")

    st.header("3. Clasificación (autómatas finitos)")
    columns = st.columns(len(result.classification))
    for column, (profile, status) in zip(columns, result.classification.items()):
        (column.success if status == "ACCEPTED" else column.error)(f"{LABELS[profile]}: {status}")

    st.header("4. Perfil del candidato (DSL + textX)")
    dsl = st.text_area("Programa generado (puedes editarlo para probar el rechazo)",
                       value=result.dsl_text, height=260, key="dsl_editor")
    try:
        model = validate_dsl(dsl)
        st.success("Programa válido según la gramática.")
        tab_html, tab_md = st.tabs(["HTML", "Markdown"])
        with tab_html:
            show_html(render_html(model))
            st.download_button("Descargar HTML", render_html(model), file_name="candidate_profile.html")
        with tab_md:
            st.markdown(render_markdown(model))
    except DSLValidationError as error:
        st.error(f"Programa rechazado ({'léxico/sintáctico' if error.kind == 'syntax' else 'semántico'}): {error}")
