"""ResumeLens por consola.

Uso (desde la raíz del repo):
    python -m src.main data/examples/sample_resume.txt
    python -m src.main data/examples/sample_resume.txt --html output/candidate.html
    python -m src.main data/examples/sample_resume.txt --markdown
"""

import argparse
import sys
from pathlib import Path

from src.pipeline import run_pipeline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ResumeLens: clasifica un CV en 4 perfiles profesionales.")
    parser.add_argument("resume", help="ruta de un CV en texto plano (.txt)")
    parser.add_argument("--html", metavar="ARCHIVO", help="guarda la ficha del candidato en HTML")
    parser.add_argument("--markdown", action="store_true", help="imprime la ficha en Markdown")
    args = parser.parse_args(argv)

    path = Path(args.resume)
    if not path.is_file():
        print(f"No existe el archivo: {path}", file=sys.stderr)
        return 1

    result = run_pipeline(path.read_text(encoding="utf-8", errors="replace"))

    print(f"Candidato: {result.name}")
    print(f"Skills extraídas:   {result.extracted['technical_skills']}")
    print(f"Skills canónicas:   {result.canonical_skills}")
    if result.unknown_skills:
        print(f"Skills desconocidas: {result.unknown_skills}")
    print("\nClasificación:")
    for profile, status in result.classification.items():
        print(f"  {profile:28} {status}")

    if result.error:
        print(f"\nEl perfil fue RECHAZADO por la gramática: {result.error}", file=sys.stderr)
        return 2

    print("\nPrograma DSL validado por textX:\n" + result.dsl_text)
    if args.markdown:
        print(result.markdown)
    if args.html:
        Path(args.html).parent.mkdir(parents=True, exist_ok=True)
        Path(args.html).write_text(result.html, encoding="utf-8")
        print(f"HTML guardado en {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())