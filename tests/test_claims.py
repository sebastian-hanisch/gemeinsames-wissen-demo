"""Jede Zahl der README wird hier nachgerechnet (DEMO-PLAYBOOK §4). Die Zählungen laufen über das ganze beschriebene Raster, nicht über einen Einzelfall."""

from fractions import Fraction
from math import comb
from pathlib import Path

import pytest

import gmw_algorithm as A
import gmw_constants as C
import gmw_experiments as X
import gmw_generals as G
from gmw_scenario import Settings, generals_view, mud_view


def _dirty_and_clean_rounds(n, k, a):
    first = A.first_known(A.play(n, A.actual_world(k), a))
    return {first[i] for i in range(k)}, {first[i] for i in range(k, n)}


def test_rounds_k_minus_a_plus_1_in_85_cases():
    cases = 0
    for n in range(1, 9):
        for a in (1, 2, 3):
            for k in range(a, n + 1):
                dirty, clean = _dirty_and_clean_rounds(n, k, a)
                assert dirty == {k - a + 1}
                assert clean == (set() if n == k else {k - a + 2})
                cases += 1
    assert cases == 85


def test_without_announcement_nobody_ever_knows():
    cases = 0
    for n in range(1, 7):
        for k in range(1, n + 1):
            p = A.play(n, A.actual_world(k), 0)
            assert p.stuck and A.first_known(p) == [None] * n and len(A.worlds_after(p, 3)) == 1 << n
            cases += 1
    assert cases == 21


def test_knowledge_ladder_depth_in_64_cases():
    cases = 0
    for n in range(1, 8):
        full = A.all_worlds(n)
        start_cache = {}
        for a in (1, 2, 3):
            fact = A.fact_at_least(full, a)
            start = start_cache.setdefault(a, A.announce(full, a))
            start_fact = A.fact_at_least(start, a)
            for k in range(a, n + 1):
                w = A.actual_world(k)
                depth = A.knowledge_level(full, n, fact, w)
                assert depth == k - a
                assert not A.is_common_knowledge(full, n, fact, w)
                assert A.is_common_knowledge(start, n, start_fact, w)
                assert A.first_known(A.play(n, w, a))[0] == depth + 1       # Runde = Tiefe + 1
                cases += 1
    assert cases == 64


def test_world_counts_n_6():
    p = A.play(6, A.actual_world(6), 1)
    assert [len(A.worlds_after(p, r)) for r in range(0, 6)] == [63, 57, 42, 22, 7, 1]
    assert [sum(comb(6, j) for j in range(r + 1, 7)) for r in range(0, 6)] == [63, 57, 42, 22, 7, 1]


def test_chain_levels_equal_delivered_messages():
    for m in range(1, 11):
        assert [G.knowledge_level(m, w) for w in G.worlds(m)] == [-1] + list(range(0, m + 1))
        assert not any(G.is_common_knowledge(m, w) for w in G.worlds(m))


def test_rule_counts_m_1_to_10():
    total = 0
    for m in range(1, 11):
        r = G.enumerate_rules(m)
        assert r.valid == 2 ** (m + 1) and r.agree == 1 and r.agree_and_attack == 0
        assert r.views == m + 3 and sum(G.NO in v for who in "AB" for v in G.views(m, who)) == 2   # README: m + 3 Sichten, zwei davon enthalten NO
        total += r.valid
    assert G.enumerate_rules(1).valid == 4 and G.enumerate_rules(10).valid == 2048
    assert total == 4092


def test_pareto_is_threshold_family_in_16_cells():
    cells = 0
    for eps in (Fraction(1, 2), Fraction(1, 5), Fraction(1, 10), Fraction(1, 20)):
        for m in (3, 5, 7, 9):
            front = G.pareto_front(G.rule_outcomes(m, eps))
            assert front == [((1 - eps) ** c, eps * (1 - eps) ** (c - 1)) for c in range(1, m + 1)] + [(Fraction(0), Fraction(0))]
            assert {d / b for b, d in front if b > 0} == {eps / (1 - eps)}
            cells += 1
    assert cells == 16


