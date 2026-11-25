from datetime import date

from tierheim.application.bestand_auflisten import BestandAuflisten
from tierheim.domain.hund import Geschlecht, Herkunft, Hund
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository


def hund(name: str, aufnahmedatum: date) -> Hund:
    return Hund(
        name=name,
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=aufnahmedatum,
        herkunft=Herkunft.FUNDTIER,
    )


def test_leerer_bestand_liefert_leere_liste():
    assert BestandAuflisten(InMemoryHundRepository()).ausfuehren() == []


def test_neueste_aufnahmen_stehen_oben():
    repository = InMemoryHundRepository()
    alt = hund("Alt", date(2026, 1, 10))
    neu = hund("Neu", date(2026, 11, 20))
    mitte = hund("Mitte", date(2026, 6, 1))
    for h in (alt, neu, mitte):
        repository.speichern(h)

    assert BestandAuflisten(repository).ausfuehren() == [neu, mitte, alt]
