from UKMap import UKMap
import requests
import json
import os
import datetime
from lxml import etree
import xml.dom.minidom as minidom

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


# name.title, name.first, name.last, location.city, email, dob, phone
class Name:
    """
    Name class

    Attributes:
        title (str): title of the name
        first (str): first name
        last (str): last name
    """

    def __init__(self, title, first, last):
        self.title = title
        self.first = first
        self.last = last

    def __str__(self):
        return f"{self.title}. {self.first} {self.last}"


class User:
    """
    User class

    Attributes:
        name (Name): name of the user
        city (str): city of the user
        email (str): email of the user
        dob (str): date of birth of the user
        phone (str): phone number of the user
    """

    def __init__(self, name, city, email, dob, phone):
        self.name = name
        self.city = city
        self.email = email
        self.dob = dob
        self.phone = phone

    def __str__(self):
        return f"{self.name}, {self.city}, {self.email}, {self.dob}, {self.phone}"


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
                # print(f"Writing {city_name}.csv")
                f.write("Date and time,Weather Condition,Temperature\n")
                for data in weather_data:
                    f.write(f"{data.date_time},{data.condition},{data.temperature}\n")


def get_weather_summarization():
    """
    Summarize the key information from the weather data.
    :return raining_cities, snowing_cities, icing_cities, else_cities, tomorrow: list of cities and tomorrow's date
    """

    raining_cities = []
    snowing_cities = []
    icing_cities = []
    else_cities = []

    today = datetime.datetime.now()
    tomorrow = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    for city in weather_cities_list:
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

    return raining_cities, snowing_cities, icing_cities, else_cities, tomorrow


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
    raining_cities, snowing_cities, icing_cities, else_cities, tomorrow = get_weather_summarization()

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


def write_xml_for_weather_date():
    """
    Write the weather data to XML files.
    :return:
    """
    raining_cities, snowing_cities, icing_cities, else_cities, tomorrow = get_weather_summarization()

    root = etree.Element("WeatherForcasting")
    date = etree.SubElement(root, "Date", Date=tomorrow)

    good_weather = etree.SubElement(date, "GoodWeather")
    good_weather.text = "Enjoy the weather if you are in these cities"
    cities = etree.SubElement(good_weather, "cities")
    for city in else_cities:
        etree.SubElement(cities, "city", name=city)

    poor_weather_raining = etree.SubElement(date, "PoorWeather", Issue="Raining")
    poor_weather_raining.text = "Bring your umbrella if you are in these cities"
    cities = etree.SubElement(poor_weather_raining, "cities")
    for city in raining_cities:
        etree.SubElement(cities, "city", name=city)

    poor_weather_icing = etree.SubElement(date, "PoorWeather", Issue="Icing")
    poor_weather_icing.text = "Mind your step if you are in these cities"
    cities = etree.SubElement(poor_weather_icing, "cities")
    for city in icing_cities:
        etree.SubElement(cities, "city", name=city)

    poor_weather_snowing = etree.SubElement(date, "PoorWeather", Issue="Snowing")
    poor_weather_snowing.text = "Plan your journey thoroughly if you are in these cities"
    cities = etree.SubElement(poor_weather_snowing, "cities")
    for city in snowing_cities:
        etree.SubElement(cities, "city", name=city)

    to_string = etree.tostring(root, xml_declaration=True, encoding="utf-8")
    dom = minidom.parseString(to_string)
    with open(f"{tomorrow}.xml", "w") as f:
        f.write(dom.toprettyxml())


def read_users():
    """
    Read in the users data (from users.csv)
    :return users: list of User objects
    """
    users = []
    try:
        with open(users_file, "r") as f:
            for line in f:
                name_title, name_first, name_last, city, email, dob, phone = line.strip().split(",")
                users.append(User(Name(name_title, name_first, name_last), city, email, dob, phone))
        return users
    except Exception as e:
        print(e)


def plot_user_cities():
    """
    Plot the cities of the users.
    :return:
    """

    raining_cities, snowing_cities, icing_cities, else_cities, tomorrow = get_weather_summarization()

    # Read in the users data
    users = read_users()

    # Read in the towns data
    towns = read_towns()

    # Initialise the UKMap object
    uk_map = UKMap()

    # Initialize the array to store number of users for each city,
    # the weather condition, and the latitudes and longitudes
    city_stats = []

    highest_count = 0

    for city in weather_cities_list:
        lower = city.lower()
        lat = 0
        lon = 0
        count = 0
        for user in users:
            if lower in user.city.lower():
                count += 1

        if count > highest_count:
            highest_count = count

        if city in raining_cities:
            weather = "rain"
        elif city in icing_cities:
            weather = "ice"
        elif city in snowing_cities:
            weather = "snow"
        else:
            weather = "else"

        for town in towns:
            if city == town.town_name:
                lat = town.latitude
                lon = town.longitude

        city_stats.append([city, count, weather, lat, lon])

    highest_marker_size = 15

    for city in city_stats:
        city_name, count, weather, lat, lon = city
        if count > 0:
            marker_size = (count / highest_count) * highest_marker_size

            if weather == "rain":
                marker = "^"
                color = "red"
            elif weather == "ice":
                marker = "D"
                color = "cyan"
            elif weather == "snow":
                marker = "*"
                color = "blue"
            else:
                marker = "o"
                color = "green"
            uk_map.plot(lon, lat, marker=marker, markersize=marker_size, color=color)
    uk_map.show()


def main():
    """
        Main function

        This function will call the following functions:
        • plot_specific_towns to plot the towns in the map
        • fetch_weather to fetch the weather data from weatherapi.com and write to csv files
        • print_weather_summary to print the weather forecast summary
        • write_xml_for_weather_date to write the weather data to XML files
        • plot_user_cities to plot the cities of the users who subscribed to the weather forecast service
        """
    plot_specific_towns()
    fetch_weather()
    print_weather_summary()
    write_xml_for_weather_date()
    plot_user_cities()


if __name__ == "__main__":
    main()
