import csv 
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.feature as cf
import cartopy.io.shapereader as shpreader
from scipy.interpolate import griddata 
import cmweather
import requests
import os
from matplotlib.path import Path
import geopandas as gpd
import cartopy.feature as cfeature
import shapefile  # pyshp library
from cartopy.feature import ShapelyFeature
from shapely.geometry import shape

output_dir = '/home/heron_ng/dev/HK_temp_map/output' 

# Load and plot the coastline
shapefile_path = '/home/heron_ng/dev/HK_temp_map/input/hk_coast_2022/Hong_Kong_18_Districts/HKDistrict18'
#coastfile = '/home/heron_ng/dev/HK_temp_map/input/hk_coast/Hong_Kong_Geological_Maps_in_1_to_100%2C000.shp'
shp_path = '/home/heron_ng/dev/HK_temp_map/input/hk_coast_2022/Hong_Kong_18_Districts/HKDistrict18.shp'

# Read the shapefile using pyshp
sf = shapefile.Reader(shapefile_path)
print('shape file read successful')
print(f"Number of shapes: {len(sf.shapes())}")
print(f"Fields: {sf.fields}")
print(f"First shape bounding box: {sf.shapes()[0].bbox}")

gdf = gpd.read_file(shp_path)

# Check CRS
print("CRS of the shapefile:", gdf.crs)
print(gdf.head())

selected_fids = [1, 2, 3, 4, 5] 
selected_gdf = gdf[gdf['FID'].isin(selected_fids)]

# Reproject to WGS84 (EPSG:4326)
gdf = gdf.to_crs("EPSG:4326")
print("Reprojected CRS:", gdf.crs)

# Save reprojected shapefile for future use
gdf.to_file("reprojected_HKDistrict18.shp", driver="ESRI Shapefile")
print(gdf.head())

shapefile_feature = ShapelyFeature(gdf.geometry, ccrs.PlateCarree(), facecolor='lightyellow', edgecolor='black')

# Plot the map
fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
ax.add_feature(shapefile_feature, linewidth=0.3)

# Set extent to Hong Kong region (adjust if needed)
ax.set_extent([113.7, 114.5, 22.1, 22.6], crs=ccrs.PlateCarree())
ax.gridlines(draw_labels=True)

# Save and show the map
plt.savefig(f"{output_dir}/reprojected_HKDistrict18_plot.png", dpi=500)
plt.clf()



# # # Extract shapes and convert to Shapely geometries
# # shapes = [shape(rec.shape.__geo_interface__) for rec in sf.shapeRecords()]

# # # Create a Cartopy feature from the Shapely geometries
# # print('Creating Cartopy features from the Shapely geometries')
# # shapefile_feature = ShapelyFeature(shapes, ccrs.PlateCarree(), facecolor='none', edgecolor='blue')

# # print('plotting')
# # # Set up the map
# # fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
# # ax.add_feature(cfeature.LAND, edgecolor='black')
# # ax.add_feature(cfeature.COASTLINE)

# # # Add the shapefile feature to the map
# # ax.add_feature(shapefile_feature, linewidth=1.0)

# # # Add gridlines for context
# # ax.gridlines(draw_labels=True)

# # # Set extent (optional) - adjust to your region of interest
# # ax.set_extent([113.7, 114.5, 22.1, 22.6], crs=ccrs.PlateCarree())

# # # Show the map
# # plt.savefig(f'{output_dir}/SHP_file_test.png', dpi=500)
# # print(f'fig saved to {output_dir}/SHP_file_test.png')
# # plt.clf()