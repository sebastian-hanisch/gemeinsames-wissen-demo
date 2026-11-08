"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jeder Zweig der Art steht hier."""

import gmw_evaluation as ev
import gmw_experiments as X
from gmw_scenario import Settings, generals_view, mud_view


def test_verdict_mud_standard_names_the_rounds():
    kind, text = ev.verdict_mud(mud_view(Settings(k=3, s=1, a=1)))
    assert kind == "success"
    assert "die 3 schmutzigen Kinder in Runde 3" in text and "das saubere Kind in Runde 4" in text and "k − a + 1 = 3" in text


def test_verdict_mud_single_dirty_child_and_several_clean_ones():
    kind, text = ev.verdict_mud(mud_view(Settings(k=1, s=2, a=1)))
    assert "meldet sich das schmutzige Kind in Runde 1" in text and "die 2 sauberen Kinder in Runde 2" in text


def test_verdict_mud_stronger_announcement():
    kind, text = ev.verdict_mud(mud_view(Settings(k=4, s=0, a=2)))
    assert "„mindestens 2“" in text and "Runde 3" in text and "k − a + 1 = 3" in text and "sauber" not in text


def test_verdict_mud_without_announcement_is_info_and_names_the_world_count():
    kind, text = ev.verdict_mud(mud_view(Settings(k=3, s=1, a=0)))
    assert kind == "info" and "16" in text and "2 andere schmutzige" in text


def test_verdict_mud_without_announcement_single_dirty_child():
    kind, text = ev.verdict_mud(mud_view(Settings(k=1, s=1, a=0)))
    assert "Das schmutzige Kind sieht kein anderes schmutziges." in text and "0 andere" not in text


def test_verdict_mud_false_announcement_is_a_warning():
    kind, text = ev.verdict_mud(mud_view(Settings(k=1, s=0, a=2)))
    assert kind == "warning" and "„mindestens 2 schmutzig“" in text and "k = 1" in text


def test_verdict_levels_before_and_after():
    kind, text = ev.verdict_levels(mud_view(Settings(k=3, s=1, a=1)))
    assert kind == "info" and "E^2" in text and "kein gemeinsames Wissen" in text and "Nach der Ansage ist es gemeinsames Wissen" in text
    kind, text = ev.verdict_levels(mud_view(Settings(k=3, s=1, a=0)))
    assert kind == "warning" and "Ohne Ansage bleibt es dabei" in text


def test_verdict_levels_single_dirty_child_has_only_level_zero():
    kind, text = ev.verdict_levels(mud_view(Settings(k=1, s=0, a=1)))
    assert "nur bis E^0" in text


def test_verdict_generals_names_the_counts():
    kind, text = ev.verdict_generals(generals_view(Settings(m=5)))
    assert kind == "success" and "64 Entscheidungsregeln" in text and "ist 1 in allen Welten einig" in text and "keine dieser einigen Regeln greift" in text and "E^5" in text
    kind, text = ev.verdict_generals(generals_view(Settings(m=1)))
    assert "4 Entscheidungsregeln" in text and "E^1" in text


def test_verdict_rule_numbers_for_the_default():
    kind, text = ev.verdict_rule(generals_view(Settings(m=5, c=3, eps=20, b=1)))
    assert "51,2 %" in text and "12,8 %" in text and "0,250" in text and "ε = 0,200" in text


def test_verdict_rule_with_messengers_names_both_losses():
    kind, text = ev.verdict_rule(generals_view(Settings(m=5, c=3, eps=50, b=3)))
    assert "12,5 %" in text and "3 Boten/Nachricht" in text


def test_verdict_rule_beyond_the_chain_says_nobody_attacks():
    kind, text = ev.verdict_rule(generals_view(Settings(m=3, c=4)))
    assert "niemand greift an" in text and "c = 4" in text and "m = 3" in text


def test_experiment_verdicts_count_cells():
    assert "5 von 5" in X.verdict_e1(X.ladder_rows(5))[1]
    assert "5 von 5 Fällen nie ein Kind" in X.verdict_e2(X.silence_rows(5))[1]
    assert "12 von 12 Zellen" in X.verdict_e3(X.rounds_rows(5), 5)[1]
    text4 = X.verdict_e4(X.rules_rows(10))[1]
    assert "4.092" in text4 and "10 sind in allen Welten einig" in text4
    assert "5 von 5 Zeilen" in X.verdict_e6(X.worlds_rows(5), 5)[1]


def test_verdict_e5_non_monotone_branch_and_monotone_branch():
    kind, text = X.verdict_e5(X.messenger_rows(50, 3, 5), 50, 3, 5)
    assert "nicht in jeder Stufe" in text
    kind, text = X.verdict_e5(X.messenger_rows(20, 3, 5), 20, 3, 5)
    assert "sinkt in jeder Stufe" in text and "0,032 %" in text
    kind, text = X.verdict_e5(X.messenger_rows(20, 6, 5), 20, 6, 5)
    assert "niemand greift an" in text


def test_formatting_helpers():
    assert ev.de(0.5123, 3) == "0,512" and ev.pct(0.512) == "51,2 %" and ev.thousands(4092) == "4.092"
