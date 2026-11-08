"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


# ---------------------------------------------------------------- Eigene Prüfungen dieser Demo
import pytest  # noqa: E402

import gmw_constants as C  # noqa: E402

RUN_BUTTONS = ["▶️ Formel gegen Simulation rechnen"] + [f"▶️ E{i} rechnen" for i in range(1, 7)]


def _texts(at):
    return " ".join([w.value for w in at.warning] + [s.value for s in at.success] + [i.value for i in at.info] + [e.value for e in at.error])


def _click(at, label):
    next(b for b in at.button if b.label == label).click().run(timeout=TIMEOUT)


def test_default_shows_the_rounds_of_the_standard_preset():
    at = _fresh_app()
    text = _texts(at)
    assert "die 3 schmutzigen Kinder in Runde 3" in text and "das saubere Kind in Runde 4" in text
    assert "64 Entscheidungsregeln" in text and "51,2 %" in text


@pytest.mark.parametrize("label", RUN_BUTTONS)
def test_each_run_button_alone_produces_a_verdict(label):
    at = _fresh_app()
    before = len(at.success) + len(at.info)
    _click(at, label)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.success) + len(at.info) > before, label


def test_run_buttons_show_their_results_only_for_the_settings_they_ran_with():
    at = _fresh_app()
    _click(at, "▶️ E3 rechnen")
    assert any("Zellen mit k ≥ a" in s.value for s in at.success)
    at.sidebar.slider(key="s_slider").set_value(0).run(timeout=TIMEOUT)
    assert not any("Zellen mit k ≥ a" in s.value for s in at.success)       # andere Kinderzahl: das alte Ergebnis wird nicht gezeigt


def test_e4_counts_all_rules_for_m_1_to_10():
    at = _fresh_app()
    _click(at, "▶️ E4 rechnen")
    assert any("4.092" in s.value for s in at.success)


def test_pdf_can_be_created_and_downloaded():
    at = _fresh_app()
    _click(at, "PDF erstellen")
    assert not at.exception
    assert isinstance(at.session_state["pdf_bytes"], bytes) and at.session_state["pdf_bytes"][:5] == b"%PDF-"


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_each_preset_sets_its_values_and_runs(name):
    at = _fresh_app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    from gmw_presets import PRESET_KEYS
    for key, state_key in PRESET_KEYS.items():
        assert at.session_state[state_key] == C.PRESETS[name][key], (name, key)


def test_false_announcement_shows_a_warning_and_no_world_graph():
    at = _fresh_app()
    at.sidebar.slider(key="k_slider").set_value(1).run(timeout=TIMEOUT)
    at.sidebar.slider(key="a_slider").set_value(3).run(timeout=TIMEOUT)
    assert not at.exception
    assert any("wäre bei k = 1 schmutzigen Kindern falsch" in w.value for w in at.warning)


def test_no_announcement_shows_the_info_that_nobody_ever_knows():
    at = _fresh_app()
    at.sidebar.slider(key="a_slider").set_value(0).run(timeout=TIMEOUT)
    assert any("weiß in keiner Runde ein Kind etwas" in i.value for i in at.info)


def test_permalink_is_clamped_to_the_slider_bounds():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.query_params["k"] = "99"
    at.query_params["m"] = "7"
    at.query_params["eps"] = "-4"
    at.run()
    assert not at.exception
    assert at.sidebar.slider(key="k_slider").value == C.K_MAX
    assert at.sidebar.slider(key="m_slider").value == 7
    assert at.sidebar.slider(key="eps_slider").value == C.EPS_MIN


def test_many_children_use_the_bars_instead_of_the_graph():
    at = _fresh_app()
    at.sidebar.slider(key="s_slider").set_value(3).run(timeout=TIMEOUT)
    assert not at.exception
    assert any("Der Weltengraph wird nur bis 4 Kinder gezeichnet" in c.value for c in at.caption)


def test_all_sliders_at_their_maxima_together():
    at = _fresh_app()
    for state_key in ("k_slider", "s_slider", "a_slider", "stage_slider", "m_slider", "c_slider", "eps_slider", "b_slider"):
        at.sidebar.slider(key=state_key).set_value(at.sidebar.slider(key=state_key).max)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]


def test_all_sliders_at_their_minima_together():
    at = _fresh_app()
    for state_key in ("k_slider", "s_slider", "a_slider", "stage_slider", "m_slider", "c_slider", "eps_slider", "b_slider"):
        at.sidebar.slider(key=state_key).set_value(at.sidebar.slider(key=state_key).min)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
