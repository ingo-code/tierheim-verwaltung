"""Use Case: Einen Hund als Neuzugang im Tierheim erfassen."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from tierheim.application.ports import HundRepository
from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, UngueltigerHund


@dataclass(frozen=True)
class NeuzugangDaten:
    """Eingabe des Use Cases – so, wie sie vom Formular bzw. der API kommt."""

    name: str
    geschlecht: Geschlecht
    herkunft: Herkunft
    aufnahmedatum: date
    rasse: str | None = None
    chipnummer: str | None = None


class NeuzugangErfassen:
    def __init__(self, repository: HundRepository, heute: Callable[[], date]) -> None:
        self._repository = repository
        self._heute = heute

    def ausfuehren(self, daten: NeuzugangDaten) -> Hund:
        if daten.aufnahmedatum > self._heute():
            raise UngueltigerHund("Das Aufnahmedatum darf nicht in der Zukunft liegen.")

        hund = Hund(
            name=daten.name,
            geschlecht=daten.geschlecht,
            herkunft=daten.herkunft,
            aufnahmedatum=daten.aufnahmedatum,
            rasse=daten.rasse,
            chipnummer=Chipnummer.aus_eingabe(daten.chipnummer) if daten.chipnummer else None,
        )
        self._repository.speichern(hund)
        return hund
