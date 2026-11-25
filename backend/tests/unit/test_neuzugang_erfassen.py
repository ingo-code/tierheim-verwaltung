from datetime import date

import pytest

from tierheim.application.neuzugang_erfassen import (
    ChipnummerBereitsVergeben,
    NeuzugangDaten,
    NeuzugangErfassen,
)
from tierheim.domain.chipnummer import Chipnummer, UngueltigeChipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Status, UngueltigerHund
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

HEUTE = date(2026, 11, 25)


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
def repository() -> InMemoryHundRepository:
    return InMemoryHundRepository()


@pytest.fixture
def neuzugang_erfassen(repository) -> NeuzugangErfassen:
    return NeuzugangErfassen(repository=repository, heute=lambda: HEUTE)


def test_neuzugang_wird_gespeichert(neuzugang_erfassen, repository):
    hund = neuzugang_erfassen.ausfuehren(daten())

    assert repository.alle() == [hund]
    assert hund.name == "Luna"
    assert hund.status == Status.AUFGENOMMEN


def test_chipnummer_aus_eingabe_wird_bereinigt_uebernommen(neuzugang_erfassen):
    hund = neuzugang_erfassen.ausfuehren(daten(chipnummer="276 098 100 123 456"))

    assert hund.chipnummer == Chipnummer("276098100123456")


def test_ungueltige_chipnummer_wird_nicht_gespeichert(neuzugang_erfassen, repository):
    with pytest.raises(UngueltigeChipnummer):
        neuzugang_erfassen.ausfuehren(daten(chipnummer="123"))

    assert repository.alle() == []


def test_aufnahmedatum_in_der_zukunft_wird_abgelehnt(neuzugang_erfassen, repository):
    with pytest.raises(UngueltigerHund):
        neuzugang_erfassen.ausfuehren(daten(aufnahmedatum=date(2026, 11, 26)))

    assert repository.alle() == []


def test_doppelte_chipnummer_wird_abgelehnt(neuzugang_erfassen, repository):
    luna = neuzugang_erfassen.ausfuehren(daten(chipnummer="276098100123456"))

    with pytest.raises(ChipnummerBereitsVergeben) as fehler:
        neuzugang_erfassen.ausfuehren(daten(name="Rex", chipnummer="276 098 100 123 456"))

    assert "Luna" in str(fehler.value)
    assert repository.alle() == [luna]


def test_mehrere_hunde_ohne_chip_sind_erlaubt(neuzugang_erfassen, repository):
    neuzugang_erfassen.ausfuehren(daten(name="Luna"))
    neuzugang_erfassen.ausfuehren(daten(name="Rex"))

    assert len(repository.alle()) == 2
