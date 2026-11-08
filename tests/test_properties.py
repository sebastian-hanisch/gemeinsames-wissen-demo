"""Eigenschaftstests: Aussagen, die für ganze Familien von Einstellungen gelten (feste Aufzählung, kein Zufall)."""

from fractions import Fraction

import pytest

import gmw_algorithm as A
import gmw_generals as G


def _first(n, k, a):
    return A.first_known(A.play(n, A.actual_world(k), a))


@pytest.mark.parametrize("n", range(2, 7))
def test_relabeling_the_children_changes_nothing(n):
    """Welche k Kinder schmutzig sind, ist gleichgültig: jede Maske mit k Bits liefert dieselben Runden je Zustand."""
    for k in range(1, n + 1):
        for mask in range(1 << n):
            if A.popcount(mask) != k:
                continue
            first = A.first_known(A.play(n, mask, 1))
            assert {first[i] for i in range(n) if (mask >> i) & 1} == {k}
            assert {first[i] for i in range(n) if not (mask >> i) & 1} <= {k + 1}


@pytest.mark.parametrize("a", [1, 2, 3])
def test_extra_clean_children_do_not_change_when_the_dirty_ones_speak(a):
    for k in range(a, 6):
        rounds = {_first(k + s, k, a)[0] for s in range(0, 4)}
        assert rounds == {k - a + 1}


def test_a_stronger_announcement_never_costs_rounds():
    for n in range(3, 7):
        for k in range(3, n + 1):
            r = [_first(n, k, a)[0] for a in (1, 2, 3)]
            assert r == sorted(r, reverse=True) and r[0] - r[2] == 2


def test_more_dirty_children_need_one_more_round_each():
    for n in range(2, 8):
        rounds = [_first(n, k, 1)[0] for k in range(1, n + 1)]
        assert rounds == list(range(1, n + 1))


def test_no_announcement_leaves_the_world_set_unchanged():
    for n in range(1, 7):
        for k in range(0, n + 1):
            p = A.play(n, A.actual_world(k), 0)
            assert p.stuck and p.rounds[0].after == p.start == A.all_worlds(n)


@pytest.mark.parametrize("m", [1, 3, 6, 10])
def test_the_ratio_of_disagreement_to_attack_does_not_depend_on_c_or_m(m):
    for eps in (Fraction(1, 5), Fraction(1, 3)):
        for c in range(1, m + 1):
            both, dis = G.threshold_probs(eps, c)
            assert dis / both == eps / (1 - eps)


def test_world_probabilities_sum_to_one_for_all_m_and_eps():
    for m in range(1, 11):
        for eps in (Fraction(1, 20), Fraction(1, 2)):
            assert sum(G.world_probs(m, eps).values()) == 1


def test_more_messengers_lower_the_ratio_but_never_to_zero():
    ratios = []
    for b in range(1, 6):
        both, dis = G.threshold_probs(G.effective_loss(0.5, b), 3)
        ratios.append(dis / both)
    assert ratios == sorted(ratios, reverse=True) and min(ratios) > 0


def test_the_absolute_disagreement_is_not_monotone_in_the_number_of_messengers():
    """ε(1−ε)^(c−1) wächst bis ε = 1/c: bei Verlust 50 % je Bote und c = 3 ist die Uneinigkeit mit 2 Boten (ε = 25 %) größer als mit 1."""
    one = G.threshold_probs(G.effective_loss(0.5, 1), 3)[1]
    two = G.threshold_probs(G.effective_loss(0.5, 2), 3)[1]
    assert two > one


def test_a_longer_chain_never_adds_a_better_trade_off():
    """Das kleinste Verhältnis Uneinigkeit / Angriff über alle Regeln ist für jedes m dasselbe."""
    eps = Fraction(1, 5)
    ratios = set()
    for m in range(1, 9):
        pts = [(b, d) for b, d in G.rule_outcomes(m, eps) if b > 0]
        ratios.add(min(d / b for b, d in pts))
    assert ratios == {eps / (1 - eps)}
