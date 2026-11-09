"""Gemeinsames Wissen: Schmutzige Kinder und Zwei Generäle - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 6 der Reihe „Teamrätsel“. Teil A: Kripke-Modell der Schmutzigen Kinder (Welten, Ansage, Runden). Teil B: Zwei Generäle im Kettenmodell
(Sichten, Wissensebenen, Aufzählung aller Entscheidungsregeln, Verlust und Boten). Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import gmw_constants as C
import gmw_evaluation as V
import gmw_experiments as X
import gmw_generals as G
import gmw_visualization as Z
from gmw_layout import dunkles_design, kopf_css
from gmw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from gmw_scenario import Settings, generals_view, mud_view

st.set_page_config(page_title="Gemeinsames Wissen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _mud(settings):
    return mud_view(settings)


@st.cache_data(show_spinner=False)
def _generals(settings):
    return generals_view(settings)


@st.cache_data(show_spinner=False)
def _outcomes(m, eps_eff):
    pts = G.rule_outcomes(m, eps_eff)
    return pts, G.pareto_front(pts)


def show(verdict):
    kind, text = verdict
    getattr(st, kind)(text)


def table(rows):
    """Tabelle ohne Index; alles als Text (Spalten mit Strich und Zahlen mischen sich sonst), None als Strich, Wahrheitswerte als ja/nein."""
    def cell(x):
        if x is None:
            return "—"
        if isinstance(x, bool):
            return "ja" if x else "nein"
        return str(x)
    st.dataframe([{k: cell(v) for k, v in r.items()} for r in rows], hide_index=True, width="stretch")


def run_button(label, key, signature, help_text):
    """▶️-Knopf: merkt sich die Einstellungen, für die gerechnet wurde; das Ergebnis erscheint nur, solange sie gelten."""
    if st.button(label, key=key, help=help_text):
        st.session_state[key + "_sig"] = signature
    return st.session_state.get(key + "_sig") == signature


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in gmw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Gemeinsames Wissen: Schmutzige Kinder und Zwei Generäle")
st.markdown(
    """
Stück 6 der Linie **Teamrätsel** (Arbeitstitel). Zwei Rätsel, ein Gedanke: **„Alle wissen es“ ist nicht „es ist gemeinsames Wissen“.** Bei den **Schmutzigen Kindern** sieht jedes Kind schon vor der Ansage des Vaters,
dass mindestens ein Kind schmutzig ist (ab zwei schmutzigen Kindern), und trotzdem melden sich die Kinder ohne die Ansage nie (gezählt bis 6 Kinder; ohne Ansage bleiben alle Welten möglich) und mit der Ansage „mindestens eines“ nach genau **k Runden** (allgemein bei „mindestens a“ nach k − a + 1 Runden). Bei den **Zwei Generälen** schafft im Kettenmodell keine Folge von
Bestätigungen, was eine einzige öffentliche Ansage schafft. Gerechnet wird mit **Welten und Sichten** (Kripke-Modell) und mit **Aufzählung** aller Entscheidungsregeln; Zahlen sind eigene Rechnung. Wer die Rätsel zuerst ohne Formeln verstehen will, öffnet „💬 In einfachen Worten“.

Abgrenzung: `globale-spiele-demo` rechnet im E-Mail-Spiel (Experiment E6 dort) dieselbe Frage als Spiel mit Auszahlungen und Gleichgewicht; hier gibt es keine
Auszahlungen, dafür die Wissensstruktur selbst und alle Regeln. `endliche-horizonte-demo` nennt gemeinsames Wissen nur als Grenze der Rückwärtsinduktion. Die Kinder und die Generäle sind **Modelle**, keine Aussagen über Menschen.

