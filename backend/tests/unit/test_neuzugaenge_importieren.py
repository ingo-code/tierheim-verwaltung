from datetime import date

import pytest

from tierheim.application.neuzugaenge_importieren import NeuzugaengeImportieren
from tierheim.application.neuzugang_erfassen import NeuzugangErfassen
from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

HEUTE = date(2026, 11, 25)
KOPF = "Name;Geschlecht;Herkunft;Aufnahmedatum;Rasse;Chipnummer\n"


@pytest.fixture
def repository() -> InMemoryHundRepository:
    return InMemoryHundRepository()


@pytest.fixture
def importieren(repository) -> NeuzugaengeImportieren:
    return NeuzugaengeImportieren(NeuzugangErfassen(repository, heute=lambda: HEUTE))


def test_gueltige_zeilen_werden_importiert(importieren, repository):
    csv = KOPF + (
        "Luna;Hündin;Abgabe;20.11.2026;Schäferhund-Mix;276 098 100 123 456\n"
        "Rex;Rüde;Fundtier;01.10.2026;;\n"
    )

    ergebnis = importieren.ausfuehren(csv)

    assert ergebnis.importiert == 2
    assert ergebnis.fehler == []
    luna = repository.finde_per_chip(Chipnummer("276098100123456"))
    assert luna.name == "Luna"
    assert luna.geschlecht == Geschlecht.HUENDIN
    assert luna.herkunft == Herkunft.ABGABE
    assert luna.aufnahmedatum == date(2026, 11, 20)
    assert luna.rasse == "Schäferhund-Mix"


def test_leere_felder_werden_zu_none(importieren, repository):
    importieren.ausfuehren(KOPF + "Rex;Rüde;Fundtier;01.10.2026;;\n")

    rex = repository.alle()[0]
    assert rex.rasse is None
    assert rex.chipnummer is None


def test_chipnummer_mit_fuehrender_null_bleibt_text(importieren, repository):
    # Herstellercode-Chips sind 15 Ziffern – als Zahl gelesen ginge nichts verloren,
    # aber die Ländercodes 001–099 beginnen mit 0. pandas darf hier nicht rechnen.
    importieren.ausfuehren(KOPF + "Mia;Hündin;Abgabe;20.11.2026;;040098100123456\n")

    assert repository.alle()[0].chipnummer == Chipnummer("040098100123456")


def test_fehlerhafte_zeilen_werden_gemeldet_und_der_rest_importiert(importieren, repository):
    csv = KOPF + (
        "Luna;Hündin;Abgabe;20.11.2026;;276098100123456\n"  # Zeile 2: ok
        "Rex;Kater;Fundtier;01.10.2026;;\n"  # Zeile 3: Geschlecht falsch
        "Bello;Rüde;Fundtier;01.10.2026;;123\n"  # Zeile 4: Chip falsch
        "Mia;Hündin;Abgabe;31.02.2026;;\n"  # Zeile 5: Datum gibt es nicht
        "Rex2;Rüde;Abgabe;01.11.2026;;276098100123456\n"  # Zeile 6: Chip doppelt
    )

    ergebnis = importieren.ausfuehren(csv)

    assert ergebnis.importiert == 1
    assert [f.zeile for f in ergebnis.fehler] == [3, 4, 5, 6]
    assert "Kater" in ergebnis.fehler[0].grund
    assert "15 Ziffern" in ergebnis.fehler[1].grund
    assert "Luna" in ergebnis.fehler[3].grund
    assert [h.name for h in repository.alle()] == ["Luna"]


def test_fehlende_spalte_wird_als_fehler_gemeldet(importieren, repository):
    ergebnis = importieren.ausfuehren("Name;Geschlecht\nLuna;Hündin\n")

    assert ergebnis.importiert == 0
    assert ergebnis.fehler[0].zeile == 1
    assert "Herkunft" in ergebnis.fehler[0].grund
    assert repository.alle() == []
