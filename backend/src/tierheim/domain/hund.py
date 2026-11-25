"""Entität Hund – ein Tier im Bestand des Tierheims."""

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from tierheim.domain.chipnummer import Chipnummer


class UngueltigerHund(ValueError):
    """Wird ausgelöst, wenn ein Hund gegen eine Fachregel verstößt."""


class Geschlecht(StrEnum):
    RUEDE = "ruede"
    HUENDIN = "huendin"


class Herkunft(StrEnum):
    FUNDTIER = "fundtier"
    ABGABE = "abgabe"
    BESCHLAGNAHME = "beschlagnahme"


class Status(StrEnum):
    AUFGENOMMEN = "aufgenommen"
    VERMITTELBAR = "vermittelbar"
    RESERVIERT = "reserviert"
    VERMITTELT = "vermittelt"


@dataclass
class Hund:
    """Entität: Ein Hund hat eine eigene Identität (id), seine Daten dürfen sich ändern."""

    name: str
    geschlecht: Geschlecht
    aufnahmedatum: date
    herkunft: Herkunft
    rasse: str | None = None
    chipnummer: Chipnummer | None = None
    status: Status = Status.AUFGENOMMEN
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise UngueltigerHund("Ein Hund braucht einen Namen.")

    def chip_nachtragen(self, chipnummer: Chipnummer) -> None:
        """Für Hunde, die ohne Chip ankommen. Ein vorhandener Chip bleibt unangetastet."""
        if self.chipnummer is not None:
            raise UngueltigerHund(
                f"{self.name} hat bereits die Chipnummer {self.chipnummer.wert}."
            )
        self.chipnummer = chipnummer
