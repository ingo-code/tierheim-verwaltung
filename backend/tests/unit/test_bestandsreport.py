from datetime import date

import pytest

from tierheim.application.bestandsreport import BestandExportieren, Bestandsreport, Langzeit
from tierheim.application.neuzugaenge_importieren import NeuzugaengeImportieren
from tierheim.application.neuzugang_erfassen import NeuzugangErfassen
from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status
from tierheim.domain.medikation import Medikation
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

HEUTE = date(2026, 11, 25)


def hund(
    name: str,
    aufnahmedatum: date,
    herkunft: Herkunft = Herkunft.FUNDTIER,
    status: Status = Status.AUFGENOMMEN,
    chipnummer: str | None = None,
) -> Hund:
    return Hund(
        name=name,
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=aufnahmedatum,
        herkunft=herkunft,
        status=status,
        chipnummer=Chipnummer(chipnummer) if chipnummer else None,
    )


@pytest.fixture
def repository() -> InMemoryHundRepository:
    repo = InMemoryHundRepository()
    bello = hund("Bello", date(2026, 11, 15), chipnummer="276098100000001")  # 10 Tage
    bello.medikation_hinzufuegen(
        Medikation(medikament="Metacam", dosis="1,5 ml", startdatum=date(2026, 11, 20))
    )
    for h in (
        bello,
        hund("Luna", date(2026, 11, 5), Herkunft.ABGABE, Status.VERMITTELBAR),  # 20 Tage
        hund("Rex", date(2026, 5, 29), Herkunft.BESCHLAGNAHME, Status.RESERVIERT),  # 180 Tage
        hund("Mia", date(2026, 10, 26), Herkunft.ABGABE, chipnummer="276098100000002"),  # 30
        hund("Alt", date(2025, 1, 1), status=Status.VERMITTELT),  # nicht mehr im Heim
    ):
        repo.speichern(h)
    return repo


@pytest.fixture
def report(repository):
    return Bestandsreport(repository, heute=lambda: HEUTE).ausfuehren()


def test_leerer_bestand_liefert_leeren_report():
    report = Bestandsreport(InMemoryHundRepository(), heute=lambda: HEUTE).ausfuehren()

    assert report.anzahl_im_heim == 0
    assert report.durchschnittliche_verweildauer_tage is None
    assert report.nach_status == {}
    assert report.langzeit == []


def test_anzahl_im_heim_ohne_vermittelte(report):
    assert report.anzahl_im_heim == 4


def test_verteilung_nach_status_ueber_alle_hunde(report):
    assert report.nach_status == {
        "aufgenommen": 2,
        "reserviert": 1,
        "vermittelbar": 1,
        "vermittelt": 1,
    }


def test_verteilung_nach_herkunft_nur_im_heim(report):
    assert report.nach_herkunft == {"abgabe": 2, "beschlagnahme": 1, "fundtier": 1}


def test_durchschnittliche_verweildauer_der_hunde_im_heim(report):
    assert report.durchschnittliche_verweildauer_tage == 60.0  # (10 + 20 + 180 + 30) / 4


def test_langzeit_zeigt_die_drei_laengsten_aufenthalte(report):
    assert report.langzeit == [
        Langzeit(name="Rex", tage=180),
        Langzeit(name="Mia", tage=30),
        Langzeit(name="Luna", tage=20),
    ]


def test_hunde_ohne_chip_alphabetisch(report):
    assert report.ohne_chip == ["Luna", "Rex"]


def test_anzahl_heute_faelliger_gaben(report):
    assert report.heute_faellige_gaben == 1


# --- CSV-Export ------------------------------------------------------------------


def test_export_hat_kopfzeile_und_deutsches_format(repository):
    csv = BestandExportieren(repository).ausfuehren()
    zeilen = csv.splitlines()

    assert zeilen[0] == "Name;Geschlecht;Herkunft;Aufnahmedatum;Rasse;Chipnummer;Status"
    assert "Bello;Rüde;Fundtier;15.11.2026;;276098100000001;aufgenommen" in zeilen
    assert len(zeilen) == 1 + 5


def test_export_und_reimport_ergeben_denselben_bestand(repository):
    csv = BestandExportieren(repository).ausfuehren()

    neu = InMemoryHundRepository()
    ergebnis = NeuzugaengeImportieren(NeuzugangErfassen(neu, heute=lambda: HEUTE)).ausfuehren(csv)

    assert ergebnis.fehler == []

    def schluessel(h):
        return (h.name, h.aufnahmedatum, h.herkunft, h.chipnummer)

    assert sorted(map(schluessel, neu.alle())) == sorted(map(schluessel, repository.alle()))
