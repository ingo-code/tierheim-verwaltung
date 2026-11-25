"""HundRepository im Arbeitsspeicher – für Tests und den ersten API-Prototyp."""

from uuid import UUID

from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Hund


class InMemoryHundRepository:
    def __init__(self) -> None:
        self._hunde: dict[UUID, Hund] = {}

    def speichern(self, hund: Hund) -> None:
        self._hunde[hund.id] = hund

    def finde_per_id(self, hund_id: UUID) -> Hund | None:
        return self._hunde.get(hund_id)

    def finde_per_chip(self, chipnummer: Chipnummer) -> Hund | None:
        return next(
            (hund for hund in self._hunde.values() if hund.chipnummer == chipnummer),
            None,
        )

    def alle(self) -> list[Hund]:
        return list(self._hunde.values())
