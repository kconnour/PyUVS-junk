"""This module provides functions and objects for working with IUVS data files.
"""
from datetime import datetime


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
