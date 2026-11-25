"""Use Case: Den aktuellen Hundebestand auflisten – neueste Aufnahmen zuerst."""

from tierheim.application.ports import HundRepository
from tierheim.domain.hund import Hund


class BestandAuflisten:
    def __init__(self, repository: HundRepository) -> None:
        self._repository = repository

    def ausfuehren(self) -> list[Hund]:
        return sorted(
            self._repository.alle(),
            key=lambda hund: hund.aufnahmedatum,
            reverse=True,
        )
