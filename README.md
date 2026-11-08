# Gemeinsames Wissen: Schmutzige Kinder und Zwei Generäle – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-gemeinsames-wissen-demo.streamlit.app/)** -->

Stück 6 der Linie **Teamrätsel** (Arbeitstitel) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Zwei klassische Rätsel, ein Gedanke: **„alle wissen es“ ist nicht „es ist gemeinsames Wissen“.** Teil A rechnet die **Schmutzigen Kinder** als Kripke-Modell (Welten, Sichten, öffentliche Ansage, Antwortrunden), Teil B die **Zwei Generäle** im Kettenmodell (Sichten, Wissensebenen, Aufzählung aller Entscheidungsregeln, Verlust und Boten). Es gibt keine Auszahlungen und keinen Eigennutz: gefragt ist, was jemand aus dem schließen kann, was er sieht und hört.

Abgrenzung: `globale-spiele-demo` (Experiment E6, E-Mail-Spiel) rechnet nahe verwandt, aber als Spiel mit Auszahlungen und Gleichgewicht, die Stufen des Wissens nur als Wahrscheinlichkeit (1−ε)ⁿ; hier stehen die Wissensstruktur selbst und **alle** Regeln im Mittelpunkt, und das E-Mail-Spiel wird **nicht** nachgerechnet. `endliche-horizonte-demo` nennt gemeinsames Wissen nur als Grenze der Rückwärtsinduktion. Das Koordinationsspiele-Stück `vorabsignale-demo` (kostenloses Reden vor einem Koordinationsspiel; bisher nur als Plan, ohne Repo) rechnet mit Auszahlungen und Lernen. **Die Kinder und die Generäle sind Modelle, keine Aussagen über Menschen oder echte Netze.**

## Warum dieses Problem

Ab zwei schmutzigen Kindern sieht jedes Kind schon vor der Ansage des Vaters („mindestens eines von euch ist schmutzig“), dass die Ansage stimmt. Sie sagt keinem etwas, das er nicht sieht, und doch bleiben die Kinder ohne sie stumm, mit ihr melden sich die schmutzigen in Runde k. **Kernfrage A:** Was ändert die Ansage, wenn niemand etwas Neues erfährt? **Kernfrage B:** Kann eine Kette von Boten leisten, was die Ansage leistet, oder gibt es überhaupt eine Regel, die Einigkeit und Angriff zugleich liefert?

## Modell

* **Schmutzige Kinder.** Eine Welt ist ein Bitvektor über n Kinder (1 = schmutzig); Kind i unterscheidet w nicht von w mit gekipptem Bit i. Die Ansage „mindestens a“ schneidet die Weltenmenge auf die Welten mit mindestens a schmutzigen Kindern; in jeder Runde antworten alle gleichzeitig auf „weißt du, ob du schmutzig bist?“ und alle hören alle Antworten. Kinder sehen alle anderen, sind ehrlich und schließen fehlerfrei, und das wissen alle voneinander.
* **Wissensleiter.** E^j φ heißt: jedes Kind weiß, dass jedes weiß, … (j Stufen). Gemeinsames Wissen C φ heißt: φ gilt in der ganzen von der wirklichen Welt aus erreichbaren Komponente.
* **Zwei Generäle.** A hat einen Befehl und sendet Nachricht 1; jede angekommene Nachricht wird bestätigt (Nachricht i nur, wenn i − 1 ankam), höchstens m Nachrichten. Welt k: die ersten k Nachrichten kamen an; Welt NO: kein Befehl. Jeder General entscheidet nur aus seiner Sicht (A kann die Welten 2t und 2t+1 nicht unterscheiden, B die Welten 2t+1 und 2t+2 sowie NO und 0). Eine Regel ordnet jeder Sicht Angriff oder Warten zu; **gültig** heißt: ohne Befehl greift keiner an.
* **Verlust.** Jeder Bote geht unabhängig mit Wahrscheinlichkeit ε verloren; tragen b Boten dieselbe Nachricht, geht sie mit ε^b verloren.
* Formeln und Quellen stehen im Expander „📐 Mathematische Formulierung“ der App.

## Methodik

