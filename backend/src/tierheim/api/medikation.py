"""Router /medikation – Tagesliste für das Pflegepersonal."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from tierheim.api.schemas import FaelligeGabeResponse
from tierheim.application.heute_faellig import HeuteFaellig

router = APIRouter(prefix="/medikation", tags=["Medikation"])


def _heute_faellig(request: Request) -> HeuteFaellig:
    return HeuteFaellig(request.app.state.repository, request.app.state.heute)


@router.get("/heute", summary="Tagesliste: heute fällige Medikamente")
def heute_faellig(
    use_case: Annotated[HeuteFaellig, Depends(_heute_faellig)],
) -> list[FaelligeGabeResponse]:
    return [FaelligeGabeResponse.aus_gabe(gabe) for gabe in use_case.ausfuehren()]
