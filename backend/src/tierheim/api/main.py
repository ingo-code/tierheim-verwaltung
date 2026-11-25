"""Einstiegspunkt der API – hier wird alles verdrahtet (Composition Root).

Start: `uv run fastapi dev src/tierheim/api/main.py` → http://127.0.0.1:8000/docs
"""

from collections.abc import Callable
from datetime import date

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from tierheim.api import hunde, medikation
from tierheim.application.hund_anzeigen import HundNichtGefunden
from tierheim.application.neuzugang_erfassen import ChipnummerBereitsVergeben
from tierheim.application.ports import HundRepository
from tierheim.domain.chipnummer import UngueltigeChipnummer
from tierheim.domain.hund import UngueltigerHund
from tierheim.domain.medikation import UngueltigeMedikation
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository


def create_app(
    repository: HundRepository | None = None,
    heute: Callable[[], date] = date.today,
) -> FastAPI:
    app = FastAPI(
        title="Tierheim-Verwaltung",
        description="Neuzugänge und Bestandshunde – mit Chipnummer und Medikation.",
        version="0.1.0",
    )
    app.state.repository = repository if repository is not None else InMemoryHundRepository()
    app.state.heute = heute
    app.include_router(hunde.router)
    app.include_router(medikation.router)
    _fehler_uebersetzen(app)
    return app


def _fehler_uebersetzen(app: FastAPI) -> None:
    """Fachliche Fehler → HTTP-Statuscodes. Die Domain kennt kein HTTP, nur die API."""

    @app.exception_handler(UngueltigeChipnummer)
    @app.exception_handler(UngueltigerHund)
    @app.exception_handler(UngueltigeMedikation)
    def fachregel_verletzt(_: Request, fehler: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(fehler)},
        )

    @app.exception_handler(ChipnummerBereitsVergeben)
    def chip_vergeben(_: Request, fehler: ChipnummerBereitsVergeben) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(fehler),
                "vorhandener_hund_id": str(fehler.vorhandener_hund.id),
            },
        )

    @app.exception_handler(HundNichtGefunden)
    def nicht_gefunden(_: Request, fehler: HundNichtGefunden) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(fehler)},
        )


app = create_app()
