"""Die Daten überleben einen Neustart der API (zwei App-Instanzen, eine Datenbankdatei)."""

from datetime import date

from fastapi.testclient import TestClient

from tierheim.api.main import create_app
from tierheim.infrastructure.sqlite_hund_repository import SqliteHundRepository

HEUTE = date(2026, 11, 25)


def starte_api(db_url: str) -> TestClient:
    return TestClient(create_app(SqliteHundRepository.fuer_url(db_url), heute=lambda: HEUTE))


def test_hund_und_medikation_ueberleben_einen_neustart(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'tierheim.db'}"

    vorher = starte_api(db_url)
    luna = vorher.post(
        "/hunde",
        json={
            "name": "Luna",
            "geschlecht": "huendin",
            "herkunft": "abgabe",
            "aufnahmedatum": "2026-11-20",
            "chipnummer": "276098100123456",
        },
    ).json()
    vorher.post(
        f"/hunde/{luna['id']}/medikationen",
        json={"medikament": "Metacam", "dosis": "1,5 ml", "startdatum": "2026-11-25"},
    )

    nachher = starte_api(db_url)  # „Neustart“: neue App, gleiche Datei

    assert nachher.get(f"/hunde/{luna['id']}").json()["name"] == "Luna"
    assert [g["hund_name"] for g in nachher.get("/medikation/heute").json()] == ["Luna"]


def test_doppelte_chipnummer_wird_auch_nach_neustart_erkannt(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'tierheim.db'}"
    hund = {
        "name": "Luna",
        "geschlecht": "huendin",
        "herkunft": "abgabe",
        "aufnahmedatum": "2026-11-20",
        "chipnummer": "276098100123456",
    }
    starte_api(db_url).post("/hunde", json=hund)

    antwort = starte_api(db_url).post("/hunde", json={**hund, "name": "Rex"})

    assert antwort.status_code == 409


def test_server_startpunkt_nutzt_sqlite_aus_umgebungsvariable(tmp_path, monkeypatch):
    db_datei = tmp_path / "aus_env.db"
    monkeypatch.setenv("TIERHEIM_DB_URL", f"sqlite:///{db_datei}")

    from tierheim.server import erzeuge_app

    erzeuge_app()

    assert db_datei.exists()