Weiter unten: **🔬 Experimente E1 bis E6**, **🚧 Wo die Annahmen enden**, die Quellen und der Expander **📐 Mathematische Formulierung**.
"""
)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/schmutzige-kinder-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Zwei Rätsel zeigen: „Alle wissen es“ ist nicht dasselbe wie „es ist gemeinsames Wissen“. Bei den **Schmutzigen Kindern** sieht jedes Kind schon vor der Ansage des Vaters, dass mindestens ein Kind schmutzig ist, sobald mehrere Kinder schmutzig sind. Trotzdem melden sich die Kinder erst nach der Ansage, und zwar in einer Runde, die von der Zahl der schmutzigen Kinder abhängt. Denn erst die laute Ansage macht aus „jeder weiß es“ die ganze Kette „jeder weiß, dass jeder weiß, und so weiter“.

Bei den **Zwei Generälen** können Boten verloren gehen. Die Demo zählt alle Verhaltensregeln durch, die ohne Befehl nicht angreifen: Nur „nie angreifen“ ist in jeder Lage einig. Mehr Boten senken die Uneinigkeit im Verhältnis zum gemeinsamen Angriff, aber nicht auf null. Alles gilt nur für die gewählten Annahmen.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/schmutzige-kinder-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktioniert gemeinsames Wissen", expanded=True):
    st.markdown(
        """
| Begriff | Bedeutung hier |
|---|---|
| **Welt** | eine mögliche Verteilung von „schmutzig“ und „sauber“ auf die Kinder (Teil A) bzw. „so viele Nachrichten sind angekommen“ (Teil B) |
| **Sicht** | die Welten, die ein Kind oder General nicht unterscheiden kann: ein Kind sieht alle anderen, nicht sich selbst |
| **Ansage** | öffentlich gesagt: alle hören sie und wissen, dass alle sie hören; sie schneidet die Weltenmenge ab |
| **E^j** | alle wissen es (E¹), alle wissen, dass alle es wissen (E²), … bis zur Tiefe j |
| **gemeinsames Wissen** | E^j für jedes j, ohne Ende |

1. **Schmutzige Kinder:** Alle antworten gleichzeitig auf „weißt du, ob du schmutzig bist?“ und hören die Antworten aller. Antwortet niemand mit „ja“, scheiden alle Welten aus, in denen jemand es gewusst hätte.
2. **Zwei Generäle:** General A hat den Befehl und schickt eine Nachricht; jede angekommene Nachricht wird bestätigt (die Kette bricht beim ersten Verlust). Jeder entscheidet nur aus dem, was er selbst gesehen hat.
3. **Warum das nicht ausreicht:** Der letzte Absender weiß nie, ob seine Nachricht ankam; die Sichten der beiden Generäle überlappen paarweise und verbinden die Welt „alle Nachrichten angekommen“ mit der Welt „kein Befehl“.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Teil A: Schmutzige Kinder**")
    k = st.slider("Schmutzige Kinder k", *bounds("k_slider"), key="k_slider", help="Wie viele Kinder schmutzig sind. Sie sind die ersten k der Kinder.")
    sc = st.slider("Saubere Kinder", *bounds("s_slider"), key="s_slider", help="Wie viele Kinder sauber sind. Zusammen mit k ergibt das die Zahl n der Kinder (höchstens 10, also 1.024 Welten).")
    a = st.slider("Ansage: mindestens a schmutzig", *bounds("a_slider"), key="a_slider",
                  help="0: der Vater schweigt. 1: „mindestens eines von euch ist schmutzig“. 2 oder 3: stärkere Ansage. Ist a größer als k, wäre die Ansage falsch; das Modell lässt nur wahre Ansagen zu.")
    stage = st.slider("Graph und Zähler nach Runde", *bounds("stage_slider"), key="stage_slider",
                      help="0: nach der Ansage, vor der ersten Antwort. Nach dem Ende des Spiels ändert sich nichts mehr, größere Werte zeigen den Endstand.")
    st.markdown("**Teil B: Zwei Generäle**")
    m = st.slider("Nachrichten m der Kette", *bounds("m_slider"), key="m_slider", help="Höchstens so viele Nachrichten werden gesendet; jede nur, wenn die vorige ankam.")
    c = st.slider("Schwelle c der Angriffsregel", *bounds("c_slider"), key="c_slider",
                  help="Die Generäle greifen an, wenn sie sicher sein können, dass mindestens c−1 bzw. c Nachrichten angekommen sind. Ist c größer als m, wird die Schwelle nie erreicht: niemand greift an.")
    eps = st.slider("Verlust je Bote in %", *bounds("eps_slider"), key="eps_slider", step=5, help="Mit dieser Wahrscheinlichkeit geht ein einzelner Bote verloren, unabhängig von den anderen.")
    b = st.slider("Boten je Nachricht b", *bounds("b_slider"), key="b_slider", help="b Boten tragen dieselbe Nachricht; sie geht nur verloren, wenn alle b verloren gehen (Verlust hoch b).")
    st.markdown("**Zufall**")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt die gezogene Welt im Spiel „Nachricht für Nachricht“ und die Simulation.")
    st.button("🎲 Neuen Zufalls-Seed ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"k_slider": int(k), "s_slider": int(sc), "a_slider": int(a), "stage_slider": int(stage), "m_slider": int(m), "c_slider": int(c),
                   "eps_slider": int(eps), "b_slider": int(b), "seed_input": int(seed)})

