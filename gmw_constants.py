"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# Schmutzige Kinder: k schmutzige und s saubere Kinder (n = k + s), Ansage „mindestens a“
K_MIN, K_MAX, DEFAULT_K = 1, 6, 3
S_MIN, S_MAX, DEFAULT_S = 0, 4, 1
A_MIN, A_MAX, DEFAULT_A = 0, 3, 1
STAGE_MIN, STAGE_MAX, DEFAULT_STAGE = 0, 7, 0   # Graph und Zähler nach so vielen Runden; nach dem Ende ändert sich nichts mehr
N_MAX = K_MAX + S_MAX                           # 10 Kinder, 1.024 Welten: 1.024 · 10 Prüfungen je Runde
GRAPH_N_MAX = 4                                 # der Weltengraph (Hyperwürfel) wird nur bis 4 Kinder gezeichnet (16 Welten)

# Zwei Generäle: Kette von m Nachrichten, Verlust eps_pct Prozent je Boten, b Boten je Nachricht, Schwelle c
M_MIN, M_MAX, DEFAULT_M = 1, 10, 5              # Aufzählung: 2^(m + 3) Regeln bei m = 10 sind 8.192
C_MIN, C_MAX, DEFAULT_C = 1, 11, 3              # c > m heißt: die Schwelle wird nie erreicht, niemand greift an
EPS_MIN, EPS_MAX, DEFAULT_EPS = 5, 50, 20       # Prozent
B_MIN, B_MAX, DEFAULT_B = 1, 5, 1
SEED_MAX, DEFAULT_SEED = 999999, 35
GAMES = 20000                                   # Spiele der Simulation „Formel gegen Simulation“
ENUM_M_MAX = M_MAX                              # Experiment E4 zählt m = 1 bis 10

COLOR_DIRTY = "#a0522d"
COLOR_CLEAN = "#4c78a8"
COLOR_OFF = "rgba(150,150,150,0.35)"
COLOR_A = "#2F6B65"
COLOR_B = "#b5651d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Drei schmutzige Kinder (Standard)": {"k": 3, "s": 1, "a": 1, "stage": 0, "m": 5, "c": 3, "eps": 20, "b": 1, "seed": DEFAULT_SEED},
    "Ohne Ansage": {"k": 3, "s": 1, "a": 0, "stage": 0, "m": 5, "c": 3, "eps": 20, "b": 1, "seed": DEFAULT_SEED},
    "Ansage „mindestens zwei“": {"k": 4, "s": 0, "a": 2, "stage": 0, "m": 5, "c": 3, "eps": 20, "b": 1, "seed": DEFAULT_SEED},
    "Ein schmutziges Kind": {"k": 1, "s": 2, "a": 1, "stage": 0, "m": 5, "c": 3, "eps": 20, "b": 1, "seed": DEFAULT_SEED},
    "Zwei Generäle: strenge Schwelle": {"k": 3, "s": 1, "a": 1, "stage": 0, "m": 8, "c": 6, "eps": 20, "b": 1, "seed": DEFAULT_SEED},
    "Zwei Generäle: drei Boten": {"k": 3, "s": 1, "a": 1, "stage": 0, "m": 5, "c": 3, "eps": 50, "b": 3, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Drei schmutzige Kinder (Standard)": "Vier Kinder, drei davon schmutzig, der Vater sagt „mindestens eines“: die drei melden sich in Runde 3, das saubere in Runde 4. Generäle: fünf Nachrichten, 20 % Verlust, Schwelle 3.",
    "Ohne Ansage": "Dieselben Kinder, aber der Vater schweigt: obwohl jedes Kind mindestens zwei schmutzige sieht, weiß nie eines etwas. Die Weltenmenge ändert sich nicht.",
    "Ansage „mindestens zwei“": "Vier schmutzige Kinder, der Vater sagt „mindestens zwei“: die Ansage ist stärker und spart Runden (k − a + 1 = 3 statt 4).",
    "Ein schmutziges Kind": "Ein schmutziges Kind sieht lauter saubere und schließt aus der Ansage sofort auf sich: Runde 1.",
    "Zwei Generäle: strenge Schwelle": "Acht Nachrichten, Schwelle 6: angegriffen wird selten, dafür gibt es seltener Uneinigkeit. Das Verhältnis beider bleibt gleich.",
    "Zwei Generäle: drei Boten": "50 % Verlust je Bote, aber drei Boten je Nachricht: eine Nachricht geht nur mit 12,5 % verloren. Sicherheit wird nur angenähert, nie erreicht.",
}
