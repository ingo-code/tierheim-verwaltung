"""Schritt 0: Der leere Test.

Er beweist nur, dass die Werkzeugkette läuft (uv, pytest, Paket importierbar).
Erst wenn dieser Test grün ist, wird committet – das ist unser Startpunkt.
"""

import tierheim


def test_paket_ist_importierbar():
    assert tierheim is not None
