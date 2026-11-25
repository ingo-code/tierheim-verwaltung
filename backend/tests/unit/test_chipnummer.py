import pytest

from tierheim.domain.chipnummer import Chipnummer, UngueltigeChipnummer


def test_gueltige_deutsche_chipnummer_wird_akzeptiert():
    chip = Chipnummer("276098100123456")
    assert chip.wert == "276098100123456"


def test_chipnummer_mit_14_ziffern_wird_abgelehnt():
    with pytest.raises(UngueltigeChipnummer):
        Chipnummer("27609810012345")


def test_chipnummer_mit_buchstaben_wird_abgelehnt():
    with pytest.raises(UngueltigeChipnummer):
        Chipnummer("27609810012345A")


@pytest.mark.parametrize(
    "nummer",
    [
        "276098100123456",  # Deutschland
        "642093400123456",  # Rumänien – häufig bei Tierschutzhunden
        "981020000123456",  # Herstellercode (900–999)
    ],
)
def test_laender_und_herstellercodes_werden_akzeptiert(nummer):
    assert Chipnummer(nummer).wert == nummer


def test_chipnummer_mit_code_000_wird_abgelehnt():
    with pytest.raises(UngueltigeChipnummer):
        Chipnummer("000123456789012")
