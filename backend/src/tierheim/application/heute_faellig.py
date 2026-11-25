"""Use Case: Tagesliste – welcher Hund bekommt heute welches Medikament?"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from tierheim.application.ports import HundRepository
from tierheim.domain.hund import Hund
from tierheim.domain.medikation import Medikation


@dataclass(frozen=True)
class FaelligeGabe:
    hund: Hund
    medikation: Medikation


class HeuteFaellig:
    def __init__(self, repository: HundRepository, heute: Callable[[], date]) -> None:
        self._repository = repository
        self._heute = heute

    def ausfuehren(self) -> list[FaelligeGabe]:
        tag = self._heute()
        gaben = [
            FaelligeGabe(hund=hund, medikation=medikation)
            for hund in self._repository.alle()
            if hund.ist_im_heim
            for medikation in hund.faellige_medikationen(tag)
        ]
        return sorted(gaben, key=lambda g: (g.hund.name, g.medikation.medikament))
