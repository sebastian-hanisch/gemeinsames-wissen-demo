"""Szenario: Einstellungen und die beiden Sichten (Schmutzige Kinder, Zwei Generäle), zusammengesetzt aus den Einheiten des Kerns."""

from __future__ import annotations

from dataclasses import dataclass

import gmw_algorithm as A
import gmw_constants as C
import gmw_generals as G
from gmw_rng import SplitMix64


@dataclass(frozen=True)
class Settings:
    k: int = C.DEFAULT_K
    s: int = C.DEFAULT_S
    a: int = C.DEFAULT_A
    stage: int = C.DEFAULT_STAGE
    m: int = C.DEFAULT_M
    c: int = C.DEFAULT_C
    eps: int = C.DEFAULT_EPS          # Prozent
    b: int = C.DEFAULT_B
    seed: int = C.DEFAULT_SEED

    @property
    def n(self) -> int:
        return self.k + self.s

    @property
    def loss(self) -> float:
        return self.eps / 100.0

    @property
    def loss_eff(self) -> float:
        return G.effective_loss(self.loss, self.b)


@dataclass(frozen=True)
class MudView:
    settings: Settings
    valid: bool                       # False: die Ansage „mindestens a“ wäre bei k schmutzigen Kindern falsch
    play: A.Play | None
    first: tuple                      # erste Wissensrunde je Kind (None: nie)
    sizes: tuple                      # Zahl der möglichen Welten: nach der Ansage, nach Runde 1, ...
    ladder_a: int                     # Stärke der Tatsache der Wissensleiter: max(a, 1)
    level_before: int | None          # größtes j mit E^j (mindestens ladder_a) vor der Ansage
    common_before: bool               # gemeinsames Wissen dieser Tatsache vor der Ansage
    common_after: bool                # nach der Ansage


def mud_view(s: Settings) -> MudView:
    n, a_eff = s.n, max(s.a, 1)
    full = A.all_worlds(n)
    fact = A.fact_at_least(full, a_eff)
    w = A.actual_world(s.k)
    level = A.knowledge_level(full, n, fact, w)
    cb = A.is_common_knowledge(full, n, fact, w)
    if s.k < s.a:
        return MudView(s, False, None, (), (), a_eff, level, cb, False)
    p = A.play(n, w, s.a)
    sizes = (len(p.start),) + tuple(len(r.after) for r in p.rounds)
    start_fact = A.fact_at_least(p.start, a_eff)
    ca = A.is_common_knowledge(p.start, n, start_fact, w)
    return MudView(s, True, p, tuple(A.first_known(p)), sizes, a_eff, level, cb, ca)


@dataclass(frozen=True)
class GeneralsView:
    settings: Settings
    levels: tuple                     # Wissensebene über „Befehl liegt vor“ in den Welten NO, 0, ..., m
    views_a: tuple
    views_b: tuple
    summary: G.RuleSummary
    both: float                       # P(beide greifen an) der Schwellenregel (0 bei c > m)
    disagree: float
    simulated_world: int
    simulated_outcome: str
    rule: dict


def generals_view(s: Settings) -> GeneralsView:
    m = s.m
    levels = tuple(G.knowledge_level(m, w) for w in G.worlds(m))
    if s.c <= m:
        both, dis = G.threshold_probs(s.loss_eff, s.c)
    else:
        both, dis = 0.0, 0.0
    world = G.draw_world(m, s.loss_eff, SplitMix64(s.seed))
    outcome = G.outcome(m, s.c, world)
    return GeneralsView(s, levels, tuple(G.views(m, "A")), tuple(G.views(m, "B")), G.enumerate_rules(m), both, dis, world, outcome,
                        G.threshold_rule(m, s.c))
