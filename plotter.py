import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import numpy as np
from scipy.interpolate import griddata
import constants as c
import cmweather
from datetime import datetime

def interpolate_temperature(valid_stations, method='linear'):
    """
    Interpolates temperature data using griddata from scipy.
    
    Parameters:
    valid_stations (dict): Dictionary containing station names and their attributes.
    T (array-like): Temperature values at the stations.
    method (str): Interpolation method to use. Default is 'linear'.
    
    Returns:
    X (array-like): Longitudes of the grid points.
    Y (array-like): Latitudes of the grid points.
    Z (array-like): Interpolated temperature values on the grid.
    
    """
    # Extract longitude, latitude, and temperature data for interpolation
    lon = np.array([data['long'] for data in valid_stations.values()])
    lat = np.array([data['lat'] for data in valid_stations.values()])
    T = np.array([data['temperature'] for data in valid_stations.values() if isinstance(data.get('temperature'), float)])

    # Generate interpolated temperature data
    xi = np.linspace(c.MINLON, c.MAXLON, 400)
    yi = np.linspace(c.MINLAT, c.MAXLAT, 400)
    X, Y = np.meshgrid(xi, yi)
    
    # Calculate the average temperature value from all existing stations
    avg_temperature = np.mean([data['temperature'] for data in valid_stations.values()])

    # Define the coordinates for the four virtual stations at the edges of the map
    virtual_stations = {
    'Station 1': {'lat': c.MINLAT, 'long': c.MINLON, 'temperature': avg_temperature},
    'Station 2': {'lat': c.MINLAT, 'long': c.MAXLON, 'temperature': avg_temperature},
    'Station 3': {'lat': c.MAXLAT, 'long': c.MINLON, 'temperature': avg_temperature},
    'Station 4': {'lat': c.MAXLAT, 'long': c.MAXLON, 'temperature': avg_temperature}
    }
    
    # Add the virtual stations to the station data
    valid_stations.update(virtual_stations)
        
    # Generate interpolated temperature data with the virtual stations included
    lon = np.array([station_data['long'] for station_data in valid_stations.values()])
    lat = np.array([station_data['lat'] for station_data in valid_stations.values()])
    T = np.array([data['temperature'] for data in valid_stations.values() if isinstance(data.get('temperature'), float)])

    Z = griddata((lon, lat), T, (X, Y), method=method)
    return X, Y, Z

def plot_temperature_map(X, Y, masked_Z, main_ax, proj, label:str = '2m Temperature (°C)'):
    """
    Plots the temperature map using contourf.
    
    Parameters:
    X (array-like): Longitudes of the grid points.
    Y (array-like): Latitudes of the grid points.
    masked_Z (array-like): Interpolated temperature values on the grid.
    main_ax (matplotlib.axes.Axes): The axes on which to plot the temperature map.
    
    valid_stations (list): List of valid station names to be marked on the map.
    
    
    Returns:
    matplotlib.contour.QuadContourSet: The contour set created by contourf.
    
    """
    con = main_ax.contourf(X, Y, masked_Z, cmap='ChaseSpectral', levels=np.linspace(c.MINTEMP, c.MAXTEMP, (c.MAXTEMP - c.MINTEMP + 1)), alpha=0.8)
    
    # Add contour lines for specific temperature levels
    main_ax.contour(X, Y, masked_Z, levels=[c.FRZE_LVL], colors='magenta', linewidths=0.5, transform=proj)
    main_ax.contour(X, Y, masked_Z, levels=[c.VCOLD_LVL], colors='lightgrey', linewidths=0.5, transform=proj)
    main_ax.contour(X, Y, masked_Z, levels=[c.COLD_LVL], colors='white', linewidths=0.5, transform=proj)
    main_ax.contour(X, Y, masked_Z, levels=[c.VHOT_LVL], colors='white', linewidths=0.5, transform=proj)
    main_ax.contour(X, Y, masked_Z, levels=[c.EHOT_LVL], colors='fuchsia', linewidths=0.5, transform=proj)
    
    cbar = plt.colorbar(con, ax=main_ax, label=label)
    
    cbar.ax.axhline(c.COLD_LVL, color="white", linewidth=1)  # Add line
    cbar.ax.axhline(c.VCOLD_LVL, color="lightgrey", linewidth=1)  # Add line
    cbar.ax.axhline(c.FRZE_LVL, color="magenta", linewidth=1)  # Add line
    cbar.ax.axhline(c.VHOT_LVL, color="white", linewidth=1)  # Add line
    cbar.ax.axhline(c.EHOT_LVL, color="fuchsia", linewidth=1)  # Add line

    
    return con, cbar

def add_station_markers(main_ax, valid_stations, datetime_str):
    """
    Adds markers for valid stations on the map.
    
    Parameters:
    main_ax (matplotlib.axes.Axes): The axes on which to plot the station markers.
    valid_stations (dict): Dictionary containing station names and their attributes.
    
    Returns:
    None
    
    """
    for station_name, station_data in valid_stations.items():
        if station_name in c.VIRTUAL_STATIONS:
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
    
    time_str_filename = datetime_str
    # Parse the datetime string
    dt = datetime.strptime(datetime_str, "%Y%m%d%H%M")
    # Format the datetime object into a human-readable string
    datetime_str = dt.strftime("%B %d, %Y, %H:%M")
    
    plt.text(.01, .01, f'datetime {datetime_str} HKT', ha='left', va='bottom', transform=main_ax.transAxes, zorder = 103)

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
    plt.savefig(f'output/HK_temp_map_newcolor_{time_str_filename}.png', dpi=500)
    plt.clf()
    print(f'figure output to output/HK_temp_map_newcolor_{time_str_filename}.png')