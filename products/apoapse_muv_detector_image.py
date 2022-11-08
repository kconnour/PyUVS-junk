from pathlib import Path
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pyuvs as pu


class SegmentDetectorImage:
    """Make a template of a detector image containing all data from a
    segment. This is broadcast into angular space so that the pixels are
    not warped. The data axis spans the figure.

    Parameters
    ----------
    n_swaths
        The number of swaths present in the data.
    height
        The desired figure height [inches].

    Examples
    --------
    Visualize this template.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       from pyuvs.graphics.templates import SegmentDetectorImage

       SegmentDetectorImage(6, 4)
       plt.show()

    """
    def __init__(self, n_swaths: int, height: float):
        self._n_swaths = n_swaths
        self._height = height
        self._width = self._compute_width()

        self._figure = self._setup_figure()

        self._data_axis = self._add_data_axis()

    def _compute_width(self) -> float:
        aspect_ratio = self._n_swaths * pu.angular_slit_width / \
                       (2 * (pu.maximum_mirror_angle - pu.minimum_mirror_angle))
        return aspect_ratio * self._height

    def _setup_figure(self) -> plt.Figure:
        return plt.figure(figsize=(self._width, self._height))

    def _add_data_axis(self) -> plt.Axes:
        return self._figure.add_axes([0, 0, 1, 1])

    @property
    def figure(self) -> plt.Figure:
        """Get the figure.

        Returns
        -------
        plt.Figure
            The figure.

        """
        return self._figure

    @property
    def data_axis(self) -> plt.Axes:
        """Get the data axis, which spans the entire figure.

        Returns
        -------
        plt.Axes
            The data axis.
        """
        return self._data_axis


def add_dim_if_necessary(arr):
    return arr if np.ndim(arr) == 3 else arr[None, :]


