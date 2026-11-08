"""Orakel-Tests gemeinsames-wissen-demo: unabhängige Rechenwege für die Kerneinheiten (DEMO-PLAYBOOK §12).

Schmutzige Kinder: der Kern rechnet mit Bitmasken, Weltenmengen und `frozenset`; die Orakel hier rechnen mit
(1) Tupeln und einer eigenen Eliminationsschleife, (2) einer Induktion über die Zahl der schmutzigen Kinder (ohne Welten),
(3) der Formel k - a + 1 und (4) dem Hamming-Abstand für die Wissensleiter.
Zwei Generäle: Sichten werden aus den Nachrichtenlisten selbst hergeleitet (nicht aus den Paaren des Kerns), alle Regeln mit
itertools.product aufgezählt und in exakten Brüchen gewichtet."""

import itertools
from fractions import Fraction
from math import comb

import pytest

import gmw_algorithm as A
import gmw_generals as G


# ---------------------------------------------------------------- Orakel Schmutzige Kinder
def oracle_mud_rounds(n, actual, a):
    """Weltenmengen als Mengen von Tupeln; Rückgabe: erste Wissensrunde je Kind (None: nie), oder 'falsch'."""
    worlds = set(itertools.product((0, 1), repeat=n))
    if a > 0:
        worlds = {w for w in worlds if sum(w) >= a}
    if actual not in worlds:
        return "falsch"
    first = [None] * n
    for rnd in range(1, n + 3):
        resp = {}
        for w in worlds:
            resp[w] = tuple(tuple(1 - w[j] if j == i else w[j] for j in range(n)) not in worlds for i in range(n))
        for i in range(n):
            if first[i] is None and resp[actual][i]:
                first[i] = rnd
        if all(f is not None for f in first):
            break
        new = {w for w in worlds if resp[w] == resp[actual]}
        if new == worlds:
            break
        worlds = new
    return first


def oracle_mud_induction(k, a):
    """Runde, in der die schmutzigen Kinder reden, ohne Welten: Ein schmutziges Kind sieht k - 1 schmutzige und erwägt „ich bin sauber“,
    dann gäbe es nur k - 1. Wäre k - 1 mit der Ansage unvereinbar (k - 1 < max(a, 1)), weiß es sofort (Runde 1); sonst hätten die k - 1 in der
    Runde r(k - 1) geredet, und ihr Schweigen verrät das Kind in der Runde danach."""
    if a == 0:
        return None

    def r(count):
        return 1 if count - 1 < max(a, 1) else r(count - 1) + 1
    return r(k)


def oracle_level(n, k, a):
    """Größtes j, für das alle Welten im Hamming-Abstand <= j von der wirklichen Welt mindestens a schmutzige Kinder haben."""
    actual = tuple([1] * k + [0] * (n - k))
    worlds = list(itertools.product((0, 1), repeat=n))
    j = -1
    while True:
        ok = all(sum(w) >= a for w in worlds if sum(x != y for x, y in zip(w, actual)) <= j + 1)
        if not ok:
            return j
        j += 1
        if j > n + 1:
            return None


@pytest.mark.parametrize("n", range(1, 7))
@pytest.mark.parametrize("a", range(0, 4))
def test_mud_kernel_matches_the_tuple_oracle_the_induction_and_the_formula(n, a):
    for k in range(0, n + 1):
        actual_t = tuple([1] * k + [0] * (n - k))
        expected = oracle_mud_rounds(n, actual_t, a)
        if k < a:
            assert expected == "falsch"
            with pytest.raises(ValueError):
                A.play(n, A.actual_world(k), a)
            continue
        if k == 0:
            continue  # kein schmutziges Kind: nichts zu melden
        p = A.play(n, A.actual_world(k), a)
        assert A.first_known(p) == expected
        if a >= 1:
            dirty = {expected[i] for i in range(k)}
            assert dirty == {k - a + 1} == {oracle_mud_induction(k, a)}
            if n > k:
                assert {expected[i] for i in range(k, n)} == {k - a + 2}
        else:
            assert all(x is None for x in expected)


@pytest.mark.parametrize("n", range(1, 8))
def test_knowledge_level_matches_the_hamming_distance_oracle(n):
    for a in (1, 2, 3):
        full = A.all_worlds(n)
        fact = A.fact_at_least(full, a)
        for k in range(1, n + 1):
            got = A.knowledge_level(full, n, fact, A.actual_world(k))
            assert got == oracle_level(n, k, a) == (k - a if k >= a else -1)


def test_common_knowledge_matches_a_tuple_breadth_first_search():
    for n in range(1, 6):
        for a in (0, 1, 2):
            worlds = {w for w in itertools.product((0, 1), repeat=n) if sum(w) >= a}
            int_worlds = frozenset(sum(b << i for i, b in enumerate(w)) for w in worlds)
            for k in range(0, n + 1):
                w0 = tuple([1] * k + [0] * (n - k))
                if w0 not in worlds:
                    continue
                seen, todo = {w0}, [w0]
                while todo:
                    cur = todo.pop()
                    for i in range(n):
                        nb = cur[:i] + (1 - cur[i],) + cur[i + 1:]
                        if nb in worlds and nb not in seen:
                            seen.add(nb)
                            todo.append(nb)
                fact_t = {w for w in worlds if sum(w) >= max(a, 1)}
                expect = seen <= fact_t
                fact = A.fact_at_least(int_worlds, max(a, 1))
                assert A.is_common_knowledge(int_worlds, n, fact, A.actual_world(k)) == expect