settings = Settings(int(k), int(sc), int(a), int(stage), int(m), int(c), int(eps), int(b), int(seed))
mv = _mud(settings)
gv = _generals(settings)
verdicts = []   # Verdikte für den PDF-Export

# ============================================================================================================================================
# Teil A
# ============================================================================================================================================
st.markdown("## 🧒 Teil A: Schmutzige Kinder")
st.caption(f"{settings.n} Kinder, davon {settings.k} schmutzig. Jedes Kind sieht die Stirn aller anderen, nicht die eigene. Der Vater sagt (oder sagt nicht), dann fragt er in jeder Runde alle gleichzeitig, ob sie wissen, ob sie schmutzig sind.")
if mv.valid and mv.play is not None:
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Welten nach der Ansage", V.thousands(mv.sizes[0]), delta=f"von {V.thousands(1 << settings.n)}", delta_color="off", delta_arrow="off")
    dirty_round = mv.first[0]
    clean_round = mv.first[settings.k] if settings.s else None
    a2.metric("Schmutzige: Runde", "nie" if dirty_round is None else str(dirty_round), delta="Rundenformel k − a + 1: " + ("—" if settings.a < 1 else str(V.rounds_formula(settings.k, settings.a))), delta_color="off", delta_arrow="off")
    a3.metric("Saubere: Runde", "—" if not settings.s else ("nie" if clean_round is None else str(clean_round)), delta_color="off")
    a4.metric("Wissenstiefe vor der Ansage", f"E^{mv.level_before}", delta="gemeinsames Wissen: " + ("ja" if mv.common_before else "nein"), delta_color="off", delta_arrow="off")
    st.markdown("**Wer weiß in welcher Runde was?**")
    table(V.mud_rows(mv))
    graph = Z.build_world_graph(mv)
    if graph is not None:
        st.markdown(f"**Welten nach {min(settings.stage, len(mv.play.rounds))} Runden** (Farbe der Kanten: welches Kind die beiden Welten nicht unterscheidet)")
        st.plotly_chart(graph, width="stretch", key="mud_graph")
    counts = Z.build_world_counts(mv)
    if counts is not None:
        st.markdown(f"**Zahl der noch möglichen Welten nach {min(settings.stage, len(mv.play.rounds))} Runden, nach Zahl der schmutzigen Kinder**")
        st.plotly_chart(counts, width="stretch", key="mud_counts")
        if settings.n > C.GRAPH_N_MAX:
            st.caption(f"Der Weltengraph wird nur bis {C.GRAPH_N_MAX} Kinder gezeichnet (16 Welten); darüber zeigt das Balkendiagramm die Weltenmenge.")
else:
    st.warning(V.verdict_mud(mv)[1])

st.markdown("### ❓ Kernfrage A: Warum reden die Kinder erst in Runde k − a + 1?")
show(V.verdict_mud(mv))
verdicts.append(V.verdict_mud(mv))
show(V.verdict_levels(mv))
verdicts.append(V.verdict_levels(mv))

st.markdown("---")

# ============================================================================================================================================
# Teil B
# ============================================================================================================================================
st.markdown("## ⚔️ Teil B: Zwei Generäle")
st.caption("General A will mit B gemeinsam angreifen. Jeder Bote kann verloren gehen. Jede angekommene Nachricht wird bestätigt; die Kette bricht beim ersten Verlust. Jeder General greift nur nach einer Regel an, die von dem abhängt, was er selbst gesehen hat.")
st.plotly_chart(Z.build_chain(gv), width="stretch", key="chain_chart")
st.caption("Oben (grün): Welten, die A nicht unterscheiden kann; unten (braun): die von B. Die Kette verbindet „alle Nachrichten angekommen“ mit „kein Befehl“. Darunter: bis zu welcher Ebene E^j alle wissen, dass ein Befehl vorliegt.")
with st.expander("Wissensebenen und Sichten als Tabelle"):
    table(V.level_table(settings.m))
    st.caption(f"A hat {len(gv.views_a)} Sichten, B hat {len(gv.views_b)} Sichten.")

