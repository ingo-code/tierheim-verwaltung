"""Integrationstests: HTTP → Pydantic → Use Case → Repository und zurück."""

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


def neuzugang(**abweichungen) -> dict:
    daten = {
        "name": "Luna",
        "geschlecht": "huendin",
        "herkunft": "abgabe",
        "aufnahmedatum": "2026-11-25",
    }
    daten.update(abweichungen)
    return daten


# --- POST /hunde ---------------------------------------------------------


def test_neuzugang_anlegen_liefert_201_und_den_hund(client):
    antwort = client.post("/hunde", json=neuzugang(chipnummer="276 098 100 123 456"))

    assert antwort.status_code == 201
    hund = antwort.json()
    assert hund["name"] == "Luna"
    assert hund["status"] == "aufgenommen"
    assert hund["chipnummer"] == "276098100123456"
    assert hund["id"]


def test_ungueltige_chipnummer_liefert_422_mit_klartext(client):
    antwort = client.post("/hunde", json=neuzugang(chipnummer="123"))

    assert antwort.status_code == 422
    assert "15 Ziffern" in antwort.json()["detail"]


def test_aufnahmedatum_in_der_zukunft_liefert_422(client):
    antwort = client.post("/hunde", json=neuzugang(aufnahmedatum="2026-11-26"))

    assert antwort.status_code == 422


def test_unbekanntes_geschlecht_liefert_422(client):
    antwort = client.post("/hunde", json=neuzugang(geschlecht="kater"))

    assert antwort.status_code == 422


def test_fehlender_name_liefert_422(client):
    daten = neuzugang()
    del daten["name"]

    assert client.post("/hunde", json=daten).status_code == 422


def test_doppelte_chipnummer_liefert_409_mit_vorhandenem_hund(client):
    luna = client.post("/hunde", json=neuzugang(chipnummer="276098100123456")).json()

    antwort = client.post("/hunde", json=neuzugang(name="Rex", chipnummer="276098100123456"))

    assert antwort.status_code == 409
    assert "Luna" in antwort.json()["detail"]
    assert antwort.json()["vorhandener_hund_id"] == luna["id"]


# --- GET /hunde ----------------------------------------------------------


def test_leerer_bestand_liefert_leere_liste(client):
    antwort = client.get("/hunde")

    assert antwort.status_code == 200
    assert antwort.json() == []


def test_bestand_enthaelt_neuzugaenge_neueste_zuerst(client):
    client.post("/hunde", json=neuzugang(name="Alt", aufnahmedatum="2026-01-10"))
    client.post("/hunde", json=neuzugang(name="Neu", aufnahmedatum="2026-11-20"))

    namen = [hund["name"] for hund in client.get("/hunde").json()]

    assert namen == ["Neu", "Alt"]


# --- GET /hunde/{id} -----------------------------------------------------


def test_einzelner_hund_per_id(client):
    luna = client.post("/hunde", json=neuzugang()).json()

    antwort = client.get(f"/hunde/{luna['id']}")

    assert antwort.status_code == 200
    assert antwort.json() == luna


def test_unbekannte_id_liefert_404(client):
    antwort = client.get("/hunde/00000000-0000-0000-0000-000000000000")

    assert antwort.status_code == 404
