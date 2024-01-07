from UKMap import UKMap
import requests
import json
import os
import datetime

lat_lon_file = "latlon.csv"
users_file = "users.csv"

weather_api_key = "4a58331f972a44e1994165349240401"
weather_api_base_url = "https://api.weatherapi.com/v1/forecast.json?aqi=no&alerts=no"

weather_cities_list = ["Aberystwyth", "Bangor", "Birmingham", "Cardiff", "Derby", "Leeds",
                       "London", "Manchester", "Swansea"]

csv_output_folder = "weather_data"
if not os.path.exists(csv_output_folder):
    os.makedirs(csv_output_folder)


class LatLon:
    """
    LatLon class

    Attributes:
        town_name (str): name of the town
        latitude (float): latitude of the town
        longitude (float): longitude of the town
    """

    def __init__(self, town_name, latitude, longitude):
        self.town_name = town_name
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return f"{self.town_name} : [{self.latitude}, {self.longitude}]"


class WeatherData:
    """
    WeatherData class

    Attributes:
        date_time (str): date and time of the weather data
        condition (str): weather condition
        temperature (float): temperature in Celsius
    """

    def __init__(self, date_time, condition, temperature):
        self.date_time = date_time
        self.condition = condition
        self.temperature = temperature


def read_towns():
    """
    Read in the towns data (from latlon.csv)
    :return towns: list of LatLon objects
    """
    towns = []
    try:
        with open(lat_lon_file, "r") as f:
            for line in f:
                town_name, latitude, longitude = line.strip().split(",")
                towns.append(LatLon(town_name, float(latitude), float(longitude)))
        return towns
    except Exception as e:
        print(e)


def fetch_weather_data(latitude, longitude, tp, days):
    """
    Fetch weather data from weatherapi.com
    :param latitude:
    :param longitude:
    :param tp:
    :param days:
    :return weather_data: list of WeatherData objects
    """
    url = f"{weather_api_base_url}&key={weather_api_key}&q={latitude},{longitude}&tp={tp}&days={days}"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            data = json.loads(response.text)
            weather_data = []
            for forecast in data["forecast"]["forecastday"]:
                for hour in forecast["hour"]:
                    weather_data.append(WeatherData(hour["time"], hour["condition"]["text"], hour["temp_c"]))
            return weather_data
    except Exception as e:
        print(e)


def plot_specific_towns():
    """
    Plotting the towns to be easily found on the map.
    :return:
    """
    # Read in the towns data
    towns = read_towns()

    # Initialise the UKMap object
    uk_map = UKMap()
    for town in towns:
        """
        Plotting the towns to be easily found on the map.
        Marker used: o
        Marker size: 6
        Color: green
        
        
        Plotting the towns that fulfil any of the following criteria:
        • The town name starts with A, B, C, L or M.
        • The town name ends with “bury” or “ampton”.
        
        Marker used: .
        Marker size: 1
        Color: red
        """
        if town.town_name in ["Aberystwyth", "Birmingham", "Cardiff", "London"]:
            uk_map.plot(town.longitude, town.latitude, marker="o", markersize=6, color="green")
        elif town.town_name[0] in ["A", "B", "C", "L", "M"] or town.town_name[-4:] in ["bury", "ampton"]:
            uk_map.plot(town.longitude, town.latitude, markersize=1, color="red")
    uk_map.show()


def fetch_weather():
    """
    Fetch weather data from weatherapi.com and write to csv files.
    :return:
    """

    cities_with_lat_long = []

    for index, city in enumerate(read_towns()):
        if city.town_name in weather_cities_list:
            cities_with_lat_long.append((city.town_name, city.latitude, city.longitude))

    for city in cities_with_lat_long:
        city_name, latitude, longitude = city
        weather_data = fetch_weather_data(latitude, longitude, 60, 3)
        if weather_data:
            with open(f"{csv_output_folder}/{city_name}.csv", "w") as f:
                print(f"Writing {city_name}.csv")
                f.write("Date and time,Weather Condition,Temperature\n")
                for data in weather_data:
                    f.write(f"{data.date_time},{data.condition},{data.temperature}\n")


def get_weather_summarization():
    """
    Summarize the key information from the weather data.
    :return raining_cities, snowing_cities, icing_cities, else_cities: list of cities
    """

    raining_cities = []
    snowing_cities = []
    icing_cities = []
    else_cities = []

    today = datetime.datetime.now()
    tomorrow = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    for city in weather_cities_list:
        rows = []
        with open(f"{csv_output_folder}/{city}.csv", "r") as f:
            series_of_rainy_hours = 0
            series_of_snowy_hours = 0
            series_of_icy_hours = 0
            for line in f:
                if line.startswith(tomorrow):
                    date_time, condition, temperature = line.strip().split(",")
                    if "rain" in condition or "drizzle" in condition:
                        series_of_rainy_hours += 1
                    elif "snow" in condition or "blizzard" in condition:
                        series_of_snowy_hours += 1
                    elif float(temperature) < 0:
                        series_of_icy_hours += 1
            if series_of_rainy_hours >= at_least(6):
                raining_cities.append(city)
            elif series_of_snowy_hours >= at_least(4):
                snowing_cities.append(city)
            elif series_of_icy_hours >= more_than(8):
                icing_cities.append(city)
            else:
                else_cities.append(city)

    return raining_cities, snowing_cities, icing_cities, else_cities


def at_least(hours):
    """
    Calculate the number of slots needed to fulfil the at least condition.
    :param hours: hours
    :return: The at-least value of the hours
    """
    return hours + 1


def more_than(hours):
    """
    Calculate the number of slots needed to fulfil the more than condition.
    :param hours: hours
    :return: The more-than value of the hours
    """
    return hours


def print_weather_summary():
    """
    Print the weather summary.
    :return:
    """
    raining_cities, snowing_cities, icing_cities, else_cities = get_weather_summarization()

    print()

    if len(else_cities) > 0:
        print("Enjoy the weather if you are living in these cities:")
        for city in else_cities:
            print(city)
    if len(raining_cities) > 0:
        print("Bring your umbrella if you are in these cities:")
        for city in raining_cities:
            print(city)
    if len(icing_cities) > 0:
        print("Mind your step if you are in these cities:")
        for city in icing_cities:
            print(city)
    if len(snowing_cities) > 0:
        print("Plan your journey thoroughly if you are in these cities:")
        for city in snowing_cities:
            print(city)


if __name__ == "__main__":
    # plot_specific_towns()
    fetch_weather()
    get_weather_summarization()
    print_weather_summary()
