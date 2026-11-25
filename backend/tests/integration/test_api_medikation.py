"""Integrationstests: Medikation über die API verordnen und die Tagesliste abrufen."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from tierheim.api.main import create_app
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

HEUTE = date(2026, 11, 25)


@pytest.fixture
def client() -> TestClient:
    app = create_app(repository=InMemoryHundRepository(), heute=lambda: HEUTE)
    return TestClient(app)


def hund_anlegen(client: TestClient, name: str = "Luna", chipnummer: str | None = None) -> dict:
    antwort = client.post(
        "/hunde",
        json={
            "name": name,
            "geschlecht": "huendin",
            "herkunft": "abgabe",
            "aufnahmedatum": "2026-11-20",
            "chipnummer": chipnummer,
        },
    )
    assert antwort.status_code == 201
    return antwort.json()


def verordnen(client: TestClient, hund_id: str, **abweichungen):
    daten = {"medikament": "Metacam", "dosis": "1,5 ml", "startdatum": "2026-11-25"}
    daten.update(abweichungen)
    return client.post(f"/hunde/{hund_id}/medikationen", json=daten)


# --- POST /hunde/{id}/medikationen ---------------------------------------------


def test_medikation_verordnen_liefert_201(client):
    luna = hund_anlegen(client)

    antwort = verordnen(client, luna["id"])

    assert antwort.status_code == 201
    medikation = antwort.json()
    assert medikation["medikament"] == "Metacam"
    assert medikation["intervall_tage"] == 1
    assert medikation["id"]


def test_medikation_erscheint_beim_hund(client):
    luna = hund_anlegen(client)
    verordnen(client, luna["id"])

    hund = client.get(f"/hunde/{luna['id']}").json()

    assert [m["medikament"] for m in hund["medikationen"]] == ["Metacam"]


def test_medikation_fuer_unbekannten_hund_liefert_404(client):
    antwort = verordnen(client, "00000000-0000-0000-0000-000000000000")

    assert antwort.status_code == 404


def test_enddatum_vor_start_liefert_422_mit_klartext(client):
    luna = hund_anlegen(client)

    antwort = verordnen(client, luna["id"], enddatum="2026-11-01")

    assert antwort.status_code == 422
    assert "Enddatum" in antwort.json()["detail"]


# --- GET /medikation/heute -----------------------------------------------------


def test_tagesliste_ist_ohne_medikation_leer(client):
    hund_anlegen(client)

    antwort = client.get("/medikation/heute")

    assert antwort.status_code == 200
    assert antwort.json() == []


def test_tagesliste_zeigt_hund_chip_und_medikament(client):
    luna = hund_anlegen(client, chipnummer="276098100123456")
    verordnen(client, luna["id"], medikament="Metacam", dosis="1,5 ml")
    verordnen(client, luna["id"], medikament="Wurmkur", startdatum="2026-11-26")  # erst morgen

    tagesliste = client.get("/medikation/heute").json()

    assert tagesliste == [
        {
            "hund_id": luna["id"],
            "hund_name": "Luna",
            "chipnummer": "276098100123456",
            "medikation_id": tagesliste[0]["medikation_id"],
            "medikament": "Metacam",
            "dosis": "1,5 ml",
        }
    ]
