from datetime import date

import pytest

from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status, UngueltigerHund


def neuer_hund(**abweichungen) -> Hund:
    """Test-Helfer: ein gültiger Hund, einzelne Felder lassen sich überschreiben."""
    werte = dict(
        name="Bello",
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=date(2026, 11, 20),
        herkunft=Herkunft.FUNDTIER,
    )
    werte.update(abweichungen)
    return Hund(**werte)


def test_neuer_hund_hat_status_aufgenommen():
    assert neuer_hund().status == Status.AUFGENOMMEN


def test_neuer_hund_hat_noch_keine_chipnummer():
    assert neuer_hund().chipnummer is None


def test_jeder_hund_bekommt_eine_eigene_id():
    assert neuer_hund().id != neuer_hund().id


@pytest.mark.parametrize("name", ["", "   "])
def test_hund_ohne_namen_wird_abgelehnt(name):
    with pytest.raises(UngueltigerHund):
        neuer_hund(name=name)


def test_hund_ohne_chip_bekommt_chip_nachgetragen():
    hund = neuer_hund()
    hund.chip_nachtragen(Chipnummer("276098100123456"))
    assert hund.chipnummer == Chipnummer("276098100123456")


def test_vorhandener_chip_wird_nicht_ueberschrieben():
    hund = neuer_hund(chipnummer=Chipnummer("276098100123456"))
    with pytest.raises(UngueltigerHund):
        hund.chip_nachtragen(Chipnummer("276098100999999"))