b1, b2, b3, b4 = st.columns(4)
b1.metric("Gültige Regeln", V.thousands(gv.summary.valid), delta="ohne Befehl kein Angriff", delta_color="off", delta_arrow="off")
b2.metric("davon einig in allen Welten", str(gv.summary.agree), delta="nie angreifen", delta_color="off", delta_arrow="off")
b3.metric("davon mit Angriff", str(gv.summary.agree_and_attack), delta="bei allen m angekommen", delta_color="off", delta_arrow="off")
b4.metric("Verlust je Nachricht", V.pct(settings.loss_eff, 2), delta=f"{settings.b} Bote{'n' if settings.b > 1 else ''} je Nachricht", delta_color="off", delta_arrow="off")
st.markdown("### ❓ Kernfrage B: Kann irgendeine Regel Einigkeit und Angriff zugleich liefern?")
show(V.verdict_generals(gv))
verdicts.append(V.verdict_generals(gv))

st.markdown("**Schwellenregel und Verlust**")
st.caption("Bei Verlust ε < 1 ist Einigkeit nur mit der Regel „nie angreifen“ garantiert. Wer angreifen will, nimmt eine Uneinigkeit in Kauf: jeder Punkt ist eine der Regeln.")
pts, front = _outcomes(settings.m, settings.loss_eff)
st.plotly_chart(Z.build_pareto(settings.m, settings.loss_eff, pts, front, gv), width="stretch", key="pareto_chart")
show(V.verdict_rule(gv))
verdicts.append(V.verdict_rule(gv))

st.markdown("**Ein Spiel Nachricht für Nachricht** (Zufalls-Seed der Seitenleiste)")
sw = gv.simulated_world
if sw == settings.m:
    path = f"alle {settings.m} Nachrichten kommen an"
else:
    path = f"{sw} Nachricht{'en' if sw != 1 else ''} kommen an, Nachricht {sw + 1} geht verloren"
words = {"beide": "beide Generäle greifen an", "einer": "nur ein General greift an: Uneinigkeit", "keiner": "keiner greift an"}
st.info(f"Gezogene Welt: {path}. Mit Schwelle c = {settings.c}: {words[gv.simulated_outcome]}.")
sim_sig = (settings.m, settings.c, settings.loss_eff, settings.seed)
if run_button("▶️ Formel gegen Simulation rechnen", "sim_button", sim_sig, f"Spielt {V.thousands(C.GAMES)} Ketten Nachricht für Nachricht; rechnet unter einer Sekunde."):
    with st.spinner("Spiele die Ketten …"):
        sim = X.simulation_rows(settings.m, settings.c, settings.loss_eff, C.GAMES, settings.seed)
    table([{"Ausgang": r["Ausgang"], "Formel": V.pct(r["Formel"], 2), "simuliert": V.pct(r["simuliert"], 2), "Standardfehler": V.pct(r["Standardfehler"], 2)} for r in sim])
    show(X.verdict_simulation(sim, C.GAMES))

st.markdown("---")

# ============================================================================================================================================
# Experimente
# ============================================================================================================================================
st.subheader("🔬 Experiment E1: Alle wissen es – und trotzdem schweigen sie")
st.caption(f"Alle k = 1 bis n bei n = {settings.n} Kindern, Ansage „mindestens eines“. Die Tiefe der Wissensleiter kommt aus dem Kripke-Modell, nicht aus einer Formel.")
if run_button("▶️ E1 rechnen", "e1_button", (settings.n,), "Rechnet das Kripke-Modell für alle k bei der gewählten Kinderzahl."):
    rows = X.ladder_rows(settings.n)
    table(rows)
    show(X.verdict_e1(rows))
    verdicts.append(X.verdict_e1(rows))

st.subheader("🔬 Experiment E2: Ohne Ansage schweigen alle")
st.caption(f"Erste Meldung der schmutzigen Kinder bei n = {settings.n}: mit Ansage und ohne. Ohne Ansage bleiben alle Welten möglich, daher meldet sich in dieser Rechnung kein Kind; getestet ist das für n bis 6.")
if run_button("▶️ E2 rechnen", "e2_button", (settings.n,), "Spielt für alle k das Spiel mit und ohne Ansage."):
    rows = X.silence_rows(settings.n)
    table(rows)
    show(X.verdict_e2(rows))
    verdicts.append(X.verdict_e2(rows))

