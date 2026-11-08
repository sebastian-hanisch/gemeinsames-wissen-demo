"""Plotly-Figuren: alle Achsen fest (fixedrange), Beschriftungen als Annotationen."""

from __future__ import annotations

from math import comb

import plotly.graph_objects as go

import gmw_algorithm as A
import gmw_constants as C
import gmw_generals as G
from gmw_scenario import GeneralsView, MudView

CHILD_COLORS = ["#4c78a8", "#e45756", "#54a24b", "#b279a2"]


def _axes(fig, xrange, yrange, xtitle=None, ytitle=None, ticks=True):
    fig.update_xaxes(range=xrange, fixedrange=True, title=xtitle, showgrid=False, zeroline=False, showticklabels=ticks)
    fig.update_yaxes(range=yrange, fixedrange=True, title=ytitle, showgrid=False, zeroline=False, showticklabels=ticks)


def _label(w: int, n: int) -> str:
    """Bitmuster der Welt: ● schmutzig, ○ sauber, Kind 1 links."""
    return "".join("●" if (w >> i) & 1 else "○" for i in range(n))


def world_positions(n: int) -> dict[int, tuple[float, float]]:
    """Welten nach Zahl der schmutzigen Kinder in Zeilen; innerhalb der Zeile gleichmäßig verteilt."""
    rows: dict[int, list[int]] = {}
    for w in range(1 << n):
        rows.setdefault(A.popcount(w), []).append(w)
    pos = {}
    for j, ws in rows.items():
        ws.sort()
        for idx, w in enumerate(ws):
            pos[w] = (idx - (len(ws) - 1) / 2.0, float(j))
    return pos


def build_world_graph(v: MudView) -> go.Figure | None:
    """Hyperwürfel der Welten (nur bis GRAPH_N_MAX Kinder): möglich = farbig, ausgeschieden = grau, wirkliche Welt umrandet; Kanten nach Kind gefärbt."""
    s = v.settings
    n = s.n
    if n > C.GRAPH_N_MAX or not v.valid or v.play is None:
        return None
    alive = A.worlds_after(v.play, s.stage)
    pos = world_positions(n)
    fig = go.Figure()
    for i in range(n):
        xs, ys = [], []
        for w in range(1 << n):
            u = w ^ (1 << i)
            if w < u:
                on = w in alive and u in alive
                if on:
                    xs += [pos[w][0], pos[u][0], None]
                    ys += [pos[w][1], pos[u][1], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=CHILD_COLORS[i], width=2.5), name=f"Kind {i + 1} kann nicht unterscheiden", hoverinfo="skip"))
    xs_off, ys_off, xs_on, ys_on, texts_on, texts_off = [], [], [], [], [], []
    for w in range(1 << n):
        x, y = pos[w]
        (xs_on if w in alive else xs_off).append(x)
        (ys_on if w in alive else ys_off).append(y)
        (texts_on if w in alive else texts_off).append(_label(w, n))
    fig.add_trace(go.Scatter(x=xs_off, y=ys_off, mode="markers+text", text=texts_off, textposition="bottom center", textfont=dict(color="rgba(150,150,150,0.8)", size=11),
                             marker=dict(size=18, color=C.COLOR_OFF), name="ausgeschieden", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs_on, y=ys_on, mode="markers+text", text=texts_on, textposition="bottom center", textfont=dict(size=12),
                             marker=dict(size=18, color=C.COLOR_DIRTY), name="möglich", hoverinfo="skip"))
    aw = v.play.actual
    fig.add_trace(go.Scatter(x=[pos[aw][0]], y=[pos[aw][1]], mode="markers", marker=dict(size=30, color="rgba(0,0,0,0)", line=dict(color="#222222", width=3)),
                             name="wirkliche Welt", hoverinfo="skip"))
    fig.update_layout(height=430, margin=dict(l=70, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.02), showlegend=True)
    _axes(fig, [-3.2, 3.2], [-0.6, n + 0.5], ticks=False)
    for j in range(n + 1):
        fig.add_annotation(x=-3.15, y=j, text=f"{j} schmutzig", showarrow=False, xanchor="left", font=dict(size=11))
    return fig


