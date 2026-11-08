"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und die Aussagen der Hilfetexte."""

import gmw_constants as C
import gmw_evaluation as ev
import gmw_presets as P
from gmw_scenario import Settings, generals_view, mud_view


def _settings(name):
    return Settings(**C.PRESETS[name])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_default_preset_equals_the_default_settings():
    assert _settings("Drei schmutzige Kinder (Standard)") == Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_help_texts_state_what_the_presets_do():
    std = mud_view(_settings("Drei schmutzige Kinder (Standard)"))
    assert std.first == (3, 3, 3, 4)                                     # „drei melden sich in Runde 3, das saubere in Runde 4“
    no_a = mud_view(_settings("Ohne Ansage"))
    assert all(x is None for x in no_a.first) and no_a.settings.k - 1 >= 2   # „mindestens zwei schmutzige“ sieht jedes Kind
    two = mud_view(_settings("Ansage „mindestens zwei“"))
    assert two.first[0] == 3 and ev.rounds_formula(4, 1) == 4            # „k − a + 1 = 3 statt 4“
    one = mud_view(_settings("Ein schmutziges Kind"))
    assert one.first[0] == 1
    strict = generals_view(_settings("Zwei Generäle: strenge Schwelle"))
    default = generals_view(_settings("Drei schmutzige Kinder (Standard)"))
    assert strict.settings.c <= strict.settings.m and strict.both < default.both
    assert abs(strict.disagree / strict.both - default.disagree / default.both) < 1e-12   # „das Verhältnis beider bleibt gleich“
    boten = _settings("Zwei Generäle: drei Boten")
    assert boten.loss_eff == 0.125                                       # „12,5 %“


def test_every_other_preset_differs_from_the_standard():
    std = C.PRESETS["Drei schmutzige Kinder (Standard)"]
    for name, preset in C.PRESETS.items():
        if name != "Drei schmutzige Kinder (Standard)":
            assert preset != std, name