* **Kern ohne Zufall:** `gmw_algorithm.py` rechnet die Schmutzigen Kinder mit Bitmasken und Weltenmengen (Ansage, Antworten, Hören, Wissensebene, Erreichbarkeit); `gmw_generals.py` die Kette (Sichten als Klassen, Wissensebene, Aufzählung aller 2^V Regeln, Schwellenregel, Verlust).
* **Aufzählung statt Beweis:** die Zahl der Regeln, die einig sind oder angreifen, wird für m = 1 bis 10 gezählt (Experiment E4), die Pareto-Menge aller Regeln bei Verlust ε wird aus allen Regeln gebildet und mit der Schwellenformel verglichen.
* **Zufall** nur in „Nachricht für Nachricht“ und in der Simulation: SplitMix64 (`gmw_rng.py`, wörtliche Kopie aus `ab-test-demo`).
* **Rechenaufwand:** Teil A höchstens 10 Kinder (1.024 Welten), Teil B höchstens m = 10 (2.048 gültige Regeln). Jede Rechnung am Regler-Maximum, auch die Experimente E1 bis E6 und die Simulation mit 20.000 Ketten, brauchte jeweils höchstens rund 0,25 Sekunden (einmal gemessen auf der Entwicklungsmaschine, nicht getestet). Die ▶️-Knöpfe rechnen nach Klick.
* **Experimente:** E1 Alle wissen es – und trotzdem schweigen sie, E2 Ohne Ansage schweigen alle ewig, E3 Runde gegen k und a, E4 Keine Regel genügt, E5 Boten statt Nachrichten, E6 Weltenzahl nach r stillen Runden.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind eigene Rechnung und stehen in `tests/test_claims.py`.

| Frage | Befund | Test |
|---|---|---|
| Wann melden sich die schmutzigen Kinder? | Bei Ansage „mindestens a“ in **Runde k − a + 1**, die sauberen Kinder eine Runde später (Kripke-Modell, Tupel-Orakel, Induktion und Formel gleich in allen **85** Fällen mit n ≤ 8, a ∈ {1, 2, 3}, a ≤ k ≤ n). | `test_rounds_k_minus_a_plus_1_in_85_cases` |
| Was ohne Ansage? | **Nie**: in allen **21** Fällen (n ≤ 6, k = 1 … n) weiß kein Kind etwas, die Weltenmenge ändert sich nicht. | `test_without_announcement_nobody_ever_knows` |
| Wie tief reicht „alle wissen es“ vor der Ansage? | „Mindestens a schmutzig“ gilt als E^j genau für **j ≤ k − a** (n ≤ 7, a ∈ {1, 2, 3}, a ≤ k ≤ n: **64** Fälle); gemeinsames Wissen ist es in keinem davon. Nach der Ansage ist es gemeinsames Wissen in allen **64**. | `test_knowledge_ladder_depth_in_64_cases` |
| Wie hängen Tiefe und Rundenzahl zusammen? | Die Meldung kommt in der Runde nach der Tiefe: Runde = Tiefe + 1 (dieselben 64 Fälle). | `test_knowledge_ladder_depth_in_64_cases` |
| Wie schrumpft die Weltenmenge? | n = 6, alle schmutzig, Ansage „mindestens eines“: **63, 57, 42, 22, 7, 1** Welten nach 0, 1, …, 5 stillen Runden = Σ_{j>r} C(6, j). | `test_world_counts_n_6` |
| Gibt es gemeinsames Wissen in der Kette? | **Nirgends** (m = 1 … 10, alle Welten); in Welt k gilt „Befehl liegt vor“ genau als **E^k**, auch bei allen m angekommenen Nachrichten nur E^m. | `test_chain_levels_equal_delivered_messages` |
| Wie viele Regeln gibt es, wie viele genügen? | Gültige Regeln: **2^(m+1)**, also 4 bei m = 1 bis 2.048 bei m = 10 (**4.092** zusammen für m = 1 … 10); davon ist **genau 1** in allen Welten einig („nie angreifen“) und **keine dieser einigen Regeln** greift bei allen m angekommenen Nachrichten an. | `test_rule_counts_m_1_to_10` |
| Was ist die beste Regel bei Verlust ε? | Die Pareto-Menge (P(beide greifen an), P(genau einer greift an)) aller gültigen Regeln ist **exakt** die Schwellenfamilie ((1−ε)^c, ε(1−ε)^(c−1)), c = 1 … m, plus „nie angreifen“: in allen **16** Zellen ε ∈ {1/2, 1/5, 1/10, 1/20} × m ∈ {3, 5, 7, 9}. Das Verhältnis Uneinigkeit zu gemeinsamem Angriff ist **ε/(1−ε)**, für jede Schwelle und jedes m dasselbe. | `test_pareto_is_threshold_family_in_16_cells` |
| Beispiel Standardeinstellung | ε = 20 %, m = 5, c = 3, 1 Bote: beide greifen an mit **51,2 %**, genau einer mit **12,8 %**, Verhältnis **0,25**. | `test_default_numbers` |
| Was bringen Boten? | Verlust 20 % je Bote, c = 3: bei 1 / 2 / 5 Boten je Nachricht greift genau einer mit **12,8 % / 3,69 % / 0,032 %** an (beide in **51,2 % / 88,5 % / 99,9 %**); das Verhältnis Uneinigkeit zu Angriff fällt von 0,25 auf unter 0,001 (b = 5), bleibt aber größer als 0. **Die Uneinigkeit selbst** wächst bis ε = 1/c (bei 50 % Verlust je Bote und c = 3: 12,5 % mit 1 Boten, 14,1 % mit 2 Boten). | `test_messengers_table`, `test_the_absolute_disagreement_is_not_monotone_in_the_number_of_messengers` |
| Stimmt die Formel mit dem Spiel überein? | Simulation (20.000 Ketten, Zufalls-Seed 35, m = 5, c = 3, ε = 20 %): alle **3** Ausgänge liegen innerhalb von 4 Standardfehlern um die Formel. | `test_simulation_within_four_standard_errors` |

