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


def make_sqrt_dayside_segment_detector_image(orbit: int, data_location: Path, saveloc: str, figheight=6):
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
    #app_flip_per_file = np.array([np.sign(np.dot(f['spacecraftgeometry'].data['vx_instrument_inertial'][:, 0], f['spacecraftgeometry'].data['v_spacecraft_rate_inertial'][:, 0])) > 0 for f in hduls])
    app_flip_per_file = np.sign(np.mean([np.dot(f['spacecraftgeometry'].data['vx_instrument_inertial'][:, 0], f['spacecraftgeometry'].data['v_spacecraft_rate_inertial'][:, 0]) for f in hduls])) > 0

    # Make the image template
    template = SegmentDetectorImage(swath_numbers[-1] + 1, figheight)

    for dayside in [True]:
        # Do nothing if there aren't any dayside/nightside files
        if dayside not in dayside_integration_mask:
            plt.close(template.figure)
            return

        # Get relevant info from the data files
        dds = np.vstack([add_dim_if_necessary(hduls[f]['detector_dark_subtracted'].data) for f in range(len(hduls)) if dayside_files[f] == dayside])
        sza = np.vstack([hduls[f]['pixelgeometry'].data['pixel_solar_zenith_angle'] for f in range(len(hduls)) if dayside_files[f] == dayside])
        altitude = np.vstack([hduls[f]['pixelgeometry'].data['pixel_corner_mrh_alt'][..., 4] for f in range(len(hduls)) if dayside_files[f] == dayside])
        app_flip = np.concatenate([np.repeat(app_flip_per_file, n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        try:
            spatial_bin_width = np.concatenate([np.repeat(hduls[f]['primary'].header['spa_size'], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
            spectral_bin_width = np.concatenate([np.repeat(hduls[f]['primary'].header['spe_size'], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        # For some reason we don't always put this info in the header
        except KeyError:
            spatial_bin_width = np.concatenate([np.repeat(int(np.median(hduls[f]['binning'].data['spabinwidth'][0])), n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
            spectral_bin_width = np.concatenate([np.repeat(int(np.median(hduls[f]['binning'].data['spebinwidth'][0])), n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
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
        #bad_pixels = np.any(np.isnan(primary), axis=-1)   # Sometimes there are nans in our data for whatever reason
        # NOTE: If I use bad pixels in the mask, I will remove the strange colored lines sometimes found in dayside data.
        # However, if I keep it, sometimes (see 601/602) it'll cause odd/even behavior. In theory the data should not have
        # NaNs and I can keep it as a guard, but for now it causes strange behavior.

        if dayside:
            #rgb_primary = pu.histogram_equalize_detector_image(primary, mask=np.logical_and(np.logical_and((sza <= 102), on_disk_pixels), ~bad_pixels)) / 255
            mask = np.logical_and((sza <= 102), on_disk_pixels)
            if np.sum(mask) > 265:
                rgb_primary = pu.sqrt_scale_detector_image(primary) / 255
                rgb_primary = np.where(app_flip, np.fliplr(rgb_primary.T), rgb_primary.T).T   # Allow for the APP to flip part way through the orbit
            else:
                plt.close(template.figure)
                return

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
    filename = orbit.code + '-sqrt.png'
    plt.savefig(save_directory / filename)

    plt.close(template.figure)


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
    #app_flip_per_file = np.array([np.sign(np.dot(f['spacecraftgeometry'].data['vx_instrument_inertial'][:, 0], f['spacecraftgeometry'].data['v_spacecraft_rate_inertial'][:, 0])) > 0 for f in hduls])
    app_flip_per_file = np.sign(np.mean([np.dot(f['spacecraftgeometry'].data['vx_instrument_inertial'][:, 0], f['spacecraftgeometry'].data['v_spacecraft_rate_inertial'][:, 0]) for f in hduls])) > 0

    # Make the image template
    template = SegmentDetectorImage(swath_numbers[-1] + 1, figheight)

    for dayside in [True]:
        # Do nothing if there aren't any dayside/nightside files
        if dayside not in dayside_integration_mask:
            plt.close(template.figure)
            return

        # Get relevant info from the data files
        dds = np.vstack([add_dim_if_necessary(hduls[f]['detector_dark_subtracted'].data) for f in range(len(hduls)) if dayside_files[f] == dayside])
        longitude = np.vstack([hduls[f]['pixelgeometry'].data['pixel_corner_lon'][..., 4] for f in range(len(hduls)) if dayside_files[f] == dayside])
        latitude = np.vstack([hduls[f]['pixelgeometry'].data['pixel_corner_lat'][..., 4] for f in range(len(hduls)) if dayside_files[f] == dayside])
        sza = np.vstack([hduls[f]['pixelgeometry'].data['pixel_solar_zenith_angle'] for f in range(len(hduls)) if dayside_files[f] == dayside])
        lt = np.vstack([hduls[f]['pixelgeometry'].data['pixel_local_time'] for f in range(len(hduls)) if dayside_files[f] == dayside])
        altitude = np.vstack([hduls[f]['pixelgeometry'].data['pixel_corner_mrh_alt'][..., 4] for f in range(len(hduls)) if dayside_files[f] == dayside])
        app_flip = np.concatenate([np.repeat(app_flip_per_file, n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        subsolar_lon = np.array([np.mean(hduls[f]['spacecraftgeometry'].data['SUB_SOLAR_LON']) for f in range(len(hduls)) if dayside_files[f] == dayside])
        subsolar_lontest = np.concatenate([hduls[f]['spacecraftgeometry'].data['SUB_SOLAR_LON'] for f in range(len(hduls)) if dayside_files[f] == dayside])
        sza[altitude!=0] = np.nan
        longitude[altitude!=0] = np.nan

        print(subsolar_lontest.shape, dds.shape)

        try:
            spatial_bin_width = np.concatenate([np.repeat(hduls[f]['primary'].header['spa_size'], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
            spectral_bin_width = np.concatenate([np.repeat(hduls[f]['primary'].header['spe_size'], n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
        # For some reason we don't always put this info in the header
        except KeyError:
            spatial_bin_width = np.concatenate([np.repeat(int(np.median(hduls[f]['binning'].data['spabinwidth'][0])), n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
            spectral_bin_width = np.concatenate([np.repeat(int(np.median(hduls[f]['binning'].data['spebinwidth'][0])), n_integrations_per_file[f]) for f in range(len(hduls)) if dayside_files[f] == dayside])
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
        #bad_pixels = np.any(np.isnan(primary), axis=-1)   # Sometimes there are nans in our data for whatever reason
        # NOTE: If I use bad pixels in the mask, I will remove the strange colored lines sometimes found in dayside data.
        # However, if I keep it, sometimes (see 601/602) it'll cause odd/even behavior. In theory the data should not have
        # NaNs and I can keep it as a guard, but for now it causes strange behavior.

        if dayside:
            #rgb_primary = pu.histogram_equalize_detector_image(primary, mask=np.logical_and(np.logical_and((sza <= 102), on_disk_pixels), ~bad_pixels)) / 255
            mask = np.logical_and((sza <= 102), on_disk_pixels)
            if np.sum(mask) > 265:
                rgb_primary = pu.histogram_equalize_detector_image(primary, mask=mask) / 255
                rgb_primary = np.where(app_flip, np.fliplr(rgb_primary.T), rgb_primary.T).T   # Allow for the APP to flip part way through the orbit
            else:
                plt.close(template.figure)
                return

        for swath in np.unique(swath_numbers):
            # Do this no matter if I'm plotting primary or angles
            swath_inds = dayside_swath_numbers == swath
            n_integrations = np.sum(swath_inds)
            x, y = pu.make_swath_grid(dayside_field_of_view[swath_inds], swath,
                                   primary.shape[1], n_integrations)

            # Plot the primary for dayside data
            if dayside:
                if swath != 0:
                    newx, newy = pu.make_swath_grid(dayside_field_of_view[swath_inds], swath,
                                              primary.shape[1]-1, n_integrations-1)
                    pu.pcolormesh_rgb_detector_image(template.data_axis, rgb_primary[swath_inds], x, y)
                    template.data_axis.contour(newx, newy, sza[dayside_swath_numbers == swath], [90], colors='red')
                    loncopy = np.copy(longitude)
                    loncopy[np.where(np.abs(longitude-subsolar_lon[swath])>10)] = np.nan
                    template.data_axis.contour(newx, newy, loncopy[dayside_swath_numbers == swath], [subsolar_lon[swath]], colors='red')
                    #template.data_axis.contour(newx, newy, longitude[dayside_swath_numbers == swath], [np.mean(subsolar_lontest[dayside_swath_numbers == swath])], colors='red')
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

    plt.close(template.figure)


def geometry_ql(orbit: int, data_location: Path, saveloc: str, figheight=6):
    """Make an geometry QL

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

    vec = [f['pixelgeometry'].data['pixel_vec'] for f in hduls]
    et = [f['integration'].data['et'] for f in hduls]



if __name__ == '__main__':
    '''import multiprocessing as mp
    import time

    start_time = time.time()

    n_cpus = mp.cpu_count()  # = 8 for my old desktop, 12 for my laptop, 20 for my new desktop
    pool = mp.Pool(n_cpus - 1)
    for orbit in range(6000, 7000):
        pool.apply_async(func=make_dayside_segment_detector_image, args=(orbit, Path('/media/kyle/McDataFace/iuvsdata/production'), '/home/kyle/iuvs/ql'))
    pool.close()
    pool.join()

    print(f'The QLs took {time.time() - start_time} seconds to process.')'''

    make_dayside_segment_detector_image(6759, Path('/media/kyle/McDataFace/iuvsdata/production'), '/home/kyle/iuvs/ql')
