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
from cartopy.feature import ShapelyFeature
from shapely.geometry import shape, Point, Polygon
from tqdm import tqdm


stations = {}
stations_csv_file_path = 'station_location.csv'

with open(stations_csv_file_path, mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        name = row['AutomaticWeatherStation_en']
        lat = float(row['GeometryLatitude'])
        long = float(row['GeometryLongitude'])
        stations[name] = {'lat': lat, 'long': long}

#print(stations['Tuen Mun'])

#Download the CSV file fomr HKO
api_link = 'https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_temperature.csv'

response = requests.get(api_link)

input_folder = '/home/heron_ng/dev/HK_temp_map/input'
input_data = 'latest_1min_temperature.csv'

if response.status_code == 200:
    csv_file_path = os.path.join(input_folder, input_data)
    with open(csv_file_path, 'wb') as file:
        file.write(response.content)
    print("CSV file downloaded and saved successfully.")
else:
    print(f"Failed to download CSV file. Status code: {response.status_code}")

try:
    with open(f'{input_folder}/{input_data}', mode= 'r', encoding= 'utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        print('Reading CSV')
        for row in csv_reader:
            try:
                #print(row)
                datetime = row.get('Date time')
                name = row.get('Automatic Weather Station')
                T = float(row.get('Air Temperature(degree Celsius)'))

                if name in stations:
                    stations[name]['temperature'] = T
                else:
                    print(f'an error occured. {name} station is not in the list of stations.')
            except Exception as e:
                print(f"An error occurred with station {row}: {e}")
                print(f"Ignoring the station")
                name = row.get('Automatic Weather Station')
                T = 'M'
                if name in stations:
                    stations[name]['temperature'] = T
                else:
                    print(f'an error occured. {name} station is not in the list of stations.')
except Exception as e:
    print(f"An error occurred while opening the file: {e}")
#print(stations)

minlon, maxlon, minlat, maxlat = (113.7, 114.5, 22.1, 22.6)

proj = ccrs.PlateCarree()
fig = plt.figure(figsize=(12, 6))
main_ax = fig.add_subplot(1, 1, 1, projection=proj)
main_ax.set_extent([minlon, maxlon, minlat, maxlat], crs=proj)

# Filter out stations with 'N/A' temperature values
valid_stations = {name: data for name, data in stations.items() if isinstance(data.get('temperature'), float)}

# Extract longitude, latitude, and temperature data for interpolation
lon = np.array([data['long'] for data in valid_stations.values()])
lat = np.array([data['lat'] for data in valid_stations.values()])
T = np.array([data['temperature'] for data in valid_stations.values() if isinstance(data.get('temperature'), float)])

# Generate interpolated temperature data
xi = np.linspace(minlon, maxlon, 400)
yi = np.linspace(minlat, maxlat, 400)
X, Y = np.meshgrid(xi, yi)

# Calculate the average temperature value from all existing stations
avg_temperature = np.mean([data['temperature'] for data in valid_stations.values()])

# Define the coordinates for the four virtual stations at the edges of the map
virtual_stations = {
    'Station 1': {'lat': minlat, 'long': minlon, 'temperature': avg_temperature},
    'Station 2': {'lat': minlat, 'long': maxlon, 'temperature': avg_temperature},
    'Station 3': {'lat': maxlat, 'long': minlon, 'temperature': avg_temperature},
    'Station 4': {'lat': maxlat, 'long': maxlon, 'temperature': avg_temperature}
}

# Add the virtual stations to the station data
valid_stations.update(virtual_stations)

# Generate interpolated temperature data with the virtual stations included
lon = np.array([station_data['long'] for station_data in valid_stations.values()])
lat = np.array([station_data['lat'] for station_data in valid_stations.values()])
T = np.array([data['temperature'] for data in valid_stations.values() if isinstance(data.get('temperature'), float)])

Z = griddata((lon, lat), T, (X, Y), method='linear')
print('plotting')

# Load and plot the coastline
coastfile = '/home/heron_ng/dev/HK_temp_map/input/hk_coast_2022/Hong_Kong_18_Districts/reprojected_HKDistrict18.shp'
coastlines = shpreader.Reader(coastfile)
shp_path = '/home/heron_ng/dev/HK_temp_map/input/hk_coast_2022/Hong_Kong_18_Districts/reprojected_HKDistrict18.shp'

gdf = gpd.read_file(shp_path)
# Check CRS
print("CRS of the shapefile:", gdf.crs)

# Add coastline and border features from shapefile
shapefile_feature = ShapelyFeature(gdf.geometry, proj, edgecolor=(0, 0, 0, 0.5), facecolor='none')
main_ax.add_feature(shapefile_feature, linewidth=0.5)

# Create a mask for the ocean (areas outside the shape)
ocean_mask = np.ones_like(Z)  # Initialize all as "ocean" (1)
# Calculate total iterations for tqdm
total_iterations = len(gdf) * Z.shape[0] * Z.shape[1]

# Use tqdm with total iterations
with tqdm(total=total_iterations) as pbar:
    for _, row in gdf.iterrows():  # Iterate over polygons
        polygon = row['geometry']  # Get the polygon
        for i in range(Z.shape[0]):  # Iterate over rows
            for j in range(Z.shape[1]):  # Iterate over columns
                point = Point(X[i, j], Y[i, j])  # Create a Shapely Point
                if polygon.contains(point):  # Check if the point is within the polygon
                    ocean_mask[i, j] = 0  # Mark as "land" (0)
                pbar.update(1)  # Update progress bar

# Mask the ocean areas with white
masked_Z = np.ma.masked_where(ocean_mask == 1, Z)

# plt.imshow(ocean_mask, origin='lower', extent=(minlon, maxlon, minlat, maxlat), cmap='gray')
# plt.title('Ocean Mask (1 = Ocean, 0 = Land)')
# plt.colorbar(label='Mask Value')
# plt.savefig('/home/heron_ng/dev/HK_temp_map/output/HK_temp_map_newcolor_shapefile_polygon.png')
# plt.clf()

# Plot the temperature data
c = main_ax.contourf(X, Y, masked_Z, cmap='ChaseSpectral', levels=np.linspace(-2, 40, 43), transform=proj, alpha=0.8)

# Add a white contour line at 0 degrees
main_ax.contour(X, Y, masked_Z, levels=[0], colors='magenta', linewidths=0.5, transform=proj)
main_ax.contour(X, Y, masked_Z, levels=[8], colors='lightgrey', linewidths=0.5, transform=proj)
main_ax.contour(X, Y, masked_Z, levels=[12], colors='white', linewidths=0.5, transform=proj)
main_ax.contour(X, Y, masked_Z, levels=[33], colors='white', linewidths=0.5, transform=proj)
main_ax.contour(X, Y, masked_Z, levels=[35], colors='fuchsia', linewidths=0.5, transform=proj)

# # Add a white overlay for the ocean
# ocean_overlay = np.ma.masked_where(ocean_mask == 0, Z)  # Mask land areas
# main_ax.contourf(X, Y, ocean_overlay, colors='white', transform=proj, alpha=1, zorder=100)

# Add the coastline
# for _, row in gdf.iterrows():
#     main_ax.add_geometries([row['geometry']], crs=proj, edgecolor='black', facecolor='none', linewidth=0.5)
cbar = plt.colorbar(c, ax=main_ax, label='2m Temperature (°C)', ticks = np.arange(-2,40,5))


temperature_level = 12
cbar.ax.axhline(temperature_level, color="white", linewidth=1)  # Add line
temperature_level = 8
cbar.ax.axhline(temperature_level, color="lightgrey", linewidth=1)  # Add line
temperature_level = 0
cbar.ax.axhline(temperature_level, color="magenta", linewidth=1)  # Add line
temperature_level = 33
cbar.ax.axhline(temperature_level, color="white", linewidth=1)  # Add line
temperature_level = 35
cbar.ax.axhline(temperature_level, color="fuchsia", linewidth=1)  # Add line

# Define the virtual station names
virtual_station_names = ['Station 1', 'Station 2', 'Station 3', 'Station 4']

# Plot station data points
for station_name, station_data in tqdm(valid_stations.items()):
    if station_name in virtual_station_names:
        lat = station_data['lat']
        lon = station_data['long']
        T = station_data['temperature']
    elif station_name in ['The Peak', 'Tai Mo Shan', 'Ngong Ping', "Tate's Cairn"]:
        lat = station_data['lat']
        lon = station_data['long']
        T = station_data['temperature']
        main_ax.plot(lon, lat, '^', c= 'green', markersize= 2, zorder= 101)
        main_ax.text(lon, lat, f'{station_name}\n{T}°C', color='black', fontsize=7, ha='left', zorder = 102)#, weight = 'bold')
    else:
        lat = station_data['lat']
        lon = station_data['long']
        T = station_data['temperature']
        main_ax.plot(lon, lat, 'o', c= 'black', markersize= 2, zorder= 101)
        main_ax.text(lon, lat, f'{station_name}\n{T}°C', color='black', fontsize=7, ha='left', zorder = 102)#, weight = 'bold')

plt.text(.01, .01, f'datetime {datetime} HKT', ha='left', va='bottom', transform=main_ax.transAxes, zorder = 103)

# Find the station with the lowest temperature
min_station = min(valid_stations.items(), key=lambda x: x[1]['temperature'])[0]
min_temp = valid_stations[min_station]['temperature']

# Find the station with the highest temperature
max_station = max(valid_stations.items(), key=lambda x: x[1]['temperature'])[0]
max_temp = valid_stations[max_station]['temperature']

# Output the station names and temperatures
plt.text(.99, .03, f'maximum: {max_temp}°C {max_station}', ha='right', va='bottom', transform=main_ax.transAxes, zorder = 103, fontsize=7, color = 'red')
plt.text(.99, .01, f'minimum: {min_temp}°C {min_station}', ha='right', va='bottom', transform=main_ax.transAxes, zorder = 103, fontsize=7, color = 'blue')

plt.tight_layout()
plt.savefig(f'/home/heron_ng/dev/HK_temp_map/output/HK_temp_map_newcolor_{datetime}_2022_coast.png', dpi=500)
plt.clf()
print(f'figure output to /home/heron_ng/dev/HK_temp_map/output/HK_temp_map_newcolor_{datetime}_2022_coast.png')