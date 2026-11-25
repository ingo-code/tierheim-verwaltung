from datetime import date
from uuid import uuid4

import pytest

from tierheim.application.heute_faellig import FaelligeGabe, HeuteFaellig
from tierheim.application.hund_anzeigen import HundNichtGefunden
from tierheim.application.medikation_hinzufuegen import (
    MedikationDaten,
    MedikationHinzufuegen,
)
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status
from tierheim.domain.medikation import Medikation, UngueltigeMedikation
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

HEUTE = date(2026, 11, 25)


def hund(name: str, status: Status = Status.AUFGENOMMEN) -> Hund:
    return Hund(
        name=name,
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=date(2026, 11, 1),
        herkunft=Herkunft.FUNDTIER,
        status=status,
    )


def medikation(medikament: str, **abweichungen) -> Medikation:
    werte = dict(medikament=medikament, dosis="1 Tablette", startdatum=date(2026, 11, 20))
    werte.update(abweichungen)
    return Medikation(**werte)


@pytest.fixture
def repository() -> InMemoryHundRepository:
    return InMemoryHundRepository()


# --- MedikationHinzufuegen ---------------------------------------------------


def test_medikation_wird_hinzugefuegt_und_gespeichert(repository):
    bello = hund("Bello")
    repository.speichern(bello)

    neu = MedikationHinzufuegen(repository).ausfuehren(
        bello.id, MedikationDaten(medikament="Metacam", dosis="1,5 ml", startdatum=HEUTE)
    )

    gespeichert = repository.finde_per_id(bello.id)
    assert gespeichert.medikationen == [neu]
    assert neu.medikament == "Metacam"


def test_medikation_fuer_unbekannten_hund_wird_abgelehnt(repository):
    with pytest.raises(HundNichtGefunden):
        MedikationHinzufuegen(repository).ausfuehren(
            uuid4(), MedikationDaten(medikament="Metacam", dosis="1,5 ml", startdatum=HEUTE)
        )


def test_ungueltige_medikation_wird_nicht_gespeichert(repository):
    bello = hund("Bello")
    repository.speichern(bello)

    with pytest.raises(UngueltigeMedikation):
        MedikationHinzufuegen(repository).ausfuehren(
            bello.id, MedikationDaten(medikament="", dosis="1,5 ml", startdatum=HEUTE)
        )

    assert repository.finde_per_id(bello.id).medikationen == []


# --- HeuteFaellig ------------------------------------------------------------


def test_ohne_medikationen_ist_die_tagesliste_leer(repository):
    repository.speichern(hund("Bello"))

    assert HeuteFaellig(repository, heute=lambda: HEUTE).ausfuehren() == []


def test_tagesliste_enthaelt_nur_heute_faellige_gaben_sortiert_nach_hund(repository):
    rex, anton = hund("Rex"), hund("Anton")
    metacam = medikation("Metacam")
    wurmkur = medikation("Wurmkur", startdatum=date(2026, 11, 24), intervall_tage=7)
    beendet = medikation("Antibiotikum", enddatum=date(2026, 11, 22))
    rex.medikation_hinzufuegen(metacam)
    anton.medikation_hinzufuegen(beendet)
    anton.medikation_hinzufuegen(wurmkur)  # erst wieder am 01.12. fällig
    repository.speichern(rex)
    repository.speichern(anton)

    tagesliste = HeuteFaellig(repository, heute=lambda: HEUTE).ausfuehren()

    assert tagesliste == [FaelligeGabe(hund=rex, medikation=metacam)]


def test_vermittelte_hunde_stehen_nicht_auf_der_tagesliste(repository):
    vermittelt = hund("Luna", status=Status.VERMITTELT)
    vermittelt.medikation_hinzufuegen(medikation("Metacam"))
    im_heim = hund("Bello")
    tablette = medikation("Schilddrüse")
    im_heim.medikation_hinzufuegen(tablette)
    repository.speichern(vermittelt)
    repository.speichern(im_heim)

    tagesliste = HeuteFaellig(repository, heute=lambda: HEUTE).ausfuehren()

    assert [gabe.hund.name for gabe in tagesliste] == ["Bello"]


def test_mehrere_gaben_werden_nach_hund_und_medikament_sortiert(repository):
    bello, anton = hund("Bello"), hund("Anton")
    for name in ("Zylkene", "Metacam"):
        bello.medikation_hinzufuegen(medikation(name))
    anton.medikation_hinzufuegen(medikation("Wurmkur"))
    repository.speichern(bello)
    repository.speichern(anton)

    tagesliste = HeuteFaellig(repository, heute=lambda: HEUTE).ausfuehren()

    assert [(g.hund.name, g.medikation.medikament) for g in tagesliste] == [
        ("Anton", "Wurmkur"),
        ("Bello", "Metacam"),
        ("Bello", "Zylkene"),
    ]
