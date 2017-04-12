"""
Add geometric extensions to :class:`xarray.Dataset` and :class:`xarray.DataArray` for use
with Data Cube.
"""
from affine import Affine

from utils import data_resolution_and_offset, geometry


def _xarray_affine(obj):
    dims = obj.crs.dimensions
    xres, xoff = data_resolution_and_offset(obj[dims[1]].values)
    yres, yoff = data_resolution_and_offset(obj[dims[0]].values)
    return Affine.translation(xoff, yoff) * Affine.scale(xres, yres)


def _xarray_extent(obj):
    return obj.geobox.extent


def _xarray_geobox(obj):
    dims = obj.crs.dimensions
    return geometry.GeoBox(obj[dims[1]].size, obj[dims[0]].size, obj.affine, obj.crs)

xarray.Dataset.geobox = property(_xarray_geobox)
xarray.Dataset.affine = property(_xarray_affine)
xarray.Dataset.extent = property(_xarray_extent)
xarray.DataArray.geobox = property(_xarray_geobox)
xarray.DataArray.affine = property(_xarray_affine)
xarray.DataArray.extent = property(_xarray_extent)