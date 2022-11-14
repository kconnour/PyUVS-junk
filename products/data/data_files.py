from pathlib import Path

from astropy.io import fits
from netCDF4 import Dataset
import numpy as np

import pyuvs as pu
from _fits import find_latest_apoapse_muv_file_paths_from_block, Orbit


def create_daynight_apoapse_muv_nc_files(data_path: Path, orbit: int, save_location: Path):
    orbit = Orbit(orbit)
    fits_files = find_latest_apoapse_muv_file_paths_from_block(data_path, orbit.orbit)
    hduls = [fits.open(f) for f in fits_files]

    dayside_files = np.array([f['observation'].data['mcp_volt'][0] < pu.day_night_voltage_boundary for f in hduls])
    for daynight in [True, False]:
        daynight_files = dayside_files == daynight
        if not np.any(daynight_files):
            continue
        daynight_hduls = [hduls[f] for f in daynight_files if f]
        nc, apoapse, binning, detector, observation, pixel_geometry, spacecraft_geometry = \
            make_daynight_nc_file_structure(orbit, daynight_hduls, save_location, daynight)


def make_daynight_nc_file_structure(orbit: Orbit, hduls: list, save_location: Path, dayside: bool):
    dds = np.vstack([add_dim_if_necessary(f['detector_dark_subtracted'].data, 3) for c, f in enumerate(hduls)])
    integrations = dds.shape[0]
    spatial_bins = dds.shape[1]
    spectral_bins = dds.shape[2]

    # Make the .nc file on the system
    save_directory = save_location / orbit.block
    save_directory.mkdir(parents=True, exist_ok=True)
    filename = f'apoapse-{orbit.code}-muv-dayside.nc' if dayside else f'apoapse-{orbit.code}-muv-nightside.nc'
    save_path = save_directory / filename
    nc = Dataset(save_path, 'w', format='NETCDF4')

    # Make the .nc dimensions
    nc.createDimension('integrations', size=integrations)
    nc.createDimension('spatial_bins', size=spatial_bins)
    nc.createDimension('spectral_bins', size=spectral_bins)
    nc.createDimension('pixel_corners', size=5)

    # Make the .nc structure
    apoapse = nc.createGroup('apoapse')
    binning = nc.createGroup('binning')
    detector = nc.createGroup('detector')
    observation = nc.createGroup('observation')
    pixel_geometry = nc.createGroup('pixel_geometry')
    spacecraft_geometry = nc.createGroup('spacecraft_geometry')

    return nc, apoapse, binning, detector, observation, pixel_geometry, spacecraft_geometry


def fill_detector_group(detector, hduls: [list]):
    raw = detector.createVariable('raw', 'f4', ('dayside_integrations', 'dayside_spatial_bins', 'dayside_spectral_bins'))
    raw.units = 'DN'
    raw[:] = np.vstack([add_dim_if_necessary(f['detector_raw'].data, 3) for f in hduls])

    dds = detector.createVariable('dark_subtracted', 'f4', ('dayside_integrations', 'dayside_spatial_bins', 'dayside_spectral_bins'))
    dds.units = 'DN'




def add_dim_if_necessary(arr, expected_dims):
    return arr if np.ndim(arr) == expected_dims else arr[None, :]






