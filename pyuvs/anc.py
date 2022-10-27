"""This module provides functions to load in standard dictionaries and arrays
for working with IUVS data."""
from pathlib import Path
import numpy as np


def _get_package_path() -> Path:
    return Path(__file__).parent.resolve()


def _get_anc_directory() -> Path:
    return _get_package_path() / 'anc'


def _get_maps_directory() -> Path:
    return _get_anc_directory() / 'maps'


def _get_templates_directory() -> Path:
    return _get_anc_directory() / 'templates'


def load_map_magnetic_field_closed_probability() -> np.ndarray:
    """Load the map denoting the probability of a closed magnetic field line.

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    This map comes from `MGS data <https://doi.org/10.1029/2007JA012435>`_. It
    has a shape of (180, 360).

    * The zeroth axis corresponds to latitude and spans -90 to 90 degrees.
    * The first axis corresponds to east longitude and spans 0 to 360 degrees.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import matplotlib.ticker as ticker
       import pyuvs as pu

       fig, ax = plt.subplots(1, 1, figsize=(6, 3), constrained_layout=True)

       b_field = pu.load_map_magnetic_field_closed_probability()
       ax.imshow(b_field, cmap='Blues_r', extent=[0, 360, -90, 90],
                          origin='lower', rasterized=True)
       ax.set_xlabel('Longitude [degrees]')
       ax.set_ylabel('Latitude [degrees]')
       ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
       ax.yaxis.set_major_locator(ticker.MultipleLocator(30))

       plt.show()

    """
    return np.load(_get_maps_directory() / 'magnetic_field_closed_probability.npy')


def load_map_magnetic_field_open_probability() -> np.ndarray:
    """Load the map denoting the probability of an open magnetic field line.

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    This map comes from `MGS data <https://doi.org/10.1029/2007JA012435>`_. It
    has a shape of (180, 360).

    * The zeroth axis corresponds to latitude and spans -90 to 90 degrees.
    * The first axis corresponds to east longitude and spans 0 to 360 degrees.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import matplotlib.ticker as ticker
       import pyuvs as pu

       fig, ax = plt.subplots(1, 1, figsize=(6, 3), constrained_layout=True)

       b_field = pu.load_map_magnetic_field_open_probability()
       ax.imshow(b_field, cmap='Blues_r', extent=[0, 360, -90, 90],
                          origin='lower', rasterized=True)
       ax.set_xlabel('Longitude [degrees]')
       ax.set_ylabel('Latitude [degrees]')
       ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
       ax.yaxis.set_major_locator(ticker.MultipleLocator(30))

       plt.show()

    """
    return np.load(_get_maps_directory() / 'magnetic_field_open_probability.npy')


def load_map_mars_surface() -> np.ndarray:
    """Load the Mars surface map.

    Returns
    -------
    np.ndarray
        Array of the image.

    Notes
    -----
    The shape of this array is (1800, 3600, 4).

    * The zeroth axis corresponds to latitude and spans -90 to 90 degrees.
    * The first axis corresponds to east longitude and spans 0 to 360 degrees.
    * The second axis is the RGBA channel.

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import matplotlib.ticker as ticker
       import pyuvs as pu

       fig, ax = plt.subplots(1, 1, figsize=(6, 3), constrained_layout=True)

       mars = pu.load_map_mars_surface()
       ax.imshow(mars, extent=[0, 360, -90, 90], origin='lower', rasterized=True)
       ax.set_xlabel('Longitude [degrees]')
       ax.set_ylabel('Latitude [degrees]')
       ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
       ax.yaxis.set_major_locator(ticker.MultipleLocator(30))

       plt.show()

    """
    return np.load(_get_maps_directory() / 'mars_surface.npy')


def load_template_wavelengths() -> np.ndarray:
    """Load the wavelength centers that correspond to the MUV templates.

    Returns
    -------
    np.ndarray
        Array of the wavelengths.

    Notes
    -----
    The shape of this array is (1024,).

    """
    return np.linspace(174.00487653, 341.44029638, num=1024)


def load_template_co_cameron() -> np.ndarray:
    """Load the normalized MUV CO Cameron bands template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_co_cameron()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'co_cameron_bands.npy')


def load_template_co_plus_1st_negative() -> np.ndarray:
    """Load the normalized MUV CO :sup:`+` 1NG (first negative) bands template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_co_plus_1st_negative()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'co+_first_negative.npy')


def load_template_co2_plus_fdb() -> np.ndarray:
    """Load the MUV CO :sub:`2` :sup:`+` FDB (Fox-Duffendack-Barker) bands template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_co2_plus_fdb()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'co2+_fox_duffendack_barker.npy')


def load_template_co2_plus_uvd() -> np.ndarray:
    """Load the MUV CO :sub:`2` :sup:`+` UVD (ultraviolet doublet) template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_co2_plus_uvd()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'co2+_ultraviolet_doublet.npy')


def load_template_n2_vk() -> np.ndarray:
    """Load the MUV N :sub:`2` VK (Vegard-Kaplan) bands template.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_n2_vk()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'nitrogen_vegard_kaplan.npy')


def load_template_no_nightglow() -> np.ndarray:
    """Load the MUV NO nightglow bands template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_no_nightglow()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'no_nightglow.npy')


def load_template_oxygen_2972() -> np.ndarray:
    """Load the MUV oxygen 297.2 nm template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_oxygen_2972()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'oxygen_2972.npy')


def load_template_solar_continuum() -> np.ndarray:
    """Load the MUV solar continuum template.

    This template is in uncalibrated DNs.

    Returns
    -------
    np.ndarray
        Array of the template.

    Notes
    -----
    The shape of this array is (1024,).

    Examples
    --------
    Visualize this array.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       import pyuvs as pu

       fig, ax = plt.subplots()

       template = pu.load_template_solar_continuum()
       wavelengths = pu.load_template_wavelengths()
       ax.plot(wavelengths, template)
       ax.set_xlim(wavelengths[0], wavelengths[-1])
       ax.set_xlabel('Wavelength [nm]')
       ax.set_ylabel('Relative brightness')

       plt.show()

    """
    return np.load(_get_templates_directory() / 'solar_continuum.npy')
