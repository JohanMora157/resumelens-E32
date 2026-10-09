"""Etapa 4 - Visualización: modelo textX ya validado -> HTML o Markdown corto."""

from html import escape

LABELS = {
    "FULL_STACK_DEVELOPER": "Full Stack Developer",
    "MACHINE_LEARNING_ENGINEER": "Machine Learning Engineer",
    "QA_ENGINEER": "QA Engineer",
    "DATA_ANALYST": "Data Analyst",
}

_CSS = """
body{font-family:system-ui,sans-serif;max-width:720px;margin:2rem auto;padding:0 1rem;color:#1b1f23}
h1{margin-bottom:.2rem} h2{font-size:1rem;text-transform:uppercase;letter-spacing:.06em;color:#57606a;margin-top:1.6rem}
.chip{display:inline-block;background:#eef2f6;border-radius:999px;padding:.15rem .7rem;margin:.15rem;font-size:.85rem}
.ok{color:#1a7f37;font-weight:600}.no{color:#b3261e;font-weight:600}
table{border-collapse:collapse;width:100%}td{padding:.35rem .5rem;border-bottom:1px solid #e5e9ee}
"""


def _contact(model):
    return [(k, v) for k, v in (("Email", model.contact.email), ("Phone", model.contact.phone)) if v]


def render_html(model) -> str:
    e = escape
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
             f"<title>{e(model.name)}</title><style>{_CSS}</style></head><body>",
             f"<h1>{e(model.name)}</h1>"]

    contact = _contact(model)
    if contact:
        parts.append("<h2>Contact</h2><ul>" + "".join(f"<li>{k}: {e(v)}</li>" for k, v in contact) + "</ul>")

    if model.experiences:
        parts.append("<h2>Experience</h2><ul>")
        for exp in model.experiences:
            extra = f" &mdash; {e(exp.description)}" if exp.description else ""
            parts.append(f"<li>{exp.years} year(s){extra}</li>")
        parts.append("</ul>")

    if model.education.entries:
        parts.append("<h2>Education</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in model.education.entries) + "</ul>")

    if model.skills.names:
        parts.append("<h2>Skills</h2>" + "".join(f"<span class='chip'>{e(s)}</span>" for s in model.skills.names))

    if model.classification.results:
        parts.append("<h2>Profile classification</h2><table>")
        for r in model.classification.results:
            css = "ok" if r.status == "ACCEPTED" else "no"
            parts.append(f"<tr><td>{e(LABELS.get(r.profile, r.profile))}</td><td class='{css}'>{r.status}</td></tr>")
        parts.append("</table>")

    parts.append("</body></html>")
    return "".join(parts)


def render_markdown(model) -> str:
    lines = [f"# {model.name}", ""]
    for k, v in _contact(model):
        lines.append(f"- **{k}:** {v}")
    if model.experiences:
        lines += ["", "## Experience"] + [
            f"- {x.years} year(s)" + (f" — {x.description}" if x.description else "") for x in model.experiences]
    if model.education.entries:
        lines += ["", "## Education"] + [f"- {x}" for x in model.education.entries]
    if model.skills.names:
        lines += ["", "## Skills", ", ".join(f"`{s}`" for s in model.skills.names)]
    if model.classification.results:
        lines += ["", "## Profile classification"] + [
            f"- {LABELS.get(r.profile, r.profile)}: **{r.status}**" for r in model.classification.results]
    return "\n".join(lines) + "\n"