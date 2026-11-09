"""Experimente E1 bis E6: reine Funktionen, die Zeilen (Wörterbücher) und ein Verdikt liefern. Alle Zahlen kommen aus dem Kern."""

from __future__ import annotations

from math import comb

import gmw_algorithm as A
import gmw_generals as G
from gmw_evaluation import de, pct, thousands


def _first_dirty(n: int, k: int, a: int) -> int | None:
    p = A.play(n, A.actual_world(k), a)
    return A.first_known(p)[0]


# ---------------------------------------------------------------- E1 Alle wissen es
def ladder_rows(n: int) -> list[dict]:
    """Je k = 1..n: Tiefe der Wissensleiter vor der Ansage „mindestens eines“, gemeinsames Wissen vorher und nachher, Runde der Meldung."""
    rows = []
    full = A.all_worlds(n)
    fact = A.fact_at_least(full, 1)
    start = A.announce(full, 1)
    start_fact = A.fact_at_least(start, 1)
    for k in range(1, n + 1):
        w = A.actual_world(k)
        rows.append({
            "k": k,
            "Tiefe j (E^j gilt)": A.knowledge_level(full, n, fact, w),
            "gemeinsames Wissen vor der Ansage": A.is_common_knowledge(full, n, fact, w),
            "gemeinsames Wissen nach der Ansage": A.is_common_knowledge(start, n, start_fact, w),
            "Runde der Meldung": _first_dirty(n, k, 1),
        })
    return rows


def verdict_e1(rows: list[dict]) -> tuple[str, str]:
    all_depth = all(r["Tiefe j (E^j gilt)"] == r["k"] - 1 for r in rows)
    all_rounds = all(r["Runde der Meldung"] == r["Tiefe j (E^j gilt)"] + 1 for r in rows)
    never = all(not r["gemeinsames Wissen vor der Ansage"] for r in rows)
    after = all(r["gemeinsames Wissen nach der Ansage"] for r in rows)
    n = len(rows)
    return "success", (f"Bei {n} Kindern gilt in {sum(r['Tiefe j (E^j gilt)'] == r['k'] - 1 for r in rows)} von {n} Fällen: Tiefe der Leiter = k − 1 ({'alle' if all_depth else 'nicht alle'}). "
                       f"Die Meldung kommt in {sum(r['Runde der Meldung'] == r['Tiefe j (E^j gilt)'] + 1 for r in rows)} von {n} Fällen in der Runde nach der Tiefe, also in Runde k ({'alle' if all_rounds else 'nicht alle'}). "
                       f"Vor der Ansage ist es in {n if never else sum(not r['gemeinsames Wissen vor der Ansage'] for r in rows)} von {n} Fällen kein gemeinsames Wissen, "
                       f"danach in {sum(bool(r['gemeinsames Wissen nach der Ansage']) for r in rows)} von {n} Fällen {'ja' if after else 'nicht immer'}.")


# ---------------------------------------------------------------- E2 Ohne Ansage
def silence_rows(n: int) -> list[dict]:
    rows = []
    for k in range(1, n + 1):
        with_a = _first_dirty(n, k, 1)
        without = _first_dirty(n, k, 0)
        rows.append({"k": k, "mit Ansage „mindestens eines“": with_a, "ohne Ansage": without})
    return rows


def verdict_e2(rows: list[dict]) -> tuple[str, str]:
    n = len(rows)
    never = sum(r["ohne Ansage"] is None for r in rows)
    ok = sum(r["mit Ansage „mindestens eines“"] == r["k"] for r in rows)
    return "success", (f"Bei {n} Kindern meldet sich ohne Ansage in {never} von {n} Fällen nie ein Kind; mit Ansage in {ok} von {n} Fällen in Runde k. "
                       f"Für k ≥ 2 sagt die Ansage keinem Kind etwas, das es nicht sieht – sie macht es gemeinsames Wissen.")


# ---------------------------------------------------------------- E3 Runde gegen k und a
def rounds_rows(n: int) -> list[dict]:
    rows = []
    for a in (1, 2, 3):
        row = {"Ansage „mindestens a“": a}
        for k in range(1, n + 1):
            row[f"k = {k}"] = _first_dirty(n, k, a) if k >= a else None
        rows.append(row)
    return rows


def verdict_e3(rows: list[dict], n: int) -> tuple[str, str]:
    cells = [(r["Ansage „mindestens a“"], k, r[f"k = {k}"]) for r in rows for k in range(1, n + 1) if k >= r["Ansage „mindestens a“"]]
    ok = sum(v == k - a + 1 for a, k, v in cells)
    return "success", f"Bei {n} Kindern stimmt die Rundenzahl k − a + 1 in {ok} von {len(cells)} Zellen mit k ≥ a; für k < a ist die Ansage falsch (Zelle leer)."


# ---------------------------------------------------------------- E4 Keine Regel genügt
def rules_rows(m_max: int) -> list[dict]:
    rows = []
    for m in range(1, m_max + 1):
        r = G.enumerate_rules(m)
        rows.append({"Nachrichten m": m, "Sichten": r.views, "gültige Regeln": r.valid, "einig in allen Welten": r.agree, "einig und Angriff bei allen m": r.agree_and_attack})
    return rows


def verdict_e4(rows: list[dict]) -> tuple[str, str]:
    total = sum(r["gültige Regeln"] for r in rows)
    agree = sum(r["einig in allen Welten"] for r in rows)
    live = sum(r["einig und Angriff bei allen m"] for r in rows)
    return "success", (f"Zusammen {thousands(total)} gültige Regeln für m = 1 bis {rows[-1]['Nachrichten m']}: {agree} sind in allen Welten einig (jedes Mal „nie angreifen“); von diesen einigen Regeln {'greift keine' if live == 0 else f'greifen {live}'} bei "
                       f"vollständig angekommener Kette an. Mehr Nachrichten (gezählt bis m = {rows[-1]['Nachrichten m']}) ändern daran nichts.")


