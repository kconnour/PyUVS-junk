"""This module contains functions for working with SPICE kernels.
"""
from datetime import datetime
import os
from pathlib import Path
import re

import numpy as np
import spiceypy as spice

from pyuvs import orbit_insertion_date

_target = 'Mars'
_observer = 'MAVEN'
_abcorr = 'LT+S'


def clear_existing_kernels() -> None:
    """Clear any existing SPICE kernels loaded in memory.

    Returns
    -------
    None

    """
    spice.kclear()


def _split_string_into_length(string: str, length: int) -> list[str]:
    # Turn a string into a list of strings that have a maximum length. This
    # is needed since spice can only handle strings of at most length 80.
    # An update in 2022 suggests this may have been increased to 255.
    return [string[i: i + length] for i in range(0, len(string), length)]


def _pool_and_furnish(kernel_path: Path, tm: str) -> None:
    split_path = _split_string_into_length(str(kernel_path), 78)
    spice.pcpool('PATH_VALUES', split_path)
    tm_path = kernel_path / f'{tm}.tm'
    spice.furnsh(str(tm_path))


def _furnish_array(kernels: list[str]) -> None:
    [spice.furnsh(str(k)) for k in kernels]


def _find_latest_kernels(filenames: list[Path], part: int,
                         getlast: bool = False, after: str = None):
    # sort the list in reverse order so the most recent kernel appears first
    # in a subset of kernels
    filenames.sort(reverse=True)

    # extract the filenames without their version number
    filetag = [os.path.basename(f).split("_v")[0] for f in filenames]

    # without version numbers, there are many repeated filenames, so find a
    # single entry for each kernel
    uniquetags, uniquetagindices = np.unique(filetag, return_index=True)

    # make a list of the kernels with one entry per kernel
    fnamelist = np.array(filenames)[uniquetagindices]

    # extract the date portions of the kernel file paths
    datepart = [re.split('[-_]', os.path.basename(fname))[part]
                for fname in fnamelist]

    # find the individual dates
    last = np.unique(datepart)[-1]

    # if a date is chosen for after, then include only the latest kernels
    # after the specified date
    if after is not None:
        retlist = [f for f, d in zip(
            fnamelist, datepart) if int(d) >= int(after)]

    # otherwise, return all the latest kernels
    else:
        retlist = fnamelist

    # if user wants, return also the date of the last of the latest kernels
    if getlast:
        return retlist, last

    # otherwise return just the latest kernels
    else:
        return retlist


def _find_long_term_kernels(ck_path: Path, kernel_type: str):
    f = sorted(ck_path.glob(f'mvn_{kernel_type}_rel_*.bc'))
    return _find_latest_kernels(f, 4) if len(f) > 0 else None, None


def _find_daily_kernels(ck_path: Path, kernel_type: str, lastlong: str):
    f = sorted(ck_path.glob(f'mvn_{kernel_type}_red_*.bc'))
    return _find_latest_kernels(f, 3, after=lastlong, getlast=True) if len(f) > 0 else (None, None)


def _find_reconstructed_kernels(ck_path: Path, kernel_type: str, lastday: str) -> list[str]:
    f = sorted(ck_path.glob(f'mvn_{kernel_type}_rec_*.bc'))
    return _find_latest_kernels(f, 3, after=lastday) if len(f) > 0 else []


def _furnish_ck_by_type(ck_path: Path, kernel_type: str) -> None:
    longterm_kernels, lastlong = _find_long_term_kernels(ck_path, kernel_type)
    #daily_kernels, lastday = _find_daily_kernels(ck_path, kernel_type, lastlong)
    #normal_kernels = _find_reconstructed_kernels(ck_path, kernel_type, None)

    #print(len(normal_kernels), type(normal_kernels), type(normal_kernels[0]))
    #print(len(daily_kernels), type(daily_kernels), type(daily_kernels[0]))
    #print(len(longterm_kernels), type(longterm_kernels), type(longterm_kernels[0]))
    #_furnish_array(normal_kernels)
    #_furnish_array(daily_kernels)
    _furnish_array([str(f) for f in longterm_kernels])


