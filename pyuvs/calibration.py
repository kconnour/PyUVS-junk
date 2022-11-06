import numpy as np
from pyuvs.anc import load_voltage_correction_voltage, \
    load_voltage_correction_coefficients, \
    load_muv_sensitivity_curve_observational, load_muv_flatfield
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


def make_flatfield(
        spatial_bin_edges: np.ndarray,
        spectral_bin_edges: np.ndarray) -> np.ndarray:
    """Make the flatfield for a given binning configuration.

    This function will rebin the "master" 133x19 flatfield constructed from
    data during the MY34 GDS onto the given spatial and spectral binning
    scheme.

    Parameters
    ----------
    spatial_bin_edges
        Spatial bin edges. This argument should be an array of integers.
    spectral_bin_edges
        Spectral bin edges. This argument should be an array of integers.

    Returns
    -------
    np.ndarray
        The flatfield for the given binning scheme.

    """
    # The data from which the flatfield was made had the following properties:
    # spatial: started pixel 103, ended on 901, and had a width of 6 pixels
    # spectra: started pixel 172, ended on 818, and had a width of 34 pixels
    ff_expanded = np.repeat(np.repeat(load_muv_flatfield(), 6, axis=0), 34, axis=1)
    ff1024 = np.pad(ff_expanded, ((103, 1024-901), (172, 1024-818)), mode='edge')

    spatial_bins = spatial_bin_edges.shape[0]-1
    spectral_bins = spectral_bin_edges.shape[0]-1

    new_flatfield = np.zeros((spatial_bins, spectral_bins))
    for spatial_bin in range(spatial_bins):
        for spectral_bin in range(spectral_bins):
            new_flatfield[spatial_bin, spectral_bin] = np.mean(
                ff1024[spatial_bin_edges[spatial_bin]: spatial_bin_edges[spatial_bin+1],
                       spectral_bin_edges[spectral_bin]: spectral_bin_edges[spectral_bin+1]])
    return new_flatfield
