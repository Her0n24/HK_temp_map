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
# main_ax.gridlines(draw_labels=True)

# # Plot station data points
# for station_name, station_data in stations.items():
#     lat = station_data['lat']
#     lon = station_data['long']
#     T = station_data['temperature']
#     main_ax.plot(lon, lat, 'o', c= 'black', markersize= 2)
#     main_ax.text(lon, lat, f'{station_name}\nTemp: {T}°C', color='black', fontsize=5, ha='left')#, weight = 'bold')

# Filter out stations with 'N/A' temperature values
valid_stations = {name: data for name, data in stations.items() if isinstance(data.get('temperature'), float)}

# Extract longitude, latitude, and temperature data for interpolation
lon = np.array([data['long'] for data in valid_stations.values()])
lat = np.array([data['lat'] for data in valid_stations.values()])
T = np.array([data['temperature'] for data in valid_stations.values() if isinstance(data.get('temperature'), float)])

# Generate interpolated temperature data
xi = np.linspace(minlon, maxlon, 100)
yi = np.linspace(minlat, maxlat, 100)
X, Y = np.meshgrid(xi, yi)

# lon = np.array([station_data['long'] for station_data in stations.values()])
# lat = np.array([station_data['lat'] for station_data in stations.values()])
#T = np.array([station_data['temperature'] for station_data in stations.values()])
# T = np.array([data['temperature'] for data in valid_stations.values() if isinstance(data.get('temperature'), float)])

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
coastfile = '/home/heron_ng/.local/share/cartopy/shapefiles/gshhs/f/GSHHS_f_L1.shp'
#coastfile = '/home/heron_ng/dev/HK_temp_map/input/hk_coast/Hong_Kong_Geological_Maps_in_1_to_100%2C000.shp'
coastlines = shpreader.Reader(coastfile)

for geometry in coastlines.geometries():
    main_ax.add_geometries([geometry], proj, edgecolor='black', facecolor='none')

#land_polygons = [geometry for geometry in coastlines.geometries()]

# Plot the interpolated temperature data on the map

level = np.linspace(-2,45, 48 )
c = main_ax.contourf(X, Y, Z, cmap='ChaseSpectral', levels= level, transform=proj, alpha=0.8)
main_ax.add_feature(cf.OCEAN, facecolor='white', zorder = 100, edgecolor='k')
plt.colorbar(c, ax=main_ax, label='2m Temperature (°C)', ticks = np.arange(-2,45,5))

# Define the virtual station names
virtual_station_names = ['Station 1', 'Station 2', 'Station 3', 'Station 4']

# Plot station data points
for station_name, station_data in valid_stations.items():
    if station_name in virtual_station_names:
        lat = station_data['lat']
        lon = station_data['long']
        T = station_data['temperature']
    elif station_name in ['The Peak', 'Tai Mo Shan', 'Ngong Ping', "Tate's Cairn"]:
        lat = station_data['lat']
        lon = station_data['long']
        T = station_data['temperature']
        main_ax.plot(lon, lat, '^', c= 'green', markersize= 2, zorder= 101)
        main_ax.text(lon, lat, f'{station_name}\n{T}°C', color='black', fontsize=5, ha='left', zorder = 102)#, weight = 'bold')
    else:
        lat = station_data['lat']
        lon = station_data['long']
        T = station_data['temperature']
        main_ax.plot(lon, lat, 'o', c= 'black', markersize= 2, zorder= 101)
        main_ax.text(lon, lat, f'{station_name}\n{T}°C', color='black', fontsize=5, ha='left', zorder = 102)#, weight = 'bold')

plt.text(.01, .01, f'datetime {datetime} HKT', ha='left', va='bottom', transform=main_ax.transAxes, zorder = 103)

# Find the station with the lowest temperature
min_station = min(valid_stations.items(), key=lambda x: x[1]['temperature'])[0]
min_temp = valid_stations[min_station]['temperature']

# Find the station with the highest temperature
max_station = max(valid_stations.items(), key=lambda x: x[1]['temperature'])[0]
max_temp = valid_stations[max_station]['temperature']

# Output the station names and temperatures
plt.text(.99, .03, f'maximum: {max_temp}°C {max_station}', ha='right', va='bottom', transform=main_ax.transAxes, zorder = 103, fontsize=7)
plt.text(.99, .01, f'minimum: {min_temp}°C {min_station}', ha='right', va='bottom', transform=main_ax.transAxes, zorder = 103, fontsize=7)

plt.tight_layout()
plt.savefig(f'/home/heron_ng/dev/HK_temp_map/output/HK_temp_map_newcolor_{datetime}.png', dpi=500)
plt.clf()
print(f'figure output to /home/heron_ng/dev/HK_temp_map/output/HK_temp_map_newcolor_{datetime}.png')