def create_apoapse_muv_nc_file_from_fits(data_path: Path, orbit: int, save_location: Path):
    orbit = Orbit(orbit)
    fits_files = find_latest_apoapse_muv_file_paths_from_block(data_path, orbit.orbit)
    hduls = [fits.open(f) for f in fits_files]

    # Get info from the fits files
    dayside_files = np.array([f['observation'].data['mcp_volt'][0] < pu.day_night_voltage_boundary for f in hduls])
    try:
        dayside_dds = np.vstack([add_dim_if_necessary(f['detector_dark_subtracted'].data, 3) for c, f in enumerate(hduls) if dayside_files[c]])
        dayside_integrations = dayside_dds.shape[0]
        dayside_spatial_bins = dayside_dds.shape[1]
        dayside_spectral_bins = dayside_dds.shape[2]
    except ValueError:
        dayside_integrations = 0
        dayside_spatial_bins = 0
        dayside_spectral_bins = 0
    try:
        nightside_dds = np.vstack([add_dim_if_necessary(f['detector_dark_subtracted'].data, 3) for c, f in enumerate(hduls) if not dayside_files[c]])
        nightside_integrations = nightside_dds.shape[0]
        nightside_spatial_bins = nightside_dds.shape[1]
        nightside_spectral_bins = nightside_dds.shape[2]
    except ValueError:
        nightside_integrations = 0
        nightside_spatial_bins = 0
        nightside_spectral_bins = 0

    # Make the .nc file on the system
    save_directory = save_location / orbit.block
    save_directory.mkdir(parents=True, exist_ok=True)
    save_path = save_directory / f'apoapse-{orbit.code}-muv.nc'
    nc = Dataset(save_path, 'w', format='NETCDF4')

    # Make the .nc structure
    nc.createDimension('dayside_integrations', size=dayside_integrations)
    nc.createDimension('dayside_spatial_bins', size=dayside_spatial_bins)
    nc.createDimension('dayside_spectral_bins', size=dayside_spectral_bins)

    nc.createDimension('nightside_integrations', size=nightside_integrations)
    nc.createDimension('nightside_spatial_bins', size=nightside_spatial_bins)
    nc.createDimension('nightside_spectral_bins', size=nightside_spectral_bins)

    nc.createDimension('total_integrations', size=dayside_integrations + nightside_integrations)

    nc.createDimension('pixel_corners', size=5)

    # Make the .nc groupings
    dayside_detector = nc.createGroup('dayside_detector')
    dayside_pixelgeometry = nc.createGroup('dayside_pixelgeometry')
    dayside_binning = nc.createGroup('dayside_binning')
    dayside_observation = nc.createGroup('dayside_observation')

    nightside_detector = nc.createGroup('nightside_detector')
    nightside_pixelgeometry = nc.createGroup('nightside_pixelgeometry')
    nightside_binning = nc.createGroup('nightside_binning')
    nightside_observation = nc.createGroup('nightside_observation')

    integration = nc.createGroup('integration')
    apoapse = nc.createGroup('apoapse')

    # Fill in the dayside detector
    raw = dayside_detector.createVariable('raw', 'f4', ('dayside_integrations', 'dayside_spatial_bins', 'dayside_spectral_bins'))
    raw.units = 'DN'
    dds = dayside_detector.createVariable('dark_subtracted', 'f4', ('dayside_integrations', 'dayside_spatial_bins', 'dayside_spectral_bins'))
    dds.units = 'DN'
    if dayside_integrations != 0:
        raw[:] = np.vstack([add_dim_if_necessary(f['detector_raw'].data, 3) for c, f in enumerate(hduls) if dayside_files[c]])
        dds[:] = dayside_dds

    # Fill in the dayside pixelgeometry
    latitude = dayside_pixelgeometry.createVariable('latitude', 'f8', ('dayside_integrations', 'dayside_spatial_bins', 'pixel_corners'))
    latitude.units = 'Degrees [N]'
    longitude = dayside_pixelgeometry.createVariable('longitude', 'f8', ('dayside_integrations', 'dayside_spatial_bins', 'pixel_corners'))
    longitude.units = 'Degrees [E]'
    tangent_altitude = dayside_pixelgeometry.createVariable('tangent_altitude', 'f8', ('dayside_integrations', 'dayside_spatial_bins', 'pixel_corners'))
    tangent_altitude.units = 'km'
    local_time = dayside_pixelgeometry.createVariable('local_time', 'f8', ('dayside_integrations', 'dayside_spatial_bins'))
    local_time.units = 'Hours'
    solar_zenith_angle = dayside_pixelgeometry.createVariable('solar_zenith_angle', 'f8', ('dayside_integrations', 'dayside_spatial_bins'))
    solar_zenith_angle.units = 'Degrees'
    emission_angle = dayside_pixelgeometry.createVariable('emission_angle', 'f8', ('dayside_integrations', 'dayside_spatial_bins'))
    emission_angle.units = 'Degrees'
    phase_angle = dayside_pixelgeometry.createVariable('phase_angle', 'f8', ('dayside_integrations', 'dayside_spatial_bins'))
    phase_angle.units = 'Degrees'

    if dayside_integrations != 0:
        latitude[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_corner_lat'], 3) for c, f in enumerate(hduls) if dayside_files[c]])
        longitude[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_corner_lon'], 3) for c, f in enumerate(hduls) if dayside_files[c]])
        tangent_altitude[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_corner_mrh_alt'], 3) for c, f in enumerate(hduls) if dayside_files[c]])
        local_time[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_local_time'], 2) for c, f in enumerate(hduls) if dayside_files[c]])
        solar_zenith_angle[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_solar_zenith_angle'], 2) for c, f in enumerate(hduls) if dayside_files[c]])
        emission_angle[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_emission_angle'], 2) for c, f in enumerate(hduls) if dayside_files[c]])
        phase_angle[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_phase_angle'], 2) for c, f in enumerate(hduls) if dayside_files[c]])

    # Fill in the dayside binning
    spatial_pixel_low = dayside_binning.createVariable('spatial_pixel_low', 'i2', ('dayside_spatial_bins',))
    spatial_pixel_low.units = 'Bin'
    spatial_pixel_high = dayside_binning.createVariable('spatial_pixel_high', 'i2', ('dayside_spatial_bins',))
    spatial_pixel_high.units = 'Bin'
    spectral_pixel_low = dayside_binning.createVariable('spectral_pixel_low', 'i2', ('dayside_spectral_bins',))
    spectral_pixel_low.units = 'Bin'
    spectral_pixel_high = dayside_binning.createVariable('spectral_pixel_high', 'i2', ('dayside_spectral_bins',))
    spectral_pixel_high.units = 'Bin'

    spatial_bin_width = dayside_binning.createVariable('spatial_bin_width', 'i2')
    spatial_bin_width.units = 'Pixels'
    spectral_bin_width = dayside_binning.createVariable('spectral_bin_width', 'i2')
    spectral_bin_width.units = 'Pixels'

    if dayside_integrations != 0:
        first_dayside_file = np.argmax(dayside_files)
        spatial_pixel_low[:] = hduls[first_dayside_file]['binning'].data['spapixlo']
        spatial_pixel_high[:] = hduls[first_dayside_file]['binning'].data['spapixhi']
        spectral_pixel_low[:] = hduls[first_dayside_file]['binning'].data['spepixlo']
        spectral_pixel_high[:] = hduls[first_dayside_file]['binning'].data['spepixhi']

        spatial_bin_width[:] = int(np.median(hduls[first_dayside_file]['binning'].data['spabinwidth'][0, 1:-1]))
        spectral_bin_width[:] = int(np.median(hduls[first_dayside_file]['binning'].data['spebinwidth'][0, 1:-1]))

    # Fill in the dayside observation
    integration_time = dayside_observation.createVariable('integration_time', 'f8')
    integration_time.units = 'seconds'
    voltage = dayside_observation.createVariable('voltage', 'f8')
    voltage.units = 'V'
    voltage_gain = dayside_observation.createVariable('voltage_gain', 'f8')
    voltage_gain.units = 'V'

    if dayside_integrations != 0:
        first_dayside_file = np.argmax(dayside_files)
        integration_time[:] = hduls[first_dayside_file]['observation'].data['int_time'][0]
        voltage[:] = hduls[first_dayside_file]['observation'].data['mcp_volt'][0]
        voltage_gain[:] = hduls[first_dayside_file]['observation'].data['mcp_gain'][0]

    # Fill in the nightside detector
    raw = nightside_detector.createVariable('raw', 'f4', ('nightside_integrations', 'nightside_spatial_bins', 'nightside_spectral_bins'))
    raw.units = 'DN'
    dds = nightside_detector.createVariable('dark_subtracted', 'f4', ('nightside_integrations', 'nightside_spatial_bins', 'nightside_spectral_bins'))
    dds.units = 'DN'
    if nightside_integrations != 0:
        raw[:] = np.vstack([add_dim_if_necessary(f['detector_raw'].data, 3) for c, f in enumerate(hduls) if not dayside_files[c]])
        dds[:] = nightside_dds

    # Fill in the nightside pixelgeometry
    latitude = nightside_pixelgeometry.createVariable('latitude', 'f8', ('nightside_integrations', 'nightside_spatial_bins', 'pixel_corners'))
    latitude.units = 'Degrees [N]'
    longitude = nightside_pixelgeometry.createVariable('longitude', 'f8', ('nightside_integrations', 'nightside_spatial_bins', 'pixel_corners'))
    longitude.units = 'Degrees [E]'
    tangent_altitude = nightside_pixelgeometry.createVariable('tangent_altitude', 'f8', ('nightside_integrations', 'nightside_spatial_bins', 'pixel_corners'))
    tangent_altitude.units = 'km'
    local_time = nightside_pixelgeometry.createVariable('local_time', 'f8', ('nightside_integrations', 'nightside_spatial_bins'))
    local_time.units = 'Hours'
    solar_zenith_angle = nightside_pixelgeometry.createVariable('solar_zenith_angle', 'f8', ('nightside_integrations', 'nightside_spatial_bins'))
    solar_zenith_angle.units = 'Degrees'
    emission_angle = nightside_pixelgeometry.createVariable('emission_angle', 'f8', ('nightside_integrations', 'nightside_spatial_bins'))
    emission_angle.units = 'Degrees'
    phase_angle = nightside_pixelgeometry.createVariable('phase_angle', 'f8', ('nightside_integrations', 'nightside_spatial_bins'))
    phase_angle.units = 'Degrees'

    if nightside_integrations != 0:
        latitude[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_corner_lat'], 3) for c, f in enumerate(hduls) if not dayside_files[c]])
        longitude[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_corner_lon'], 3) for c, f in enumerate(hduls) if not dayside_files[c]])
        tangent_altitude[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_corner_mrh_alt'], 3) for c, f in enumerate(hduls) if not dayside_files[c]])
        local_time[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_local_time'], 2) for c, f in enumerate(hduls) if not dayside_files[c]])
        solar_zenith_angle[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_solar_zenith_angle'], 2) for c, f in enumerate(hduls) if not dayside_files[c]])
        emission_angle[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_emission_angle'], 2) for c, f in enumerate(hduls) if not dayside_files[c]])
        phase_angle[:] = np.vstack([add_dim_if_necessary(f['pixelgeometry'].data['pixel_phase_angle'], 2) for c, f in enumerate(hduls) if not dayside_files[c]])

    # Fill in the nightside binning
    spatial_pixel_low = nightside_binning.createVariable('spatial_pixel_low', 'i2', ('nightside_spatial_bins',))
    spatial_pixel_low.units = 'Bin'
    spatial_pixel_high = nightside_binning.createVariable('spatial_pixel_high', 'i2', ('nightside_spatial_bins',))
    spatial_pixel_high.units = 'Bin'
    spectral_pixel_low = nightside_binning.createVariable('spectral_pixel_low', 'i2', ('nightside_spatial_bins',))
    spectral_pixel_low.units = 'Bin'
    spectral_pixel_high = nightside_binning.createVariable('spectral_pixel_high', 'i2', ('nightside_spatial_bins',))
    spectral_pixel_high.units = 'Bin'

    spatial_bin_width = nightside_binning.createVariable('spatial_bin_width', 'i2')
    spatial_bin_width.units = 'Pixels'
    spectral_bin_width = nightside_binning.createVariable('spectral_bin_width', 'i2')
    spectral_bin_width.units = 'Pixels'

    if nightside_integrations != 0:
        first_nightside_file = np.argmin(dayside_files)
        spatial_pixel_low[:] = hduls[first_nightside_file]['binning'].data['spapixlo']
        spatial_pixel_high[:] = hduls[first_nightside_file]['binning'].data['spapixhi']
        spectral_pixel_low[:] = hduls[first_nightside_file]['binning'].data['spepixlo']
        spectral_pixel_high[:] = hduls[first_nightside_file]['binning'].data['spepixhi']

        spatial_bin_width[:] = int(np.median(hduls[first_nightside_file]['binning'].data['spabinwidth'][0, 1:-1]))
        spectral_bin_width[:] = int(np.median(hduls[first_nightside_file]['binning'].data['spebinwidth'][0, 1:-1]))

    # Fill in the nightside observation
    integration_time = nightside_observation.createVariable('integration_time', 'f8')
    integration_time.units = 'seconds'
    voltage = nightside_observation.createVariable('voltage', 'f8')
    voltage.units = 'V'
    voltage_gain = nightside_observation.createVariable('voltage_gain', 'f8')
    voltage_gain.units = 'V'

    if nightside_integrations != 0:
        first_nightside_file = np.argmin(dayside_files)
        integration_time[:] = hduls[first_nightside_file]['observation'].data['int_time'][0]
        voltage[:] = hduls[first_nightside_file]['observation'].data['mcp_volt'][0]
        voltage_gain[:] = hduls[first_nightside_file]['observation'].data['mcp_gain'][0]

    # Fill in the integration
    ephemeris_time = integration.createVariable('ephemeris_time', 'f8')
    ephemeris_time.units = 'seconds after J2000'
    ephemeris_time[:] = np.concatenate([f['integration'].data['et'] for f in hduls])

    field_of_view = integration.createVariable('field_of_view', 'f8')
    field_of_view.units = 'Degrees'
    field_of_view[:] = np.concatenate([f['integration'].data['fov_deg'] for f in hduls])

    swath_number = integration.createVariable('swath_number', 'i2')
    swath_number[:] = pu.swath_number(field_of_view[:])

    dayside = integration.createVariable('dayside', 'bool')

    relay = integration.createVariable('relay', 'bool')



    # Fill in the apoapse

    nc.close()


if __name__ == '__main__':
    p = Path('/media/kyle/McDataFace/iuvsdata/production')
    s = Path('/media/kyle/McDataFace/iuvsdata/apoapse')
    o = Orbit(3453)
    create_apoapse_muv_nc_file_from_fits(p, o.orbit, s)

    test = Dataset(s / o.block / f'apoapse-{o.code}-muv.nc', "r", format="NETCDF4")
    print(test)

    print(test['dayside_observation']['voltage'][:])

    pg = test['dayside_binning']
    lt = pg['spatial_bin_width'][:]
    b = pg['spatial_pixel_low'][:]
    print(lt)
    print(b)

    pg = test['nightside_binning']
    lt = pg['spatial_bin_width'][:]
    b = pg['spatial_pixel_low'][:]
    print(lt)
    print(b)

    raise SystemExit(9)

    files = find_latest_apoapse_muv_file_paths_from_block(p, 3453)

    # Get some test data
    hduls = [fits.open(f) for f in files]
    print(hduls[0].info())
    print(hduls[0]['observation'].data.columns)
    raise SystemExit(9)
    for f in hduls:
        print(f['primary'].data.shape)
    raise SystemExit(9)
    print(hduls[0]['pixelgeometry'].data.columns)
    '''
    test = Dataset("/home/kyle/orbit03453.nc", "w", format="NETCDF4")
    pixelgeo = test.createGroup('pixel-geometry')
    test.createDimension('integrations', size=sza.shape[0])
    test.createDimension('spatial-bins', size=sza.shape[1])

    nsza = pixelgeo.createVariable("solar-zenith-angle", "f8", ("integrations", 'spatial-bins'))
    nsza.units = 'degrees'
    print(nsza)
    nsza[:] = sza
    print(nsza)

    test.close()

    test = Dataset("/home/kyle/orbit03453.nc", "r", format="NETCDF4")
    g = test['pixel-geometry']
    szaf = g['solar-zenith-angle']
    print(szaf)
    f = szaf[:]
    print(type(f))
    print(f.shape)
    print(f)

    print(f / sza)
    print(np.array_equal(f, sza))'''

