About IUVS
==========

IUVS is the Imaging Ultraviolet Spectrograph instrument aboard the MAVEN
mission. For a detailed description of the instrument, check out the
`IUVS instrument paper
<https://link.springer.com/article/10.1007/s11214-014-0098-7>`_.
Some highlights and information on the binning is described below.

Generic
-------
IUVS is a 1024x1024 pixel detector with a slit on top. Thus, one axis
represents the spatial (along-slit) dimension and another represents the
spectral dimension. We move the scan mirror each integration and by "stacking"
these integrations, we can build up an 2D image (each integration is a 1D
image). After scanning across the planet we reset the scan mirror and scan at
other locations, and collectively these make up swaths.

Observing Modes
---------------
IUVS observes using the following modes:

* Apoapse
* Periapse
* Inlimb
* Outlimb
* Incorona
* Outcorona
* Relay-echelle
* Star
* Sun-charge

Additionally, there may be some one-off observations like observations of
Phobos, interstellar objects, etc. Note that due to MAVEN's precessing orbit,
any given mode may be on the dayside or nightside and the sub-spacecraft
latitude will slowly change.

Apoapse
~~~~~~~
Apoapse is the largest volume dataset on IUVS. The resolution frequently changes
when we use dayside settings. At the start of the mission we used 10 spatial
bins and around 30 spectral bins, but the dayside spectra are relatively
featureless so we switched to higher spatial resolution and lower spectral
resolution. 133 x 19 (spatial x spectral) is a common resolution, as is 50 x 19.
Occasionally we use 15 or 20 spectral bins. In any case, beware that these
may change frequently!
