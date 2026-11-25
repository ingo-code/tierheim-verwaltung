"""Use Case: Neuzugänge aus einer CSV-Datei importieren (z. B. aus einer alten Excel-Liste).

Format wie aus deutschem Excel: Trennzeichen `;`, Datum `TT.MM.JJJJ`,
Werte wie „Rüde“/„Hündin“, „Fundtier“/„Abgabe“/„Beschlagnahme“.
Fehlerhafte Zeilen werden übersprungen und mit Zeilennummer gemeldet.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from io import StringIO

import pandas as pd

from tierheim.application.neuzugang_erfassen import (
    ChipnummerBereitsVergeben,
    NeuzugangDaten,
    NeuzugangErfassen,
)
from tierheim.domain.hund import Geschlecht, Herkunft

PFLICHTSPALTEN = ["Name", "Geschlecht", "Herkunft", "Aufnahmedatum"]
DATUMSFORMAT = "%d.%m.%Y"
ERSTE_DATENZEILE = 2  # Zeile 1 ist die Kopfzeile

GESCHLECHT_AUS_TEXT = {
    "rüde": Geschlecht.RUEDE,
    "ruede": Geschlecht.RUEDE,
    "hündin": Geschlecht.HUENDIN,
    "huendin": Geschlecht.HUENDIN,
}


@dataclass(frozen=True)
class ImportFehler:
    zeile: int
    grund: str


@dataclass
class ImportErgebnis:
    importiert: int = 0
    fehler: list[ImportFehler] = field(default_factory=list)


class NeuzugaengeImportieren:
    def __init__(self, neuzugang_erfassen: NeuzugangErfassen) -> None:
        self._neuzugang_erfassen = neuzugang_erfassen

    def ausfuehren(self, csv_text: str) -> ImportErgebnis:
        # dtype=str: pandas soll nichts „erraten“ – sonst wird die Chipnummer zur Zahl.
        # keep_default_na=False: leere Felder bleiben "" statt NaN.
        tabelle = pd.read_csv(
            StringIO(csv_text.lstrip("﻿")), sep=";", dtype=str, keep_default_na=False
        )

        fehlende = [spalte for spalte in PFLICHTSPALTEN if spalte not in tabelle.columns]
        if fehlende:
            return ImportErgebnis(
                fehler=[ImportFehler(zeile=1, grund=f"Spalte fehlt: {', '.join(fehlende)}")]
            )

        ergebnis = ImportErgebnis()
        for position, zeile in enumerate(tabelle.to_dict("records")):
            try:
                self._neuzugang_erfassen.ausfuehren(_zu_daten(zeile))
                ergebnis.importiert += 1
            except (ValueError, ChipnummerBereitsVergeben) as fehler:
                ergebnis.fehler.append(
                    ImportFehler(zeile=position + ERSTE_DATENZEILE, grund=str(fehler))
                )
        return ergebnis


def _zu_daten(zeile: dict[str, str]) -> NeuzugangDaten:
    return NeuzugangDaten(
        name=zeile["Name"],
        geschlecht=_geschlecht(zeile["Geschlecht"]),
        herkunft=_herkunft(zeile["Herkunft"]),
        aufnahmedatum=_datum(zeile["Aufnahmedatum"]),
        rasse=zeile.get("Rasse") or None,
        chipnummer=zeile.get("Chipnummer") or None,
    )


def _geschlecht(text: str) -> Geschlecht:
    try:
        return GESCHLECHT_AUS_TEXT[text.strip().lower()]
    except KeyError:
        raise ValueError(f"Unbekanntes Geschlecht '{text}' (erwartet Rüde oder Hündin).") from None


def _herkunft(text: str) -> Herkunft:
    try:
        return Herkunft(text.strip().lower())
    except ValueError:
        erlaubt = ", ".join(h.value.capitalize() for h in Herkunft)
        raise ValueError(f"Unbekannte Herkunft '{text}' (erwartet {erlaubt}).") from None


def _datum(text: str) -> date:
    try:
        return datetime.strptime(text.strip(), DATUMSFORMAT).date()
    except ValueError:
        raise ValueError(f"Ungültiges Datum '{text}' (erwartet TT.MM.JJJJ).") from None
