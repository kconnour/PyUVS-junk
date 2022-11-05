"""This module provides functions and objects for working with IUVS data files.
"""
from datetime import datetime
import math
from pathlib import Path


class Orbit:
    """A data structure containing info from an orbit number

    Parameters
    ----------
    orbit: int
        The MAVEN orbit number.

    Raises
    ------
    TypeError
        Raised if the input orbit is not an int.

    Examples
    --------
    Create an orbit and get its properties.

    >>> import pyuvs as pu
    >>> orbit = pu.Orbit(3453)
    >>> orbit.code
    'orbit03453'
    >>> orbit.block
    'orbit03400'

    """
    def __init__(self, orbit: int):
        self._orbit = orbit
        self._validate_input()

        self._code = self._make_code()
        self._block = self._make_block()

    def _validate_input(self) -> None:
        if not isinstance(self.orbit, int):
            message = 'The orbit must be an int.'
            raise TypeError(message)

    def _make_code(self) -> str:
        return 'orbit' + f'{self.orbit}'.zfill(5)

    def _make_block(self) -> str:
        block = math.floor(self.orbit / 100) * 100
        return 'orbit' + f'{block}'.zfill(5)

    @property
    def orbit(self) -> int:
        """Get the input orbit.

        """
        return self._orbit

    @property
    def code(self) -> str:
        """Get the IUVS "orbit code" for the input orbit.

        """
        return self._code

    @property
    def block(self) -> str:
        """Get the IUVS orbit block for the input orbit.

        """
        return self._block


class DataFilename:
    """A data structure containing info from a single IUVS filename.

    It ensures the input filename represents an IUVS filename and extracts all
    information related to the observation and processing pipeline from the
    input.

    Parameters
    ----------
    filename: str
        The filename of an IUVS data product.

    Raises
    ------
    FileNotFoundError
        Raised if the input file path does not exist.
    ValueError
        Raised if the input file does not fit the IUVS filename pattern.

    """
    def __init__(self, filename: str):
        self._filename = filename
        self._validate_filename()

        self._spacecraft = self._make_spacecraft()
        self._instrument = self._make_instrument()
        self._level = self._make_level()

        self._description = self._make_description()   # maybe no
        self._segment = self._make_segment()
        self._orbit = self._make_orbit()
        self._channel = self._make_channel()

        self._timestamp = self._make_timestamp()
        self._datetime = self._make_datetime()

        self._version = self._make_version()
        self._revision = self._make_revision()
        self._extension = self._make_extension()

    def __str__(self):
        return self._filename

    def _validate_filename(self):
        if not isinstance(self._filename, str):
            message = 'The input filename must a string.'
            raise TypeError(message)

    @property
    def filename(self) -> str:
        """Get the input filename.

        """
        return self._filename

    @property
    def spacecraft(self) -> str:
        """Get the spacecraft code from the filename.

        """
        return self._spacecraft

    @property
    def instrument(self) -> str:
        """Get the instrument code from the filename.

        """
        return self._instrument

    @property
    def level(self) -> str:
        """Get the data product level from the filename.

        """
        return self._level

    @property
    def segment(self) -> str:
        """Get the observation segment from the filename.

        """
        return self._segment

    @property
    def orbit(self) -> int:
        """Get the orbit number from the filename.

        """
        return self._orbit

    @property
    def channel(self) -> str:
        """Get the observation channel from the filename.

        """
        return self._channel

    @property
    def timestamp(self) -> str:
        """Get the timestamp of the observation from the filename.

        """
        return self._make_timestamp()

    @property
    def datetime(self) -> datetime:
        """Get the datetime from the filename.

        """
        return self._datetime

    @property
    def version(self) -> int:
        """Get the version code from the filename.

        """
        return self._version

    @property
    def revision(self) -> int:
        """Get the revision code from the filename.

        """
        return self._revision

    @property
    def extension(self) -> str:
        """Get the extension of filename.

        """
        return self._extension

    def _make_spacecraft(self):
        return self._split_filename_on_underscore()[0]

    def _make_instrument(self):
        try:
            return self._split_filename_on_underscore()[1]
        except IndexError as ie:
            message = 'The input file is not an IUVS data file.'
            raise ValueError(message) from ie

    def _make_level(self):
        try:
            return self._split_filename_on_underscore()[2]
        except IndexError as ie:
            message = 'The input file is not an IUVS data file.'
            raise ValueError(message) from ie

    def _make_description(self):
        return self._split_filename_on_underscore()[3]

    def _make_segment(self):
        orbit_index = self._get_split_index_containing_orbit()
        segments = self._split_description()[:orbit_index]
        return '-'.join(segments)

    def _make_orbit(self):
        orbit_index = self._get_split_index_containing_orbit()
        orbit = self._split_description()[orbit_index].removeprefix('orbit')
        return int(orbit)

    def _make_channel(self):
        orbit_index = self._get_split_index_containing_orbit()
        return self._split_description()[orbit_index + 1]

    def _make_timestamp(self):
        return self._split_filename_on_underscore()[4]

    def _make_datetime(self):
        date = self._split_timestamp()[0]
        time = self._split_timestamp()[1]

        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[6:])

        hour = int(time[:2])
        minute = int(time[2:4])
        second = int(time[4:])

        return datetime(year, month, day, hour, minute, second)

    def _make_version(self):
        return int(self._split_filename_on_underscore()[5][1:])

    def _make_revision(self):
        return int(self._split_filename_on_underscore()[6][1:])

    def _make_extension(self):
        return self._split_stem_from_extension()[1]

    def _split_filename_on_underscore(self) -> list[str]:
        stem = self._split_stem_from_extension()[0]
        return stem.split('_')

    def _split_stem_from_extension(self) -> list[str]:
        extension_index = self._filename.find('.')
        stem = self._filename[:extension_index]
        extension = self._filename[extension_index + 1:]
        return [stem, extension]

    def _split_timestamp(self) -> list[str]:
        return self.timestamp.split('T')

    def _split_description(self) -> list[str]:
        return self._description.split('-')

    def _get_split_index_containing_orbit(self) -> int:
        return [c for c, f in enumerate(self._split_description())
                if 'orbit' in f][0]


