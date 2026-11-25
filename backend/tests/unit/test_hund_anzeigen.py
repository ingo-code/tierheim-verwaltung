from datetime import date
from uuid import uuid4

import pytest

from tierheim.application.hund_anzeigen import HundAnzeigen, HundNichtGefunden
from tierheim.domain.hund import Geschlecht, Herkunft, Hund
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository


def test_vorhandener_hund_wird_angezeigt():
    repository = InMemoryHundRepository()
    bello = Hund(
        name="Bello",
        geschlecht=Geschlecht.RUEDE,
        aufnahmedatum=date(2026, 11, 20),
        herkunft=Herkunft.FUNDTIER,
    )
    repository.speichern(bello)

    assert HundAnzeigen(repository).ausfuehren(bello.id) == bello


def test_unbekannter_hund_loest_hund_nicht_gefunden_aus():
    with pytest.raises(HundNichtGefunden):
        HundAnzeigen(InMemoryHundRepository()).ausfuehren(uuid4())
