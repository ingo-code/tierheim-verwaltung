"""Vertragstests: Das muss JEDES HundRepository können.

Dieselben Tests laufen gegen alle Umsetzungen (In-Memory und SQLite).
"""

from datetime import date

import pytest

from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status
from tierheim.domain.medikation import Medikation
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository
from tierheim.infrastructure.sqlite_hund_repository import SqliteHundRepository

CHIP = Chipnummer("276098100123456")


def hund(name: str = "Bello", chipnummer: Chipnummer | None = None) -> Hund:
    return Hund(
        name=name,
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=date(2026, 11, 20),
        herkunft=Herkunft.FUNDTIER,
        chipnummer=chipnummer,
    )


def _in_memory(tmp_path):
    return InMemoryHundRepository()


def _sqlite(tmp_path):
    return SqliteHundRepository.fuer_url(f"sqlite:///{tmp_path / 'test.db'}")


@pytest.fixture(params=[_in_memory, _sqlite], ids=["in_memory", "sqlite"])
def repository(request, tmp_path):
    return request.param(tmp_path)


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


def test_status_und_rasse_werden_gespeichert(repository):
    bello = hund()
    bello.rasse = "Labrador-Mix"
    bello.status = Status.VERMITTELBAR
    repository.speichern(bello)

    geladen = repository.finde_per_id(bello.id)

    assert geladen.status == Status.VERMITTELBAR
    assert geladen.rasse == "Labrador-Mix"


def test_medikationen_werden_mitgespeichert(repository):
    bello = hund()
    metacam = Medikation(
        medikament="Metacam",
        dosis="1,5 ml",
        startdatum=date(2026, 11, 20),
        enddatum=date(2026, 12, 4),
        intervall_tage=2,
    )
    bello.medikation_hinzufuegen(metacam)
    repository.speichern(bello)

    assert repository.finde_per_id(bello.id).medikationen == [metacam]


def test_spaeter_hinzugefuegte_medikation_wird_gespeichert(repository):
    bello = hund()
    erste = Medikation(medikament="Metacam", dosis="1,5 ml", startdatum=date(2026, 11, 20))
    zweite = Medikation(medikament="Wurmkur", dosis="1 Tablette", startdatum=date(2026, 11, 21))
    bello.medikation_hinzufuegen(erste)
    repository.speichern(bello)

    geladen = repository.finde_per_id(bello.id)
    geladen.medikation_hinzufuegen(zweite)
    repository.speichern(geladen)

    assert repository.finde_per_id(bello.id).medikationen == [erste, zweite]


def test_alle_liefert_jeden_hund_genau_einmal(repository):
    for name in ("Bello", "Luna", "Rex"):
        repository.speichern(hund(name=name))

    assert sorted(h.name for h in repository.alle()) == ["Bello", "Luna", "Rex"]
