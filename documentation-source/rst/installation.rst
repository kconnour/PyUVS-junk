Installation
============

.. tip::
   We recommend using virtual environments when installing PyUVS.

To install PyUVS, first clone the repository using
``git clone https://github.com/kconnour/PyUVS.git`` or your favorite git
client. Regardless of which product you want to make, you'll need additional
information. These include files like spectral templates, maps of Mars,
instrumental correction arrays, and GCM runs. It's a terrible idea to
version control these files so I put them online. Download them at my
`CU OneDrive link
<https://o365coloradoedu-my.sharepoint.com/:f:/g/personal/kyco2464_colorado_edu/Es_QzcEZfo1Jh-Y675axO9MBZ68F0GhsIc1OQNvBNAnNNQ?e=FuKFRC>`_.
Place these in a folder named ``anc`` within the ``pyuvs`` folder, keeping the
same directory structure as the folder you downloaded.

Then, install ``pyuvs`` using
``<path to python interpreter> -m pip install <path to PyUVS>``. For example,
when I'm in the PyUVS directory this looks like
``/home/kyle/repos/PyUVS/venv/bin/python -m pip install .``.

You can now import pyuvs with ``import pyuvs``. We recommend the syntax
``import pyuvs as pu`` so your hopes aren't too high.

.. note::
   This will install the base pyuvs library and its dependencies. The PyUVS
   project comes with additional scripts for making data, creating images,
   and performing radiative transfer.

Data files
----------
The pyuvs library has support for the "official" data files. It assumes
that the data files are organized according to the IUVS standard:

| <IUVS-root>
| ├── spice
| └── iuvs-data
|     ├── production
|     │   ├── orbitXXXXX
|     └── stage
|         ├── orbitXXXXX

``<IUVS-root>`` can have whatever name, but the other folders have the
above naming convention. At some point, I will include a list of all the data
filenames on OneDrive.

Data
----
I'll add these when the time comes.

Images
------
I'll add these when the time comes.

Radiative Transfer
------------------
I'll add these when the time comes.
