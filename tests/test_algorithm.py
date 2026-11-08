"""Kern gegen Handrechnung: jede Einheit der Schmutzigen Kinder und der Zwei Generäle an einer Mini-Instanz (DEMO-PLAYBOOK §1b)."""

import pytest

import gmw_algorithm as A
import gmw_generals as G


# ---------------------------------------------------------------- Schmutzige Kinder
def test_popcount_and_world_counts():
    assert [A.popcount(w) for w in (0, 1, 3, 7, 5)] == [0, 1, 2, 3, 2]
    assert len(A.all_worlds(3)) == 8


def test_announce_sizes_for_three_children():
    """Welten mit mindestens a schmutzigen Kindern bei n = 3: C(3,1)+C(3,2)+C(3,3) = 7, 3+1 = 4, 1; a = 0 ändert nichts (8)."""
    full = A.all_worlds(3)
    assert [len(A.announce(full, a)) for a in (0, 1, 2, 3)] == [8, 7, 4, 1]


def test_knows_own_by_hand(zwei_kinder):
    n, S = zwei_kinder
    assert A.knows_own(S, 1, 0) is True    # Welt 01: Kind 1 sähe sich sauber nur in Welt 00, die ausgeschieden ist
    assert A.knows_own(S, 1, 1) is False   # Kind 2 kann Welt 01 von Welt 11 nicht unterscheiden
    assert A.answers_in(S, 3, n) == (False, False)
    assert A.answers_in(S, 1, n) == (True, False)


def test_hear_answers_leaves_only_worlds_with_the_same_answers(zwei_kinder):
    n, S = zwei_kinder
    assert A.hear_answers(S, (False, False), n) == frozenset({3})
    assert A.hear_answers(S, (True, False), n) == frozenset({1})


def test_play_two_children_both_dirty_by_hand(zwei_kinder):
    n, _ = zwei_kinder
    p = A.play(2, A.actual_world(2), 1)
    assert [r.answers for r in p.rounds] == [(False, False), (True, True)]
    assert A.first_known(p) == [2, 2]
    assert not p.stuck


def test_play_two_children_one_dirty_by_hand():
    """Nur Kind 1 schmutzig: Kind 1 sieht Kind 2 sauber und weiß es in Runde 1; Kind 2 erfährt es durch die Antwort in Runde 2."""
    p = A.play(2, A.actual_world(1), 1)
    assert A.first_known(p) == [1, 2]


def test_play_without_announcement_is_stuck():
    p = A.play(3, A.actual_world(2), 0)
    assert p.stuck and A.first_known(p) == [None, None, None] and len(p.rounds) == 1


def test_play_rejects_a_false_announcement():
    with pytest.raises(ValueError):
        A.play(3, A.actual_world(1), 2)


def test_worlds_after_is_constant_after_the_end():
    p = A.play(3, A.actual_world(3), 1)
    assert A.worlds_after(p, 0) == p.start and len(p.start) == 7
    assert A.worlds_after(p, 99) == A.worlds_after(p, len(p.rounds))


def test_everyone_knows_two_children_by_hand():
    """n = 2, Tatsache „mindestens eines“ = {1, 2, 3}: E ergibt {3} (nur dort sind beide Nachbarn auch in der Tatsache), E² ist leer."""
    full = A.all_worlds(2)
    fact = A.fact_at_least(full, 1)
    e1 = A.everyone_knows(full, 2, fact)
    assert e1 == frozenset({3})
    assert A.everyone_knows(full, 2, e1) == frozenset()
    assert A.knowledge_level(full, 2, fact, 3) == 1
    assert A.knowledge_level(full, 2, fact, 1) == 0
    assert A.knowledge_level(full, 2, fact, 0) == -1


def test_common_knowledge_before_and_after_the_announcement():
    full = A.all_worlds(3)
    fact = A.fact_at_least(full, 1)
    assert not A.is_common_knowledge(full, 3, fact, 7)
    start = A.announce(full, 1)
    assert A.is_common_knowledge(start, 3, A.fact_at_least(start, 1), 7)


