"""Ports: Schnittstellen, die die Anwendung braucht, aber nicht selbst umsetzt.

Die Umsetzung (In-Memory, SQLite, ...) liegt in `infrastructure/`. So hängt die
Anwendung nie von einer Datenbank ab – nur die Datenbank von der Anwendung.
"""

from typing import Protocol

from tierheim.domain.hund import Hund


class HundRepository(Protocol):
    def speichern(self, hund: Hund) -> None: ...
