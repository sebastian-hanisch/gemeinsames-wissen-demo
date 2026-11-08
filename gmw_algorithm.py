"""Kern, Teil 1: Schmutzige Kinder als Kripke-Modell (nur Standardbibliothek).

Eine Welt ist eine Bitmaske über die n Kinder (Bit i gesetzt: Kind i ist schmutzig). Kind i sieht alle anderen, nicht sich selbst:
Es unterscheidet die Welten w und w XOR (1 << i) nicht. Eine öffentliche Ansage oder eine gehörte Antwortrunde schneidet die Menge
der Welten, die noch möglich sind, auf eine Teilmenge zu. Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben
(DEMO-PLAYBOOK §1b); `play` ruft nur der Reihe nach auf."""

from __future__ import annotations

from dataclasses import dataclass


def popcount(w: int) -> int:
    """Zahl der schmutzigen Kinder in der Welt w."""
    return bin(w).count("1")


def all_worlds(n: int) -> frozenset[int]:
    """Alle 2^n Welten."""
    return frozenset(range(1 << n))


def announce(worlds: frozenset[int], a: int) -> frozenset[int]:
    """Öffentliche Ansage „mindestens a Kinder sind schmutzig“: nur Welten mit popcount >= a bleiben. a = 0 ändert nichts."""
    return frozenset(w for w in worlds if popcount(w) >= a)


def knows_own(worlds: frozenset[int], w: int, i: int) -> bool:
    """Kind i weiß in Welt w, ob es selbst schmutzig ist, genau dann, wenn die Welt mit gekipptem Bit i nicht mehr möglich ist."""
    return (w ^ (1 << i)) not in worlds


def answers_in(worlds: frozenset[int], w: int, n: int) -> tuple[bool, ...]:
    """Antworten aller n Kinder auf „weißt du, ob du schmutzig bist?“ in der Welt w."""
    return tuple(knows_own(worlds, w, i) for i in range(n))


def hear_answers(worlds: frozenset[int], heard: tuple[bool, ...], n: int) -> frozenset[int]:
    """Alle haben die Antworten `heard` gehört: es bleiben die Welten, in denen dieselben Antworten gefallen wären."""
    return frozenset(w for w in worlds if answers_in(worlds, w, n) == heard)


@dataclass(frozen=True)
class Round:
    number: int                      # 1, 2, ...
    worlds: frozenset[int]           # möglich vor der Runde
    answers: tuple[bool, ...]        # Antworten in der wirklichen Welt
    after: frozenset[int]            # möglich nach dem Hören der Antworten


@dataclass(frozen=True)
class Play:
    n: int
    actual: int
    a: int
    start: frozenset[int]            # Weltenmenge nach der Ansage, vor Runde 1
    rounds: tuple[Round, ...]
    stuck: bool                      # True: Weltenmenge ändert sich nicht mehr, und nicht alle Kinder wissen es


def actual_world(k: int) -> int:
    """Die ersten k Kinder sind schmutzig (die Kinder sind austauschbar)."""
    return (1 << k) - 1


def play(n: int, actual: int, a: int, max_rounds: int | None = None) -> Play:
    """Die Runden des Spiels: alle antworten gleichzeitig, alle hören alle Antworten, bis alle Kinder es wissen oder nichts mehr passiert.

    Wirft ValueError, wenn die Ansage in der wirklichen Welt falsch wäre (popcount(actual) < a): der Vater sagt nur Wahres."""
    if popcount(actual) < a:
        raise ValueError(f"Die Ansage „mindestens {a}“ ist falsch bei {popcount(actual)} schmutzigen Kindern")
    limit = max_rounds if max_rounds is not None else n + 2
    start = announce(all_worlds(n), a)
    worlds = start
    rounds: list[Round] = []
    stuck = False
    for number in range(1, limit + 1):
        ans = answers_in(worlds, actual, n)
        after = hear_answers(worlds, ans, n)
        rounds.append(Round(number, worlds, ans, after))
        if all(ans):
            break
        if after == worlds:
            stuck = True
            break
        worlds = after
    return Play(n, actual, a, start, tuple(rounds), stuck)


def first_known(p: Play) -> list[int | None]:
    """Je Kind die erste Runde, in der es seinen Zustand weiß (None: nie)."""
    out: list[int | None] = [None] * p.n
    for r in p.rounds:
        for i, yes in enumerate(r.answers):
            if yes and out[i] is None:
                out[i] = r.number
    return out


def worlds_after(p: Play, stage: int) -> frozenset[int]:
    """Mögliche Welten nach `stage` Runden (0: nach der Ansage). Nach dem Ende des Spiels ändert sich nichts mehr."""
    if stage <= 0:
        return p.start
    idx = min(stage, len(p.rounds)) - 1
    return p.rounds[idx].after


# ---------------------------------------------------------------- Wissensebenen und gemeinsames Wissen
def neighbors(w: int, n: int, worlds: frozenset[int]) -> list[int]:
    """Die Welten, die ein Kind von w nicht unterscheidet (höchstens n), soweit sie noch möglich sind."""
    return [w ^ (1 << i) for i in range(n) if (w ^ (1 << i)) in worlds]


def everyone_knows(worlds: frozenset[int], n: int, fact: frozenset[int]) -> frozenset[int]:
    """E(fact): die Welten, in denen jedes Kind weiß, dass `fact` gilt (fact gilt in w und in allen von dort unterscheidbaren Welten)."""
    return frozenset(w for w in worlds if w in fact and all(v in fact for v in neighbors(w, n, worlds)))


def knowledge_level(worlds: frozenset[int], n: int, fact: frozenset[int], w: int, limit: int = 64) -> int | None:
    """Größtes j, für das E^j(fact) in w gilt; None, wenn die Iteration einen Fixpunkt erreicht, der w enthält (gemeinsames Wissen).
    Gilt fact in w nicht, ist die Antwort -1."""
    if w not in fact:
        return -1
    current = fact
    level = 0
    for _ in range(limit):
        nxt = everyone_knows(worlds, n, current)
        if nxt == current:
            return None
        if w not in nxt:
            return level
        current = nxt
        level += 1
    raise RuntimeError("Wissensebene nicht abgeschlossen")


def reachable(worlds: frozenset[int], n: int, w: int) -> frozenset[int]:
    """Alle Welten, die über beliebig viele Unterscheidungslücken eines Kindes von w aus erreichbar sind."""
    seen = {w}
    todo = [w]
    while todo:
        cur = todo.pop()
        for v in neighbors(cur, n, worlds):
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return frozenset(seen)


def is_common_knowledge(worlds: frozenset[int], n: int, fact: frozenset[int], w: int) -> bool:
    """C(fact) in w: fact gilt in der ganzen von w erreichbaren Komponente."""
    return w in worlds and reachable(worlds, n, w) <= fact


def fact_at_least(worlds: frozenset[int], a: int) -> frozenset[int]:
    """Die Tatsache „mindestens a Kinder sind schmutzig“ als Weltenmenge."""
    return frozenset(w for w in worlds if popcount(w) >= a)
