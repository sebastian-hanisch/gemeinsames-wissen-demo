"""Kennzahlen, Zahlenformat und Verdikte als reine Funktionen: `verdict_*(...) -> (Art, Text)`; die App ruft `getattr(st, Art)(Text)`.

Alle Zahlen in den Texten kommen aus der Rechnung (DEMO-PLAYBOOK §1d), nicht aus dem Plan."""

from __future__ import annotations

import gmw_algorithm as A
import gmw_generals as G
from gmw_scenario import GeneralsView, MudView


def de(x: float, digits: int = 3) -> str:
    """Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 1) -> str:
    """Anteil 0..1 als Prozent mit Dezimalkomma."""
    return de(100.0 * x, digits) + " %"


def thousands(x: int) -> str:
    return f"{int(x):,}".replace(",", ".")


def ansage_text(a: int) -> str:
    return "mindestens eines" if a == 1 else f"mindestens {a}"


def dirty_phrase(k: int) -> str:
    return "das schmutzige Kind" if k == 1 else f"die {k} schmutzigen Kinder"


def rounds_formula(k: int, a: int) -> int | None:
    """Runde, in der die schmutzigen Kinder sich melden: k - a + 1 bei Ansage „mindestens a“ (a >= 1); ohne Ansage nie (None)."""
    return None if a < 1 else k - a + 1


# ---------------------------------------------------------------- Verdikte
def verdict_mud(v: MudView) -> tuple[str, str]:
    s = v.settings
    if not v.valid:
        return "warning", (f"Die Ansage „{ansage_text(s.a)} schmutzig“ wäre bei k = {s.k} schmutzigen Kindern falsch. "
                           f"Das Modell lässt nur wahre Ansagen zu; wählen Sie k ≥ a oder eine schwächere Ansage.")
    assert v.play is not None
    dirty = sorted({v.first[i] for i in range(s.k) if v.first[i] is not None})
    clean = sorted({v.first[i] for i in range(s.k, s.n) if v.first[i] is not None})
    if v.play.stuck and not dirty:
        return "info", (f"Ohne Ansage („mindestens eines“) weiß in keiner Runde ein Kind etwas: die Menge der möglichen Welten bleibt bei "
                        f"{thousands(v.sizes[0])} stehen, die Antworten „weiß nicht“ verraten nichts Neues. "
                        + ("Das schmutzige Kind sieht kein anderes schmutziges." if s.k == 1 else f"Dabei sieht jedes der {s.k} schmutzigen Kinder {s.k - 1} andere schmutzige."))
    text = (f"Mit der Ansage „{ansage_text(s.a)}“ {'meldet' if s.k == 1 else 'melden'} sich {dirty_phrase(s.k)} in Runde {dirty[0]}")
    if clean:
        text += f", {'das saubere Kind' if s.s == 1 else f'die {s.s} sauberen Kinder'} in Runde {clean[0]}"
    text += f". Rundenformel k − a + 1 = {rounds_formula(s.k, s.a)}."
    return "success", text


def verdict_levels(v: MudView) -> tuple[str, str]:
    if not v.valid:
        return "warning", "Ohne wahre Ansage gibt es hier keine Wissensleiter."
    fact = f"mindestens {v.ladder_a} Kind{'er' if v.ladder_a > 1 else ''} schmutzig"
    before = (f"Vor der Ansage gilt „{fact}“ als E^{v.level_before}: jedes Kind weiß es (E¹)" if (v.level_before or 0) >= 1
              else f"Vor der Ansage gilt „{fact}“ nur bis E^{v.level_before}")
    deeper = f", jedes weiß, dass jedes es weiß, und so weiter bis zur Tiefe {v.level_before}" if (v.level_before or 0) >= 2 else ""
    tail = (", aber es ist kein gemeinsames Wissen" if not v.common_before else ", und es ist gemeinsames Wissen")
    after = " Nach der Ansage ist es gemeinsames Wissen." if v.common_after else " Ohne Ansage bleibt es dabei."
    return ("info" if v.common_after else "warning"), before + deeper + tail + "." + after


def verdict_generals(v: GeneralsView) -> tuple[str, str]:
    s, r = v.settings, v.summary
    lv = v.levels[-1]
    text = (f"Von {thousands(r.valid)} Entscheidungsregeln, die ohne Befehl nicht angreifen, ist {r.agree} in allen Welten einig (nie angreifen); "
            f"{'keine dieser einigen Regeln greift' if r.agree_and_attack == 0 else f'von diesen einigen Regeln greifen {r.agree_and_attack}'} bei allen {s.m} angekommenen Nachrichten an. Auch wenn alle {s.m} Nachrichten ankommen, gilt „Befehl liegt vor“ nur als E^{lv}, "
            f"gemeinsames Wissen gibt es nirgends.")
    return "success", text


def verdict_rule(v: GeneralsView) -> tuple[str, str]:
    s = v.settings
    if s.c > s.m:
        return "info", (f"Die Schwelle c = {s.c} liegt über der Kettenlänge m = {s.m}: sie wird nie erreicht, niemand greift an, es gibt auch keine Uneinigkeit. "
                        f"Das ist die einzige Regel, die in allen Welten einig ist.")
    ratio = v.disagree / v.both
    e = s.loss_eff
    return "info", (f"Schwelle c = {s.c}, Verlust je Nachricht {pct(e, 1)} (Verlust je Bote {s.eps} %, {s.b} Bote{'n' if s.b > 1 else ''}/Nachricht): beide greifen an mit {pct(v.both)}, "
                    f"genau einer mit {pct(v.disagree)}. Verhältnis Uneinigkeit zu gemeinsamem Angriff {de(ratio, 3)} = ε/(1−ε) mit ε = {de(e, 3)}; "
                    f"es hängt nicht von m und nicht von c ab.")


def mud_rows(v: MudView) -> list[dict]:
    """Tabelle „wer weiß was“: je Kind seine Antwort in jeder Runde."""
    if not v.valid or v.play is None:
        return []
    rows = []
    for i in range(v.settings.n):
        row = {"Kind": f"Kind {i + 1} ({'schmutzig' if i < v.settings.k else 'sauber'})"}
        for r in v.play.rounds:
            row[f"Runde {r.number}"] = "weiß es" if r.answers[i] else "weiß nicht"
        rows.append(row)
    return rows


def level_table(m: int) -> list[dict]:
    rows = []
    for w in G.worlds(m):
        lv = G.knowledge_level(m, w)
        rows.append({"Welt": "kein Befehl" if w == G.NO else f"{w} angekommen", "Wissensebene": "—" if lv == -1 else f"E^{lv}",
                     "gemeinsames Wissen": "ja" if G.is_common_knowledge(m, w) else "nein"})
    return rows


def silent_text(n: int, a: int) -> str:
    return f"{n} Kinder, Ansage {a}"


def k_levels(n: int) -> list[tuple[int, int | None]]:
    """(k, größtes j) vor der Ansage „mindestens eines“, für k = 1..n (Kern, nicht die Formel)."""
    full = A.all_worlds(n)
    fact = A.fact_at_least(full, 1)
    return [(k, A.knowledge_level(full, n, fact, A.actual_world(k))) for k in range(1, n + 1)]
