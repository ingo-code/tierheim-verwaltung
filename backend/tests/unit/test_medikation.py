from datetime import date

import pytest

from tierheim.domain.medikation import Medikation, UngueltigeMedikation

START = date(2026, 11, 20)


def medikation(**abweichungen) -> Medikation:
    werte = dict(medikament="Metacam", dosis="1,5 ml", startdatum=START)
    werte.update(abweichungen)
    return Medikation(**werte)


# --- Fälligkeit ------------------------------------------------------------


@pytest.mark.parametrize(
    "tag, faellig",
    [
        (date(2026, 11, 19), False),  # vor dem Start
        (date(2026, 11, 20), True),  # am Starttag
        (date(2026, 11, 21), True),
        (date(2026, 12, 31), True),  # ohne Enddatum: dauerhaft
    ],
)
def test_taegliche_medikation(tag, faellig):
    assert medikation().ist_faellig_am(tag) is faellig


@pytest.mark.parametrize(
    "tag, faellig",
    [
        (date(2026, 11, 20), True),
        (date(2026, 11, 21), False),
        (date(2026, 11, 22), True),
    ],
)
def test_medikation_jeden_zweiten_tag(tag, faellig):
    assert medikation(intervall_tage=2).ist_faellig_am(tag) is faellig


@pytest.mark.parametrize(
    "tag, faellig",
    [
        (date(2026, 11, 25), True),  # letzter Tag zählt mit
        (date(2026, 11, 26), False),  # danach nicht mehr
    ],
)
def test_medikation_endet_am_enddatum(tag, faellig):
    assert medikation(enddatum=date(2026, 11, 25)).ist_faellig_am(tag) is faellig


# --- Regeln beim Anlegen ---------------------------------------------------


@pytest.mark.parametrize("name", ["", "  "])
def test_medikation_ohne_medikament_wird_abgelehnt(name):
    with pytest.raises(UngueltigeMedikation):
        medikation(medikament=name)


def test_medikation_ohne_dosis_wird_abgelehnt():
    with pytest.raises(UngueltigeMedikation):
        medikation(dosis="")


def test_intervall_kleiner_eins_wird_abgelehnt():
    with pytest.raises(UngueltigeMedikation):
        medikation(intervall_tage=0)


def test_enddatum_vor_startdatum_wird_abgelehnt():
    with pytest.raises(UngueltigeMedikation):
        medikation(enddatum=date(2026, 11, 19))