**Befunde gegenüber dem Plan (`teamraetsel-planung/PLAN.md`):** Der Plan erwartete „Koordination mit beliebig vielen Boten unmöglich“ und „wie nah man mit wachsender Botenzahl an Sicherheit kommt“. Gerechnet ist schärfer: im Kettenmodell ändert die **Länge** der Kette (m) am Verhältnis Uneinigkeit zu Angriff **nichts**; sie erlaubt nur strengere Schwellen (seltener angreifen). Näher an Sicherheit kommt man über **mehr Boten je Nachricht** (ε^b), nie bis zur Sicherheit; dabei fällt das Verhältnis, nicht in jeder Stufe aber die Uneinigkeit selbst (sie steigt, solange ε^b über 1/c liegt).

## Ehrliche Grenzen

* **Lehrbuchkerne.** Die Rätsel und ihre Lösung (k Runden, Unmöglichkeit der garantierten Koordination) sind bekannt; neu ist hier nur die Aufzählung aller Regeln im Kettenmodell und das Verhältnis ε/(1−ε), jeweils für diese Modelle.
* **Kettenmodell:** andere Kommunikationsmuster (parallele Boten ohne Bestätigung, Zeitschranken, Wiederholungen, mehrere Runden gleichzeitig) sind nicht gerechnet. Der Verlust ist unabhängig und gleich groß; bei **gegnerischem** Verlust gelten die Verlustzahlen nicht (die Aufzählung über Welten gilt weiter).
* **Regeln hängen nur von der eigenen Sicht ab, ohne Zufall.** Mischungen aus diesen Regeln haben ein Verhältnis, das nicht unter dem kleinsten liegt (Mediantenregel); Regeln mit geteiltem Zufall (gemeinsamer Münzwurf vorab) sind nicht gerechnet.
* **Schmutzige Kinder:** vollständige Sicht, ehrliche und fehlerfreie Kinder, gleichzeitige Antwort, wahre Ansage. Bei unvollständiger Sicht (nur Nachbarn) oder Fehlern gilt die Rundenformel nicht; nicht gerechnet. Die Kinder sind austauschbar, die schmutzigen sind die ersten k.
* **Kein E-Mail-Spiel, keine Auszahlungen.** Ob ein Betrieb bei Verlustrisiko angreift, ist eine Gleichgewichtsfrage (`globale-spiele-demo`, E6); sie wird hier weder nachgerechnet noch bestätigt.
* **Quellen** nur laut Abstract bzw. Einleitung (Websuche 2026-11-08), nicht im Volltext: Aumann (1976), „Agreeing to Disagree“, *Annals of Statistics* 4(6), 1236–1239 (Definition gemeinsamen Wissens als unendliche Kette); Halpern und Moses (1990), „Knowledge and Common Knowledge in a Distributed Environment“, *Journal of the ACM* 37(3), 549–587 (ein korrektes Protokoll greift nur an, wenn der Angriff gemeinsames Wissen ist; bei nicht garantierter Kommunikation ist es unerreichbar). Rubinstein (1989), „The Electronic Mail Game“, nur als Verweis auf `globale-spiele-demo`, hier nicht nachgelesen. Die Rätsel selbst sind Sammlungswissen. Die Zahlen und Zählungen sind eigene Rechnung und stammen aus keiner dieser Arbeiten.
* Mausklicks auf die Diagramme sind nicht getestet (keine Auswahl in den Diagrammen). Nur an erfundenen Parametern geprüft, keine Messung an Menschen oder Netzen.

