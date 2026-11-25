"""Router für Import, Reports und Export – Datei-Ein-/Ausgabe über HTTP."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from tierheim.application.bestandsreport import BestandExportieren, Bestandsreport
from tierheim.application.neuzugaenge_importieren import NeuzugaengeImportieren
from tierheim.application.neuzugang_erfassen import NeuzugangErfassen

router = APIRouter(tags=["Import & Reports"])

BOM = "﻿"  # Byte Order Mark: Excel erkennt daran UTF-8 (sonst kaputte Umlaute)


# --- Schemas ---------------------------------------------------------------------


class ImportFehlerResponse(BaseModel):
    zeile: int
    grund: str


class ImportErgebnisResponse(BaseModel):
    importiert: int
    fehler: list[ImportFehlerResponse]


class LangzeitResponse(BaseModel):
    name: str
    tage: int


class ReportResponse(BaseModel):
    anzahl_im_heim: int
    nach_status: dict[str, int]
    nach_herkunft: dict[str, int]
    durchschnittliche_verweildauer_tage: float | None
    langzeit: list[LangzeitResponse]
    ohne_chip: list[str]
    heute_faellige_gaben: int


# --- Dependencies ----------------------------------------------------------------


def _importieren(request: Request) -> NeuzugaengeImportieren:
    state = request.app.state
    return NeuzugaengeImportieren(NeuzugangErfassen(state.repository, state.heute))


def _bestandsreport(request: Request) -> Bestandsreport:
    return Bestandsreport(request.app.state.repository, request.app.state.heute)


def _exportieren(request: Request) -> BestandExportieren:
    return BestandExportieren(request.app.state.repository)


# --- Endpunkte -------------------------------------------------------------------


@router.post("/import/neuzugaenge", summary="Neuzugänge aus CSV importieren (Excel, ;)")
async def neuzugaenge_importieren(
    datei: UploadFile,
    use_case: Annotated[NeuzugaengeImportieren, Depends(_importieren)],
) -> ImportErgebnisResponse:
    ergebnis = use_case.ausfuehren(_als_text(await datei.read()))
    return ImportErgebnisResponse(**asdict(ergebnis))


@router.get("/reports/bestand", summary="Bestandsreport: Kennzahlen für die Heimleitung")
def bestandsreport(
    use_case: Annotated[Bestandsreport, Depends(_bestandsreport)],
) -> ReportResponse:
    return ReportResponse(**asdict(use_case.ausfuehren()))


@router.get("/export/bestand.csv", summary="Bestand als CSV für Excel herunterladen")
def bestand_exportieren(
    use_case: Annotated[BestandExportieren, Depends(_exportieren)],
) -> Response:
    return Response(
        content=(BOM + use_case.ausfuehren()).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="bestand.csv"'},
    )


def _als_text(inhalt: bytes) -> str:
    """UTF-8 (mit/ohne BOM) oder – wie bei „CSV (Trennzeichen-getrennt)“ aus Excel – Windows-1252."""
    try:
        return inhalt.decode("utf-8-sig")
    except UnicodeDecodeError:
        return inhalt.decode("cp1252")
