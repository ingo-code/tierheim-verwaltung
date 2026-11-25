from datetime import date

import pytest

from tierheim.application.neuzugang_erfassen import NeuzugangDaten, NeuzugangErfassen
from tierheim.domain.chipnummer import Chipnummer, UngueltigeChipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status, UngueltigerHund

HEUTE = date(2026, 11, 25)


class FakeHundRepository:
    """Test-Double: erfüllt das Protocol HundRepository, speichert nur in einer Liste."""

    def __init__(self) -> None:
        self.gespeichert: list[Hund] = []

    def speichern(self, hund: Hund) -> None:
        self.gespeichert.append(hund)


def daten(**abweichungen) -> NeuzugangDaten:
    werte = dict(
        name="Luna",
        geschlecht=Geschlecht.HUENDIN,
        herkunft=Herkunft.ABGABE,
        aufnahmedatum=HEUTE,
    )
    werte.update(abweichungen)
    return NeuzugangDaten(**werte)


@pytest.fixture
def repository() -> FakeHundRepository:
    return FakeHundRepository()


@pytest.fixture
def neuzugang_erfassen(repository) -> NeuzugangErfassen:
    return NeuzugangErfassen(repository=repository, heute=lambda: HEUTE)


def test_neuzugang_wird_gespeichert(neuzugang_erfassen, repository):
    hund = neuzugang_erfassen.ausfuehren(daten())

    assert repository.gespeichert == [hund]
    assert hund.name == "Luna"
    assert hund.status == Status.AUFGENOMMEN


def test_chipnummer_aus_eingabe_wird_bereinigt_uebernommen(neuzugang_erfassen):
    hund = neuzugang_erfassen.ausfuehren(daten(chipnummer="276 098 100 123 456"))

    assert hund.chipnummer == Chipnummer("276098100123456")


def test_ungueltige_chipnummer_wird_nicht_gespeichert(neuzugang_erfassen, repository):
    with pytest.raises(UngueltigeChipnummer):
        neuzugang_erfassen.ausfuehren(daten(chipnummer="123"))

    assert repository.gespeichert == []


def test_aufnahmedatum_in_der_zukunft_wird_abgelehnt(neuzugang_erfassen, repository):
    with pytest.raises(UngueltigerHund):
        neuzugang_erfassen.ausfuehren(daten(aufnahmedatum=date(2026, 11, 26)))

    assert repository.gespeichert == []