def furnish_ck(spice_directory: Path) -> None:
    """Furnish the spacecraft C-kernels.

    Returns
    -------
    None

    Notes
    -----
    This function currently only furnishes the long term kernels (as opposed to
    the daily or reconstructed kernels).

    """
    ck_path = spice_directory / 'mvn' / 'ck'
    _furnish_ck_by_type(ck_path, 'app')
    _furnish_ck_by_type(ck_path, 'sc')

    ck_kernels = sorted(ck_path.glob('mvn_iuv_all_l0_20*.bc'))
    if len(ck_kernels) > 0:
        _furnish_array(_find_latest_kernels(ck_kernels, 4))
    else:
        print('No ck kernels found.')


def furnish_spk(spice_directory: Path) -> None:
    """Furnish the spacecraft spk kernels (ephemeris data of its location).

    Returns
    -------
    None

    """
    spk_path = spice_directory / 'mvn' / 'spk'
    spk_kernels = sorted(spk_path.glob('trj_orb_*-*_rec*.bsp'))
    if len(spk_kernels) > 0:
        rec, _ = _find_latest_kernels(spk_kernels, 3, getlast=True)
        _furnish_array(rec)
    else:
        print('No spk kernels found.')


def furnish_sclk(spice_directory: Path) -> None:
    """Furnish the spacecraft sclk kernels (the spacecraft clock).

    Returns
    -------
    None

    """
    sclk_path = spice_directory / 'mvn' / 'sclk'
    clock_kernels = sorted(sclk_path.glob('MVN_SCLKSCET.0*.tsc'))
    _furnish_array(clock_kernels)


def _furnish_mars(mars_path: Path) -> None:
    mars_kernel = mars_path / 'mar097.bsp'
    spice.furnsh(str(mars_kernel))


def furnish_standard_kernels(spice_directory: Path) -> None:
    r"""Furnish all the kernels typically required by IUVS observations.

    This will load in ck, spk, and sclk kernels.

    Returns
    -------
    None

    """
    mvn_kernel_path = spice_directory / 'mvn'
    generic_kernel_path = spice_directory / 'generic_kernels'
    mars_kernel_path = generic_kernel_path / 'spk'

    _pool_and_furnish(mvn_kernel_path, 'mvn')
    _pool_and_furnish(generic_kernel_path, 'generic')
    _furnish_mars(mars_kernel_path)

    furnish_ck(spice_directory)
    furnish_spk(spice_directory)
    furnish_sclk(spice_directory)


def compute_maven_apsis_et(
        segment='apoapse',
        start_time: datetime = orbit_insertion_date,
        end_time: datetime = datetime.utcnow(),
        step_size: float = 60):
    """Compute the ephemeris time at MAVEN's apses.

    Parameters
    ----------
    segment : str
        The orbit point at which to calculate the ephemeris time. Must be either
        "apoapse" or "periapse".
    start_time: datetime
        The earliest datetime to include in the search.
    end_time: datetime
        The latest datetime to include in the search.
    step_size: float
        The step size [seconds] to use for the search.

    Returns
    -------
    orbit_numbers : np.ndarray
        Array of MAVEN orbit numbers. If ``start_time`` is not the date of
        orbital insertion, these numbers are the orbit numbers relative to the
        starting time!
    et_array : np.ndarray
        Array of ephemeris times for chosen orbit segment.

    Notes
    -----
    You must have already furnished the kernels between the starting and ending
    datetimes.

    Examples
    --------
    Find the ephemeris time of orbit 3453.

    >>> from pathlib import Path
    >>> from datetime import datetime
    >>> import pyuvs as pu
    >>> p = Path('/media/kyle/McDataFace/spice')
    >>> pu.clear_existing_kernels()
    >>> pu.furnish_standard_kernels(p)
    >>> orbits, et = compute_maven_apsis_et(end_time=datetime(2019, 1, 1))
    >>> et[orbits==3453][0]
    521227372.7148782

    """
    et_start = spice.datetime2et(start_time)
    et_end = spice.datetime2et(end_time)

    abcorr = 'NONE'
    match segment:
        case 'apoapse':
            relate = 'LOCMAX'
            refval = 3396 + 6200
        case 'periapse':
            relate = 'LOCMIN'
            refval = 3396 + 500
        case _:
            print('The segment must either be "apoapse" or "periapse".')
            return
    adjust = 0
    et = [et_start, et_end]
    cnfine = spice.utils.support_types.SPICEDOUBLE_CELL(2)
    spice.wninsd(et[0], et[1], cnfine)
    ninterval = round((et[1] - et[0]) / step_size)
    result = spice.utils.support_types.SPICEDOUBLE_CELL(
        round(1.1 * (et[1] - et[0]) / 4.5))
    spice.gfdist(_target, abcorr, _observer, relate, refval, adjust, step_size,
                 ninterval, cnfine, result=result)
    count = spice.wncard(result)
    et_array = np.zeros(count)
    if count == 0:
        print('Result window is empty.')
    else:
        for i in range(count):
            lr = spice.wnfetd(result, i)
            left = lr[0]
            right = lr[1]
            if left == right:
                et_array[i] = left

    # make array of orbit numbers
    orbit_numbers = np.arange(1, len(et_array) + 1, 1, dtype=int)

    return orbit_numbers, et_array


