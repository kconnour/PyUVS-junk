from datetime import datetime
import pytest
from pyuvs import Orbit, DataFilename


class TestOrbit:
    @pytest.fixture
    def orbit(self):
        yield Orbit(3453)

    def test_orbit_yields_known_code(self, orbit):
        assert orbit.code == 'orbit03453'

    def test_orbit_yields_known_block(self, orbit):
        assert orbit.block == 'orbit03400'


class TestDataFilename:
    @pytest.fixture
    def apoapse_l1b_filename(self):
        yield 'mvn_iuv_l1b_apoapse-orbit03453-muv_20160708T044652_v13_r01.fits.gz'

    @pytest.fixture
    def bogus_l1b_filename(self):
        yield 'mvn-iuv-l1b-apoapse-orbit03453-muv-20160708T044652-v13-r01.fits.gz'

    @pytest.fixture
    def relay_echelle_l1b_filename(self):
        yield 'mvn_iuv_l1b_relay-echelle-orbit16976-ech_20220811T003439_v13_r01.fits.gz'

    def test_int_input_raises_type_error(self):
        with pytest.raises(TypeError):
            DataFilename(10)

    def test_bogus_filename_raises_value_error(self, bogus_l1b_filename):
        with pytest.raises(ValueError):
            DataFilename(bogus_l1b_filename)

    def test_filename_yields_input_filename(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).filename == apoapse_l1b_filename

    def test_filename_yields_known_spacecraft(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).spacecraft == 'mvn'

    def test_filename_yields_known_instrument(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).instrument == 'iuv'

    def test_filename_yields_known_level(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).level == 'l1b'

    def test_filename_yields_known_segment(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).segment == 'apoapse'

    def test_filename_yields_known_orbit(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).orbit == 3453

    def test_filename_yields_known_channel(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).channel == 'muv'

    def test_filename_yields_known_timestamp(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).timestamp == '20160708T044652'

    def test_filename_yields_known_datetime(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).datetime == datetime(2016, 7, 8, 4, 46, 52)

    def test_filename_yields_known_version(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).version == 13

    def test_filename_yields_known_revision(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).revision == 1

    def test_filename_yields_known_extension(self, apoapse_l1b_filename):
        assert DataFilename(apoapse_l1b_filename).extension == 'fits.gz'

    def test_relay_echelle_yields_known_segment(self, relay_echelle_l1b_filename):
        assert DataFilename(relay_echelle_l1b_filename).segment == 'relay-echelle'
