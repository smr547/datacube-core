========
Mac OS X
========

.. note::

    This section was typed up from memory. Verification and input would be appreciated.

Required software
-----------------
Homebrew::

    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

HDF5, netCDF4, and GDAL::

   brew install hdf5
   brew install homebrew/science/netcdf
   brew install gdal
   brew install libyaml

Python and packages
-------------------
Python 2.7 and 3.5+ are supported.

Download the latest version of the software from the `repository <https://github.com/opendatacube/datacube-core>`_ and install it::

    git clone https://github.com/opendatacube/datacube-core
    cd datacube-core
    git checkout develop
    python setup.py install --user

It may be useful to use conda to install binary packages::

    conda install psycopg2 gdal libgdal hdf5 rasterio netcdf4 libnetcdf pandas

.. note::

    Usage of virtual environments is recommended
