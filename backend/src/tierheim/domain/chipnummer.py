"""Wertobjekt Chipnummer (Transponder nach ISO 11784/11785).

Regeln:
- genau 15 Ziffern
- die ersten 3 Ziffern sind ein Ländercode (001–899, z. B. 276 = Deutschland)
  oder ein Herstellercode (900–999); 000 ist ungültig
"""

from dataclasses import dataclass
from typing import Self

LAENGE = 15
UNGUELTIGER_CODE = "000"


class UngueltigeChipnummer(ValueError):
    """Wird ausgelöst, wenn eine Chipnummer nicht der ISO-Norm entspricht."""


@dataclass(frozen=True)
class Chipnummer:
    """Wertobjekt: Eine Chipnummer ist immer gültig, sonst gibt es sie gar nicht."""

    wert: str

    def __post_init__(self) -> None:
        if len(self.wert) != LAENGE:
            raise UngueltigeChipnummer(
                f"Chipnummer muss {LAENGE} Ziffern haben, hat aber {len(self.wert)}."
            )
        if not self.wert.isdigit():
            raise UngueltigeChipnummer("Chipnummer darf nur Ziffern enthalten.")
        if self.code == UNGUELTIGER_CODE:
            raise UngueltigeChipnummer("Länder-/Herstellercode 000 ist ungültig.")

    @classmethod
    def aus_eingabe(cls, text: str) -> Self:
        """Erzeugt eine Chipnummer aus einer Benutzereingabe, z. B. '276 098 100 123 456'."""
        return cls(text.replace(" ", "").strip())

    @property
    def code(self) -> str:
        """Die ersten 3 Ziffern: Länder- oder Herstellercode."""
        return self.wert[:3]