def make_dayside_segment_detector_image(orbit: int, data_location: Path, saveloc: str, figheight=6):
    """Make an apoapse MUV detector image

    Parameters
    ----------
    orbit
        The orbit number
    data_location
        The location of the data directory.
    saveloc
        The general save location.
    figheight
        The figure height.

    Returns
    -------
    None

    Examples
    --------
    >>> make_dayside_segment_detector_image(3749, Path('/media/kyle/McDataFace/iuvsdata/production'), '/home/kyle/iuvs/ql')

    """
    # Load in the data
    orbit = pu.Orbit(orbit)
    data_paths = pu.find_latest_apoapse_muv_file_paths_from_block(data_location, orbit.orbit)
    if data_paths == []:
        return
    hduls = [fits.open(f) for f in data_paths]

    # Make data that's independent of day/night
    field_of_view = np.concatenate([f['integration'].data['fov_deg'] for f in hduls])
    swath_numbers = pu.swath_number(field_of_view)
    dayside_files = np.array([f['observation'].data['mcp_volt'][0] < pu.day_night_voltage_boundary for f in hduls])
    n_integrations_per_file = [f['primary'].data.shape[0] if np.ndim(f['primary'].data)==3 else 1 for f in hduls]
    dayside_integration_mask = np.concatenate([np.repeat(dayside_files[f], n_integrations_per_file[f]) for f in range(len(hduls))])
    app_flip_per_file = np.array([np.sign(np.dot(f['spacecraftgeometry'].data['vx_instrument_inertial'][-1], f['spacecraftgeometry'].data['v_spacecraft_rate_inertial'][-1])) > 0 for f in hduls])

    # Make the image template
    template = SegmentDetectorImage(swath_numbers[-1] + 1, figheight)

    for dayside in [True]:
        # Do nothing if there aren't any dayside/nightside files
        if dayside not in dayside_integration_mask:
            return

        # Get relevant info from the data files
        dds = np.vstack([add_dim_if_necessary(hduls[f]['detector_dark_subtracted'].data) for f in range(len(hduls)) if dayside_files[f] == dayside])
        sza = np.vstack([hduls[f]['pixelgeometry'].data['pixel_solar_zenith_angle'] for f in range(len(hduls)) if dayside_files[f] == dayside])
        altitude = np.vstack([hduls[f]['pixelgeometry'].data['pixel_corner_mrh_alt'][..., 4] for f in range(len(hduls)) if dayside_files[f] == dayside])
        app_flip = np.concatenate([np.repeat(app_flip_per_file[f], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        spatial_bin_width = np.concatenate([np.repeat(hduls[f]['primary'].header['spa_size'], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        spectral_bin_width = np.concatenate([np.repeat(hduls[f]['primary'].header['spe_size'], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        voltage = np.concatenate([np.repeat(hduls[f]['observation'].data['mcp_volt'][0], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        voltage_gain = np.concatenate([np.repeat(hduls[f]['observation'].data['mcp_gain'][0], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        integration_time = np.concatenate([np.repeat(hduls[f]['observation'].data['int_time'][0], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        wavelength_center = hduls[np.argmax(dayside_files==dayside)]['observation'].data['wavelength'][0]
        expanded_wavelength = np.broadcast_to(wavelength_center, spatial_bin_width.shape + wavelength_center.shape)
        curve = pu.make_calibration_curve(np.moveaxis(expanded_wavelength, 0, -1), voltage_gain, integration_time, spatial_bin_width)
        calibration_curve = np.moveaxis(curve, -1, 0)

        calibrated_dds = dds / calibration_curve

        gain_correction = pu.make_gain_correction(np.moveaxis(calibrated_dds, 0, -1), spatial_bin_width, spectral_bin_width, integration_time, voltage, voltage_gain)
        gain_corrected_dds = calibrated_dds * np.moveaxis(gain_correction, -1, 0)

        spatial_bin_edges = np.append(hduls[np.argmax(dayside_files==dayside)]['binning'].data['spapixlo'][0, :],
                                    hduls[np.argmax(dayside_files==dayside)]['binning'].data['spapixhi'][0, -1] + 1)
        spectral_bin_edges = np.append(hduls[np.argmax(dayside_files == dayside)]['binning'].data['spepixlo'][0, :],
                                     hduls[np.argmax(dayside_files == dayside)]['binning'].data['spepixhi'][0, -1] + 1)
        ff = pu.make_flatfield(spatial_bin_edges, spectral_bin_edges)

        primary = gain_corrected_dds / ff

        on_disk_pixels = altitude == 0
        dayside_field_of_view = field_of_view[dayside_integration_mask]
        dayside_swath_numbers = swath_numbers[dayside_integration_mask]
        bad_pixels = np.any(np.isnan(primary), axis=-1)   # Sometimes there are nans in our data for whatever reason

        if dayside:
            rgb_primary = pu.histogram_equalize_detector_image(primary, mask=np.logical_and(np.logical_and((sza <= 102), on_disk_pixels), ~bad_pixels)) / 255
            rgb_primary = np.where(app_flip, np.fliplr(rgb_primary.T), rgb_primary.T).T   # Allow for the APP to flip part way through the orbit

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = dayside_swath_numbers == swath
            n_integrations = np.sum(swath_inds)
            x, y = pu.make_swath_grid(dayside_field_of_view[swath_inds], swath,
                                   primary.shape[1], n_integrations)

            # Plot the primary for dayside data
            if dayside:
                pu.pcolormesh_rgb_detector_image(template.data_axis,
                                              rgb_primary[swath_inds], x, y)

    template.data_axis.set_xlim(0, pu.angular_slit_width * (swath_numbers[-1] + 1))
    template.data_axis.set_ylim(pu.minimum_mirror_angle * 2,
                                pu.maximum_mirror_angle * 2)
    template.data_axis.set_xticks([])
    template.data_axis.set_yticks([])
    template.data_axis.set_facecolor('k')
    save_directory = Path(saveloc) / orbit.block

    # Make the directory if it's not already there and save the file
    save_directory.mkdir(parents=True, exist_ok=True)
    filename = orbit.code + '.png'
    plt.savefig(save_directory / filename)


if __name__ == '__main__':
    for o in range(2000):
        print(o)
        make_dayside_segment_detector_image(3749, Path('/media/kyle/McDataFace/iuvsdata/production'), '/home/kyle/iuvs/ql')
