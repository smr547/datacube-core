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
    export PATH=$PATH:/Library/PostgreSQL/9.4/bin
    python setup.py install --user

Currently getting ``killed 9`` error

.. code-block::

   Installed /private/var/folders/wb/rrjrrn3s03dcp_zc3mcdlcch0000gn/T/easy_install-ubozq9/netCDF4-1.2.9/.eggs/Cython-0.26-py2.7-macosx-10.11-intel.egg
   Killed: 9


It may be useful to use conda to install binary packages::

    conda install psycopg2 gdal libgdal hdf5 rasterio netcdf4 libnetcdf pandas

I tried 

.. code-block::
   conda install psycopg2
   conda install gdal
   conda install rasterio
   conda install netcdf4
   conda install pandas

and then 

.. code-block::
   
    python setup.py install --user

This seemed to work but I found I could not ``import datacube`` in ``ipython``

```
In [1]: import datacube
---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
<ipython-input-1-f6e34d7a5430> in <module>()
----> 1 import datacube

/Users/stevenring/Library/Python/2.7/lib/python/site-packages/datacube-1.5.1+126.g6660608-py2.7.egg/datacube/__init__.py in <module>()
     19 from __future__ import absolute_import
     20 from .version import __version__
---> 21 from .api import Datacube
     22 from .config import set_options
     23 import warnings

/Users/stevenring/Library/Python/2.7/lib/python/site-packages/datacube-1.5.1+126.g6660608-py2.7.egg/datacube/api/__init__.py in <module>()
      5 from __future__ import absolute_import
      6
----> 7 from datacube.storage.masking import list_flag_names, describe_variable_flags, make_mask
      8 from ._api import API
      9 from .core import Datacube

/Users/stevenring/Library/Python/2.7/lib/python/site-packages/datacube-1.5.1+126.g6660608-py2.7.egg/datacube/storage/masking.py in <module>()
      9 import warnings
     10
---> 11 from datacube.utils import generate_table
     12
     13 from xarray import DataArray, Dataset

/Users/stevenring/Library/Python/2.7/lib/python/site-packages/datacube-1.5.1+126.g6660608-py2.7.egg/datacube/utils/__init__.py in <module>()
     21
     22 import dateutil.parser
---> 23 import jsonschema
     24 import netCDF4
     25 import numpy

ImportError: No module named jsonschema
```
   
work without error
.. note::

    Usage of virtual environments is recommended