def test_default_numbers():
    v = generals_view(Settings())
    assert (v.settings.m, v.settings.c, v.settings.eps, v.settings.b) == (5, 3, 20, 1)
    assert round(100 * v.both, 1) == 51.2 and round(100 * v.disagree, 1) == 12.8
    assert v.disagree / v.both == pytest.approx(0.25)


def test_messengers_table():
    rows = X.messenger_rows(20, 3, 5)
    assert [round(100 * r["genau einer greift an"], 3) for r in rows][:2] == [12.8, 3.686]
    assert round(100 * rows[1]["genau einer greift an"], 2) == 3.69
    assert round(100 * rows[4]["genau einer greift an"], 3) == 0.032
    assert [round(100 * rows[i]["beide greifen an"], 1) for i in (0, 1, 4)] == [51.2, 88.5, 99.9]
    assert rows[0]["Verhältnis"] == pytest.approx(0.25) and rows[4]["Verhältnis"] < 0.001 and all(r["Verhältnis"] > 0 for r in rows)
    half = X.messenger_rows(50, 3, 5)
    assert round(100 * half[0]["genau einer greift an"], 1) == 12.5 and round(100 * half[1]["genau einer greift an"], 1) == 14.1


def test_simulation_within_four_standard_errors():
    rows = X.simulation_rows(5, 3, 0.2, C.GAMES, 35)
    assert C.GAMES == 20000 and len(rows) == 3
    for r in rows:
        assert abs(r["simuliert"] - r["Formel"]) <= 4 * r["Standardfehler"]


def test_preset_three_messengers_loss_is_12_5_percent():
    assert Settings(eps=50, b=3).loss_eff == 0.125


def test_hook_everyone_sees_a_dirty_child_but_it_is_not_common_knowledge():
    """Zur Einleitung: ab zwei schmutzigen Kindern sieht jedes Kind mindestens ein schmutziges anderes, und „mindestens eines“ ist E^(k−1), aber nie gemeinsames Wissen."""
    for k in range(2, 7):
        for s in range(0, 5 - 0):
            n = k + s
            w = A.actual_world(k)
            assert min(A.popcount(w & ~(1 << i)) for i in range(n)) >= 1
            v = mud_view(Settings(k=k, s=s, a=1))
            assert v.level_before == k - 1 >= 1 and not v.common_before and v.common_after


def test_readme_regler_line_names_the_slider_bounds():
    """Die Zeile „Regler“ der README nennt Bereiche und Voreinstellungen der Regler aus gmw_constants.py."""
    root = Path(__file__).resolve().parent.parent
    line = next(x for x in (root / "README.md").read_text(encoding="utf-8").splitlines() if x.startswith("* **Regler**"))

    def de(x):
        return f"{x:,}".replace(",", ".")
    expected = [
        f"schmutzige Kinder k {C.K_MIN} bis {C.K_MAX} ({C.DEFAULT_K})", f"saubere Kinder {C.S_MIN} bis {C.S_MAX} ({C.DEFAULT_S})",
        f"mit a {C.A_MIN} bis {C.A_MAX} ({C.DEFAULT_A})", f"nach Runde {C.STAGE_MIN} bis {C.STAGE_MAX} ({C.DEFAULT_STAGE})",
        f"Nachrichten m {C.M_MIN} bis {C.M_MAX} ({C.DEFAULT_M})", f"Schwelle c {C.C_MIN} bis {C.C_MAX} ({C.DEFAULT_C})",
        f"{C.EPS_MIN} bis {C.EPS_MAX} % in Schritten von 5 ({C.DEFAULT_EPS} %)", f"b {C.B_MIN} bis {C.B_MAX} ({C.DEFAULT_B})",
        f"Zufalls-Seed 0 bis {de(C.SEED_MAX)} ({C.DEFAULT_SEED})", f"höchstens {C.N_MAX}",
    ]
    for part in expected:
        assert part in line, part
