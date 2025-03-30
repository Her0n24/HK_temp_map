import csv
import requests
import os

def download_csv(api_link, output_path, stations:dict):
    """
    Downloads a CSV file from the given API link from data.gov.hk and saves it to the specified output path.

    Parameters:
    api_link (str): The URL of the API endpoint to download the CSV from.
    output_path (str): The local path where the CSV file will be saved.
    """
    response = requests.get(api_link)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"CSV file downloaded and saved to {output_path}")
    else:
        raise Exception(f"Failed to download CSV file. Status code: {response.status_code}")

    try:
        with open(output_path, mode= 'r', encoding= 'utf-8-sig') as file:
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
    return stations, datetime
    
def load_station_data(csv_path):
    """
    Loads station data from a CSV file and returns a list of dictionaries.

    Parameters:
    csv_path (str): The path to the CSV file containing station data.

    Returns:
    list: A list of dictionaries, each representing a station with its attributes.
    """
    stations = {}
    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['AutomaticWeatherStation_en']
            lat = float(row['GeometryLatitude'])
            long = float(row['GeometryLongitude'])
            stations[name] = {'lat': lat, 'long': long}
    return stations
