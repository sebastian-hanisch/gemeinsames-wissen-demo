"""Gemeinsame Fixtures: Mini-Instanzen, die von Hand gerechnet sind (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def zwei_kinder():
    """Zwei Kinder, Bit 0 = Kind 1, Bit 1 = Kind 2. Nach der Ansage „mindestens eines“ bleiben die Welten 01, 10, 11 (als Zahlen 1, 2, 3).
    Handrechnung: In Welt 1 (nur Kind 1 schmutzig) weiß Kind 1 es sofort (Welt 0 ist ausgeschieden), Kind 2 nicht (Welt 3 ist noch möglich).
    In Welt 3 weiß keiner etwas; nach dem Schweigen bleibt nur Welt 3; in Runde 2 wissen beide."""
    import gmw_algorithm as A
    return 2, A.announce(A.all_worlds(2), 1)
