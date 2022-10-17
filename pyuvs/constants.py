"""This module contains constants relevant to IUVS.

Most of the values here come from the seminal `IUVS paper
<https://link.springer.com/article/10.1007/s11214-014-0098-7>`_.
"""
import numpy as np


spatial_slit_thickness: float = 0.1
"""Thickness of the slit [mm].

Notes
-----
This values comes from Table 3 (p. 91) of the IUVS paper. 
"""

spatial_slit_length: float = 19.8
"""Length of the slit [mm].

Notes
-----
This values comes from Table 3 (p. 91) of the IUVS paper. 
"""

telescope_focal_length: float = 99.5
"""Focal length of the IUVS telescope mirror [mm].

Notes
-----
This values comes from an email Alan Hoskins where he noted that he used this
value in his ray tracing code. The IUVS paper simply notes this value is 
100 mm (see Table 3, p. 91) with only 1 significant figure. 
"""

angular_slit_width: float = spatial_slit_length / telescope_focal_length * \
                            180 / np.pi
"""Width of the slit [degrees]."""

# TODO: is this the IUVS pipeline value? OR is it 24/1024
pixel_length: float = 22/1024
"""Length of an IUVS detector pixel [mm].

Notes
-----
This values is derived from figure 11 of the IUVS paper, where the pixel length
is simply the length of the detector divided by 1024 pixels.
"""

pixel_angular_size: float = pixel_length / telescope_focal_length * \
                            spatial_slit_thickness / telescope_focal_length
"""Angular size of a detector pixel [sr]. """

minimum_mirror_angle: float = 30.2508544921875
"""Minimum angle [degrees] the scan mirror can obtain.

Notes
-----
This value comes from Justin Deighan.
"""

maximum_mirror_angle: float = 59.6502685546875
"""Maximum angle [degrees] the scan mirror can obtain.

Notes
-----
This value comes from Justin Deighan.
"""

day_night_voltage_boundary: int = 790
"""Voltage defining the boundary between dayside and nightside settings."""
