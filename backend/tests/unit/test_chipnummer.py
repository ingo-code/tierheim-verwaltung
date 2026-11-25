import pytest

from tierheim.domain.chipnummer import Chipnummer, UngueltigeChipnummer


def test_gueltige_deutsche_chipnummer_wird_akzeptiert():
    chip = Chipnummer("276098100123456")
    assert chip.wert == "276098100123456"


def test_chipnummer_mit_14_ziffern_wird_abgelehnt():
    with pytest.raises(UngueltigeChipnummer):
        Chipnummer("27609810012345")