def compute_solar_longitude(et: float) -> float:
    """Compute the solar longitude for a given ephemeris time.

    Parameters
    ----------
    et: float
        The ephemeris time.

    """
    return np.degrees(spice.lspcn(_target, et, _abcorr))


def compute_subsolar_point(et: float) -> tuple[float, float]:
    """Compute the subsolar point for a given ephemeris time.

    Parameters
    ----------
    et: float
        The ephemeris time.

    Returns
    -------
    tuple[float, float]
        The [latitude, longitude] of the subsolar point.

    """
    spoint, _, _ = spice.subslr(
        'Intercept: ellipsoid', _target, et, 'IAU_MARS', _abcorr, _observer)
    rpoint, colatpoint, lonpoint = spice.recsph(spoint)
    subsolar_lat = 90 - np.degrees(colatpoint)
    subsolar_lon = np.degrees(lonpoint)
    subsolar_lon += 360 if subsolar_lon < 0 else subsolar_lon
    return subsolar_lat, subsolar_lon


def compute_subspacecraft_point(et: float) -> tuple[float, float]:
    """Compute the subspacecraft point for a given ephemeris time.

    Parameters
    ----------
    et: float
        The ephemeris time.

    Returns
    -------
    tuple[float, float]
        The [latitude, longitude] of the subspacecraft point.

    """
    spoint, _, _ = spice.subpnt(
        'Intercept: ellipsoid', _target, et, 'IAU_MARS', _abcorr, _observer)
    rpoint, colatpoint, lonpoint = spice.recsph(spoint)
    subsc_lat = 90 - np.degrees(colatpoint)
    subsc_lon = np.degrees(lonpoint)
    subsc_lon += 360 if subsc_lon < 0 else subsc_lon
    return subsc_lat, subsc_lon


def _compute_distance(et: float, observer: str) -> float:
    _, _, srfvec = spice.subpnt(
        'Intercept: ellipsoid', _target, et, 'IAU_MARS', _abcorr, observer)
    return np.sqrt(np.sum(srfvec ** 2))


def compute_subspacecraft_altitude(et: float) -> float:
    """Compute the subspacecraft altitude [km] for a given ephemeris time.

    Parameters
    ----------
    et: float
        The ephemeris time.

    """
    return _compute_distance(et, _observer)


def compute_mars_sun_distance(et: float) -> float:
    """Compute the Mars-sun distance [km] for a given ephemeris time.

    Parameters
    ----------
    et: float
        The ephemeris time.

    """
    return _compute_distance(et, 'SUN')


if __name__ == '__main__':
    p = Path('/media/kyle/McDataFace/spice')
    clear_existing_kernels()
    furnish_standard_kernels(p)
    o, et = compute_maven_apsis_et(end_time=datetime(2019, 1, 1))
    myet = et[o==3453]
    print(compute_solar_longitude(myet))
    print(compute_subspacecraft_point(myet))
    print(compute_subsolar_point(myet))
    print(compute_subspacecraft_altitude(myet))
