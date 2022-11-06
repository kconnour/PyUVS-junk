import numpy as np
import pytest
from pyuvs.calibration import make_flatfield
from pyuvs.anc import load_muv_flatfield


class TestMakeFlatfield:
    @pytest.fixture
    def spatial_binning_133(self):
        yield np.linspace(103, 901, num=134).astype('int')

    @pytest.fixture
    def spectral_binning_19(self):
        yield np.linspace(172, 818, num=20).astype('int')

    def test_my34gds_gives_same_result_as_input_flatfield(self, spatial_binning_133, spectral_binning_19):
        ff = load_muv_flatfield()
        new_ff = make_flatfield(spatial_binning_133, spectral_binning_19)
        assert np.all(np.isclose(ff, new_ff))


