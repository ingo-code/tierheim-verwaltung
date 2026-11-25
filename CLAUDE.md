# Tierheim-Verwaltung – Lern- und Demo-Projekt

Verwaltungssoftware für Tierheime: Neuzugänge und Bestandshunde erfassen, Chipnummer und Medikation
immer im Blick. Ziel ist ein **Python-Lern- und Portfolio-Projekt** (Schwerpunkt
Python, APIs und Daten). Der Nutzer lernt Python. Erkläre deshalb jeden Schritt kurz und lass ihn
selbst tippen, wenn er das möchte.

## Struktur (3 Teilprojekte in einem Repo)
- `backend/`: Python 3.13, FastAPI, Pydantic, SQLAlchemy, pytest. Paketverwaltung mit **uv**.
- `frontend/`: Next.js (TypeScript). Spricht nur über die REST-API mit dem Backend.
- `docs/`: Fachlichkeit, Lernplan, Architektur-Entscheidungen (ADR). Kontext für Mensch und Agent.

## Befehle
- Tests: `cd backend && uv run pytest`
- Abhängigkeit hinzufügen: `uv add <paket>` bzw. `uv add --dev <paket>`
- API starten (SQLite, Auto-Reload): `cd backend && uv run uvicorn tierheim.server:erzeuge_app --factory --reload`
  → http://127.0.0.1:8000/docs · Datenbank: `TIERHEIM_DB_URL` (Standard `sqlite:///tierheim.db`)

## Arbeitsweise: TDD, streng
1. **Rot:** Zuerst ein Test, der das gewünschte Verhalten beschreibt. Ausführen und zusehen, wie er fehlschlägt.
2. **Grün:** Nur so viel Code schreiben, dass der Test grün wird.
3. **Refactor:** Aufräumen, wobei die Tests grün bleiben.
4. **Commit** nur bei grünen Tests. Jedes Feature beginnt mit einem grünen Stand.
- Ein Feature = ein kleiner Schritt. Kein Code ohne Test, der ihn verlangt.
- Der Agent schlägt zuerst den Test vor und wartet auf die Freigabe, erst dann kommt der Produktivcode.
- Testnamen auf Deutsch und als Satz, z. B. `test_chipnummer_mit_14_ziffern_wird_abgelehnt`.

## Architektur: Clean Architecture
Abhängigkeiten zeigen nur nach innen: `api → application → domain`, `infrastructure → application → domain`.
- `domain/`: Entitäten und Regeln (Hund, Chipnummer, Medikation). **Reines Python**, ohne FastAPI und ohne Datenbank.
- `application/`: Use Cases (z. B. `NeuzugangErfassen`) und Schnittstellen (Ports) wie `HundRepository` als `Protocol`.
- `infrastructure/`: Umsetzungen der Ports (In-Memory, SQLite mit SQLAlchemy). Tabellenklassen getrennt von der Domain.
  Neue Repository-Umsetzungen müssen die Vertragstests in `tests/unit/test_hund_repository.py` bestehen.
- `server.py`: Produktions-Startpunkt (echte DB, echtes Datum). Tests nutzen `create_app(...)` direkt.
- `api/`: FastAPI-Router, Request/Response-Schemas (Pydantic) und die Verdrahtung (Dependency Injection).
- Unit-Tests (`tests/unit/`) testen domain und application ohne I/O. Integrationstests (`tests/integration/`) testen API und Datenbank.

## Clean Code
- Fachbegriffe auf Deutsch, wie im Tierheim (Hund, Neuzugang, Chipnummer, Medikation). Technik-Begriffe auf Englisch (repository, router).
- Kleine Funktionen, sprechende Namen, Type Hints überall, keine magischen Zahlen.
- Wertobjekte für Regeln (z. B. `Chipnummer` validiert sich selbst) statt verstreuter `if`-Prüfungen.

## Fachlichkeit
Siehe `docs/fachlichkeit.md`. Lernfortschritt: `docs/lernplan.md`.
