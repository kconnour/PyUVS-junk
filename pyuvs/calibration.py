import numpy as np
from pyuvs.anc import load_voltage_correction_voltage, \
    load_voltage_correction_coefficients, \
    load_muv_sensitivity_curve_observational
from pyuvs.constants import pixel_angular_size


def make_gain_correction(
        detector_dark_subtracted: np.ndarray,
        spatial_bin_size: int,
        spectral_bin_size: int,
        integration_time: float,
        mcp_volt: float,
        mcp_gain: float) -> np.ndarray:
    """

    Parameters
    ----------
    detector_dark_subtracted
        The detector dark subtracted structure.
    spatial_bin_size
        The number of detector pixels in a spatial bin.
    spectral_bin_size
        The number of detector pixels in a spectral bin.
    integration_time
        The integration time of each observation.
    mcp_volt
        The MCP voltage of each observation.
    mcp_gain
        The MCP voltage gain of each observation.

    Returns
    -------
    np.ndarray
        The estimated DN of the observation.

    """
    volt_array = load_voltage_correction_voltage()
    voltage_coeff = load_voltage_correction_coefficients()
    ref_mcp_gain = 50.909455

    normalized_img = detector_dark_subtracted / spatial_bin_size / \
                     spectral_bin_size / integration_time

    a = np.interp(mcp_volt, volt_array, voltage_coeff[:, 0])
    b = np.interp(mcp_volt, volt_array, voltage_coeff[:, 1])

    norm_img = np.exp(a + b * np.log(normalized_img))
    return norm_img / normalized_img * mcp_gain / ref_mcp_gain


def make_calibration_curve(
        wavelength_center: np.ndarray,
        mcp_gain: float,
        integration_time: float,
        spatial_bin_size: float) -> np.ndarray:
    """Make the calibration curve for a given set of observation parameters.

    Parameters
    ----------
    wavelength_center
        The wavelengths at the center of each bin.
    mcp_gain
        The MCP voltage gain.
    integration_time
        The integration time of each observation.
    spatial_bin_size
        The number of detector pixels in a spatial bin.

    Returns
    -------
    np.ndarray
        The sensitivity curve [DN/kR].

    Notes
    -----
    This currently uses wavelength to determine the sensitivity curve, but this
    is just a proxy for where on the detector it falls. Bin edges would be a
    better metric in the future.

    """
    sensitivity_curve = load_muv_sensitivity_curve_observational()
    rebinned_sensitivity_curve = np.interp(wavelength_center,
                                           sensitivity_curve[:, 0],
                                           sensitivity_curve[:, 1])
    return rebinned_sensitivity_curve * 4 * np.pi * 10 ** -9 / mcp_gain / \
        pixel_angular_size / integration_time / spatial_bin_size


if __name__ == "__main__":
    from astropy.io import fits
    from pyuvs import find_latest_apoapse_muv_file_paths_from_block
    from pathlib import Path
    p = Path('/media/kyle/McDataFace/iuvsdata/production')
    f = find_latest_apoapse_muv_file_paths_from_block(p, 3453)
    g = f[0]
    hdul = fits.open(g)

    dds = hdul['detector_dark_subtracted'].data
    sza = hdul['pixelgeometry'].data['pixel_solar_zenith_angle']
    spectral_bin_width: int = int(np.median(hdul['binning'].data['spebinwidth'][0]))  # bins
    spatial_bin_width: int = int(np.median(hdul['binning'].data['spabinwidth'][0]))  # bins
    spectral_bin_low = hdul['binning'].data['spepixlo'][0, :]  # bin number
    spectral_bin_high = hdul['binning'].data['spepixhi'][0, :]  # bin number
    voltage: float = hdul['observation'].data['mcp_volt'][0]
    voltage_gain: float = hdul['observation'].data['mcp_gain'][0]
    i_time: float = hdul['observation'].data['int_time'][0]
    w = hdul['observation'].data['wavelength'][0, 0]

    foo = make_gain_correction(dds, spatial_bin_width, spectral_bin_width, i_time, voltage, voltage_gain)
    print(foo.shape)
    bar = make_calibration_curve(w, voltage_gain, i_time, spatial_bin_width)
    print(bar.shape)

