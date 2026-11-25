"""Reporting mit pandas: Bestandsreport (Kennzahlen) und CSV-Export für Excel."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from tierheim.application.bestand_auflisten import BestandAuflisten
from tierheim.application.heute_faellig import HeuteFaellig
from tierheim.application.neuzugaenge_importieren import DATUMSFORMAT
from tierheim.application.ports import HundRepository
from tierheim.domain.hund import Geschlecht, Hund

ANZAHL_LANGZEIT = 3
GESCHLECHT_ALS_TEXT = {Geschlecht.RUEDE: "Rüde", Geschlecht.HUENDIN: "Hündin"}


@dataclass(frozen=True)
class Langzeit:
    name: str
    tage: int


@dataclass(frozen=True)
class Report:
    anzahl_im_heim: int = 0
    nach_status: dict[str, int] = field(default_factory=dict)
    nach_herkunft: dict[str, int] = field(default_factory=dict)
    durchschnittliche_verweildauer_tage: float | None = None
    langzeit: list[Langzeit] = field(default_factory=list)
    ohne_chip: list[str] = field(default_factory=list)
    heute_faellige_gaben: int = 0


class Bestandsreport:
    def __init__(self, repository: HundRepository, heute: Callable[[], date]) -> None:
        self._repository = repository
        self._heute = heute

    def ausfuehren(self) -> Report:
        tag = self._heute()
        tabelle = _als_tabelle(self._repository.alle(), tag)
        if tabelle.empty:
            return Report()

        im_heim = tabelle[tabelle["im_heim"]]
        langzeit = im_heim.nlargest(ANZAHL_LANGZEIT, "tage")

        return Report(
            anzahl_im_heim=len(im_heim),
            nach_status=_zaehlen(tabelle["status"]),
            nach_herkunft=_zaehlen(im_heim["herkunft"]),
            durchschnittliche_verweildauer_tage=(
                round(float(im_heim["tage"].mean()), 1) if not im_heim.empty else None
            ),
            langzeit=[
                Langzeit(name=name, tage=int(tage))
                for name, tage in zip(langzeit["name"], langzeit["tage"])
            ],
            ohne_chip=sorted(im_heim.loc[~im_heim["hat_chip"], "name"]),
            heute_faellige_gaben=len(HeuteFaellig(self._repository, self._heute).ausfuehren()),
        )


class BestandExportieren:
    """Bestand als CSV im selben Format, das der Import versteht (plus Spalte Status)."""

    def __init__(self, repository: HundRepository) -> None:
        self._repository = repository

    def ausfuehren(self) -> str:
        zeilen = [
            {
                "Name": hund.name,
                "Geschlecht": GESCHLECHT_ALS_TEXT[hund.geschlecht],
                "Herkunft": hund.herkunft.value.capitalize(),
                "Aufnahmedatum": hund.aufnahmedatum.strftime(DATUMSFORMAT),
                "Rasse": hund.rasse or "",
                "Chipnummer": hund.chipnummer.wert if hund.chipnummer else "",
                "Status": hund.status.value,
            }
            for hund in BestandAuflisten(self._repository).ausfuehren()
        ]
        spalten = ["Name", "Geschlecht", "Herkunft", "Aufnahmedatum", "Rasse", "Chipnummer", "Status"]
        return pd.DataFrame(zeilen, columns=spalten).to_csv(sep=";", index=False, lineterminator="\n")


# --- Hilfsfunktionen -------------------------------------------------------------


def _als_tabelle(hunde: list[Hund], tag: date) -> pd.DataFrame:
    """Eine Zeile pro Hund – die Form, mit der pandas rechnen kann."""
    return pd.DataFrame(
        [
            {
                "name": hund.name,
                "status": hund.status.value,
                "herkunft": hund.herkunft.value,
                "tage": (tag - hund.aufnahmedatum).days,
                "hat_chip": hund.chipnummer is not None,
                "im_heim": hund.ist_im_heim,
            }
            for hund in hunde
        ]
    )


def _zaehlen(spalte: pd.Series) -> dict[str, int]:
    """Häufigkeiten, alphabetisch sortiert, mit echten int statt numpy-Zahlen."""
    return {str(wert): int(anzahl) for wert, anzahl in spalte.value_counts().sort_index().items()}
