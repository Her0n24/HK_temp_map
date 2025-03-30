from data_loader import download_csv, load_station_data
from ocean_mask import generate_ocean_mask, load_ocean_mask
from plotter import plot_temperature_map, add_station_markers, interpolate_temperature
import constants as c
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd
import numpy as np
from shapely.geometry import shape, Point, Polygon
from cartopy.feature import ShapelyFeature


def main():
    # Paths and constants
    api_link = 'https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_temperature.csv'
    station_location_data_path = 'input/station_location.csv'
    data_input_path = 'input/latest_1min_temperature.csv'
    mask_file_path = 'input/ocean_mask.npy'
    shapefile_path = 'input/hk_coast_2022/Hong_Kong_18_Districts/reprojected_HKDistrict18.shp'

    # Step 1: Read Stations location and Download data CSV 
    stations = load_station_data(station_location_data_path)
    stations, datetime = download_csv(api_link, data_input_path, stations)
    
    # Step 2: Initialise the plot and load the shapefile
    
    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(12, 6))
    main_ax = fig.add_subplot(1, 1, 1, projection=proj)
    main_ax.set_extent([c.MINLON, c.MAXLON, c.MINLAT, c.MAXLAT], crs=proj)

    # Filter out stations with 'N/A' temperature values
    valid_stations = {name: data for name, data in stations.items() if isinstance(data.get('temperature'), float)}

    X, Y, Z = interpolate_temperature(valid_stations, method='linear')
    
    gdf = gpd.read_file(shapefile_path)
    print("CRS of the shapefile:", gdf.crs)
    
    shapefile_feature = ShapelyFeature(gdf.geometry, proj, edgecolor=(0, 0, 0, 0.5), facecolor='none')
    main_ax.add_feature(shapefile_feature, linewidth=0.5)
    
    # Step 3: Interpolate temperature
    ocean_mask = generate_ocean_mask(gdf,X, Y, Z, mask_file_path)
    
    # Mask the ocean areas with white
    masked_Z = np.ma.masked_where(ocean_mask == 1, Z)
    
    # Step 4: Plot the temperature map
    con, cbar = plot_temperature_map(X, Y, masked_Z, main_ax, proj)
    add_station_markers(main_ax, valid_stations, datetime)
    
if __name__ == "__main__":
    main()