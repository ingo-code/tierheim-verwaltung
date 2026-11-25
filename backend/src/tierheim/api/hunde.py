"""Router /hunde – dünn: HTTP übersetzen, Use Case aufrufen, Antwort formen. Keine Fachlogik."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from tierheim.api.schemas import HundResponse, NeuzugangRequest
from tierheim.application.bestand_auflisten import BestandAuflisten
from tierheim.application.hund_anzeigen import HundAnzeigen
from tierheim.application.neuzugang_erfassen import NeuzugangErfassen

router = APIRouter(prefix="/hunde", tags=["Hunde"])


# --- Dependencies: bauen die Use Cases aus dem, was create_app bereitgelegt hat ---


def _neuzugang_erfassen(request: Request) -> NeuzugangErfassen:
    return NeuzugangErfassen(request.app.state.repository, request.app.state.heute)


def _bestand_auflisten(request: Request) -> BestandAuflisten:
    return BestandAuflisten(request.app.state.repository)


def _hund_anzeigen(request: Request) -> HundAnzeigen:
    return HundAnzeigen(request.app.state.repository)


# --- Endpunkte ---------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED, summary="Neuzugang erfassen")
def neuzugang_anlegen(
    eingabe: NeuzugangRequest,
    use_case: Annotated[NeuzugangErfassen, Depends(_neuzugang_erfassen)],
) -> HundResponse:
    return HundResponse.aus_hund(use_case.ausfuehren(eingabe.als_daten()))


@router.get("", summary="Bestand auflisten (neueste zuerst)")
def bestand(
    use_case: Annotated[BestandAuflisten, Depends(_bestand_auflisten)],
) -> list[HundResponse]:
    return [HundResponse.aus_hund(hund) for hund in use_case.ausfuehren()]


@router.get("/{hund_id}", summary="Einzelnen Hund anzeigen")
def hund_anzeigen(
    hund_id: UUID,
    use_case: Annotated[HundAnzeigen, Depends(_hund_anzeigen)],
) -> HundResponse:
    return HundResponse.aus_hund(use_case.ausfuehren(hund_id))
