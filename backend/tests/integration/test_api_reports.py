"""Integrationstests: CSV-Upload, Bestandsreport und CSV-Export über HTTP."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from tierheim.api.main import create_app
from tierheim.infrastructure.in_memory_hund_repository import InMemoryHundRepository

HEUTE = date(2026, 11, 25)
CSV = (
    "Name;Geschlecht;Herkunft;Aufnahmedatum;Rasse;Chipnummer\n"
    "Luna;Hündin;Abgabe;05.11.2026;Schäferhund-Mix;276098100123456\n"
    "Rex;Rüde;Fundtier;15.11.2026;;\n"
    "Kaputt;Kater;Fundtier;15.11.2026;;\n"
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(repository=InMemoryHundRepository(), heute=lambda: HEUTE))


def hochladen(client: TestClient, inhalt: bytes):
    return client.post(
        "/import/neuzugaenge", files={"datei": ("bestand.csv", inhalt, "text/csv")}
    )


def test_csv_upload_importiert_und_meldet_fehler(client):
    antwort = hochladen(client, CSV.encode("utf-8"))

    assert antwort.status_code == 200
    assert antwort.json()["importiert"] == 2
    assert antwort.json()["fehler"] == [
        {"zeile": 4, "grund": "Unbekanntes Geschlecht 'Kater' (erwartet Rüde oder Hündin)."}
    ]
    assert len(client.get("/hunde").json()) == 2


def test_csv_aus_excel_mit_bom_wird_gelesen(client):
    antwort = hochladen(client, CSV.encode("utf-8-sig"))

    assert antwort.json()["importiert"] == 2


def test_csv_in_windows_1252_wird_gelesen(client):
    antwort = hochladen(client, CSV.encode("cp1252"))

    assert antwort.json()["importiert"] == 2
    assert {h["name"] for h in client.get("/hunde").json()} == {"Luna", "Rex"}


def test_bestandsreport(client):
    hochladen(client, CSV.encode("utf-8"))

    report = client.get("/reports/bestand").json()

    assert report["anzahl_im_heim"] == 2
    assert report["nach_herkunft"] == {"abgabe": 1, "fundtier": 1}
    assert report["durchschnittliche_verweildauer_tage"] == 15.0  # (20 + 10) / 2
    assert report["langzeit"][0] == {"name": "Luna", "tage": 20}
    assert report["ohne_chip"] == ["Rex"]


def test_csv_export_als_download_fuer_excel(client):
    hochladen(client, CSV.encode("utf-8"))

    antwort = client.get("/export/bestand.csv")

    assert antwort.status_code == 200
    assert antwort.headers["content-type"].startswith("text/csv")
    assert "attachment" in antwort.headers["content-disposition"]
    assert antwort.content.startswith("﻿".encode("utf-8"))  # BOM, damit Excel Umlaute erkennt
    assert "Luna;Hündin;Abgabe;05.11.2026" in antwort.content.decode("utf-8-sig")
