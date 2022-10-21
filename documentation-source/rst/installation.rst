Installation
============

.. tip::
   We recommend using virtual environments when installing PyUVS.

To install PyUVS, first clone the repository using
``git clone https://github.com/kconnour/PyUVS.git`` or your favorite git
client. Then, install it using
``<path to python interpreter> -m pip install <path to PyUVS>``. For example,
when I'm in the PyUVS directory this looks like
``/home/kyle/repos/PyUVS/venv/bin/python -m pip install .`` for me.

You can now import pyuvs with ``import pyuvs``. We recommend the syntax
``import pyuvs as pu`` so your hopes aren't too high.

.. note::
   This will install the base pyuvs library and its dependencies. The PyUVS
   project comes with additional scripts for making data, creating images,
   and performing radiative transfer.

Setup
-----
Regardless of which product you want to make, you'll need additional
information. Specifically, this includes the flatfield, detector sensitivity
curve, voltage correction, etc. I plan to have scripts that create these
binarized arrays from the IUVS data (this way I'm not version controlling
binarized files!) but for now, please add them manually.

Data
----
I'll add these when the time comes.

Images
------
I'll add these when the time comes.

Radiative Transfer
------------------
I'll add these when the time comes.

Data Files
==========
I assume that the data is organized according to the IUVS standard:

| IUVS-root
| ├── spice
| └── iuvs-data
|     ├── production
|     │   ├── orbitXXXXX
|     └── stage
|         ├── orbitXXXXX