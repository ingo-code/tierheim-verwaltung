"""Pydantic-Schemas: Was über HTTP rein- und rausgeht (≈ Zod-Schemas in TypeScript).

Bewusst getrennt von den Domain-Klassen: Die API darf sich ändern (Feldnamen,
Formate), ohne dass die Fachlogik angefasst werden muss.
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from tierheim.application.heute_faellig import FaelligeGabe
from tierheim.application.medikation_hinzufuegen import MedikationDaten
from tierheim.application.neuzugang_erfassen import NeuzugangDaten
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status
from tierheim.domain.medikation import TAEGLICH, Medikation


class NeuzugangRequest(BaseModel):
    name: str = Field(min_length=1, examples=["Luna"])
    geschlecht: Geschlecht
    herkunft: Herkunft
    aufnahmedatum: date
    rasse: str | None = Field(default=None, examples=["Schäferhund-Mix"])
    chipnummer: str | None = Field(default=None, examples=["276 098 100 123 456"])

    def als_daten(self) -> NeuzugangDaten:
        return NeuzugangDaten(**self.model_dump())


class MedikationRequest(BaseModel):
    medikament: str = Field(min_length=1, examples=["Metacam"])
    dosis: str = Field(min_length=1, examples=["1,5 ml"])
    startdatum: date
    enddatum: date | None = None
    intervall_tage: int = Field(default=TAEGLICH, ge=1, description="1 = täglich, 7 = wöchentlich")

    def als_daten(self) -> MedikationDaten:
        return MedikationDaten(**self.model_dump())


class MedikationResponse(BaseModel):
    id: UUID
    medikament: str
    dosis: str
    startdatum: date
    enddatum: date | None
    intervall_tage: int

    @classmethod
    def aus_medikation(cls, medikation: Medikation) -> "MedikationResponse":
        return cls(
            id=medikation.id,
            medikament=medikation.medikament,
            dosis=medikation.dosis,
            startdatum=medikation.startdatum,
            enddatum=medikation.enddatum,
            intervall_tage=medikation.intervall_tage,
        )


class HundResponse(BaseModel):
    id: UUID
    name: str
    geschlecht: Geschlecht
    herkunft: Herkunft
    aufnahmedatum: date
    rasse: str | None
    chipnummer: str | None
    status: Status
    medikationen: list[MedikationResponse]

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
            medikationen=[MedikationResponse.aus_medikation(m) for m in hund.medikationen],
        )


class FaelligeGabeResponse(BaseModel):
    """Eine Zeile der Tagesliste – flach, damit das Frontend sie direkt anzeigen kann."""

    hund_id: UUID
    hund_name: str
    chipnummer: str | None
    medikation_id: UUID
    medikament: str
    dosis: str

    @classmethod
    def aus_gabe(cls, gabe: FaelligeGabe) -> "FaelligeGabeResponse":
        return cls(
            hund_id=gabe.hund.id,
            hund_name=gabe.hund.name,
            chipnummer=gabe.hund.chipnummer.wert if gabe.hund.chipnummer else None,
            medikation_id=gabe.medikation.id,
            medikament=gabe.medikation.medikament,
            dosis=gabe.medikation.dosis,
        )
