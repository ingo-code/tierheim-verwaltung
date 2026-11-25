"""Use Case: Einen Hund als Neuzugang im Tierheim erfassen."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from tierheim.application.ports import HundRepository
from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, UngueltigerHund


class ChipnummerBereitsVergeben(Exception):
    """Die Chipnummer gehört schon zu einem Hund im Bestand."""

    def __init__(self, chipnummer: Chipnummer, vorhandener_hund: Hund) -> None:
        super().__init__(
            f"Chipnummer {chipnummer.wert} ist bereits {vorhandener_hund.name} zugeordnet."
        )
        self.vorhandener_hund = vorhandener_hund


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

        chipnummer = Chipnummer.aus_eingabe(daten.chipnummer) if daten.chipnummer else None
        if chipnummer is not None:
            self._pruefe_chip_ist_frei(chipnummer)

        hund = Hund(
            name=daten.name,
            geschlecht=daten.geschlecht,
            herkunft=daten.herkunft,
            aufnahmedatum=daten.aufnahmedatum,
            rasse=daten.rasse,
            chipnummer=chipnummer,
        )
        self._repository.speichern(hund)
        return hund

    def _pruefe_chip_ist_frei(self, chipnummer: Chipnummer) -> None:
        vorhandener_hund = self._repository.finde_per_chip(chipnummer)
        if vorhandener_hund is not None:
            raise ChipnummerBereitsVergeben(chipnummer, vorhandener_hund)
