import os
import numpy as np
import json
import sys
import rasterio as rio
import gdal
import osr
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import mapping

class AerialImage:

    def image_bbox(self, padding_pct):
        bfp = gpd.read_file(self.bfp_path)
        xmin, ymin, xmax, ymax = bfp.bounds.values[0]
        width = xmax - xmin
        height = ymax - ymin
        max_row, max_col = rio.open(self.image_path).shape[:2]
        xmin_f, xmax_f, ymin_f, ymax_f = xmin - padding_pct * width, xmax + padding_pct * width, \
                                         ymin - padding_pct * height, ymax + padding_pct * height

        xres = (xmax_f - xmin_f) / max_col
        yres = (ymax_f - ymin_f) / max_row

        return [xmin_f, ymin_f, xmax_f, ymax_f, xres, yres, max_col, max_row]

    def georeferencing(self, bfp_path, img_path, padding_pct):
        self.bfp_path = bfp_path
        self.image_path = img_path
        img_dir, img_name = os.path.dirname(self.image_path), os.path.basename(self.image_path)
        img_name, _ = os.path.splitext(img_name)
        out_path = os.path.join(img_dir, 'prj_{}.tif'.format(img_name))
        ulx, ymin, xmax, uly, xres, yres, xsize, ysize = self.image_bbox(padding_pct)

        d = rio.open(self.image_path).read()

        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(out_path, xsize, ysize, 3, gdal.GDT_Float32)

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        ds.SetProjection(srs.ExportToWkt())

        gt = [ulx, xres, 0, uly, 0, -yres]
        ds.SetGeoTransform(gt)

        for i in range(3):
            outband = ds.GetRasterBand(i + 1)
            outband.WriteArray(d[i, :, :])

        return out_path

    def extract_image(self, raster, poly):
        geometry = poly.geometry.values[0]
        geoms = [mapping(geometry)]
        out_image, out_transform = mask(raster, geoms, crop=False)

        return out_image