## Verifikation

* **Umfang:** die Suite umfasst 220 Tests (`pytest tests`).
* **Kern gegen Handrechnung** (`tests/conftest.py`, `tests/test_algorithm.py`): zwei Kinder (Welten 1, 2, 3, Antworten und Runden von Hand), n = 3 (7, 4, 1 Welten nach der Ansage), E und E² für n = 2, Sichten und Regelzahl für m = 1 und m = 2, Schwellenregel c = 1 und c = 2.
* **Orakel** (`tests/test_oracle_gemeinsames_wissen.py`): Schmutzige Kinder mit Tupelmengen und eigener Eliminationsschleife, einer Induktion ohne Welten, der Formel k − a + 1 und dem Hamming-Abstand für die Wissensleiter (n ≤ 6 bzw. 7, a ∈ {0, 1, 2, 3}); gemeinsames Wissen per Breitensuche auf Tupeln; Sichten der Generäle aus den Nachrichtenlisten selbst (m = 1 … 10); Regeln mit `itertools.product` in exakten Brüchen gegen den Kern; Pareto-Menge gegen die Schwellenformel.
* **Eigenschaften** (`tests/test_properties.py`): Reihenfolge der Kinder, saubere Kinder ändern die Meldung der schmutzigen nicht, stärkere Ansage spart Runden, Wahrscheinlichkeiten summieren sich zu 1, Verhältnis unabhängig von m und c, die Uneinigkeit ist in der Botenzahl nicht monoton.
* **Zweig-Tests:** Ansage 0 weicht von Ansage 1 ab; Schwelle über m greift nie an; falsche Ansage meldet eine Warnung.
* **Claims** (`tests/test_claims.py`): jede Zahl dieser README. **Verdikte** (`tests/test_verdicts.py`), **Randfälle** (`tests/test_edge_cases.py`), **Presets** samt Hilfetexten (`tests/test_presets.py`).
* **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum, die ▶️-Knöpfe einzeln, PDF), Permalink, Layout, Footer, Laufzeit-Importe. Mutationstests gibt es nicht (abgeschafft).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Teil A, Teil B, Experimente, PDF, Annahmen, Mathematik) |
| `gmw_algorithm.py` | Kern Teil A: Welten, Ansage, Antwortrunden, Wissensebene, gemeinsames Wissen |
| `gmw_generals.py` | Kern Teil B: Kette, Sichten, Aufzählung der Regeln, Schwellenregel, Verlust |
| `gmw_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `gmw_evaluation.py` | Zahlenformat und Verdikte als reine Funktionen |
| `gmw_experiments.py` | Experimente E1 bis E6 und die Simulation |
| `gmw_layout.py` | Fester Kopf (Stylesheet) |
| `gmw_pdf_export.py` | PDF-Export (fpdf2), nach Klick |
| `gmw_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `gmw_rng.py` | SplitMix64, wörtliche Kopie aus `ab-test-demo` |
| `gmw_scenario.py` | Einstellungen und die beiden Sichten |
| `gmw_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen, Orakel, Eigenschaften, Claims, Verdikte, Randfälle, Presets, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

* Unvollständige Sicht der Kinder (Sichtgraph), fehlerhafte oder lügende Kinder.
* Das E-Mail-Spiel und jede Auszahlung: `globale-spiele-demo`. Kostenlose Nachrichten vor Koordinationsspielen: Koordinationsspiele-Stück `vorabsignale-demo` (bisher nur als Plan).
* Gegnerischer Verlust, Zeitschranken, parallele Boten ohne Bestätigung, zufällige Regeln mit geteiltem Münzwurf.
* Byzantinische Generäle (Verräter unter den Generälen): anderes Problem.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