st.subheader("🔬 Experiment E3: Runde gegen k und a")
st.caption(f"Runde der ersten Meldung bei n = {settings.n} Kindern für die Ansagen „mindestens 1, 2, 3“. Leer: die Ansage wäre falsch.")
if run_button("▶️ E3 rechnen", "e3_button", (settings.n,), "Spielt alle Kombinationen aus a und k."):
    rows = X.rounds_rows(settings.n)
    table(rows)
    show(X.verdict_e3(rows, settings.n))
    verdicts.append(X.verdict_e3(rows, settings.n))

st.subheader("🔬 Experiment E4: Keine Regel genügt")
st.caption("Alle Entscheidungsregeln der Kette für m = 1 bis 10 aufgezählt (ohne Befehl kein Angriff): wie viele sind einig, wie viele greifen an?")
if run_button("▶️ E4 rechnen", "e4_button", (), f"Zählt für m = 1 bis {C.ENUM_M_MAX} alle Regeln auf (bis zu 2.048 gültige Regeln)."):
    with st.spinner("Zähle alle Regeln …"):
        rows = X.rules_rows(C.ENUM_M_MAX)
    table(rows)
    show(X.verdict_e4(rows))
    verdicts.append(X.verdict_e4(rows))

st.subheader("🔬 Experiment E5: Boten statt Nachrichten")
st.caption(f"Verlust {settings.eps} % je Bote, Schwelle c = {settings.c}, m = {settings.m}: mehr Boten je Nachricht senken das Verhältnis Uneinigkeit zu Angriff, aber nie auf null.")
if run_button("▶️ E5 rechnen", "e5_button", (settings.eps, settings.c, settings.m), "Rechnet b = 1 bis 5 Boten je Nachricht."):
    rows = X.messenger_rows(settings.eps, settings.c, settings.m)
    table([{"Boten b": r["Boten b"], "Verlust je Nachricht": V.pct(r["Verlust je Nachricht"], 3), "beide greifen an": V.pct(r["beide greifen an"], 2),
            "genau einer greift an": V.pct(r["genau einer greift an"], 3), "Verhältnis": "—" if r["Verhältnis"] is None else V.de(r["Verhältnis"], 4)} for r in rows])
    show(X.verdict_e5(rows, settings.eps, settings.c, settings.m))
    verdicts.append(X.verdict_e5(rows, settings.eps, settings.c, settings.m))

st.subheader("🔬 Experiment E6: Weltenzahl nach s stillen Runden")
st.caption(f"Alle n = {settings.n} Kinder schmutzig, Ansage „mindestens eines“: wie viele Welten bleiben nach r Runden ohne „ja“? Gegenprobe: Summe der Binomialkoeffizienten.")
if run_button("▶️ E6 rechnen", "e6_button", (settings.n,), "Spielt das Spiel mit n schmutzigen Kindern und zählt die Welten je Runde."):
    rows = X.worlds_rows(settings.n)
    table(rows)
    show(X.verdict_e6(rows, settings.n))
    verdicts.append(X.verdict_e6(rows, settings.n))

st.markdown("---")

st.subheader("📄 Ergebnisse als PDF")
if st.button("PDF erstellen", key="pdf_button"):
    from gmw_pdf_export import build_pdf
    st.session_state["pdf_bytes"] = build_pdf(settings, verdicts)
if st.session_state.get("pdf_bytes"):
    st.download_button("⬇️ PDF herunterladen", st.session_state["pdf_bytes"], file_name="gemeinsames-wissen.pdf", mime="application/pdf", key="pdf_download")

st.markdown("---")

