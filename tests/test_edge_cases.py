"""Randfälle (DEMO-PLAYBOOK §12): kleinste und größte Fälle der beiden Kerne und der Ansichten."""

import pytest

import gmw_algorithm as A
import gmw_constants as C
import gmw_generals as G
from gmw_scenario import Settings, generals_view, mud_view


def test_a_single_child_who_sees_nobody():
    """n = 1: das Kind sieht keinen anderen. Mit Ansage „mindestens eines“ weiß es sofort, ohne Ansage nie."""
    assert A.first_known(A.play(1, 1, 1)) == [1]
    assert A.first_known(A.play(1, 1, 0)) == [None]


def test_exactly_two_children_all_dirty_and_one_dirty():
    assert A.first_known(A.play(2, 3, 1)) == [2, 2]
    assert A.first_known(A.play(2, 1, 1)) == [1, 2]


def test_everybody_dirty_has_no_clean_child_to_wait_for():
    p = A.play(4, A.actual_world(4), 1)
    assert A.first_known(p) == [4, 4, 4, 4] and len(p.rounds) == 4


def test_announcement_equal_to_k_ends_in_round_one():
    for k in (1, 2, 3):
        assert A.first_known(A.play(4, A.actual_world(k), k))[:k] == [1] * k


def test_largest_instance_finishes():
    v = mud_view(Settings(k=C.K_MAX, s=C.S_MAX, a=1))
    assert v.valid and v.play is not None and len(v.sizes) == C.K_MAX + 2 and v.first[0] == C.K_MAX


def test_false_announcement_is_marked_invalid():
    v = mud_view(Settings(k=1, s=2, a=3))
    assert not v.valid and v.play is None


def test_stage_beyond_the_end_shows_the_final_state():
    p = A.play(3, A.actual_world(2), 1)
    assert A.worlds_after(p, 7) == p.rounds[-1].after


def test_chain_with_one_message():
    r = G.enumerate_rules(1)
    assert r.valid == 4
    assert G.threshold_probs(0.5, 1) == (0.5, 0.5)


@pytest.mark.parametrize("m,c", [(1, 1), (1, 11), (10, 10), (10, 11), (3, 4)])
def test_threshold_edges(m, c):
    v = generals_view(Settings(m=m, c=c))
    if c > m:
        assert v.both == 0.0 and v.disagree == 0.0
    else:
        assert v.both > 0 and v.disagree > 0
    assert v.simulated_outcome in {"beide", "einer", "keiner"}


def test_all_minima_and_all_maxima():
    low = Settings(C.K_MIN, C.S_MIN, C.A_MIN, C.STAGE_MIN, C.M_MIN, C.C_MIN, C.EPS_MIN, C.B_MIN, 0)
    high = Settings(C.K_MAX, C.S_MAX, C.A_MAX, C.STAGE_MAX, C.M_MAX, C.C_MAX, C.EPS_MAX, C.B_MAX, C.SEED_MAX)
    for s in (low, high):
        mud_view(s)
        generals_view(s)


def test_extreme_loss_with_five_messengers_is_small_but_positive():
    e = G.effective_loss(0.5, 5)
    assert e == pytest.approx(1 / 32)
    both, dis = G.threshold_probs(e, 10)
    assert 0 < dis < both < 1
