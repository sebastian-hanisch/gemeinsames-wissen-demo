"""PDF-Export (fpdf2, Kernschriften): Einstellungen und die Verdikte. Erst nach Klick erzeugt (DEMO-PLAYBOOK §1c)."""

from __future__ import annotations

from fpdf import FPDF

from gmw_scenario import Settings

_REPLACE = {"–": "-", "—": "-", "≤": "<=", "≥": ">=", "≠": "!=", "²": "2", "Σ": "Summe", "·": "*", "−": "-", "„": '"', "“": '"', "∞": "unendlich", "→": "->", "ε": "eps",
            "×": "x", "≈": "~", "¹": "1", "⁵": "5", "∈": "in", "…": "...", "‚": ",", "‘": "'", "’": "'", "”": '"', "●": "o", "○": "-", "^": "^"}


def _latin(text: str) -> str:
    """Kernschriften kennen nur Latin-1: Sonderzeichen ersetzen, Markdown-Sterne entfernen."""
    for a, b in _REPLACE.items():
        text = text.replace(a, b)
    return text.replace("**", "").replace("`", "").encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings, verdicts: list[tuple[str, str]]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _latin("Gemeinsames Wissen: Schmutzige Kinder und Zwei Generäle"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _latin(f"Schmutzige Kinder: k = {s.k} schmutzig, {s.s} sauber, Ansage 'mindestens {s.a}' (0 = keine). "
                                f"Zwei Generäle: m = {s.m} Nachrichten, Verlust {s.eps} % je Bote, {s.b} Bote(n) je Nachricht, Schwelle c = {s.c}, Zufalls-Seed {s.seed}."),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Verdikte", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for _, text in verdicts:
        pdf.multi_cell(0, 5, _latin(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _latin("Kripke-Modell und Kettenmodell sind Modellannahmen (Kinder sehen alle anderen, alle sind ehrlich und schlussfolgern fehlerfrei; "
                                "Nachrichten gehen unabhängig voneinander verloren), keine Aussagen über Menschen oder echte Netze. Alle Zahlen sind eigene Rechnung."),
                   new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