# ============================================================================================================================================
# Annahmen, Grenzen, Mathematik, Quellen
# ============================================================================================================================================
st.subheader("🚧 Wo die Annahmen enden")
ASSUMPTIONS_MARKDOWN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Jedes Kind sieht alle anderen** (vollständige Sicht) | Sieht ein Kind nur manche, bilden die Welten einen anderen Graphen; die Rundenformel k − a + 1 gilt dann nicht mehr. Nicht gerechnet. | — |
| **Alle Kinder sind ehrlich, schlussfolgern fehlerfrei und wissen das voneinander** | Das ist selbst gemeinsames Wissen. Ist ein Kind nicht fehlerfrei, kippt die Kette der Schlüsse; nicht gerechnet. | — |
| **Der Vater sagt nur Wahres** | Eine falsche Ansage (a > k) lässt das Modell nicht zu; die Demo meldet es. | — |
| **Kettenmodell der Generäle**: Nachricht i wird nur gesendet, wenn Nachricht i − 1 ankam | Andere Kommunikationsmuster (parallele Boten ohne Bestätigung, Zeitschranken, Wiederholungen) sind nicht gerechnet. | — |
| **Verlust unabhängig und gleich groß** (feste Wahrscheinlichkeit je Bote) | Bei gegnerischem Verlust (ein Feind fängt gezielt ab) gelten die Verlustzahlen nicht; die Aufzählung, dass keine Regel Einigkeit und Angriff zugleich liefert, zählt Welten und nicht Wahrscheinlichkeiten und gilt weiter. | — |
| **Regeln hängen nur von der eigenen Sicht ab, ohne Zufall** | Mischungen aus diesen Regeln haben ein Verhältnis Uneinigkeit zu Angriff, das nicht unter dem kleinsten liegt; Zufall mit geteiltem Münzwurf ist nicht gerechnet. | — |
| **Keine Auszahlungen**, nur Wissen | Ob ein Betrieb bei Verlustrisiko angreift, ist eine Gleichgewichtsfrage: Sie steht im E-Mail-Spiel von `globale-spiele-demo` (E6). | `globale-spiele-demo` |
| **Kein Reden vor dem Spiel**, keine Strategiewahl | Kostenlose Nachrichten vor Koordinationsspielen sind das Thema des Koordinationsspiele-Stücks `vorabsignale-demo` (bisher nur als Plan). | `vorabsignale-demo` (bisher nur als Plan) |
"""
st.markdown(ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/schmutzige-kinder-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Teil A: Gegeben sind $n$ Kinder, davon $k$ schmutzig, die jeweils alle anderen sehen, und die öffentliche Ansage „mindestens $a$ schmutzig“. Gesucht ist, wie tief das Wissen vor der Ansage reicht und in welcher Runde $r$ sich die schmutzigen Kinder melden. Teil B: Gegeben ist eine Kette von höchstens $m$ Nachrichten, die mit Wahrscheinlichkeit $\varepsilon$ verloren gehen. Gesucht ist eine Regel, bei der beide Generäle zugleich angreifen. In der Tabelle bezeichnet jeder Buchstabe nur eines.

| Symbol | Bedeutung |
|---|---|
| $w \in \{0, 1\}^n$, $\lvert w \rvert$ | Welt: Bitvektor über die $n$ Kinder (1 = schmutzig), $\lvert w \rvert$ ist die Zahl der schmutzigen Kinder |
| $k$ | Zahl der schmutzigen Kinder in der wirklichen Welt |
| $w \oplus e_i$ | die Welt $w$ mit gekipptem Bit $i$; Kind $i$ unterscheidet beide Welten nicht |
| $a$, $W_a$ | Ansage „mindestens $a$“ und die Menge der Welten mit mindestens $a$ schmutzigen Kindern |
| $K_i$, $E^j$, $C$ | Kind $i$ weiß; alle wissen, $j$-fach ineinandergesetzt; gemeinsames Wissen |
| $r$ | Runde, in der sich die schmutzigen Kinder melden |
| $s$, $q$, $\binom{n}{q}$ | Zahl stiller Runden; Laufzahl der Summe über die Zahl schmutziger Kinder; Zahl der Welten mit $q$ schmutzigen Kindern |
| $m$, $c$, $t$ | höchste Zahl der Nachrichten, Schwelle der Angriffsregel und Weltnummer der Generäle (die ersten $t$ Nachrichten kamen an) |
| $\varepsilon$, $b$ | Verlustwahrscheinlichkeit einer Nachricht (bei $b$ Boten je Nachricht $\varepsilon^b$) und Zahl der Boten |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/schmutzige-kinder-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Schmutzige Kinder.** Eine Welt ist $w \in \{0,1\}^n$ ($w_i = 1$: Kind $i$ schmutzig), $|w|$ die Zahl der schmutzigen Kinder. Kind $i$ unterscheidet $w$ nicht von $w \oplus e_i$:

$$ w \sim_i w \oplus e_i $$

Die Ansage „mindestens $a$“ schneidet die Weltenmenge auf

$$ W_a = \{ w : |w| \ge a \} $$

Kind $i$ weiß seinen Zustand in $w$ genau dann, wenn die Nachbarwelt nicht mehr möglich ist:

$$ K_i\text{(Zustand)} \iff w \oplus e_i \notin W $$

Nach einer Runde ohne „ja“ bleiben nur Welten, in denen niemand es gewusst hätte. Alle Antworten sind öffentlich; so entsteht aus Schweigen Wissen.

**Wissensleiter.** Mit $E\varphi = \bigwedge_i K_i \varphi$ gilt $E^j\varphi$ in $w$ genau dann, wenn $\varphi$ in allen Welten im Abstand höchstens $j$ von $w$ gilt. Für $\varphi$ = „mindestens $a$ schmutzig“ in der Welt mit $k$ schmutzigen Kindern ist das

$$ E^j \varphi \iff j \le k - a $$

Gemeinsames Wissen $C\varphi$ in $w$ heißt: $\varphi$ gilt in der ganzen von $w$ aus erreichbaren Komponente. Vor der Ansage enthält sie die Welt $w = 0$, in der $\varphi$ falsch ist.

**Rundenzahl.** Die schmutzigen Kinder wissen es in Runde

$$ r = k - a + 1 $$

und die sauberen Kinder in Runde $r + 1$ (Kripke-Modell gegen diese Formel geprüft; $a \ge 1$). Nach $s$ stillen Runden (alle $n$ Kinder schmutzig, $a = 1$) sind noch

$$ \sum_{q > s} \binom{n}{q} $$

Welten möglich, wobei $s$ die Zahl der stillen Runden ist und $q$ die Laufzahl der Summe (Zahl schmutziger Kinder in einer Welt). So bezeichnet $k$ nur die Zahl der schmutzigen Kinder, $j$ nur die Tiefe von $E^j$ und $r$ nur die Runde der Meldung.

**Zwei Generäle.** Welt $t \in \{0, \dots, m\}$: die ersten $t$ Nachrichten kamen an; Welt NO: kein Befehl. $A$ unterscheidet $t$ und $t+1$ für gerades $t$ nicht, $B$ für ungerades $t$; außerdem kann $B$ die Welten NO und $0$ nicht unterscheiden. Beide zusammen haben $m + 3$ Sichten. Bei Verlust $\varepsilon$ je Nachricht:

$$ P(t) = (1-\varepsilon)^t \varepsilon \quad (t < m), \qquad P(m) = (1-\varepsilon)^m $$

Die Schwellenregel $c$ ($1 \le c \le m$) liefert

$$ P(\text{beide greifen an}) = (1-\varepsilon)^c, \qquad P(\text{genau einer greift an}) = \varepsilon (1-\varepsilon)^{c-1} $$

Das Verhältnis beider ist $\varepsilon/(1-\varepsilon)$, unabhängig von $c$ und $m$. Tragen $b$ Boten dieselbe Nachricht, ersetzt $\varepsilon^b$ den Verlust $\varepsilon$.

**Quellen** (Abstract bzw. Einleitung, Websuche 2026-11-08, nicht im Volltext gelesen). Aumann (1976), „Agreeing to Disagree“, *Annals of Statistics* 4(6), 1236–1239: Definition gemeinsamen Wissens als unendliche Kette (jeder weiß, jeder weiß, dass der andere es weiß, …).
Halpern und Moses (1990), „Knowledge and Common Knowledge in a Distributed Environment“, *Journal of the ACM* 37(3), 549–587: ein korrektes Protokoll für den koordinierten Angriff greift nur an, wenn der Angriff gemeinsames Wissen ist; bei nicht garantierter Kommunikation ist gemeinsames Wissen unerreichbar.
Rubinstein (1989), „The Electronic Mail Game“, *American Economic Review* 79(3): nur als Verweis auf `globale-spiele-demo`, hier nicht nachgelesen. Die Rätsel selbst sind Sammlungswissen; die Zählungen und Zahlen dieser Demo sind eigene Rechnung.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Teamrätsel: Strategie ohne Verständigung](https://sebastianhanisch.net/konzepte-teamraetsel.html)."
)
