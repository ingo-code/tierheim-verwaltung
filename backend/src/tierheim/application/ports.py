"""Ports: Schnittstellen, die die Anwendung braucht, aber nicht selbst umsetzt.

Die Umsetzung (In-Memory, SQLite, ...) liegt in `infrastructure/`. So hängt die
Anwendung nie von einer Datenbank ab – nur die Datenbank von der Anwendung.
"""

from typing import Protocol
from uuid import UUID

from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Hund


class HundRepository(Protocol):
    def speichern(self, hund: Hund) -> None:
        """Legt einen Hund an oder aktualisiert ihn (gleiche id)."""
        ...

    def finde_per_id(self, hund_id: UUID) -> Hund | None: ...

    def finde_per_chip(self, chipnummer: Chipnummer) -> Hund | None: ...

    def alle(self) -> list[Hund]: ...
