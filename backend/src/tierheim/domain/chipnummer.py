from dataclasses import dataclass

LAENGE = 15


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
