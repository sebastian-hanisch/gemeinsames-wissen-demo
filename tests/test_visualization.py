"""Abbildungen: Achsen fest, richtige Zahl der Spuren, keine Figur im ungültigen Fall."""

import gmw_constants as C
import gmw_generals as G
import gmw_visualization as Z
from gmw_scenario import Settings, generals_view, mud_view


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def test_world_graph_for_four_children_has_sixteen_worlds_and_locked_axes():
    v = mud_view(Settings(k=3, s=1, a=1, stage=0))
    fig = Z.build_world_graph(v)
    assert fig is not None and _locked(fig)
    on = [t for t in fig.data if t.name == "möglich"][0]
    off = [t for t in fig.data if t.name == "ausgeschieden"][0]
    assert len(on.x) == 15 and len(off.x) == 1                              # nach der Ansage fehlt nur die Welt ○○○○


def test_world_graph_shrinks_with_the_stage():
    sizes = []
    for stage in range(0, 5):
        fig = Z.build_world_graph(mud_view(Settings(k=3, s=1, a=1, stage=stage)))
        sizes.append(len([t for t in fig.data if t.name == "möglich"][0].x))
    assert sizes == [15, 11, 5, 1, 1]                                      # nach der Ansage und nach Runde 1, 2, 3; danach unverändert


def test_world_graph_is_not_drawn_for_many_children_or_a_false_announcement():
    assert Z.build_world_graph(mud_view(Settings(k=3, s=2))) is None
    assert Z.build_world_graph(mud_view(Settings(k=1, s=0, a=3))) is None
    assert Z.build_world_counts(mud_view(Settings(k=1, s=0, a=3))) is None


def test_world_counts_bars_sum_to_the_world_numbers():
    v = mud_view(Settings(k=3, s=2, a=1, stage=0))
    fig = Z.build_world_counts(v)
    total, now = fig.data[0].y, fig.data[1].y
    assert sum(total) == 32 and sum(now) == 31 and _locked(fig)


def test_chain_figure_has_one_marker_per_world():
    v = generals_view(Settings(m=4))
    fig = Z.build_chain(v)
    markers = [t for t in fig.data if t.name == "Welt"][0]
    assert len(markers.x) == 6 and _locked(fig)


def test_pareto_figure_contains_all_rules_and_the_front():
    s = Settings(m=5, c=3, eps=20)
    v = generals_view(s)
    pts = G.rule_outcomes(5, s.loss_eff)
    fig = Z.build_pareto(5, s.loss_eff, pts, G.pareto_front(pts), v)
    assert len([t for t in fig.data if t.name.startswith("alle")][0].x) == 64 and _locked(fig)
    assert any(t.name == "gewählte Schwelle c = 3" for t in fig.data)


def test_pareto_without_attack_has_no_selected_point():
    s = Settings(m=3, c=5)
    v = generals_view(s)
    pts = G.rule_outcomes(3, s.loss_eff)
    fig = Z.build_pareto(3, s.loss_eff, pts, G.pareto_front(pts), v)
    assert not any(t.name.startswith("gewählte") for t in fig.data)


def test_graph_constant_matches_the_figure_limit():
    assert C.GRAPH_N_MAX == 4
