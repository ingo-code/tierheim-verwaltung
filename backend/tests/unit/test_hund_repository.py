"""Vertragstests: Das muss JEDES HundRepository können.

In Lektion 6 kommt hier die SQLite-Umsetzung als zweiter Parameter dazu –
die Tests bleiben gleich.
"""

from datetime import date

import pytest

from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

CHIP = Chipnummer("276098100123456")


def hund(name: str = "Bello", chipnummer: Chipnummer | None = None) -> Hund:
    return Hund(
        name=name,
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=date(2026, 11, 20),
        herkunft=Herkunft.FUNDTIER,
        chipnummer=chipnummer,
    )


@pytest.fixture(params=[InMemoryHundRepository], ids=["in_memory"])
def repository(request):
    return request.param()


def test_neues_repository_ist_leer(repository):
    assert repository.alle() == []


def test_gespeicherter_hund_wird_wiedergefunden(repository):
    bello = hund()
    repository.speichern(bello)

    assert repository.finde_per_id(bello.id) == bello
    assert repository.alle() == [bello]


def test_unbekannte_id_liefert_none(repository):
    assert repository.finde_per_id(hund().id) is None


def test_hund_wird_per_chipnummer_gefunden(repository):
    bello = hund(chipnummer=CHIP)
    repository.speichern(hund(name="Luna"))
    repository.speichern(bello)

    assert repository.finde_per_chip(CHIP) == bello


def test_unbekannte_chipnummer_liefert_none(repository):
    repository.speichern(hund())

    assert repository.finde_per_chip(CHIP) is None


def test_erneutes_speichern_aktualisiert_statt_zu_verdoppeln(repository):
    bello = hund()
    repository.speichern(bello)
    bello.chip_nachtragen(CHIP)
    repository.speichern(bello)

    assert len(repository.alle()) == 1
    assert repository.finde_per_chip(CHIP) == bello
