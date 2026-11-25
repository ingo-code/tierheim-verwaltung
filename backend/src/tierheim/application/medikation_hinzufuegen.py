"""Use Case: Einem Hund ein Medikament verordnen."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from tierheim.application.hund_anzeigen import HundNichtGefunden
from tierheim.application.ports import HundRepository
from tierheim.domain.medikation import TAEGLICH, Medikation


@dataclass(frozen=True)
class MedikationDaten:
    medikament: str
    dosis: str
    startdatum: date
    enddatum: date | None = None
    intervall_tage: int = TAEGLICH


class MedikationHinzufuegen:
    def __init__(self, repository: HundRepository) -> None:
        self._repository = repository

    def ausfuehren(self, hund_id: UUID, daten: MedikationDaten) -> Medikation:
        hund = self._repository.finde_per_id(hund_id)
        if hund is None:
            raise HundNichtGefunden(hund_id)

        medikation = Medikation(
            medikament=daten.medikament,
            dosis=daten.dosis,
            startdatum=daten.startdatum,
            enddatum=daten.enddatum,
            intervall_tage=daten.intervall_tage,
        )
        hund.medikation_hinzufuegen(medikation)
        self._repository.speichern(hund)
        return medikation
