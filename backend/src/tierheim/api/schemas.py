"""Pydantic-Schemas: Was über HTTP rein- und rausgeht (≈ Zod-Schemas in TypeScript).

Bewusst getrennt von den Domain-Klassen: Die API darf sich ändern (Feldnamen,
Formate), ohne dass die Fachlogik angefasst werden muss.
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from tierheim.application.neuzugang_erfassen import NeuzugangDaten
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status


class NeuzugangRequest(BaseModel):
    name: str = Field(min_length=1, examples=["Luna"])
    geschlecht: Geschlecht
    herkunft: Herkunft
    aufnahmedatum: date
    rasse: str | None = Field(default=None, examples=["Schäferhund-Mix"])
    chipnummer: str | None = Field(default=None, examples=["276 098 100 123 456"])

    def als_daten(self) -> NeuzugangDaten:
        return NeuzugangDaten(**self.model_dump())


class HundResponse(BaseModel):
    id: UUID
    name: str
    geschlecht: Geschlecht
    herkunft: Herkunft
    aufnahmedatum: date
    rasse: str | None
    chipnummer: str | None
    status: Status

    @classmethod
    def aus_hund(cls, hund: Hund) -> "HundResponse":
        return cls(
            id=hund.id,
            name=hund.name,
            geschlecht=hund.geschlecht,
            herkunft=hund.herkunft,
            aufnahmedatum=hund.aufnahmedatum,
            rasse=hund.rasse,
            chipnummer=hund.chipnummer.wert if hund.chipnummer else None,
            status=hund.status,
        )
