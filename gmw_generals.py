"""Kern, Teil 2: Zwei Generäle im Kettenmodell (nur Standardbibliothek).

Modell: General A hat einen Angriffsbefehl und schickt Nachricht 1 an B. Nachricht i wird nur gesendet, wenn Nachricht i - 1 angekommen ist
(jeder bestätigt, was er bekommt), höchstens m Nachrichten. Welt k = Zahl der angekommenen Nachrichten (0 bis m); die Welt NO (= -1) ist
die Welt ohne Befehl, in der A nichts sendet. Eine Sicht ist die Klasse der Welten, die ein General nicht unterscheidet: A kann nicht wissen,
ob seine zuletzt gesendete Nachricht ankam (Welten 2t und 2t + 1), B ebenso (Welten 2t + 1 und 2t + 2); dass es B nicht schon in der Welt 0 von der Welt NO
unterscheiden kann, folgt daraus, dass B ohne Nachricht nichts sieht.
Eine Entscheidungsregel ordnet jeder Sicht „Angriff“ oder „Warten“ zu."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

NO = -1  # Welt ohne Befehl


def worlds(m: int) -> list[int]:
    """NO, 0, 1, ..., m."""
    return [NO] + list(range(m + 1))


def _pairs(who: str, m: int) -> list[tuple[int, int]]:
    """Paare von Welten, die der General `who` nicht unterscheidet."""
    if who == "A":
        return [(k, k + 1) for k in range(0, m) if k % 2 == 0]
    return [(NO, 0)] + [(k, k + 1) for k in range(0, m) if k % 2 == 1]


def views(m: int, who: str) -> list[frozenset[int]]:
    """Die Sichten von `who` als Klassen ununterscheidbarer Welten, sortiert nach der kleinsten Welt."""
    parent = {w: w for w in worlds(m)}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for x, y in _pairs(who, m):
        parent[find(x)] = find(y)
    classes: dict[int, set[int]] = {}
    for w in worlds(m):
        classes.setdefault(find(w), set()).add(w)
    return sorted((frozenset(c) for c in classes.values()), key=min)


def view_of(m: int, who: str, w: int) -> frozenset[int]:
    for v in views(m, who):
        if w in v:
            return v
    raise ValueError(w)


def knowledge_level(m: int, w: int) -> int | None:
    """Größtes j mit E^j(„A hat einen Befehl“) in der Welt w (-1 in der Welt NO); None bei gemeinsamem Wissen (kommt in der Kette nie vor)."""
    fact = {x for x in worlds(m) if x != NO}
    if w not in fact:
        return -1
    level = 0
    current = set(fact)
    for _ in range(4 * m + 8):
        nxt = {x for x in worlds(m) if x in current and all(y in current for who in ("A", "B") for y in view_of(m, who, x))}
        if nxt == current:
            return None
        if w not in nxt:
            return level
        current = nxt
        level += 1
    raise RuntimeError("Ebene nicht abgeschlossen")


def is_common_knowledge(m: int, w: int) -> bool:
    """C(„Befehl liegt vor“) in w: die erreichbare Komponente enthält NO nicht (sie enthält es immer, die Kette ist zusammenhängend)."""
    seen = {w}
    todo = [w]
    while todo:
        cur = todo.pop()
        for who in ("A", "B"):
            for y in view_of(m, who, cur):
                if y not in seen:
                    seen.add(y)
                    todo.append(y)
    return NO not in seen


# ---------------------------------------------------------------- Entscheidungsregeln
@dataclass(frozen=True)
class RuleSummary:
    m: int
    views: int            # Zahl der Sichten beider Generäle zusammen
    valid: int            # Regeln, in denen ohne Befehl keiner angreift
    agree: int            # davon: in jeder Welt greifen beide an oder beide warten
    agree_and_attack: int  # davon: bei allen m angekommenen Nachrichten greifen beide an


def _decisions(m: int):
    va, vb = views(m, "A"), views(m, "B")
    ia = {w: i for i, v in enumerate(va) for w in v}
    ib = {w: len(va) + i for i, v in enumerate(vb) for w in v}
    return va, vb, ia, ib


def enumerate_rules(m: int) -> RuleSummary:
    """Zählt alle 2^V Regeln (V = Sichten beider Generäle) und prüft Gültigkeit, Einigkeit und Angriff."""
    va, vb, ia, ib = _decisions(m)
    total = len(va) + len(vb)
    valid = agree = live = 0
    for bits in range(1 << total):
        if (bits >> ia[NO]) & 1 or (bits >> ib[NO]) & 1:
            continue
        valid += 1
        if all(((bits >> ia[w]) & 1) == ((bits >> ib[w]) & 1) for w in worlds(m)):
            agree += 1
            if (bits >> ia[m]) & 1 and (bits >> ib[m]) & 1:
                live += 1
    return RuleSummary(m, total, valid, agree, live)


def world_probs(m: int, eps):
    """Wahrscheinlichkeit der Welt k = 0..m bei Verlust eps je Nachricht (Befehl liegt vor): Kette bricht bei der ersten verlorenen Nachricht."""
    p = {k: (1 - eps) ** k * eps for k in range(m)}
    p[m] = (1 - eps) ** m
    return p


def rule_outcomes(m: int, eps):
    """Für jede gültige Regel (ohne Befehl kein Angriff): (P(beide greifen an), P(genau einer greift an)) bei Verlust eps.
    eps darf float oder Fraction sein."""
    va, vb, ia, ib = _decisions(m)
    total = len(va) + len(vb)
    p = world_probs(m, eps)
    out = []
    for bits in range(1 << total):
        if (bits >> ia[NO]) & 1 or (bits >> ib[NO]) & 1:
            continue
        both = dis = 0 * eps
        for k in range(m + 1):
            da, db = (bits >> ia[k]) & 1, (bits >> ib[k]) & 1
            if da and db:
                both = both + p[k]
            elif da != db:
                dis = dis + p[k]
        out.append((both, dis))
    return out


def pareto_front(points):
    """Pareto-Punkte (P(beide), P(uneinig)): zu jeder Angriffswahrscheinlichkeit die kleinste Uneinigkeit, nur echte Verbesserungen."""
    best: dict = {}
    for both, dis in points:
        if both not in best or dis < best[both]:
            best[both] = dis
    front = []
    cur = None
    for both in sorted(best, reverse=True):
        if cur is None or best[both] < cur:
            front.append((both, best[both]))
            cur = best[both]
    return front


def threshold_probs(eps_eff, c: int):
    """Schwellenregel c: beide greifen an mit (1 - e)^c, genau einer mit e (1 - e)^(c - 1) (c >= 1, c <= m); darüber (c > m): nie angreifen."""
    if c < 1:
        raise ValueError("c >= 1")
    return (1 - eps_eff) ** c, eps_eff * (1 - eps_eff) ** (c - 1)


def threshold_rule(m: int, c: int) -> dict[str, dict[int, bool]]:
    """Die Schwellenregel c als Entscheidung je Welt: der General, der die Welten c - 1 und c nicht unterscheidet (A bei geradem c - 1, sonst B),
    greift an, wenn seine Sicht nur Welten >= c - 1 enthält; der andere, wenn seine Sicht nur Welten >= c enthält. c > m: niemand greift an."""
    out = {"A": {}, "B": {}}
    if c > m:
        for who in out:
            for w in worlds(m):
                out[who][w] = False
        return out
    unsure = "A" if (c - 1) % 2 == 0 else "B"
    for who in ("A", "B"):
        limit = c - 1 if who == unsure else c
        for w in worlds(m):
            out[who][w] = min(view_of(m, who, w)) >= limit
    return out


def outcome(m: int, c: int, k: int) -> str:
    """Ergebnis der Schwellenregel c in der Welt k: 'beide', 'einer', 'keiner'."""
    rule = threshold_rule(m, c)
    da, db = rule["A"][k], rule["B"][k]
    return "beide" if da and db else ("einer" if da != db else "keiner")


def draw_world(m: int, eps_eff: float, rng) -> int:
    """Zieht die Welt: Nachricht für Nachricht, jede geht mit Wahrscheinlichkeit eps_eff verloren; `rng.uniform()` liefert [0, 1)."""
    k = 0
    while k < m:
        if rng.uniform() < eps_eff:
            break
        k += 1
    return k


def effective_loss(eps, b: int):
    """Eine Nachricht, die b Boten unabhängig voneinander trägt, geht nur verloren, wenn alle b verloren gehen: eps^b."""
    return eps ** b


def fraction_eps(eps_pct: int) -> Fraction:
    return Fraction(eps_pct, 100)