def test_reachable_in_the_full_cube_is_everything():
    assert A.reachable(A.all_worlds(3), 3, 5) == A.all_worlds(3)


# ---------------------------------------------------------------- Zwei Generäle
def test_views_for_two_messages_by_hand():
    """m = 2, Welten NO, 0, 1, 2: A unterscheidet 0 und 1 nicht (seine Nachricht 1 könnte verloren sein), B unterscheidet NO und 0 sowie 1 und 2 nicht."""
    assert G.views(2, "A") == [frozenset({-1}), frozenset({0, 1}), frozenset({2})]
    assert G.views(2, "B") == [frozenset({-1, 0}), frozenset({1, 2})]


def test_knowledge_level_equals_number_of_delivered_messages_for_m_2():
    assert [G.knowledge_level(2, w) for w in G.worlds(2)] == [-1, 0, 1, 2]


def test_no_common_knowledge_anywhere_in_the_chain():
    assert not any(G.is_common_knowledge(3, w) for w in G.worlds(3))


def test_enumerate_rules_for_one_message_by_hand():
    """m = 1: Sichten A {NO}, {0,1}; B {NO,0}, {1}: vier Sichten, 16 Regeln, 4 mit „ohne Befehl kein Angriff“ (A(NO) und B(NO,0) warten).
    Einig überall: A({0,1}) = B({NO,0}) = Warten in Welt 0, in Welt 1 A = B({1}); A({0,1}) muss warten, also auch B({1}): genau 1 Regel."""
    r = G.enumerate_rules(1)
    assert (r.views, r.valid, r.agree, r.agree_and_attack) == (4, 4, 1, 0)


def test_world_probabilities_sum_to_one():
    from fractions import Fraction
    p = G.world_probs(4, Fraction(1, 5))
    assert sum(p.values()) == 1 and p[0] == Fraction(1, 5) and p[4] == Fraction(4, 5) ** 4


def test_threshold_probs_by_hand():
    from fractions import Fraction
    both, dis = G.threshold_probs(Fraction(1, 2), 2)
    assert (both, dis) == (Fraction(1, 4), Fraction(1, 4))


def test_threshold_rule_c_1_and_c_2_by_hand():
    """m = 2, c = 1: A greift an, wenn seine Sicht nur Welten >= 0 enthält (Welt 0, 1, 2), B, wenn nur >= 1 (Welt 1, 2): nur in Welt 0 uneinig."""
    r = G.threshold_rule(2, 1)
    assert r["A"] == {-1: False, 0: True, 1: True, 2: True}
    assert r["B"] == {-1: False, 0: False, 1: True, 2: True}
    r2 = G.threshold_rule(2, 2)   # B ist unsicher zwischen 1 und 2: B greift an, wenn Sicht >= 1; A, wenn Sicht >= 2
    assert r2["B"] == {-1: False, 0: False, 1: True, 2: True}
    assert r2["A"] == {-1: False, 0: False, 1: False, 2: True}


def test_threshold_beyond_the_chain_never_attacks():
    r = G.threshold_rule(3, 4)
    assert not any(r["A"].values()) and not any(r["B"].values())


def test_effective_loss():
    assert G.effective_loss(0.5, 3) == pytest.approx(0.125)


def test_draw_world_stops_at_the_first_loss():
    class Fixed:
        def __init__(self, values):
            self.values = list(values)

        def uniform(self):
            return self.values.pop(0)
    assert G.draw_world(5, 0.3, Fixed([0.9, 0.9, 0.1])) == 2     # zwei Nachrichten kommen an, die dritte geht verloren
    assert G.draw_world(2, 0.3, Fixed([0.9, 0.9])) == 2           # alle kommen an
    assert G.draw_world(3, 0.3, Fixed([0.1])) == 0
