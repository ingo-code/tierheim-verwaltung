"""Wertobjekt Medikation – ein Medikament mit Dosis, Zeitraum und Intervall."""

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

TAEGLICH = 1


class UngueltigeMedikation(ValueError):
    """Wird ausgelöst, wenn eine Medikation gegen eine Fachregel verstößt."""


@dataclass(frozen=True)
class Medikation:
    medikament: str
    dosis: str
    startdatum: date
    enddatum: date | None = None
    intervall_tage: int = TAEGLICH
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.medikament.strip():
            raise UngueltigeMedikation("Medikament fehlt.")
        if not self.dosis.strip():
            raise UngueltigeMedikation("Dosis fehlt.")
        if self.intervall_tage < 1:
            raise UngueltigeMedikation("Intervall muss mindestens 1 Tag sein.")
        if self.enddatum is not None and self.enddatum < self.startdatum:
            raise UngueltigeMedikation("Enddatum liegt vor dem Startdatum.")

    def ist_faellig_am(self, tag: date) -> bool:
        if tag < self.startdatum:
            return False
        if self.enddatum is not None and tag > self.enddatum:
            return False
        tage_seit_start = (tag - self.startdatum).days
        return tage_seit_start % self.intervall_tage == 0