def build_world_counts(v: MudView) -> go.Figure | None:
    """Balken je Zahl j schmutziger Kinder: alle Welten (hell) und die nach `stage` Runden noch möglichen (dunkel)."""
    if not v.valid or v.play is None:
        return None
    s = v.settings
    n = s.n
    alive = A.worlds_after(v.play, s.stage)
    total = [comb(n, j) for j in range(n + 1)]
    now = [sum(1 for w in alive if A.popcount(w) == j) for j in range(n + 1)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(n + 1)), y=total, name="alle Welten", marker_color=C.COLOR_OFF))
    fig.add_trace(go.Bar(x=list(range(n + 1)), y=now, name="noch möglich", marker_color=C.COLOR_DIRTY))
    ymax = max(total) * 1.15
    fig.update_layout(barmode="overlay", height=300, margin=dict(l=50, r=10, t=10, b=40), legend=dict(orientation="h", y=1.12))
    _axes(fig, [-0.6, n + 0.6], [0, ymax], xtitle="Zahl der schmutzigen Kinder in der Welt", ytitle="Welten")
    fig.update_xaxes(tickmode="linear", dtick=1)
    return fig


def build_chain(v: GeneralsView) -> go.Figure:
    """Die Kette der Welten NO, 0, ..., m. Linien über der Kette: Welten, die A nicht unterscheidet; unter der Kette: B. Angegeben ist die Wissensebene E^j."""
    s = v.settings
    m = s.m
    ws = G.worlds(m)
    xs = {w: float(w + 1) for w in ws}  # NO bei 0
    fig = go.Figure()
    for who, color, ypos in (("A", C.COLOR_A, 0.28), ("B", C.COLOR_B, -0.28)):
        fx, fy = [], []
        for view in (v.views_a if who == "A" else v.views_b):
            if len(view) > 1:
                lo, hi = min(view), max(view)
                fx += [xs[lo], xs[hi], None]
                fy += [ypos, ypos, None]
        fig.add_trace(go.Scatter(x=fx, y=fy, mode="lines", line=dict(color=color, width=7), opacity=0.55, name=f"General {who} unterscheidet die Welten nicht", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[xs[w] for w in ws], y=[0.0] * len(ws), mode="markers", marker=dict(size=22, color=[C.COLOR_OFF if w == G.NO else C.COLOR_LINE for w in ws]),
                             name="Welt", hoverinfo="skip"))
    sw = v.simulated_world
    fig.add_trace(go.Scatter(x=[xs[sw]], y=[0.0], mode="markers", marker=dict(size=34, color="rgba(0,0,0,0)", line=dict(color="#222222", width=3)), name="gezogene Welt", hoverinfo="skip"))
    for w, lv in zip(ws, v.levels):
        fig.add_annotation(x=xs[w], y=0.0, text="kein<br>Befehl" if w == G.NO else str(w), showarrow=False, font=dict(size=10, color="white"))
        fig.add_annotation(x=xs[w], y=-0.62, text="—" if lv == -1 else f"E^{lv}", showarrow=False, font=dict(size=12))
    fig.add_annotation(x=-0.6, y=-0.62, text="Wissen:", showarrow=False, xanchor="right", font=dict(size=12))
    fig.add_annotation(x=-0.6, y=0.0, text="angekommene Nachrichten:", showarrow=False, xanchor="right", font=dict(size=11))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.18))
    _axes(fig, [-3.6, m + 1.6], [-0.9, 0.7], ticks=False)
    return fig


def build_pareto(m: int, eps: float, points, front, v: GeneralsView) -> go.Figure:
    """Jede gültige Regel als Punkt (P(beide greifen an), P(genau einer greift an)); die Gerade ε/(1−ε) und die gewählte Schwellenregel."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=7, color=C.COLOR_OFF), name=f"alle {len(points)} gültigen Regeln", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[p[0] for p in front], y=[p[1] for p in front], mode="lines+markers", line=dict(color=C.COLOR_LINE, width=2), marker=dict(size=9, color=C.COLOR_LINE),
                             name="beste Regeln (Pareto)", hoverinfo="skip"))
    slope = eps / (1.0 - eps) if eps < 1 else 0.0
    ymax = max(0.05, max(ys + [slope]) * 1.1)
    x_end = min(1.0, ymax / slope) if slope > 0 else 1.0
    fig.add_trace(go.Scatter(x=[0, x_end], y=[0, slope * x_end], mode="lines", line=dict(color="#999999", dash="dash"), name="Uneinigkeit = ε/(1−ε) · Angriff", hoverinfo="skip"))
    if v.both > 0:
        fig.add_trace(go.Scatter(x=[v.both], y=[v.disagree], mode="markers", marker=dict(size=15, color=C.COLOR_DIRTY, symbol="diamond"), name=f"gewählte Schwelle c = {v.settings.c}", hoverinfo="skip"))
    fig.update_layout(height=340, margin=dict(l=60, r=10, t=10, b=50), legend=dict(orientation="h", y=1.2))
    _axes(fig, [-0.02, 1.02], [-0.01, ymax], xtitle="P(beide greifen an)", ytitle="P(genau einer greift an)")
    return fig