def make_filename_pattern(segment: str, orbit: int, channel: str) -> str:
    """Make the glob pattern of a set of IUVS filenames.

    Parameters
    ----------
    segment: str
        The orbital segment.
    orbit: int
        The orbit number.
    channel: str
        The instrument channel.

    Returns
    -------
    str
        The glob pattern of IUVS filenames.

    """
    orbit = Orbit(orbit)
    return f'*{segment}*{orbit.code}*{channel}*.fits.gz'


def find_all_file_paths(data_directory: Path, segment: str, orbit: int,
                        channel: str) -> list[Path]:
    """Find all IUVS data file paths that match a set of patterns.

    Parameters
    ----------
    data_directory
        The absolute path to the directory where data files are located.
    segment: str
        The orbital segment.
    orbit: int
        The orbit number.
    channel: str
        The instrument channel.

    Returns
    -------
    list[Path]
        Sorted list of paths matching the input patterns.

    """
    data_filename_pattern = make_filename_pattern(segment, orbit, channel)
    return sorted(data_directory.glob(data_filename_pattern))


def find_outdated_file_paths(files: list[Path]) -> list[Path]:
    """Find the outdated files from a list of files.

    Parameters
    ----------
    files: list[Path]
        Collection of paths of IUVS data files.

    Returns
    -------
    list[Path]
        All of the outdated data file paths.

    """
    filenames = sorted([str(f).replace('s0', 'a0') for f in files])
    last_time_stamp = ''
    last_channel = ''
    last_file = None
    old_files = []
    for f in filenames:
        df = DataFilename(f)
        if df.timestamp == last_time_stamp and df.channel == last_channel:
            old_files.append(Path(last_file))
        if 'a0' in f:
            f = f.replace('a0', 's0')
        last_time_stamp = df.timestamp
        last_channel = df.channel
        last_file = f
    return old_files


def find_latest_file_paths(data_directory: Path, segment: str, orbit: int,
                           channel: str) -> list[Path]:
    """Find the latest file paths that match a set of patterns.

    Parameters
    ----------
    data_directory: Path
        The directory where data files are located.
    segment: str
        The segment name.
    orbit: int
        The orbit number.
    channel: str
        The channel name.

    Returns
    -------
    list[Path]
        The latest file paths matching the input patterns.

    """
    all_files = find_all_file_paths(data_directory, segment, orbit, channel)
    outdated_files = find_outdated_file_paths(all_files)
    return [f for f in all_files if f not in outdated_files]


def find_latest_file_paths_from_block(data_directory: Path, segment: str,
                                      orbit: int, channel: str) -> list[Path]:
    """Find the latest file paths of a given pattern in a given directory,
    where the directory is divided into blocks of data spanning 100 orbits.

    Parameters
    ----------
    data_directory: Path
        The directory where the data blocks are located.
    segment: str
        The segment name.
    orbit: int
        The orbit number.
    channel: str
        The channel name.

    Returns
    ------
    list[Path]
        The latest file paths matching the input patterns.

    """
    block_path = data_directory / Orbit(orbit).block
    return find_latest_file_paths(block_path, segment, orbit, channel)


def find_latest_apoapse_muv_file_paths_from_block(
        data_directory: Path, orbit: int) -> list[Path]:
    """Find the latest apoapse muv file paths in a given directory, where the
    directory is divided into blocks of data spanning 100 orbits.

    Parameters
    ----------
    data_directory: Path
        The directory where the data blocks are located.
    orbit: int
        The orbit number.

    Returns
    -------
    list[Path]
        The latest apoapse MUV file paths from the given orbit.

    Examples
    --------
    Find the latest files from orbit 3453

    >>> from pathlib import Path
    >>> import pyuvs as pu
    >>> p = Path('/media/kyle/McDataFace/iuvsdata/production')
    >>> f = find_latest_apoapse_muv_file_paths_from_block(p, 3453)
    >>> f[0]
    PosixPath('/media/kyle/McDataFace/iuvsdata/production/orbit03400/mvn_iuv_l1b_apoapse-orbit03453-muv_20160708T044652_v13_r01.fits.gz')
    
    """
    return find_latest_file_paths_from_block(
        data_directory, 'apoapse', orbit, 'muv')