@pytest.mark.parametrize("n", range(2, 8))
def test_world_count_after_silent_rounds_is_a_binomial_sum(n):
    p = A.play(n, A.actual_world(n), 1)
    for r in range(len(p.rounds)):
        assert len(A.worlds_after(p, r)) == sum(comb(n, j) for j in range(r + 1, n + 1))


# ---------------------------------------------------------------- Orakel Zwei Generäle
def explicit_view(who, k, m):
    """Die Sicht eines Generals nach der Welt k, hergeleitet aus den Nachrichten selbst: was er gesendet und was er empfangen hat."""
    if k == G.NO:
        return ("kein Befehl",) if who == "A" else ((), ())
    sent, received = [], []
    for i in range(1, m + 1):
        sender = "A" if i % 2 == 1 else "B"
        gets_sent = i == 1 or i - 1 <= k
        delivered = i <= k
        if sender == who and gets_sent:
            sent.append(i)
        if sender != who and delivered:
            received.append(i)
    return ("Befehl", tuple(sent), tuple(received)) if who == "A" else (tuple(sent), tuple(received))


@pytest.mark.parametrize("m", range(1, 11))
def test_views_equal_the_explicit_message_views(m):
    for who in ("A", "B"):
        classes = G.views(m, who)
        for x in G.worlds(m):
            for y in G.worlds(m):
                same_core = any(x in c and y in c for c in classes)
                assert same_core == (explicit_view(who, x, m) == explicit_view(who, y, m)), (m, who, x, y)


def oracle_rules(m, eps):
    """Alle Regeln als Zuordnung Sicht -> {0,1} per itertools.product, gewichtet in Brüchen."""
    keys_a = sorted({explicit_view("A", k, m) for k in G.worlds(m)}, key=repr)
    keys_b = sorted({explicit_view("B", k, m) for k in G.worlds(m)}, key=repr)
    p = {k: (1 - eps) ** k * eps for k in range(m)}
    p[m] = (1 - eps) ** m
    out = []
    for dec in itertools.product((0, 1), repeat=len(keys_a) + len(keys_b)):
        da = dict(zip(keys_a, dec[: len(keys_a)]))
        db = dict(zip(keys_b, dec[len(keys_a):]))
        if da[explicit_view("A", G.NO, m)] or db[explicit_view("B", G.NO, m)]:
            continue
        both = sum((p[k] for k in range(m + 1) if da[explicit_view("A", k, m)] and db[explicit_view("B", k, m)]), Fraction(0))
        dis = sum((p[k] for k in range(m + 1) if da[explicit_view("A", k, m)] != db[explicit_view("B", k, m)]), Fraction(0))
        agree = all(da[explicit_view("A", k, m)] == db[explicit_view("B", k, m)] for k in G.worlds(m))
        out.append((both, dis, agree, bool(da[explicit_view("A", m, m)] and db[explicit_view("B", m, m)])))
    return out


@pytest.mark.parametrize("m", range(1, 9))
def test_rule_counts_match_the_oracle_enumeration(m):
    rules = oracle_rules(m, Fraction(1, 5))
    r = G.enumerate_rules(m)
    assert r.valid == len(rules) == 2 ** (m + 1)
    assert r.agree == sum(1 for x in rules if x[2]) == 1
    assert r.agree_and_attack == sum(1 for x in rules if x[2] and x[3]) == 0


@pytest.mark.parametrize("eps", [Fraction(1, 2), Fraction(1, 5), Fraction(1, 10), Fraction(1, 20)])
@pytest.mark.parametrize("m", [3, 5, 7])
def test_pareto_set_of_all_rules_is_the_threshold_family(eps, m):
    oracle = oracle_rules(m, eps)
    core = G.rule_outcomes(m, eps)
    assert sorted((b, d) for b, d, _, _ in oracle) == sorted(core)
    front = G.pareto_front(core)
    formula = [((1 - eps) ** c, eps * (1 - eps) ** (c - 1)) for c in range(1, m + 1)] + [(Fraction(0), Fraction(0))]
    assert front == formula
    assert {d / b for b, d in front if b > 0} == {eps / (1 - eps)}


@pytest.mark.parametrize("m", [2, 5, 8])
def test_threshold_rule_realizes_its_formula(m):
    eps = Fraction(1, 5)
    p = G.world_probs(m, eps)
    for c in range(1, m + 1):
        rule = G.threshold_rule(m, c)
        both = sum(p[k] for k in range(m + 1) if rule["A"][k] and rule["B"][k])
        dis = sum(p[k] for k in range(m + 1) if rule["A"][k] != rule["B"][k])
        assert (both, dis) == G.threshold_probs(eps, c)
        assert not rule["A"][G.NO] and not rule["B"][G.NO]