# ---------------------------------------------------------------- E5 Boten statt Nachrichten
def messenger_rows(eps_pct: int, c: int, m: int) -> list[dict]:
    rows = []
    for b in range(1, 6):
        e = G.effective_loss(eps_pct / 100.0, b)
        if c <= m:
            both, dis = G.threshold_probs(e, c)
        else:
            both, dis = 0.0, 0.0
        rows.append({"Boten b": b, "Verlust je Nachricht": e, "beide greifen an": both, "genau einer greift an": dis,
                     "Verhältnis": (dis / both) if both > 0 else None})
    return rows


def verdict_e5(rows: list[dict], eps_pct: int, c: int, m: int) -> tuple[str, str]:
    if c > m:
        return "info", f"Schwelle c = {c} liegt über m = {m}: niemand greift an, kein Boten-Effekt zu messen."
    first, last = rows[0], rows[-1]
    monotone = all(rows[i + 1]["genau einer greift an"] <= rows[i]["genau einer greift an"] for i in range(len(rows) - 1))
    tail = ("Auch die Uneinigkeit selbst sinkt in jeder Stufe." if monotone
            else f"Die Uneinigkeit selbst sinkt nicht in jeder Stufe: ε(1−ε)^(c−1) wächst bis ε = 1/c = {de(1 / c, 3)}, danach fällt sie.")
    return "info", (f"Bei Verlust {eps_pct} % je Bote und Schwelle c = {c}: mit 1 Bote je Nachricht greifen beide in {pct(first['beide greifen an'])} an, einer allein in {pct(first['genau einer greift an'])}; "
                    f"mit {last['Boten b']} Boten in {pct(last['beide greifen an'])} bzw. {pct(last['genau einer greift an'], 3)}. Das Verhältnis Uneinigkeit zu Angriff fällt von {de(first['Verhältnis'], 4)} auf "
                    f"{de(last['Verhältnis'], 6)}, bleibt aber bei jeder gerechneten Botenzahl größer als 0. {tail}")


# ---------------------------------------------------------------- E6 Weltenzahl nach s Runden
def worlds_rows(n: int) -> list[dict]:
    """Alle n Kinder schmutzig, Ansage „mindestens eines“: Zahl der möglichen Welten nach s stillen Runden (s = 0 bis n − 1; in Runde n wissen es alle)
    und die Summe der Binomialkoeffizienten dazu."""
    p = A.play(n, A.actual_world(n), 1)
    rows = []
    for s in range(0, len(p.rounds)):
        size = len(A.worlds_after(p, s))
        rows.append({"Runden vorbei": s, "mögliche Welten (Kripke)": size, "Σ_{q>s} C(n, q)": sum(comb(n, q) for q in range(s + 1, n + 1))})
    return rows


def verdict_e6(rows: list[dict], n: int) -> tuple[str, str]:
    same = all(r["mögliche Welten (Kripke)"] == r["Σ_{q>s} C(n, q)"] for r in rows)
    return "success", (f"Bei {n} Kindern schrumpft die Weltenmenge von {thousands(rows[0]['mögliche Welten (Kripke)'])} nach der Ansage auf {rows[-1]['mögliche Welten (Kripke)']} nach "
                       f"{rows[-1]['Runden vorbei']} stillen Runden; die Zählung stimmt in {sum(r['mögliche Welten (Kripke)'] == r['Σ_{q>s} C(n, q)'] for r in rows)} von {len(rows)} Zeilen mit der Summe der Binomialkoeffizienten überein"
                       f"{'' if same else ' (nicht überall)'}.")


# ---------------------------------------------------------------- Formel gegen Simulation (Zwei Generäle)
def simulate_rule(m: int, c: int, eps_eff: float, games: int, seed: int) -> dict[str, int]:
    """Spielt `games` Ketten Nachricht für Nachricht (SplitMix64) und zählt die Ausgänge der Schwellenregel c."""
    from gmw_rng import SplitMix64
    rng = SplitMix64(seed)
    rule = G.threshold_rule(m, c)
    counts = {"beide": 0, "einer": 0, "keiner": 0}
    for _ in range(games):
        k = G.draw_world(m, eps_eff, rng)
        da, db = rule["A"][k], rule["B"][k]
        counts["beide" if da and db else ("einer" if da != db else "keiner")] += 1
    return counts


def simulation_rows(m: int, c: int, eps_eff: float, games: int, seed: int) -> list[dict]:
    counts = simulate_rule(m, c, eps_eff, games, seed)
    if c <= m:
        both, dis = G.threshold_probs(eps_eff, c)
    else:
        both, dis = 0.0, 0.0
    exact = {"beide": both, "einer": dis, "keiner": 1.0 - both - dis}
    rows = []
    for key in ("beide", "einer", "keiner"):
        p = exact[key]
        se = (p * (1 - p) / games) ** 0.5
        rows.append({"Ausgang": key, "Formel": p, "simuliert": counts[key] / games, "Standardfehler": se})
    return rows


def verdict_simulation(rows: list[dict], games: int) -> tuple[str, str]:
    inside = sum(abs(r["simuliert"] - r["Formel"]) <= 4 * r["Standardfehler"] + 1e-12 for r in rows)
    return "success", f"Bei {thousands(games)} gespielten Ketten liegen {inside} von {len(rows)} Ausgängen innerhalb von 4 Standardfehlern um die Formel."
