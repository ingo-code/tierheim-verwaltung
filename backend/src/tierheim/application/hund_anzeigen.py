"""Use Case: Einen einzelnen Hund anhand seiner id anzeigen."""

from uuid import UUID

from tierheim.application.ports import HundRepository
from tierheim.domain.hund import Hund


class HundNichtGefunden(Exception):
    def __init__(self, hund_id: UUID) -> None:
        super().__init__(f"Kein Hund mit der id {hund_id} im Bestand.")


class HundAnzeigen:
    def __init__(self, repository: HundRepository) -> None:
        self._repository = repository

    def ausfuehren(self, hund_id: UUID) -> Hund:
        hund = self._repository.finde_per_id(hund_id)
        if hund is None:
            raise HundNichtGefunden(hund_id)
        return hund
