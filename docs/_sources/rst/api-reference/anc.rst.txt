Ancillary files
===============
Once you've downloaded the data from the OneDrive link from the installation,
you can easily access the ancillary files with these functions.

Maps
----
.. autosummary::
   :toctree: generated/

   pyuvs.load_map_magnetic_field_closed_probability
   pyuvs.load_map_magnetic_field_open_probability
   pyuvs.load_map_mars_surface

Templates
---------
.. autosummary::
   :toctree: generated/

   pyuvs.load_template_wavelengths
   pyuvs.load_template_co_cameron
   pyuvs.load_template_co_plus_1st_negative
   pyuvs.load_template_co2_plus_fdb
   pyuvs.load_template_co2_plus_uvd
   pyuvs.load_template_n2_vk
   pyuvs.load_template_no_nightglow
   pyuvs.load_template_oxygen_2972
   pyuvs.load_template_solar_continuum

Instrument
----------
Generic
~~~~~~~
.. autosummary::
   :toctree: generated/

   pyuvs.load_voltage_correction_voltage
   pyuvs.load_voltage_correction_coefficients

Far-ultraviolet
~~~~~~~~~~~~~~~
.. autosummary::
   :toctree: generated/

   pyuvs.load_fuv_sensitivity_curve_manufacturer

Mid-ultraviolet
~~~~~~~~~~~~~~~
.. autosummary::
   :toctree: generated/

   pyuvs.load_muv_flatfield
   pyuvs.load_muv_point_spread_function
   pyuvs.load_muv_sensitivity_curve_manufacturer
   pyuvs.load_muv_sensitivity_curve_observational
