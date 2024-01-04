from UKMap import UKMap

lat_lon_file = "latlon.csv"
users_file = "users.csv"


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


class User:




if __name__ == "__main__":
    main()
