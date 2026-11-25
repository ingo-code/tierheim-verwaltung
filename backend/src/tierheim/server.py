"""Produktions-Startpunkt: echte SQLite-Datenbank, echtes Datum.

Start (im Ordner backend/):
    uv run uvicorn tierheim.server:erzeuge_app --factory --reload
→ http://127.0.0.1:8000/docs

Datenbank: Umgebungsvariable TIERHEIM_DB_URL, Standard `sqlite:///tierheim.db`.
Eine Fabrikfunktion statt `app = ...` auf Modulebene: So legt das bloße Importieren
(z. B. in Tests) keine Datenbankdatei an.
"""

import os

from fastapi import FastAPI

from tierheim.api.main import create_app
from tierheim.infrastructure.sqlite_hund_repository import SqliteHundRepository

STANDARD_DB_URL = "sqlite:///tierheim.db"


def erzeuge_app() -> FastAPI:
    db_url = os.environ.get("TIERHEIM_DB_URL", STANDARD_DB_URL)
    return create_app(repository=SqliteHundRepository.fuer_url(db_url))
